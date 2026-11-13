"""Standalone voice ownership, low-byte indices, forward aliases and raw I/O."""
from difftest import Case,load_suite
BASE=load_suite('adlib').base
CASES=[]
KEEP=('AX','BX','CX','DX','SI','DI','BP','IF','DF')
def add(title,name,setup,args=(),regs=None,flags=0x602,extra=()):
    CASES.append(Case(title,'SOUND:'+name,setup=setup,args=args,regs=regs or {},kind='far',flags=flags,out_regs=KEEP+extra))
contexts=[(0,0,0),(12,0,2),(12,1,2),(13,1,2),(0xffff,2,0x109),(12,1,9),(13,0,0x10)]
for name in ['SetAdlibChannelVolume','SetAdlibChannelGain','KeyOffAdlibChannel','SetAdlibFrequency','LoadAdlibInstrument']:
 for channel in [0,8,9,255,256,264,265,0xffff]:
  for owner,playing,reserved in contexts:
   def setup(m,owner=owner,playing=playing,reserved=reserved):
    BASE(m)
    for n,v in dict(CurrentAdlxSlot=owner,MainAdlxPlaying=playing,ReservedAdlibChannelCount=reserved).items():m.ww('SOUND:'+n,v)
    m.write(0x6000,0x100,bytes((i*23+17)&255 for i in range(12)))
   args=(channel,) if name=='KeyOffAdlibChannel' else (channel,0x100,0x6000) if name=='LoadAdlibInstrument' else (channel,0xa5c3)
   add(f'{name} ch{channel} owner{owner} playing{playing} reserved{reserved}',name,setup,args)
for channel in [0,8]:
 for view in ['AdlibVoiceStates','SavedAdlibVoiceStates']:
  for delta in [-20,-12,-11,-4,-1,0,1,5,11,12,16,20]:
   for owner,playing,reserved in [(0,0,0),(12,0,9),(13,1,9)]:
    def setup(m,owner=owner,playing=playing,reserved=reserved):
     BASE(m)
     for n,v in dict(CurrentAdlxSlot=owner,MainAdlxPlaying=playing,ReservedAdlibChannelCount=reserved).items():m.ww('SOUND:'+n,v)
    # A distinct paragraph representation of the same physical source.
    def args(m,channel=channel,view=view,delta=delta):return (channel,m.off('SOUND:'+view)+20*channel+delta+16,m.seg('SOUND:'+view)-1)
    add(f'alias {channel}/{view}/{delta} owner{owner} playing{playing} reserved{reserved}','LoadAdlibInstrument',setup,args)
for offset in [0xfff7,0xfff9,0xfffe,0xffff]:
 def setup(m,offset=offset):
    BASE(m)
    for i in range(12):m.write(0x6000,(offset+i)&65535,bytes([(i*39+7)&255]))
 add(f'wrapping instrument {offset:x}','LoadAdlibInstrument',setup,(0,offset,0x6000))
for offset in [0,0xffff]:add(f'MMIO instrument {offset:x}','LoadAdlibInstrument',BASE,(0,offset,0xa000))
for channel in range(9):
 for saved in [False,True]:
  for kind in ['floor','ceil','prefix']:
   for offset in [0xfff9,0xffff]:
    def setup(m,channel=channel,saved=saved,kind=kind,offset=offset):
     BASE(m);label='SavedAdlibVoiceStates' if saved else 'AdlibVoiceStates';physical=m.seg('SOUND:'+label)*16+m.off('SOUND:'+label)+20*channel
     if kind=='prefix':bank=((physical+((15-physical)&15))-0xffff)//16
     else:bank=(physical+(15 if kind=='ceil' else 0))//16
     for i in range(12):m.write(bank,(offset+i)&65535,bytes([(i*37+91)&255]))
     for n,v in dict(CurrentAdlxSlot=12 if saved else 13,MainAdlxPlaying=1,ReservedAdlibChannelCount=9).items():m.ww('SOUND:'+n,v)
    def args(m,channel=channel,saved=saved,kind=kind,offset=offset):
     label='SavedAdlibVoiceStates' if saved else 'AdlibVoiceStates';physical=m.seg('SOUND:'+label)*16+m.off('SOUND:'+label)+20*channel
     bank=((physical+((15-physical)&15))-0xffff)//16 if kind=='prefix' else (physical+(15 if kind=='ceil' else 0))//16
     return channel,offset,bank
    add(f'wrapped alias ch{channel} saved{saved} {kind} {offset:x}','LoadAdlibInstrument',setup,args)
for calibration in [0,1,63,64,255]:
 def setup(m,calibration=calibration):BASE(m);m.ww('SOUND:SoundIoDelayMultiplier',0xab00|calibration)
 for packed in [0,0x120,0xfeaf,0xffff]:
  add(f'raw write {packed:x} multiplier{calibration}','WriteAdlibRegister',setup,regs={'BX':packed},extra=('CF','OF'))
 for factor in [0,1,2,4,255]:
  add(f'delay {factor} multiplier{calibration}','DelaySoundIo',setup,regs={'AX':0xa500|factor},extra=('CF','OF'))
