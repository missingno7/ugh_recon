"""Independent known answers for every supported device service; no DOS boot."""
import ctypes as C
import struct
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from difftest import load_dll,Regs,DeviceState
from emu import Devices,Machine,REG_NAMES,MEM_SIZE


def main():
    d=load_dll();mem=d.ugh_memory().contents
    d.ugh_read.argtypes=[C.c_uint32];d.ugh_read.restype=C.c_uint8
    d.ugh_write.argtypes=[C.c_uint32,C.c_uint8]
    d.ugh_load16.restype=C.c_uint16;d.ugh_load32.restype=C.c_uint32
    d.ugh_store32.argtypes=[C.c_uint16,C.c_uint16,C.c_uint32]
    assert C.sizeof(DeviceState)==d.ugh_device_size()
    # Operand bytes stay contiguous even above 1 MiB; effective offsets wrap
    # only between instructions. Distinct decoys rule out wrapped high bytes.
    for seg,off in ((0x7500,0xffff),(0xffff,0xffff),(0x7000,0xfffe)):
        a=16*seg+off;mem[a:a+4]=b'\x12\x34\x56\x78';mem[16*seg:16*seg+2]=b'\xaa\xbb'
        assert d.ugh_load16(seg,off)==0x3412 and d.ugh_load32(seg,off)==0x78563412
        d.ugh_store16(seg,off,0x1234);assert bytes(mem[a:a+2])==b'\x34\x12'
        d.ugh_store32(seg,off,0xfedcba98);assert bytes(mem[a:a+4])==b'\x98\xba\xdc\xfe'
        assert bytes(mem[16*seg:16*seg+2])==b'\xaa\xbb'

    d.ugh_devices_reset();p=Devices();c=d.ugh_device_state().contents
    def out(port,value,size=1):p.out(port,size,value);d.platform_out(port,size,value)
    def inp(port,expected):assert p.inp(port,1)==expected and d.platform_in(port,1)==expected
    def gc(index,value):out(0x3ce,index);out(0x3cf,value)
    def write(off,value):p.write(off,value);d.ugh_write(0xa0000+off,value)
    def read(off,expected):assert p.read(off)==expected and d.ugh_read(0xa0000+off)==expected
    def planes(off,expected):
        assert [p.planes[i*65536+off] for i in range(4)]==expected
        assert [c.planes[i*65536+off] for i in range(4)]==expected
    out(0x3c4,2)
    for plane,value in enumerate((0x11,0x22,0x33,0x44)):
        out(0x3c5,1<<plane);write(0x1234,value)
    planes(0x1234,[0x11,0x22,0x33,0x44]);read(0x1234,0x11)
    assert list(c.latch)==list(p.latch)==[0x11,0x22,0x33,0x44]
    out(0x3c5,15);gc(5,1);write(0x1235,0xff)
    planes(0x1235,[0x11,0x22,0x33,0x44])
    gc(5,0);gc(8,0);write(0x1236,0xff);planes(0x1236,[0x11,0x22,0x33,0x44])
    gc(8,0xf0);write(0x1237,0xaa);planes(0x1237,[0xa1,0xa2,0xa3,0xa4])
    gc(8,255);gc(5,2);write(0x1238,5);planes(0x1238,[255,0,255,0])
    gc(5,3);gc(0,5);write(0x1239,0xf0);planes(0x1239,[0xf1,2,0xf3,4])
    gc(5,0);gc(3,0x18);write(0x1240,0xff);planes(0x1240,[0xee,0xdd,0xcc,0xbb])
    gc(3,1);write(0x1241,1);planes(0x1241,[128]*4)
    gc(3,0);gc(1,5);gc(0,1);write(0x1242,0x6a);planes(0x1242,[255,0x6a,0,0x6a])
    gc(4,2);gc(5,0);read(0x1234,0x33);inp(0x3cf,0)
    gc(2,1);gc(7,3);gc(5,8);read(0x1234,0x11)
    # CRTC, attribute address/data flip-flop and DAC 6-bit cycling.
    out(0x3d4,0x0c);out(0x3d5,0x55);inp(0x3d5,0x55)
    out(0x3c0,0x10);out(0x3c0,0x41);inp(0x3c1,0x41)
    out(0x3c8,255)
    for v in (0xff,2,3,4):out(0x3c9,v)
    assert list(c.dac[765:768])==list(p.dac[765:768])==[63,2,3]
    assert c.dac[0]==p.dac[0]==4 and c.dac_index==p.dac_index==0
    # AdLib register/data and scripted timer status (no invented OPL clock).
    out(0x388,0xa0);out(0x389,0x7b)
    assert c.opl[0xa0]==p.opl[0xa0]==0x7b
    # DMA flip-flop, page, mode/mask; PIT zero divisor and PIC mask.
    for port,v in ((0xc,0),(2,0x34),(2,0x12),(3,0xff),(3,3),(0x83,0xa),
                   (0xb,0x49),(0xa,1),(0x21,0x80),(0x20,0x20),(0x43,0x36),(0x40,0),(0x40,0)):
        out(port,v)
    for dev in (p,c):
        assert (dev.dma_address,dev.dma_count,dev.dma_page,dev.dma_mode,dev.dma_mask)==(0x1234,0x3ff,10,0x49,1)
        assert dev.pic_mask==0x80 and dev.pit_divisor==0 and dev.pit_phase==0
    assert not c.error

    # Fixture scripts: raw scans/prefixes, retrace bits, joystick trigger reset,
    # DSP busy/ready/reset/data/ack, OPL timer statuses. Both consume finite data.
    d.ugh_devices_reset();p=Devices();c=d.ugh_device_state().contents
    for port,values in ((0x60,[0xe0,0x9e]),(0x3da,[0x81,8]),(0x201,[0xff,0x0f,0]),
                        (0x22c,[0x80,0x81,0]),(0x22a,[0xaa]),(0x22e,[0x80]),(0x388,[0,0xc0])):
        p.script(port,values)
    C.memmove(C.addressof(c),p.state(),len(p.state()))
    inp(0x60,0xe0);inp(0x60,0x9e);inp(0x3da,0x81);assert p.attr_phase==c.attr_phase==0
    inp(0x3da,8);out(0x201,0x55);inp(0x201,255);inp(0x201,15);out(0x201,0);inp(0x201,255)
    out(0x226,1);out(0x226,0);inp(0x22e,128);inp(0x22a,0xaa)
    inp(0x22c,128);inp(0x22c,129);inp(0x22c,0);out(0x22c,0xd1);inp(0x388,0);inp(0x388,0xc0)
    assert C.string_at(C.addressof(c),len(p.state()))==p.state()
    try:p.inp(0x60,1)
    except RuntimeError as e:assert 'exhausted' in str(e)
    else:raise AssertionError('script exhaustion accepted')
    d.platform_in(0x60,1);assert c.error

    # Finite waveform cycles: exact order, nonconsuming BIOS peeks and restart.
    for values,cycles in (([],1),([0,8],0),([1],0x100000000)):
        q=Devices()
        try:q.script(0x201,values,cycles=cycles)
        except ValueError:pass
        else:raise AssertionError('invalid finite waveform accepted')
        assert q.script_count==0
    d.ugh_devices_reset();p=Devices();c=d.ugh_device_state().contents
    p.script(0x3da,[0,8],cycles=3);p.script(0x201,[255,0],cycles=2)
    p.script(0xffff,[0x1e61,0x3062],cycles=2)
    C.memmove(C.addressof(c),p.state(),len(p.state()))
    for expected in [0,8]*3:inp(0x3da,expected)
    assert p.scripts[0].cursor==c.scripts[0].cursor==2
    inp(0x201,255);inp(0x201,0);inp(0x201,255)
    out(0x201,0);assert p.scripts[1].cycles_left==c.scripts[1].cycles_left==2
    for expected in [255,0]*2:inp(0x201,expected)
    assert C.string_at(C.addressof(c),len(p.state()))==p.state()
    try:p.inp(0x3da,1)
    except RuntimeError:pass
    else:raise AssertionError('finite waveform did not exhaust')
    d.platform_in(0x3da,1);assert c.error

    # Direct DOS/BIOS KATs: explicit bytes and register outputs on BOTH sides.
    m=Machine();m.prepare('GAME:loc_001C',regs=dict(AX=0x3509,DS=0x7500,DX=0xabcd),flags=0xed7)
    m.write(0,0x24,b'\x34\x12\xcd\xab');m.write(0x7500,0x100,b'SCORE.DAT\0')
    p=m.device;p.script(0xfffe,[0x173b3b63]);p.script(0xffff,[0x1e61,0x3062],cycles=2);p.file('SCORE.DAT',b'ABCD')
    d.ugh_devices_reset();c=d.ugh_device_state().contents;C.memmove(mem,m.snapshot(),MEM_SIZE);C.memmove(C.addressof(c),p.state(),len(p.state()))
    r=Regs(**{n.lower():m.reg(n) for n in REG_NAMES})
    def interrupt(n,**inputs):
        for key,value in inputs.items():m.setreg(key,value);setattr(r,key.lower(),value)
        p.interrupt(n,m);assert d.platform_interrupt(n,C.byref(r))==0
        for key in REG_NAMES:assert m.reg(key)==getattr(r,key.lower()),key
        assert C.string_at(C.addressof(c),len(p.state()))==p.state()
    interrupt(0x21,AX=0x3509);assert r.bx==0x1234 and r.es==0xabcd and r.flags==0xed7
    interrupt(0x21,AX=0x2509,DS=0x4567,DX=0x789a)
    assert m.read(0,0x24,4)==bytes(mem[0x24:0x28])==b'\x9a\x78\x67\x45'
    interrupt(0x21,AX=0x3509);assert (r.bx,r.es)==(0x789a,0x4567)
    interrupt(0x21,AX=0x2c00);assert (r.cx,r.dx)==(0x173b,0x3b63)
    for key in [0x1e61,0x3062]*2:
        for repeat_peek in range(2):
            interrupt(0x16,AX=0x100);assert r.ax==key and not r.flags&64
        interrupt(0x16,AX=0);assert r.ax==key
    interrupt(0x16,AX=0x100);assert r.flags&64
    interrupt(0x10,AX=0x13);interrupt(0x10,AX=0xf00);assert r.ax==0x5013
    interrupt(0x21,AX=0x3d00,DS=0x7500,DX=0x100);assert r.ax==5 and not r.flags&1
    interrupt(0x21,AX=0x3f00,BX=5,CX=10,DX=0x200);assert r.ax==4
    assert m.read(0x7500,0x200,4)==bytes(mem[0x75200:0x75204])==b'ABCD'
    interrupt(0x21,AX=0x3e00,BX=5);interrupt(0x21,AX=0x3c00,DX=0x100,CX=0);assert r.ax==5 and c.files[0].length==0
    p.io_limit=c.io_limit=2;m.write(0x7500,0x200,b'XYZ');mem[0x75200:0x75203]=b'XYZ'
    interrupt(0x21,AX=0x4000,BX=5,CX=3,DX=0x200);assert r.ax==2 and bytes(c.files[0].data[:2])==b'XY'
    interrupt(0x21,AX=0x3e00,BX=5);interrupt(0x21,AX=0x3e00,BX=5);assert r.ax==6 and r.flags&1
    m.write(0x7500,0x300,b'ABSENT.DAT\0');mem[0x75300:0x7530b]=b'ABSENT.DAT\0'
    interrupt(0x21,AX=0x3d00,DX=0x300);assert r.ax==2 and r.flags&1
    p.dos_error=c.dos_error=5;interrupt(0x21,AX=0x3d00,DX=0x100);assert r.ax==5 and r.flags&1
    # Only file requests decrement the delayed-error countdown. A selected
    # failed request leaves handles, cursor, contents and destination untouched.
    for skip in (1,2):
        p.dos_error=c.dos_error=5;p.dos_error_skip=c.dos_error_skip=skip
        interrupt(0x10,AX=0xf00);assert c.dos_error_skip==skip
        interrupt(0x21,AX=0x3d00,DS=0x7500,DX=0x100);assert r.ax==5 and not r.flags&1
        before=m.read(0x7500,0x400,4)
        interrupt(0x21,AX=0x3f00,BX=5,CX=2,DX=0x400)
        if skip==1:
            assert r.ax==5 and r.flags&1 and c.handles[5].position==0
            assert m.read(0x7500,0x400,4)==before
            interrupt(0x21,AX=0x3e00,BX=5)
        else:
            assert r.ax==2 and not r.flags&1 and c.handles[5].position==2
            interrupt(0x21,AX=0x3e00,BX=5)
            assert r.ax==5 and r.flags&1 and c.handles[5].active
            interrupt(0x21,AX=0x3e00,BX=5)
        assert c.dos_error==c.dos_error_skip==0
    interrupt(0x21,AX=0x4c07);assert p.exited==c.exited==1 and p.exit_code==c.exit_code==7

    # Exact-address resolution rejects an unknown address without fake success.
    saved=bytes(r);assert d.ugh_dispatch(0xdead,0xbeef,C.byref(r))==3 and bytes(r)==saved
    # IRQ0 calibration is also a KAT: independent assertions on both captured
    # measurements and IVT restoration run through the normal differential suite.
    from difftest import load_suite,run
    for case in load_suite('sound_engine').CASES:
        if case.routine=='SOUND:CalibrateSoundDelay':assert not run(case,m,d,True)
    # Explicit IRQ3 delivery follows IVT, creates an IRQ frame and IRETs.
    m.reset();m.device.schedule(m.seg('GAME:WaitVerticalRetraceActive'),m.off('GAME:WaitVerticalRetraceActive'),irq=3,clocks=17)
    m.device.script(0x3da,[8]);seg,off=m.address('GAME:FailDosCriticalError');m.write(0,44,struct.pack('<HH',off,seg))
    initial=m.prepare('GAME:WaitVerticalRetraceActive',regs=dict(AX=0xa500),flags=0x602)
    C.memmove(mem,m.snapshot(),MEM_SIZE);d.ugh_devices_reset();c=d.ugh_device_state().contents;C.memmove(C.addressof(c),m.device.state(),len(m.device.state()))
    r=Regs(**{n.lower():v for n,v in initial.items()});assert d.platform_service_point_at(2,r.cs,r.ip,C.byref(r))==0
    assert r.sp==initial['SP'] and r.flags==0x602 and r.ax==0xa503 and c.clocks==17
    result=m.run();assert result['AX']==0xa508 and m.device.clocks==17 and m.device.log[0]==(4,3,0,17)
    assert d.c_WaitVerticalRetraceActive(C.byref(r))==0 and r.ax==0xa508
    # A sound-card IRQ uses the real translated probe handler and ordered EOI.
    m.reset();seg,off=m.address('SOUND:HandleDspProbeInterrupt');m.write(0,60,struct.pack('<HH',off,seg))
    site=m.address('GAME:WaitVerticalRetraceActive');m.device.schedule(*site,irq=7,clocks=1193)
    initial=m.prepare('GAME:WaitVerticalRetraceActive',regs=dict(AX=0xa500),flags=0x602)
    C.memmove(mem,m.snapshot(),MEM_SIZE);d.ugh_devices_reset();c=d.ugh_device_state().contents
    C.memmove(C.addressof(c),m.device.state(),len(m.device.state()));r=Regs(**{n.lower():v for n,v in initial.items()})
    c.pic_mask=0x80
    assert d.platform_service_point_at(2,*site,C.byref(r))==0 and c.irq_cursor==0 and c.clocks==0
    c.pic_mask=0;r.flags&=~512
    assert d.platform_service_point_at(2,*site,C.byref(r))==0 and c.irq_cursor==0
    r.flags|=512
    assert d.platform_service_point_at(2,*site,C.byref(r))==0 and c.irq_cursor==1 and c.clocks==1193
    assert r.ax==0xa520 and r.sp==initial['SP'] and r.flags==0x602
    flag_address=16*seg+m.off('SOUND:DspProbeIrqSeen');assert mem[flag_address]==1
    assert [(x.kind,x.port,x.size,x.value) for x in c.log[:c.count]]==[(4,7,0,1193),(1,0x20,1,0x20)]
    m.device.pic_mask=0x80;assert not m.device.service(m,*site)
    m.device.pic_mask=0;m.setreg('FLAGS',2);assert not m.device.service(m,*site)
    m.setreg('FLAGS',0x602);assert m.device.service(m,*site)
    m.device.script(0x3da,[8]);result=m.run()
    assert result['AX']==0xa508 and m.rb('SOUND:DspProbeIrqSeen')==1 and m.device.clocks==1193
    # Bounded original execution still rejects a nonreturn and unsupported INT.
    for routine,budget,needle in [('GAME:WaitVerticalRetraceActive',100,'exhausted'),
                                  ('GAME:ComplementHighScoreTable',1,'budget')]:
        m.reset();m.prepare(routine)
        try:m.run(budget)
        except RuntimeError as e:assert needle in str(e),str(e)
        else:raise AssertionError('unbounded/unsupported execution accepted')
    print('PASS platform KAT: contiguous operands, VGA modes/latches/controllers/DAC, vectors/IRET/IRQs, files, BIOS, scripts, OPL, DSP, DMA, PIC/PIT')


if __name__=='__main__':main()
