"""Whole-game gate controls: full-state hashing, IRQ policy and a caught C fault."""
import ctypes as C
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import random
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import cbuild
import wholegame as w
from emu import Devices, MEM_SIZE, NativeVga
from difftest import load_dll


def main():
    with tempfile.TemporaryDirectory(prefix='kat-',dir=w.ROOT/'build/workers/whole') as td:
        scratch=Path(td); path=scratch/'attract.txt'
        path.write_text('entry GAME:PlayAttractDemo\nframes 40\ncard none\n')
        s=w.scenario(path); m,initial=w.fixture(s)
        original,cov,saved=w.original(s,m,initial)
        assert len(original)==40 and 'GAME:RunScriptedDemo' in cov['routines']
        # A RAM-only checkpoint at frame 32 reproduces every later boundary.
        rm,ri=w.fixture(s)
        replay,_,_=w.original(s,rm,ri,resume=saved[32])
        assert replay==original
        accel=NativeVga(scratch)
        try:
            # Same real map/demo rendering with the Python and native hardware
            # callbacks. The game CPU remains Unicorn on both runs.
            w.VGA_ACCELERATOR=accel
            am,ai=w.fixture(s); accelerated,_,_=w.original(s,am,ai)
            assert accelerated==original
            py=Devices(); fast=Devices(); seed=random.Random(0x7630)
            pixels=seed.randbytes(4*65536); py.planes[:]=pixels; fast.planes[:]=pixels
            ptr=C.c_void_p(C.addressof(fast.raw))
            for iteration in range(512):
                gc=seed.randbytes(9); latch=seed.randbytes(4); mask=seed.randrange(16); read_map=seed.randrange(4)
                for d in (py,fast):d.gc[:]=gc;d.latch[:]=latch;d.map_mask=mask;d.read_map=read_map
                off=seed.choice((65535,65534,seed.randrange(65536)));size=seed.choice((1,2,4,8));value=seed.getrandbits(64)
                for j in range(size):py.write(off+j,value>>(8*j))
                accel.dll.vga_write(None,off,size,value,ptr)
                expected=sum(py.read(off+j)<<(8*j) for j in range(size))
                assert accel.dll.vga_read(None,off,size,ptr)==expected
                assert bytes(py.planes)==bytes(fast.planes) and bytes(py.latch)==bytes(fast.latch)
            accel.dll.vga_read(None,0,16,ptr); assert fast.error==1
        finally:
            w.VGA_ACCELERATOR=None;accel.close()
        ram=bytes(MEM_SIZE); sp=initial['SP']
        digest=w.compared_ram(ram,sp)
        for address in (0x20,0x113bf,0x20000,0x6c190,0x8fefe,0x100000):
            b=bytearray(ram); b[address]=1
            assert w.compared_ram(b,sp)!=digest
        b=bytearray(ram); b[0x80002]=1
        assert w.compared_ram(b,sp)==digest
        rolling=hashlib.sha256(); rolling.update(b'a'); rolling.update(b'b')
        assert rolling.digest()==hashlib.sha256(b'ab').digest()
        assert rolling.digest()!=hashlib.sha256(b'ba').digest()
        # Keyboard make/break and E0 are actual IRQ scan bytes.
        path.write_text('frames 2\n1: right -right\n')
        assert w.scenario(path)['events'][1]==[0xe0,0x4d,0xe0,0xcd]
        clock=w.Clock(dict(s,events={0:[0x1e]}),m); dev=Devices()
        clock.service(dev,*clock.poll,2,m.read)
        assert dev.irq_count==0
        clock.service(dev,*clock.poll,0x202,m.read)
        assert dev.irq_count==1 and dev.irqs[0].irq==1
        assert dev.scripts[0].runs[0].value==0x1e

        # Compile an intentionally wrong translation in scratch, never editing
        # maintained C. The normal and instrumented builds use identical flags.
        good=cbuild.build(scratch/'good.dll',trace_dir=scratch/'sources')
        generated=scratch/'sources/scene.c'; content=generated.read_text()
        assert content.count('W(ScreenFadeStep,4);')==1
        generated.write_text(content.replace('W(ScreenFadeStep,4);','W(ScreenFadeStep,8);'))
        receipt=json.loads((scratch/'cbuild.json').read_text()); cmd=receipt['command']
        mutant=scratch/'mutant.dll'; cmd[cmd.index('-o')+1]=str(mutant)
        env=dict(os.environ,PATH=str(cbuild.GCC.parent)+os.pathsep+os.environ.get('PATH',''))
        subprocess.run(cmd,check=True,capture_output=True,env=env)
        with patch('difftest.cbuild.build',return_value=mutant):
            dll=load_dll(); nm,ni=w.fixture(s)
            try:
                failure=w.native(s,nm,ni,dll,original)
                assert failure and failure['frame']==3
                result=w.diagnose(s,failure,original,saved,scratch)
                assert any('ScreenFade' in x for x in result['differences'])
                entry=result['first_entry_difference']
                assert entry['original']['caller']=='GAME:RunScriptedDemo',entry
                assert result['checkpoint_frame']==1
                print('PASS whole KAT: native/Python VGA, replay, complete digest, IRQ inputs, mutation frame 3, named caller')
            finally:
                import _ctypes
                _ctypes.FreeLibrary(dll._handle)
    return 0


if __name__=='__main__': raise SystemExit(main())
