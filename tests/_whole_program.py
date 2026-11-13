"""Bounded program-entry composition; never boots DOS or runs the native EXE."""
import ctypes as C,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from difftest import load_dll,Regs
from emu import Machine,REG_NAMES,MEM_SIZE
from unicorn import UC_HOOK_CODE

def main():
 d=load_dll();m=Machine();limit=2
 m.device.script(0x3da,[0,8],cycles=10000)
 m.device.script(0x201,[255]*10000)
 m.device.script(0xfffe,[0x10203040])
 m.device.script(0x388,[0xe0]) # Explicit failed first OPL probe; no invented card.
 for site in ('loc_1163','loc_116B'):m.device.schedule(m.seg('SOUND:'+site),m.off('SOUND:'+site),clocks=65536)
 initial=m.prepare('GAME:RunDosGame',regs={},flags=0x202)
 original=m.snapshot();devices=m.device.state();frames=[]
 def capture(uc,address,size,user):
  if address==m.seg('GAME:SwapAndDisplayVgaPage')*16+m.off('GAME:SwapAndDisplayVgaPage')+0x2a:
   frames.append((m.snapshot(),m.device.state(),list(m.device.log),m.steps))
   if len(frames)>=limit:m.uc.emu_stop()
 m.uc.hook_add(UC_HOOK_CODE,capture)
 failure=None
 try:
  while m.steps<30000000:
   m.resume_irq=False;m.uc.emu_start(m.reg('CS')*16+m.reg('IP'),0,count=30000000-m.steps)
   if not m.resume_irq:break
  if m.error:failure=str(m.error)
 except Exception as e:failure=f'{type(e).__name__}: {e}'
 mem=d.ugh_memory().contents;C.memmove(mem,original,MEM_SIZE);d.ugh_devices_reset()
 dev=d.ugh_device_state().contents;C.memmove(C.addressof(dev),devices,len(devices))
 results=[]
 CALLBACK=C.CFUNCTYPE(C.c_int,C.POINTER(Regs))
 def compare(rp):
  i=len(results)
  if i>=len(frames):return 2
  asm,device,logs,steps=frames[i];got=bytes(mem);differences=[]
  # The original-frame return scratch is excluded, as in routine tests.
  for a,b in [(0,0x80000),(0x80000+initial['SP'],MEM_SIZE)]:
   if asm[a:b]!=got[a:b]:
    p=next(p for p in range(a,b) if asm[p]!=got[p]);differences.append(f'RAM {p:05X}: {asm[p]:02X}/{got[p]:02X}');break
  cdevice=C.string_at(C.addressof(dev),len(device))
  if cdevice!=device:
   p=next(p for p in range(len(device)) if cdevice[p]!=device[p]);differences.append(f'device {p:X}: {device[p]:02X}/{cdevice[p]:02X}')
  clog=[(e.kind,e.port,e.size,e.value) for e in dev.log[:dev.count]]
  if clog!=logs:differences.append('ordered platform log')
  results.append(dict(frame=i+1,oracle_steps=steps,differences=differences))
  return 2 if differences or len(results)>=limit else 0
 callback=CALLBACK(compare);d.ugh_set_frame_observer.argtypes=[CALLBACK];d.ugh_set_frame_observer(callback)
 r=Regs(**{n.lower():v for n,v in initial.items()});d.c_RunDosGame.argtypes=[C.POINTER(Regs)]
 status=d.c_RunDosGame(C.byref(r));d.ugh_set_frame_observer(CALLBACK())
 result=dict(entry='GAME:0008 (_main / RunDosGame)',frame_limit=limit,oracle_frames=len(frames),
             oracle_failure=failure,oracle_stop=f'{m.reg("CS"):04X}:{m.reg("IP"):04X}',
             c_status=status,frames=results)
 Path('build/workers/c-close/whole-program.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(result,indent=2),flush=True)
 return 0 if len(results)==limit and not failure and all(not r['differences'] for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
