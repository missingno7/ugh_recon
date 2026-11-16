"""Independent literal diagnostic, run only after the native recorder exits."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
import wholegame
from difftest import Regs
from emu import DeviceState,IoEvent,MEM_SIZE


def diagnose(path,out,dllpath,frame):
    out=Path(out);script=wholegame.scenario(Path(path));m,initial=wholegame.fixture(script)
    dll=C.CDLL(str(Path(dllpath).resolve()));dll.ugh_memory.restype=C.POINTER(C.c_uint8*MEM_SIZE);dll.ugh_device_state.restype=C.POINTER(DeviceState)
    memory=dll.ugh_memory().contents;device=dll.ugh_device_state().contents
    C.memmove(memory,m.snapshot(),MEM_SIZE);dll.ugh_devices_reset();data=m.device.state();C.memmove(C.addressof(device),data,len(data))
    clock=wholegame.Clock(script,m);records=[];rolling=hashlib.sha256()
    F=C.CFUNCTYPE(C.c_int,C.POINTER(Regs));S=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(Regs))
    def boundary(r):
        ram=bytes(memory);dev=C.string_at(C.addressof(device),DeviceState.count.offset);io=C.string_at(C.addressof(device)+DeviceState.log.offset,device.count*C.sizeof(IoEvent));i=len(records)
        records.append(wholegame.record(ram,dev,io,rolling,m,initial['SP'],r.contents.sp));device.count=0;clock.frame=len(records)
        if i==frame:
            (out/f'literal-{i}.ram').write_bytes(ram);(out/f'literal-{i}.devices').write_bytes(dev);(out/f'literal-{i}.io').write_bytes(io)
            native=(out/f'frame-{i}.ram').read_bytes();print('RAM',wholegame.decode_differences(ram,native,m)[:25])
            first=list(struct.iter_unpack('<4I',io));second=list(struct.iter_unpack('<4I',(out/f'frame-{i}.io').read_bytes()))
            print('IO lengths',len(first),len(second));print('IO first differences',[(j,a,b) for j,(a,b) in enumerate(zip(first,second)) if a!=b][:25])
            return 2
        return 0
    def service(seg,off,r):clock.service(device,seg,off,r.contents.flags,lambda seg,off,n:bytes(memory[seg*16+off:seg*16+off+n]));return 0
    fc,sc=F(boundary),S(service);dll.ugh_set_frame_observer.argtypes=[F];dll.ugh_set_frame_observer(fc);dll.ugh_set_service_observer.argtypes=[S];dll.ugh_set_service_observer(sc)
    r=Regs(**{k.lower():v for k,v in initial.items()});getattr(dll,'c_'+script['entry'].split(':')[1])(C.byref(r))
    if script.get('end') and len(records)<=frame:
        boundary(C.pointer(r));records[-1]['terminal']=script['end']
    group={'scenarios':'whole','levels':'levels','levels-audio':'levels-audio','levels-deep':'levels-deep'}.get(Path(path).parent.name)
    reference=ROOT/'build'/group/(Path(path).stem+'.ref.json') if group else out/'original/reference.json'
    expected=json.loads(reference.read_text())['frames'][:len(records)]
    assert records==expected,'literal diagnostic differs from original ASM cache'
    print('PASS independent literal matches original ASM records',len(records))


if __name__=='__main__':diagnose(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]),int(sys.argv[4]))
