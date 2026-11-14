"""Generated complete-entry comparisons; full RAM including stack/ABI/ordered ports."""
import ctypes as C,random,struct,sys,hashlib,time
from pathlib import Path
from closure_support import ROOT,receipt,save
from pictures_build import OUT,build,NAMES
sys.path.insert(0,str(ROOT/'tools'))
import contacts_reference,difftest,nbuild
contacts_reference.OUT=OUT/'reference'

def main():
 start=time.perf_counter();plain=contacts_reference.prepare_reference(local=True);dlls=[nbuild.load_l1(build(reference=True)),nbuild.load_l1(build(ice=True))];m=difftest.Machine();rng=random.Random(13013);rows=[]
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
  a,b=results;assert a[0]==b[0] and a[4]==b[4],(len(rows),name,'status/error',a[0],b[0],a[4],b[4]);assert a[1]==b[1],(len(rows),name,'ABI',struct.unpack('<14H',a[1]),struct.unpack('<14H',b[1]));assert a[2]==b[2],(len(rows),name,'full RAM including all stack bytes',next((i for i,(x,y) in enumerate(zip(a[2],b[2])) if x!=y),None));assert a[3]==b[3],(len(rows),name,'ordered I/O');assert a[5]==b[5],(len(rows),name,'complete device state',next(i for i,(x,y) in enumerate(zip(a[5],b[5])) if x!=y));assert a[6]==b[6],(len(rows),name,'ordered service entries',next((i for i,(x,y) in enumerate(zip(a[6],b[6])) if x!=y),None));rows.append(dict(name=name,status=a[0],error=a[4],events=len(a[3])//16,RAM_sha256=hashlib.sha256(a[2]).hexdigest(),ports_sha256=hashlib.sha256(a[3]).hexdigest(),devices_sha256=hashlib.sha256(a[5]).hexdigest(),services=len(a[6]),service_sha256=hashlib.sha256(repr(a[6]).encode()).hexdigest(),entries={n:sum(seg==m.seg('GAME:'+n) and off==m.off('GAME:'+n) for seg,off,_ in a[6]) for n in [*NAMES,'RestoreKeyboardInterrupt']}))


 corpus=[];corpus_folder=OUT/'corpus';corpus_folder.mkdir(exist_ok=True)
 # Shipped picture corpus goes through the maintained native ICE bridge too.
 for frame in [0x2bf6,0x2d9a,0x2f9e,0x2fb7]:
  m.reset();resource=m.seg(f'B{frame:04X}:ext_{frame:04X}');scratch=m.seg('ZERO:IceDecodeWorkspace');m.write(scratch,0,bytes((j*13+7)&255 for j in range(64768)));pair('UnpackPictureAndCopyPalette',{'SI':resource},flags=0xed7)
  from dataprobe import IceDecoder
  stream=m.read(resource,0,65536);packed=int.from_bytes(stream[4:8],'big');unpacked=int.from_bytes(stream[8:12],'big');assert unpacked==64768
  decoded=IceDecoder(stream,m.raw_image,bytes(65536)).decode(packed-1,unpacked)
  actual=C.string_at(C.addressof(dlls[1].ugh_memory().contents)+16*scratch,64768);reference=C.string_at(C.addressof(dlls[0].ugh_memory().contents)+16*scratch,64768)
  assert actual==reference==decoded
  palette=actual[64000:];assert len(palette)==768 and max(palette)<=63
  (corpus_folder/f'{frame:04x}.decoded.bin').write_bytes(actual)
  corpus.append(dict(frame=f'{frame:04X}',header=stream[:12].hex(),packed=packed,unpacked=unpacked,pixels=64000,palette=768,palette_max=max(palette),decoded_sha256=hashlib.sha256(actual).hexdigest(),palette_sha256=hashlib.sha256(palette).hexdigest(),native_equals_L1_equals_dataprobe=True))
 save(OUT/'corpus.json',receipt([sys.executable,'verif/pictures_evidence.py'],[Path(__file__),ROOT/'native/ice.c',ROOT/'native/bridge/ice_bridge.c',ROOT/'native/pictures.c',ROOT/'native/bridge/pictures_bridge.c',ROOT/'tools/dataprobe.py',plain],result='PASS',pictures=corpus))
 # Invalid/short logical input has ordinary RAM after it; no file length exists.
 for i in range(160):
  m.reset();resource=0x7500;scratch=m.seg('ZERO:IceDecodeWorkspace');m.write(scratch,0,rng.randbytes(64768));raw=rng.choice([b'',b'I',b'IC',b'ICx',b'bad!',b'Ice!'])+rng.randbytes(rng.randrange(30));m.write(resource,0,bytes(65536));m.write(resource,0,raw)
  if raw[:4]==b'ICE!':continue
  destination=rng.choice([0,1,0xfa00,0xfa01,0xfa02,0xfffe,0xffff,0x4681]);destseg=rng.choice([scratch,0x6800]);m.ww('GAME:PicturePaletteDestination',destination);m.ww('GAME:PicturePaletteDestination',destseg,2);pair('UnpackPictureAndCopyPalette',{'SI':resource,'DS':rng.choice([m.seg('DGROUP:PlayerCount'),0x7400]),'CX':rng.randrange(65536)})
 # Small/zero/overflowing low-word headers, high size words, literal and match
 # boundaries. Full64K buffers retain spill beyond the physical FD00 workspace.
 from dataprobe import ice_pack235
 fixtures=[ice_pack235(bytes((j*7+3)&255 for j in range(n))) for n in [1,2,3,4,31,255,768,2048,64767,64768,64769,65535,65536]]
 for raw in fixtures[:3]:
  changed=bytearray(raw);changed[4:6]=b'\x12\x34';changed[8:10]=b'\x56\x78';fixtures.append(bytes(changed))
 fixtures += [b'ICE!'+(13).to_bytes(4,'big')+n.to_bytes(4,'big')+bytes([ch]) for n in [0,1,2,3,4] for ch in [0,1,2,64,128,129,192,255]]
 for raw in fixtures:
  m.reset();resource=0x7500;scratch=m.seg('ZERO:IceDecodeWorkspace');m.write(resource,0,bytes(65536));m.write(resource,0,raw);m.write(scratch,0,bytes(64768));pair('UnpackPictureAndCopyPalette',{'SI':resource},flags=0x602)
 menu=difftest.load_suite('menu')
 for frame in [0x2bf6,0x2d9a,0x2f9e,0x2fb7]:
  for timeout in [0,1,2,17]:
   m.reset();menu.composition_fixture(m);pair('ShowPackedPictureAndWait',{'SI':m.seg(f'B{frame:04X}:ext_{frame:04X}'),'CX':timeout},flags=0x202)
 # Timed real IRQs at each displayed picture, including release-bit variants.
 for ordinal in range(4):
  for scan in [1,0x81,16,0x90,0x39]:
   m.reset();menu.composition_fixture(m);m.device.script_count=0;m.device.script(0x3da,[0,8],cycles=0xffffffff);m.device.script(0x201,[255],cycles=0xffffffff)
   m.write(0,0x24,struct.pack('<HH',m.off('GAME:HandleKeyboardScanInterrupt'),m.seg('GAME:HandleKeyboardScanInterrupt')));m.device.script(0x60,[scan]);m.device.schedule(m.seg('GAME:loc_449B'),m.off('GAME:loc_449B'),skip=sum([280,280,140][:ordinal]),irq=1);pair('ShowStartupPictures',flags=0x202)
   observed=rows[-1];observed.update(requested_picture=ordinal,scan=scan);assert observed['entries']['ShowPackedPictureAndWait']==(ordinal+1 if (scan&127) in [1,16] else 4),observed;assert observed['entries']['RestoreKeyboardInterrupt']==int((scan&127)==16),observed
 save(OUT/'pictures-cases.json',receipt([sys.executable,'verif/pictures_evidence.py'],[Path(__file__),ROOT/'verif/pictures_build.py',ROOT/'native/pictures.c',ROOT/'native/pictures.h',ROOT/'native/bridge/pictures_bridge.c',ROOT/'native/ice.c',ROOT/'native/bridge/ice_bridge.c',ROOT/'c/video.c',ROOT/'c/scene.c',ROOT/'c/ice.c',plain],result='PASS',cases=rows,seconds=time.perf_counter()-start));print('PASS',len(rows),'picture full RAM/device/service pairs',flush=True)
if __name__=='__main__':main()
