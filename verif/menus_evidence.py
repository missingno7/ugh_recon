"""Generated complete-entry comparisons; full RAM including stack/ABI/ordered ports."""
import ctypes as C,random,struct,sys,hashlib,time
from pathlib import Path
from closure_support import ROOT,receipt,save
from menus_build import OUT,build,NAMES
sys.path.insert(0,str(ROOT/'tools'))
import contacts_reference,difftest,nbuild
contacts_reference.OUT=OUT/'reference'

def main():
 start=time.perf_counter();plain=contacts_reference.prepare_reference(local=True);dlls=[nbuild.load_l1(build(reference=True)),nbuild.load_l1(build())];m=difftest.Machine();rng=random.Random(13131);rows=[]
 def pair(name,regs=None,flags=None,failure_poll=0):
  initial=m.prepare('GAME:'+name,{**difftest.POISON,'DS':m.seg('DGROUP:PlayerCount'),**(regs or {})},'near',(),rng.choice([2,0x202,0x602,0xed7]) if flags is None else flags);memory=m.snapshot();device=m.device.state();results=[]
  for dll in dlls:
   C.memmove(dll.ugh_memory().contents,memory,len(memory));dll.ugh_devices_reset();dev=dll.ugh_device_state().contents;C.memmove(C.addressof(dev),device,len(device));r=difftest.Regs(**{n.lower():v for n,v in initial.items()});entries=[];entry_type=C.CFUNCTYPE(None,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs));entry_callback=entry_type(lambda seg,off,rp:entries.append((seg,off,bytes(rp.contents))));dll.ugh_set_entry_observer.argtypes=[entry_type];dll.ugh_set_entry_observer(entry_callback);callback_type=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs));calls=[0]
   def service(segment,offset,rp):
    if segment==m.seg('GAME:PollKeyboardScanChange') and offset==m.off('GAME:PollKeyboardScanChange'):
     calls[0]+=1
     if failure_poll and calls[0]==failure_poll:rp.contents.ax=0x81a5;rp.contents.flags=0x8d7;return 1
    return 0
   callback=callback_type(service) if failure_poll else callback_type();dll.ugh_set_service_observer.argtypes=[callback_type];dll.ugh_set_service_observer(callback);f=getattr(dll,'c_'+name);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r));dll.ugh_set_service_observer(callback_type());dll.ugh_set_entry_observer(entry_type());ram=bytes(dll.ugh_memory().contents);events=C.string_at(C.addressof(dev.log),dev.count*C.sizeof(difftest.IoEvent)) if hasattr(difftest,'IoEvent') else C.string_at(C.addressof(dev.log),dev.count*16);device_observation=C.string_at(C.addressof(dev),type(dev).log.offset);results.append((status,bytes(r),ram,events,dev.error,device_observation,entries))
  a,b=results
  if name=='CopyIndexedMenuString':assert len(a[6])==len(b[6])==0,(len(rows),name,'direct leaf has no child entry')
  elif name=='DrawTextLine':
   first=m.read(initial['DS'],initial['SI'],1)[0]
   if first==254:first=m.read(initial['DS'],(initial['SI']+(-1 if initial['FLAGS']&0x400 else 1))&65535,1)[0]
   if first in [0,13,253]:assert len(a[6])==len(b[6])==0,(len(rows),name,'empty line has no glyph service')
   else:assert a[6] and b[6],(len(rows),name,'nonempty glyph service stream')
  elif name=='DrawMenuHeaderSprites':assert len(a[6])==len(b[6])==3,(len(rows),name,'exact three header sprite calls')
  else:assert a[6] and b[6],(len(rows),name,'nonempty ordered entry stream')
  assert a[0]==b[0] and a[4]==b[4],(len(rows),name,'status/error',a[0],b[0],a[4],b[4]);assert a[1]==b[1],(len(rows),name,'ABI',struct.unpack('<14H',a[1]),struct.unpack('<14H',b[1]));assert a[2]==b[2],(len(rows),name,'full RAM including all stack bytes',next((i for i,(x,y) in enumerate(zip(a[2],b[2])) if x!=y),None));assert a[3]==b[3],(len(rows),name,'ordered I/O');assert a[5]==b[5],(len(rows),name,'complete device state',next(i for i,(x,y) in enumerate(zip(a[5],b[5])) if x!=y));assert a[6]==b[6],(len(rows),name,'ordered service entries',next((i for i,(x,y) in enumerate(zip(a[6],b[6])) if x!=y),None));rows.append(dict(name=name,status=a[0],error=a[4],events=len(a[3])//16,RAM_sha256=hashlib.sha256(a[2]).hexdigest(),ports_sha256=hashlib.sha256(a[3]).hexdigest(),devices_sha256=hashlib.sha256(a[5]).hexdigest(),services=len(a[6]),service_sha256=hashlib.sha256(repr(a[6]).encode()).hexdigest()))



 menu=difftest.load_suite('menu')
 for i in range(120):
  m.reset();ds=rng.choice([m.seg('DGROUP:PlayerCount'),0x7500]);reverse=i&1;source=rng.choice([0x1000,0xfffe,1,0xffff]);destination=source if i%3==0 else ((source+(1 if reverse else -1))&65535) if i%3==1 else 0x8000
  index=rng.randrange(65536);table=0x600;stream=rng.randbytes(24).replace(b'\0',b'A')+b'\0';m.write(ds,0,bytes(65537))
  for j,ch in enumerate(stream):m.write(ds,(source+(-j if reverse else j))&65535,bytes([ch]))
  m.write(ds,(table+2*index)&65535,struct.pack('<H',source));pair('CopyIndexedMenuString',{'DS':ds,'SI':table,'DI':destination,'BX':index},flags=0x602 if reverse else 0x202)
 for i in range(220):
  m.reset();ds=m.seg('DGROUP:PlayerCount');menu.graphics(m,ds,rng.choice([159,175,192,200]));reverse=bool(i&1);stream=bytearray()
  for line in range(rng.randrange(1,4)):
   if rng.randrange(2):stream.append(254)
   stream.extend(rng.choice([b for b in range(1,256) if b not in (13,253)]) for _ in range(rng.randrange(40)))
   stream.append(rng.choice([13,253]))
  stream.append(0);source=rng.choice([0x6000,0xfffe,0xffff,1])
  for j,ch in enumerate(stream):m.write(ds,(source+(-j if reverse else j))&65535,bytes([ch]))
  pair('DrawTextLine' if i%3==0 else 'DrawTextBlock',{'DS':ds,'SI':source,'CX':rng.choice([0,32,176,191,192,65535])},flags=0x602 if reverse else 0x202)
 for name in ['DrawMainMenu','DrawControlOptions','DrawMenuHeaderSprites']:
  for i in range(8):
   m.reset();menu.composition_fixture(m);m.ww('DGROUP:PlayerCount',rng.choice([1,2]));m.ww('DGROUP:SelectedDifficulty',rng.randrange(3));m.ww('DGROUP:PlayerOneControlMode',rng.choice([65535,0,1]));m.ww('DGROUP:PlayerTwoControlMode',rng.choice([65535,0,1]));pair(name,flags=0x202)
 for ch in range(256):
  m.reset();menu.composition_fixture(m);m.device.script(0xffff,[ch,13]);pair('EditLevelPassword',flags=0x202)
 for keys in [b'ABCDEFGHIJKLMNOPQRSTU\r',b'ABCDEFGHIJKLMNOPQRSTU\x08Z\r',b'\x08\x08\r',b'a1z9!\r']:
  m.reset();menu.composition_fixture(m);m.device.script(0xffff,list(keys));pair('EditLevelPassword',flags=0x202)
 for presence in range(4):
  for mode in [65535,0,1]:
   for scan in [59,60]:
    m.reset();menu.composition_fixture(m);m.ww('DGROUP:PlayerOneControlMode',mode);m.ww('DGROUP:PlayerTwoControlMode',mode);m.ww('DGROUP:JoystickPresentFlags',65535 if presence&1 else 0);m.ww('DGROUP:SecondJoystickPresent',65535 if presence&2 else 0);m.wb('GAME:LatestInterruptScanCode',0);m.wb('DGROUP:CurrentKeyboardScanCode',0)
    m.write(0,0x24,struct.pack('<HH',m.off('GAME:HandleKeyboardScanInterrupt'),m.seg('GAME:HandleKeyboardScanInterrupt')));m.device.script(0x60,[scan,1]);m.device.schedule(m.seg('GAME:PollKeyboardScanChange'),m.off('GAME:PollKeyboardScanChange'),irq=1);m.device.schedule(m.seg('GAME:PollKeyboardScanChange'),m.off('GAME:PollKeyboardScanChange'),irq=1);pair('SelectPlayerControls',flags=0x202)
 for players,count in [(1,69),(2,81)]:
  for level in range(count):
   m.reset();menu.composition_fixture(m);m.ww('DGROUP:PlayerCount',players);m.ww('DGROUP:PlayerArrayBytes',2*players);m.ww('DGROUP:CurrentLevelIndex',level);pair('ShowLevelIntroduction',flags=0x202)
 for name in ['PrepareAttractMap0','PrepareAttractMap90']:
  for i in range(2):m.reset();menu.composition_fixture(m);pair(name,flags=0x202 if i==0 else 0x602)
 for pages in [None,b'\xfeONE\rTWO\0\xff',b'\xfd\0\xfeTHREE\0\xff']:
  m.reset();menu.composition_fixture(m);m.device.script_count=0;m.device.script(0x3da,[0,8],cycles=0xffffffff);m.device.script(0x201,[255],cycles=0xffffffff)
  if pages is not None:m.write(m.seg('DGROUP:PlayerCount'),m.off('DGROUP:Text_091F'),pages)
  pair('ShowCreditsPages',flags=0x202)
 assert sum(row['services'] for row in rows)>0,'entry trace instrumentation missing'
 save(OUT/'menus-cases.json',receipt([sys.executable,'verif/menus_evidence.py'],[Path(__file__),ROOT/'verif/menus_build.py',ROOT/'native/menus.c',ROOT/'native/menus.h',ROOT/'native/high_scores.c',ROOT/'native/high_scores.h',ROOT/'native/front_end.h',ROOT/'native/bridge/menus_bridge.c',ROOT/'native/bridge/high_scores_bridge.c',ROOT/'native/bridge/front_end_support.h',ROOT/'c/menu.c',ROOT/'c/menu_helpers.c',ROOT/'c/scene.c',plain],result='PASS',cases=rows,seconds=time.perf_counter()-start));print('PASS',len(rows),'menus full RAM/device/service pairs',flush=True)
if __name__=='__main__':main()
