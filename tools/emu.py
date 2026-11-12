"""Bounded single-routine oracle: rebuilt plain EXE only, never a DOS boot.

Loads all MZ relocations at 1010h, preserves all frames, uses independent Python
device hooks. Calls stop on a checked near/far/IRET return sentinel; unhandled
interrupts, ports, callbacks and budget exhaustion are errors.
"""
import struct
from unicorn import (Uc, UcError, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE,
                     UC_HOOK_INTR, UC_HOOK_INSN)
from unicorn.x86_const import *
from common import MZ
import cgen

LOAD = cgen.LOAD
MEM_SIZE = 0x110000
STACK_SEG, STACK_TOP, SENTINEL = 0x8000, 0xFF00, 0xFFF0
DATA_SEG = LOAD + cgen.FRAMES['DGROUP']
REG_NAMES = ('AX','BX','CX','DX','SI','DI','BP','SP','CS','DS','ES','SS','IP','FLAGS')
REG = {name: globals()['UC_X86_REG_'+name] for name in REG_NAMES}
FLAGS = dict(CF=1,PF=4,AF=16,ZF=64,SF=128,IF=512,DF=1024,OF=2048)


import ctypes as C
class IoEvent(C.Structure):
    _fields_=[(n,C.c_uint32) for n in ('kind','port','size','value')]
class ScriptRun(C.Structure):
    _fields_=[('value',C.c_uint32),('repeat',C.c_uint32)]
class InputScript(C.Structure):
    _fields_=[(n,C.c_uint32) for n in ('port','count','cursor','used')]+[('runs',ScriptRun*128)]
class IrqEvent(C.Structure):
    _fields_=[(n,C.c_uint32) for n in ('segment','offset','skip','irq','clocks')]
class DosFile(C.Structure):
    _fields_=[('name',C.c_uint8*64),('data',C.c_uint8*8192),('exists',C.c_uint32),('length',C.c_uint32)]
class DosHandle(C.Structure):
    _fields_=[(n,C.c_uint32) for n in ('active','file','position','mode')]
class DeviceState(C.Structure):
    _fields_=[('planes',C.c_uint8*(4*65536)),('latch',C.c_uint8*4)]+[
        (n,C.c_uint8) for n in ('seq_index','map_mask','gc_index','read_map')]+[
        (n,C.c_uint8*k) for n,k in [('gc',9),('seq',5),('crtc',25),('attr',21),('dac',768)]]+[
        (n,C.c_uint8) for n in ('crtc_index','attr_index','attr_phase','dac_index','dac_component','opl_index')]+[
        ('opl',C.c_uint8*256)]+[(n,C.c_uint8) for n in ('pic_mask','dma_flip','dma_mode','dma_mask','dma_page')]+[
        (n,C.c_uint16) for n in ('dma_address','dma_count','pit_divisor')]+[
        (n,C.c_uint8) for n in ('pit_phase','pit_command','video_mode','video_page','video_columns','exit_code','exited')]+[
        ('clocks',C.c_uint32),('script_count',C.c_uint32),('scripts',InputScript*16),
        ('irq_count',C.c_uint32),('irq_cursor',C.c_uint32),('irqs',IrqEvent*64),
        ('files',DosFile*8),('handles',DosHandle*32),('io_limit',C.c_uint32),('dos_error',C.c_uint32),
        ('count',C.c_uint32),('error',C.c_uint32),('log',IoEvent*270000)]


class Devices:
    """Finite, serializable hardware fixtures. No host input, files or time.

    Raw port scripts are run-length encoded; FFFF is BIOS keys, FFFE DOS time.
    IRQ events identify an original polling instruction, visits to skip, IRQ and
    integer PIT clocks. Delivery occurs only with IF set and that IRQ unmasked.
    """
    def __init__(self):
        self.raw=DeviceState(); self.log=[]
        self.map_mask=15; self.seq[2]=15; self.gc[8]=255
        self.video_mode=3; self.video_columns=80

    def __getattr__(self,name): return getattr(self.raw,name)
    def __setattr__(self,name,value):
        if name in ('raw','log'): object.__setattr__(self,name,value)
        elif hasattr(self.raw,name): setattr(self.raw,name,value)
        else: object.__setattr__(self,name,value)

    def state(self): return C.string_at(C.addressof(self.raw),DeviceState.count.offset)

    def script(self,port,values):
        runs=[]
        for v in values:
            if runs and runs[-1][0]==v: runs[-1][1]+=1
            else: runs.append([v,1])
        if len(runs)>128 or self.script_count>=16: raise ValueError('fixture script capacity')
        if any(self.scripts[i].port==port for i in range(self.script_count)): raise ValueError('duplicate port script')
        s=self.scripts[self.script_count]; self.script_count+=1; s.port=port; s.count=len(runs)
        for i,(v,n) in enumerate(runs): s.runs[i]=ScriptRun(v,n)

    def _script(self,port):
        return next((self.scripts[i] for i in range(self.script_count) if self.scripts[i].port==port),None)

    def _take(self,port,peek=False):
        s=self._script(port)
        if s is None or s.cursor>=s.count: raise RuntimeError(f'exhausted input script {port:04X}')
        v=s.runs[s.cursor].value
        if not peek:
            s.used+=1
            if s.used==s.runs[s.cursor].repeat: s.cursor+=1; s.used=0
        return v

    def schedule(self,segment,offset,irq=0,skip=0,clocks=1):
        if not 0<=irq<=7 or self.irq_count>=64: raise ValueError('IRQ fixture capacity/range')
        self.irqs[self.irq_count]=IrqEvent(segment,offset,skip,irq,clocks); self.irq_count+=1

    def file(self,name,data=b''):
        name=name.encode('ascii') if isinstance(name,str) else name
        if len(name)>63 or len(data)>8192: raise ValueError('file fixture capacity')
        f=next((f for f in self.files if not f.exists),None)
        if f is None: raise ValueError('file fixture slots exhausted')
        f.name[:len(name)]=name; f.data[:len(data)]=data; f.length=len(data); f.exists=1

    def read(self,off):
        for p in range(4): self.latch[p]=self.planes[p*65536+(off&65535)]
        if self.gc[5]&8:
            result=255
            for p in range(4):
                if self.gc[7]&(1<<p): result &= self.latch[p] ^ (0 if self.gc[2]&(1<<p) else 255)
            return result
        return self.latch[self.read_map&3]

    def write(self,off,value):
        rotate=self.gc[3]&7; value&=255
        rotated=((value>>rotate)|(value<<(8-rotate)))&255
        mode=self.gc[5]&3; op=(self.gc[3]>>3)&3
        for p in range(4):
            if not self.map_mask&(1<<p): continue
            latch=self.latch[p]; mask=self.gc[8]
            if mode==1: result=latch
            else:
                if mode==0: source=(255 if self.gc[0]&(1<<p) else 0) if self.gc[1]&(1<<p) else rotated
                elif mode==2: source=255 if value&(1<<p) else 0
                else: source=255 if self.gc[0]&(1<<p) else 0; mask &= rotated
                source=[source,source&latch,source|latch,source^latch][op]
                result=(source&mask)|(latch&(~mask&255))
            self.planes[p*65536+(off&65535)]=result

    def out(self,port,size,value):
        self.log.append((1,port,size,value))
        if size not in (1,2): raise RuntimeError('unsupported OUT width')
        for i in range(size):
            p,b=(port+i)&65535,(value>>(8*i))&255
            if p==0x3c4: self.seq_index=b
            elif p==0x3c5 and self.seq_index<5:
                self.seq[self.seq_index]=b
                if self.seq_index==2: self.map_mask=b&15
            elif p==0x3ce: self.gc_index=b
            elif p==0x3cf and self.gc_index<9:
                self.gc[self.gc_index]=b
                if self.gc_index==4: self.read_map=b&3
            elif p==0x3d4: self.crtc_index=b
            elif p==0x3d5 and self.crtc_index<25: self.crtc[self.crtc_index]=b
            elif p==0x3c0:
                if not self.attr_phase: self.attr_index=b&31
                elif self.attr_index<21: self.attr[self.attr_index]=b
                else: raise RuntimeError('unsupported attribute index')
                self.attr_phase^=1
            elif p==0x3c8: self.dac_index=b; self.dac_component=0
            elif p==0x3c9:
                self.dac[3*self.dac_index+self.dac_component]=b&63; self.dac_component+=1
                if self.dac_component==3: self.dac_component=0; self.dac_index=(self.dac_index+1)&255
            elif p==0x388: self.opl_index=b
            elif p==0x389: self.opl[self.opl_index]=b
            elif p==0x20 and b==0x20: pass
            elif p==0x21: self.pic_mask=b
            elif p==0x40:
                self.pit_divisor=(self.pit_divisor&255)|(b<<8) if self.pit_phase else (self.pit_divisor&0xff00)|b
                self.pit_phase^=1
            elif p==0x43 and b==0x36: self.pit_command=b; self.pit_phase=0
            elif p in (2,3):
                name='dma_address' if p==2 else 'dma_count'; old=getattr(self,name)
                setattr(self,name,(old&255)|(b<<8) if self.dma_flip else (old&0xff00)|b); self.dma_flip^=1
            elif p==0xa: self.dma_mask=b
            elif p==0xb: self.dma_mode=b
            elif p==0xc: self.dma_flip=0
            elif p==0x83: self.dma_page=b
            elif p==0x201 and self._script(p) is not None: self._script(p).cursor=0; self._script(p).used=0
            elif 0x206<=p<=0x26e and p&15 in (6,12) and (self._script((p&0xfff0)+12) is not None or self._script((p&0xfff0)+14) is not None): pass
            else: raise RuntimeError(f'unsupported OUT {p:04X}={b:02X}')

    def inp(self,port,size):
        if size!=1: raise RuntimeError('unsupported IN width')
        if port==0x3c5 and self.seq_index<5: v=self.seq[self.seq_index]
        elif port==0x3cf and self.gc_index<9: v=self.gc[self.gc_index]
        elif port==0x3d5 and self.crtc_index<25: v=self.crtc[self.crtc_index]
        elif port==0x3c1 and self.attr_index<21: v=self.attr[self.attr_index]
        elif port==0x21: v=self.pic_mask
        else:
            v=self._take(port)
            if port==0x3da: self.attr_phase=0
        self.log.append((2,port,size,v)); return v

    def interrupt(self,number,m):
        ax=m.reg('AX'); ah,al=ax>>8,ax&255; self.log.append((3,number,0,ax))
        def result(v,error=False):
            m.setreg('AX',v); m.setreg('FLAGS',(m.reg('FLAGS')&~1)|int(error))
        if number==0x21 and ah==0x35:
            off,seg=struct.unpack('<HH',m.read(0,4*al,4)); m.setreg('BX',off); m.setreg('ES',seg)
        elif number==0x21 and ah==0x25: m.write(0,4*al,struct.pack('<HH',m.reg('DX'),m.reg('DS')))
        elif number==0x21 and ah==0x2c:
            v=self._take(0xfffe); m.setreg('CX',v>>16); m.setreg('DX',v)
        elif number==0x21 and ah==0x4c: self.exited=1; self.exit_code=al
        elif number==0x10 and ah==0: self.video_mode=al; self.video_page=0
        elif number==0x10 and ah==15:
            m.setreg('AX',self.video_mode+256*self.video_columns); m.setreg('BX',(m.reg('BX')&255)+256*self.video_page)
        elif number==0x16 and ah in (0,1):
            s=self._script(0xffff)
            if ah==1 and (s is None or s.cursor==s.count): m.setreg('FLAGS',m.reg('FLAGS')|64)
            else:
                m.setreg('AX',self._take(0xffff,peek=ah==1))
                if ah==1: m.setreg('FLAGS',m.reg('FLAGS')&~64)
        elif number==0x21 and 0x3c<=ah<=0x40:
            if self.dos_error:
                e=self.dos_error; self.dos_error=0; result(e,True); return
            if ah in (0x3c,0x3d):
                name=bytearray()
                for i in range(63):
                    b=m.read(m.reg('DS'),(m.reg('DX')+i)&65535,1)[0]
                    if not b: break
                    name.append(b)
                else: result(3,True); return
                padded=bytes(name).ljust(64,b'\0')
                f=next((i for i,x in enumerate(self.files) if x.exists and bytes(x.name)==padded),None)
                if f is None and ah==0x3d: result(2,True); return
                h=next((i for i in range(5,32) if not self.handles[i].active),None)
                if f is None: f=next((i for i,x in enumerate(self.files) if not x.exists),None)
                if h is None or f is None: result(4,True); return
                if ah==0x3c: self.files[f].name[:]=padded; self.files[f].length=0; self.files[f].exists=1
                self.handles[h]=DosHandle(1,f,0,2 if ah==0x3c else al); result(h)
            else:
                index=m.reg('BX')
                if index>=32 or not self.handles[index].active: result(6,True); return
                h=self.handles[index]; f=self.files[h.file]
                if ah==0x3e: h.active=0; result(0); return
                length=m.reg('CX'); length=min(length,self.io_limit) if self.io_limit else length
                if ah==0x3f:
                    if h.mode==1: result(5,True); return
                    length=min(length,max(0,f.length-h.position))
                    for i in range(length): m.write(m.reg('DS'),(m.reg('DX')+i)&65535,bytes((f.data[h.position+i],)))
                else:
                    if h.mode==0: result(5,True); return
                    length=min(length,8192-h.position)
                    for i in range(length): f.data[h.position+i]=m.read(m.reg('DS'),(m.reg('DX')+i)&65535,1)[0]
                    if not m.reg('CX') or h.position+length>f.length: f.length=h.position+length
                h.position+=length; result(length)
        else: raise RuntimeError(f'unsupported INT {number:02X}, AX={ax:04X}')

    def service(self,m,segment,offset):
        if self.irq_cursor>=self.irq_count: return False
        e=self.irqs[self.irq_cursor]
        if e.segment!=segment or e.offset!=offset: return False
        if e.skip: e.skip-=1; return False
        if not m.reg('FLAGS')&512 or self.pic_mask&(1<<e.irq): return False
        self.clocks=(self.clocks+e.clocks)&0xffffffff; self.irq_cursor+=1; self.log.append((4,e.irq,0,e.clocks))
        sp=(m.reg('SP')-6)&65535
        m.write(m.reg('SS'),sp,struct.pack('<HHH',offset,segment,m.reg('FLAGS')))
        m.setreg('SP',sp); m.setreg('FLAGS',m.reg('FLAGS')&~0x300)
        off,seg=struct.unpack('<HH',m.read(0,4*(8+e.irq),4)); m.setreg('CS',seg); m.setreg('IP',off)
        return True


class Machine:
    def __init__(self, coverage=False):
        mz, self.symbols = cgen.read_symbols()
        self.image = bytearray(mz.image)
        for site in mz.sites:
            v = struct.unpack_from('<H', self.image, site)[0]
            struct.pack_into('<H', self.image, site, (v+LOAD)&65535)
        self.raw_image = mz.image
        self.uc = Uc(UC_ARCH_X86, UC_MODE_16)
        self.uc.mem_map(0,0xA0000)
        self.uc.mem_map(0xB0000,MEM_SIZE-0xB0000)
        self.uc.mmio_map(0xA0000,65536,self._vread,None,self._vwrite,None)
        self.uc.hook_add(UC_HOOK_CODE,self._code)
        self.uc.hook_add(UC_HOOK_INSN,self._in,None,1,0,UC_X86_INS_IN)
        self.uc.hook_add(UC_HOOK_INSN,self._out,None,1,0,UC_X86_INS_OUT)
        self.uc.hook_add(UC_HOOK_INTR,self._intr)
        self.coverage = coverage
        self.executed = set()
        self.reset()

    def reset(self):
        self.device = Devices()
        self.restore(bytes(MEM_SIZE))
        self.uc.mem_write(LOAD*16,bytes(self.image))
        self.steps = 0
        self.error = None
        self.returned = False

    def address(self, name):
        if name not in self.symbols: raise KeyError('use MODULE:Name: '+name)
        x = self.symbols[name]
        return LOAD+x['frame'], x['offset']

    def off(self, name): return self.address(name)[1]
    def seg(self, name): return self.address(name)[0]
    def read(self, seg, off, n):
        return bytes(self.uc.mem_read(seg*16+off,n))
    def write(self, seg, off, value): self.uc.mem_write(seg*16+off,bytes(value))
    def rb(self, name, delta=0):
        s,o=self.address(name); return self.read(s,(o+delta)&65535,1)[0]
    def rw(self, name, delta=0):
        s,o=self.address(name); return struct.unpack('<H',self.read(s,(o+delta)&65535,2))[0]
    def wb(self, name, value, delta=0):
        s,o=self.address(name); self.write(s,(o+delta)&65535,bytes((value&255,)))
    def ww(self, name, value, delta=0):
        s,o=self.address(name); self.write(s,(o+delta)&65535,struct.pack('<H',value&65535))
    def reg(self, name): return self.uc.reg_read(REG[name])&65535
    def setreg(self,name,value): self.uc.reg_write(REG[name],value&65535)

    def snapshot(self):
        return (bytes(self.uc.mem_read(0,0xA0000)) + bytes(65536) +
                bytes(self.uc.mem_read(0xB0000,MEM_SIZE-0xB0000)))

    def restore(self, data):
        self.uc.mem_write(0,bytes(data[:0xA0000]))
        self.uc.mem_write(0xB0000,bytes(data[0xB0000:]))

    def _vread(self,uc,offset,size,user):
        try: return sum(self.device.read(offset+i)<<(8*i) for i in range(size))
        except Exception as e: self.error=e; uc.emu_stop(); return 0
    def _vwrite(self,uc,offset,size,value,user):
        for i in range(size): self.device.write(offset+i,value>>(i*8))
    def _in(self,uc,port,size,user):
        try: return self.device.inp(port,size)
        except Exception as e: self.error=e; uc.emu_stop(); return 0
    def _out(self,uc,port,size,value,user):
        try: self.device.out(port,size,value)
        except Exception as e: self.error=e; uc.emu_stop()
    def _intr(self,uc,number,user):
        try: self.device.interrupt(number,self)
        except Exception as e: self.error=e; uc.emu_stop()
    def _code(self,uc,address,size,user):
        if address==self.stop_at:
            self.returned=True; uc.emu_stop(); return
        if self.device.service(self,self.reg('CS'),self.reg('IP')):
            self.resume_irq=True; uc.emu_stop(); return
        self.steps+=1
        if self.coverage: self.executed.add(address-LOAD*16)

    def prepare(self, routine, regs=None, kind='near', args=(), flags=0x202):
        """Put far-cdecl words after the return frame, identical for ASM and C.
        SS is a dedicated scratch segment outside all loaded program/data bytes.
        """
        segment, offset = self.address(routine)
        initial=dict.fromkeys(REG_NAMES,0)
        initial.update(CS=segment,IP=offset,DS=DATA_SEG,ES=DATA_SEG,SS=STACK_SEG,FLAGS=flags)
        initial.update(regs or {})
        if initial['SS']!=STACK_SEG: raise ValueError('test stack must use the dedicated scratch segment')
        frame=[SENTINEL] + ([segment] if kind in ('far','iret') else [])
        if kind=='iret':
            frame.append(initial['FLAGS'])
            initial['FLAGS'] &= ~0x300 # hardware interrupt entry clears IF and TF, not DF
        initial['SP']=STACK_TOP-len(frame)*2
        for k,v in initial.items(): self.setreg(k,v)
        self.write(STACK_SEG,initial['SP'],struct.pack('<'+'H'*(len(frame)+len(args)),*frame,*args))
        self.stop_at=segment*16+SENTINEL
        self.return_size=len(frame)*2
        return initial

    def run(self,budget=5_000_000):
        self.returned=False; self.steps=0
        try:
            while self.steps<budget:
                self.resume_irq=False
                self.uc.emu_start(self.reg('CS')*16+self.reg('IP'),0,count=budget-self.steps)
                if not self.resume_irq: break
        except UcError as e:
            raise RuntimeError(f'{e} at {self.reg("CS"):04X}:{self.reg("IP"):04X}') from e
        if self.error: raise self.error
        if not self.returned:
            raise RuntimeError(f'budget {budget} exhausted at {self.reg("CS"):04X}:{self.reg("IP"):04X}')
        if self.reg('SP')!=STACK_TOP:
            raise RuntimeError(f'return stack imbalance: SP={self.reg("SP"):04X}')
        return {k:self.reg(k) for k in REG_NAMES}


if __name__=='__main__':
    m=Machine()
    print(f'loaded rebuilt image: {len(m.image)} bytes, {len(m.symbols)} symbol aliases; no code executed')
