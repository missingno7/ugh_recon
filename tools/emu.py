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


class Devices:
    """Pilot contract: unchained VGA, read mode 0, write mode 0, full bit mask.
    Other configurations require their own model and known-answer checks first.
    PIC/PIT bytes are logged; no interrupts arrive implicitly with wall time.
    """
    def __init__(self):
        self.planes = bytearray(4*65536)
        self.latch = bytearray(4)
        self.seq_index, self.map_mask, self.gc_index, self.read_map = 0,15,0,0
        self.log = []

    def read(self, off):
        for p in range(4): self.latch[p] = self.planes[p*65536+(off&65535)]
        return self.latch[self.read_map&3]

    def write(self, off, value):
        for p in range(4):
            if self.map_mask & (1<<p): self.planes[p*65536+(off&65535)] = value&255

    def out(self, port, size, value):
        self.log.append((1,port,size,value))
        for i in range(size):
            p, b = port+i, (value>>(i*8))&255
            if p == 0x3C4: self.seq_index = b
            elif p == 0x3C5 and self.seq_index == 2: self.map_mask = b&15
            elif p in (0x20,0x40,0x43): pass
            else: raise RuntimeError(f'unsupported OUT {p:04X}={b:02X}')

    def inp(self, port, size):
        self.log.append((2,port,size,0))
        raise RuntimeError(f'unsupported IN {port:04X}/{size}')

    def interrupt(self, number, machine):
        self.log.append((3,number,0,machine.reg('AX')))
        raise RuntimeError(f'unsupported INT {number:02X}, AX={machine.reg("AX"):04X}')

    def state(self):
        return bytes(self.planes+self.latch+bytes((self.seq_index,self.map_mask,self.gc_index,self.read_map)))


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
            self.uc.emu_start(self.reg('CS')*16+self.reg('IP'),0,count=budget)
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
