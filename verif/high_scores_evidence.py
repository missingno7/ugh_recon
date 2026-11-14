"""Generated complete-entry comparisons; full RAM including stack/ABI/ordered ports."""
import ctypes as C,random,struct,sys,hashlib,time
from pathlib import Path
from closure_support import ROOT,receipt,save
from high_scores_build import OUT,build,NAMES
sys.path.insert(0,str(ROOT/'tools'))
import contacts_reference,difftest,nbuild
contacts_reference.OUT=OUT/'reference'

def main():
 start=time.perf_counter();plain=contacts_reference.prepare_reference(local=True);dlls=[nbuild.load_l1(build(reference=True)),nbuild.load_l1(build())];m=difftest.Machine();rng=random.Random(13013);rows=[]
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
  a,b=results;assert a[0]==b[0] and a[4]==b[4],(len(rows),name,'status/error',a[0],b[0],a[4],b[4]);assert a[1]==b[1],(len(rows),name,'ABI',struct.unpack('<14H',a[1]),struct.unpack('<14H',b[1]));assert a[2]==b[2],(len(rows),name,'full RAM including all stack bytes',next((i for i,(x,y) in enumerate(zip(a[2],b[2])) if x!=y),None));assert a[3]==b[3],(len(rows),name,'ordered I/O');assert a[5]==b[5],(len(rows),name,'complete device state',next(i for i,(x,y) in enumerate(zip(a[5],b[5])) if x!=y));assert a[6]==b[6],(len(rows),name,'ordered service entries',next((i for i,(x,y) in enumerate(zip(a[6],b[6])) if x!=y),None));rows.append(dict(name=name,status=a[0],error=a[4],events=len(a[3])//16,RAM_sha256=hashlib.sha256(a[2]).hexdigest(),ports_sha256=hashlib.sha256(a[3]).hexdigest(),devices_sha256=hashlib.sha256(a[5]).hexdigest(),services=len(a[6]),service_sha256=hashlib.sha256(repr(a[6]).encode()).hexdigest()))


 for i in range(400):
  m.reset();ds=rng.choice([m.seg('DGROUP:PlayerCount'),0x7500]);m.write(ds,m.off('DGROUP:HighScoreRows'),rng.randbytes(107));m.write(ds,m.off('DGROUP:Data_0CF1'),b'UGH!.HI\0');m.ww('DGROUP:HighScoreFileHandle',0xbeef)
  if ds!=m.seg('DGROUP:PlayerCount'):m.write(ds,m.off('DGROUP:HighScoreFileHandle'),b'\xef\xbe')
  if i%5:m.device.file('UGH!.HI',rng.randbytes(rng.choice([0,1,53,106,107,108,8192])))
  m.device.io_limit=rng.choice([0,1,53,106,107,108]);m.device.dos_error=5 if i%7==0 else 0;m.device.dos_error_skip=i%3
  pair('LoadHighScores' if i&1 else 'SaveHighScores',{'DS':ds})
 for i in range(300):
  m.reset();ds=rng.choice([m.seg('DGROUP:PlayerCount'),0x7500]);m.write(ds,0,rng.randbytes(65537));pair(rng.choice(['GetHighScoreRow','GetHighScoreDigits','TestHighScoreQualification','CopyHighScoreRowDown','ComplementHighScoreTable']),{'DS':ds,'CX':rng.randrange(65536)})
 menu=difftest.load_suite('menu')
 keys=[b'\r',b'abc Z9!\x08\r',b'abcdefghijkl\r',b'abcdefghijklM\x08Z\r',b'\x08\x08\r',bytes([0,255,13])]
 for rank in range(6):
  for key in keys:
   m.reset();menu.composition_fixture(m);m.device.script(0xffff,list(key));m.ww('DGROUP:ScoreLowWord',12345);m.ww('DGROUP:ScoreHighWord',0)
   for row in range(5):m.write(m.seg('DGROUP:PlayerCount'),m.off('DGROUP:HighScoreRows')+21*row+14,b' 99999' if row<rank else b'     1')
   pair('InsertHighScoreAndClearScore',flags=0x202)
 for score in [0,1,9,10,99,100,99999,100000,999999,1000000,0x7fffffff,0x80000000,0xffffffff]:
  m.reset();menu.composition_fixture(m);m.device.script(0xffff,[13]);m.ww('DGROUP:ScoreLowWord',score&65535);m.ww('DGROUP:ScoreHighWord',score>>16);pair('InsertHighScoreAndClearScore',flags=0x202)
 for name in ['ShowHighScores','DrawHighScoreNameEntry']:
  for i in range(4):m.reset();menu.composition_fixture(m);pair(name,flags=0x202)
 save(OUT/'high-cases.json',receipt([sys.executable,'verif/high_scores_evidence.py'],[Path(__file__),ROOT/'verif/high_scores_build.py',ROOT/'native/high_scores.c',ROOT/'native/high_scores.h',ROOT/'native/front_end.h',ROOT/'native/bridge/high_scores_bridge.c',ROOT/'native/bridge/front_end_support.h',ROOT/'c/menu.c',ROOT/'c/menu_helpers.c',ROOT/'c/game_services.c',plain],result='PASS',cases=rows,seconds=time.perf_counter()-start));print('PASS',len(rows),'high-score full RAM/device/service pairs',flush=True)
if __name__=='__main__':main()
