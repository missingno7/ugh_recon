"""Freeze the standalone seam: test-only world, write journal and effect projector.

Only verif/projector/* and close-adlx-20 artifacts are owned. All game/platform
instrumentation is in a git-archive copy of a pinned committed baseline. Every
compiler/host/driver child is serial, bounded to 600s and 8GiB with a Windows Job.
No reference file is ever read by the C projector or used to construct its state.
"""
import argparse
import ctypes as C
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/workers/close-adlx-20'
BASELINE_REVISION='8ecc728a456513cc168ad75da0c4f40565d78e88'
sys.path.insert(0,str(ROOT/'tools'))
from windows_job import WindowsJob,ExtendedLimits
from standalone_census import bodies,masked
from projector.schema import generate as generate_schema
from projector.publications import instrument_publication


def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bounded(command,tag,env=None,cwd=ROOT):
    start=time.perf_counter()
    with WindowsJob() as job:
        limits=ExtendedLimits();limits.basic.flags=0x2000|0x100|0x200
        limits.process_memory=limits.job_memory=8*1024**3
        if not job.kernel.SetInformationJobObject(job.handle,9,C.byref(limits),C.sizeof(limits)):raise C.WinError(C.get_last_error())
        p=subprocess.Popen(list(map(str,command)),cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        job.assign(p)
        try:stdout,stderr=p.communicate(timeout=600)
        except subprocess.TimeoutExpired:
            job.terminate();stdout,stderr=p.communicate()
            save(OUT/'negative'/f'{tag}-{time.time_ns()}.json',dict(result='TIMEOUT',command=list(map(str,command)),stdout=stdout,stderr=stderr))
            raise RuntimeError(tag+' timed out')
    result=dict(command=list(map(str,command)),returncode=p.returncode,stdout=stdout,stderr=stderr,
                seconds=time.perf_counter()-start,memory_limit_bytes=8*1024**3,timeout_seconds=600)
    save(OUT/'children'/f'{tag}.json',result)
    if p.returncode:
        save(OUT/'negative'/f'{tag}-{time.time_ns()}.json',result)
        raise RuntimeError(tag+' failed: '+stderr[-5000:])
    return result


def freeze(revision=BASELINE_REVISION):
    folder=OUT/'frozen'
    commit=subprocess.check_output(['git','rev-parse',revision],cwd=ROOT,text=True).strip()
    if folder.exists():
        info=json.loads((OUT/'baseline.json').read_text())
        assert info['commit']==commit,'existing frozen archive has a different revision; use a separate reviewed output tree'
        return info
    raw=subprocess.check_output(['git','archive','--format=zip',commit],cwd=ROOT)
    folder.mkdir(parents=True)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for entry in archive.infolist():assert (folder/entry.filename).resolve().is_relative_to(folder.resolve())
        archive.extractall(folder)
    info=dict(commit=commit,archive_sha256=hashlib.sha256(raw).hexdigest(),
              scope='Committed tree only; concurrent uncommitted ICE files are excluded.')
    save(OUT/'baseline.json',info);return info


def with_return_hook(text,name,hook):
    parts=[x for x in bodies(text) if x[3]==name];assert len(parts)==1,(name,len(parts))
    a,b,e,n=parts[0];body=text[b+1:e];clean=masked(body);edits=[]
    for m in re.finditer(r'\breturn\b',clean):
        end=clean.index(';',m.end());expr=body[m.end():end].strip()
        v='{'+('__auto_type pr_result=('+expr+');' if expr else '')+hook+'return'+(' pr_result' if expr else '')+';}'
        edits.append((m.start(),end+1,v))
    for a,z,v in reversed(edits):body=body[:a]+v+body[z:]
    body+='\n'+hook+'\n'
    return text[:b+1]+body+text[e:]


def units_at(frozen):
    result=[]
    statuses=['migrated','verified-under-assumptions','verified-within-contract','integration-validated']
    for p in sorted((frozen/'metadata/closure').glob('*.json')):
        d=json.loads(p.read_text())
        if d.get('status') not in statuses:continue
        files=d['native'].get('files',[])
        native=[f for f in files if f.startswith('native/') and '/bridge/' not in f and f.endswith('.c')]
        bridge=[f for f in files if f.startswith('native/bridge/') and f.endswith('.c')]
        assert len(native)==len(bridge)==1,p
        exports=sorted(set(re.findall(r'\bEXPORT\s+int\s+(c_\w+)\s*\(',(frozen/bridge[0]).read_text())))
        result.append(dict(component=d.get('component',p.stem),native=native[0],bridge=bridge[0],exports=exports))
    return result


def build(literal=False,revision=BASELINE_REVISION):
    import hostbuild,cgen
    info=freeze(revision);frozen=OUT/'frozen';folder=OUT/('literal' if literal else 'instrumented');folder.mkdir(exist_ok=True)
    units=[] if literal else units_at(frozen);exports={n for u in units for n in u['exports']}
    inputs=[Path(__file__),*sorted((ROOT/'verif/projector').glob('*')),
            ROOT/'verif/standalone_census.py',ROOT/'verif/windows_job.py',ROOT/'tools/hostbuild.py',ROOT/'tools/cgen.py',ROOT/'tools/common.py']
    for top in ['c','native','host']:
        for p in sorted((frozen/top).rglob('*')):
            if p.suffix not in ['.c','.h','.inc']:continue
            rel=p.relative_to(frozen).as_posix();text=p.read_text()
            if top=='c' and p.suffix=='.c':
                for n in sorted(exports):text=re.sub(r'\b'+re.escape(n)+r'\b','l1_'+n[2:],text)
            text=hostbuild.composition_source(rel,text,units)
            if not literal and rel=='c/memory.c':
                text=with_return_hook(text,'ugh_read','pr_vga_read(a);')
                a,b,e,n=next(x for x in bodies(text) if x[3]=='ugh_write')
                text=text[:e]+'\npr_write(a,v);\n'+text[e:]
            if not literal and rel=='c/platform.c':
                needle='e->kind=kind; e->port=port; e->size=size; e->value=value;'
                assert needle in text;text=text.replace(needle,needle+'pr_event(kind,port,size,value);')
                for n,mask in [('platform_out',79),('platform_in',79),('platform_interrupt',127),('platform_service_point_at',79),('ugh_devices_reset',255)]:
                    text=with_return_hook(text,n,f'pr_services({mask});')
            if not literal and rel=='host/main.c':
                needle='load_data(data); ugh_devices_reset(); scenario_fixture();';assert needle in text
                text=text.replace(needle,'load_data(data); pr_verify_baseline(); ugh_devices_reset(); scenario_fixture();')
                text=text.replace('HostSymbol entry=host_symbol(scenario.entry);','pr_import();\nHostSymbol entry=host_symbol(scenario.entry);')
            if not literal and rel=='host/digest.c':
                needle='void host_digest(Regs *r,const char *terminal) {';assert needle in text
                text=text.replace(needle,needle+'\npr_boundary(r,terminal);',1)
            if not literal and rel=='native/decimal.c':
                for needle in ['output->bytes[output->cursor]=digit;','output->bytes[output->cursor]=255;']:
                    if needle in text:text=text.replace(needle,needle+'pr_pointer_write(output->bytes+output->cursor,output->bytes[output->cursor]);')
                    else:assert any(name+'(' in text for name in ['audio_borrowed_store','palette_borrowed_store','input_borrowed_store'])
            if not literal and rel=='native/far_copy.c':
                needle='destination[destination_cursor]=source[source_cursor];'
                if needle in text:text=text.replace(needle,needle+'pr_pointer_write(destination+destination_cursor,destination[destination_cursor]);')
                else:assert any(name+'(' in text for name in ['audio_borrowed_store','palette_borrowed_store','input_borrowed_store'])
            if not literal and rel=='native/bridge/ice_bridge.c':
                needle='memcpy(ugh_mem+destination,output,sizeof output);'
                if needle in text:text=text.replace(needle,needle+'pr_publish(ugh_mem+destination,sizeof output);')
                else:assert 'audio_workspace_publish(' in text
            if not literal:text=instrument_publication(rel,text)
            target=folder/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
    schema=generate_schema(frozen,folder)
    for n in ['world.h','observer.h','observer.c']:shutil.copy2(ROOT/'verif/projector'/n,folder/n)
    (folder/'fallbacks.h').write_text('#include "ugh.h"\n'+''.join('int l1_'+n[2:]+'(Regs *);\n' for n in sorted(exports)))
    (folder/'units.c').write_text('#include "host.h"\nconst char *host_native_units[]={'+','.join(json.dumps(u['component']) for u in units)+'};\nconst unsigned host_native_unit_count='+str(len(units))+';\nconst char *host_variant='+json.dumps('literal' if literal else 'native-bridged')+';\n')
    mz,symbols=cgen.read_symbols() # read-only validation; never cgen.generate()
    lines=['#include "host.h"','const HostSymbol host_symbols[]={']
    lines+=['{'+json.dumps(n)+f',{cgen.LOAD+r["frame"]},{r["offset"]}'+'},' for n,r in sorted(symbols.items())]
    lines+=['};','const unsigned host_symbol_count=sizeof(host_symbols)/sizeof(host_symbols[0]);','const char host_data_hash[]="'+hashlib.sha256(mz.data).hexdigest()+'";']
    (folder/'symbols.c').write_text('\n'.join(lines)+'\n')
    shutil.copy2(ROOT/'build/link/plain/UGH.EXE',folder/'ugh-data.exe')
    raw=mz.data;word=lambda at:struct.unpack_from('<H',raw,at)[0]
    header=word(8)*16;image=bytearray(0x110000);image[cgen.LOAD*16:cgen.LOAD*16+len(raw)-header]=raw[header:]
    for i in range(word(6)):
        at=word(24)+4*i;site=cgen.LOAD*16+word(at)+16*word(at+2)
        struct.pack_into('<H',image,site,(struct.unpack_from('<H',image,site)[0]+cgen.LOAD)&65535)
    (folder/'baseline.bin').write_bytes(image)
    sources=sorted((folder/'c').glob('*.c'))+sorted((folder/'host').glob('*.c'))
    sources += [folder/u['native'] for u in units]+[folder/u['bridge'] for u in units]
    sources += [folder/'units.c',folder/'symbols.c']+([] if literal else [folder/'observer.c'])
    command=[hostbuild.GCC,'-O2','-g','-std=c11','-Wall','-Wextra','-Werror','-fwrapv',
             *hostbuild.composition_options(units,folder),
             '-include',folder/'observer.h','-include',folder/'fallbacks.h',
             '-I',folder,'-I',folder/'c','-I',folder/'host','-I',hostbuild.SDL/'include','-I',hostbuild.OPL,
             '-o',folder/'ugh.exe',*sources,hostbuild.OPL/'opl3.c','-L',hostbuild.SDL/'lib','-lSDL3','-lbcrypt']
    env=dict(os.environ,PATH=str(hostbuild.GCC.parent)+os.pathsep+os.environ.get('PATH',''))
    receipt=bounded(command,'build-literal' if literal else 'build',env)
    for dll in [hostbuild.SDL/'bin/SDL3.dll',hostbuild.GCC.parent/'libwinpthread-1.dll']:
        if dll.exists():shutil.copy2(dll,folder/dll.name)
    inputs=[p for p in inputs if p.is_file()]
    receipt.update(baseline=info,units=units,compiler_sha256=sha(hostbuild.GCC),
        executable_sha256=sha(folder/'ugh.exe'),baseline_sha256=sha(folder/'baseline.bin'),
        inputs={str(p.relative_to(ROOT)):sha(p) for p in inputs},
        frozen_inputs={str(p.relative_to(frozen)):sha(p) for top in ['c','native','host','metadata/closure'] for p in (frozen/top).rglob('*') if p.is_file()},
        rebuilt_data_sha256=sha(folder/'ugh-data.exe'),typed_bindings=len(schema['bindings']))
    save(folder/'build.json' if literal else OUT/'build.json',receipt)
    print('Built '+('literal comparator' if literal else 'projector')+':',len(schema['bindings']),'typed bindings;',len(schema['unclassified_overlapping_bindings']),'ambiguous bindings deferred to journal',flush=True)


def one(name,controls=False):
    folder=OUT/'instrumented';build=json.loads((OUT/'build.json').read_text())
    for n,h in build['inputs'].items():assert sha(ROOT/n)==h,'projector input changed: '+n
    assert sha(folder/'ugh.exe')==build['executable_sha256']
    frozen=OUT/'frozen';path=frozen/'tests/scenarios'/f'{name}.txt';smoke=name=='smoke'
    frames=256 if smoke else next(int(x.split()[1]) for x in path.read_text().splitlines() if x.startswith('frames '))
    target=OUT/'runs'/f'{name}.json';target.parent.mkdir(exist_ok=True)
    env=dict(os.environ,PR_BASELINE=str(folder/'baseline.bin'),PR_RECEIPT=str(target))
    if controls:env['PR_CONTROLS']='1'
    command=[folder/'ugh.exe','--headless',str(frames),'--timeout','590']
    command+=['--smoke','256'] if smoke else ['--script',path]
    child=bounded(command,'run-'+name,env)
    got=[json.loads(x) for x in child['stdout'].splitlines()]
    refpath=ROOT/'build/whole'/('attract.ref.json' if smoke else name+'.ref.json')
    ref=json.loads(refpath.read_text())['frames'];assert got[:len(ref)]==ref,(name,'reference mismatch')
    if smoke:
        literal=bounded([OUT/'literal/ugh.exe','--headless','256','--smoke','256','--timeout','590'],'smoke-literal')
        expected=[json.loads(x) for x in literal['stdout'].splitlines()]
        assert got==expected and len(got)==256,'full literal smoke mismatch'
    else:assert len(got)==len(ref),(name,'reference length')
    result=json.loads(target.read_text());assert result['boundaries']==len(got) and result['baseline_verified']
    if controls:assert len(result['controls'])==5 and all(x['detected'] for x in result['controls'])
    result.update(scenario=name,result='PASS',seconds=child['seconds'],matched_reference_records=len(ref),
        serialized_records=len(got),reference_sha256=sha(refpath),full_smoke_literal=smoke,
        build_sha256=sha(OUT/'build.json'),no_reference_records_imported=True)
    save(target,result);print('PASS',name,len(got),'boundaries',round(child['seconds'],2),'s',flush=True)


def summarize():
    build=json.loads((OUT/'build.json').read_text());schema=json.loads((OUT/'instrumented/schema.json').read_text())
    runs=[json.loads(p.read_text()) for p in sorted((OUT/'runs').glob('*.json'))]
    assert len(runs)==21 and all(r['result']=='PASS' for r in runs)
    for r in runs:assert r['build_sha256']==sha(OUT/'build.json')
    owner_rows=[]
    for i,name in enumerate(schema['owners']):
        typed=[b for b in schema['bindings'] if b['owner']==i]
        row=dict(name=name,bindings=len(typed),typed_bytes=sum(b['width'] for b in typed),
                 writes=sum(r['owners'][i]['write_deliveries'] for r in runs),
                 max_touched=max(r['owners'][i]['touched_bytes'] for r in runs))
        owner_rows.append(row)
    controls=next(r for r in runs if r['scenario']=='gameplay')['controls'];assert all(c['detected'] for c in controls)
    summary=dict(result='PASS',baseline=build['baseline'],owners=owner_rows,
        scenarios=[{k:r[k] for k in ['scenario','serialized_records','matched_reference_records','terminal_boundaries','seconds','events','journal_observed_bytes']} for r in runs],
        controls=controls,model_typed=sum(r['status'].startswith('typed') for r in schema['model_coverage']),
        model_total=len(schema['model_coverage']),
        scope='Write/effect-driven preservation of current host observations, not independent subsystem algorithms or a standalone production world.',
        reference_scope='20 complete cached scenario references; smoke cached96 prefix plus a fresh frozen unmodified compiled-literal256 comparator.')
    save(OUT/'summary.json',summary)
    lines=['# Owner coverage','',
           'Typed bytes are declared canonical storage, not broad alias ownership. Writes are delivered source writes, including repeated/same-value writes. Unknown overlaps are not assigned a second owner. Service fields are imported cold and updated from explicit effect seams; they are not a new device implementation.','',
           '| Owner | Bindings | Typed historical bytes | Delivered byte writes | Maximum touched bytes in one run |','|---|---:|---:|---:|---:|']
    for r in owner_rows:lines.append('| '+r['name']+' | '+' | '.join(str(r[k]) for k in ['bindings','typed_bytes','writes','max_touched'])+' |')
    lines+=['','## Named model cells','','| Cell | Coverage | Canonical field / exact alias |','|---|---|---|']
    for row in schema['model_coverage']:lines.append('| '+row['name']+' | '+row['status']+' | '+', '.join(row['bindings'])+' |')
    (OUT/'COVERAGE.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('PASS summary:',sum(r['serialized_records'] for r in runs),'boundaries;',summary['model_typed'],'/',summary['model_total'],'named cells start in typed bindings',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',action='store_true');p.add_argument('--literal',action='store_true')
    p.add_argument('--revision',default=BASELINE_REVISION,help='committed seam checkpoint (default: accepted pre-composition baseline)')
    p.add_argument('--one');p.add_argument('--controls',action='store_true');p.add_argument('--all',action='store_true');p.add_argument('--summarize',action='store_true')
    a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    if a.build:build(a.literal,a.revision)
    if a.one:one(a.one,a.controls)
    if a.summarize:summarize()
    if a.all:
        bounded([sys.executable,__file__,'--build','--revision',a.revision],'driver-build')
        bounded([sys.executable,__file__,'--build','--literal','--revision',a.revision],'driver-build-literal')
        for path in sorted((OUT/'frozen/tests/scenarios').glob('*.txt')):
            args=['--one',path.stem]+(['--controls'] if path.stem=='gameplay' else [])
            child=bounded([sys.executable,__file__,*args],'driver-'+path.stem);print(child['stdout'],end='',flush=True)
        child=bounded([sys.executable,__file__,'--one','smoke'],'driver-smoke');print(child['stdout'],end='',flush=True)
        summarize()


if __name__=='__main__':main()
