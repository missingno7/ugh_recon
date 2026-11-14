"""Reproduce the ICE scratch landing without modifying maintained L1 or tools.

--cases/--proof run isolated evidence. --accept archives committed HEAD, overlays
only FILES, promotes ice_scratch there, then runs the actual acceptance CLIs.
No reference is derived from this adapter. Every child has an 8-GiB/600-s Job.
"""
import argparse
import ctypes as C
import hashlib
import io
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import tarfile
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/workers/close-stones-14'
sys.path.insert(0,str(ROOT/'tools'))
from windows_job import WindowsJob,ExtendedLimits
from closure_support import GCC,hashes,save

FILES=['native/ice_scratch.c','native/ice_scratch.h',
       'native/bridge/ice_scratch_bridge.c','verif/ice_scratch.py',
       'verif/ice_scratch_proof.c','verif/ice_scratch_scan.c','metadata/closure/ice_scratch.json']

def bounded(command,tag,cwd=ROOT,ok=(0,),env=None):
    OUT.mkdir(parents=True,exist_ok=True)
    command=list(map(str,command));started=time.perf_counter()
    with WindowsJob() as job:
        limit=ExtendedLimits();limit.basic.flags=0x2000|0x100|0x200
        limit.process_memory=limit.job_memory=8*1024**3
        if not job.kernel.SetInformationJobObject(job.handle,9,C.byref(limit),C.sizeof(limit)):
            raise C.WinError(C.get_last_error())
        p=subprocess.Popen(command,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        job.assign(p)
        try:stdout,stderr=p.communicate(timeout=600)
        except subprocess.TimeoutExpired:
            job.terminate();stdout,stderr=p.communicate()
            save(OUT/(tag+'.json'),dict(command=command,result='TIMEOUT',stdout=stdout,stderr=stderr))
            raise RuntimeError(tag+' TIMEOUT')
    row=dict(command=command,cwd=str(cwd),returncode=p.returncode,seconds=time.perf_counter()-started,
             stdout=stdout,stderr=stderr,memory_limit_bytes=8*1024**3,timeout_seconds=600)
    save(OUT/(tag+'.json'),row)
    if p.returncode not in ok:
        save(OUT/(tag+'-negative-'+str(time.time_ns())+'.json'),row)
        raise RuntimeError(tag+': '+stdout[-1500:]+stderr[-4000:])
    print(tag, 'PASS' if p.returncode==0 else 'DETECTED', round(row['seconds'],3),'s',flush=True)
    return row

def build(tag='pair',mutant=None,one_step=False):
    import nbuild
    folder=OUT/tag;folder.mkdir(parents=True,exist_ok=True)
    sources=[]
    for p in sorted((ROOT/'c').glob('*.c')):
        text=p.read_text()
        for name in ['UnpackIceStream','UnpackIceToScratch']:
            text=re.sub(r'\bc_'+name+r'\b','l1_'+name,text)
        if one_step and p.name=='ice.c':text=text.replace('2000000','1')
        target=folder/p.name;target.write_text(text);sources.append(target)
    for name in ['native/ice.c','native/ice_scratch.c','native/bridge/ice_bridge.c',
                 'native/bridge/ice_scratch_bridge.c']:
        p=ROOT/name;text=p.read_text()
        if one_step and name=='native/ice.c':text=text.replace('2000000u','1u')
        if mutant and name==mutant[0]:
            assert mutant[1] in text;text=text.replace(mutant[1],mutant[2])
        # Resolve quoted project headers as in the original source directory.
        text=re.sub(r'#include "([^"]+)"',lambda m:'#include "'+(p.parent/m[1]).resolve().as_posix()+'"'
                    if (p.parent/m[1]).is_file() else m[0],text)
        target=folder/('native_'+p.name);target.write_text(text);sources.append(target)
    dll=folder/'pair.dll'
    declarations=folder/'fallbacks.h'
    declarations.write_text('#include "ugh.h"\nint l1_UnpackIceStream(Regs *);\nint l1_UnpackIceToScratch(Regs *);\n')
    command=[GCC,'-shared','-O2','-std=c11','-Wall','-Wextra','-Werror','-fwrapv',
             '-I',ROOT/'c','-include',declarations,'-o',dll,*sources]
    compiled=bounded(command,tag+'-compile')
    compiled.update(compiler_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),
                    inputs=hashes([*sources,declarations,*sorted((ROOT/'c').glob('*.h')),
                                   *sorted((ROOT/'c').glob('*.inc'))]))
    save(OUT/(tag+'-compile.json'),compiled)
    return nbuild.load_l1(dll)

def pair(dll,initial,r):
    from difftest import MEM_SIZE,Regs
    observations=[];mem=dll.ugh_memory().contents
    for fn in [dll.l1_UnpackIceToScratch,dll.c_UnpackIceToScratch]:
        C.memmove(mem,initial,MEM_SIZE);dll.ugh_devices_reset()
        actual=Regs.from_buffer_copy(r);code=fn(C.byref(actual))
        observations.append((code,bytes(actual),bytes(mem),bytes(dll.ugh_device_state().contents)))
    return observations

def cases():
    from difftest import Case,Regs,MEM_SIZE,run
    from emu import Machine
    from ice_fuzz import corpus
    from dataprobe import ice_pack235
    dll=build();m=Machine();snapshot=m.snapshot();scratch=m.seg('ZERO:IceDecodeWorkspace');dest=scratch*16
    rows=[];unicorn=[];rng=random.Random(0x14ce)
    def unicorn_pair(case,poison):
        for target in ['l1_UnpackIceToScratch','c_UnpackIceToScratch']:
            case.cfunc=target
            problems=run(case,m,dll,poison);assert not problems,(case.title,target,problems)
            unicorn.append(dict(case=case.title,target=target,poison=poison,steps=m.steps))
    base=list(corpus(120,m))
    for kind,stream,data in base:
        initial=bytearray(snapshot)
        initial[0x75000:0x85000]=stream.ljust(65536,b'\0')
        initial[dest:dest+65536]=rng.randbytes(65536)
        r=Regs(ax=0xa1,bx=0xb2,cx=0xc3,dx=0xd4,bp=0xe5,si=0,di=0xbeef,
               ds=0x7500,es=0xdead,ss=0x9000,sp=0x100,flags=0xed7)
        a,b=pair(dll,bytes(initial),r);assert a==b,(kind,len(stream),'pair')
        assert a[2][dest:dest+len(data)]==data
        rows.append(dict(kind=kind,packed=len(stream),output=len(data),sha256=hashlib.sha256(stream).hexdigest()))
    # Actual shipped resources retain their physical source addresses, including
    # the first source window's harmless overlap with the unused workspace tail.
    for frame in [0x1a38,0x2bf6,0x2d9a,0x2f9e,0x2fb7]:
        case=Case('scratch resource '+hex(frame),'GAME:UnpackIceToScratch',
            regs=lambda machine,f=frame:dict(DS=machine.seg(f'B{f:04X}:IceStream_{f:04X}'),SI=0,ES=0xdead,DI=0xbeef),
            flags=0x602,out_regs=('AX','BX','CX','DX','BP','SI','DI','DF'))
        for poison in [False,True]:
            unicorn_pair(case,poison)
    for length in [1,32768,32769,65535,65536]:
        data=(bytes(range(256))*(length//256+1))[:length];stream=ice_pack235(data)
        case=Case('scratch boundary '+str(length),'GAME:UnpackIceToScratch',
            setup=lambda machine,s=stream:machine.write(0x7500,0,s),
            regs=dict(DS=0x7500,SI=0,ES=0xdead,DI=0xbeef),flags=0x602,
            out_regs=('AX','BX','CX','DX','BP','SI','DI','DF'),budget=12000000)
        unicorn_pair(case,True)
    # Full incoming offset slice; every possible SI, both rejected signatures,
    # all incoming ES/DI values permuted through the same slice. Word at FFFF
    # is physically contiguous; the next word's effective offset wraps.
    bad=0
    for cursor in range(65536):
        for raw in [b'xx',b'ICxx']:
            initial=bytearray(snapshot);p=0x75000+cursor
            initial[p:p+2]=raw[:2]
            if raw[:2]==b'IC':
                p=0x75000+((cursor+2)&65535);initial[p:p+2]=raw[2:]
            r=Regs(si=cursor,di=cursor^0xa5a5,ds=0x7500,es=cursor,flags=0xed7)
            # Full RAM equality for the complete slice would copy 280 GiB.
            # Neither early return writes RAM; compare it once at each edge,
            # while compiled complete-register comparison covers every cursor.
            mem=dll.ugh_memory().contents;C.memmove(mem,bytes(initial),MEM_SIZE)
            a=Regs.from_buffer_copy(r);b=Regs.from_buffer_copy(r)
            x=dll.l1_UnpackIceToScratch(C.byref(a));y=dll.c_UnpackIceToScratch(C.byref(b))
            assert x==y==0 and bytes(a)==bytes(b),(cursor,raw)
            if cursor in [0,1,65533,65534,65535]:assert bytes(mem)==bytes(initial)
            bad+=1
    for cursor in [0,1,65533,65534,65535]:
        for raw in [b'xx',b'ICxx']:
            def setup(machine,c=cursor,s=raw):
                machine.write(0x7500,c,s[:2])
                if s[:2]==b'IC':machine.write(0x7500,(c+2)&65535,s[2:])
            case=Case('scratch bad signature '+str(cursor)+str(raw),'GAME:UnpackIceToScratch',
                setup=setup,regs=dict(DS=0x7500,SI=cursor,ES=0xdead,DI=0xbeef),flags=0x602,
                out_regs=('AX','BX','CX','DX','BP','SI','DI','DF'))
            unicorn_pair(case,True)
    admissions=[]
    for cursor,segment in [(16,0x7500),(65533,0x7500),(65534,0x7500),(65535,0x7500),(0,scratch)]:
        initial=bytearray(snapshot);at=segment*16+cursor
        initial[at:at+2]=b'IC';at=segment*16+((cursor+2)&65535);initial[at:at+2]=b'E!'
        if not cursor:
            raw=ice_pack235(b'Z');initial[dest:dest+len(raw)]=raw
        mem=dll.ugh_memory().contents;C.memmove(mem,bytes(initial),MEM_SIZE)
        r=Regs(ds=segment,si=cursor,es=0xdead,di=0xbeef,flags=0xed7)
        status=dll.c_UnpackIceToScratch(C.byref(r))
        assert status==1 and r.es==scratch and r.di==0 and bytes(mem)==bytes(initial),(cursor,segment,status)
        admissions.append(dict(cursor=cursor,source_segment=segment,result='REJECTED_WITHOUT_FALLBACK'))
    # One actual outer iteration, all first payloads and five output words.
    # This specifically checks partial writes with the local cursors unpublished.
    bounded_dll=build('one-step',one_step=True);partial=0;outcomes={}
    for length in range(5):
        for payload in range(256):
            stream=b'ICE!'+(13).to_bytes(4,'big')+length.to_bytes(4,'big')+bytes([payload])
            initial=bytearray(snapshot);initial[0x75000:0x85000]=stream.ljust(65536,b'\0')
            initial[dest:dest+65536]=bytes([0xa5])*65536
            r=Regs(ds=0x7500,es=0xdead,di=0xbeef,flags=0xed7)
            a,b=pair(bounded_dll,bytes(initial),r);assert a==b,(length,payload)
            outcomes[str(a[0])]=outcomes.get(str(a[0]),0)+1
            if a[0]==2 and a[2]!=bytes(initial):partial+=1
    assert partial
    full_ring=[]
    for packed,length in [(1,1),(1,3),(13,1),(13,2),(65535,1),(0,1)]:
        initial=bytearray(snapshot)
        stream=b'ICE!'+packed.to_bytes(4,'big')+length.to_bytes(4,'big')
        initial[0x75000:0x85000]=stream.ljust(65536,b'\0')
        initial[dest:dest+65536]=bytes([0xa5])*65536
        r=Regs(ds=0x7500,es=0xdead,di=0xbeef,flags=0xed7)
        a,b=pair(dll,bytes(initial),r);assert a==b,('full ring',packed,length)
        full_ring.append(dict(packed=packed,output=length,status=a[0],partial=a[2]!=bytes(initial)))
    assert any(row['status']==2 and row['partial'] for row in full_ring)
    result=dict(result='PASS',generated=rows,unicorn=unicorn,all_offset_bad_magic_cases=bad,
                one_step_cases=1280,one_step_outcomes=outcomes,one_step_partial_errors=partial,
                full_ring=full_ring,admission_controls=admissions,
                image_sha256=hashlib.sha256(m.raw_image).hexdigest(),
                compiler_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),
                inputs=hashes([ROOT/p for p in FILES if not p.endswith('.json')]+list((ROOT/'c').glob('*.[ch]'))+
                    list((ROOT/'c').glob('*.inc'))+[ROOT/p for p in ['native/ice.c','native/ice.h',
                    'native/bridge/ice_bridge.c','tools/difftest.py','tools/emu.py','tools/nbuild.py',
                    'tools/dataprobe.py','verif/closure_support.py','verif/windows_job.py','verif/ice_fuzz.py']]))
    save(OUT/'cases.json',result);print('cases PASS',len(rows),len(unicorn),bad,partial,flush=True)

def proof():
    from closure_support import function
    folder=OUT/'proof';folder.mkdir(parents=True,exist_ok=True)
    preprocess=[GCC,'-E','-P','-nostdinc','-I'+str(ROOT/'verif/cbmc_shim'),
                '-I'+str(ROOT/'native'),ROOT/'verif/ice_scratch_proof.c','-o',folder/'proof.i']
    bounded(preprocess,'proof-preprocess')
    manifest=json.loads((ROOT/'metadata/verif-tools.json').read_text());tool=Path(manifest['cbmc']['exe'])
    assert hashlib.sha256(tool.read_bytes()).hexdigest()==manifest['cbmc']['exe_sha256']
    command=[tool,folder/'proof.i','--unwind','3','--unwinding-assertions','--bounds-check',
             '--pointer-check','--signed-overflow-check','--slice-formula','--trace']
    row=bounded(command,'proof-cbmc');assert 'VERIFICATION SUCCESSFUL' in row['stdout']
    save(OUT/'proof.json',dict(result='PASS',command=list(map(str,command)),preprocess=list(map(str,preprocess)),
         inputs=hashes([ROOT/'native/ice_scratch.c',ROOT/'native/ice_scratch.h',ROOT/'native/ice.h',ROOT/'verif/ice_scratch_proof.c',tool]),
         profile='Actual complete adapter C; arbitrary codec reply/status/cursors/counts and byte write; one call equality seam. Codec internals separately accepted, not re-proved here.',
         preprocessed_sha256=hashlib.sha256((folder/'proof.i').read_bytes()).hexdigest()))
    # Mechanically retain complete signature/setup branches; the recognized
    # branch meets the codec proof at a checked return value of 77 on both sides.
    literal=function((ROOT/'c/ice.c').read_text(),'c_UnpackIceStream')
    literal=literal.split('    r->si+=2;\n    uint16_t packed=')[0]+'    return 77;\n}\n'
    wrapper=function((ROOT/'c/dos_input.c').read_text(),'c_UnpackIceToScratch')
    wrapper=wrapper.replace('c_UnpackIceToScratch','reference_scratch')
    modern=function((ROOT/'native/bridge/ice_scratch_bridge.c').read_text(),'c_UnpackIceToScratch')
    modern=modern.split('    if (r->si!=4)')[0]+'    return 77;\n}\n'
    assert all('return 77' in s for s in [literal,modern])
    (folder/'scan_bodies.inc').write_text(literal+wrapper+modern)
    preprocess=[GCC,'-E','-P','-nostdinc','-U_WIN32','-I'+str(ROOT/'verif/cbmc_shim'),
        '-I'+str(ROOT/'c'),'-I'+str(folder),ROOT/'verif/ice_scratch_scan.c','-o',folder/'scan.i']
    bounded(preprocess,'scan-preprocess')
    command=[tool,folder/'scan.i','--unwind','4','--unwinding-assertions','--bounds-check',
             '--pointer-check','--signed-overflow-check','--slice-formula','--trace']
    row=bounded(command,'scan-cbmc');assert 'VERIFICATION SUCCESSFUL' in row['stdout']
    save(OUT/'scan.json',dict(result='PASS',command=list(map(str,command)),preprocess=list(map(str,preprocess)),
        inputs=hashes([ROOT/'verif/ice_scratch_scan.c',ROOT/'c/dos_input.c',ROOT/'c/ice.c',ROOT/'c/ugh.h',
                       ROOT/'c/ugh_sym.h',ROOT/'native/bridge/ice_scratch_bridge.c',tool]),
        profile='Actual L1 scratch wrapper, L1 decoder signature prefix and actual native bridge prefix. All 16-bit incoming registers/flags, both 16-bit signature words, ordinary synchronous reads; recognized header-at-zero assumption only. Complete register frame and ordered physical reads checked at recognized seam or return.',
        preprocessed_sha256=hashlib.sha256((folder/'scan.i').read_bytes()).hexdigest()))

def mutations():
    from difftest import Regs
    from emu import Machine
    from dataprobe import ice_pack235
    m=Machine();snapshot=m.snapshot();dest=m.seg('ZERO:IceDecodeWorkspace')*16
    valid=bytearray(snapshot);raw=ice_pack235(b'workspace test')
    valid[0x75000:0x85000]=raw.ljust(65536,b'\0')
    bad=bytearray(snapshot);bad[0x75000:0x75004]=b'bad!'
    partial=bytearray(snapshot)
    raw=b'ICE!'+(13).to_bytes(4,'big')+(1).to_bytes(4,'big')+b'\xc1'
    partial[0x75000:0x85000]=raw.ljust(65536,b'\0')
    partial[dest:dest+65536]=bytes([0xa5])*65536
    native='native/ice_scratch.c';bridge='native/bridge/ice_scratch_bridge.c'
    specs=[('workspace_binding',(bridge,'r->es=UGH_S_ZERO_IceDecodeWorkspace;',
             'r->es=UGH_S_ZERO_IceDecodeWorkspace+1;'),valid,False),
           ('initial_cursor',(bridge,'logic(r,0,16)','logic(r,1,16)'),bad,False),
           ('error_source_cursor',(native,'result->source_cursor=10;','result->source_cursor=11;'),partial,True),
           ('error_destination_cursor',(native,'result->workspace_cursor=0;',
             'result->workspace_cursor=(uint16_t)result->decoder.destination_cursor;'),partial,True),
           ('discard_partial',(bridge,'memcpy(ugh_mem+destination,output,sizeof output);',
             'if (status==ICE_OK) memcpy(ugh_mem+destination,output,sizeof output);'),partial,True)]
    rows=[]
    for name,change,initial,one_step in specs:
        dll=build('mutant-'+name,change,one_step)
        r=Regs(ds=0x7500,es=0xdead,di=0xbeef,flags=0xed7)
        a,b=pair(dll,bytes(initial),r);assert a!=b,(name,'SURVIVED')
        rows.append(dict(name=name,result='DETECTED_BY_BRIDGE',change=change,
                         one_iteration=one_step,l1_status=a[0],native_status=b[0]))
    save(OUT/'mutations.json',dict(result='PASS',controls=rows));print('5/5 mutations detected',flush=True)

def reuse():
    import ice_cbmc
    rows=[]
    accepted=json.loads((ROOT/'metadata/closure/ice.json').read_text())
    profiles=[p for evidence in accepted['evidence'] for p in evidence.get('profiles',[])]
    # Fingerprints of the accepted pilot's two controls (not equivalence proofs).
    # The nine equivalence fingerprints and commands come from the committed
    # certificate itself. No historical build/ directory is needed for replay.
    profiles += [dict(profile='reach_whole_s16_o4_u17',result='WITNESSED',stream=16,output=4,iterations=3,
          preprocessed_sha256='d2c28ad7bed688506c61a6e49503363560611f65fe072aec7da32f2e7162946d'),
        dict(profile='negative_whole_s16_o2_u1',result='FAIL',stream=16,output=2,iterations=2,
          preprocessed_sha256='d3d5db8ddd7b04273ff5a1efd70b6c327890d55eda5c331d0cf9da4fbc414fd2')]
    assert len(profiles)==11
    primitives=['reader','bits','literal','length','offset']
    for record in profiles:
        name=record['profile'];mode=re.fullmatch(r'(?:final|reach|negative)_(\w+)_s\d+_o\d+_u\d+',name)[1]
        folder=OUT/'codec-replay'/name;ice_cbmc.prepare(folder,mode=mode)
        command=[GCC,'-E','-P','-nostdinc','-I'+str(ROOT/'verif/cbmc_shim'),'-I'+str(ROOT/'native'),
            '-DSTREAM_SIZE='+str(record['stream']),'-DOUTPUT_SIZE='+str(record['output']),
            '-DTOKEN_BOUND='+str(record['iterations']),'-DPRIMITIVE='+str(primitives.index(mode) if mode in primitives else 0),
            '-DCOVER_RUN='+str(int(name.startswith('reach'))),folder/'whole.c','-o',folder/'whole.i']
        bounded(command,'codec-preprocess-'+name)
        actual=hashlib.sha256((folder/'whole.i').read_bytes()).hexdigest()
        assert actual==record['preprocessed_sha256'],name+' changed'
        rows.append({**record,'current_preprocess':list(map(str,command)),
                     'current_preprocessed_sha256':actual,'current_C_identical':True})
    save(OUT/'codec-reuse.json',dict(result='PASS',profiles=rows,accepted_certificate='metadata/closure/ice.json',
         inputs=hashes([ROOT/'native/ice.c',ROOT/'native/ice.h',ROOT/'native/bridge/ice_bridge.c',ROOT/'c/ice.c']),
         scope='No codec proof rerun or broader claim: eleven current-C profiles reproduce accepted preprocessing byte for byte, including the reachability and negative unwind controls.'))

def certificate():
    import closure
    files=FILES[:3]
    inputs=[ROOT/p for p in FILES if not p.endswith('.json')]+[ROOT/p for p in
        ['c/dos_input.c','c/ice.c','c/ugh.h','c/ugh_sym.h','native/ice.c','native/ice.h','native/bridge/ice_bridge.c',
         'metadata/closure/ice.json','tools/hostbuild.py','tools/closure.py',
         'tools/difftest.py','tools/emu.py','tools/wholegame.py','verif/standalone_census.py','verif/windows_job.py',
         'metadata/verif-tools.json','verif/ice_cbmc.py','verif/ice_fuzz.py','tools/dataprobe.py',
         'tools/nbuild.py','verif/closure_support.py','src/asm/GAME.ASM']]
    inputs += list((ROOT/'c').glob('*.[ch]'))+list((ROOT/'c').glob('*.inc'))
    cert=dict(component='ice_scratch',status='unanalyzed',proposed_status='migrated',
       proposed_status_reason='Full admitted scratch-entry contract has C and D; B proves the complete adapter and actual signature/setup prefix at checked codec seams. Codec whole/step B domains remain exactly those of ice, not a full-ring proof.',
       original=dict(owned=[dict(identity='GAME:UnpackIceToScratch',address='013B:4CA5')],
                     L0=['src/asm/GAME.ASM:UnpackIceToScratch, fallthrough to UnpackIceStream'],
                     L1=['c/dos_input.c:c_UnpackIceToScratch']),
       native=dict(files=files,header='native/ice_scratch.h',functions=['ice_unpack_scratch'],
                   bridge='c_UnpackIceToScratch',build='python verif/ice_scratch.py --cases'),
       purpose='ICE-owned scratch/workspace adapter composing the accepted ice_decode API. Borrowed storage, no second workspace owner or decoder implementation; separate certificate preserves the existing codec proof/source locks.',
       interface=dict(inputs=['Borrowed disjoint native source/workspace buffers and their available sizes; header at source[0]; workspace is initialized in/out, never cleared'],
           outputs=['IceStatus and unchanged decoder result, plus published source/workspace cursors; partial workspace on errors'],
           bridge=['ES always becomes ZERO:IceDecodeWorkspace; DI=0 before signature scan; DF cleared. Bad magic publishes SI+2 or SI+4 with 16-bit wrap. Recognized streams start at SI=0; completion publishes decoder cursors; budget failure publishes SI=10, DI=0 and partial bytes.',
                   'AX/BX/CX/DX/BP/DS/SS/SP/CS preserved. Incoming arithmetic flags are not application observations; L1 equality checks include them, L0 checks compare only live DF.',
                   'No fallback: out-of-admission recognized offset/overlap returns UGH_UNSUPPORTED. ICE_LIMIT maps UGH_BUDGET; short storage is native-only TRUNCATED/RANGE.'],
           admission=['Ordinary synchronous RAM, immutable ICE tables/resources, no device/code/live-stack aliases; actual source-read and workspace-write footprints disjoint. The first shipped resource window overlaps only the untouched workspace tail, tested at its physical address.',
                      'Bridge storage supplies two full 65536-byte snapshots. Bad-magic operands at FFFF read contiguous physical words before effective SI wraps. A recognized nonzero-header stream is outside the existing ice bridge contract.']),
       callers=[dict(routine='GAME:LoadCurrentLevelState',native='native/bridge/session_bridge.c:c_LoadCurrentLevelState',
                     observes='ES scratch and expanded bytes; then copies 160 words with DF clear; DS restored by caller'),
                dict(routine='GAME:PrepareAttractMap',native='native/bridge/menus_bridge.c:prepare_attract_map',
                     observes='ES scratch and expanded tile map; same stable near-entry ABI')],
       callees=['ice_unpack_scratch -> accepted native ice_decode; no L1 decoder/direct-call dependency'],
       indirect=['No indirect transfer or callback; both callers dispatch the stable scratch entry through the bridge.'],
       memory=dict(reads='Source signature/header/stream plus seeded workspace backreferences; immutable codec tables',
                   writes='Codec workspace writes only, in original backward order; no zero initialization; bridge republishes the full snapshot without other-byte changes',
                   persistent='No state allocated or retained: loader-owned scratch storage is borrowed per call.'),
       assumptions=['Valid nonnull view/result objects and accessible initialized buffers of the supplied sizes.',
                    'Recognized application headers start at zero; rejected signatures admit every 16-bit SI.',
                    'Ordinary disjoint read/write footprints, immutable resources/tables, no live-stack/code/device alias; synchronous execution.',
                    'Full 65536-byte windows retain wrap and malformed seed references; no general malformed-stream termination theorem. Two-million-token L1 harness guard retained.',
                    'B seam proves forwarding and publication for arbitrary codec replies; codec B only covers its accepted bounded buffer/one-step profiles. General codec/bridge remains C.'],
       eliminated=['Original ES/DI setup becomes bridge binding plus explicit borrowed workspace view; no global native scratch or dispatcher in native code.',
                   'The executed generated c/dos_input.c -> l1_UnpackIceStream edge is retired by replacing c_UnpackIceToScratch. hostbuild.py unchanged.'],
       retained=['Ignored high size words and incoming workspace cursor; raw 16-bit backward cursor wrap; seed-byte reads and overlap within output.',
                 'Bad magic early-return cursor, unconditional workspace binding and DF clear; partial output and unpublished local cursors on budget error.',
                 'No invented error recovery, source/workspace clearing, validation or success flag.'],
       evidence=[],amiga=dict(classification='not-used',finding='DOS wrapper and accepted DOS ICE API determine this boundary.'),
       uncertainty=['C/D scenarios are not all-state reachability proofs; dormant L1 copies remain linked for literal/reference evidence, but none of their ICE bodies executes in the native census.',
                    'Native safety errors and unrecognized bridge admissions are not DOS semantics; full 64-KiB malformed termination is not proved.'],
       dependencies={p:closure.actual_dependencies(ROOT/p) for p in files},
       verification_input_hashing='sha256-lf-text',
       verification_tools=dict(gcc=dict(exe=str(GCC),sha256=hashlib.sha256(GCC.read_bytes()).hexdigest()),
                               cbmc=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']),
       verification_inputs={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest() for p in inputs})
    specs=[('complete scratch adapter output/frame/dependence at codec seam','B','CBMC on actual complete adapter C, arbitrary reply/status/cursors and partial byte; forwarding and exactly one call checked',
            '--proof','PASS; actual code, no decoder internals replaced by a claimed proof; 8 GiB, 600 s, one solver permit','proof.json'),
           ('accepted codec evidence reused without widening','B','Regenerate current-code preprocessing for eleven accepted profiles; byte equality; bounded domains, reachability and negative unwind controls retained',
            '--reuse','PASS eleven profiles identical; codec algorithm and old bridge unmodified','codec-reuse.json'),
           ('L0/L1/native scratch projection, workspace and error publication','C','Unicorn rebuilt-ASM differential, full-RAM/device/register compiled pair, full incoming-offset bad-magic slice and one-iteration partial-output enumeration',
            '--cases','PASS 147 compiled corpus cases; 25 L0/L1 and 25 L0/native Unicorn comparisons; all 131072 rejected-signature offsets; 1280 one-iteration cases; six unmodified full-ring cases including actual two-million-token partial-output error','cases.json'),
           ('bridge mutation controls','C','Independent mutations of workspace binding, initial cursor, error cursors and discarded partial writes',
            '--mutations','PASS 5/5 DETECTED_BY_BRIDGE','mutations.json'),
           ('clean committed baseline composition and direct-call census','D','Actual build/closure/host CLIs in committed archive plus only this worker, scratch promotion; all maintained references reused, instrumented census also compares full smoke to literal',
            '--accept','PASS closure; plain/proof builds; native/literal 21/21 each; 20 scenarios plus smoke, zero L1 ICE bodies and zero fallbacks','acceptance.json')]
    for prop,level,method,arg,result,artifact in specs:
        cert['evidence'].append(dict(property=prop,level=level,method=method,command='python verif/ice_scratch.py '+arg,
                                     result=result,date='2026-11-14',artifact='build/workers/close-stones-14/'+artifact))
    cert['evidence'].append(dict(property='scratch setup, signature reads and complete register frame at codec seam',level='B',
         method='CBMC over mechanically extracted actual L1 wrapper, L1 decoder prefix and native bridge prefix; arbitrary 16-bit registers/flags and both signature words; exact ordered-read assertion',
         command='python verif/ice_scratch.py --proof',result='PASS; only ordinary read service and recognized-header-at-zero assumptions; no codec or alias proof inferred',date='2026-11-14',
         artifact='build/workers/close-stones-14/scan.json'))
    save(ROOT/'metadata/closure/ice_scratch.json',cert)

def snapshot():
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    target=OUT/'baseline';target.mkdir(parents=True,exist_ok=True)
    pin=target/'.closure-baseline.json'
    if pin.exists():assert json.loads(pin.read_text())['revision']==revision,'baseline changed: use a new worker directory'
    else:
        archive=subprocess.check_output(['git','archive','--format=tar',revision],cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            for member in tar.getmembers():
                if not member.isfile():continue
                p=(target/member.name).resolve();assert p.is_relative_to(target.resolve())
                data=tar.extractfile(member).read();current=ROOT/member.name
                if current.is_file() and current.read_bytes().replace(b'\r\n',b'\n')==data.replace(b'\r\n',b'\n'):data=current.read_bytes()
                p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        save(pin,dict(revision=revision,overlay=FILES,scope='Committed HEAD plus only this worker; no close-adlx-20 files.'))
    for name in FILES:
        p=target/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
    p=target/'metadata/closure/ice_scratch.json';cert=json.loads(p.read_text());cert['status']='migrated';save(p,cert)
    # These gates use the freshly reconstructed image, not an original EXE.
    refs=target/'build/whole';refs.mkdir(parents=True,exist_ok=True)
    for p in (ROOT/'build/whole').glob('*.ref.json'):shutil.copyfile(p,refs/p.name)
    save(OUT/'baseline.json',dict(revision=revision,overlay_inputs=hashes([ROOT/p for p in FILES]),
         references=hashes(list((ROOT/'build/whole').glob('*.ref.json')))))
    return target

def accept():
    target=snapshot()
    # wholegame's optional historical call-edge ledger is not an input to any
    # frame reference. An empty scratch ledger requests no call-edge claims.
    ledger=target/'build/workers/c-close/call-edges.json'
    if not ledger.exists():ledger.parent.mkdir(parents=True,exist_ok=True);save(ledger,[])
    commands=[['tools/closure.py'],['tools/build.py'],['tools/wholegame.py'],['tools/hostbuild.py'],
        ['host/check.py','--variant','native'],['tools/hostbuild.py','--literal'],
        ['host/check.py','--variant','literal'],['verif/standalone_census.py','--all']]
    rows=[]
    for i,args in enumerate(commands):
        row=bounded([sys.executable,*args],'accept-'+str(i),cwd=target);rows.append(row)
        if args==['host/check.py','--variant','native']:shutil.copyfile(target/'build/workers/host-native/host-check-native.json',OUT/'host-native.json')
        if args==['host/check.py','--variant','literal']:shutil.copyfile(target/'build/workers/host-native/host-check-literal.json',OUT/'host-literal.json')
    census=target/'build/workers/close-adlx-19/census.json';j=json.loads(census.read_text())
    ice=[f for f in j['functions'] if f['kind']=='c' and ('Ice' in f['name'] or f['path']=='c/ice.c')]
    assert not ice,ice
    assert sum(s['fallback_calls'] for s in j['scenarios'])==0
    # Every direct renamed call inside every executed L1 body, including inline
    # helpers. The census's source-body hooks also catch non-entry helpers.
    hazards=[]
    for f in j['functions']:
        if f['kind']!='c':continue
        text=(target/'c'/Path(f['path']).name).read_text()
        from closure_support import function
        try:body=function(text,f['name'])
        except ValueError:continue
        exports={n for u in json.loads((target/'build/workers/close-adlx-19/instrumented/build.json').read_text())['units'] for n in u['exports']}
        calls=sorted(set(re.findall(r'\b(c_\w+)\s*\(',body))&exports-{f['name']})
        if calls:hazards.append(dict(function=f['name'],path=f['path'],count=f['count'],calls=calls))
    save(OUT/'acceptance.json',dict(result='PASS',baseline=json.loads((OUT/'baseline.json').read_text()),commands=rows,
         l1_ice_bodies=ice,fallbacks=0,other_executed_l1_rename_hazards=hazards,
         census=str(census.relative_to(ROOT)),census_sha256=hashlib.sha256(census.read_bytes()).hexdigest()))
    print('acceptance PASS; zero L1 ICE, zero fallbacks; rename hazards',hazards,flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['cases','proof','accept','mutations','reuse','certificate','internal']:
        parser.add_argument('--'+name,action='store_true')
    args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    if args.cases:
        if args.internal:cases()
        else:bounded([sys.executable,__file__,'--cases','--internal'],'cases-child')
    if args.proof:proof()
    if args.mutations:
        if args.internal:mutations()
        else:bounded([sys.executable,__file__,'--mutations','--internal'],'mutations-child')
    if args.reuse:reuse()
    if args.certificate:certificate()
    if args.accept:accept()

if __name__=='__main__':main()
