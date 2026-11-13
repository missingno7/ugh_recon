"""Lifetime/reset/calibration L0 cases; generated inputs, never oracle output."""
import struct,random
from difftest import Case,load_suite
BASE=load_suite('adlib').base
REGS=('AX','BX','CX','DX','SI','DI','BP','IF','DF')
CASES=[]
for pattern in [0,1,0xa5,0xff]:
 def setup(m,pattern=pattern):
    BASE(m);m.write(m.seg('SOUND:ClearSoundState'),12,bytes((pattern+i*31)&255 for i in range(0x488)))
    m.ww('SOUND:SoundIoDelayMultiplier',0xdef0);m.ww('SOUND:CalibrationLoopRemainder',0x1234)
    m.wb('SOUND:AdlibInitAttempted',0x7b)
 CASES.append(Case(f'common PCM/ADLX reset {pattern}','SOUND:ClearSoundState',setup=setup,kind='far',flags=0xed7,out_regs=REGS))
for routine in ['BeginSoundDelayMeasurement','FinishSoundDelayMeasurement']:
 for cx,dx in [(0,0),(1,1),(65535,65535),(32768,32767),(65535,0),(0,65535)]:
  def setup(m):
    BASE(m);m.ww('SOUND:PreviousCalibrationTimerVector',0x2468);m.ww('SOUND:PreviousCalibrationTimerSegment',0x1357)
  CASES.append(Case(f'{routine} raw {cx}/{dx}','SOUND:'+routine,setup=setup,regs=dict(CX=cx,DX=dx),kind='iret',flags=0xed7,out_regs=REGS))
for first,second in [(0,0),(1,1),(2,65535),(0,65536),(3,65537),(1,131071),(0,131072)]:
 def setup(m,first=first,second=second):
    BASE(m);m.write(0,0x20,struct.pack('<HH',0x2468,0x1357));bank=m.seg('SOUND:CalibrateSoundDelay')
    m.device.schedule(bank,m.off('SOUND:loc_1163'),skip=first,clocks=65536)
    m.device.schedule(bank,m.off('SOUND:loc_116B'),skip=second,clocks=65536)
 CASES.append(Case(f'calibration block boundary {first}/{second}','SOUND:CalibrateSoundDelay',setup=setup,kind='far',flags=0xed7,out_regs=REGS+('CF','PF','AF','ZF','SF','OF')))
for attempted in [0,1,2,128,255]:
 for installed in [0,1]:
  def setup(m,attempted=attempted,installed=installed):
    BASE(m);m.wb('SOUND:AdlibInitAttempted',attempted);m.ww('TIMER:TimerInterruptInstalled',installed)
    m.ww('DGROUP:PreviousInt08Offset',0x1234);m.ww('DGROUP:PreviousInt08Segment',0x5678)
  CASES.append(Case(f'shutdown cached {attempted} installed {installed}','SOUND:ShutdownAdlibPlayback',setup=setup,kind='far',flags=0xed7,out_regs=REGS))
for statuses in [(0x20,), (0x80,), (0xff,), (0,0), (0x1f,0x1f), (0,0x20),(0,0x40),(0,0x80),(0,0xe0),(0x1f,0xff)]:
 def setup(m,statuses=statuses):
    BASE(m);m.device.script(0x388,statuses);m.write(0,0x20,struct.pack('<HH',0x2468,0x1357));bank=m.seg('SOUND:CalibrateSoundDelay')
    m.device.schedule(bank,m.off('SOUND:loc_1163'),skip=0,clocks=65536)
    m.device.schedule(bank,m.off('SOUND:loc_116B'),skip=1,clocks=65536)
 CASES.append(Case(f'probe bitmask {statuses}','SOUND:InitializeAdlibPlayback',setup=setup,kind='far',flags=0x602,out_regs=REGS))
