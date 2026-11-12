"""Known-answer checks, independent of differential agreement. Run directly."""
import ctypes as C
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from difftest import load_dll, DeviceState
from emu import Devices, Machine


def main():
    d=load_dll()
    d.ugh_write.argtypes=[C.c_uint32,C.c_uint8]
    d.ugh_read.argtypes=[C.c_uint32]; d.ugh_read.restype=C.c_uint8
    # Full plane/map-mask known answers, including physical segment alias and latches.
    d.ugh_devices_reset(); c=d.ugh_device_state().contents; p=Devices()
    for plane in range(4):
        mask=1<<plane; value=0x11*(plane+1)
        p.out(0x3C4,1,2); p.out(0x3C5,1,mask); p.write(0x1234,value)
        d.platform_out(0x3C4,1,2); d.platform_out(0x3C5,1,mask)
        d.ugh_write(0xA1234,value)
    assert [p.planes[x*65536+0x1234] for x in range(4)]==[0x11,0x22,0x33,0x44]
    assert [c.planes[x*65536+0x1234] for x in range(4)]==[0x11,0x22,0x33,0x44]
    assert p.read(0x1234)==0x11 and d.ugh_read(0xA1234)==0x11
    assert list(p.latch)==list(c.latch)==[0x11,0x22,0x33,0x44]
    d.platform_out(0x3C4,2,0x0502)
    p.out(0x3C4,2,0x0502)
    d.ugh_write(0xA1235,0x5A); p.write(0x1235,0x5A)
    assert [c.planes[x*65536+0x1235] for x in range(4)]==[0x5A,0,0x5A,0]
    assert [p.planes[x*65536+0x1235] for x in range(4)]==[0x5A,0,0x5A,0]
    assert not c.error
    # Unsupported requests and bounded execution must fail closed.
    d.platform_out(0x3C4,1,4); d.platform_out(0x3C5,1,8)
    assert c.error==1
    m=Machine()
    m.prepare('TIMER:HandleTimerInterrupt',kind='iret',flags=0xF02)
    assert m.reg('FLAGS')&0x300==0, 'hardware IRQ entry must clear IF and TF'
    assert int.from_bytes(m.read(m.reg('SS'),m.reg('SP')+4,2),'little')==0xF02
    for routine,budget,needle in [('GAME:WaitVerticalRetraceActive',100,'unsupported IN'),
                                  ('GAME:SeedRandomFromDosSeconds',100,'unsupported INT'),
                                  ('GAME:ComplementHighScoreTable',1,'budget')]:
        m.reset(); m.prepare(routine)
        try: m.run(budget)
        except RuntimeError as e: assert needle in str(e),str(e)
        else: raise AssertionError('oracle failed to reject '+routine)
    assert C.sizeof(DeviceState)==d.ugh_device_size()
    print('PASS platform KAT: planes, map masks, latches, word OUT, unsupported services, bounded oracle')


if __name__=='__main__': main()
