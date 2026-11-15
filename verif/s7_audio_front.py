"""Active front-end evidence from independent literal entry executions."""
from pathlib import Path
import ctypes as C,hashlib,json,struct,sys,re
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
from job_pool import run,save
import s7_audio,s7_audio_record,cgen,respack

def generate(folder,scenario):
    source=s7_audio_record.generate(folder,frontend=scenario);s=source.read_text()
    s=s.replace('terminal=1;frame();','if(game_audio_terminal(world,&services)!=GS_OK)return 4;terminal=1;frame();')
    if scenario=='intro':
        mz,sy=cgen.read_symbols();load=cgen.LOAD*16
        def a(n):return load+sy['DGROUP:'+n]['linear']
        def o(n):return sy['GAME:'+n]['offset']
        baseline=bytearray((folder/'baseline.bin').read_bytes())
        struct.pack_into('<I',baseline,a('ScoreLowWord'),0)
        struct.pack_into('<H',baseline,a('LevelIntroTextPointer'),sy['DGROUP:PasswordEditBuffer']['offset'])
        baseline[a('PasswordEditBuffer'):a('PasswordEditBuffer')+11]=b'INTRO TEST\0'
        (folder/'baseline.bin').write_bytes(baseline)
        rows=respack.inventory(mz.image,sy)[0]
        base=cgen.FRAMES['DGROUP']*16
        pw=struct.unpack_from('<H',mz.image,sy['DGROUP:PasswordListPointers']['linear'])[0]
        start=pw
        # PasswordListPointers contains a near pointer to the first string.
        end=mz.image.index(b'\0',base+start)+1
        resource=min([r for r in rows if r['image_start']<=base+start and end<=r['image_start']+r['size']],key=lambda r:r['size'])
        setup=f'''GSBytes passwords;GSResourceClass kind;if(services.resources.view(services.resources_context,UINT64_C({resource['id']}),&passwords,&kind)!=GS_OK)return 3;
 memcpy(world->front.password,"INTRO TEST",11);world->run.score=0;services.input.pump=pump;
 GSBytes intro={{world->front.password,11}},password={{passwords.data+{base+start-resource['image_start']},{end-base-start}}};'''
        s=s.replace('if(score_case)world->run.score=999999;','if(score_case)world->run.score=999999;'+setup)
        s=s.replace('if(score_case)status=game_front_scores_insert(world,&services).status;else status=game_front_password(world,&services);','status=game_front_introduction(world,&services,intro,password);')
        # A single swap inside ShowLevelIntroduction; final observation is the
        # harness return after its palette fade and restored live Water Y.
        old=f'(terminal?1:score_case?(frames==0?{o("InsertHighScoreAndClearScore")+0xc0}:frames==8?{o("ShowHighScores")+0x1e}:{o("DrawHighScoreNameEntry")+0x1c}):(frames==0?{o("EditLevelPassword")+9}:{o("EditLevelPassword")+0x56}))'
        assert old in s;s=s.replace(old,f'(terminal?1:{o("ShowLevelIntroduction")+0x69})')
        s=s.replace('gs_test_stream(&backend->bios,bios,count,1);','(void)bios;(void)count;')
        s=re.sub(r'InputScript \*bs=&device.scripts\[device.script_count\+\+\];.*?for\(unsigned i=0;i<count;i\+\+\)bs->runs\[i\]=\(ScriptRun\)\{bios\[i\].value,1\};','',s,flags=re.S)
    source.write_text(s);return source

def reference(out):
    import wholegame
    from difftest import load_dll,Regs
    from emu import DeviceState,IoEvent,MEM_SIZE
    dll=load_dll(out/'literal.dll')
    for scenario in ['score','intro']:
        folder=out/scenario;folder.mkdir(exist_ok=True)
        script=wholegame.scenario(ROOT/'tests/scenarios/high-score.txt');script['card']='adlib'
        if scenario=='intro':script.update(entry='GAME:ShowLevelIntroduction',score='0',bios='',events={1:[1,129]})
        m,initial=wholegame.fixture(script)
        if scenario=='intro':
            m.ww('DGROUP:LevelIntroTextPointer',m.off('DGROUP:PasswordEditBuffer'));m.write(m.seg('DGROUP:PasswordEditBuffer'),m.off('DGROUP:PasswordEditBuffer'),b'INTRO TEST\0')
        m.device.irq_count=2
        for i,site in enumerate(['loc_1163','loc_116B']):
            e=m.device.irqs[i];e.segment=m.seg('SOUND:'+site);e.offset=m.off('SOUND:'+site);e.irq=0;e.clocks=65536
        init=m.prepare('C:InitializeSoundSystem',kind='far',args=(1,),flags=0x202)
        memory=dll.ugh_memory().contents;dev=dll.ugh_device_state().contents
        C.memmove(memory,m.snapshot(),MEM_SIZE);dll.ugh_devices_reset();data=m.device.state();C.memmove(C.addressof(dev),data,len(data))
        r=Regs(**{k.lower():v for k,v in init.items()});assert dll.c_InitializeSoundSystem(C.byref(r))==0
        m.restore(bytes(memory));initial=m.prepare(script['entry'],kind='near',flags=0x202);C.memmove(memory,m.snapshot(),MEM_SIZE)
        clock=wholegame.Clock(script,m);frames=[];rolling=hashlib.sha256();io=bytearray();terminal=False
        F=C.CFUNCTYPE(C.c_int,C.POINTER(Regs));S=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(Regs))
        def frame(r):
            ram=bytes(memory);device=C.string_at(C.addressof(dev),DeviceState.count.offset);events=C.string_at(C.addressof(dev)+DeviceState.log.offset,dev.count*C.sizeof(IoEvent));io.extend(events)
            index=len(frames)
            for suffix,blob in [('ram',ram),('devices',device),('io',io)]:(folder/f'frame-{index}.{suffix}').write_bytes(blob)
            record=wholegame.record(ram,device,events,rolling,m,initial['SP'],r.contents.sp)
            if terminal:record['terminal']='return'
            frames.append(record);dev.count=0;clock.frame=len(frames);return 0
        def service(seg,off,r):clock.service(dev,seg,off,r.contents.flags,lambda seg,off,n:bytes(memory[seg*16+off:seg*16+off+n]));return 0
        fc,sc=F(frame),S(service);dll.ugh_set_frame_observer.argtypes=[F];dll.ugh_set_frame_observer(fc);dll.ugh_set_service_observer.argtypes=[S];dll.ugh_set_service_observer(sc)
        r=Regs(**{k.lower():v for k,v in initial.items()});fn=getattr(dll,'c_'+script['entry'].split(':')[1]);assert fn(C.byref(r))==0
        assert dll.c_FadeAndShutdownSound(C.byref(r))==0
        r.sp=(r.sp+2)&65535;r.ip=0xfff0;terminal=True;frame(C.pointer(r));save(folder/'records.json',frames)
        dll.ugh_set_frame_observer(F());dll.ugh_set_service_observer(S())

def verify(out,prod):
    root=out/'active-front';root.mkdir(exist_ok=True);expected=root/'reference';expected.mkdir(exist_ok=True)
    actual={}
    for name in ['score','intro']:
        folder=root/name;folder.mkdir(exist_ok=True);exe=s7_audio.executable(generate(folder,name),folder,prod)
        r=run([exe,prod/'ugh.res',folder/'baseline.bin',folder],ROOT,folder,'record');actual[name]=[json.loads(x) for x in r['stdout'].splitlines()]
        save(folder/'actual.json',actual[name])
    # The expected observations are generated in an isolated process and first
    # read only after both production executions have exited.
    run([sys.executable,__file__,'--reference-worker',expected],ROOT,root,'reference')
    results={}
    for name,got in actual.items():
        want=json.loads((expected/name/'records.json').read_text())
        diffs=[dict(frame=i,field=k,actual=a.get(k),expected=b.get(k)) for i,(a,b) in enumerate(zip(got,want)) for k in set(a)|set(b) if a.get(k)!=b.get(k)]
        if len(got)!=len(want):diffs.append(dict(field='count',actual=len(got),expected=len(want)))
        save(root/name/'differences.json',diffs);results[name]=dict(records=len(got),differences=diffs)
        print(name,len(got),[(d.get('frame'),d['field']) for d in diffs],flush=True)
    save(root/'receipt.json',results);assert not any(r['differences'] for r in results.values())
    return {n:dict(result='PASS',records=r['records']) for n,r in results.items()}
if __name__=='__main__':
    if sys.argv[1]=='--reference-worker':reference(Path(sys.argv[2]))
    else:
        out=Path(sys.argv[1]).resolve();verify(out,out/'production')
