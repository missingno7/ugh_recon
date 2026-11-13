"""Malformed/truncated containers and reset/wrapper offset behavior vs L0."""
from difftest import Case,load_suite
import struct
API=load_suite('sound_api');BASE=load_suite('adlib').base
CASES=[]
def data(ahsize=10,imsize=0,root=0x1234,voices=3,rate=0xbeef):
    raw=bytearray(b'ADLX'+struct.pack('>I',root)+b'AHDR'+struct.pack('>I',ahsize)+bytes(ahsize)+b'IMAP'+struct.pack('>I',imsize)+bytes(imsize)+b'TRCK'+b'BAD!')
    raw[18]=voices;raw[22:24]=struct.pack('<H',rate);return bytes(raw)
def setup_data(m,raw,offset=0x401,reserved=0,slot=8):
    BASE(m);API.base(m,1)
    m.ww('SOUND:ReservedAdlibChannelCount',reserved)
    # A truncated file has ordinary neighboring RAM, not a native file-bound
    # error. The byte immediately past FFFF is independent of wrapped byte0.
    m.write(0x6000,0,bytes([0xa5])*65537)
    for i,value in enumerate(raw):m.write(0x6000,(offset+i)&65535,bytes([value]))
    m.ww('SOUND:AudioChannelStates',0x8acf,slot*42+4)
def add(title,routine,setup,args):
    CASES.append(Case(title,'C:'+routine,setup=setup,args=args,kind='far',out_regs=('AX','SI','DI','BP','IF','DF'),flags=0x602))
valid=data()
for length in range(len(valid)+1):
 for slot in [8,12]:
    add(f'truncated prefix{length} slot{slot}','LoadAdlibTrackData',lambda m,length=length,slot=slot:setup_data(m,valid[:length],slot=slot),(slot,0x401,0x6000,0))
for position in [0,1,2,3,8,9,10,11,26,27,28,29,34,35,36,37]:
 for offset in [0,0xfff9]:
    raw=bytearray(valid);raw[position]^=1
    add(f'tag mutation{position} offset{offset:x}','LoadAdlibTrackData',lambda m,raw=bytes(raw),offset=offset:setup_data(m,raw,offset),(8,offset,0x6000,1))
for reserved in [0,8,9,10,255,0x8000,0xffff]:
 for voices in [0,1,9,10,255]:
  for slot in [8,12]:
   raw=data(voices=voices)
   add(f'capacity slot{slot} reserved{reserved} voices{voices}','LoadAdlibTrackData',lambda m,raw=raw,reserved=reserved,slot=slot:setup_data(m,raw,reserved=reserved,slot=slot),(slot,0x401,0x6000,0xffff))
for ahsize,imsize,root in [(0,0,0),(1,0,33),(10,13,0x12345678),(20,2,0xffff0000),(0xffff,0,0x80000001)]:
 if ahsize==0xffff:continue # wrap size is tested by staged generated evidence
 for offset in [1,0xfff1]:
    raw=data(ahsize,imsize,root)
    add(f'odd chunks{ahsize}/{imsize}/{root:x} offset{offset:x}','LoadAdlibTrackData',lambda m,raw=raw,offset=offset:setup_data(m,raw,offset,slot=12),(12,offset,0x6000,0))
for slot in [8,12,13,0x8000,0xffff]:
 add(f'wrapper parser negative slot{slot}','LoadAdlibChannel',lambda m:setup_data(m,b'BAD!'),(slot,0x401,0x6000,0x5678,3))
for offset in [0x500,0x254]:
 def aliases(m,offset=offset):
    BASE(m);API.base(m,1);m.write(m.seg('SOUND:AudioChannelStates'),offset,valid)
 add(f'parser source aliases SOUND at{offset:x}','LoadAdlibTrackData',aliases,
     lambda m,offset=offset:(12,offset,m.seg('SOUND:AudioChannelStates'),1))
for slot in [0,7,8,12,13,0x7fff,0x8000,0xfffe,0xffff]:
 for control in [0,4,0xffff]:
    def reset(m,slot=slot,control=control):
        BASE(m);p=(m.off('SOUND:AudioChannelStates')+42*slot)&65535;s=m.seg('SOUND:AudioChannelStates')
        for field,value in [(6,0xfffe),(8,0xabcd),(16,0x1234),(18,0x5678),(40,control)]:m.write(s,(p+field)&65535,struct.pack('<H',value))
    add(f'reset signed slot{slot:04x} control{control:04x}','ResetAdlibTrackChannelCursor',reset,(slot,))
