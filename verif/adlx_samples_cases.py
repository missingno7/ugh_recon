"""Generated sample containers and native alias/mixer L0 cases."""
import struct
from difftest import Case,load_suite
API=load_suite('sound_api');BASE=API.base;CASES=[]
def sample(body=7,compression=0,prefix=b'8SVX',root=128):
    data=bytearray(b'FORM'+struct.pack('>I',root)+prefix+b'VHDR'+struct.pack('>I',20)+bytes(20)+b'BODY'+struct.pack('>I',body)+bytes(range(64)))
    at=data.index(b'VHDR')+4;data[at+16:at+18]=b'\x1f\x40';data[at+19]=compression;return bytes(data)
for slot in [0,7,8,65535]:
 for length in [0,1,7,64000,64001,65536,0xffffffff]:
  for compression in [0,2,255]:
   def setup(m,length=length,compression=compression):
    BASE(m,2);m.ww('SOUND:AudioChannelStates',0xabcd,4);m.write(0x7100,0x100,sample(length,compression))
   CASES.append(Case(f'sample import {slot}/{length}/{compression}','C:LoadIffSample',setup=setup,args=(slot,0x100,0x7100,0xffff,0,0xffff),kind='far',flags=0x602,out_regs=('AX','SI','DI','BP','IF','DF')))
for skip in range(1,5):
 raw=sample(prefix=b'8SVX'+b'V'*skip+b'VHDRnope')
 def setup(m,raw=raw):BASE(m,2);m.write(0x7100,0x100,raw)
 CASES.append(Case(f'short circuit overlapping tags {skip}','C:LoadIffSample',setup=setup,args=(0,0x100,0x7100,255,1,256),kind='far',out_regs=('AX','SI','DI','BP','IF','DF')))
