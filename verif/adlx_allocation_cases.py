"""Allocation policy, steal/restore ordering, stale owners and capacity edges."""
from difftest import Case,load_suite
import struct
BASE=load_suite('adlib').base
API=load_suite('sound_api')
CASES=[]
def desc(m,x,d,v):m.ww('SOUND:AudioChannelStates',v,x*42+d)
def init(m,slot,count,reserved,first,music,owner,playing):
    BASE(m)
    for n,v in dict(SoundDeviceBits=1,ReservedAdlibChannelCount=reserved,MusicVoiceCount=music,
        MainAdlxPlaying=playing,MusicTrackVolume=0xfedf,CurrentAdlxSlot=owner,AdlxPlaybackGuard=0xa523).items():m.ww('SOUND:'+n,v)
    for x in range(8,12):
        for d,v in [(34,0),(36,0xffff),(40,0)]:desc(m,x,d,v)
    for d,v in [(6,0x1234),(8,0x7890),(16,0x9876),(18,0x6543),(34,count),(36,first),(40,5)]:desc(m,slot,d,v)
    for i in range(9):m.ww('SOUND:AdlibChannelOwnerSlot',owner,i*20)
    # The effect instrument's physical9 owner aliases this cell.
    m.ww('SOUND:SavedAdlibVoiceStates',0xbeef,16)
def add(name,routine,setup,args,df=False):
    CASES.append(Case(name,'C:'+routine,setup=setup,args=args,kind='far',flags=0x602 if df else 0x202,
        out_regs=(('AX',) if routine in ['StartAdlibTrackChannel','PlayAdlibEffect'] else ())+('SI','DI','BP','IF','DF')))
for slot in range(8,12):
 for count,reserved,first in [(0,0,9),(1,1,8),(1,3,8),(2,4,7),(4,9,5),(9,9,0)]:
  for music,owner,playing in [(0,8,0),(9,8,1),(9,12,0),(9,13,1),(0,0xffff,1)]:
   for op in ['StopAdlibTrackChannel','RestoreAdlibVoiceAllocation']:
    def setup(m,slot=slot,count=count,reserved=reserved,first=first,music=music,owner=owner,playing=playing):
        init(m,slot,count,reserved,first,music,owner,playing)
        peer=9 if slot==8 else 8
        for d,v in [(34,reserved-count),(36,9-reserved),(40,6)]:desc(m,peer,d,v)
    add(f'{op} slot{slot} n{count} r{reserved} base{first} music{music} owner{owner}',op,setup,(slot,))
for slot in [8,11,12]:
 for count,reserved in [(0,0),(1,0),(3,2),(9,0),(2,8),(10,0),(0xffff,1)]:
  for volume in [0,255,256,0xffff]:
   for playing in [0,1]:
    def setup(m,slot=slot,count=count,reserved=reserved,playing=playing):
        init(m,8,0,reserved,9,9,12,playing)
        for d,v in [(34,count),(36,0 if slot==12 else 9),(40,4)]:desc(m,slot,d,v)
    # Main malformed huge voice counts would escape the typed owner, and are
    # not useful finite L0 tests. Corrupt effect capacity failure is finite.
    if slot==12 and count>9:continue
    add(f'start {slot} n{count} r{reserved} vol{volume} playing{playing}','StartAdlibTrackChannel',setup,(slot,volume))
for op in ['StopAdlibTrackChannel','RestoreAdlibVoiceAllocation','StartAdlibTrackChannel']:
 for count,reserved,first in [(1,1,8),(1,3,8),(2,4,7)]:
  def setup(m,op=op,count=count,reserved=reserved,first=first):
    init(m,8,count,reserved,first,9,8,1)
    if op=='StartAdlibTrackChannel':desc(m,8,40,4);m.ww('SOUND:ReservedAdlibChannelCount',0)
  add(f'backward copy {op}/{count}/{reserved}',op,setup,(8,150) if op=='StartAdlibTrackChannel' else (8,),True)
for free in [8,9,10,11,None]:
 for ages in [(0,0,0,0),(0xffffffff,7,3,3),(0x80000000,0x7fffffff,0xfffffffe,1)]:
  for valid in [False,True]:
   def setup(m,free=free,ages=ages,valid=valid):
    init(m,8,0,0,9,9,0,1)
    m.write(0x7200,0x401,API.adlx(1) if valid else b'BAD!')
    for x in range(8,12):
     desc(m,x,34,0);desc(m,x,36,9);desc(m,x,40,4 if x==free else 5)
     desc(m,x,0,ages[x-8]&65535);desc(m,x,2,ages[x-8]>>16)
   add(f'play free{free} ages{ages} valid{valid}','PlayAdlibEffect',setup,(0x401,0x7200,0x1234,2))
