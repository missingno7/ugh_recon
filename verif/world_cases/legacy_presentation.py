"""Step 4 completion: native HUD/history and weather/rain ownership.
Serial 600-second / 8-GiB children, scratch promotion, pure literal comparator.
"""
import argparse,ctypes as C,hashlib,inspect,io,json,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/workers/close-stones-22'
sys.path.insert(0,str(ROOT/'tools'))
import pixel_composition as pixels
pages=pixels.pages;prior=pixels.prior;palette=pixels.palette;audio=pixels.audio;timing=pixels.timing
pixels.OUT=pages.OUT=prior.OUT=palette.OUT=audio.OUT=timing.OUT=timing.common.OUT=OUT
bounded=pixels.bounded;save=pixels.save;sha=pixels.sha
NEW=['native/presentation_world.h','native/presentation_world.c','native/bridge/presentation_world_bridge.h','native/bridge/presentation_world_bridge.c']
BASE=NEW+['native/bridge/water_weather_bridge.c','verif/presentation_composition.py','tools/hostbuild.py','host/main.c','verif/projector/observer.c','verif/projector/timing_serializer.h','verif/projector/publications.py','verif/projector_evidence.py']
READ=list(dict.fromkeys(pixels.READ+['verif/pixel_composition.py','metadata/closure/pixel_world.json','native/hud.c','native/hud.h','native/water_weather.c','native/water_weather.h','native/session.c','native/session.h','native/bridge/hud_bridge.c','native/bridge/hud_support.h','native/bridge/session_bridge.c','native/bridge/menus_bridge.c','native/bridge/high_scores_bridge.c','src/data/DGDATA.ASM']))
NAMES=['InitializeLevelDisplay','LoadCurrentLevelState','RefreshHudAndTimerBar','DrawHudDigit','DrawHudDigitAndAdvance','RedrawChangedTwoDigitNumber','RedrawChangedFourDigitNumber','RedrawChangedSixDigitNumber','AdvanceWaterSurface','DrawWaterSurface','DrawWaterSurfaceFrame0','DrawWaterSurfaceFrame1','DrawWaterSurfaceFrame2','AdvanceRainParticles','RespawnRainParticle','DrawRainParticles','RestoreRainBackground','EncodeTwoDecimalDigits','EncodeFourDecimalDigits','EncodeSixDecimalDigits','ShowLevelIntroduction','TestHighScoreQualification']
TOTAL=7660
REGIONS=[(0xc8,14),(0x27a2,6),(0x27ac,35),(0x2800,4),(0x2905,4),(0x2e8b,1158)]

def files():return sorted(set(BASE+subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()+['metadata/closure/presentation_world.json']))

def snapshot():
 revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();target=OUT/'baseline'
 raw=subprocess.check_output(['git','archive','--format=tar',revision],cwd=ROOT)
 with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
  for member in tar.getmembers():
   if not member.isfile():continue
   p=(target/member.name).resolve();assert p.is_relative_to(target.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(tar.extractfile(member).read())
 for f in files():p=target/f;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,p)
 p=target/'metadata/closure/presentation_world.json';c=json.loads(p.read_text());c['status']='migrated';save(p,c)
 for bank in ['whole','levels','levels-audio','levels-deep']:
  dest=target/'build'/bank;dest.mkdir(parents=True,exist_ok=True)
  for p in (ROOT/'build'/bank).glob('*.ref.json'):shutil.copyfile(p,dest/p.name)
 save(target/'build/workers/c-close/call-edges.json',[])
 save(OUT/'baseline.json',dict(revision=revision,overlay={f:sha(ROOT/f) for f in files()}));return target
pixels.snapshot=pages.snapshot=prior.snapshot=palette.snapshot=audio.snapshot=timing.snapshot=snapshot
build=palette.build;levels=palette.levels

def relock(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'relock',locals())




def api(group=None,*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'api',locals())

def api_load_cut(text):
 from closure_support import function
 if not re.search(r'EXPORT\s+int\s+c_LoadCurrentLevelState\s*\(Regs\s*\*r\)\s*\{',text):return text
 body=function(text,'c_LoadCurrentLevelState');text=text.replace(body,body.replace('c_LoadCurrentLevelState(','fixture_load_body(',1))
 return text+'\nextern int api_stop_at_load;\nEXPORT int c_LoadCurrentLevelState(Regs *r){if(api_stop_at_load)return UGH_BUDGET;return fixture_load_body(r);}\n'

def extra_weather_cases():
 import difftest
 scene=difftest.load_suite('scene');cases=[]
 for water in [0,1,191,192,65535,32767,32768]:
  for name in ['AdvanceRainParticles','DrawRainParticles','RestoreRainBackground']:
   def setup(m,water=water):
    m.ww('DGROUP:VgaRowStrideBytes',96);m.wb('DGROUP:LevelRainDirection',1);m.ww('DGROUP:WaterYPixels',water)
    m.ww('GAME:DrawPagePointer',0x1000);m.ww('GAME:DrawPagePointer',0xa000,2);m.ww('GAME:BackgroundPagePointer',0x6000);m.ww('GAME:BackgroundPagePointer',0xa000,2)
    m.ww('DGROUP:WaterSurfaceByteOffset',0xffff)
    for n in ['RainParticleOffsets','RainPreviousOffsets','RainParticleXModuloFour']:
     for i in range(193):m.ww('DGROUP:'+n,((i*97)&0x3fff) if n!='RainParticleXModuloFour' else i&3,2*i)
    m.ww('DGROUP:JoystickPresentFlags',0x8001)
   cases.append(difftest.Case(f'{name} water={water:04x} allocation/alias','GAME:'+name,setup=setup,regs=dict(DS=scene.DATA_SEG),out_regs=('AX','BX','CX','DX','SI','DI','BP','IF','DF','CF','PF','ZF','SF','OF'),budget=5_000_000))
 return cases

def proof():
 from closure_support import function
 folder=OUT/'proof';folder.mkdir(exist_ok=True);bridge=(ROOT/'native/bridge/presentation_world_bridge.c').read_text()
 prefix='#include "presentation_world.h"\n#include <stddef.h>\n#include "'+(ROOT/'native/presentation_world.c').as_posix()+'"\n'
 prefix+='void *memcpy(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}\n'
 prefix+=re.search(r'typedef struct PresentationField.*?} PresentationField;',bridge,re.S)[0]+'\n'+''.join(function(bridge,n) for n in ['presentation_field_get','presentation_field_put'])
 prefix+='void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);\n#define assert(c) __CPROVER_assert((c),#c)\n'
 code=r'''NativePresentationWorld nondet_world(void);unsigned nondet_uint(void);uint8_t nondet_byte(void);
int main(void){
 world=nondet_world();unsigned width=nondet_uint(),member=nondet_uint(),index=nondet_uint(),stride=nondet_uint(),lane=nondet_uint(),other=nondet_uint();
 __CPROVER_assume((width==1 || width==2) && index<193 && stride>=width && stride<=6 && lane<width);
 __CPROVER_assume(member<sizeof world && index*stride+member+width<=sizeof world && other<sizeof world);
 unsigned at=member+index*stride;__CPROVER_assume(other<at || other>=at+width);
 PresentationField field={0,member,width,index+1,stride};unsigned position=index*width+lane;
 uint16_t before=0,after=0;if(width==2)memcpy(&before,(uint8_t*)&world+at,2);else before=((uint8_t*)&world)[at];
 uint8_t frame=((uint8_t*)&world)[other],value=nondet_byte();
 assert(presentation_field_get(&field,position)==(uint8_t)(before>>(lane*8)));assert(((uint8_t*)&world)[other]==frame);
 presentation_field_put(&field,position,value);assert(presentation_field_get(&field,position)==value);assert(((uint8_t*)&world)[other]==frame);
 if(width==2){memcpy(&after,(uint8_t*)&world+at,2);assert(after==(uint16_t)((before&~(255u<<(lane*8)))|((unsigned)value<<(lane*8))));}
 else assert(((uint8_t*)&world)[at]==value);
}
'''
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe'];rows=[]
 def run(name,code,unwind):
  source=folder/(name+'.c');source.write_text(code);pre=folder/(name+'.i');bounded([timing.common.GCC,'-E','-P','-nostdinc','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',source,'-o',pre],'proof-'+name+'-preprocess')
  r=bounded([tool,pre,'--unwind',str(unwind),'--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-'+name);assert 'VERIFICATION SUCCESSFUL' in r['stdout'];rows.append(dict(profile=name,source=sha(source),preprocessed=sha(pre)))
 run('fields',prefix+code,3)
 session=(ROOT/'native/session.c').read_text();code='#include "session.h"\n'+''.join(function(session,n) for n in ['session_display_byte','session_display_score'])+r'''
void __CPROVER_assert(int,const char*);
#define assert(c) __CPROVER_assert((c),#c)
uint8_t nondet_byte(void);uint32_t nondet_uint32(void);
int main(void){uint8_t b=nondet_byte();uint32_t s=nondet_uint32();
 uint16_t wide=(uint16_t)b+11;uint8_t low=(uint8_t)(wide&255u);unsigned expected=low<100?low:low-100;
 assert(session_display_byte(b)==expected);
 uint64_t sum=(uint64_t)s+111111u;uint32_t truncated=(uint32_t)(sum&0xffffffffu);
 uint32_t wanted=truncated<=1000000u?truncated:(uint32_t)((uint64_t)truncated+0x100000000ull-1000000u);
 assert(session_display_score(s)==wanted);
 assert(session_display_score(888889u)==1000000u);assert(session_display_score(0xffffffffu)==111110u);
}
'''
 run('seeds',code,2)
 save(OUT/'proof.json',dict(result='PASS',profiles=rows,scope='Actual C numeric strided field get/put: arbitrary complete owner, valid byte/word member, any of 193 records and stride through six bytes, selected-byte output/frame and arbitrary-other-byte frame/dependence. Actual session seed C proved for full byte and 32-bit domains, including wrap, strict equality and single subtraction. Registry/serialization layout independently exhaustively checked in compiled C.'))

def router():
 folder=OUT/'router';folder.mkdir(exist_ok=True)
 code=r'''#include "presentation_world_bridge.h"
#include <stdio.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];uint8_t ugh_read(uint32_t a){return ugh_mem[a];}void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
uint8_t pixel_borrowed_byte(const uint8_t*p,uint32_t i){return p[i];}void pixel_borrowed_store(uint8_t*p,uint32_t i,uint8_t v){p[i]=v;}
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE],wanted[UGH_MEM_SIZE];
static struct {unsigned address;uint16_t *word;} words[600];static unsigned nwords,nbytes;
static struct {unsigned address;uint8_t *byte;} bytes[21];
static void word(unsigned at,uint16_t *p){words[nwords].address=lin(DATA_SEG,(uint16_t)at);words[nwords++].word=p;wanted[lin(DATA_SEG,(uint16_t)at)]=wanted[lin(DATA_SEG,(uint16_t)(at+1))]=1;}
static void byte(unsigned at,uint8_t *p){bytes[nbytes].address=lin(DATA_SEG,(uint16_t)at);bytes[nbytes++].byte=p;wanted[lin(DATA_SEG,(uint16_t)at)]=1;}
int main(void){
 NativePresentationWorld *w=native_presentation_world();
 for(unsigned i=0;i<14;i++)byte(0xc8+i,&w->hud.digits[i/7][i%7]);
 word(0x27a6,&w->hud.timer_width);word(0x27ac,&w->hud.cursor_x);word(0x27ae,&w->hud.cursor_y);
 for(unsigned i=0;i<9;i++)word(0x27b0+2*i,&w->hud.layout_x[i]);
 for(unsigned i=0;i<2;i++){word(0x27c2+2*i,&w->hud.score_words[i]);word(0x2800+2*i,&w->hud.icons[i]);}
 word(0x27c6,&w->hud.fare);word(0x27c8,&w->hud.retained_seed);
 byte(0x27ca,&w->hud.multiplier);byte(0x27cb,&w->hud.lives);byte(0x27cc,&w->hud.counter);byte(0x27cd,&w->hud.fare_pending);
 byte(0x27a2,&w->weather.pending);byte(0x27a3,&w->weather.countdown);word(0x27a4,&w->weather.frame);byte(0x27ce,&w->weather.phase);
 word(0x2905,&w->weather.previous_y);word(0x2907,&w->weather.byte_offset);
 for(unsigned i=0;i<193;i++){word(0x2e8b+2*i,&w->weather.rain[i].position);word(0x300d+2*i,&w->weather.rain[i].previous);word(0x318f+2*i,&w->weather.rain[i].modulo);}
 if(nwords!=600 || nbytes!=21)return 1;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++){if(presentation_is_owned(a))return 2;ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);}
 memcpy(expected,ugh_mem,sizeof expected);presentation_cold_import(ugh_mem);if(presentation_owned_bytes()!=1221)return 3;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(presentation_is_owned(a)!=(int)wanted[a])return 4;
 for(unsigned i=0;i<nwords;i++){
  unsigned a=words[i].address;if(*words[i].word!=(unsigned)(expected[a]|expected[a+1]*256u))return 5;
  for(unsigned v=0;v<65536;v++){
   presentation_shared_write(a,(uint8_t)v);presentation_borrowed_store(ugh_mem,a+1,(uint8_t)(v>>8));uint8_t lo,hi;
   if(!presentation_shared_read(a,&lo) || !presentation_shared_read(a+1,&hi) || (unsigned)(lo|hi*256u)!=v || *words[i].word!=v || presentation_borrowed_byte(ugh_mem+(a&~15u),a&15u)!=lo)return 6;
   expected[a]=lo;expected[a+1]=hi;
  }
 }
 for(unsigned i=0;i<nbytes;i++){
  unsigned a=bytes[i].address;if(*bytes[i].byte!=expected[a])return 7;
  for(unsigned v=0;v<256;v++){presentation_shared_write(a,(uint8_t)v);expected[a]=(uint8_t)v;uint8_t now;if(*bytes[i].byte!=v || !presentation_shared_read(a,&now) || now!=v)return 8;}
 }
 memcpy(output,ugh_mem,sizeof output);presentation_serialize(output);if(memcmp(output,expected,sizeof output) || presentation_check_serialization(output)!=UINT32_MAX)return 9;
 unsigned values=0;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(wanted[a])for(unsigned v=0;v<256;v++){
  presentation_shared_write(a,(uint8_t)v);expected[a]=(uint8_t)v;uint8_t now;presentation_shared_read(a,&now);if(now!=v)return 10;
  presentation_serialize(output);if(memcmp(output,expected,sizeof output))return 11;values++;
 }
 presentation_require_seal(ugh_mem);unsigned bad=lin(DATA_SEG,0x330f);output[bad]^=1;if(presentation_check_serialization(output)!=bad)return 12;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(!wanted[a]){uint8_t v=49;if(presentation_shared_read(a,&v) || presentation_shared_write(a,17) || v!=49)return 13;}
 // Declared slot 192 is owned; slot 193 aliases next field / input and is not enlarged.
 if(!presentation_is_owned(lin(DATA_SEG,0x330f)) || presentation_is_owned(lin(DATA_SEG,0x3311)))return 14;
 printf("{\"owned_bytes\":1221,\"words\":%u,\"single_bytes\":%u,\"word_roundtrips\":%u,\"byte_values\":%u,\"physical_addresses\":%u,\"private_storage_bytes\":%u}\n",nwords,nbytes,nwords*65536u,values,UGH_MEM_SIZE,(unsigned)sizeof *w);return 0;
}
'''
 source=folder/'router.c';source.write_text(code);exe=folder/'router.exe';bounded([timing.common.GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,source,ROOT/'native/presentation_world.c',ROOT/'native/bridge/presentation_world_bridge.c'],'router-compile')
 r=bounded([exe],'router-run');save(OUT/'router.json',dict(result='PASS',counts=json.loads(r['stdout']),scope='Independent literal address/named-member layout, all 1221 physical bytes and outside addresses; complete words at every storage location, all bytes, observation serialization/frame/seal and exact 193-record bounds.'))

def pair_case(machine,name,dlls,rows,regs=None,stop=False,actions=(),label=None,flags=None):
 import difftest
 initial=machine.prepare('GAME:'+name,{**difftest.POISON,**(regs or {})},'far',(),flags if flags is not None else 0x602 if len(rows)&1 else 0x202)
 memory=machine.snapshot();state=machine.device.state();observations=[]
 for dll in dlls:
  C.memmove(dll.ugh_memory().contents,memory,len(memory));dll.ugh_devices_reset();dev=dll.ugh_device_state().contents;C.memmove(C.addressof(dev),state,len(state))
  C.c_int.in_dll(dll,'api_stop_at_load').value=int(stop);dll.api_begin()
  r=difftest.Regs(**{k.lower():v for k,v in initial.items()});fn=getattr(dll,'api_c_'+name);fn.argtypes=[C.POINTER(difftest.Regs)];status=fn(C.byref(r))
  for target,changes in actions:
   for bank,offset,value in changes:
    dll.api_live_store.argtypes=[C.c_uint16,C.c_uint16,C.c_uint16];dll.api_live_store(bank,offset,value)
   C.c_int.in_dll(dll,'api_stop_at_load').value=0
   action=getattr(dll,'api_c_'+target);action.argtypes=[C.POINTER(difftest.Regs)];status=action(C.byref(r))
  observations.append((status,bytes(r),bytes(dll.ugh_memory().contents),bytes(dev)))
 if observations[0]!=observations[1]:
  a,b=observations;save(OUT/'backend-difference.json',dict(case=label or name,status=[a[0],b[0]],registers=[list(a[1]),list(b[1])],first_ram=next((i for i,(x,y) in enumerate(zip(a[2],b[2])) if x!=y),None),first_device=next((i for i,(x,y) in enumerate(zip(a[3],b[3])) if x!=y),None)))
 assert observations[0]==observations[1],label or name
 rows.append(dict(case=label or name,entry=name,status=observations[0][0]))
 return observations[0]

def backend():
 import nbuild,difftest,random
 dlls=[nbuild.load_l1(OUT/'api/hud'/v/'api.dll') for v in ['reference','composed']]
 machine=difftest.Machine();rows=[];data=machine.seg('DGROUP:PlayerCount')
 byte_seeds=0;score_seeds=0
 def setup_seed(lives,multi,score,players=1,reverse=False):
  machine.reset();machine.ww('DGROUP:LevelWorkspacePointer',0x2648);machine.ww('DGROUP:LevelWorkspacePointer',data,2)
  for at,size in REGIONS:machine.write(data,at,bytes((i*73+lives*17+at)&255 for i in range(size)))
  machine.wb('DGROUP:LivesRemaining',lives);machine.wb('DGROUP:ScoreMultiplier',multi)
  machine.ww('DGROUP:ScoreLowWord',score&65535);machine.ww('DGROUP:ScoreHighWord',score>>16);machine.ww('DGROUP:PlayerCount',players)
 for v in range(256):
  score=(v*0x1000101)&0xffffffff;setup_seed(v,255-v,score,1+v%2)
  result=pair_case(machine,'InitializeLevelDisplay',dlls,rows,dict(DS=data),stop=True,label='byte seed '+str(v),flags=0x202);ram=result[2]
  def word(n):a=data*16+machine.off('DGROUP:'+n);return ram[a]|ram[a+1]*256
  wanted=lambda x:((x+11)&255)-100 if ((x+11)&255)>=100 else ((x+11)&255)
  assert ram[data*16+machine.off('DGROUP:HudCachedLives')]==wanted(v)
  assert ram[data*16+machine.off('DGROUP:HudCachedMultiplier')]==wanted(255-v)
  total=(score+111111)&0xffffffff;total=total-1000000 if total>1000000 else total
  assert (word('HudCachedScoreLow')|word('HudCachedScoreHigh')*65536)==total
  byte_seeds+=1
 scores=[0,1,888887,888888,888889,888890,999998,999999,1000000,1000001,1888889,0x7fffffff,0x80000000,0xffffffff-111111,0xffffffff-111110,0xfffffffe,0xffffffff]
 scores+=list(dict.fromkeys(((h<<16)|lo) for h in [0,1,14,15,16,0x7fff,0x8000,0xffff] for lo in [0,1,0x423f,0x4240,0xffff]))
 for score in scores:
  setup_seed(255,200,score);pair_case(machine,'InitializeLevelDisplay',dlls,rows,dict(DS=data),stop=True,label='score seed '+str(score),flags=0x202);score_seeds+=1
 for flags in [0x202,0x602]:
  setup_seed(249,255,0xffffffff)
  result=pair_case(machine,'InitializeLevelDisplay',dlls,rows,dict(DS=data),stop=True,label='bulk-clear direction and live seed '+hex(flags),flags=flags);ram=result[2]
  # Backward STOS reaches the live counters/score. Seeds use those post-clear
  # values; the original routine never clears DF on entry.
  for live,cached in [('LivesRemaining','HudCachedLives'),('ScoreMultiplier','HudCachedMultiplier')]:
   actual=ram[data*16+machine.off('DGROUP:'+live)];assert ram[data*16+machine.off('DGROUP:'+cached)]==wanted(actual)
 # Full allocated rain domain and the cross-array/input aliases at physical slot193.
 suite=__import__('difftest').load_suite('render')
 for water in [0,1,191,192,0xffff,0x7fff,0x8000]:
  for name in ['AdvanceRainParticles','DrawRainParticles','RestoreRainBackground']:
   case=next(c for c in extra_weather_cases() if c.routine=='GAME:'+name and ('water='+format(water,'04x')) in c.title)
   machine.reset();case.setup(machine);pair_case(machine,name,dlls,rows,dict(DS=data),label=name+' physical '+str(water))
 # Stateful whole-owner history: render a HUD, change live inputs, render again.
 for kind in ['lives','score-low','fare-one','icon-one','journeys','multiplier','unchanged']:
  case=suite.hud_case(kind);machine.reset();case.setup(machine)
  changes=[(data,machine.off('DGROUP:LivesRemaining'),0x0207),(data,machine.off('DGROUP:ScoreLowWord'),0xbeef),(data,machine.off('DGROUP:ScoreHighWord'),3)]
  pair_case(machine,'RefreshHudAndTimerBar',dlls,rows,dict(DS=data),actions=[('RefreshHudAndTimerBar',changes)],label='live cached history '+kind)
 # Whole world owners remain pairwise disjoint, including all 193 allocated records.
 modern=dlls[1];modern.api_live_word.argtypes=[C.c_uint16,C.c_uint16];modern.api_live_word.restype=C.c_uint16
 # Explicit slot aliases using live typed views after the fixture has activated.
 modern.api_live_store.argtypes=[C.c_uint16,C.c_uint16,C.c_uint16]
 modern.api_live_store(data,0x2e8b+386,0xa761);assert modern.api_live_word(data,0x300d)==0xa761
 modern.api_live_store(data,0x300d+386,0x8162);assert modern.api_live_word(data,0x318f)==0x8162
 modern.api_live_store(data,0x318f+386,0x9173);assert modern.api_live_word(data,0x3311)==0x9173
 save(OUT/'backend.json',dict(result='PASS',cases=rows,byte_seed_inputs=byte_seeds,score_seed_inputs=score_seeds,physical_slot_193_aliases=3,scope='Independent compiled L1/composed complete RAM, full registers/flags and Devices, including actual InitializeLevelDisplay before its immediate load service, full byte seeds and 32-bit boundaries, stateful HUD histories, 193-slot/slot193 aliases and native input ownership.'))

def borrowers():
 source=inspect.getsource(palette.borrowers)
 source=source.replace('  for dll in dlls:\n','  for dll in dlls:\n   dll.api_begin()\n')
 source=source.replace("OUT/'api'/v/'api.dll'","OUT/'api/hud'/v/'api.dll'")
 source=source.replace("m.seg('GAME:BaseRgbPalette')","m.seg('DGROUP:DecimalDigitBuffer')").replace("m.off('GAME:BaseRgbPalette')","m.off('DGROUP:DecimalDigitBuffer')").replace("m.off('GAME:FadedRgbPalette')","m.off('DGROUP:HudCachedScoreLow')")
 source=source.replace('[0x681,0x682,0x981,0xc81]','[0x20d6,0x47cf,0x5311,0x5313]').replace('ES=game+0x400','ES=game-0x200')
 # The base RGB binding is not automatically the moved decimal buffer.
 source=source.replace("pair('UploadBasePalette',regs=", "m.ww('DGROUP:BasePalettePointer',base);m.ww('DGROUP:BasePalettePointer',game,2)\n pair('UploadBasePalette',regs=")
 # Seed actual decimal divisors at their normal data binding, not an alias bank.
 source=source.replace("m.write(game,m.off('DGROUP:'+label)","m.write(game,m.off('DGROUP:'+label)")
 env=dict(palette.__dict__);exec(source,env);env['borrowers']()
 r=json.loads((OUT/'borrowers.json').read_text());r.pop('excluded_probe',None);r['scope']='L1/composed byte windows spanning current/prior digits, HUD caches, weather and rain: forward/backward/overlap/wrap copy, decimal and duplicate aliases, per-component palette source mutation and real ICE writes ending across allocated fields and the adjacent native input owner. Decoder code/tables remain disjoint.';save(OUT/'borrowers.json',r)


def projector(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'projector',locals())


def census(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'census',locals())


def copy_host(target,folder):
 for top in ['c','native','host','metadata','tools','verif','src']:shutil.copytree(target/top,folder/top,dirs_exist_ok=True)
 shutil.copytree(target/'build/link',folder/'build/link',dirs_exist_ok=True)
 capture=folder/'capture.py';capture.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n')
 return capture


def rain_reference(target):
 import wholegame,cgen
 from emu import NativeVga
 script=target/'verif/random_rain.txt';spec=wholegame.scenario(script);folder=OUT/'rain';folder.mkdir(exist_ok=True)
 save(target/'build/workers/c-close/call-edges.json',[]);wholegame.ROOT=target
 accelerator=NativeVga(folder);wholegame.VGA_ACCELERATOR=accelerator
 try:
  m,initial=wholegame.fixture(spec);key=wholegame.identity(script,m);p=folder/'random-rain.ref.json'
  if p.exists() and json.loads(p.read_text())['key']==key:return p
  frames,coverage,_=wholegame.original(spec,m,initial)
  save(p,dict(key=key,version=wholegame.VERSION,frames=frames,coverage=coverage,provenance='Reconstructed ASM via tools.wholegame.original; native output never used'))
  return p
 finally:wholegame.VGA_ACCELERATOR=None;accelerator.close()


def weather_runs():
 import os,wholegame,level_suite
 from closure_support import function
 target=snapshot();folder=OUT/'weather-runs';capture=copy_host(target,folder)
 names=NAMES[8:17]+['RefreshHudAndTimerBar','InitializeLevelDisplay','LoadCurrentLevelState']
 (folder/'host/presentation_counts.c').write_text('#include <stdio.h>\n#include <stdlib.h>\nstatic unsigned long long counts['+str(len(names))+'];\nstatic void dump(void){const char*p=getenv("PRESENTATION_COUNTS");if(!p)return;FILE*f=fopen(p,"w");if(!f)abort();fputs("[",f);for(unsigned i=0;i<'+str(len(names))+';i++)fprintf(f,"%s%llu",i?",":"",counts[i]);fputs("]",f);fclose(f);}\nvoid presentation_count(unsigned i){static int ready;if(!ready){atexit(dump);ready=1;}counts[i]++;}\n')
 for bridge,entries in [('water_weather',names[:9]),('hud',names[9:10]),('session',names[10:])]:
  p=folder/('native/bridge/'+bridge+'_bridge.c');text=p.read_text();wrappers=[]
  for n in entries:
   body=function(text,'c_'+n);renamed=body.replace('c_'+n+'(','counted_'+n+'(',1);assert renamed!=body;text=text.replace(body,renamed)
   wrappers.append('EXPORT int c_'+n+'(Regs*r){presentation_count('+str(names.index(n))+');return counted_'+n+'(r);}\n')
  p.write_text('extern void presentation_count(unsigned);\n'+text+'\n'+''.join(wrappers))
 bounded([sys.executable,'tools/hostbuild.py'],'weather-counts-build',folder)
 selected=[r for r in level_suite.selection() if r['weather']];assert len(selected)==4
 scenarios=[(f"{'one' if r['players']==1 else 'two'}-{r['number']:02d}",r) for r in selected]+[('random-rain',None)]
 rain=rain_reference(target);rows=[]
 for name,record in scenarios:
  script=target/('tests/levels/'+name+'.txt') if record else target/'verif/random_rain.txt'
  reference=target/('build/levels/'+name+'.ref.json') if record else rain;ref=json.loads(reference.read_text());spec=wholegame.scenario(script)
  result=folder/(name+'.counts.json');os.environ['PRESENTATION_COUNTS']=str(result)
  try:r=bounded([sys.executable,capture,folder/'build/host/ugh.exe','--headless',str(spec['frames']),'--script',script,'--timeout','590'],'weather-counts-'+name)
  finally:os.environ.pop('PRESENTATION_COUNTS',None)
  actual=json.loads(r['stdout']);assert actual['returncode']==0,actual['stderr'];frames=[json.loads(line) for line in actual['stdout'].splitlines()]
  assert frames==ref['frames'],(name,'independent ASM reference mismatch')
  counts=dict(zip(names,json.loads(result.read_text())));assert all(counts[n]>0 for n in ['AdvanceRainParticles','RespawnRainParticle','DrawRainParticles','RestoreRainBackground']),counts
  rows.append(dict(scenario=name,level={k:record[k] for k in ['record','players','number','weather','title']} if record else 'Existing random-rain witness',entries=counts,frames=len(frames),reference_key=ref['key']))
 save(OUT/'weather-runs.json',dict(result='PASS',runs=rows,scope='Generated entry counters only; every frame matches independent rebuilt-ASM references. All four rainy physical records plus existing random-rain witness.'))


def defects():
 import wholegame
 target=snapshot();rain=rain_reference(target);rows=[]
 for fault,name,scenario in [(1,'stale-hud-cache','gameplay-adlib'),(2,'dropped-rain-respawn','random-rain'),(3,'wrong-rain-modulo-step','random-rain'),(4,'missed-serialization','gameplay-adlib')]:
  folder=OUT/'defects'/name;capture=copy_host(target,folder)
  p=folder/'tools/hostbuild.py';text=p.read_text();needle="return (['-DUGH_NATIVE_PRESENTATION']";assert text.count(needle)==1
  p.write_text(text.replace(needle,"return (['-DPRESENTATION_TEST_FAULT="+str(fault)+"','-DUGH_NATIVE_PRESENTATION']",1))
  # Windows CRT abort may wait for a crash dialog. Keep the actual consuming
  # predicates, but give their failure an identified, noninteractive exit in
  # these generated defect copies only (never in maintained native code).
  for rel,symbol in [('native/bridge/hud_support.h','hd_require'),('native/bridge/session_support.h','sq_require'),('native/bridge/water_weather_bridge.c','ww_require')]:
   p=folder/rel;text=p.read_text();old='static void '+symbol+'(int c){if(!c)abort();}';assert text.count(old)==1
   new='static void '+symbol+'(int c){if(!c){fputs("PRESENTATION_CONTROL_BRIDGE_ASSERT:'+symbol+'\\n",stderr);exit(87);}}'
   p.write_text('#include <stdio.h>\n'+text.replace(old,new))
  bounded([sys.executable,'tools/hostbuild.py'],'defect-'+name+'-build',folder)
  script=target/('verif/random_rain.txt' if scenario=='random-rain' else 'tests/scenarios/'+scenario+'.txt')
  reference=json.loads((rain if scenario=='random-rain' else target/('build/whole/'+scenario+'.ref.json')).read_text())
  r=bounded([sys.executable,capture,folder/'build/host/ugh.exe','--headless',str(wholegame.scenario(script)['frames']),'--script',script,'--timeout','590'],'defect-'+name+'-run')
  actual=json.loads(r['stdout']);got=[json.loads(line) for line in actual['stdout'].splitlines()];expected=reference['frames']
  first=next((i for i,(a,b) in enumerate(zip(got,expected)) if a!=b),None)
  if fault==4:assert actual['returncode']==88 and 'missed serialization' in actual['stderr'],actual
  else:assert (first is not None and actual['returncode']==0) or (actual['returncode']==87 and 'PRESENTATION_CONTROL_BRIDGE_ASSERT:' in actual['stderr']),(name,actual['returncode'],actual['stderr'])
  rows.append(dict(defect=name,result='DETECTED_BY_BRIDGE' if actual['returncode']==87 else 'DETECTED',scenario=scenario,frame=first+1 if first is not None else len(got)+1,exit=actual['returncode'],first_expected=expected[first] if first is not None else None,first_actual=got[first] if first is not None else None,diagnostic=actual['stderr'][-1500:]))
 save(OUT/'defects.json',dict(result='PASS',controls=rows))


def inventory():
 assert sum(n for _,n in REGIONS)==1221
 save(OUT/'inventory.json',dict(result='PASS',baseline='c358a8419574a949b592db23424205062211bfca',moved_bytes=1221,hud_bytes=54,weather_bytes=1167,total_native_bytes=TOTAL,regions=[dict(segment='DGROUP',offset=f'{at:04X}',length=n) for at,n in REGIONS],allocation='Three declared arrays of 193 words, represented as 193 native records; byte router preserves physical cross-array aliases. Slot193 modulo aliases input_world presence, never a 194th owned rain record.',water_y='Deferred to step 5: WaterY32/WaterYPixels shared by water, session, menus and high scores; existing canonical RAM owner retained. WaterSurfaceStep remains level/world configuration.',shared_histories='Player draw caches and all actor render histories remain canonical for step 5. No actors.h change.',borrowers=['HUD: session seeds/layout/bulk clear; menu level-introduction cursor; high-score decimal current/prior digit buffers','Weather: loader bulk clear, 193 rain seeds and 577 prewarm advances; water simulation and pixel recipes','Physical byte windows: far copy, decimal/duplicate, ICE and streaming palette reads; audio workspace routing','Adjacent slot193 rain modulo: native input presence owner; no duplicate ownership']));


def finalize(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'finalize',locals())


def main(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'main',locals())


# Scheduled by world_gate; no private CLI.
