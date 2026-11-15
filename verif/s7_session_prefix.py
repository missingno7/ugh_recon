"""Full-record proof of the native cold-session prefix in level openings.

Stops at the first uncomposed gameplay callback. These prefixes are explicitly
not the 160-frame gameplay opening certificate.
"""
from pathlib import Path
import json
import re
import struct
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
import cgen
import s7_demo_record
import s7_session_record
import nativebuild
from cbuild import GCC
from job_pool import run,save


def generate(out,players=1,level=0):
    path=s7_demo_record.generate(out,'pregame')
    s=path.read_text().replace('#include "native/compose_demo.h"','#include "native/compose_demo.h"\n#include "native/compose_session.h"')
    s=s.replace('if(frames==160)exit(0);','')
    mz,symbols=cgen.read_symbols();load=cgen.LOAD*16
    def a(n):return load+symbols['DGROUP:'+n]['linear']
    def o(n):return symbols['GAME:'+n]['offset']
    helpers,fields,_=s7_session_record.projection(full=True)
    pump=f'''static GSStatus pump(void *context,GSInputPollCut cut){{
 GSTestBackend *b=context;static unsigned cursor;
 if(cut==GS_INPUT_SCAN&&frames>=1){{
 unsigned scan=(cursor++&1)?156:28;GSTestRun run={{scan,1}};gs_test_stream(&b->scans,&run,1,1);
 InputScript *p=NULL;for(unsigned i=0;i<device.script_count;i++)if(device.scripts[i].port==0x60)p=&device.scripts[i];
 if(!p){{p=&device.scripts[device.script_count++];p->port=0x60;}}p->count=1;p->cursor=p->used=0;p->cycles=p->cycles_left=1;p->runs[0]=(ScriptRun){{scan,1}};
 device.irq_count=1;device.irq_cursor=0;device.irqs[0]=(IrqEvent){{REC_GAME_SEG,{o('PollKeyboardScanChange')},0,1,0}};
 }}return GS_OK;
}}
'''
    s=s.replace('static void frame(void){',helpers+pump+'static void frame(void){')
    s=s.replace(' memcpy(device.plane',fields+'\n memcpy(device.plane')
    start=s.index(' printf("\\\"return\\\":')
    end=s.index('\n',start)
    ret=f'(w->session.level?(w->run.water_y==175?{o("ShowLevelIntroduction")+0x69}:{o("InitializeLevelDisplay")+0x104}):(frames==0?{o("PrepareAttractMap0")+0x42}:frames==1?{o("PlayPreGameDemo")+3}:{o("RunScriptedDemo")+0x56}))'
    s=s[:start]+' printf("\\\"return\\\":%u}}\\n",'+ret+');'+s[end:]
    s=s.replace('case GST_PRESENT:frame();break;', '''case GST_ACK:event(LOG_OUT,0x20,1,0x20);break;
 case GST_SCAN:device.irq_cursor++;event(LOG_IRQ,1,0,0);event(LOG_IN,0x60,1,e.b);consume(0x60);break;
 case GST_PRESENT:frame();break;''')
    s=s.replace('GameServices services=gs_test_services(backend);','GameServices services=gs_test_services(backend);services.input.pump=pump;')
    s=s.replace('world->run.configuration.players=1;world->run.configuration.player_bytes=2;',f'world->run.configuration.players={players};world->run.configuration.player_bytes={2*players};')
    import dataprobe
    row=next(r for r in dataprobe.levels(mz)[1] if r['players']==players and r['number']==level+1)
    setup='memset(world->front.password,32,20);memcpy(world->front.password,"%s",%d);'%(row['password'],len(row['password']))
    s=s.replace('backend->recorder=effect;GameDemoResult result=game_demo_play(world,&services,DEMO_PRESENT_PREGAME);',setup+'backend->recorder=effect;GameSessionResult result=game_session_run(world,&services,GAME_SESSION_PASSWORD);')
    s=s.replace('result.status,result.selection,frames','result.status,result.display_stage,frames')
    s=s.replace('free(world);free(backend);gs_resources_close(&pack);return 4;', 'int success=result.kind==GAME_SESSION_UNSUPPORTED&&result.action==SESSION_INITIALIZE_LEVEL&&(result.display_stage==10||result.display_stage==11);free(world);free(backend);gs_resources_close(&pack);return success?0:4;')
    baseline=bytearray((out/'baseline.bin').read_bytes())
    struct.pack_into('<H',baseline,a('PlayerCount'),players);struct.pack_into('<H',baseline,a('PlayerArrayBytes'),2*players)
    baseline[a('PasswordEditBuffer'):a('PasswordEditBuffer')+20]=row['password'].encode().ljust(20,b' ')
    (out/'baseline.bin').write_bytes(baseline);path.write_text(s)
    return path


def verify(out,prod,players=1,level=0):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);prod=Path(prod)
    source=generate(out,players,level)
    audited=json.loads((prod/'nativebuild.json').read_text())
    assert audited['result']=='PASS' and audited['manifest']==nativebuild.sha(ROOT/'metadata/native-manifest.json')
    for name,digest in audited['inputs'].items():assert nativebuild.sha(ROOT/name)==digest,'stale production input: '+name
    manifest=json.loads((ROOT/'metadata/native-manifest.json').read_text());sources=manifest['core']+manifest['backends']['test']
    objects=[prod/('object-%02d.o'%i) for i,s in enumerate(sources) if s!='port/test/main.c']
    obj=out/'record.o';exe=out/'record.exe'
    run([GCC,'-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I',ROOT,'-I',ROOT/'port','-I',prod,'-c',source,'-o',obj],ROOT,out,'compile')
    run([GCC,*objects,obj,'-o',exe],ROOT,out,'link')
    result=run([exe,prod/'ugh.res',out/'baseline.bin',out],ROOT,out,'record')
    actual=[json.loads(line) for line in result['stdout'].splitlines()]
    # Original ASM expected records are first read after process exit.
    expected=json.loads((ROOT/'build/levels'/f'{"one" if players==1 else "two"}-{level+1:02d}.ref.json').read_text())['frames'][:len(actual)]
    differences=[]
    for i,(got,want) in enumerate(zip(actual,expected)):
        for field in sorted(set(got)|set(want)):
            if got.get(field)!=want.get(field):differences.append(dict(frame=i,field=field,actual=got.get(field),expected=want.get(field)))
    if len(actual)!=len(expected):differences.append(dict(field='record_count'))
    save(out/'actual.json',dict(frames=actual));save(out/'differences.json',differences)
    save(out/'receipt.json',dict(result='FAIL' if differences else 'PASS',prefix_records=len(actual),gameplay_frames=0,differences=differences,stop=result['stderr']))
    print('prefix',players,level+1,len(actual),'records',[(d.get('frame'),d['field']) for d in differences],flush=True)
    return not differences


def diagnose(out,players,level):
    import ctypes as C
    import wholegame
    from difftest import load_dll,Regs
    from emu import MEM_SIZE,DeviceState,IoEvent
    out=Path(out);dll=load_dll(out/'literal.dll')
    script=wholegame.scenario(ROOT/'tests/levels'/f'{"one" if players==1 else "two"}-{level+1:02d}.txt')
    m,initial=wholegame.fixture(script);memory=dll.ugh_memory().contents;device=dll.ugh_device_state().contents
    C.memmove(memory,m.snapshot(),MEM_SIZE);dll.ugh_devices_reset();data=m.device.state();C.memmove(C.addressof(device),data,len(data))
    clock=wholegame.Clock(script,m);frames=[];rolling=__import__('hashlib').sha256()
    count=len(json.loads((out/'actual.json').read_text())['frames'])
    F=C.CFUNCTYPE(C.c_int,C.POINTER(Regs));S=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(Regs))
    def frame(r):
        ram=bytes(memory);dev=C.string_at(C.addressof(device),DeviceState.count.offset);events=C.string_at(C.addressof(device)+DeviceState.log.offset,device.count*C.sizeof(IoEvent))
        i=len(frames);frames.append(wholegame.record(ram,dev,events,rolling,m,initial['SP'],r.contents.sp));device.count=0;clock.frame=len(frames)
        native=(out/f'frame-{i}.ram').read_bytes();(out/f'literal-{i}.ram').write_bytes(ram)
        print(i,wholegame.decode_differences(ram,native,m)[:30],flush=True)
        return 2 if len(frames)==count else 0
    def service(seg,off,r):clock.service(device,seg,off,r.contents.flags,lambda seg,off,n:bytes(memory[seg*16+off:seg*16+off+n]));return 0
    fc,sc=F(frame),S(service);dll.ugh_set_frame_observer.argtypes=[F];dll.ugh_set_frame_observer(fc);dll.ugh_set_service_observer.argtypes=[S];dll.ugh_set_service_observer(sc)
    r=Regs(**{k.lower():v for k,v in initial.items()});dll.c_RunGameFromPassword(C.byref(r))
    expected=json.loads((ROOT/'build/levels'/f'{"one" if players==1 else "two"}-{level+1:02d}.ref.json').read_text())['frames'][:count]
    assert frames==expected,'literal diagnostic prefix differs from cached original ASM'


def all_prefixes(out,prod):
    import concurrent.futures
    import dataprobe
    rows=dataprobe.levels(cgen.read_symbols()[0])[1]
    one=[r for r in rows if r['players']==1];known={r['record'] for r in one}
    selected=one+[r for r in rows if r['players']==2 and r['record'] not in known]
    assert len(selected)==81
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    # Three independently bounded compile/link/replay children at most.
    def check(row):
        name=f'{"one" if row["players"]==1 else "two"}-{row["number"]:02d}'
        return name,verify(out/name,prod,row['players'],row['number']-1)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=dict(pool.map(check,selected))
    receipts={name:json.loads((out/name/'receipt.json').read_text()) for name in results}
    save(out/'receipt.json',dict(result='PASS' if all(results.values()) else 'FAIL',
                               physical_openings=len(results),prefix_records=sum(r['prefix_records'] for r in receipts.values()),
                               gameplay_frames=0,scope='session prefix through first uncomposed callback; not full opening suites',cases=receipts))
    return all(results.values())


if __name__=='__main__':
    p=__import__('argparse').ArgumentParser();p.add_argument('--players',type=int,default=1);p.add_argument('--level',type=int,default=1);p.add_argument('--out',type=Path,default=ROOT/'build/workers/s7-session/prefix');p.add_argument('--production',type=Path,default=ROOT/'build/workers/s7-session/production');p.add_argument('--diagnose',action='store_true');p.add_argument('--all',action='store_true');a=p.parse_args()
    if a.diagnose:diagnose(a.out,a.players,a.level-1);raise SystemExit(0)
    if a.all:raise SystemExit(0 if all_prefixes(a.out,a.production) else 1)
    raise SystemExit(0 if verify(a.out,a.production,a.players,a.level-1) else 1)
