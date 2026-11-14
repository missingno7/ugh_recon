"""Generated complete-entry comparisons; full RAM including stack/ABI/ordered ports."""
import ctypes as C,random,struct,sys,hashlib,time
from pathlib import Path
from closure_support import ROOT,receipt,save
from video_dos_build import OUT,build,NAMES
sys.path.insert(0,str(ROOT/'tools'))
import contacts_reference,difftest,nbuild
contacts_reference.OUT=OUT/'reference'

def main():
 start=time.perf_counter();plain=contacts_reference.prepare_reference(local=True);dlls=[nbuild.load_l1(build(reference=True)),nbuild.load_l1(build())];m=difftest.Machine();rng=random.Random(12012);rows=[]
 def pair(name,regs=None,flags=None,failure_poll=0):
  initial=m.prepare('GAME:'+name,{**difftest.POISON,'DS':m.seg('DGROUP:PlayerCount'),**(regs or {})},'iret' if name=='FailDosCriticalError' else 'near',(),rng.choice([2,0x202,0x602,0xed7]) if flags is None else flags);memory=m.snapshot();device=m.device.state();results=[]
  for dll in dlls:
   C.memmove(dll.ugh_memory().contents,memory,len(memory));dll.ugh_devices_reset();dev=dll.ugh_device_state().contents;C.memmove(C.addressof(dev),device,len(device));r=difftest.Regs(**{n.lower():v for n,v in initial.items()});callback_type=C.CFUNCTYPE(C.c_int,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs));calls=[0];service_log=[];entries=[];entry_type=C.CFUNCTYPE(None,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs));entry_callback=entry_type(lambda seg,off,rp:entries.append((seg,off,bytes(rp.contents))));dll.ugh_set_entry_observer.argtypes=[entry_type];dll.ugh_set_entry_observer(entry_callback if failure_poll else entry_type())
   def service(segment,offset,rp):
    if segment==m.seg('GAME:loc_449B') and offset==m.off('GAME:loc_449B')+0:
     calls[0]+=1;service_log.append((segment,offset,bytes(rp.contents)))
     if failure_poll and calls[0]==failure_poll:rp.contents.ax=0x81a5;rp.contents.flags=0x8d7;return 1
    return 0
   callback=callback_type(service) if failure_poll else callback_type();dll.ugh_set_service_observer.argtypes=[callback_type];dll.ugh_set_service_observer(callback);f=getattr(dll,'c_'+name);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r));dll.ugh_set_service_observer(callback_type());dll.ugh_set_entry_observer(entry_type());ram=bytes(dll.ugh_memory().contents);events=C.string_at(C.addressof(dev.log),dev.count*C.sizeof(difftest.IoEvent)) if hasattr(difftest,'IoEvent') else C.string_at(C.addressof(dev.log),dev.count*16);device_observation=C.string_at(C.addressof(dev),type(dev).log.offset);results.append((status,bytes(r),ram,events,dev.error,device_observation,calls[0],service_log,entries))
  a,b=results
  if failure_poll:
   assert a[0]==b[0]==1 and a[6]==b[6]==failure_poll,(len(rows),name,'requested failure must be delivered',failure_poll,a[0],b[0],a[6],b[6])
   assert a[7]==b[7] and a[7],(len(rows),name,'nonempty ordered wait service prefixes')
   assert len(a[8])==len(b[8])==1+4*(failure_poll-1),(len(rows),name,'known dispatched prefix count',len(a[8]),len(b[8]))
   assert a[8]==b[8],(len(rows),name,'ordered entry-service ABI prefix')
  assert a[0]==b[0] and a[4]==b[4],(len(rows),name,'status/error',a[0],b[0],a[4],b[4]);assert a[1]==b[1],(len(rows),name,'ABI',struct.unpack('<14H',a[1]),struct.unpack('<14H',b[1]));assert a[2]==b[2],(len(rows),name,'full RAM including all stack bytes',next((i for i,(x,y) in enumerate(zip(a[2],b[2])) if x!=y),None));assert a[3]==b[3],(len(rows),name,'ordered I/O');assert a[5]==b[5],(len(rows),name,'complete device state',next(i for i,(x,y) in enumerate(zip(a[5],b[5])) if x!=y));rows.append(dict(name=name,status=a[0],error=a[4],events=len(a[3])//16,RAM_sha256=hashlib.sha256(a[2]).hexdigest(),ports_sha256=hashlib.sha256(a[3]).hexdigest(),requested_failure=failure_poll,entry_services=len(a[8]),entry_sha256=hashlib.sha256(repr(a[8]).encode()).hexdigest(),service_points=a[6],service_sha256=hashlib.sha256(repr(a[7]).encode()).hexdigest(),devices_sha256=hashlib.sha256(a[5]).hexdigest()))

 def retrace(values=None):m.device.script(0x3da,values or [0,8],cycles=0xffffffff)
 for i in range(100):
  m.reset();bank=rng.choice([0x7500,0x7700]);source=rng.choice([0,1,0x180,0x200,0xfffe,0xffff,rng.randrange(65536)]);dest=rng.choice([source,(source+2)&65535,(source-2)&65535,(source-384)&65535,0xffff,rng.randrange(65536)])
  m.write(bank,0,rng.randbytes(65537));ds=rng.choice([m.seg('DGROUP:PlayerCount'),0x7300]);m.write(ds,m.off('DGROUP:PaletteSourcePointer'),struct.pack('<HH',source,bank));m.write(ds,m.off('DGROUP:BasePalettePointer'),struct.pack('<HH',dest,bank if i%2 else 0x7900));pair('DuplicateSourcePaletteHalves',{'DS':ds})
 for i in range(150):
  m.reset();retrace();m.write(m.seg('GAME:BaseRgbPalette'),m.off('GAME:BaseRgbPalette'),rng.randbytes(1536));ds=rng.choice([m.seg('DGROUP:PlayerCount'),0x7300]);m.write(ds,m.off('DGROUP:FadedPalettePointer'),struct.pack('<HH',rng.choice([0,0xffff,m.off('GAME:FadedRgbPalette')]),rng.choice([0x7500,m.seg('GAME:BaseRgbPalette')])));pair('ScaleAndUploadFadedPalette',{'DS':ds,'CX':rng.choice([0,1,4,252,255,256,257,32767,32768,65535,rng.randrange(65536)])})
 for i in range(60):
  m.reset();retrace();ds=rng.choice([m.seg('DGROUP:PlayerCount'),0x7300]);m.write(0x7500,0,rng.randbytes(65537));m.write(ds,m.off('DGROUP:BasePalettePointer'),struct.pack('<HH',rng.choice([0,1,0xffff,rng.randrange(65536)]),0x7500));pair('UploadBasePalette',{'DS':ds})
 for name in ['FadePaletteIn','FadePaletteOut','BlackenVgaPalette']:
  for i in range(8):
   m.reset();retrace();m.write(m.seg('GAME:BaseRgbPalette'),m.off('GAME:BaseRgbPalette'),rng.randbytes(768));pair(name,{'CX':rng.randrange(65536)})
 for i in range(80):
  m.reset();m.device.planes[:]=rng.randbytes(4*65536)
  for j in range(9):m.device.gc[j]=rng.randrange(256)
  pair('ClearAllVgaPlanes')
 for i in range(80):
  m.reset();count=rng.choice([0,1,2,3,16,127,256,16000,0x4800]);m.ww('GAME:VgaPlaneCopyByteCount',count);m.ww('GAME:DrawPagePointer',rng.choice([0,1,0xffff,0xfffe,rng.randrange(65536)]));m.ww('GAME:DrawPagePointer',rng.choice([0xa000,0x7500]),2);sourcebank=rng.choice([0xa000,0x7500]);m.write(0x7500,0,rng.randbytes(65537));m.ww('DGROUP:DecodedImagePointer',rng.randrange(65536));m.ww('DGROUP:DecodedImagePointer',sourcebank,2);m.device.planes[:]=rng.randbytes(4*65536);pair('UploadChunkyImageToVgaPlanes')
 for i in range(80):
  m.reset();retrace([8,255,0]);m.ww('GAME:DrawPagePointer',rng.randrange(65536));m.ww('GAME:DisplayedVgaPagePointer',rng.randrange(65536));m.ww('GAME:DrawPagePointer',rng.randrange(65536),2);m.ww('GAME:DisplayedVgaPagePointer',rng.randrange(65536),2);pair('SwapAndDisplayVgaPage')
 for name in ['ConfigureVgaGameplayPages','ConfigureVgaPicturePages']:
  for i in range(20):
   m.reset();retrace();m.device.planes[:]=rng.randbytes(4*65536)
   for j in range(5):m.device.seq[j]=rng.randrange(256)
   for j in range(25):m.device.crtc[j]=rng.randrange(256)
   for key in ['DrawPagePointer','DisplayedVgaPagePointer','BackgroundPagePointer','FixedVgaPagePointer']:m.ww('GAME:'+key,rng.randrange(65536),2)
   pair(name)
 for i in range(100):m.reset();pair('EnableAllVgaWritePlanes')
 for name,target in [('WaitVerticalRetraceActive',8),('WaitVerticalRetraceInactive',0)]:
  for raw in range(256):
   m.reset();retrace([raw,target]);pair(name)
  m.reset();retrace([target^8]);pair(name)
 for name in ['WaitNextVerticalRetrace','WaitThroughVerticalRetrace']:
  for i in range(40):m.reset();retrace([rng.randrange(256) for _ in range(8)]+[0,8,0]);pair(name)
 for count in [0,1,2,3,255,256,32768,65535]:
  m.reset();retrace();pair('WaitRetraceCount',{'CX':count})
 video=difftest.load_suite('video')
 for count in [0,1,2,3,255,32768,65535]:
  for buttons in [0,16,128]:
   m.reset();retrace();video.input_setup(m,buttons);m.device.script_count-=1;m.device.script(0x201,[255^buttons],cycles=0xffffffff);pair('WaitForInputOrRetraceTimeout',{'CX':count})
 for failure in [1,2,3]:
  m.reset();retrace();video.input_setup(m);m.device.script_count-=1;m.device.script(0x201,[255],cycles=0xffffffff);pair('WaitForInputOrRetraceTimeout',{'CX':3},failure_poll=failure)
 for name in ['InstallDosCriticalErrorFailHandler','FailDosCriticalError']:
  for i in range(100):
   m.reset();m.device.dos_error=5 if i%3==0 else 0;pair(name,{'AX':rng.randrange(65536),'DS':rng.randrange(0x8000)})
 for name in ['WaitVerticalRetraceActive','WaitVerticalRetraceInactive','WaitNextVerticalRetrace','WaitThroughVerticalRetrace','UploadBasePalette','ScaleAndUploadFadedPalette','ConfigureVgaGameplayPages','ConfigureVgaPicturePages','BlackenVgaPalette','FadePaletteIn','FadePaletteOut']:
  m.reset();pair(name)
 save(OUT/'cases.json',receipt([sys.executable,'verif/video_dos_evidence.py'],[Path(__file__),ROOT/'verif/video_dos_build.py',ROOT/'native/video_dos.c',ROOT/'native/video_dos.h',ROOT/'native/bridge/video_dos_bridge.c',ROOT/'c/dos_input.c',ROOT/'c/game_services.c',ROOT/'c/video.c',plain],result='PASS',cases=rows,seconds=time.perf_counter()-start));print('PASS',len(rows),'compiled video/DOS pairs',flush=True)
if __name__=='__main__':main()
