"""Timer/lifetime/logical-clock first ownership cut; generated-copy evidence.
Cold import once, sealed RAM thereafter, native owner serialization. Serial
600-second/8-GiB children; only a committed archive receives scratch promotion.
"""
import argparse,ctypes as C,hashlib,io,json,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/workers/close-adlx-22'
sys.path.insert(0,str(ROOT/'tools'))
import entry_retirement as common
common.OUT=OUT
bounded=common.bounded
save=common.save
sha=common.sha
BASE_FILES=['native/timing_world.c','native/timing_world.h','native/audio_bytes.h','native/audio.h','native/adlx_loader.c','native/adlx_sections.c','native/bridge/timing_world_bridge.c','native/bridge/timing_world_bridge.h',
'native/bridge/timer_bridge.c','native/bridge/timer_lifetime_bridge.c','native/bridge/music_clock_bridge.c',
'host/main.c','host/digest.c','tools/hostbuild.py','verif/standalone_census.py','verif/projector_evidence.py',
'verif/projector/observer.c','verif/projector/timing_serializer.h','verif/timing_composition.py']
def locks(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'locks',locals())
def files():
 modified=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
 return sorted(set(BASE_FILES+modified+['metadata/closure/timing_world.json']))
def snapshot():
 target=OUT/'baseline';revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 marker=target/'.composition-revision'
 if target.exists() and (not marker.exists() or marker.read_text()!=revision):
  assert target.resolve().is_relative_to(OUT.resolve()) and target.name=='baseline'
  shutil.rmtree(target)
 # Restore all committed inputs on every overlay, including a certificate
 # whose temporary lock note was removed by the final fixed-point pass.
 raw=subprocess.check_output(['git','archive','--format=tar',revision],cwd=ROOT)
 with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
  for member in archive.getmembers():
   if not member.isfile():continue
   p=(target/member.name).resolve();assert p.is_relative_to(target.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(archive.extractfile(member).read())
 marker.write_text(revision)
 for f in files():
  p=target/f;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,p)
 p=target/'metadata/closure/timing_world.json';c=json.loads(p.read_text());c['status']='migrated';save(p,c)
 # This driver is the accepted first-cut profile. The second-cut driver
 # deliberately promotes audio_world after taking this same clean archive.
 p=target/'metadata/closure/audio_world.json'
 if p.exists():
  c=json.loads(p.read_text());c['status']='unanalyzed';save(p,c)
 refs=target/'build/whole';refs.mkdir(parents=True,exist_ok=True)
 for p in (ROOT/'build/whole').glob('*.ref.json'):shutil.copyfile(p,refs/p.name)
 save(target/'build/workers/c-close/call-edges.json',[])
 save(OUT/'baseline.json',dict(revision=revision,overlay={f:sha(ROOT/f) for f in files()}));return target

def build(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'build',locals())

def api(group=None,*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'api',locals())

def router():
 folder=OUT/'router';folder.mkdir(exist_ok=True)
 source=folder/'router.c'
 source.write_text(r'''#include "timing_world_bridge.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
#define machine ugh_mem
static uint8_t expected[UGH_MEM_SIZE],observed[UGH_MEM_SIZE];
static uint16_t word(uint16_t bank,uint16_t offset){unsigned a=lin(bank,offset);return (uint16_t)(expected[a]|expected[a+1]*256u);}
int c_ChainSavedTimerInterrupt(Regs *r){(void)r;return 0;}
int c_AdvanceMusicFade(Regs *r){(void)r;return 0;}
int c_TickAdlxPlayback(Regs *r){(void)r;return 0;}
int c_ClearSoundState(Regs *r){(void)r;return 0;}
int c_HandleTimerInterrupt(Regs *r){(void)r;return 0;}
int main(void){
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)machine[a]=(uint8_t)((a*193u+(a>>8)*73u)^0x9d);
 machine[lin(DATA_SEG,D(LastActiveTimerSlotOffset))]=30;machine[lin(DATA_SEG,D(LastActiveTimerSlotOffset))+1]=0;
 memcpy(expected,machine,sizeof expected);timing_cold_import(machine);
 if(timing_owned_bytes()!=320)return 1;
 unsigned addresses[320],n=0;for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(timing_is_owned(a))addresses[n++]=a;
 memcpy(observed,machine,sizeof observed);timing_serialize(observed);
 if(memcmp(observed,expected,sizeof observed))return 2;
 NativeTimingWorld *owner=native_timing_world();
 if(owner->music.ticks!=(word(SOUND_SEG,S(AdlxTickCount))|(uint32_t)word(SOUND_SEG,S(AdlxTickHighWord))*65536u))return 10;
 if(owner->music.origin!=(word(SOUND_SEG,S(MainAdlxTimeOrigin))|(uint32_t)word(SOUND_SEG,S(MainAdlxTimeOriginHigh))*65536u))return 11;
 if(owner->music.rate!=word(SOUND_SEG,S(MusicTicksPerUnit)) || owner->music.playing!=word(SOUND_SEG,S(MainAdlxPlaying)) || owner->music.section_loop!=word(SOUND_SEG,S(MainAdlxSectionLoopEnabled)))return 12;
 TimerState state;uint16_t fragments[32];if(!timing_snapshot(&state,fragments) || state.count!=16)return 13;
 if(state.quantum!=(word(DATA_SEG,D(NextPitQuantumLow))|(uint32_t)word(DATA_SEG,D(NextPitQuantumHigh))*65536u) || state.earliest!=(word(DATA_SEG,D(EarliestTimerIntervalLow))|(uint32_t)word(DATA_SEG,D(EarliestTimerIntervalHigh))*65536u))return 19;
 if(state.installed!=word(TIMER_SEG,T(TimerInterruptInstalled)) || state.programmed_divisor!=word(DATA_SEG,D(ProgrammedPitDivisor)))return 20;
 for(unsigned i=0;i<16;i++){
  if(state.slots[i].interval!=(word(DATA_SEG,(uint16_t)(D(TimerIntervalLowBySlot)+i*2))|(uint32_t)word(DATA_SEG,(uint16_t)(D(TimerIntervalHighBySlot)+i*2))*65536u))return 14;
  if(state.slots[i].remaining!=(word(DATA_SEG,(uint16_t)(D(TimerRemainingLowBySlot)+i*2))|(uint32_t)word(DATA_SEG,(uint16_t)(D(TimerRemainingHighBySlot)+i*2))*65536u))return 15;
  if(state.slots[i].due!=word(DATA_SEG,(uint16_t)(D(TimerCallbackDueBySlot)+i*2)) || state.slots[i].handle!=word(DATA_SEG,(uint16_t)(D(TimerHandleBySlot)+i*2)) || state.by_handle[i]!=word(DATA_SEG,(uint16_t)(D(TimerSlotOffsetByHandle)+i*2)))return 16;
  if(fragments[i*2]!=word(DATA_SEG,(uint16_t)(D(TimerCallbackOffsetBySlot)+i*4)) || fragments[i*2+1]!=word(DATA_SEG,(uint16_t)(D(TimerCallbackSegmentBySlot)+i*4)))return 17;
 }
 state.slots[14].interval=0x12345678;state.installed^=0xffff;timing_commit(&state,fragments);
 unsigned low=lin(DATA_SEG,D(TimerIntervalLowBySlot)+28),high=lin(DATA_SEG,D(TimerIntervalHighBySlot)+28);
 expected[low]=0x78;expected[low+1]=0x56;expected[high]=0x34;expected[high+1]=0x12;
 timing_serialize(observed);if(memcmp(observed,expected,sizeof observed))return 18;
 unsigned writes=0;
 for(unsigned i=0;i<n;i++)for(unsigned value=0;value<256;value++){
  unsigned a=addresses[i];if(!timing_shared_write(a,(uint8_t)value))return 3;
  expected[a]=(uint8_t)value;timing_serialize(observed);
  for(unsigned j=0;j<n;j++)if(observed[addresses[j]]!=expected[addresses[j]])return 4;
  uint8_t read;if(!timing_shared_read(a,&read) || read!=value)return 5;
  if(audio_borrowed_byte(machine,a)!=value || audio_borrowed_byte(machine+(a&~15u),a&15u)!=value)return 21;
  if(!(a&15u) && a>=65536 && audio_borrowed_byte(machine+a-65536,65536)!=value)return 22;
  if(timing_check_serialization(observed)!=UINT32_MAX)return 6;
  timing_require_seal(machine);writes++;
 }
 observed[addresses[7]]^=1;if(timing_check_serialization(observed)!=addresses[7])return 7;
 unsigned words=0;
 for(unsigned position=0;position<32;position++)for(unsigned word=0;word<65536;word++){
  unsigned a=lin(DATA_SEG,(uint16_t)(D(TimerCallbackOffsetBySlot)+position*2));
  timing_shared_write(a,(uint8_t)word);timing_shared_write(a+1,(uint8_t)(word>>8));
  expected[a]=(uint8_t)word;expected[a+1]=(uint8_t)(word>>8);
  uint8_t low,high;timing_shared_read(a,&low);timing_shared_read(a+1,&high);
  if((unsigned)(low|high*256u)!=word)return 8;
  if(!(word&255u)){
   timing_serialize(observed);
   for(unsigned j=0;j<n;j++)if(observed[addresses[j]]!=expected[addresses[j]])return 9;
  }
  words++;
 }
 printf("{\"owned_bytes\":%u,\"byte_writes\":%u,\"callback_word_roundtrips\":%u,\"canonical_control\":true}\n",n,writes,words);
 return 0;
}
''')
 exe=folder/'router.exe';bounded([common.GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-fwrapv','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,source,ROOT/'native/timing_world.c',ROOT/'native/bridge/timing_world_bridge.c'],'router-compile')
 row=bounded([exe],'router');save(OUT/'router.json',dict(result='PASS',counts=json.loads(row['stdout'])))

def corpus():
 import struct
 import nbuild,dataprobe,difftest
 from emu import Machine,LOAD
 import contacts_reference
 contacts_reference.OUT=OUT/'corpus-reference'
 contacts_reference.prepare_reference(local=True)
 dataprobe.IMAGE=contacts_reference.expanded_image(local=False);dataprobe.OUT=OUT/'format'
 streams=dataprobe.music(dataprobe.validate())
 dlls=[nbuild.load_l1(OUT/'api'/p/'api.dll') for p in ['reference','composed']]
 m=Machine();basecase=difftest.load_suite('adlib').base;rows=[]
 for effects in [False,True]:
  for stream in streams:
   frame=int(stream['frame'],16)
   configs=[(stream['channels'],8,0,1),(stream['channels'],9,1,1),(stream['channels'],10,1,2),(stream['channels'],11,0,1),(stream['channels'],8,1,1),(stream['channels'],11,1,0)] if effects else [(0,12,1,1),(2,12,1,1),(9,12,1,1),(0x10,13,0,1),(0x101,12,1,1),(10,12,1,1),(2,13,0,2)]
   for reserved,slot,playing,repeat in configs:
    m.reset();basecase(m)
    for key,value in dict(CurrentAdlxSlot=slot,ReservedAdlibChannelCount=reserved,MainAdlxPlaying=playing,
      MainAdlxFlags=1,MainAdlxRepeatCount=repeat,MainAdlxStartPointer=42,MainAdlxStartSegment=frame+LOAD,
      MainAdlxCursor=42,MainAdlxCursorSegment=frame+LOAD,AdlxTickCount=0xfffc,AdlxTickHighWord=0xffff,
      MainAdlxDeadlineLow=0xfffc,MainAdlxDeadlineHigh=0xffff).items():m.ww('SOUND:'+key,value)
    effect=m.off('SOUND:AudioChannelStates')+slot*42
    if effects:
     m.ww('SOUND:SoundDeviceBits',1);m.ww('SOUND:MusicVoiceCount',9);m.ww('SOUND:AdlxTimerPeriod',0x7fff if slot==11 else 100 if slot==8 and playing else 0x1843 if playing else 0)
     m.ww('SOUND:CurrentAdlxRecordOffset',effect)
     for field,value in [(4,repeat),(6,42),(8,frame+LOAD),(16,42),(18,frame+LOAD),(28,0xc8),(30,0xfffc),(32,0xffff),(34,stream['channels']),(36,9-reserved),(38,256),(40,5 if repeat else 7)]:
      m.write(m.seg('SOUND:AudioChannelStates'),effect+field,struct.pack('<H',value))
    routine='RunEffectAdlxEvents' if effects else 'RunMainAdlxEvents'
    initial=m.prepare('SOUND:'+routine,difftest.POISON,'far',(),0x602)
    for dll in dlls:
     C.memmove(dll.ugh_memory().contents,m.snapshot(),difftest.MEM_SIZE);dll.ugh_devices_reset();dll.api_begin()
    states=[difftest.Regs(**{n.lower():v for n,v in initial.items()}) for _ in dlls]
    sound=m.seg('SOUND:MainAdlxFlags')*16
    status_at=effect+40 if effects else m.off('SOUND:MainAdlxFlags')
    cursor=effect+16 if effects else m.off('SOUND:MainAdlxCursor')
    bank=effect+18 if effects else m.off('SOUND:MainAdlxCursorSegment')
    ordered=[];passes=0
    for burst in range(1,20001):
     logs=[]
     for dll,r in zip(dlls,states):
      memory=dll.ugh_memory().contents;r.di=memory[sound+cursor]|memory[sound+cursor+1]<<8;r.es=memory[sound+bank]|memory[sound+bank+1]<<8
      dll.ugh_device_state().contents.count=0
      fn=getattr(dll,'api_c_'+routine);fn.argtypes=[C.POINTER(difftest.Regs)];fn.restype=C.c_int
      assert fn(C.byref(r))==0,(frame,effects,reserved,burst)
      dev=dll.ugh_device_state().contents;assert not dev.error
      logs.append([(e.kind,e.port,e.size,e.value) for e in dev.log[:dev.count]])
     assert logs[0]==logs[1],(frame,effects,reserved,burst,'ordered OPL/ports')
     ordered.extend(logs[0])
     left,right=[bytes(d.ugh_memory().contents) for d in dlls]
     lo=initial['SS']*16;hi=lo+initial['SP']
     assert left[:lo]==right[:lo] and left[hi:]==right[hi:],(frame,effects,reserved,burst,'RAM')
     for name in ['ax','bx','cx','dx','si','di','bp','ds','es','ss','sp']:
      assert getattr(states[0],name)==getattr(states[1],name),(frame,effects,reserved,burst,name)
     assert states[0].flags&0x600==states[1].flags&0x600
     if effects and left[sound+cursor]==42 and left[sound+cursor+1]==0:passes+=1
     if not left[sound+status_at]&1:break
     if effects and not repeat and passes==2:break
    else:raise AssertionError((frame,effects,'20000-burst bound'))
    rows.append(dict(frame=stream['frame'],effects=effects,reserved=reserved,slot=slot,playing=playing,repeat=repeat,bursts=burst,outcome='two infinite-repeat passes' if effects and not repeat else 'END',ports=len(ordered),ordered_sha256=hashlib.sha256(json.dumps(ordered).encode()).hexdigest()))
 save(OUT/'corpus.json',dict(result='PASS',streams=len(streams),configurations=rows,scope='Every shipped ADLX resource in main/effect roles, persistent native owner between bursts; full RAM observations and ordered ports versus independent compiled L1. END or two infinite-repeat passes within 20000 bursts.'))
 print('corpus PASS',len(streams),'resources',len(rows),'configurations',flush=True)

def lifetime():
 import nbuild
 from difftest import Regs,MEM_SIZE
 from emu import Machine
 dlls=[nbuild.load_l1(OUT/'api'/p/'api.dll') for p in ['reference','composed']]
 m=Machine();rows=[]
 callback_type=C.CFUNCTYPE(C.c_int,C.c_uint8,C.POINTER(Regs))
 for dll in dlls:
  dll.api_live_word.argtypes=[C.c_uint16,C.c_uint16];dll.api_live_word.restype=C.c_uint16
  dll.api_live_store.argtypes=[C.c_uint16,C.c_uint16,C.c_uint16]
 for name in ['InstallTimerInterrupt','RestoreTimerInterrupt']:
  for foreign in [False,True]:
   for installed in [0,1,0x8000]:
    for fail in [False,True]:
     m.reset();bank=0x7500 if foreign else m.seg('TIMER:TimerInterruptInstalled')
     m.ww('TIMER:TimerInterruptInstalled',0x6b31 if foreign else installed)
     m.write(bank,m.off('TIMER:TimerInterruptInstalled'),installed.to_bytes(2,'little'))
     m.ww('DGROUP:PreviousInt08Offset',0x100);m.ww('DGROUP:PreviousInt08Segment',0xf000)
     m.write(0,0x20,b'\x00\x01\x00\xf0')
     initial=m.snapshot();observations=[]
     for dll in dlls:
      C.memmove(dll.ugh_memory().contents,initial,MEM_SIZE);dll.ugh_devices_reset();seen=[]
      def service(number,r,dll=dll):
       if number==0x21:
        seen.append((r.contents.ax,dll.api_live_word(bank,m.off('TIMER:TimerInterruptInstalled'))))
        # A provider mutation at the continuation cut, through the explicit
        # typed shared view, not an output-image or live-RAM repair.
        dll.api_live_store(m.seg('DGROUP:TimerIntervalLowBySlot'),m.off('DGROUP:TimerIntervalLowBySlot')+30,0xb4ca)
        if fail:return 1
       return -1
      cb=callback_type(service);dll.ugh_set_interrupt_service(cb)
      r=Regs(cs=bank,ds=0x7340,es=0x7c20,ss=0x9000,sp=0x100,flags=0xed7,ax=0xc123,bx=0x2323,cx=0x3434,dx=0x4545,si=0x5656,di=0x6767,bp=0x7878)
      status=getattr(dll,'api_c_'+name)(C.byref(r));dev=dll.ugh_device_state().contents
      observations.append((status,bytes(r),bytes(dll.ugh_memory().contents),bytes(dev),seen))
      dll.ugh_set_interrupt_service(callback_type())
     assert observations[0]==observations[1],(name,foreign,installed,fail)
     rows.append(dict(entry=name,foreign_code_view=foreign,installed=installed,failed_service=fail,cuts=len(observations[0][4])))
 save(OUT/'lifetime.json',dict(result='PASS',cases=rows,scope='Compiled L1/composed lifetime prefixes, live CS flag views, arbitrary nonzero installed values, provider failure and inactive-slot mutation at DOS cuts; full RAM observations/registers/devices/service order.'))

def proof():
 from closure_support import function
 folder=OUT/'proof';folder.mkdir(exist_ok=True)
 bridge=(ROOT/'native/bridge/timing_world_bridge.c').read_text()
 body=re.search(r'typedef struct TimingBinding.*?} TimingBinding;',bridge,re.S)[0]
 prefix='#include "timing_world.h"\n#include <stddef.h>\nvoid *memcpy(void*d,const void*s,size_t n){unsigned char *a=d;const unsigned char*b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}\n#include "'+(ROOT/'native/timing_world.c').as_posix()+'"\n'
 prefix+='void __CPROVER_assert(int,const char*);void __CPROVER_assume(int);\n#define assert(c) __CPROVER_assert((c),#c)\n'
 prefix+='static uint8_t ugh_mem[1];\n'
 prefix+=body+'\nstatic TimingBinding bindings[1];static uint16_t at[2]={1,1},previous[2];static unsigned long long shared_writes;\n'
 prefix+='static uint16_t token_word(uint16_t v,const uint16_t*p){(void)v;(void)p;assert(0);return 0;}\nstatic uint16_t word_token(uint16_t v,unsigned p){(void)v;(void)p;assert(0);return 0;}\nstatic uint16_t open_words[32];\nint timing_is_owned(uint32_t a){return a<2;}\n'
 prefix+=''.join(function(bridge,n) for n in ['get','put','timing_shared_write'])
 main=r'''uint32_t nondet_word(void);uint8_t nondet_byte(void);unsigned nondet_unsigned(void);
int main(void){
 NativeTimingWorld *w=native_timing_world();native_timing_reset();
 uint32_t old=nondet_word();uint8_t byte=nondet_byte();unsigned address=nondet_unsigned();
 __CPROVER_assume(address<2);unsigned wide=nondet_unsigned();__CPROVER_assume(wide<2);
 unsigned half=nondet_unsigned();__CPROVER_assume(half<2);if(!wide)half=0;
 w->last_offset=6;w->timer.count=4;
 w->music.ticks=old;w->music.rate=(uint16_t)old;
 uint16_t initial_rate=w->music.rate;uint32_t initial_ticks=w->music.ticks;
 bindings[0]=(TimingBinding){0,wide?(size_t)((uint8_t*)&w->music.ticks-(uint8_t*)w):(size_t)((uint8_t*)&w->music.rate-(uint8_t*)w),wide?4:2,half*16,0,0};
 uint32_t expected=wide?old:(uint16_t)old;unsigned shift=half*16+address*8;
 expected=(expected&~(255u<<shift))|((uint32_t)byte<<shift);
 assert(timing_shared_write(address,byte)==1);
 if(wide){assert(w->music.ticks==expected);assert(w->music.rate==initial_rate);}
 else {assert(w->music.rate==(uint16_t)expected);assert(w->music.ticks==initial_ticks);}
 assert(get(&bindings[0])==(uint16_t)(expected>>(half*16)));
 assert(w->timer.count==4 && w->last_offset==6 && shared_writes==1);
 assert(!w->music.origin && !w->music.playing && !w->music.section_loop);
 assert(!w->timer.quantum && !w->timer.earliest && !w->timer.installed);
}
'''
 harness=folder/'field.c';harness.write_text(prefix+main)
 bounded([common.GCC,'-E','-P','-nostdinc','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',harness,'-o',folder/'field.i'],'proof-preprocess')
 tool=Path(json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe'])
 result=bounded([tool,folder/'field.i','--unwind','8','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-fields')
 assert 'VERIFICATION SUCCESSFUL' in result['stdout']
 save(OUT/'proof.json',dict(result='PASS',scope='Actual get/put/shared-write C, numeric 16/32-bit fields and either word/byte lane, arbitrary old value and byte. Frame/dependence; callback token fields separately enumerated, no timer algorithm proof widened.',preprocessed_sha256=sha(folder/'field.i')))

def reuse():
 folder=OUT/'reuse';folder.mkdir(exist_ok=True);rows=[]
 for rel in ['native/bridge/timer_bridge.c','native/bridge/timer_lifetime_bridge.c','native/bridge/music_clock_bridge.c','native/adlx_loader.c','native/adlx_sections.c']:
  name=Path(rel).name
  before=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT,text=True)
  texts=[before,(ROOT/rel).read_text()];tokens=[]
  for index,text in enumerate(texts):
   text=re.sub(r'#include "([^"]+)"',lambda m:'#include "'+str((ROOT/rel).parent.joinpath(m[1]).resolve()).replace('\\','/')+'"' if (ROOT/rel).parent.joinpath(m[1]).is_file() else m[0],text)
   source=folder/(str(index)+'-'+name);source.write_text(text);output=source.with_suffix('.i')
   bounded([common.GCC,'-E','-P','-I',ROOT/'c',source,'-o',output],'reuse-'+str(index)+'-'+name)
   tokens.append(re.findall(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\w+|[^\s]',output.read_text()))
  assert tokens[0]==tokens[1],name
  rows.append(dict(file=rel,legacy_preprocessed_tokens_identical=True,token_sha256=hashlib.sha256(json.dumps(tokens[0]).encode()).hexdigest()))
 pure=[]
 for p in sorted((ROOT/'native').glob('*.c')):
  if p.name.startswith(('adlx_','music_clock','timer')) and p.name not in ['adlx_loader.c','adlx_sections.c']:
   old=subprocess.check_output(['git','show','HEAD:'+p.relative_to(ROOT).as_posix()],cwd=ROOT)
   assert old.replace(b'\r\n',b'\n')==p.read_bytes().replace(b'\r\n',b'\n')
   pure.append(p.relative_to(ROOT).as_posix())
 save(OUT/'reuse.json',dict(result='PASS',bridges=rows,pure_sources_unchanged=pure,scope='Legacy preprocessed bridge C and accepted pure algorithm sources unchanged. Existing solver/codec domains are reused without widening; new composed views have separate API, enumeration and proof evidence.'))

def defects():
 target=snapshot();assert target.is_dir();rows=[]
 for fault,label in [(1,'dropped-callback'),(2,'opl-order'),(3,'stale-irq-state'),(4,'missed-serialization')]:
  folder=OUT/'defects'/label
  for top in ['c','native','host','metadata','tools','verif','src']:shutil.copytree(target/top,folder/top,dirs_exist_ok=True)
  shutil.copytree(target/'build/link',folder/'build/link',dirs_exist_ok=True)
  p=folder/'native/bridge/timing_world_bridge.c'
  p.write_text('#define TIMING_TEST_FAULT '+str(fault)+'\n'+(target/'native/bridge/timing_world_bridge.c').read_text())
  if fault==2:
   p=folder/'c/platform.c';text=(target/'c/platform.c').read_text()
   assert text.count('void platform_out(')==1
   text=text.replace('void platform_out(','void platform_device_out(',1)
   text+=r'''
extern int timing_audio_callback_active(void);
void platform_out(uint16_t port,unsigned size,uint32_t value){
 static unsigned pending,done,saved_size;static uint16_t saved_port;static uint32_t saved_value;
 if(!done && timing_audio_callback_active() && (port==0x388 || port==0x389)){
  if(!pending){pending=1;saved_port=port;saved_size=size;saved_value=value;return;}
  platform_device_out(port,size,value);platform_device_out(saved_port,saved_size,saved_value);done=1;pending=0;return;
 }
 platform_device_out(port,size,value);
}
'''
   p.write_text(text)
  bounded([sys.executable,'tools/hostbuild.py'],'defect-build-'+label,folder)
  scenario=target/'tests/scenarios/gameplay-adlib.txt'
  run=bounded([folder/'build/host/ugh.exe','--headless','48','--script',scenario,'--timeout','590'],'defect-run-'+label) if fault!=4 else None
  if fault==4:
   # A missed publication is a diagnostic stop, never a repaired image.
   from windows_job import WindowsJob,ExtendedLimits
   # Reuse the bounded runner's expected-failure capture through a tiny child.
   checker=OUT/'defects'/'capture.py';checker.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n')
   result=bounded([sys.executable,checker,folder/'build/host/ugh.exe','--headless','979','--script',scenario,'--timeout','590'],'defect-run-'+label)
   failed=json.loads(result['stdout']);assert failed['returncode']!=0 and 'missed owned serialization' in failed['stderr']
   rows.append(dict(defect=label,result='DETECTED',failure=failed));continue
  actual=[json.loads(line) for line in run['stdout'].splitlines()]
  expected=json.loads((ROOT/'build/whole/gameplay-adlib.ref.json').read_text())['frames']
  mismatch=next((i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b),None)
  assert mismatch is not None,(label,'vacuous control')
  rows.append(dict(defect=label,result='DETECTED',scenario='gameplay-adlib',frame=mismatch))
 save(OUT/'defects.json',dict(result='PASS',controls=rows))

def census(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'census',locals())

def census_result():
 target=OUT/'baseline'
 j=json.loads((target/'build/workers/close-adlx-19/census.json').read_text())
 assert not [f for f in j['functions'] if f['kind']=='c' and f.get('entry')]
 assert sum(s['fallback_calls'] for s in j['scenarios'])==0
 island={'native/bridge/timer_bridge.c','native/bridge/timer_lifetime_bridge.c','native/bridge/music_clock_bridge.c','native/bridge/timing_world_bridge.c'}
 internal=[];outside=[];irq=[]
 for path in sorted((target/'build/workers/close-adlx-19/detail').glob('*.json')):
  run=json.loads(path.read_text())
  for edge in run['machine_edges']:
   if edge['kind']=='ABI-entry':continue
   if edge['kind']=='interrupt-delivery':
    irq.append(dict(scenario=run['scenario'],**edge));continue
   if edge['bridge']['path'] in island:
    row=dict(scenario=run['scenario'],**edge)
    target_owner=edge['target'].get('owner')
    (internal if target_owner in island or target_owner in {'timer','timer_lifetime','music_clock','timing_world'} else outside).append(row)
 assert not internal,internal[:3]
 assert irq,'No IRQ delivery was observed'
 assert any(f['name']=='c_HandleTimerInterrupt' and f['kind']=='bridge' and f['count'] for f in j['functions'])
 save(OUT/'census.json',dict(result='PASS',summary=j,internal_island_machine_edges=internal,incoming_platform_irq_edges=irq,outgoing_service_or_remaining_audio_edges=outside))

def projector(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'projector',locals())

def audit():
 # Preserve the earlier census's incomplete model and exact access expressions.
 # Arbitrary byte aliases are serviced, not assigned an invented symbolic owner.
 source=ROOT/'native/bridge/timing_world_bridge.c'
 body=source.read_text().split('static void define_bindings(void)')[1].split('static uint16_t get(')[0]
 names=sorted(set(re.findall(r'(?:D|S|T)\((\w+)\)',body)));assert len(names)==25
 prior=OUT/'baseline/build/workers/close-adlx-19/static.json'
 j=json.loads(prior.read_text());rows=[]
 for name in names:
  rows.append(dict(symbol=name,model=j['variables'].get(name,'No separate model cell; retained explicit high-word binding'),
    borrowed_accesses=[dict(component=b['component'],bridge=b['bridge'],access=b['ram_symbols'][name]) for b in j['bridges'] if name in b['ram_symbols']]))
 current=[]
 for p in sorted((ROOT/'native/bridge').glob('*')):
  if p.suffix not in ['.c','.h']:continue
  hits=[dict(line=i+1,text=line.strip()) for i,line in enumerate(p.read_text().splitlines()) if any(re.search(r'\b'+n+r'\b',line) for n in names)]
  if hits:current.append(dict(file=p.relative_to(ROOT).as_posix(),expressions=hits))
 save(OUT/'borrowers.json',dict(result='PASS',source_census_sha256=sha(prior),source_sha256=sha(source),named_cells=25,
  before=dict(canonical_native_owned_bytes=0,observation_model_typed=269,model_total=392),
  after=dict(canonical_native_owned_bytes=320,timer_bytes=306,logical_music_clock_bytes=14,provider_saved_binding_bytes_in_timer=4,observation_model_typed=269,model_total=392,native_owned_baseline_bytes=0,native_owned_journal_bytes=0),
  routes=['Timer/clock/lifetime entry adapters directly borrow NativeTimingWorld',
   'Other bridge rd/wr accesses use an explicit generated memory-service typed byte view; never RAM resynchronization',
   'Pure loader/section byte windows use audio_borrowed_byte in composition only, including raw source aliases',
   'Unknown aliases retain their source expressions and model completeness=false; raw writes to sealed bytes stop'],
  rows=rows,current_symbol_expressions=current))

def finalize(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'finalize',locals())

def main(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'main',locals())
# Scheduled by world_gate; no private CLI.
