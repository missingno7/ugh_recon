"""Abnormal far CALL/near RET landing states; diagnostic, never return acceptance."""
import ctypes as C
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from difftest import load_dll,Regs,POISON
from emu import Machine,REG_NAMES,MEM_SIZE,STACK_SEG

def main():
 d=load_dll();m=Machine();mem=d.ugh_memory().contents;rows=[]
 for routine,landing,args in [('SOUND:ProbeSoundBlasterDmaIrq',0x1f19,()),
       ('SOUND:ShutdownDspPlayback',0x20c5,()),('SOUND:InitializeDspPlayback',0x1f19,()),
       ('C:LoadSoundBankResource',0x116,(1,2,3,4,5,6)),('C:InitializeSoundSystem',0x1f19,(2,))]:
  m.reset();m.ww('SOUND:DspBasePort',0x220);m.ww('SOUND:SoundIoDelayMultiplier',1)
  m.device.script(0x22c,[0]*10)
  if routine in ('SOUND:InitializeDspPlayback','C:InitializeSoundSystem'):
   m.device.schedule(m.seg(routine),m.off('SOUND:loc_1163')) if False else None
   for site in ('loc_1163','loc_116B'):m.device.schedule(m.seg('SOUND:'+site),m.off('SOUND:'+site),clocks=65536)
  initial=m.prepare(routine,regs=POISON,kind='far',args=args,flags=0x602)
  snapshot=m.snapshot();device=m.device.state()
  m.stop_at=m.seg('GAME:RunDosGame')*16+landing
  while m.steps<1000000:
   m.resume_irq=False;m.uc.emu_start(m.reg('CS')*16+m.reg('IP'),0,count=1000000-m.steps)
   if not m.resume_irq:break
  assert not m.error and m.returned,(routine,m.error,m.steps)
  want={n:m.reg(n) for n in REG_NAMES};asm=m.snapshot()
  C.memmove(mem,snapshot,MEM_SIZE);d.ugh_devices_reset();dev=d.ugh_device_state().contents
  C.memmove(C.addressof(dev),device,len(device));r=Regs(**{n.lower():v for n,v in initial.items()})
  fn=getattr(d,'c_'+routine.split(':')[1]);fn.argtypes=[C.POINTER(Regs)]
  assert fn(C.byref(r))==4
  for n in REG_NAMES:
   if n=='FLAGS':
    # Arithmetic scratch is not a C compiler ABI, but IF/DF always flow.
    assert (r.flags^want[n])&0x600==0,(routine,n,hex(want[n]),hex(r.flags))
   else:assert getattr(r,n.lower())==want[n],(routine,n,hex(want[n]),hex(getattr(r,n.lower())))
  for a,b in ((0,STACK_SEG*16),(STACK_SEG*16+initial['SP'],MEM_SIZE)):
   assert bytes(mem[a:b])==asm[a:b],routine
  # Unlike normal final-return tests, inspect the actual retained caller CS.
  a=r.ss*16+r.sp
  end=r.ss*16+initial['SP']+4+2*len(args)
  assert bytes(mem[a:end])==asm[a:end],(routine,'live stack differs')
  assert int.from_bytes(asm[a:a+2],'little')==(initial['CS'] if routine=='C:LoadSoundBankResource' else m.seg('SOUND:DspBasePort'))
  assert C.string_at(C.addressof(dev),len(device))==m.device.state(),routine
  assert [(x.kind,x.port,x.size,x.value) for x in dev.log[:dev.count]]==m.device.log
  rows.append(dict(routine=routine,landing=f'{r.cs:04X}:{r.ip:04X}',sp=f'{r.sp:04X}',steps=m.steps))
  print('PASS control landing',routine,rows[-1],flush=True)
 Path('build/workers/c-close/abi-landings.json').write_text(json.dumps(rows,indent=2))
if __name__=='__main__':main()
