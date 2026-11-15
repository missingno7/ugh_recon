"""Partial standalone step 4: pages, indexed controls, clear/upload and swap/retrace.
Serial children, 600 s / 8 GiB. Scratch promotion only; no narrower VGA policy.
"""
import argparse,hashlib,inspect,json,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/workers/close-stones-20'
sys.path.insert(0,str(ROOT/'tools'))
import input_composition as prior
palette=prior.prior;timing=palette.timing;audio=palette.audio
prior.OUT=palette.OUT=audio.OUT=timing.OUT=timing.common.OUT=OUT
bounded=prior.bounded;save=prior.save;sha=prior.sha
NEW=['native/video_pages.h','native/video_pages.c','native/bridge/video_pages_bridge.h','native/bridge/video_pages_bridge.c']
BASE=NEW+['native/bridge/video_dos_bridge.c','verif/video_pages_platform_model.inc','verif/video_pages_composition.py',
 'tools/hostbuild.py','host/main.c','verif/projector/observer.c','verif/projector/timing_serializer.h',
 'verif/projector/publications.py','verif/projector_evidence.py']
READ=list(dict.fromkeys(prior.READ+['verif/input_composition.py','metadata/closure/input_world.json','native/video_dos.c','native/video_dos.h','src/asm/GAME.ASM','c/platform.c','c/memory.c','verif/vga_state_census.py']))
READ=list(dict.fromkeys(READ+['c/platform.h']+['metadata/closure/'+n+'.json' for n in ['player_physics','water_weather','session','demo_presentation']]))
NAMES=['ClearAllVgaPlanes','EnableAllVgaWritePlanes','ConfigureVgaGameplayPages','ConfigureVgaPicturePages',
 'SwapAndDisplayVgaPage','UploadChunkyImageToVgaPlanes','WaitNextVerticalRetrace','WaitRetraceCount',
 'WaitThroughVerticalRetrace','WaitVerticalRetraceActive','WaitVerticalRetraceInactive','WaitForInputOrRetraceTimeout']
TOTAL=6435

def files():return sorted(set(BASE+subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()+['metadata/closure/video_pages.json']))
palette.files=files
original_snapshot=palette.snapshot

def snapshot():
 target=original_snapshot();p=target/'metadata/closure/video_pages.json';c=json.loads(p.read_text());c['status']='migrated';save(p,c);return target
prior.snapshot=palette.snapshot=audio.snapshot=timing.snapshot=snapshot
build=palette.build
levels=palette.levels

def relock(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'relock',locals())


def api(group=None,*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'api',locals())

def projector(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'projector',locals())


def router():
 folder=OUT/'router';folder.mkdir(exist_ok=True)
 stubs='\n'.join('int c_'+n+'(Regs *r){(void)r;return 0;}' for n in ['BlackenVgaPalette','EnableAllVgaWritePlanes','ClearAllVgaPlanes','WaitNextVerticalRetrace','WaitVerticalRetraceActive','WaitVerticalRetraceInactive','PollKeyboardScanChange','SampleJoystickAxesAndButtons'])
 code=r'''#include "video_pages_bridge.h"
#include <stdio.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
uint8_t input_borrowed_byte(const uint8_t *p,uint32_t i){return p[i];}
void input_borrowed_store(uint8_t *p,uint32_t i,uint8_t v){p[i]=v;}
STUBS
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE];
int main(void){
 uint32_t base=lin(GAME_SEG,0x4600);
 uint8_t value=49;if(video_pages_shared_read(base,&value) || video_pages_shared_write(base,17) || value!=49)return 1;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(expected,ugh_mem,sizeof expected);video_pages_cold_import(ugh_mem);
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(video_pages_is_owned(a)!=(a>=base && a<base+20))return 2;
 if(video_pages_owned_bytes()!=20)return 3;
 _Static_assert(sizeof(NativeVideoPages)==20,"ten packed numeric words");
 NativeVideoPages *w=native_video_pages();
 uint16_t *words[]={&w->height,&w->copy_count,&w->fixed.position,&w->fixed.bank.value,&w->displayed.position,&w->displayed.bank.value,&w->draw.position,&w->draw.bank.value,&w->background.position,&w->background.bank.value};
 memcpy(output,ugh_mem,sizeof output);video_pages_serialize(output);if(memcmp(output,expected,sizeof output))return 4;
 for(unsigned i=0;i<10;i++){
  if(*words[i]!=(unsigned)(expected[base+2*i]|expected[base+2*i+1]*256u))return 5;
  for(unsigned v=0;v<65536;v++){
   video_pages_borrowed_store(ugh_mem,base+2*i,(uint8_t)v);video_pages_shared_write(base+2*i+1,(uint8_t)(v>>8));
   uint8_t lo,hi;video_pages_shared_read(base+2*i,&lo);video_pages_shared_read(base+2*i+1,&hi);
   if(*words[i]!=v || (unsigned)(lo|hi*256u)!=v || video_pages_borrowed_byte(ugh_mem+(base&~15u),2*i)!=lo)return 6;
   expected[base+2*i]=lo;expected[base+2*i+1]=hi;
  }
  video_pages_serialize(output);if(memcmp(output,expected,sizeof output))return 7;
 }
 for(unsigned i=0;i<20;i++)for(unsigned v=0;v<256;v++){
  video_pages_shared_write(base+i,(uint8_t)v);expected[base+i]=(uint8_t)v;
  video_pages_serialize(output);if(memcmp(output,expected,sizeof output))return 8;
  if(video_pages_check_serialization(output)!=UINT32_MAX)return 9;
 }
 video_pages_require_seal(ugh_mem);output[base+13]^=1;if(video_pages_check_serialization(output)!=base+13)return 10;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(a<base || a>=base+20){uint8_t v=49;if(video_pages_shared_read(a,&v) || video_pages_shared_write(a,17) || v!=49)return 11;}
 Regs r={0};r.cs=GAME_SEG+1;r.ss=0x8000;r.sp=0x100;r.ip=0x4567;
 if(video_pages_peer(VIDEO_PEER_WaitNextVerticalRetrace,0x1234,&r)!=UGH_BAD_CALLBACK || r.sp!=0x100)return 12;
 r.cs=GAME_SEG;if(video_pages_peer(VIDEO_PEER_WaitNextVerticalRetrace,0x1234,&r) || r.sp!=0x100 || r.ip!=0x4567)return 13;
 if(video_pages_peer((VideoPeerRole)99,0x1234,&r)!=UGH_BAD_CALLBACK || r.sp!=0xfe)return 14;
 printf("{\"owned_bytes\":20,\"byte_values\":5120,\"word_roundtrips\":655360,\"physical_addresses\":%u,\"peer_rejections\":2}\n",UGH_MEM_SIZE);return 0;
}
'''.replace('STUBS',stubs)
 source=folder/'router.c';source.write_text(code);exe=folder/'router.exe'
 bounded([timing.common.GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,source,ROOT/'native/video_pages.c',ROOT/'native/bridge/video_pages_bridge.c'],'router-compile')
 r=bounded([exe],'router-run');save(OUT/'router.json',dict(result='PASS',counts=json.loads(r['stdout'])))


def proof():
 from closure_support import function
 folder=OUT/'proof';folder.mkdir(exist_ok=True);bridge=(ROOT/'native/bridge/video_pages_bridge.c').read_text()
 prefix='#include "video_pages.h"\n#include "'+(ROOT/'native/video_pages.c').as_posix()+'"\n'
 prefix+=''.join(function(bridge,n) for n in ['video_pages_get_word','video_pages_put_word'])
 prefix+='void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);\n#define assert(c) __CPROVER_assert((c),#c)\n'
 # One selected word and arbitrary other word: complete ten-word frame inventory.
 main=r'''NativeVideoPages nondet_world(void);unsigned nondet_uint(void);uint16_t nondet_word(void);uint8_t nondet_byte(void);
int main(void){
 pages=nondet_world();unsigned selected=nondet_uint(),other=nondet_uint(),lane=nondet_uint();
 __CPROVER_assume(selected<10 && other<10 && other!=selected && lane<2);
 uint16_t *words[]={&pages.height,&pages.copy_count,&pages.fixed.position,&pages.fixed.bank.value,&pages.displayed.position,&pages.displayed.bank.value,&pages.draw.position,&pages.draw.bank.value,&pages.background.position,&pages.background.bank.value};
 uint16_t old=*words[selected],frame=*words[other];
 assert(video_pages_get_word(selected)==old);assert(*words[other]==frame);assert(*words[selected]==old);
 uint8_t value=nondet_byte();unsigned shift=lane*8;
 uint16_t result=(uint16_t)((old&~(255u<<shift))|((unsigned)value<<shift));
 video_pages_put_word(selected,result);
 assert(*words[selected]==result);assert(video_pages_get_word(selected)==result);assert(*words[other]==frame);
 assert((uint8_t)(video_pages_get_word(selected)>>shift)==value);
 assert((uint8_t)(*words[selected]>>((1-lane)*8))==(uint8_t)(old>>((1-lane)*8)));
}
'''
 source=folder/'fields.c';source.write_text(prefix+main);pre=folder/'fields.i'
 bounded([timing.common.GCC,'-E','-P','-nostdinc','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',source,'-o',pre],'proof-preprocess')
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe']
 r=bounded([tool,pre,'--unwind','2','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-fields')
 assert 'VERIFICATION SUCCESSFUL' in r['stdout']
 owner=dict(source=sha(source),preprocessed=sha(pre))
 provider=(ROOT/'verif/video_pages_platform_model.inc').read_text()
 code='#include "video_pages.h"\n'+r'''
void __CPROVER_assert(int,const char*);
#define assert(c) __CPROVER_assert((c),#c)
static unsigned count;static uint32_t addresses[2];static uint8_t values[2],reply;
uint8_t ugh_read(uint32_t a){addresses[count++]=a;return reply;}
void ugh_write(uint32_t a,uint8_t v){addresses[count]=a;values[count++]=v;}
'''+''.join(function(provider,n) for n in ['video_service_source_byte','video_service_store_byte','video_service_store_word'])+r'''
uint16_t nondet_word(void);uint8_t nondet_byte(void);
int main(void){
 VideoCellAddress a={{nondet_word()},nondet_word()};uint16_t value=nondet_word();reply=nondet_byte();
 uint32_t physical=(uint32_t)a.bank.value*16u+a.position;
 count=0;uint8_t read=video_service_source_byte(a);assert(count==1 && addresses[0]==physical && read==reply);
 count=0;video_service_store_byte(a,(uint8_t)value);assert(count==1 && addresses[0]==physical && values[0]==(uint8_t)value);
 count=0;video_service_store_word(a,value);assert(count==2 && addresses[0]==physical && addresses[1]==physical+1);
 assert(values[0]==(uint8_t)value && values[1]==(uint8_t)(value>>8));
}
'''
 source=folder/'services.c';source.write_text(code);pre=folder/'services.i'
 bounded([timing.common.GCC,'-E','-P','-nostdinc','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',source,'-o',pre],'proof-services-preprocess')
 r=bounded([tool,pre,'--unwind','2','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-services')
 assert 'VERIFICATION SUCCESSFUL' in r['stdout']
 save(OUT/'proof.json',dict(result='PASS',scope='Actual ten-way numeric get/put C: arbitrary complete 20-byte owner, selected word/byte and byte value, equality to independently named member, read-only getter, output plus other-byte and arbitrary-other-word frame. These cover all ten words, no padding. Actual provider source/byte/word service C: full bank/position/value slices, full read reply, exact ordered physical accesses, no clipping and physical high-byte carry. Physical routing/serialization separately exhaustively enumerated in C. No blanket whole-handler B claim.',owner=owner,services=dict(source=sha(source),preprocessed=sha(pre))))

def borrowers():
 source=inspect.getsource(palette.borrowers)
 source=source.replace("m.off('GAME:BaseRgbPalette')","m.off('GAME:PlayfieldHeight')").replace("m.off('GAME:FadedRgbPalette')","m.off('GAME:DrawPagePointer')")
 source=source.replace('[0x681,0x682,0x981,0xc81]','[0x614]').replace('ES=game+0x400','ES=game+0x400')
 source=source.replace(" save(OUT/'borrowers.json'", """ for src in [base,base+1,faded]:
  m.reset();m.ww('GAME:DrawPagePointer',0xfffe);m.ww('GAME:DrawPagePointer',0xa000,2);m.ww('GAME:VgaPlaneCopyByteCount',2)
  m.ww('DGROUP:DecodedImagePointer',src);m.ww('DGROUP:DecodedImagePointer',game,2)
  pair('UploadChunkyImageToVgaPlanes',regs=dict(DS=m.seg('DGROUP:DecodedImagePointer')))
 for src in [0,1,0xfffe]:
  for dst in [4,0x3e80,0xa988,0xffff]:
   for count in [1,2,7]:
    m.reset();m.ww('GAME:DrawPagePointer',dst);m.ww('GAME:DrawPagePointer',0xa000,2);m.ww('GAME:VgaPlaneCopyByteCount',count)
    m.ww('DGROUP:DecodedImagePointer',src);m.ww('DGROUP:DecodedImagePointer',0xa000,2)
    pair('UploadChunkyImageToVgaPlanes',regs=dict(DS=m.seg('DGROUP:DecodedImagePointer')))
 save(OUT/'borrowers.json'""")
 env=dict(palette.__dict__);exec(source,env);env['borrowers']()
 r=json.loads((OUT/'borrowers.json').read_text());r.pop('excluded_probe',None)
 r['scope']='Independent L1/composed live ABI, full Devices and RAM outside scratch stack. Far-copy/decimal/palette/ICE windows alias the 20 page lanes; forward/backward/wrapping overlapping windows; live chunky reads from VGA and off-page destinations. Decoder tables remain disjoint. No renderer/collision handler service conversion claimed.';save(OUT/'borrowers.json',r)


def backend(fault=0):
 import hostbuild
 folder=OUT/('backend' if not fault else 'defects/backend-'+str(fault));folder.mkdir(parents=True,exist_ok=True)
 code=r'''#include "platform.h"
#include "video_pages_bridge.h"
#include "input_world_bridge.h"
#include "palette_world_bridge.h"
#include "timing_world_bridge.h"
#include <stdio.h>
#include <string.h>
void ugh_devices_reset(void);
static Devices seed,expected;
static uint8_t memory[UGH_MEM_SIZE],result[UGH_MEM_SIZE];
static void begin_epoch(void){
#if VIDEO_TEST_FAULT == 3
 Regs r={0};video_service_frame_end((VideoServiceContext*)&r);
#endif
}
static void checkpoint(void){memcpy(&seed,&ugh_devices,sizeof seed);memcpy(memory,ugh_mem,sizeof memory);}
static void finish_old(void){memcpy(&expected,&ugh_devices,sizeof expected);memcpy(result,ugh_mem,sizeof result);memcpy(&ugh_devices,&seed,sizeof seed);memcpy(ugh_mem,memory,sizeof memory);}
static int match(void){return !memcmp(&expected,&ugh_devices,sizeof expected) && !memcmp(result,ugh_mem,sizeof result);}
int main(void){
 unsigned controls=0,pixels=0,levels=0;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 for(unsigned route=0;route<6;route++)for(unsigned value=0;value<256;value++){
  ugh_devices_reset();ugh_devices.seq_index=2;ugh_devices.crtc_index=19;
  ugh_devices.attr_index=16;ugh_devices.attr_phase=1;
  static const unsigned ports[]={0x3c4,0x3c5,0x3d4,0x3d5,0x3c0,0x3c1};
  checkpoint();unsigned raw=0;
  if(route==5)raw=platform_in(ports[route],1);else platform_out(ports[route],1,value);
  finish_old();unsigned now=0;
  if(route==5)now=video_service_control_read((VideoControlRoute)route).value;else video_service_control_write((VideoControlRoute)route,(uint8_t)value);
  if(now!=raw || !match())return 1;
  controls++;
 }
 for(unsigned wm=0;wm<4;wm++)for(unsigned rm=0;rm<2;rm++)for(unsigned rp=0;rp<4;rp++)for(unsigned mask=0;mask<16;mask++){
  ugh_devices_reset();ugh_devices.gc[5]=(uint8_t)(wm|(rm<<3));ugh_devices.gc[8]=(uint8_t)(0x55^(mask*17u));
  ugh_devices.gc[0]=(uint8_t)mask;ugh_devices.gc[1]=(uint8_t)(mask^15);ugh_devices.gc[2]=(uint8_t)(mask^5);ugh_devices.gc[7]=(uint8_t)(mask^10);ugh_devices.gc[3]=(uint8_t)((mask&3)*8+(mask&7));
  ugh_devices.map_mask=(uint8_t)mask;ugh_devices.read_map=(uint8_t)rp;
  const unsigned offsets[]={0,4,0x3e80,0x7d00,0xa988,0xffff};
  for(unsigned k=0;k<6;k++){
   unsigned o=offsets[k];for(unsigned p=0;p<4;p++){ugh_devices.plane[p][o]=(uint8_t)(p*43+mask*7);ugh_devices.latch[p]=(uint8_t)(0xe1-p*33);}
   begin_epoch();checkpoint();uint8_t raw=ugh_read(0xa0000+o);ugh_write(0xa0000+o,(uint8_t)(raw^0x93));finish_old();
   uint8_t now=video_service_source_byte((VideoCellAddress){{0xa000},(uint16_t)o});video_service_store_byte((VideoCellAddress){{0xa000},(uint16_t)o},(uint8_t)(now^0x93));
   if(now!=raw || !match())return 2;
   checkpoint();ugh_write(0xa0000+o,0x2d);ugh_write(0xa0000+o+1,0x7b);finish_old();
   video_service_store_word((VideoCellAddress){{0xa000},(uint16_t)o},0x7b2d);if(!match())return 3;
   pixels+=2;
  }
 }
 // Live read-after-write is deliberately in one epoch, never a cached source.
 for(unsigned mode=0;mode<2;mode++){
 ugh_devices_reset();ugh_devices.map_mask=15;ugh_devices.gc[8]=255;ugh_devices.gc[5]=(uint8_t)mode;
 for(unsigned p=0;p<4;p++)for(unsigned i=0;i<12;i++)ugh_devices.plane[p][i]=(uint8_t)(p*17+i*13);
 begin_epoch();checkpoint();for(unsigned i=0;i<2;i++){uint8_t v=ugh_read(0xa0000+i*4);ugh_write(0xa0004+i*4,v);}finish_old();
 for(unsigned i=0;i<2;i++){uint8_t v=video_service_source_byte((VideoCellAddress){{0xa000},(uint16_t)(i*4)});video_service_store_byte((VideoCellAddress){{0xa000},(uint16_t)(4+i*4)},v);}if(!match())return 4;
 }
 // A non-VGA source must preserve foreign latches; word high byte crosses B0000.
 ugh_devices_reset();ugh_devices.map_mask=15;ugh_devices.gc[5]=1;
 for(unsigned p=0;p<4;p++){ugh_devices.latch[p]=(uint8_t)(0x31+p*17);ugh_devices.plane[p][0]=0x92;}
 checkpoint();uint8_t raw=ugh_read(0x75000);ugh_write(0xaffff,raw);ugh_write(0xb0000,0x7b);finish_old();
 uint8_t now=video_service_source_byte((VideoCellAddress){{0x7500},0});video_service_store_word((VideoCellAddress){{0xa000},0xffff},(uint16_t)(now|0x7b00));
 if(!match())return 3;
 for(unsigned p=0;p<4;p++)if(ugh_devices.plane[p][65535]!=(uint8_t)(0x31+p*17) || ugh_devices.plane[p][0]!=0x92)return 3;
 if(ugh_mem[0xb0000]!=0x7b)return 3;
 for(unsigned i=0;i<256;i++){
  ugh_devices_reset();ugh_devices.script_count=1;InputScript *s=&ugh_devices.scripts[0];s->port=0x3da;s->count=1;s->cycles=s->cycles_left=1;s->runs[0]=(ScriptRun){i,1};
  checkpoint();unsigned raw=platform_in(0x3da,1);finish_old();VideoByteReply reply=video_service_retrace_level();if(reply.value!=raw || reply.status!=(expected.error?UGH_UNSUPPORTED:UGH_OK) || !match())return 5;levels++;
 }
 wr16(DATA_SEG,D(LastActiveTimerSlotOffset),30);timing_cold_import(ugh_mem);palette_cold_import(ugh_mem);input_cold_import(ugh_mem);video_pages_cold_import(ugh_mem);
 unsigned owned=0;for(unsigned a=0;a<UGH_MEM_SIZE;a++){unsigned n=(unsigned)timing_is_owned(a)+(unsigned)palette_is_owned(a)+(unsigned)input_is_owned(a)+(unsigned)video_pages_is_owned(a);if(n>1)return 6;owned+=n;}
 if(owned!=6435)return 7;
 video_pages_require_seal(ugh_mem);printf("{\"controls\":%u,\"pixel_read_store_pairs\":%u,\"full_retrace_bytes\":%u,\"native_bytes\":%u,\"live_alias_epochs\":2,\"foreign_latch_aperture_cross\":true}\n",controls,pixels,levels,owned);return 0;
}
'''
 source=folder/'backend.c';source.write_text(code)
 command=json.loads((OUT/'children/api-composed-compile.json').read_text())['command']
 platform=folder/'platform.c';units=hostbuild.selected_units()+[dict(component='video_pages')]
 platform.write_text(hostbuild.composition_source('c/platform.c',(ROOT/'c/platform.c').read_text(),units))
 command=[str(platform) if x==str(OUT/'api/composed/platform.c') else x for x in command]
 if fault:command.append('-DVIDEO_TEST_FAULT='+str(fault))
 command=[x for x in command if x!='-shared'];command[command.index('-o')+1]=str(folder/'backend.exe');command.extend([str(source)])
 bounded(command,'backend-compile-'+str(fault))
 if fault:
  capture=folder/'capture.py';capture.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n')
  r=bounded([sys.executable,capture,folder/'backend.exe'],'backend-defect-'+str(fault));actual=json.loads(r['stdout']);assert actual['returncode'] in [1,2,3,4],actual
  if fault==3:assert actual['returncode']==4,'Snapshot must be caught by same-epoch read-after-write, not stale fixtures'
  return dict(defect={1:'wrong-lane-mask',2:'stale-read-plane',3:'frame-start-copy-snapshot',4:'clipped-destination'}[fault],result='DETECTED',exit=actual['returncode'],scope='Typed source/store/control provider, including unchanged full inherited VGA model. Snapshot control checked at live source/store seam; sprite restore-copy conversion remains future work.')
 r=bounded([folder/'backend.exe'],'backend-run');save(OUT/'backend.json',dict(result='PASS',counts=json.loads(r['stdout']),scope='Actual c/platform and c/memory machine operations vs typed provider; whole RAM and Devices/log comparison for every transaction. All write/read modes, planes, lane masks and controls; hidden/off-page offsets, physical word aperture crossing, same-epoch read-after-write, all retrace reply bytes.'))

def census(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'census',locals())


def defects():
 rows=[backend(fault) for fault in [1,2,3,4]]
 target=snapshot()
 for fault,label in [(5,'reordered-retrace-page-swap'),(6,'missed-serialization')]:
  folder=OUT/'defects'/label
  for top in ['c','native','host','metadata','tools','verif','src']:shutil.copytree(target/top,folder/top,dirs_exist_ok=True)
  shutil.copytree(target/'build/link',folder/'build/link',dirs_exist_ok=True)
  p=folder/'tools/hostbuild.py';text=p.read_text().replace("return (['-DUGH_NATIVE_VIDEO_PAGES']", "return ['-DVIDEO_TEST_FAULT="+str(fault)+"']+(['-DUGH_NATIVE_VIDEO_PAGES']",1);p.write_text(text)
  bounded([sys.executable,'tools/hostbuild.py'],'defect-build-'+label,folder)
  capture=folder/'capture.py';capture.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n')
  command=[folder/'build/host/ugh.exe','--headless','48','--script',target/'tests/scenarios/gameplay-adlib.txt','--timeout','590']
  r=bounded([sys.executable,capture,*command],'defect-run-'+label);actual=json.loads(r['stdout'])
  if fault==6:
   assert actual['returncode']==88 and 'missed serialization' in actual['stderr'];rows.append(dict(defect=label,result='DETECTED',exit=88));continue
  assert actual['returncode']==0,actual['stderr']
  frames=[json.loads(line) for line in actual['stdout'].splitlines()];expected=json.loads((ROOT/'build/whole/gameplay-adlib.ref.json').read_text())['frames']
  first=next((i for i,(a,b) in enumerate(zip(frames,expected)) if a!=b),None);assert first is not None,label
  rows.append(dict(defect=label,result='DETECTED',scenario='gameplay-adlib',first_record=first+1))
 save(OUT/'defects.json',dict(result='PASS',controls=rows))


def inventory():
 import cgen
 _,symbols=cgen.read_symbols();model=json.loads((ROOT/'metadata/program-model.json').read_text());moved=[]
 for n,width in [('PlayfieldHeight',2),('VgaPlaneCopyByteCount',2),('FixedVgaPagePointer',4),('DisplayedVgaPagePointer',4),('DrawPagePointer',4),('BackgroundPagePointer',4)]:
  s=symbols['GAME:'+n];moved.append(dict(symbol='GAME:'+n,address=(cgen.LOAD+s['frame'])*16+s['offset'],bytes=width,model=model['variables'].get(n,{})))
 base=moved[0]['address'];assert [(m['address']-base,m['bytes']) for m in moved]==[(0,2),(2,2),(4,4),(8,4),(12,4),(16,4)]
 raw_users=[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'native').rglob('*.c')) if re.search(r'\bugh_mem\b',p.read_text())]
 allowed={'native/bridge/'+n+'_bridge.c' for n in ['adlx_loader','audio_world','decimal','far_copy','ice','ice_scratch','input_world','palette_world','timing_world','video_pages']};assert set(raw_users)<=allowed,set(raw_users)-allowed
 save(OUT/'ownership.json',dict(result='PASS',before=6415,added=20,after=TOTAL,moved=moved,raw_window_adapters=raw_users,
  shared_owners_stay_put=['WaterYPixels: existing shared water/session/menu owner; physics, passengers, demos and renderer read their accepted typed projections. WaterSurfaceByteOffset is a separate draw-derived offset and stays put in this cut','Player draw caches: current player/session/render shared owner in RAM','ActorRenderStorage histories: persistent actor canonical owner in RAM; demo, session and renderer remain explicit projections'],
  services=['Indexed sequencer/CRTC/attribute requests in original streaming order, preserving all inherited control and latch state','Live byte source/full-byte reply and indexed byte/word stores, opaque bank plus wrapping word position; no clipping','Retrace full-byte reply; active/input timeout scheduling cuts; page frame delivery after CRTC writes'],
  remaining='HUD caches/history; renderer/erase and render-owned weather state; sprite/latch-copy/read-plane/collision/water mark services; critical-error DOS hooks. No canonical player/actor/Water Y duplication.'))


def finalize(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'finalize',locals())


def main(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'main',locals())
# Scheduled by world_gate; no private CLI.
