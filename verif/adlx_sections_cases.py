"""Section grammar, modified dispatch, routed application and live handoff."""
from difftest import Case,load_suite
import struct
BASE=load_suite('adlib').base
API=load_suite('sound_api')
CASES=[]
def add(title,routine,setup,args=(),flags=0x202,sound=False):
    CASES.append(Case(title,('SOUND:' if sound else 'C:')+routine,setup=setup,args=args,kind='far',flags=flags,
        out_regs=(('AX',) if routine=='ScanMusicEvents' else ())+('SI','DI','BP','IF','DF')))
def scan(m,stream,off=0x100):
    BASE(m);API.base(m,1)
    for n,v in dict(MainAdlxPlaying=1,MusicVoiceCount=9,MusicTicksPerUnit=1,MainAdlxStartPointer=off,MusicEventStreamLength=len(stream)).items():m.ww('SOUND:'+n,v)
    m.ww('SOUND:MainAdlxStartPointer',0x6000,2)
    for i,b in enumerate(stream):m.write(0x6000,(off+i)&65535,bytes([b]))
streams=[b'\x81\x82\x83\x80',b'\x0f\xff\x81\x80',b'\x77\x03abc\x81\x82\x80',
 b'\x40'+bytes(range(11))+b'\x81\x10\x34\xe0\x30\xff\x20\x60\x01\x02\x70\x02zz\x50\x82\x80',
 b'\x4f'+bytes(range(12))+b'\x81\x80']
for i,stream in enumerate(streams):
 for a,b in [(0,0),(1,2),(2,1),(0xffff,0xffff)]:
  add(f'section grammar{i} {a}/{b}','ScanMusicEvents',lambda m,stream=stream:scan(m,stream),(a,b),0x602)
for off,stream in [(0xffff,b'\x81'),(0xfffe,b'\x81\x82\x80'),(0x100,b'\x81')]:
 add(f'post-fetch limit{off:x}/{len(stream)}','ScanMusicEvents',lambda m,off=off,stream=stream:scan(m,stream,off),(1,2),0x602)
for mutation in ['values','target','duplicate','high-word']:
 def modified(m,mutation=mutation):
    scan(m,b'\x01\x10\x80\x81\x82\x80');s,o=m.address('C:ScanMusicEvents');at=o+0x2c8
    if mutation=='values':
        for i in range(7):m.write(s,at+i*2,struct.pack('<H',0xa500+i))
    elif mutation=='target':m.write(s,at+14,struct.pack('<H',o+0x209))
    elif mutation=='duplicate':m.write(s,at+2,struct.pack('<H',0))
    else:m.write(s,at,struct.pack('<H',0x100))
 add(f'modified scan table {mutation}','ScanMusicEvents',modified,(1,3),0x602)
for count in [0,1,9]:
 for reserved in [0,1,8,9,10,0xffff,0x109,0x101,0x1009]:
  for current in [8,12,13,0xffff]:
   for playing in [0,1,2]:
    for backwards in [False,True]:
     def apply(m,count=count,reserved=reserved,current=current,playing=playing):
        BASE(m);API.base(m,1)
        for n,v in dict(MusicVoiceCount=count,ReservedAdlibChannelCount=reserved,CurrentAdlxSlot=current,MainAdlxPlaying=playing,ScannedMusicClockTicks=0xfffe,MainAdlxTimeOrigin=0xffff).items():m.ww('SOUND:'+n,v)
        m.ww('SOUND:ScannedMusicClockTicks',0xffff,2);m.ww('SOUND:MainAdlxTimeOrigin',0xffff,2)
        m.ww('SOUND:FirstScannedEvent',0xabcd);m.ww('SOUND:FirstScannedEvent',0x6000,2)
        for i in range(9):m.write(m.seg('SOUND:ScannedAdlibVoiceStates'),m.off('SOUND:ScannedAdlibVoiceStates')+20*i,bytes((i*51+j*39+7)&255 for j in range(20)))
     add(f'apply count{count} res{reserved} current{current} playing{playing} DF{backwards}','ApplyScannedMusicEvents',apply,flags=0x602 if backwards else 0x202)
for enabled in [0,1,2,0xffff]:
 for cursor in [0xff,0x100,0x101]:
  for high in [0,1]:
   def tick(m,enabled=enabled,cursor=cursor,high=high):
    BASE(m);API.base(m,1)
    for n,v in dict(MainAdlxPlaying=1,AdlxPlaybackGuard=0,AdlxTickCount=0,AdlxTickHighWord=high,MainAdlxDeadlineLow=0,MainAdlxDeadlineHigh=0,
      MainAdlxCursor=cursor,MainAdlxCursorSegment=0x6000,MainAdlxSectionEnd=0x100,MainAdlxSectionLoopEnabled=enabled,
      FirstScannedEvent=0x100,MusicVoiceCount=0,MainAdlxFlags=5,MainAdlxStepQ8=256).items():
      if n=='MainAdlxStepQ8':continue
      m.ww('SOUND:'+n,v)
    m.ww('SOUND:FirstScannedEvent',0x6000,2);m.write(0x6000,0xff,b'\x81\x81\x81')
   add(f'tick section flag{enabled} cursor{cursor:x} high{high}','TickAdlxPlayback',tick,sound=True)
