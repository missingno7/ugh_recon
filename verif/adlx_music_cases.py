"""Music lifecycle/fade edges against rebuilt L0 with real timer/voice peers."""
from difftest import Case,load_suite
from adlx_loader_cases import data,setup_data
BASE=load_suite('adlib').base;API=load_suite('sound_api')
CASES=[]
def base(m):BASE(m);API.base(m,1)
def add(title,name,setup,args=(),sound=False,flags=0x602):
    CASES.append(Case(title,('SOUND:' if sound else 'C:')+name,setup=setup,args=args,kind='far',flags=flags,out_regs=('AX','BX','CX','DX','SI','DI','BP','IF','DF') if sound else ('AX','SI','DI','BP','IF','DF')))
for duration in [0,1,2,255,0x7fff,0x8000,0xffff]:
 for volume in [0,73,255,256,0xffff]:
  for valid in [False,True]:
   def start(m,valid=valid):setup_data(m,data(voices=3) if valid else b'BAD!',slot=12)
   add(f'start duration{duration} volume{volume} valid{valid}','StartMusicTrack',start,(0x401,0x6000,duration,volume))
for count in [0,1,9,10,255,256,257,265,511,512]:
 for reserved in [0,1,9,0x109]:
  for playing in [0,1,2]:
   def volume(m,count=count,reserved=reserved,playing=playing):
    base(m)
    for n,v in dict(MusicVoiceCount=count,ReservedAdlibChannelCount=reserved,MainAdlxPlaying=playing,CurrentAdlxSlot=13).items():m.ww('SOUND:'+n,v)
   add(f'volume count{count} reserved{reserved} playing{playing}','SetMusicTrackVolume',volume,(0xab81,))
for step,duration,start,target in [(0,1,0,255),(0,2,255,0),(1,2,0,255),(2,2,73,17),(0xffff,0xffff,0,255),(0,0xffff,0,1),(0x7fff,0x8000,0x8000,0xffff)]:
 def fade(m,step=step,duration=duration,start=start,target=target):
    base(m)
    for n,v in dict(MainAdlxPlaying=1,MusicVoiceCount=9,MusicFadeScheduled=1,MusicFadeStep=step,MusicFadeDuration=duration,MusicFadeStartVolume=start,MusicFadeTargetVolume=target).items():m.ww('SOUND:'+n,v)
 add(f'fade {step}/{duration}/{start}/{target}','AdvanceMusicFade',fade,sound=True)
for playing in [0,1,2]:
 for scheduled in [0,1,2,3]:
  def stop(m,playing=playing,scheduled=scheduled):
   base(m);m.ww('SOUND:MainAdlxPlaying',playing);m.ww('SOUND:MusicFadeScheduled',scheduled)
  add(f'instant stop playing{playing} scheduled{scheduled}','StopMusicTrack',stop,(0,))
