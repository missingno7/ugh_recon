"""Literal diagnostics only. Dumps never feed production owners or providers."""
from pathlib import Path
import ctypes as C,hashlib,json,sys,struct
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
import wholegame
from difftest import load_dll,Regs
from emu import DeviceState,IoEvent,MEM_SIZE

def dump(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);dll=load_dll(out/'literal.dll')
 for name in ['high-score','password']:
    folder=out/name;folder.mkdir(exist_ok=True);actual=out.parent/name
    s=wholegame.scenario(ROOT/'tests/scenarios'/f'{name}.txt');m,initial=wholegame.fixture(s)
    memory=dll.ugh_memory().contents;device=dll.ugh_device_state().contents
    C.memmove(memory,m.snapshot(),MEM_SIZE);dll.ugh_devices_reset();data=m.device.state();C.memmove(C.addressof(device),data,len(data))
    clock=wholegame.Clock(s,m);frames=[];rolling=hashlib.sha256();io=bytearray();terminal=False
    F=C.CFUNCTYPE(C.c_int,C.POINTER(Regs));S=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(Regs))
    def frame(r):
        ram=bytes(memory);dev=C.string_at(C.addressof(device),DeviceState.count.offset);events=C.string_at(C.addressof(device)+DeviceState.log.offset,device.count*C.sizeof(IoEvent));io.extend(events)
        index=len(frames)
        for suffix,blob in [('ram',ram),('devices',dev),('io',io)]: (folder/f'frame-{index}.{suffix}').write_bytes(blob)
        record=wholegame.record(ram,dev,events,rolling,m,initial['SP'],r.contents.sp)
        if terminal:record['terminal']='return'
        frames.append(record);device.count=0;clock.frame=len(frames);return 0
    def service(seg,off,r):clock.service(device,seg,off,r.contents.flags,lambda seg,off,n:bytes(memory[seg*16+off:seg*16+off+n]));return 0
    fc,sc=F(frame),S(service);dll.ugh_set_frame_observer.argtypes=[F];dll.ugh_set_frame_observer(fc);dll.ugh_set_service_observer.argtypes=[S];dll.ugh_set_service_observer(sc)
    r=Regs(**{k.lower():v for k,v in initial.items()});fn=getattr(dll,'c_'+s['entry'].split(':')[1]);status=fn(C.byref(r));assert status==0;r.sp=(r.sp+2)&65535;r.ip=0xfff0;terminal=True;frame(C.pointer(r))
    reference=json.loads((ROOT/'build/whole'/f'{name}.ref.json').read_text())['frames'];assert frames==reference,'literal diagnostic differs'
    print(name,'literal exact',len(frames))
    for i in [0,1,len(frames)-1]:
        want=(folder/f'frame-{i}.ram').read_bytes();got=(actual/f'frame-{i}.ram').read_bytes();print(i,'RAM',wholegame.decode_differences(want,got,m)[:40])
        want=(folder/f'frame-{i}.devices').read_bytes();got=(actual/f'frame-{i}.devices').read_bytes();diff=[j for j,(a,b) in enumerate(zip(want,got)) if a!=b];print('device',len(diff),[(j,want[j],got[j]) for j in diff[:20]])
        want=(folder/f'frame-{i}.io').read_bytes();got=(actual/f'frame-{i}.io').read_bytes()
        events1=list(struct.iter_unpack('<IIII',want));events2=list(struct.iter_unpack('<IIII',got));first=next((j for j,(a,b) in enumerate(zip(events1,events2)) if a!=b),None);print('IO',len(events1),len(events2),'first',first,events1[first:first+5] if first is not None else '',events2[first:first+5] if first is not None else '')
if __name__=='__main__':
 if sys.argv[1]=='--worker':dump(sys.argv[2])
 else:
    from job_pool import run
    folder=Path(sys.argv[1]).resolve();print(run([sys.executable,__file__,'--worker',folder],ROOT,folder.parent,'literal-diagnostic')['stdout'])
