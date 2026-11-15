"""Compiled full-RAM, ordered store/service and alias checks for cut 5B."""
import ctypes as C,inspect,json,re,sys
HELPER=r'''#include "platform.h"
#ifdef UGH_NATIVE_RANDOM
#include "random_world_bridge.h"
#include "timing_world_bridge.h"
#include "palette_world_bridge.h"
#include "input_world_bridge.h"
#include "video_pages_bridge.h"
#include "pixel_world_bridge.h"
#include "presentation_world_bridge.h"
#include "run_world_bridge.h"
#endif
#include <string.h>
#include <stdlib.h>
typedef struct RngTrace {uint32_t address;uint8_t value,words[8];} RngTrace;
static RngTrace traces[4096];static unsigned enabled,used;static uint32_t watched;
EXPORT void api_rng_trace_begin(uint16_t bank){enabled=1;used=0;watched=lin(bank,0x4ef7);}
EXPORT unsigned api_rng_trace_count(void){return used;}
EXPORT RngTrace *api_rng_trace_data(void){return traces;}
void api_rng_notify(uint32_t a,uint8_t value){
 uint32_t base=watched;if(!enabled || a<base || a>=base+8)return;
 if(used==4096)exit(89);
 RngTrace *t=&traces[used++];memset(t,0,sizeof *t);t->address=a;t->value=value;
 for(unsigned i=0;i<8;i++)t->words[i]=ugh_read(base+i);
}
void api_device_write(uint32_t,uint8_t);
void ugh_write(uint32_t a,uint8_t value){api_device_write(a,value);
#ifdef UGH_NATIVE_RANDOM
 if(rng_is_owned(a))return;
#endif
 api_rng_notify(a,value);
}
EXPORT unsigned api_rng_owner_audit(void){
#ifdef UGH_NATIVE_RANDOM
 unsigned total=0,new_bytes=0;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++){
  unsigned n=timing_is_owned(a)+palette_is_owned(a)+input_is_owned(a)+video_pages_is_owned(a)+pixel_is_owned(a)+presentation_is_owned(a)+run_is_owned(a)+rng_is_owned(a);
  if(n>1)return 1;
  total+=n;new_bytes+=(unsigned)rng_is_owned(a);
 }
 if(total!=8041 || new_bytes!=8)return 2;
#endif
 return 0;
}
static unsigned seconds,services;
static int bulk_time(uint8_t n,Regs*r){if(n!=0x21 || (r->ax>>8)!=0x2c)return UGH_UNSUPPORTED;services++;r->cx=0x0c22;r->dx=(uint16_t)(seconds*256+56);return UGH_OK;}
EXPORT uint32_t api_rng_bulk(void){
 enabled=0;Regs r={0};r.cs=GAME_SEG;r.flags=0x602;ugh_set_interrupt_service(bulk_time);services=0;
 for(unsigned i=1;i<4;i++)wr16(GAME_SEG,(uint16_t)(0x4ef7+2*i),(uint16_t)(0x8173u+i*0x1333u));
 for(unsigned w=0;w<65536;w++)for(seconds=0;seconds<256;seconds++){
  wr16(GAME_SEG,0x4ef7,(uint16_t)w);ugh_devices.count=0;
  if(c_SeedRandomFromDosSeconds(&r)!=UGH_OK || rd16(GAME_SEG,0x4ef7)!=((w&255u)|seconds*256u) || ugh_devices.count!=1)return 1;
  for(unsigned i=1;i<4;i++)if(rd16(GAME_SEG,(uint16_t)(0x4ef7+2*i))!=(uint16_t)(0x8173u+i*0x1333u))return 2;
 }
 ugh_set_interrupt_service(0);if(services!=16777216u)return 3;
 // Every bound, each starting at a carry-heavy state. Independent wide sums.
 for(unsigned bound=0;bound<65536;bound++){
  uint16_t old[4]={0xffff,0x8000,0x7fff,0xffff},next[4];
  for(unsigned i=0;i<4;i++)wr16(GAME_SEG,(uint16_t)(0x4ef7+2*i),old[i]);
  uint32_t sum=bound+old[0];uint16_t first=(uint16_t)sum;
  for(unsigned i=1;i<4;i++){sum=old[i]+(i==1?first:next[i-1])+(sum/65536u);next[i]=(uint16_t)sum;}
  next[0]=(uint16_t)(first+next[3]+sum/65536u);r.ax=(uint16_t)bound;
  if(c_NextRandomBelowAx(&r)!=UGH_OK || r.ax!=(uint32_t)next[0]*bound/65536u)return 4;
  for(unsigned i=0;i<4;i++)if(rd16(GAME_SEG,(uint16_t)(0x4ef7+2*i))!=next[i])return 5;
 }
 return 0;
}
'''

def compile_trace(ROOT,OUT,bounded,label,mutation=None):
 folder=OUT/'api/trace'/label;folder.mkdir(parents=True,exist_ok=True)
 profile='reference' if label=='reference' else 'composed'
 command=json.loads((OUT/('children/api-random-'+profile+'-compile.json')).read_text())['command'];command[command.index('-o')+1]=str(folder/'api.dll')
 for i,arg in enumerate(command):
  if not arg.endswith('.c'):continue
  original=__import__('pathlib').Path(arg);text=original.read_text();changed=False
  if original.name=='memory.c':assert text.count('void ugh_write(')==1;text=text.replace('void ugh_write(','void api_device_write(',1);changed=True
  if original.name=='random_world_bridge.c':
   assert text.count('rng_put(lane,value);return 1;')==1;text='#include "ugh.h"\nextern void api_rng_notify(uint32_t,uint8_t);\n'+text.replace('rng_put(lane,value);return 1;','rng_put(lane,value);api_rng_notify(address,value);return 1;');changed=True
  if mutation:
   name,old,new=mutation
   if original.name==name:assert text.count(old)==1,(name,old);text=text.replace(old,new);changed=True
  if changed:
   text=re.sub(r'#include "([^\"]+)"',lambda m:'#include "'+(original.parent/m[1]).resolve().as_posix()+'"' if (original.parent/m[1]).is_file() else m[0],text)
   target=folder/original.name;target.write_text(text);command[i]=str(target)
 helper=folder/'trace.c';helper.write_text(HELPER);command.append(str(helper));dll=folder/'api.dll'
 bounded(command,'trace-'+label+'-compile');return dll

class Trace(C.Structure):_fields_=[('address',C.c_uint32),('value',C.c_uint8),('words',C.c_uint8*8)]

def load(path):
 import nbuild
 dll=nbuild.load_l1(path);dll.api_rng_trace_count.restype=C.c_uint;dll.api_rng_trace_data.restype=C.POINTER(Trace)
 dll.api_live_word.argtypes=[C.c_uint16,C.c_uint16];dll.api_live_word.restype=C.c_uint16;dll.api_live_store.argtypes=[C.c_uint16,C.c_uint16,C.c_uint16]
 dll.api_rng_bulk.restype=C.c_uint32
 return dll

def pair(m,dlls,name,bound=0,mutate=False,fail=False,flags=0x602,foreign=False):
 import difftest
 game=m.seg('GAME:RandomStateWord0');bank=0x7500 if foreign else game
 initial=m.prepare('GAME:'+name,{**difftest.POISON,**({'DS':m.seg('DGROUP:PlayerCount'),'BX':0} if name=='RespawnRainParticle' else {}),'AX':bound,'CS':bank},'far',(),flags);memory=m.snapshot();device=m.device.state();outputs=[];holds=[]
 for dll in dlls:
  C.memmove(dll.ugh_memory().contents,memory,len(memory));dll.ugh_devices_reset();dev=dll.ugh_device_state().contents;C.memmove(C.addressof(dev),device,len(device));dll.api_begin();dll.api_rng_trace_begin.argtypes=[C.c_uint16];dll.api_rng_trace_begin(bank);calls=[]
  if mutate or fail:
   fn=C.CFUNCTYPE(C.c_int,C.c_uint8,C.POINTER(difftest.Regs))
   def service(number,r,dll=dll,calls=calls):
    assert number==0x21 and r.contents.ax>>8==0x2c;calls.append(number)
    if mutate:
     for i,v in enumerate([0xb761,0xc872,0xd983,0xea94]):dll.api_live_store(bank,0x4ef7+2*i,v)
    r.contents.cx=0xa24d;r.contents.dx=0xfe81;r.contents.ax=0x2c37;r.contents.flags=0x6d7
    return 1 if fail else 0
   cb=fn(service);holds.append(cb);dll.ugh_set_interrupt_service.argtypes=[fn];dll.ugh_set_interrupt_service(cb)
  r=difftest.Regs(**{k.lower():v for k,v in initial.items()});function=getattr(dll,'api_c_'+name);function.argtypes=[C.POINTER(difftest.Regs)];status=function(C.byref(r))
  if mutate or fail:dll.ugh_set_interrupt_service(fn())
  if name=='SeedRandomFromDosSeconds':assert dev.count==1,'empty/extra time request'
  count=dll.api_rng_trace_count();assert count<4096
  trace=C.string_at(dll.api_rng_trace_data(),count*C.sizeof(Trace));ram=bytes(dll.ugh_memory().contents)
  outputs.append((status,bytes(r),ram,bytes(dev),trace,tuple(calls)))
 return outputs

def setup(m,state=(0x7f03,0x8134,0x48bc,0x2347),foreign=False):
 m.reset();bank=0x7500 if foreign else m.seg('GAME:RandomStateWord0')
 for i,v in enumerate(state):m.write(bank,0x4ef7+2*i,v.to_bytes(2,'little'))
 m.device.script(0xfffe,[0x0c223b38])

def run(ROOT,OUT,bounded,save):
 import difftest,nbuild,palette_composition as palette
 paths=[compile_trace(ROOT,OUT,bounded,p) for p in ['reference','composed']];dlls=[load(p) for p in paths];m=difftest.Machine();rows=[]
 for foreign in [False,True]:
  for state in [(0,0,0,0),(65535,65535,65535,65535),(0x8000,0x7fff,0xffff,1),(0x7f03,0x8134,0x48bc,0x2347)]:
   for bound in [0,1,2,319,320,321,0x7fff,0x8000,0xfffe,0xffff]:
    setup(m,state,foreign);out=pair(m,dlls,'NextRandomBelowAx',bound,foreign=foreign);assert out[0]==out[1],('draw',state,bound,foreign)
    assert len(out[0][4])==8*C.sizeof(Trace),'empty/missing store stream';rows.append(dict(entry='NextRandomBelowAx',bound=bound,state=state,foreign=foreign,store_bytes=8))
  for mutate in [False,True]:
   for fail in [False,True]:
    setup(m,foreign=foreign);out=pair(m,dlls,'SeedRandomFromDosSeconds',mutate=mutate,fail=fail,foreign=foreign);assert out[0]==out[1],('seed',mutate,fail,foreign)
    assert len(out[0][4])==(8*int(mutate)+int(not fail))*C.sizeof(Trace)
    if mutate:
     a=0x7500*16+0x4ef7 if foreign else m.seg('GAME:RandomStateWord0')*16+0x4ef7
     assert int.from_bytes(out[1][2][a:a+2],'little')==(0xb761 if fail else 0xfe61),'stale parent overwrite'
    rows.append(dict(entry='SeedRandomFromDosSeconds',mutate=mutate,failed_service=fail,foreign=foreign,service_calls=1,store_bytes=len(out[0][4])//C.sizeof(Trace)))
 # Actual composed and L1 bridge bulk sweeps; no Python callbacks/observer snapshots
 # inside these loops. Each seed's real DOS service log is count-checked.
 for dll in dlls:
  setup(m);out=pair(m,[dll,dll],'NextRandomBelowAx',0);assert out[0]==out[1]
  assert dll.api_rng_owner_audit()==0,'overlap or missing owner'
  assert dll.api_rng_bulk()==0,'full-domain canonical owner seed/bound sweep'
 # Reuse generic live-window corpus with RNG at its base, but omit ICE windows:
 # reaching this GAME-embedded state would overlap active code/tables, outside
 # the accepted ICE source/resource disjointness contract (a 5R/D5 question).
 source=inspect.getsource(palette.borrowers);source=source[:source.index(' # A maximal ICE destination')]
 source=source.replace("OUT/'api'/v/'api.dll'","OUT/'api/random'/v/'api.dll'")
 source=source.replace("m.seg('GAME:BaseRgbPalette')","m.seg('GAME:RandomStateWord0')").replace("m.off('GAME:BaseRgbPalette')","m.off('GAME:RandomStateWord0')").replace("m.off('GAME:FadedRgbPalette')","m.off('GAME:RandomStateWord2')")
 source=source.replace('  for dll in dlls:\n','  for dll in dlls:\n   dll.api_begin()\n')
 source=source.replace("pair('UploadBasePalette',regs=", "m.ww('DGROUP:BasePalettePointer',base);m.ww('DGROUP:BasePalettePointer',game,2)\n pair('UploadBasePalette',regs=")
 source+=' save(OUT/"byte-borrowers.json",dict(result="PASS",cases=rows))\n'
 env=dict(palette.__dict__,OUT=OUT,save=save);exec(source,env);env['borrowers']()
 windows=json.loads((OUT/'byte-borrowers.json').read_text())
 save(OUT/'borrowers.json',dict(result='PASS',cases=rows,bulk=dict(pairwise_disjoint_native_bytes=8041,seed_word0_seconds_pairs=16777216,bounds=65536,profiles=['L1','composed-native-owner']),byte_window_cases=len(windows['cases']),scope='Actual L1/native-owner full RAM/Regs/Devices and ordered physical byte-store prefixes; time callback and failure preserve a live mutation, numeric high-byte alias; complete seed word0/seconds product plus full bound sweep; live far-copy/decimal/streaming palette windows. ICE code/table aliasing deferred, not newly admitted.'))

def defects(ROOT,OUT,bounded,save,snapshot,previous):
 import difftest,wholegame
 m=difftest.Machine();reference=load(OUT/'api/trace/reference/api.dll');rows=[]
 mutations=[
 ('whole-seed-word',('random_bridge.c','rng_write8(r->cs,G(RandomSecondsSeedByte),(uint8_t)(state.word[0]>>8));','rng_write16(r->cs,G(RandomStateWord0),(uint16_t)(state.word[0]&0xff00u));'),'SeedRandomFromDosSeconds',320,False),
 ('reordered-recurrence-stores',('random_bridge.c','    rng_write16(r->cs,G(RandomStateWord1),state.word[1]);','    rng_write16(r->cs,G(RandomStateWord0),state.word[0]);\n    rng_write16(r->cs,G(RandomStateWord1),state.word[1]);'),'NextRandomBelowAx',320,False),
 ('skip-zero-bound',('random_bridge.c','    RandomState state=random_project(r);','    if(!r->ax)return UGH_OK;\n    RandomState state=random_project(r);'),'NextRandomBelowAx',0,False),
 ('extra-rain-prewarm-draw',('water_weather_bridge.c',' int status=PIXEL_CALL(NextRandomBelowAx,ret);',' uint16_t held_bound=r->ax;int extra_status=PIXEL_CALL(NextRandomBelowAx,ret);if(extra_status)return extra_status;r->ax=held_bound;\n int status=PIXEL_CALL(NextRandomBelowAx,ret);'),'RespawnRainParticle',0,False),
 ('stale-parent-reseed',('random_bridge.c','    RandomState state=random_project(r);\n    RandomDosTime time=', '    RandomState state=random_project(r);state.word[0]=(uint16_t)((state.word[0]&0xff00u)|3u);\n    RandomDosTime time='),'SeedRandomFromDosSeconds',0,True)]
 from closure_support import function
 next_body=function((ROOT/'native/bridge/random_bridge.c').read_text(),'c_NextRandomBelowAx')
 word0='    rng_write16(r->cs,G(RandomStateWord0),state.word[0]);\n'
 word1='    rng_write16(r->cs,G(RandomStateWord1),state.word[1]);\n'
 reordered=next_body.replace(word0,'').replace(word1,word0+word1)
 mutations[1]=('reordered-recurrence-stores',('random_bridge.c',next_body,reordered),'NextRandomBelowAx',320,False)
 seed=function((ROOT/'native/bridge/random_bridge.c').read_text(),'c_SeedRandomFromDosSeconds')
 stale=seed.replace('{','{RandomState before_time=random_project(r);',1).replace('RandomState state=random_project(r);','for(unsigned i=0;i<4;i++)rng_write16(r->cs,(uint16_t)(G(RandomStateWord0)+2*i),before_time.word[i]);\n    RandomState state=before_time;')
 mutations[-1]=('stale-parent-reseed',('random_bridge.c',seed,stale),'SeedRandomFromDosSeconds',0,True)
 text=(ROOT/'native/random.c').read_text();old='sum=(uint32_t)state->word[1]+first+(sum>>16);\n    state->word[1]=(uint16_t)sum;\n    sum=(uint32_t)state->word[2]+state->word[1]+(sum>>16);\n    state->word[2]=(uint16_t)sum;'
 new='sum=(uint32_t)state->word[2]+state->word[1]+(sum>>16);\n    state->word[2]=(uint16_t)sum;\n    sum=(uint32_t)state->word[1]+first+(sum>>16);\n    state->word[1]=(uint16_t)sum;'
 assert text.count(old)==1
 mutations.append(('reordered-recurrence',('random.c',old,new),'NextRandomBelowAx',320,False))
 # The zero test inserts only into NextRandomBelowAx, not both seed/project sites.
 for name,mutation,entry,bound,mutate in mutations:
  if name=='skip-zero-bound':mutation=(mutation[0],'EXPORT int c_NextRandomBelowAx(Regs *r) {','EXPORT int c_NextRandomBelowAx(Regs *r) {if(!r->ax)return UGH_OK;')
  path=compile_trace(ROOT,OUT,bounded,'mutant-'+name,mutation);modern=load(path)
  setup(m)
  if entry=='RespawnRainParticle':
   m.ww('DGROUP:WaterYPixels',191);m.ww('DGROUP:VgaRowStrideBytes',96);m.wb('DGROUP:LevelRainDirection',1)
  got=pair(m,[reference,modern],entry,bound,mutate=mutate);assert got[0]!=got[1],(name,'survived')
  if name=='reordered-recurrence-stores':assert got[0][:4]==got[1][:4] and len(got[0][4])==len(got[1][4]) and got[0][4]!=got[1][4],'store-order control must have equal returned state and store count'
  rows.append(dict(defect=name,result='DETECTED',case=entry,observation='ordered store prefixes' if name=='reordered-recurrence-stores' else 'full RAM/registers/Devices/service/store sequence'))
 # Missed serialization in the independent router and a composed host.
 folder=OUT/'defects';folder.mkdir(exist_ok=True);exe=folder/'serialize.exe'
 bounded([previous.timing.common.GCC,'-O2','-std=c11','-DRNG_TEST_FAULT=1','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/random_world_router.c',ROOT/'native/random_world.c',ROOT/'native/bridge/random_world_bridge.c'],'defect-serialize-compile')
 capture=folder/'capture.py';capture.write_text('import json,subprocess,sys\nr=subprocess.run(sys.argv[1:],capture_output=True,text=True);print(json.dumps(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)))\n')
 a=json.loads(bounded([sys.executable,capture,exe],'defect-serialize-run')['stdout']);assert a['returncode']==88 and 'missed serialization' in a['stderr']
 rows.append(dict(defect='missed-serialization',result='DETECTED',scope='Independent compiled router',exit=88))
 target=snapshot();generated=folder/'host-missed-serialization';hostcapture=previous.copy_host(target,generated)
 p=generated/'tools/hostbuild.py';text=p.read_text();needle="return (['-DUGH_NATIVE_RANDOM']";assert text.count(needle)==1;p.write_text(text.replace(needle,"return (['-DRNG_TEST_FAULT=1','-DUGH_NATIVE_RANDOM']",1))
 bounded([sys.executable,'tools/hostbuild.py'],'defect-host-serialization-build',generated)
 script=target/'tests/scenarios/gameplay-adlib.txt';a=json.loads(bounded([sys.executable,hostcapture,generated/'build/host/ugh.exe','--headless','48','--script',script,'--timeout','590'],'defect-host-serialization-run')['stdout'])
 assert a['returncode']==88 and 'missed serialization' in a['stderr'];rows.append(dict(defect='missed-serialization',result='DETECTED',scenario='gameplay-adlib',frame=1,exit=88))
 save(OUT/'defects.json',dict(result='PASS',controls=rows,scope='Actual generated bridge seams; ordered prefix oracle detects changed publication order even when returned state agrees. Extra rain request and stale-parent time reply controls are nonempty. Maintained native algorithms unchanged.'))
