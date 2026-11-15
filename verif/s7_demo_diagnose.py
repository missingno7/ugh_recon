"""Independent literal diagnostics. Dumps are never production inputs."""
import ctypes as C
import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
import wholegame
from difftest import load_dll,Regs
from emu import DeviceState,IoEvent,MEM_SIZE

def dump(out,smoke=False):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);dll=load_dll(out/'literal.dll')
    for name in (['attract'] if smoke else ['attract','pregame','completion','reveal']):
        folder=out/('smoke' if smoke else name);folder.mkdir(exist_ok=True);actual=out.parent/name
        scenario=wholegame.scenario(ROOT/'tests/scenarios'/f'{name}.txt');m,initial=wholegame.fixture(scenario)
        if smoke:scenario['frames']=256
        memory=dll.ugh_memory().contents;device=dll.ugh_device_state().contents
        C.memmove(memory,m.snapshot(),MEM_SIZE);dll.ugh_devices_reset();data=m.device.state();C.memmove(C.addressof(device),data,len(data))
        clock=wholegame.Clock(scenario,m);frames=[];rolling=hashlib.sha256();io=bytearray()
        F=C.CFUNCTYPE(C.c_int,C.POINTER(Regs));S=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(Regs))
        def frame(r):
            ram=bytes(memory);dev=C.string_at(C.addressof(device),DeviceState.count.offset);events=C.string_at(C.addressof(device)+DeviceState.log.offset,device.count*C.sizeof(IoEvent));io.extend(events)
            index=len(frames)
            if not smoke and index in [0,1,2,3,scenario['frames']-1]:
                for suffix,blob in [('ram',ram),('devices',dev),('io',io)]:(folder/f'frame-{index}.{suffix}').write_bytes(blob)
            frames.append(wholegame.record(ram,dev,events,rolling,m,initial['SP'],r.contents.sp))
            device.count=0;clock.frame=len(frames);return 2 if len(frames)==scenario['frames'] else 0
        def service(seg,off,r):clock.service(device,seg,off,r.contents.flags,lambda seg,off,n:bytes(memory[seg*16+off:seg*16+off+n]));return 0
        fc,sc=F(frame),S(service);dll.ugh_set_frame_observer.argtypes=[F];dll.ugh_set_frame_observer(fc);dll.ugh_set_service_observer.argtypes=[S];dll.ugh_set_service_observer(sc)
        r=Regs(**{k.lower():v for k,v in initial.items()});getattr(dll,'c_'+scenario['entry'].split(':')[1])(C.byref(r))
        expected=json.loads((ROOT/'build/whole'/f'{name}.ref.json').read_text())['frames'];assert frames[:len(expected)]==expected,'literal differs from reference'
        if smoke:
            (folder/'reference.json').write_text(json.dumps(dict(frames=frames),indent=2)+'\n');print('PASS independent smoke: 256 attract records; 96/96 cached prefix exact');continue
        assert len(frames)==len(expected)
        print(name,'literal exact',len(frames),flush=True)
        for i in [0,1,2,3,scenario['frames']-1]:
            want=(folder/f'frame-{i}.ram').read_bytes();got=(actual/f'frame-{i}.ram').read_bytes();print(i,'RAM',wholegame.decode_differences(want,got,m)[:12])
            want=(folder/f'frame-{i}.io').read_bytes();got=(actual/f'frame-{i}.io').read_bytes();first=next((j for j,(a,b) in enumerate(zip(want,got)) if a!=b),None)
            rows1=list(struct.iter_unpack('<IIII',want));rows2=list(struct.iter_unpack('<IIII',got));j=first//16 if first is not None else 0
            print('IO',len(rows1),len(rows2),'first',j if first is not None else None,rows1[j:j+4],rows2[j:j+4],flush=True)
if __name__=='__main__':
    if sys.argv[1] in ['--worker','--smoke-worker']:dump(sys.argv[2],sys.argv[1]=='--smoke-worker')
    else:
        from job_pool import run
        out=Path(sys.argv[1]).resolve();print(run([sys.executable,__file__,'--worker',out],ROOT,out.parent,'literal-diagnostics')['stdout'])
