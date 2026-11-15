"""Partial standalone step 4: persistent RGB palettes and streaming DAC services.
Every heavy child is serial, 600 seconds / 8 GiB. Native promotion occurs only
in a committed-baseline archive. The input and raw plane islands are unchanged.
"""
import argparse,hashlib,inspect,io,json,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/workers/close-stones-18'
sys.path.insert(0,str(ROOT/'tools'))
import audio_composition as audio
import timing_composition as timing
timing.OUT=audio.OUT=OUT;timing.common.OUT=OUT
audio.prior=timing
bounded=timing.bounded;save=timing.save;sha=timing.sha
NEW=['native/palette_world.h','native/palette_world.c','native/bridge/palette_world_bridge.h','native/bridge/palette_world_bridge.c']
BASE=NEW+['verif/palette_composition.py','native/bridge/video_dos_bridge.c','tools/hostbuild.py','host/main.c','verif/projector/timing_serializer.h','verif/projector/observer.c','verif/projector/publications.py','verif/projector_evidence.py']
READ_INPUTS=['c/ugh.h','c/ugh_sym.h','metadata/verif-tools.json','tools/cgen.py','metadata/program-model.json']
# Bind the reused evidence and accepted peer contracts as well as this adapter.
# No existing certificate refers back to palette_world, so these locks are acyclic.
READ_INPUTS += ['verif/audio_composition.py','verif/timing_composition.py','verif/entry_retirement.py',
 'verif/standalone_census.py','verif/level_suite.py','verif/closure_support.py','verif/windows_job.py',
 'tools/nbuild.py','tools/difftest.py','tools/dataprobe.py','tools/cbuild.py',
 *['metadata/closure/'+n+'.json' for n in ['video_dos','render_primitives','actor_render','audio_world',
     'timing_world','ice','ice_scratch','far_copy','decimal','pictures']],
 *[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'verif/cbmc_shim').glob('*')) if p.is_file()]]
def files():
 return sorted(set(BASE+subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()+['metadata/closure/palette_world.json']))
def snapshot():
 revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();target=OUT/'baseline'
 raw=subprocess.check_output(['git','archive','--format=tar',revision],cwd=ROOT)
 with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
  for member in tar.getmembers():
   if not member.isfile():continue
   p=(target/member.name).resolve();assert p.is_relative_to(target.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(tar.extractfile(member).read())
 for f in files():p=target/f;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,p)
 p=target/'metadata/closure/palette_world.json';c=json.loads(p.read_text());c['status']='migrated';save(p,c)
 for bank in ['whole','levels','levels-audio','levels-deep']:
  dest=target/'build'/bank;dest.mkdir(parents=True,exist_ok=True)
  for p in (ROOT/'build'/bank).glob('*.ref.json'):shutil.copyfile(p,dest/p.name)
 save(target/'build/workers/c-close/call-edges.json',[])
 save(OUT/'baseline.json',dict(revision=revision,overlay={f:sha(ROOT/f) for f in files()}));return target
# Reuse composed integration runners against this owner and scratch promotion.
audio.snapshot=timing.snapshot=snapshot

def locks(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'locks',locals())
def build(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'build',locals())

def api(group=None,*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'api',locals())

def router():
 folder=OUT/'router';folder.mkdir(exist_ok=True)
 code=r"""#include "palette_world_bridge.h"
#include <stdio.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
uint8_t audio_borrowed_byte(const uint8_t *p,uint32_t i){return p[i];}
void audio_borrowed_store(uint8_t *p,uint32_t i,uint8_t v){p[i]=v;}
int c_WaitNextVerticalRetrace(Regs *r){(void)r;return 0;}
int c_ScaleAndUploadFadedPalette(Regs *r){(void)r;return 0;}
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE];
int main(void){
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(expected,ugh_mem,sizeof expected);palette_cold_import(ugh_mem);
 unsigned addresses[1536],n=0;for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(palette_is_owned(a))addresses[n++]=a;
 if(n!=1536 || palette_owned_bytes()!=n)return 1;
 memcpy(output,ugh_mem,sizeof output);palette_serialize(output);if(memcmp(output,expected,sizeof output))return 2;
 for(unsigned i=0;i<n;i++){
  for(unsigned v=0;v<256;v++){
   if(v&1)palette_borrowed_store(ugh_mem+(addresses[i]&~15u),addresses[i]&15u,(uint8_t)v);
   else if(!palette_shared_write(addresses[i],(uint8_t)v))return 3;
   expected[addresses[i]]=(uint8_t)v;uint8_t actual;
   if(!palette_shared_read(addresses[i],&actual) || actual!=v)return 4;
   if(palette_borrowed_byte(ugh_mem,addresses[i])!=v)return 5;
   if(i && (!palette_shared_read(addresses[i-1],&actual) || actual!=expected[addresses[i-1]]))return 6;
   if(i+1<n && (!palette_shared_read(addresses[i+1],&actual) || actual!=expected[addresses[i+1]]))return 7;
  }
  palette_serialize(output);
  for(unsigned j=0;j<n;j++)if(output[addresses[j]]!=expected[addresses[j]])return 8;
  if(palette_check_serialization(output)!=UINT32_MAX)return 9;
  palette_require_seal(ugh_mem);
 }
 if(memcmp(native_palette_world()->base,expected+lin(GAME_SEG,G(BaseRgbPalette)),768) || memcmp(native_palette_world()->faded,expected+lin(GAME_SEG,G(FadedRgbPalette)),768))return 10;
 palette_serialize(output);output[addresses[n/2]]^=1;if(palette_check_serialization(output)!=addresses[n/2])return 11;
 uint8_t value=0;for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(!palette_is_owned(a) && palette_shared_read(a,&value))return 12;
 Regs r={0};r.cs=(uint16_t)(GAME_SEG+1);r.ss=0x8000;r.sp=0x100;r.ip=0x4567;
 if(palette_peer_deliver(PALETTE_PEER_WaitNextVerticalRetrace,0x1234,&r)!=UGH_BAD_CALLBACK || r.sp!=0x100 || r.ip!=0x4567)return 13;
 r.cs=GAME_SEG;if(palette_peer_deliver(PALETTE_PEER_WaitNextVerticalRetrace,0x1234,&r)!=UGH_OK || r.sp!=0x100 || r.ip!=0x4567)return 14;
 if(palette_peer_deliver((PalettePeerRole)99,0x1234,&r)!=UGH_BAD_CALLBACK || r.sp!=0xfe || r.ip!=0x4567)return 15;
 printf("{\"owned_bytes\":%u,\"byte_values\":%u,\"outside_addresses\":%u,\"missed_output_control\":true,\"explicit_peer_rejections\":2}\n",n,n*256u,UGH_MEM_SIZE-n);return 0;
}
"""
 source=folder/'router.c';source.write_text(code)
 exe=folder/'router.exe';bounded([timing.common.GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,source,ROOT/'native/palette_world.c',ROOT/'native/bridge/palette_world_bridge.c'],'router-compile')
 row=bounded([exe],'router-run');save(OUT/'router.json',dict(result='PASS',counts=json.loads(row['stdout'])))

def proof():
 from closure_support import function
 folder=OUT/'proof';folder.mkdir(exist_ok=True)
 bridge=(ROOT/'native/bridge/palette_world_bridge.c').read_text()
 prefix='#include "palette_world.h"\n#include "'+(ROOT/'native/palette_world.c').as_posix()+'"\n'
 prefix+='static unsigned active;\n#include "'+(ROOT/'c/ugh_sym.h').as_posix()+'"\n#define GAME_SEG UGH_SEG_GAME\n#define G(n) UGH_O_GAME_##n\n'
 prefix+=function((ROOT/'c/ugh.h').read_text(),'lin')
 prefix+=''.join(function(bridge,n) for n in ['palette_index','palette_get','palette_put','palette_shared_read','palette_shared_write'])
 harness=folder/'bytes.c'
 main=r"""void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);
#define assert(c) __CPROVER_assert((c),#c)
NativePaletteWorld nondet_world(void);unsigned nondet_uint(void);uint8_t nondet_byte(void);
int main(void){
 world=nondet_world();unsigned index=nondet_uint(),other=nondet_uint();
 __CPROVER_assume(index<1536 && other<1536 && index!=other);
 uint8_t before=palette_get(index),frame=palette_get(other),value=nondet_byte(),reply=nondet_byte();
 active=nondet_uint();__CPROVER_assume(active<2);
 unsigned was_active=active;
 uint32_t address=index<768?lin(GAME_SEG,G(BaseRgbPalette)+index):lin(GAME_SEG,G(FadedRgbPalette)+index-768);
 assert(palette_shared_write(address,value)==(int)active);
 assert(palette_get(index)==(active?value:before));assert(palette_get(other)==frame);
 uint8_t old_reply=reply;
 int read=palette_shared_read(address,&reply);assert(read==(int)active);
 assert(reply==(active?value:old_reply));assert(active==was_active);
 assert(palette_get(index)==(active?value:before));assert(palette_get(other)==frame);
 uint32_t outside=nondet_uint();unsigned decoded=0;
 __CPROVER_assume(!palette_index(outside,&decoded));
 before=palette_get(index);frame=palette_get(other);
 assert(!palette_shared_write(outside,value));assert(palette_get(index)==before && palette_get(other)==frame);
 old_reply=reply;assert(!palette_shared_read(outside,&reply));assert(reply==old_reply);
 assert(palette_get(index)==before && palette_get(other)==frame && active==was_active);
}
"""
 harness.write_text(prefix+main)
 bounded([timing.common.GCC,'-E','-P','-nostdinc','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',harness,'-o',folder/'bytes.i'],'proof-preprocess')
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe']
 r=bounded([tool,folder/'bytes.i','--unwind','3','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-bytes')
 assert 'VERIFICATION SUCCESSFUL' in r['stdout']
 save(OUT/'proof.json',dict(result='PASS',scope='Actual palette index/get/put/shared byte C. Arbitrary complete owner, selected and arbitrary other byte, active/inactive routing, arbitrary outside address and all byte values: output, frame and dependence.',source=sha(harness),preprocessed=sha(folder/'bytes.i')))

def borrowers():
 import ctypes as C,random,struct
 import difftest,nbuild
 dlls=[nbuild.load_l1(OUT/'api'/v/'api.dll') for v in ['reference','composed']]
 m=difftest.Machine();rng=random.Random(1818);rows=[]
 def pair(name,args=(),regs=None,mutate=False):
  initial=m.prepare('GAME:'+name,{**difftest.POISON,**(regs or {})},'far',args,0x602 if len(rows)&1 else 0x202);memory=m.snapshot();observations=[];callbacks=[]
  for dll in dlls:
   C.memmove(dll.ugh_memory().contents,memory,len(memory));dll.ugh_devices_reset();dev=dll.ugh_device_state().contents;state=m.device.state();C.memmove(C.addressof(dev),state,len(state))
   if mutate:
    output=C.CFUNCTYPE(None,C.c_uint16,C.c_uint,C.c_uint32);events=[0]
    def on_output(port,size,value,dll=dll,events=events):
     if port==0x3c9:
      events[0]+=1
      if events[0]==1:dll.ugh_store16(game,base+1,0xa735)
    cb=output(on_output);callbacks.append(cb);dll.ugh_set_output_observer.argtypes=[output];dll.ugh_set_output_observer(cb)
   r=difftest.Regs(**{k.lower():v for k,v in initial.items()});fn=getattr(dll,'api_c_'+name);fn.argtypes=[C.POINTER(difftest.Regs)];status=fn(C.byref(r))
   if mutate:dll.ugh_set_output_observer(output())
   actual=bytes(dll.ugh_memory().contents);lo=initial['SS']*16;hi=lo+initial['SP']
   live=tuple(getattr(r,k) for k in ['ax','bx','cx','dx','si','di','bp','sp','cs','ds','es','ss','ip'])+(r.flags&0x600,)
   observations.append((status,live,actual[:lo]+actual[hi:],bytes(dev)))
  if observations[0]!=observations[1]:
   save(OUT/'borrower-negative.json',dict(entry=name,index=len(rows),statuses=[o[0] for o in observations],live=[o[1] for o in observations],memory_first=next((i for i,(a,b) in enumerate(zip(observations[0][2],observations[1][2])) if a!=b),None),device_first=next((i for i,(a,b) in enumerate(zip(observations[0][3],observations[1][3])) if a!=b),None)))
  assert observations[0]==observations[1],(name,len(rows),'compiled borrower mismatch')
  rows.append(dict(entry=name,args=args,regs=regs,interleaved_output_mutation=mutate,status=observations[0][0]))
 game=m.seg('GAME:BaseRgbPalette');base=m.off('GAME:BaseRgbPalette');faded=m.off('GAME:FadedRgbPalette')
 for source in [base,faded,0xfffe]:
  for delta in [-4,-1,0,1,4]:
   for count in [0,1,2,12,42,255,768,65535]:
    m.reset();m.write(game,base,rng.randbytes(1536));pair('CopyFarBytes',(count,0,source,game,(source+delta)&65535,game))
 for target in [base,base+1,faded-2,faded,0xffff]:
  for value in [0,1,99,100,65535,0xffffffff]:
   for name in ['EncodeTwoDecimalDigits','EncodeFourDecimalDigits','EncodeSixDecimalDigits']:
    m.reset()
    for label,word in [('DecimalTenDivisor',10),('DecimalHundredDivisor',100),('DecimalThousandDivisor',1000),('DecimalTenThousandDivisor',10000)]:m.write(game,m.off('DGROUP:'+label),struct.pack('<H',word))
    pair(name,regs=dict(DS=game,SI=target,AX=value&65535,DX=value>>16))
 for source in [base-2,base,base+1,faded]:
  for destination in [base-2,base,base+2,faded]:
   m.reset();m.write(game,base,rng.randbytes(1536))
   for label,word in [('BasePalettePointer',destination),('PaletteSourcePointer',source)]:m.ww('DGROUP:'+label,word);m.ww('DGROUP:'+label,game,2)
   pair('DuplicateSourcePaletteHalves',regs=dict(DS=m.seg('DGROUP:BasePalettePointer')))
 m.reset();m.write(game,base,bytes((i*73)&255 for i in range(1536)));m.device.script(0x3da,[0,8],cycles=0xffffffff)
 pair('UploadBasePalette',regs=dict(DS=m.seg('DGROUP:BasePalettePointer')),mutate=True)
 # A maximal ICE destination window spans palette, audio and timer-owned cells.
 from dataprobe import ice_pack235
 for length in [0x681,0x682,0x981,0xc81]:
  m.reset();data=(bytes(range(256))*(length//256+1))[:length];stream=ice_pack235(data);m.write(0x7500,0,stream)
  pair('UnpackIceStream',regs=dict(DS=0x7500,ES=game+0x400,SI=0,DI=0xbeef))
 save(OUT/'borrowers.json',dict(result='PASS',cases=rows,excluded_probe='An exploratory ICE destination GAME:0000 with unpacked length 32768 overwrites immutable decoder tables. It is outside the accepted ICE disjoint-table contract; diagnostic retained in negative receipts. Safe windows end before GAME:4C81 and still cover both palettes.',scope='Independent compiled L1 versus composed owner, live ABI/IF/DF, RAM outside current scratch stack, complete devices/ordered output. Ordered copy/decimal/duplicate overlap and word wraps, interleaved source mutation during DAC output, and real ICE writes across both palettes with retained audio/timer lanes in the seeded 64KiB window.'))

def backend(fault=0):
 folder=OUT/('backend' if not fault else 'defects/backend-'+str(fault));folder.mkdir(exist_ok=True);source=folder/'backend.c'
 source.write_text(r"""#include "platform.h"
#include "palette_world.h"
#include <stdio.h>
#include <string.h>
static uint8_t expected[768],actual[768];
static void controls(void){
 for(unsigned i=0;i<9;i++)ugh_devices.gc[i]=(uint8_t)(i*37u+19);
 for(unsigned i=0;i<5;i++)ugh_devices.seq[i]=(uint8_t)(i*43u+91);
 for(unsigned i=0;i<4;i++)ugh_devices.latch[i]=(uint8_t)(i*67u+33);
 ugh_devices.map_mask=5;ugh_devices.read_map=3;
}
static int unchanged(void){
 for(unsigned i=0;i<9;i++)if(ugh_devices.gc[i]!=(uint8_t)(i*37u+19))return 0;
 for(unsigned i=0;i<5;i++)if(ugh_devices.seq[i]!=(uint8_t)(i*43u+91))return 0;
 for(unsigned i=0;i<4;i++)if(ugh_devices.latch[i]!=(uint8_t)(i*67u+33))return 0;
 return ugh_devices.map_mask==5 && ugh_devices.read_map==3;
}
int main(void){
 unsigned cases=0;
 for(unsigned i=0;i<768;i++)expected[i]=actual[i]=(uint8_t)(i*73u+11);
 for(unsigned index=0;index<256;index++)for(unsigned component=0;component<3;component++)for(unsigned value=0;value<256;value++){
  memcpy(ugh_devices.dac,expected,768);ugh_devices.dac_index=(uint8_t)index;ugh_devices.dac_component=(uint8_t)component;ugh_devices.count=0;controls();
  platform_out(0x3c9,1,value);memcpy(expected,ugh_devices.dac,768);
  uint8_t next=ugh_devices.dac_index,part=ugh_devices.dac_component;IoEvent record=ugh_devices.log[0];
  memcpy(ugh_devices.dac,actual,768);ugh_devices.dac_index=(uint8_t)index;ugh_devices.dac_component=(uint8_t)component;ugh_devices.count=0;controls();
  palette_service_dac((PaletteDacWrite){PALETTE_DAC_COMPONENT,(uint8_t)value});memcpy(actual,ugh_devices.dac,768);
  if(memcmp(actual,expected,768) || next!=ugh_devices.dac_index || part!=ugh_devices.dac_component || ugh_devices.count!=1 || memcmp(&record,ugh_devices.log,sizeof record) || !unchanged())return 1;
  cases++;
 }
 for(unsigned value=0;value<256;value++){
  ugh_devices.dac_index=73;ugh_devices.dac_component=2;ugh_devices.count=0;controls();platform_out(0x3c8,1,value);
  uint8_t next=ugh_devices.dac_index,part=ugh_devices.dac_component;IoEvent record=ugh_devices.log[0];
  ugh_devices.dac_index=73;ugh_devices.dac_component=2;ugh_devices.count=0;controls();palette_service_dac((PaletteDacWrite){PALETTE_DAC_SELECT,(uint8_t)value});
  if(next!=ugh_devices.dac_index || part!=ugh_devices.dac_component || ugh_devices.count!=1 || memcmp(&record,ugh_devices.log,sizeof record) || !unchanged())return 2;
  cases++;
 }
 /* Reproduce the census's compatibility edges on the same composed memory. */
 memset(ugh_devices.gc,0,sizeof ugh_devices.gc);ugh_devices.gc[8]=255;ugh_devices.map_mask=15;ugh_devices.read_map=3;
 ugh_write(0xa0064,41);ugh_devices.gc[5]=1;
 ugh_write(0xa0065,ugh_read(0xa0064));ugh_write(0xa0066,ugh_read(0xa0065));
 for(unsigned p=0;p<4;p++)if(ugh_devices.plane[p][101]!=41 || ugh_devices.plane[p][102]!=41)return 3;
 for(unsigned p=0;p<4;p++)ugh_devices.latch[p]=(uint8_t)(0x30+p);
 ugh_write(0xa00c8,0);for(unsigned p=0;p<4;p++)if(ugh_devices.plane[p][200]!=(uint8_t)(0x30+p))return 4;
 ugh_devices.gc[5]=0;for(unsigned p=0;p<4;p++)ugh_devices.plane[p][0]=(uint8_t)(0x60+p);
 wr16(0xa000,0xffff,0x7b2d);
 for(unsigned p=0;p<4;p++)if(ugh_devices.plane[p][65535]!=0x2d || ugh_devices.plane[p][0]!=(uint8_t)(0x60+p))return 5;
 if(ugh_mem[0xb0000]!=0x7b || rd16(0xa000,0xffff)!=0x7b2d || rd8(0xa000,0)!=0x63)return 6;
 printf("{\"transactions\":%u,\"inherited_controls_unchanged\":true,\"compatibility_edges\":3}\n",cases);return 0;
}
""")
 command=json.loads((OUT/'children/api-composed-compile.json').read_text())['command']
 import hostbuild
 units=hostbuild.selected_units()
 platform=folder/'platform.c';platform.write_text(hostbuild.composition_source('c/platform.c',(ROOT/'c/platform.c').read_text(),units))
 command=[str(platform) if str(x).endswith(('\\platform.c','/platform.c')) else x for x in command]
 if fault:command.append('-DPALETTE_TEST_FAULT='+str(fault))
 command=[x for x in command if x!='-shared'];command[command.index('-o')+1]=str(folder/'backend.exe');command.extend(['-I',str(ROOT/'native'),str(source)])
 bounded(command,'backend-compile-'+str(fault))
 if fault:
  capture=folder/'capture.py';capture.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n')
  r=bounded([sys.executable,capture,folder/'backend.exe'],'backend-defect-'+str(fault));actual=json.loads(r['stdout']);assert actual['returncode']==1,actual
  return dict(defect='wrong-lane-mask' if fault==5 else 'stale-read-plane',result='DETECTED',scope='Typed DAC provider must frame inherited plane/lane state',exit=1)
 r=bounded([folder/'backend.exe'],'backend-run')
 save(OUT/'backend.json',dict(result='PASS',counts=json.loads(r['stdout']),scope='Actual c/platform DAC versus typed provider: 256 indices x3 valid inherited partial-component states x256 bytes, plus index selection. Exact log order, all DAC bytes/cursors and frame of inherited GC, sequencer, mask, read-plane and latch state; census same-copy overlap/read-after-write, inherited foreign latch and aperture word-cross/wrap examples reproduced.'))

def projector(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'projector',locals())

def levels(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'levels',locals())
PALETTE_ENTRIES={'c_BlackenVgaPalette','c_UploadBasePalette','c_DuplicateSourcePaletteHalves','c_ScaleAndUploadFadedPalette','c_FadePaletteIn','c_FadePaletteOut'}
def census(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'census',locals())

def defects():
 target=snapshot();rows=[]
 for fault,label in [(1,'missed-serialization'),(2,'dac-batch-order'),(3,'stale-palette-view'),(4,'dropped-dac-component')]:
  folder=OUT/'defects'/label
  for top in ['c','native','host','metadata','tools','verif','src']:shutil.copytree(target/top,folder/top,dirs_exist_ok=True)
  shutil.copytree(target/'build/link',folder/'build/link',dirs_exist_ok=True)
  p=folder/'tools/hostbuild.py';text=p.read_text().replace("return (['-DUGH_NATIVE_PALETTE']", "return ['-DPALETTE_TEST_FAULT="+str(fault)+"']+(['-DUGH_NATIVE_PALETTE']",1);p.write_text(text)
  bounded([sys.executable,'tools/hostbuild.py'],'defect-build-'+label,folder)
  command=[folder/'build/host/ugh.exe','--headless','48','--script',target/'tests/scenarios/gameplay-adlib.txt','--timeout','590']
  capture=OUT/'defects/capture.py';capture.parent.mkdir(exist_ok=True);capture.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n')
  result=bounded([sys.executable,capture,*command],'defect-run-'+label);actual=json.loads(result['stdout'])
  if fault==1:
   assert actual['returncode']==88 and 'missed serialization' in actual['stderr'];rows.append(dict(defect=label,result='DETECTED',exit=88));continue
  assert actual['returncode']==0,actual['stderr']
  records=[json.loads(line) for line in actual['stdout'].splitlines()];expected=json.loads((ROOT/'build/whole/gameplay-adlib.ref.json').read_text())['frames']
  first=next((i for i,(a,b) in enumerate(zip(records,expected)) if a!=b),None);assert first is not None,label
  rows.append(dict(defect=label,result='DETECTED',scenario='gameplay-adlib',first_record=first+1))
 rows.extend([backend(5),backend(6)])
 save(OUT/'defects.json',dict(result='PASS',controls=rows,remaining='Dropped scan delivery remains with the uncomposed input seam. Lane/read-plane controls here test the DAC provider frame; they do not close those plane services.'))

def finalize(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'finalize',locals())


def main(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'main',locals())
# Scheduled by world_gate; no private CLI.
