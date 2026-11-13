"""Previously missing effect END, channel-nine owner and timer-fault edges."""
import sys,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from difftest import Case,load_suite
BASE=load_suite('adlib').base
CASES=[]
REGS=('AX','BX','CX','DX','SI','DI','BP','IF','DF')

def add(title,routine,setup,regs):
    def initialized(m):BASE(m);setup(m)
    CASES.append(Case(title,'SOUND:'+routine,setup=initialized,regs=regs,kind='far',flags=0x602,out_regs=REGS))

for slot in range(8,12):
 for voices in [1,2,9]:
  for playing in [0,1]:
   for repeats in [0,1,0x8000,0xffff]:
    def setup(m,slot=slot,voices=voices,playing=playing,repeats=repeats):
        record=m.off('SOUND:AudioChannelStates')+42*slot;s=m.seg('SOUND:AudioChannelStates')
        for name,value in dict(CurrentAdlxRecordOffset=record,CurrentAdlxSlot=slot,SoundDeviceBits=1,
                MusicVoiceCount=9,MainAdlxPlaying=playing,ReservedAdlibChannelCount=voices,AdlxPlaybackGuard=0xa502).items():m.ww('SOUND:'+name,value)
        for field,value in [(4,repeats),(6,0x1234),(8,0x6000),(16,0x110),(18,0x6000),(34,voices),(36,9-voices),(40,5)]:m.write(s,record+field,struct.pack('<H',value))
    add(f'END C-stop slot{slot} voices{voices} main{playing} repeats{repeats:04x}','HandleEffectAdlxControl',setup,dict(AX=0xa577,ES=0x6000,DI=0x101))

for slot in [8,9,10,11]:
 def setup(m,slot=slot):
    record=m.off('SOUND:AudioChannelStates')+42*slot;s=m.seg('SOUND:AudioChannelStates');other=8 if slot!=8 else 9
    for name,value in dict(CurrentAdlxRecordOffset=record,CurrentAdlxSlot=slot,SoundDeviceBits=1,MusicVoiceCount=9,MainAdlxPlaying=1,ReservedAdlibChannelCount=2,AdlxPlaybackGuard=3).items():m.ww('SOUND:'+name,value)
    for field,value in [(4,1),(6,0x111),(8,0x6000),(34,1),(36,8),(40,5)]:m.write(s,record+field,struct.pack('<H',value))
    for field,value in [(34,1),(36,7),(40,5)]:m.write(s,m.off('SOUND:AudioChannelStates')+42*other+field,struct.pack('<H',value))
    m.ww('SOUND:AdlibChannelOwnerSlot',other,7*20)
 add(f'END compacts peer while releasing slot{slot}','HandleEffectAdlxControl',setup,dict(AX=0x77,ES=0x6000,DI=0x100))

for nibble in [0,1,9,15]:
 for owner in [8,12,13,0xffff]:
  def setup(m,nibble=nibble,owner=owner):
    record=m.off('SOUND:AudioChannelStates')+8*42;s=m.seg('SOUND:AudioChannelStates')
    m.ww('SOUND:CurrentAdlxSlot',owner);m.write(s,record+36,struct.pack('<H',0xab00|((9-nibble)&255)))
    m.write(0x6000,0x100,bytes(11)+b'\x81')
  add(f'instrument physical9 aliases saved0 owner{owner:04x} nibble{nibble}','HandleEffectAdlxInstrument',setup,dict(AX=0xa540|nibble,ES=0x6000,DI=0x100))

for owner in [0,12,0xffff]:
 def setup(m,owner=owner):
    m.ww('SOUND:CurrentAdlxSlot',owner);m.write(0x6000,0x100,b'\x40\x81')
 add(f'END stop rejects raw identity{owner:04x}','HandleEffectAdlxControl',setup,dict(AX=0x77,ES=0x6000,DI=0x100))
