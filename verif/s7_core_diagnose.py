"""Independent literal startup dumps for diagnostics, never production input."""
from pathlib import Path
import ctypes as C,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
import wholegame
from difftest import load_dll,Regs
from emu import DeviceState,IoEvent,MEM_SIZE

def dump(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    s=wholegame.scenario(ROOT/'tests/scenarios/startup.txt');s['frames']=6
    m,initial=wholegame.fixture(s);dll=load_dll(out/'literal.dll')
    memory=dll.ugh_memory().contents;device=dll.ugh_device_state().contents
    C.memmove(memory,m.snapshot(),MEM_SIZE);dll.ugh_devices_reset()
    data=m.device.state();C.memmove(C.addressof(device),data,len(data))
    clock=wholegame.Clock(s,m);frames=[];rolling=hashlib.sha256();io=bytearray()
    F=C.CFUNCTYPE(C.c_int,C.POINTER(Regs));S=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(Regs))
    def frame(r):
        ram=bytes(memory);dev=C.string_at(C.addressof(device),DeviceState.count.offset)
        events=C.string_at(C.addressof(device)+DeviceState.log.offset,device.count*C.sizeof(IoEvent));io.extend(events)
        index=len(frames);(out/f'frame-{index}.ram').write_bytes(ram);(out/f'frame-{index}.devices').write_bytes(dev);(out/f'frame-{index}.io').write_bytes(io)
        frames.append(wholegame.record(ram,dev,events,rolling,m,initial['SP'],r.contents.sp))
        device.count=0;clock.frame=len(frames);return 2 if len(frames)==6 else 0
    def service(seg,off,r):
        clock.service(device,seg,off,r.contents.flags,lambda seg,off,n:bytes(memory[seg*16+off:seg*16+off+n]));return 0
    fc,sc=F(frame),S(service);dll.ugh_set_frame_observer.argtypes=[F];dll.ugh_set_frame_observer(fc)
    dll.ugh_set_service_observer.argtypes=[S];dll.ugh_set_service_observer(sc)
    r=Regs(**{k.lower():v for k,v in initial.items()});dll.c_RunDosGame(C.byref(r))
    reference=json.loads((ROOT/'build/whole/startup.ref.json').read_text())['frames'][:6]
    assert frames==reference,'literal diagnostic disagrees with independent reference'
    (out/'records.json').write_text(json.dumps(frames,indent=2)+'\n')
    actual=out.parent/'record'
    diagnostics=[]
    for i in range(6):
        want=(out/f'frame-{i}.ram').read_bytes();got=(actual/f'frame-{i}.ram').read_bytes()
        differences=wholegame.decode_differences(want,got,m)
        print(i, '\n'.join(differences));diagnostics.append(dict(frame=i,differences=differences))
    (out/'differences.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
if __name__=='__main__':
    if sys.argv[1]=='--worker':dump(Path(sys.argv[2]))
    else:
        from job_pool import run
        folder=Path(sys.argv[1]).resolve()
        result=run([sys.executable,__file__,'--worker',folder],ROOT,folder.parent,'literal-diagnostic')
        print(result['stdout'],end='')
