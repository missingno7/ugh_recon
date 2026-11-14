"""Generated complete-entry comparisons; exact persistent RAM/ABI/ordered ports."""
import ctypes as C,random,struct,sys,hashlib,time
from pathlib import Path
from closure_support import ROOT,receipt,save
from input_build import OUT,build,NAMES
sys.path.insert(0,str(ROOT/'tools'))
import contacts_reference,difftest,nbuild
contacts_reference.OUT=OUT/'reference'

def main():
 start=time.perf_counter();plain=contacts_reference.prepare_reference(local=True);dlls=[nbuild.load_l1(build(reference=True)),nbuild.load_l1(build())];m=difftest.Machine();rng=random.Random(11011);rows=[]
 def pair(name,regs=None,flags=None,failure_poll=0):
  initial=m.prepare('GAME:'+name,{**difftest.POISON,'DS':m.seg('DGROUP:PlayerCount'),**(regs or {})},'iret' if name=='HandleKeyboardScanInterrupt' else 'near',(),rng.choice([2,0x202,0x602,0xed7]) if flags is None else flags);memory=m.snapshot();device=m.device.state();results=[]
  for dll in dlls:
   C.memmove(dll.ugh_memory().contents,memory,len(memory));dll.ugh_devices_reset();dev=dll.ugh_device_state().contents;C.memmove(C.addressof(dev),device,len(device));r=difftest.Regs(**{n.lower():v for n,v in initial.items()});callback_type=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs));calls=[0]
   def service(segment,offset,rp):
    if segment==m.seg('GAME:PollKeyboardScanChange') and offset==m.off('GAME:PollKeyboardScanChange'):
     calls[0]+=1
     if failure_poll and calls[0]==failure_poll:rp.contents.ax=0x81a5;rp.contents.flags=0x8d7;return 1
    return 0
   callback=callback_type(service) if failure_poll else callback_type();dll.ugh_set_service_observer.argtypes=[callback_type];dll.ugh_set_service_observer(callback);f=getattr(dll,'c_'+name);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r));dll.ugh_set_service_observer(callback_type());ram=bytes(dll.ugh_memory().contents);events=C.string_at(C.addressof(dev.log),dev.count*C.sizeof(difftest.IoEvent)) if hasattr(difftest,'IoEvent') else C.string_at(C.addressof(dev.log),dev.count*16);results.append((status,bytes(r),ram,events,dev.error))
  a,b=results;assert a[0]==b[0] and a[4]==b[4],(len(rows),name,'status/error',a[0],b[0],a[4],b[4]);assert a[1]==b[1],(len(rows),name,'ABI',struct.unpack('<14H',a[1]),struct.unpack('<14H',b[1]));lo=initial['SS']*16;hi=lo+initial['SP'];assert a[2][:lo]==b[2][:lo] and a[2][hi:]==b[2][hi:],(len(rows),name,'RAM',next((i for i,(x,y) in enumerate(zip(a[2],b[2])) if x!=y and not lo<=i<hi),None));assert a[3]==b[3],(len(rows),name,'ordered I/O');rows.append(dict(name=name,status=a[0],error=a[4],events=len(a[3])//16,RAM_sha256=hashlib.sha256(a[2]).hexdigest(),ports_sha256=hashlib.sha256(a[3]).hexdigest()))
 for i in range(800):
  m.reset();ds=m.seg('DGROUP:PlayerCount');m.device.script(0x60,[rng.randrange(256)]);m.wb('DGROUP:KeyboardSequenceIndex',rng.randrange(256));m.ww('DGROUP:PlayerOneControlMode',rng.randrange(65536));m.ww('DGROUP:PlayerTwoControlMode',rng.randrange(65536))
  for slot in range(34):m.wb('DGROUP:KeyboardSequenceCandidateState',rng.choice([0,1,254,255]),6*slot)
  for slot in [0,2]:
   for name in ['PlayerUpInput','PlayerDownInput','PlayerLeftInput','PlayerRightInput','PlayerActionInput']:m.ww('DGROUP:'+name,rng.randrange(65536),slot)
  # Arbitrary destinations include writes into the matcher table region.
  if i%3==0:
   m.write(ds,m.off('DGROUP:KeyboardSequenceRecords'),bytes([rng.randrange(256),255,rng.randrange(256),rng.randrange(256),rng.randrange(256),0,255]));m.wb('DGROUP:KeyboardSequenceIndex',0)
  pair('HandleKeyboardScanInterrupt')
 for i in range(800):
  m.reset();ds=rng.choice([m.seg('DGROUP:PlayerCount'),0x7500]);m.write(ds,m.off('DGROUP:CurrentKeyboardScanCode'),rng.randbytes(3));m.wb('GAME:LatestInterruptScanCode',rng.randrange(256));pair('PollKeyboardScanChange',{'DS':ds})
 for i in range(600):
  m.reset();mask=rng.randrange(16);limit=rng.choice([0,1,2,3,10,32767,32768,65535]);m.wb('DGROUP:JoystickEnabledAxisMask',mask);m.ww('DGROUP:JoystickSampleLoopLimit',limit);m.device.script(0x201,[rng.randrange(256),rng.randrange(256),*[rng.randrange(256) for _ in range(rng.randrange(12))],0,0,0,0],cycles=0xffffffff);pair('SampleJoystickAxesAndButtons')
 for mask in [16,128,255]:
  m.reset();m.wb('DGROUP:JoystickEnabledAxisMask',mask);m.ww('DGROUP:JoystickSampleLoopLimit',0);m.device.script(0x201,[0],cycles=0xffffffff);pair('SampleJoystickAxesAndButtons')
 for i in range(1200):
  m.reset();ds=m.seg('DGROUP:PlayerCount');m.ww('DGROUP:PlayerCount',rng.choice([0,1,2,3,4,65535]));m.wb('GAME:LatestInterruptScanCode',rng.randrange(256));m.device.script(0x201,[rng.randrange(256),rng.randrange(256)],cycles=0xffffffff);m.wb('DGROUP:JoystickEnabledAxisMask',0);m.ww('DGROUP:JoystickSampleLoopLimit',rng.randrange(65536))
  for slot in [0,2]:
   m.ww('DGROUP:PlayerOneControlMode',rng.choice([0,1,65535,32768,16384,16383,32767,65534,rng.randrange(65536)]),slot)
   for name in ['FirstJoystickXCount','FirstJoystickYCount','JoystickLeftThresholds','JoystickRightThresholds','JoystickUpThresholds','JoystickDownThresholds','JoystickButtonBits','PlayerUpInput','PlayerDownInput','PlayerLeftInput','PlayerRightInput','PlayerActionInput']:m.ww('DGROUP:'+name,rng.randrange(65536),slot)
  pair('PollPlayerControls')
 for presence in range(4):
  for ticks in [0,1,2,7,32767,32768,32769,65535]:
   m.reset();first=(0xf0|(0 if presence&1 else 3)|(0 if presence&2 else 12));m.device.script(0x201,[first,first]+[255]*ticks+[0]*4,cycles=0xffffffff);m.ww('DGROUP:PlayerOneControlMode',0x8123);m.ww('DGROUP:PlayerTwoControlMode',0x8456)
   for name in ['JoystickLeftThresholds','JoystickRightThresholds','JoystickUpThresholds','JoystickDownThresholds']:m.ww('DGROUP:'+name,0xbeef);m.ww('DGROUP:'+name,0xbeef,2)
   pair('DetectAndCalibrateJoysticks')
 for name in ['HandleKeyboardScanInterrupt','InstallKeyboardSequenceInterrupt']:
  m.reset();m.write(m.seg('DGROUP:PlayerCount'),0,bytes(65536));m.device.script(0x60,[0],cycles=0xffffffff);pair(name)
 for name in ['InstallKeyboardSequenceInterrupt','RestoreKeyboardInterrupt']:
  for i in range(150):
   m.reset();m.write(0,0x24,rng.randbytes(4));m.write(0x40,0x1a,rng.randbytes(4));m.ww('DGROUP:PreviousKeyboardVector',rng.randrange(65536));m.ww('DGROUP:PreviousKeyboardVectorSegment',rng.randrange(65536))
   m.device.dos_error=5 if i%5==0 else 0;m.device.dos_error_skip=i%2
   if name=='InstallKeyboardSequenceInterrupt':
    for slot in range(34):m.wb('DGROUP:KeyboardSequenceCandidateState',rng.randrange(256),6*slot)
   pair(name)
 video=difftest.load_suite('video')
 for i in range(50):
  m.reset();video.input_setup(m,rng.choice([16,32,64,128]));m.device.script(0x3da,[0,8],cycles=0xffffffff);pair('WaitForScanChangeOrJoystickButton')
 for name in ['SampleJoystickAxesAndButtons','DetectAndCalibrateJoysticks']:
  m.reset();pair(name)
 for failure in [1,2]:
  m.reset();video.input_setup(m);m.device.script(0x3da,[0,8],cycles=0xffffffff);pair('WaitForScanChangeOrJoystickButton',failure_poll=failure)
 save(OUT/'cases.json',receipt([sys.executable,'verif/input_evidence.py'],[Path(__file__),ROOT/'verif/input_build.py',ROOT/'native/input.c',ROOT/'native/input.h',ROOT/'native/bridge/input_bridge.c',ROOT/'c/dos_input.c',ROOT/'c/scene.c',ROOT/'c/game_services.c',ROOT/'c/video.c',plain],result='PASS',cases=rows,seconds=time.perf_counter()-start));print('PASS',len(rows),'compiled complete input pairs',flush=True)
if __name__=='__main__':main()
