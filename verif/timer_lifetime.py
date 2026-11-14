"""Timer-lifetime evidence and committed-baseline replay; no maintained L1 edits.

All evidence children use the accepted worker runner's owned 8-GiB/600-s Job.
The production-facing API uses typed requests and opaque provider bindings.
Only bridges construct compatibility stack frames or interpret machine words.
"""
import argparse,ctypes as C,hashlib,io,json,os,re,shutil,subprocess,sys,tarfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/workers/close-stones-15'
sys.path.insert(0,str(ROOT/'tools'))
from closure_support import GCC,hashes,save,function
import ice_scratch as runner
runner.OUT=OUT
bounded=runner.bounded

ENTRIES=['InstallTimerInterrupt','RestoreTimerInterrupt','ChainSavedTimerInterrupt',
         'RegisterTimerCallbackFromStack','RemoveTimerCallbackFromStack','loc_032F']
CANONICAL=['RegisterTimerCallback','RemoveTimerCallback','SetTimerCallbackInterval','HandleTimerInterrupt']
FILES=['native/timer_lifetime.c','native/timer_lifetime.h','native/bridge/timer_lifetime_bridge.c',
       'verif/timer_lifetime.py','verif/timer_lifetime_protocol.c','metadata/closure/timer_lifetime.json']

def sources():
    return [ROOT/p for p in FILES if not p.endswith('.json')]+[ROOT/p for p in
        ['native/timer.c','native/timer.h','native/bridge/timer_bridge.c','verif/ice_scratch.py',
         'verif/closure_support.py','verif/windows_job.py','metadata/verif-tools.json',
         'verif/timer_evidence.py','verif/timer_enumeration.c','verif/timer_projection.py',
         'verif/timer_callbacks.py','tools/difftest.py','tools/emu.py','tools/hostbuild.py',
         'host/check.py','tools/wholegame.py','verif/standalone_census.py','src/asm/TIMER.ASM',
         'metadata/closure/timer.json','metadata/program-model.json','tests/timer.py',
         'tests/timer_stack.py','tests/timer_system.py']]+list((ROOT/'c').glob('*.[ch]'))+list((ROOT/'c').glob('*.inc'))

def build(tag='native',mutant=None):
    import nbuild
    folder=OUT/tag;folder.mkdir(parents=True,exist_ok=True)
    selected=ENTRIES+CANONICAL if tag!='reference' else []
    files=[]
    for p in sorted((ROOT/'c').glob('*.c')):
        text=p.read_text()
        for name in selected:text=re.sub(r'\bc_'+name+r'\b','l1_'+name,text)
        target=folder/p.name;target.write_text(text);files.append(target)
    if selected:
        for name in ['native/timer.c','native/bridge/timer_bridge.c',*FILES[:3:2]]:
            p=ROOT/name;text=p.read_text()
            if mutant and name==mutant[0]:
                assert mutant[1] in text;text=text.replace(mutant[1],mutant[2])
            text=re.sub(r'#include "([^"]+)"',lambda m:'#include "'+(p.parent/m[1]).resolve().as_posix()+'"'
                        if (p.parent/m[1]).is_file() else m[0],text)
            target=folder/('native_'+p.name);target.write_text(text);files.append(target)
    declarations=folder/'fallbacks.h'
    declarations.write_text('#include "ugh.h"\n'+''.join('int l1_'+n+'(Regs *);\n' for n in selected))
    dll=folder/'timer.dll';command=[GCC,'-shared','-O2','-std=c11','-Wall','-Wextra','-Werror','-fwrapv',
         '-I',ROOT/'c','-include',declarations,'-o',dll,*files]
    row=bounded(command,tag+'-compile');row['inputs']=hashes([*files,declarations,*sources()])
    row['compiler_sha256']=hashlib.sha256(GCC.read_bytes()).hexdigest();save(OUT/(tag+'-compile.json'),row)
    return nbuild.load_l1(dll)

def compare(reference,native,initial,r,name,device=None):
    from difftest import MEM_SIZE,Regs
    result=[]
    for dll in [reference,native]:
        mem=dll.ugh_memory().contents;C.memmove(mem,initial,MEM_SIZE);dll.ugh_devices_reset()
        if device is not None:C.memmove(C.addressof(dll.ugh_device_state().contents),device,len(device))
        actual=Regs.from_buffer_copy(r);fn=getattr(dll,'c_'+name);fn.argtypes=[C.POINTER(Regs)]
        status=fn(C.byref(actual));result.append((status,bytes(actual),bytes(mem),bytes(dll.ugh_device_state().contents)))
    return result

def projection_check():
    original=(ROOT/'native/bridge/timer_bridge.c').read_text();new=(ROOT/FILES[2]).read_text()
    for name in ['timer_word_token','timer_token_word','timer_project','timer_publish']:
        old=function(original,name).replace('    if((last&1) || last>30) return 0;\n','')
        for n in ['timer_word_token','timer_token_word','timer_project','timer_publish']:old=old.replace(n,'lifetime_'+n[6:])
        assert old==function(new,'lifetime_'+name[6:]),name+' projection copy drift'

def cases():
    import difftest
    from difftest import Regs
    from emu import Machine
    reference=build('reference');native=build();m=Machine();rows=[]
    projection_check()
    for suite in ['timer','timer_stack','timer_system','timer_callbacks']:
        mod=__import__(suite) if suite=='timer_callbacks' else difftest.load_suite(suite)
        for case in mod.CASES:
            for poison in [False,True]:
                for label,dll in [('L1',reference),('native',native)]:
                    problems=difftest.run(case,m,dll,poison)
                    rows.append(dict(suite=suite,case=case.title,target=label,poison=poison,problems=problems))
                    assert not problems,(suite,case.title,label,problems)
    save(OUT/'cases.json',dict(result='PASS',cases=rows,inputs=hashes(sources()),
         image_sha256=hashlib.sha256(m.raw_image).hexdigest(),scope='Maintained timer/stack/system suites plus descending callback mutation case, L0 vs pure L1 and native bridges; malformed canonical API cases retain that accepted unit\'s explicit L1 fallback, not this adapter\'s admission.'))
    print('Unicorn cases',len(rows),'PASS',flush=True)

def seed(m,count=4):
    from difftest import Regs
    m.reset()
    import random
    rng=random.Random(15032)
    for name in ['TimerIntervalLowBySlot','TimerIntervalHighBySlot','TimerRemainingLowBySlot',
                 'TimerRemainingHighBySlot','TimerCallbackDueBySlot','TimerHandleBySlot',
                 'TimerSlotOffsetByHandle','TimerCallbackOffsetBySlot','TimerCallbackSegmentBySlot']:
        for i in range(16):m.ww('DGROUP:'+name,rng.randrange(65536),i*(4 if 'CallbackOffset' in name or 'CallbackSegment' in name else 2))
    m.ww('DGROUP:LastActiveTimerSlotOffset',(count-1)*2)
    for i in range(16):
        m.ww('DGROUP:TimerSlotOffsetByHandle',i*2 if i<count else 0x8000,i*2)
        m.ww('DGROUP:TimerHandleBySlot',i*2,i*2)
    m.ww('DGROUP:ProgrammedPitDivisor',0x3456)
    m.ww('DGROUP:PreviousInt08Offset',0x100);m.ww('DGROUP:PreviousInt08Segment',0xf000)
    m.ww('TIMER:TimerInterruptInstalled',0)
    m.write(0,0x20,b'\x00\x01\x00\xf0')
    r=Regs(ax=0x12ab,bx=0x3456,cx=0x789a,dx=0xbcde,si=0xf012,di=0x3456,bp=0x6789,
           ds=m.seg('DGROUP:PreviousInt08Offset'),es=0x4500,cs=m.seg('TIMER:TimerInterruptInstalled'),
           ss=0x9000,sp=0x200,ip=0x4567,flags=0x402)
    return m.snapshot(),r

def observed(dll,initial,r,name,fail_at=0,status=7,mutate_get=False):
    from difftest import MEM_SIZE,Regs
    mem=dll.ugh_memory().contents;C.memmove(mem,initial,MEM_SIZE);dll.ugh_devices_reset()
    actual=Regs.from_buffer_copy(r);journal=[];calls=0
    # All RAM at matching cuts, with actual working registers and ordered I/O.
    def cut(event):journal.append((event,bytes(actual),bytes(mem)))
    INTERRUPT=C.CFUNCTYPE(C.c_int,C.c_uint8,C.POINTER(Regs))
    OUTPUT=C.CFUNCTYPE(None,C.c_uint16,C.c_uint,C.c_uint32)
    def interrupt(number,rp):
        nonlocal calls
        calls+=1;cut(('DOS',number,rp.contents.ax))
        if mutate_get and rp.contents.ax==0x3508:
            # A successful service can update an inactive record before the
            # continuation. Reborrow the owner at this cut, not before service.
            import re
            symbols=(ROOT/'c/ugh_sym.h').read_text()
            base=int(re.search(r'#define UGH_O_DGROUP_TimerCallbackDueBySlot (0x[0-9A-Fa-f]+)',symbols)[1],16)
            at=rp.contents.ds*16+base+30;mem[at]^=0x5a
        return status if calls==fail_at else -1
    def output(port,size,value):cut(('OUT',port,size,value))
    icb=INTERRUPT(interrupt);ocb=OUTPUT(output)
    dll.ugh_set_interrupt_service.argtypes=[INTERRUPT];dll.ugh_set_output_observer.argtypes=[OUTPUT]
    dll.ugh_set_interrupt_service(icb);dll.ugh_set_output_observer(ocb)
    try:
        fn=getattr(dll,'c_'+name);fn.argtypes=[C.POINTER(Regs)];code=fn(C.byref(actual))
    finally:
        dll.ugh_set_interrupt_service(INTERRUPT());dll.ugh_set_output_observer(OUTPUT())
    return code,bytes(actual),bytes(mem),bytes(dll.ugh_device_state().contents),journal

def extra():
    from difftest import Regs,MEM_SIZE
    from emu import Machine
    reference=build('reference');native=build();m=Machine();initial,r=seed(m)
    records=[]
    for name,fail_at in [('InstallTimerInterrupt',0),('InstallTimerInterrupt',1),('InstallTimerInterrupt',2),
                         ('RestoreTimerInterrupt',0),('RestoreTimerInterrupt',1),('ChainSavedTimerInterrupt',0)]:
        for error in ([1,2,3,4,7] if fail_at else [0]):
            image=bytearray(initial)
            at=m.seg('TIMER:TimerInterruptInstalled')*16+m.off('TIMER:TimerInterruptInstalled')
            image[at:at+2]=(1 if name=='RestoreTimerInterrupt' else 0).to_bytes(2,'little')
            a=observed(reference,bytes(image),r,name,fail_at,error)
            b=observed(native,bytes(image),r,name,fail_at,error)
            assert a==b,(name,fail_at,error,'matching-cut journal')
            records.append(dict(entry=name,failure_call=fail_at,error=error,events=[e[0] for e in a[-1]]))
    a=observed(reference,initial,r,'InstallTimerInterrupt',mutate_get=True)
    b=observed(native,initial,r,'InstallTimerInterrupt',mutate_get=True)
    assert a==b,'successful GET must reborrow inactive state'
    records.append(dict(entry='InstallTimerInterrupt',service_mutation='inactive due after GET',events=[e[0] for e in a[-1]]))
    # Complete installed-word slice and a complete incoming-FLAGS slice. The
    # full-RAM and device cut comparisons above cover active transitions; these
    # scalar slices check actual complete-register publication at every value.
    flag_address=m.seg('TIMER:TimerInterruptInstalled')*16+m.off('TIMER:TimerInterruptInstalled')
    slices=[]
    for name,field in [('InstallTimerInterrupt','installed'),('RestoreTimerInterrupt','installed'),
                       ('ChainSavedTimerInterrupt','flags')]:
        for dll in [reference,native]:C.memmove(dll.ugh_memory().contents,initial,MEM_SIZE);dll.ugh_devices_reset()
        for value in range(65536):
            observations=[]
            for dll in [reference,native]:
                mem=dll.ugh_memory().contents
                if field=='installed':mem[flag_address]=value&255;mem[flag_address+1]=value>>8
                dev=dll.ugh_device_state().contents;dev.count=0
                actual=Regs.from_buffer_copy(r)
                if field=='flags':actual.flags=value
                fn=getattr(dll,'c_'+name);fn.argtypes=[C.POINTER(Regs)]
                code=fn(C.byref(actual));observations.append((code,bytes(actual)))
            assert observations[0]==observations[1],(name,field,value)
            if value in [0,1,0x7fff,0x8000,0xfffe,0xffff]:
                assert bytes(reference.ugh_memory().contents)==bytes(native.ugh_memory().contents)
                assert bytes(reference.ugh_device_state().contents)==bytes(native.ugh_device_state().contents)
        slices.append(dict(entry=name,field=field,cases=65536))
    # All physical slot orders, counts and requested handles, including duplicate
    # mappings and arbitrary fragmented target words; this exercises both bugs.
    mapped=0
    for count in range(2,17):
        for destination in range(count):
            for handle in [0,2,30]:
                initial,rr=seed(m,count);image=bytearray(initial)
                base=m.seg('DGROUP:TimerSlotOffsetByHandle')*16+m.off('DGROUP:TimerSlotOffsetByHandle')
                image[base+handle:base+handle+2]=(destination*2).to_bytes(2,'little')
                image[rr.ss*16+rr.sp+4:rr.ss*16+rr.sp+10]=handle.to_bytes(2,'little')+b'\xa5\x5a\x01\x80'
                for name in ['RemoveTimerCallbackFromStack','loc_032F']:
                    a,b=compare(reference,native,bytes(image),rr,name);assert a==b,(count,destination,handle,name)
                    mapped+=1
    registered=0
    for callback in ['TIMER:ChainSavedTimerInterrupt','SOUND:AdvanceMusicFade','SOUND:TickAdlxPlayback',
                     'SOUND:ClearSoundState','TIMER:HandleTimerInterrupt']:
        for count in [1,15]:
            for interval in [0,1,65535,65536,0x7fffffff,0x80000000,0xffffffff]:
                for free in [0,count]:
                    initial,rr=seed(m,count);image=bytearray(initial)
                    base=m.seg('DGROUP:TimerSlotOffsetByHandle')*16+m.off('DGROUP:TimerSlotOffsetByHandle')
                    for index in range(free+1,count+1):image[base+index*2:base+index*2+2]=b'\0\0'
                    image[base+free*2:base+free*2+2]=b'\0\x80'
                    raw=m.off(callback).to_bytes(2,'little')+m.seg(callback).to_bytes(2,'little')+interval.to_bytes(4,'little')
                    p=rr.ss*16+rr.sp+4;image[p:p+8]=raw
                    a,b=compare(reference,native,bytes(image),rr,'RegisterTimerCallbackFromStack')
                    assert a==b,(callback,count,interval,free);registered+=1
    admissions=[]
    for name,handle,count,last in [('RegisterTimerCallbackFromStack',0,16,30),
            ('RemoveTimerCallbackFromStack',1,4,6),('RemoveTimerCallbackFromStack',32,4,6),
            ('RemoveTimerCallbackFromStack',0,4,7)]:
        initial,rr=seed(m,count);image=bytearray(initial)
        at=m.seg('DGROUP:LastActiveTimerSlotOffset')*16+m.off('DGROUP:LastActiveTimerSlotOffset')
        image[at:at+2]=last.to_bytes(2,'little');p=rr.ss*16+rr.sp+4
        image[p:p+8]=handle.to_bytes(2,'little')+b'\x00\x00\x01\x00\x00\x00'
        mem=native.ugh_memory().contents;C.memmove(mem,bytes(image),MEM_SIZE)
        fn=getattr(native,'c_'+name);fn.argtypes=[C.POINTER(Regs)]
        assert fn(C.byref(rr))==1,(name,handle,last)
        admissions.append(dict(entry=name,handle=handle,last=last,result='REJECTED_WITHOUT_L1'))
    # Accepted projection's exhaustive enumeration/corpus, rerun in owned paths.
    import timer_evidence,timer_projection
    timer_evidence.OUT=OUT/'accepted-core';timer_evidence.enumerate_cases()
    timer_projection.OUT=OUT/'accepted-projection';timer_projection.main()
    save(OUT/'extra.json',dict(result='PASS',service_prefixes=records,slices=slices,
         mapped_removals=mapped,registrations=registered,admissions=admissions,inputs=hashes(sources()),
         static_reachability={name:json.loads((ROOT/'metadata/program-model.json').read_text())['routines']['TIMER:'+name]
                              for name in ENTRIES}))
    print('extra PASS',len(records),'prefixes',mapped,'mapped removals',flush=True)

def mutations():
    from emu import Machine
    reference=build('reference');m=Machine();initial,r=seed(m)
    module='native/timer_lifetime.c';bridge='native/bridge/timer_lifetime_bridge.c'
    specs=[('clear_due',(module,'state->count=1;','state->count=1; state->slots[0].due=0;'),'InstallTimerInterrupt'),
      ('quantum',(module,'state->quantum=65536u;','state->quantum=65535u;'),'InstallTimerInterrupt'),
      ('map_zero',(module,'state->by_handle[0]=0;','state->by_handle[0]=TIMER_FREE;'),'InstallTimerInterrupt'),
      ('saved_binding',(bridge,'D(PreviousInt08Offset),offset);','D(PreviousInt08Offset),(uint16_t)(offset+1));'),'InstallTimerInterrupt'),
      ('missing_pit',(module,'request->kind=TIMER_LIFETIME_RESET_PIT;','request->kind=TIMER_LIFETIME_NONE;'),'RestoreTimerInterrupt'),
      ('pit_command',(module,'request->pit_command=0x36;','request->pit_command=0x34;'),'RestoreTimerInterrupt'),
      ('disabled_chain',(module,'request->enable_interrupts=1;','request->enable_interrupts=0;'),'ChainSavedTimerInterrupt'),
      ('unconsumed',(module,'request->kind=TIMER_LIFETIME_NONE;','request->kind=TIMER_LIFETIME_BIND_TIMER;'),'InstallTimerInterrupt'),
      ('stack_interval',(bridge,'request.interval=r->bx | (uint32_t)r->cx*65536u;',
                         'request.interval=r->cx | (uint32_t)r->bx*65536u;'),'RegisterTimerCallbackFromStack'),
      ('wrong_stride',('native/timer.c','timer_remove_wrong_stride(state,tail,destination);',
                         'timer_remove_wrong_stride(state,tail*2,destination*2);'),'RemoveTimerCallbackFromStack'),
      ('wrong_map',('native/timer.c','state->by_handle[0]=result;','state->by_handle[result/2]=(uint16_t)(destination*2);'),'RemoveTimerCallbackFromStack'),
      ('wrong_032f',(bridge,'lifetime_stack(r,2,','lifetime_stack(r,0,'),'loc_032F')]
    specs.append(('stale_cut',(bridge,
        '    lifetime_project(&state,open); state.installed=rd16(r->cs,T(TimerInterruptInstalled));\n',''),
        'InstallTimerInterrupt'))
    rows=[]
    for label,change,name in specs:
        dll=build('mutant-'+label,change);initial,rr=seed(m,4);image=bytearray(initial)
        if name=='RestoreTimerInterrupt':
            p=m.seg('TIMER:TimerInterruptInstalled')*16+m.off('TIMER:TimerInterruptInstalled');image[p:p+2]=b'\x01\0'
        if name.endswith('FromStack') or name=='loc_032F':
            args=[0,0xa55a,0x8001]
            if name=='RegisterTimerCallbackFromStack':
                args=[m.off('SOUND:ClearSoundState'),m.seg('SOUND:ClearSoundState'),0x1234,0x5678]
            p=rr.ss*16+rr.sp+4;raw=b''.join(x.to_bytes(2,'little') for x in args);image[p:p+len(raw)]=raw
        if label=='stale_cut':
            a=observed(reference,bytes(image),rr,name,mutate_get=True)
            b=observed(dll,bytes(image),rr,name,mutate_get=True)
        else:a,b=compare(reference,dll,bytes(image),rr,name)
        assert a!=b,(label,'SURVIVED')
        rows.append(dict(name=label,change=change,entry=name,result='DETECTED_BY_BRIDGE',l1_status=a[0],native_status=b[0]))
    save(OUT/'mutations.json',dict(result='PASS',controls=rows));print(len(rows),'mutants detected',flush=True)

def certificate():
    import closure
    owned=FILES[:3];locations=['0008','00A0','0099','030E','0323','032F']
    cert=dict(component='timer_lifetime',status='unanalyzed',proposed_status='migrated',
       proposed_status_reason='Actual-C B covers protocol/frame, full-capacity admitted typed registration/removal and successful-get baseline initialization. Full bridge/service shell remains C with D composition; no all-state or instruction-interleaving claim.',
       original=dict(owned=[dict(identity='TIMER:'+n,address='0A32:'+o) for n,o in zip(ENTRIES,locations)],
            L0=['src/asm/TIMER.ASM install/restore/chain and three far-cdecl adapters'],
            L1=['c/timer_system.c:c_InstallTimerInterrupt/c_RestoreTimerInterrupt/c_ChainSavedTimerInterrupt',
                'c/timer_stack.c:c_RegisterTimerCallbackFromStack/c_RemoveTimerCallbackFromStack/c_loc_032F']),
       native=dict(files=owned,header='native/timer_lifetime.h',
            functions=['timer_lifetime_install','timer_lifetime_restore','timer_lifetime_chain','timer_lifetime_consume','timer_lifetime_apply'],
            bridge=['c_'+n for n in ENTRIES],build='python verif/timer_lifetime.py --cases'),
       purpose='Timer-owned additive lifetime/ABI adapter over the accepted TimerState scheduler. A provider-owned opaque external binding and explicit successful-service requests replace the native-facing vector/IRET/stack shell; no second scheduler or timer state owner.',
       interface=dict(inputs=['Borrowed TimerState, TimerLifetime saved provider binding, and per-operation request/result objects; initialized, ordinary, disjoint storage.',
                'Installation consumes installed as a literal truth word. Incoming count/maps/records are stale until successful binding read; no old-count validation is needed for baseline initialization.',
                'Stack entry admits accepted timer API states: aligned last offset 0..30, register count<16 with free marker at/below new index and a named callback, remove count>=2 and an even handle with an aligned active map. Bijection is not assumed.'],
            outputs=['Install: NONE if already active, otherwise installed=1 then READ_BINDING; successful reply saves binding and initializes baseline before BIND_TIMER.',
                'Restore: NONE if inactive, otherwise installed=0 then BIND_SAVED; only successful binding emits RESET_PIT command36/low0/high0; successful consumption ends at NONE.',
                'Chain: DELIVER of saved typed binding with enable_interrupts=1. Test backend directly delivers BIOS day-clock/midnight/EOI effects at the same cut.',
                'Typed REGISTER/REMOVE requests invoke accepted timer API. Result contains handle and minimum; the bridge alone loads stack words and publishes register clobbers.'],
            service_failure='Failed service is not consumed. Preserve installed flag and all preceding state/I/O. Failed install GET leaves DS=DGROUP; failed install SET restores incoming DS; failed restore SET leaves DS at saved external segment with no PIT reset.',
            normal_completion='Bridge requires each expected kind and successful matching consumption, then NONE; no unconsumed normal request is accepted.',
            projection='Canonical timer RAM remains shared with the accepted timer bridge. Four private projection helpers are checked exact copies, with only old-count admission removed for installation. Reborrow after service success and before its continuation; a GET-time inactive-slot write survives initialization. Count is not republished until successful GET initializes it. Other operations explicitly enforce API admission. The saved binding provider maps bridge-local identities 1/2 to raw old/reply vector words; those words exist only in the compatibility adapter.'),
       callers=['Native lifecycle and audio bridges use stable existing TIMER entry ABI for install/restore.',
                'Accepted timer ISR invokes chain as its baseline callback, after live descending callback consumption.',
                'Three stack entries have no recorded internal callers; public direct entry remains admitted and tested. loc_032F targets REMOVE, not interval setter.'],
       callees=dict(native=['timer_target','timer_register','timer_remove','timer_handle_slot'],
            services=['read external binding','bind timer interrupt role','restore saved external binding','reset PIT','deliver typed external role'],
            backend=['DOS21 vector services and PIT writes in bridge only; direct platform_bios_timer for the BIOS role.',
                     'OTHER binding retains accepted explicit IRET services or BAD_CALLBACK, not an implicit BIOS default. No L1 timer-lifetime body is called.']),
       indirect=dict(native='No indirect C call in the ordinary adapter; request kind, callback role and provider identity are data.',
            BIOS='Saved external INT08 binding, not invented game code. Typed BIOS role replaces numeric/far dispatch on shipped fixture path.',
            open='Provider may retain other external identities. Compatibility backend uses existing IRET-service admission for OTHER and retains failure prefix. Four external hooks are unchanged.'),
       memory=dict(owner='One accepted TimerState plus saved provider binding; borrowed projections only.',
            writes=['Install flag before GET; saved external binding and baseline arrays/maps only after successful GET.',
                    'Install initializes slot0 interval/remaining/target/handle, count, maps, earliest and quantum. All due fields, inactive records and programmed divisor survive.',
                    'Restore changes installed only, restores external binding and emits PIT reset. Cached programmed divisor stays stale.',
                    'Register/remove effects are exactly accepted scheduler writes, including wrong callback-word stride, moved handle not repaired and handle-zero map defect.'],
            shell='Bridge retains compatibility stack save/far/IRET bytes and live working registers for verification. Native API has no registers, original addresses, dispatcher or mutable global machine.'),
       assumptions=['Single serialized operation, matching accepted deterministic virtual PIT/service cuts. No proof of arbitrary instruction-level IRQ interleavings.',
            'Ordinary synchronous timer storage and installed flag, disjoint from live stack, code/table/device aliases; immutable callback identity bindings.',
            'Native pointers/objects nonnull and disjoint where read/written; request payload validity is defined by kind. Non-NONE service is consumed once only after successful delivery.',
            'External binding service preserves ordinary vector-service register contract; it may fail with a nonzero status, retaining prefix. No unknown external handler is assumed to be BIOS.',
            'Stack requests retain accepted named callback and aligned physical-prefix/handle admission, including arbitrary map aliases and callback fragments during removal. Rejected new-entry admission returns unsupported without L1.',
            'B uses full sixteen-slot initialized state, full scalar widths and aligned normalized timer-RAM view from accepted evidence. Baseline initialization is proved at the successful GET seam. Bridge flags, stack bytes and platform service implementation remain C.'],
       eliminated=['Native-facing DOS vectors and PUSHF/far-IRET become provider binding plus typed DELIVER with interrupt-enable policy.',
            'Stack-word interpretation and compatibility frame creation stay solely in bridge; native typed API calls the accepted scheduler directly.',
            'All six former L1 entry bodies are replaced, with no new fallback. Existing timer unit/native files/certificate remain unchanged.'],
       retained=['Literal truth-word install/restore guards, stale due/records/divisor, baseline period/remaining/quantum/minimum65536 and public handle-zero map.',
            'PIT reset order36,0,0 after successful external binding restoration; saved binding survives restore.',
            'STI before external delivery, test-backend BIOS midnight/day-clock wrap and EOI order, callback clobber and frame effects.',
            'loc_032F still REMOVE; trailing BX/CX loads are ignored by removal, then replaced by minimum. Wrong stride and wrong handle-map repairs are deliberately not fixed.'],
       evidence=[],amiga=dict(classification='not-used',finding='DOS timer lifetime/ABI shell and accepted scheduler establish the boundary.'),
       uncertainty=['Bridge/device/working-register shell has C and D, not whole-function B. No production linker or all-level execution claim.',
            'Dormant independent L1 copies remain linked in verification host; runtime census is not universal unreachability proof.',
            'OTHER external bindings and malformed stack requests stay explicit service/admission boundaries, not default success.'],
       dependencies={p:closure.actual_dependencies(ROOT/p) for p in owned},
       verification_input_hashing='sha256-lf-text',
       verification_inputs={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest() for p in sources()},
       verification_tools=dict(gcc=dict(exe=str(GCC),sha256=hashlib.sha256(GCC.read_bytes()).hexdigest()),
                               cbmc=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']))
    specs=[('actual-C protocol, frame and successful-get baseline; typed API relation','B','CBMC on actual native C and mechanically extracted actual L1 baseline; accepted full-capacity symbolic API harness invokes actual new adapter',
            '--proof','PASS seven profiles; full scalar widths/sixteen slots, complete unwind18; no codec/model substitution','proof.json'),
           ('Unicorn L0/L1/native contracts and IRQ callback mutation','C','Maintained timer, timer_stack, timer_system and timer_callbacks suites, ordinary and poisoned inputs, rebuilt ASM vs pure L1 and selected native bridges',
            '--cases','PASS 472 comparisons; canonical malformed cases retain the accepted old timer unit\'s explicit fallback, not a new lifetime-entry fallback','cases.json'),
           ('matching-cut service journals, errors, scalar slices and maps','C','Full RAM/register/device pairs plus ordered services at actual working cuts; seeded failure injection, full installed/FLAGS slices, mapped removals, accepted core enumeration/projection replay',
            '--extra','PASS 19 service-prefix cases including GET-time inactive-slot mutation, three65536-value slices,810 mapped removals,140 named-role registrations and four rejected admissions; existing timer corpus and projection enumeration pass','extra.json'),
           ('semantic and bridge mutants','C','Seed stale-field, quantum, map, saved binding, PIT omission/command, STI, unconsumed request, stack interval, wrong-stride/wrong-map and loc_032F mutations',
            '--mutations','PASS13/13 DETECTED_BY_BRIDGE including stale pre-service projection','mutations.json'),
           ('clean baseline host and retirement census','D','Committed HEAD archive plus only worker-owned overlay, scratch certificate promotion, actual unmodified closure/build/wholegame/host/check/census CLIs',
            '--accept','PASS43 certificates/0 errors, native/literal21/21, all20 scenarios plus smoke; six L1 entry bodies0 and fallbacks0','acceptance.json')]
    for prop,level,method,arg,result,artifact in specs:
        cert['evidence'].append(dict(property=prop,level=level,method=method,command='python verif/timer_lifetime.py '+arg,
                                    result=result,date='2026-11-14',artifact='build/workers/close-stones-15/'+artifact))
    save(ROOT/'metadata/closure/timer_lifetime.json',cert)

def solver(command,folder,timeout):
    row=bounded(command,'solver-'+Path(folder).name,ok=(0,10))
    log=row['stdout']+row['stderr'];(Path(folder)/'cbmc.log').write_text(log)
    return row['returncode'],row['seconds'],log

def proof():
    import closure_support as support
    support.run_solver=solver
    for mode in range(4):
        folder=OUT/f'protocol-{mode}'
        result=support.cbmc(ROOT/'verif/timer_lifetime_protocol.c',folder,sources(),unwind=18,timeout=600,
                            defines=['-DPROFILE='+str(mode)])
        assert result['result']=='PASS',result
    # Reuse the accepted actual-C RAM projection and symbolic-state assumptions;
    # replace ONLY the native API invocation with the actual typed adapter.
    import timer_evidence as evidence
    evidence.OUT=OUT/'api';accepted_cbmc=evidence.cbmc
    def composed(harness,folder,inputs,**kwargs):
        text=harness.read_text().replace('int main(void)',
             '#include "'+(ROOT/'native/timer_lifetime.c').as_posix()+'"\nint main(void)')
        text=text.replace('int result=timer_register(&state,TIMER_ADLX_PLAYBACK,interval);',
             'TimerApiRequest request={TIMER_API_REGISTER,TIMER_ADLX_PLAYBACK,interval,0}; TimerApiResult reply; CHECK(timer_lifetime_apply(&state,&request,&reply),"typed register admitted"); int result=reply.handle;')
        text=text.replace('uint16_t result=timer_remove(&state,handle);',
             'TimerApiRequest request={TIMER_API_REMOVE,TIMER_OPEN,0,handle}; TimerApiResult reply; CHECK(timer_lifetime_apply(&state,&request,&reply),"typed remove admitted"); uint16_t result=reply.handle; CHECK(reply.minimum==state.earliest,"typed minimum");')
        harness.write_text(text)
        return accepted_cbmc(harness,folder,[*inputs,*sources()],**kwargs)
    evidence.cbmc=composed
    evidence.prove('register',16,600,False,symbolic=True)
    evidence.prove('remove',16,600,False,symbolic=True)
    # Actual L1 successful-get initialization block, including its entire map
    # loop, versus the native successful read-binding transition.
    folder=OUT/'baseline-proof';inputs=evidence.pair(folder)
    literal=function((ROOT/'c/timer_system.c').read_text(),'c_InstallTimerInterrupt')
    literal=literal[literal.index('    wr16(r->ds,D(PreviousInt08Offset)'):literal.index('    r->ax=TIMER_SEG; r->ds=r->ax;')]
    harness=folder/'harness.c';harness.write_text('''void __CPROVER_assert(_Bool,const char *);
void __CPROVER_assume(_Bool); void __CPROVER_havoc_object(void *);
#define CHECK __CPROVER_assert
#include "pair.inc"
#include "'''+(ROOT/'native/timer_lifetime.c').as_posix()+'''"
static void original_baseline(Regs *r) {
'''+literal+'''}
int main(void) {
 __CPROVER_havoc_object(words); TimerState state;project(&state);
 state.installed=0;state.programmed_divisor=rd16(DATA_SEG,D(ProgrammedPitDivisor));
 TimerLifetime life; TimerExternalBinding reply; TimerLifetimeRequest request;
 timer_lifetime_install(&state,&request);
 CHECK(timer_lifetime_consume(&state,&life,&request,TIMER_LIFETIME_READ_BINDING,reply),"accepted GET");
 Regs original;original.ds=DATA_SEG;original_baseline(&original);
 compare(&state,1);
 CHECK(rd16(DATA_SEG,D(TimerCallbackOffsetBySlot))==T(ChainSavedTimerInterrupt),"original chain role");
 CHECK(rd16(DATA_SEG,D(TimerCallbackSegmentBySlot))==TIMER_SEG,"original timer role");
 CHECK(state.slots[0].target.first==TIMER_ENTRY_CHAIN && state.slots[0].target.second==TIMER_GROUP_TIMER,"typed chain role");
 CHECK(state.programmed_divisor==rd16(DATA_SEG,D(ProgrammedPitDivisor)),"stale divisor");
 CHECK(state.installed==1 && request.kind==TIMER_LIFETIME_BIND_TIMER,"publication before binding");
 CHECK(life.saved.role==reply.role && life.saved.identity==reply.identity,"binding retained");
}''')
    result=accepted_cbmc(harness,folder,[*inputs,*sources()],unwind=18,timeout=600)
    assert result['result']=='PASS',result
    save(OUT/'proof.json',dict(result='PASS',profiles=[str(p.relative_to(ROOT)) for p in OUT.rglob('result.json')
         if p.parent.name.startswith(('protocol-','cbmc_register','cbmc_remove','baseline-proof'))],inputs=hashes(sources()),
         scope='Actual native protocol/frame and mismatched-consumption properties; full-capacity symbolic typed API vs actual L1 under accepted aligned timer-RAM admission; actual L1 install baseline block vs native successful binding transition. All bounds fully cover sixteen slots.'))

def snapshot():
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    target=OUT/('baseline-'+revision[:12]);target.mkdir(parents=True,exist_ok=True);pin=target/'.closure-baseline.json'
    if pin.exists():assert json.loads(pin.read_text())['revision']==revision
    else:
        archive=subprocess.check_output(['git','archive','--format=tar',revision],cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            for member in tar.getmembers():
                if not member.isfile():continue
                p=(target/member.name).resolve();assert p.is_relative_to(target.resolve())
                data=tar.extractfile(member).read();current=ROOT/member.name
                if current.is_file() and current.read_bytes().replace(b'\r\n',b'\n')==data.replace(b'\r\n',b'\n'):data=current.read_bytes()
                p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        save(pin,dict(revision=revision,overlay=FILES))
    for name in FILES:
        p=target/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
    p=target/'metadata/closure/timer_lifetime.json';cert=json.loads(p.read_text());cert['status']='migrated';save(p,cert)
    refs=target/'build/whole';refs.mkdir(parents=True,exist_ok=True)
    for p in (ROOT/'build/whole').glob('*.ref.json'):shutil.copyfile(p,refs/p.name)
    save(OUT/'baseline.json',dict(revision=revision,overlay_inputs=hashes([ROOT/p for p in FILES])))
    return target

def accept():
    target=snapshot();ledger=target/'build/workers/c-close/call-edges.json'
    if not ledger.exists():ledger.parent.mkdir(parents=True,exist_ok=True);save(ledger,[])
    commands=[['tools/closure.py'],['tools/build.py'],['tools/wholegame.py'],['tools/hostbuild.py'],
        ['host/check.py','--variant','native'],['tools/hostbuild.py','--literal'],
        ['host/check.py','--variant','literal'],['verif/standalone_census.py','--all']]
    rows=[]
    for i,args in enumerate(commands):
        rows.append(bounded([sys.executable,*args],'accept-'+str(i),cwd=target))
        if args[0]=='host/check.py':
            label=args[-1];shutil.copyfile(target/'build/workers/host-native'/('host-check-'+label+'.json'),OUT/('host-'+label+'.json'))
    census=target/'build/workers/close-adlx-19/census.json';j=json.loads(census.read_text())
    retired=[f for f in j['functions'] if f['kind']=='c' and f['name'] in ['c_'+n for n in ENTRIES]+['l1_'+n for n in ENTRIES]]
    assert not retired,retired
    assert sum(s['fallback_calls'] for s in j['scenarios'])==0
    save(OUT/'acceptance.json',dict(result='PASS',baseline=json.loads((OUT/'baseline.json').read_text()),commands=rows,
          l1_timer_lifetime=retired,fallbacks=0,census=str(census.relative_to(ROOT)),census_sha256=hashlib.sha256(census.read_bytes()).hexdigest()))
    print('Acceptance PASS; six L1 bodies retired; zero fallbacks',flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['cases','proof','accept','certificate','mutations','extra','internal']:parser.add_argument('--'+name,action='store_true')
    args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    for name in ['cases','proof','extra','mutations']:
        if getattr(args,name):
            if args.internal:globals()[name]()
            else:bounded([sys.executable,__file__,'--'+name,'--internal'],name+'-child')
    if args.certificate:certificate()
    if args.accept:accept()

if __name__=='__main__':main()
