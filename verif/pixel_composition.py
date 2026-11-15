"""Step 4 pixel-service composition; renderer scratch is native, shared world stays put.
Each external child: 600 s, 8 GiB, serial. Full compatibility, scratch promotion only.
"""
import argparse,ctypes as C,hashlib,inspect,io,json,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/workers/close-stones-21'
sys.path.insert(0,str(ROOT/'tools'))
import video_pages_composition as pages
prior=pages.prior;palette=pages.palette;audio=pages.audio;timing=pages.timing
pages.OUT=prior.OUT=palette.OUT=audio.OUT=timing.OUT=timing.common.OUT=OUT
bounded=pages.bounded;save=pages.save;sha=pages.sha
NEW=['native/pixel_world.h','native/pixel_world.c','native/bridge/pixel_world_bridge.h','native/bridge/pixel_world_bridge.c','native/bridge/pixel_io.h']
BRIDGES=['native/bridge/'+n+'_bridge.c' for n in ['render_primitives','hud','water_weather','actor_render','player_physics']]
BASE=NEW+BRIDGES+['native/bridge/pixel_io.h','native/bridge/hud_support.h','verif/pixel_platform_model.inc','verif/pixel_composition.py','tools/hostbuild.py','host/main.c','verif/projector/observer.c','verif/projector/timing_serializer.h','verif/projector/publications.py','verif/projector_evidence.py']
READ=list(dict.fromkeys(pages.READ+['verif/video_pages_composition.py','metadata/closure/video_pages.json','metadata/closure/hud.json','native/player_physics.c','native/bridge/actor_render_bridge.c','verif/player_physics_l0_cases.py','verif/water_weather_l0_cases.py']))
NAMES=['DrawTransparentSprite','DrawMapTile','DrawTileMap','SaveDrawPageBackground','RestorePlayfieldBackground','RestoreBackgroundRectangle','RestoreSpriteBackground','RestoreTileBackground','RestorePlayerBackground','AnimateAndDrawPlayer','CachePlayerDrawState','DrawHudBorders','DrawHudDigit','DrawHudDigitAndAdvance','RedrawChangedTwoDigitNumber','RedrawChangedFourDigitNumber','RedrawChangedSixDigitNumber','RefreshHudAndTimerBar','AdvanceWaterSurface','DrawWaterSurface','DrawWaterSurfaceFrame0','DrawWaterSurfaceFrame1','DrawWaterSurfaceFrame2','AdvanceRainParticles','RespawnRainParticle','DrawRainParticles','RestoreRainBackground','MovePlayerWithVgaCollisions','SamplePlayerCollisionPixels','DrawDemoSprites','EraseDemoSprites','ResetSpriteEraseState']
TOTAL=6439

def files():return sorted(set(BASE+subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()+['metadata/closure/pixel_world.json']))

def snapshot():
 revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();target=OUT/'baseline'
 raw=subprocess.check_output(['git','archive','--format=tar',revision],cwd=ROOT)
 with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
  for member in tar.getmembers():
   if not member.isfile():continue
   p=(target/member.name).resolve();assert p.is_relative_to(target.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(tar.extractfile(member).read())
 for f in files():p=target/f;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,p)
 p=target/'metadata/closure/pixel_world.json';c=json.loads(p.read_text());c['status']='migrated';save(p,c)
 for bank in ['whole','levels','levels-audio','levels-deep']:
  dest=target/'build'/bank;dest.mkdir(parents=True,exist_ok=True)
  for p in (ROOT/'build'/bank).glob('*.ref.json'):shutil.copyfile(p,dest/p.name)
 save(target/'build/workers/c-close/call-edges.json',[])
 save(OUT/'baseline.json',dict(revision=revision,overlay={f:sha(ROOT/f) for f in files()}));return target
pages.snapshot=prior.snapshot=palette.snapshot=audio.snapshot=timing.snapshot=snapshot
build=palette.build;levels=palette.levels

def projector():
 source=inspect.getsource(palette.projector).replace('6148',str(TOTAL)).replace('Palette ownership cut only','Pixel service cut');env=dict(palette.__dict__);exec(source,env);env['projector']()

def relock(final=False):
 import closure
 p=ROOT/'metadata/closure/pixel_world.json'
 if not p.exists() or not p.stat().st_size:save(p,dict(component='pixel_world',status='unanalyzed',original=dict(owned=[],composes=['render_primitives','hud','water_weather','actor_render','player_physics','video_pages']),native=dict(files=NEW,functions=['native_pixel_world'],bridge='Native owner; explicit typed services and verification-only ABI continuations'),purpose='Step 4 pixel service cut and exclusive renderer scratch ownership',interface=dict(inputs='Cold fixture, opaque bank identities, live source reads, inherited full VGA controls and retrace replies',outputs='Native persistent page state, typed ordered requests, separate observation serialization'),callers=['Video entry ABI; pictures, session, demos, renderer, physics, water and generic byte windows'],callees=['Typed indexed controls, live lane stores/source reads, retrace/cut/frame services; accepted video kernels and peers'],indirect=['Closed VideoPeerRole; opaque page bank identities; verification continuation only'],amiga=dict(classification='not-used',finding='Composition only; accepted DOS contracts retained'),uncertainty=['Partial cut: HUD/render/weather ownership and sprite/copy/collision services remain; no production backend'],memory=dict(owner='NativePixelWorld, four historical renderer lanes',total_with_prior=TOTAL,remaining='HUD/weather ownership remains for a separate cut; player caches, actor histories and Water Y remain canonical and unmoved'),assumptions=['Accepted video scalar/cursor/timing domains; no narrowing of inherited VGA controls','Opaque synchronous continuation is verification-only ABI metadata; production state contains no Regs or RAM pointer','Original disjoint active code/resource/stack domains; arbitrary stored banks/offsets where the video API admits them'],eliminated=['RAM ownership of renderer scratch; pixel island raw plane/control ports and internal near dispatch'],retained=['Unchanged bank words, DF and word reductions, zero-count wrap, full inherited GC/latch controls, off-page and live source aliases'],evidence=[],verification_inputs={},dependencies={},verification_input_hashing='sha256-lf-text'))
 old={p.name:json.loads(subprocess.check_output(['git','show','HEAD:'+p.relative_to(ROOT).as_posix()],cwd=ROOT,text=True)) for p in (ROOT/'metadata/closure').glob('*.json') if p.stem!='pixel_world'}
 for p in (ROOT/'metadata/closure').glob('*.json'):
  c=json.loads(p.read_text())
  if p.name in old:
   if 'evidence_refreshed' in old[p.name]:c['evidence_refreshed']=old[p.name]['evidence_refreshed']
   else:c.pop('evidence_refreshed',None)
  save(p,c)
 changed={}
 for iteration in range(100):
  dirty=False
  for p in sorted((ROOT/'metadata/closure').glob('*.json')):
   c=json.loads(p.read_text())
   for f in c.get('dependencies',{}):
    if f in BASE:c['dependencies'][f]=closure.actual_dependencies(ROOT/f)
   if p.stem=='pixel_world':
    c['dependencies']={f:closure.actual_dependencies(ROOT/f) for f in NEW}
    c['verification_inputs']={f:sha(ROOT/f) for f in BASE+READ}
    if not c['evidence']:c['evidence']=[dict(property='Native renderer-word seam',level='B',method='Actual-C output/frame/dependence profile; composition gate separately pending',command='python verif/pixel_composition.py --proof',result='PASS' if (OUT/'proof.json').exists() else 'Pending',date='2026-11-15')]
   for f,h in c.get('verification_inputs',{}).items():
    data=(ROOT/f).read_bytes();data=data.replace(b'\r\n',b'\n') if c.get('verification_input_hashing')=='sha256-lf-text' else data
    actual=hashlib.sha256(data).hexdigest()
    if actual!=h:c['verification_inputs'][f]=actual;dirty=True
   if p.name in old:
    inputs=[f for f,h in c.get('verification_inputs',{}).items() if h!=old[p.name].get('verification_inputs',{}).get(f)]
    if (inputs or c.get('dependencies')!=old[p.name].get('dependencies')) and p.name not in changed:
     direct=any(not f.startswith('metadata/closure/') for f in inputs) or c.get('dependencies')!=old[p.name].get('dependencies')
     note=dict(date='2026-11-15',reason='Pixel services and renderer ownership; prior claim domains/status unchanged' if direct else 'Dependent composition-note hash cascade only',commands=['python verif/pixel_composition.py --gate'],results='PASS' if final else 'Pending pixel composition acceptance',inputs=inputs)
     c['evidence_refreshed']=old[p.name].get('evidence_refreshed',[])+[note];changed[p.name]=note;dirty=True
   save(p,c)
  if not dirty:break
 else:raise RuntimeError('lock cycle')
 save(OUT/'relocks.json',dict(certificates=changed))



def api(group):
 source=inspect.getsource(timing.api)
 suites=['video','video_upload','render_primitives','render'] if group=='raster' else ['scene']
 source=re.sub(r"suites=\[[^\n]+\]",'suites='+repr(suites),source,1)
 source=source.replace(" import timer_callbacks\n cases += [('timer_callbacks',c) for c in timer_callbacks.CASES]\n",'')
 if group=='world':
  source=source.replace(' names=sorted'," cases=[(s,c) for s,c in cases if c.routine.split(':')[1] in "+repr(NAMES)+"]\n import player_physics_l0_cases,water_weather_l0_cases\n cases += [('scene',c) for c in player_physics_l0_cases.cases()+water_weather_l0_cases.cases()]\n names=sorted",1)
 source=source.replace("{'timing_world','audio_world'}","{'timing_world','audio_world','palette_world','input_world','video_pages','pixel_world'}")
 source=source.replace("units.append(dict(component='timing_world',native=ROOT/'native/timing_world.c',bridge=ROOT/'native/bridge/timing_world_bridge.c',exports=[]))", "units.extend([dict(component=n,native=ROOT/('native/'+n+'.c'),bridge=ROOT/('native/bridge/'+n+'_bridge.c'),exports=[]) for n in ['timing_world','audio_world','palette_world','input_world','video_pages','pixel_world']])")
 headers=''.join('#include "'+n+'_bridge.h"\\n' for n in ['pixel_world','video_pages','input_world','palette_world'])
 source=source.replace("fixture.write_text('#include \"timing_world_bridge.h\"", "fixture.write_text('"+headers+'#include "timing_world_bridge.h"')
 for action in ['cold_import','require_seal','serialize']:
  value='timing_api_observation' if action=='serialize' else 'ugh_mem'
  needle=' timing_'+action+'('+value+');'
  extra=''.join('\\n#ifdef UGH_NATIVE_'+flag+'\\n '+name+'_'+action+'('+value+');\\n#endif' for flag,name in [('PALETTE','palette'),('INPUT','input'),('VIDEO_PAGES','video_pages'),('PIXEL','pixel')])
  source=source.replace(needle,needle+extra)
 source=source.replace("sources += [u['native'] for u in units]+[u['bridge'] for u in units]+[fixture]", "sources.append(fixture)\n  for original in [u['native'] for u in units]+[u['bridge'] for u in units]:\n   text=original.read_text();new=hostbuild.composition_source(original.relative_to(ROOT).as_posix(),text,units)\n   if new!=text:\n    path=folder/('native_'+original.name);path.write_text(new);sources.append(path)\n   else:sources.append(original)")
 source=source.replace("OUT/'api'/label","OUT/'api'/"+repr(group)+"/label").replace("'api-'+label+'-compile'",repr('api-'+group+'-')+"+label+'-compile'")
 source=source.replace("assert old['timer_fallbacks'] and new['status']==1,(old,new)","assert new['status'] in (1,3),(old,new)").replace(' assert len(declines)==32','')
 source=source.replace('composed_matching=2202-len(declines),legacy_matching=2202','composed_matching=len(cases)*2-len(declines),legacy_matching=len(cases)*2').replace("OUT/'api.json'","OUT/"+repr('api-'+group+'.json'))
 source=source.replace("print('API PASS legacy 2202; composed 2170 matches + 32 explicit domain rejections',flush=True)","print('API PASS',len(cases)*2,'cases;',len(declines),'explicit rejects',flush=True)")
 seam={f:sha(ROOT/f) for f in BASE+READ if not f.startswith('metadata/closure/')}
 env=dict(timing.__dict__);exec(source,env);env['api']()
 p=OUT/('api-'+group+'.json');receipt=json.loads(p.read_text());receipt['seam_inputs']=seam;receipt['scope']='Independent Unicorn vs legacy/composed; complete RAM outside scratch stack, Devices and ordered IO; declared live ABI/flags. World group includes all 1024 collision high-bit patterns and inherited water modes.';save(p,receipt)

def router():
 source=inspect.getsource(pages.router)
 source=source.replace("['BlackenVgaPalette','EnableAllVgaWritePlanes','ClearAllVgaPlanes','WaitNextVerticalRetrace','WaitVerticalRetraceActive','WaitVerticalRetraceInactive','PollKeyboardScanChange','SampleJoystickAxesAndButtons']",repr(sorted(set(re.findall(r'case PIXEL_PEER_(\w+):',(ROOT/'native/bridge/pixel_world_bridge.c').read_text())))))
 source=source.replace('video_pages','pixel').replace('NativeVideoPages','NativePixelWorld').replace('native_pixel()','native_pixel_world()').replace('0x4600','0x45fc').replace('input_borrowed_','video_pages_borrowed_')
 source=source.replace('base+20','base+4').replace('!=20','!=4').replace('==20','==4').replace('i<10','i<2').replace('i<20','i<4').replace('sizeof(NativePixelWorld)==20','sizeof(NativePixelWorld)==4').replace('ten packed numeric words','two numeric words')
 a=source.index(' uint16_t *words[]=');b=source.index('\n',a)
 source=source[:a]+' uint16_t *words[]={&w->plane_state,&w->water_distance};'+source[b:]
 source=source.replace('base+13','base+3').replace('VIDEO_PEER_WaitNextVerticalRetrace','PIXEL_PEER_DrawTransparentSprite').replace('VideoPeerRole','PixelPeerRole')
 source=source.replace('pixel_borrowed_byte(ugh_mem+(base&~15u),2*i)','pixel_borrowed_byte(ugh_mem+(base&~15u),(base&15u)+2*i)')
 source=source.replace('owned_bytes\\\":20','owned_bytes\\\":4').replace('byte_values\\\":5120','byte_values\\\":1024').replace('word_roundtrips\\\":655360','word_roundtrips\\\":131072')
 source=source.replace('native/pixel.c','native/pixel_world.c').replace('native/bridge/pixel_bridge.c','native/bridge/pixel_world_bridge.c').replace('"pixel_bridge.h"','"pixel_world_bridge.h"')
 source=source.replace('STUBS\nstatic uint8_t', 'STUBS\nint pixel_service_continuation(PixelContinuationKind k,PixelExternalBinding b,uint16_t ret,PixelServiceContext*c){(void)k;(void)b;(void)ret;(void)c;return UGH_BAD_CALLBACK;}\nstatic uint8_t')
 # Tail-only peers also need declarations in this standalone router.
 source=source.replace(" for n in "," for n in ",1)
 env=dict(pages.__dict__);exec(source,env);env['router']()

def proof():
 from closure_support import function
 folder=OUT/'proof';folder.mkdir(exist_ok=True);bridge=(ROOT/'native/bridge/pixel_world_bridge.c').read_text()
 prefix='#include "pixel_world.h"\n#include "'+(ROOT/'native/pixel_world.c').as_posix()+'"\n'+''.join(function(bridge,n) for n in ['pixel_get_word','pixel_put_word'])
 prefix+='void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);\n#define assert(c) __CPROVER_assert((c),#c)\n'
 main=r'''NativePixelWorld nondet_world(void);uint8_t nondet_byte(void);uint16_t nondet_word(void);unsigned nondet_uint(void);
int main(void){
 world=nondet_world();unsigned selected=nondet_uint(),lane=nondet_uint();__CPROVER_assume(selected<2 && lane<2);
 uint16_t *words[]={&world.plane_state,&world.water_distance};uint16_t old=*words[selected],frame=*words[1-selected];
 assert(pixel_get_word(selected)==old);assert(*words[selected]==old && *words[1-selected]==frame);
 uint8_t value=nondet_byte();unsigned shift=lane*8;uint16_t after=(uint16_t)((old&~(255u<<shift))|((unsigned)value<<shift));
 pixel_put_word(selected,after);assert(*words[selected]==after && pixel_get_word(selected)==after && *words[1-selected]==frame);
 uint16_t origin=nondet_word();unsigned ordinal=nondet_uint();__CPROVER_assume(ordinal<10);
 const uint16_t expected[]={0,3,5,1824,1827,1829,576,581,1152,1157};
 assert(pixel_collision_position(origin,ordinal)==(uint16_t)(origin+expected[ordinal]));
}
'''
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe'];rows=[]
 def run(name,code,unwind):
  source=folder/(name+'.c');source.write_text(code);pre=folder/(name+'.i')
  bounded([timing.common.GCC,'-E','-P','-nostdinc','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',source,'-o',pre],'proof-'+name+'-preprocess')
  r=bounded([tool,pre,'--unwind',str(unwind),'--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-'+name)
  assert 'VERIFICATION SUCCESSFUL' in r['stdout'];rows.append(dict(profile=name,source=sha(source),preprocessed=sha(pre)))
 run('owner',prefix+main,2)
 provider=(ROOT/'verif/pixel_platform_model.inc').read_text()
 code='#include "pixel_world.h"\n'+r'''
void __CPROVER_assert(int,const char*);
#define assert(c) __CPROVER_assert((c),#c)
static unsigned count;static uint32_t addresses[2];static uint8_t kinds[2],values[2],reply;
uint8_t ugh_read(uint32_t a){kinds[count]=0;addresses[count++]=a;return reply;}
void ugh_write(uint32_t a,uint8_t v){kinds[count]=1;addresses[count]=a;values[count++]=v;}
'''+''.join(function(provider,n) for n in ['pixel_service_read','pixel_service_store','pixel_service_copy','pixel_service_water_mark'])+r'''
uint16_t nondet_word(void);uint8_t nondet_byte(void);
int main(void){
 VideoCellAddress a={{nondet_word()},nondet_word()},b={{nondet_word()},nondet_word()};uint8_t v=nondet_byte();reply=nondet_byte();
 uint32_t p=(uint32_t)a.bank.value*16u+a.position,q=(uint32_t)b.bank.value*16u+b.position;
 count=0;assert(pixel_service_read(a,PIXEL_COLLISION)==reply);assert(count==1 && kinds[0]==0 && addresses[0]==p);
 count=0;pixel_service_store(a,v);assert(count==1 && kinds[0]==1 && addresses[0]==p && values[0]==v);
 count=0;assert(pixel_service_copy(a,b)==reply);assert(count==2 && kinds[0]==0 && kinds[1]==1 && addresses[0]==p && addresses[1]==q && values[1]==reply);
 count=0;assert(pixel_service_water_mark(a)==reply);assert(count==2 && kinds[0]==0 && kinds[1]==1 && addresses[0]==p && addresses[1]==p && values[1]==64);
}
'''
 run('services',code,2)
 # Real sampler C, real flag helpers, ten symbolic complete reply bytes.
 sampler=function((ROOT/'native/bridge/player_physics_bridge.c').read_text(),'c_SamplePlayerCollisionPixels')
 pure=function((ROOT/'native/player_physics.c').read_text(),'player_collision_sample')
 code='#include "'+(ROOT/'c/ugh.h').as_posix()+'"\n#include "pixel_world.h"\n'+r'''
void __CPROVER_assert(int,const char*);
#define assert(c) __CPROVER_assert((c),#c)
static uint8_t replies[10];static unsigned consumed;static uint16_t expected_bank,expected_origin;
uint8_t pixel_service_read(VideoCellAddress a,PixelReadRole role){
 const uint16_t d[]={0,3,5,1824,1827,1829,576,581,1152,1157};
 assert(consumed<10 && role==PIXEL_COLLISION && a.bank.value==expected_bank && a.position==(uint16_t)(expected_origin+d[consumed]));
 return replies[consumed++];
}
'''+function((ROOT/'native/pixel_world.c').read_text(),'pixel_collision_position')+pure+sampler+r'''
uint8_t nondet_byte(void);Regs nondet_regs(void);
int main(void){Regs r=nondet_regs(),before=r;expected_bank=r.es;expected_origin=r.si;
 for(unsigned i=0;i<10;i++)replies[i]=nondet_byte();consumed=0;
 assert(c_SamplePlayerCollisionPixels(&r)==UGH_OK);assert(consumed==10);
 assert((uint8_t)r.ax==player_collision_sample(replies));assert((r.ax&65280)==(before.ax&65280));
 assert(r.bx==before.bx && r.cx==before.cx && r.dx==before.dx && r.si==before.si && r.di==before.di && r.bp==before.bp && r.sp==before.sp && r.cs==before.cs && r.ds==before.ds && r.es==before.es && r.ss==before.ss && r.ip==before.ip);
}
'''
 # Real ugh.h needs the real stdint + symbolic model; no RAM arrays are symbolic.
 source=folder/'sampler.c';source.write_text(code);pre=folder/'sampler.i'
 bounded([timing.common.GCC,'-E','-P','-U_WIN32','-DUGH_NATIVE_PIXEL','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'c','-I',ROOT/'native',source,'-o',pre],'proof-sampler-preprocess')
 r=bounded([tool,pre,'--unwind','11','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-sampler');assert 'VERIFICATION SUCCESSFUL' in r['stdout'];rows.append(dict(profile='sampler',source=sha(source),preprocessed=sha(pre)))
 save(OUT/'proof.json',dict(result='PASS',profiles=rows,scope='Actual-C renderer-word output/frame/dependence; full bank/word address and full reply slices; read-before-write copy/mark streams; actual sampler ten-read order, independent word reductions, full-byte reply use and other-register frame. No whole-physics/HUD/weather B claim.'))

def backend(fault=0):
 import hostbuild
 folder=OUT/('backend' if not fault else 'defects/backend-'+str(fault));folder.mkdir(parents=True,exist_ok=True)
 code=r'''#include "platform.h"
#include "pixel_world_bridge.h"
#include "video_pages_bridge.h"
#include "input_world_bridge.h"
#include "palette_world_bridge.h"
#include "timing_world_bridge.h"
#include <stdio.h>
#include <string.h>
void ugh_devices_reset(void);int l1_SamplePlayerCollisionPixels(Regs *);
int l1_DrawWaterSurfaceFrame0(Regs*);int l1_DrawWaterSurfaceFrame1(Regs*);int l1_DrawWaterSurfaceFrame2(Regs*);
static Devices seed,expected;static uint8_t memory[UGH_MEM_SIZE],result[UGH_MEM_SIZE];
static void checkpoint(void){memcpy(&seed,&ugh_devices,sizeof seed);memcpy(memory,ugh_mem,sizeof memory);}
static void old_done(void){memcpy(&expected,&ugh_devices,sizeof expected);memcpy(result,ugh_mem,sizeof result);memcpy(&ugh_devices,&seed,sizeof seed);memcpy(ugh_mem,memory,sizeof memory);}
static int match(void){return !memcmp(&expected,&ugh_devices,sizeof expected) && !memcmp(result,ugh_mem,sizeof result);}
static void epoch(void){
#if PIXEL_TEST_FAULT == 3
 extern void pixel_test_epoch(void);pixel_test_epoch();
#endif
}
int main(void){
 unsigned controls=0,copies=0,marks=0,samples=0;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 for(unsigned route=0;route<4;route++)for(unsigned value=0;value<256;value++){
  ugh_devices_reset();ugh_devices.seq_index=2;ugh_devices.gc_index=4;
  const unsigned ports[]={0x3c4,0x3c5,0x3ce,0x3cf};checkpoint();platform_out(ports[route],1,value);old_done();
  pixel_service_control_write((PixelControlRoute)route,(uint8_t)value);if(!match())return 11;controls++;
 }
 for(unsigned route=1;route<4;route+=2)for(unsigned value=0;value<256;value++){
  ugh_devices_reset();ugh_devices.seq_index=2;ugh_devices.gc_index=8;ugh_devices.seq[2]=(uint8_t)value;ugh_devices.gc[8]=(uint8_t)value;
  checkpoint();unsigned raw=platform_in(route==1?0x3c5:0x3cf,1);old_done();VideoByteReply now=pixel_service_control_read((PixelControlRoute)route);
  if(now.value!=raw || now.status || !match())return 11;controls++;
 }
 for(unsigned wm=0;wm<4;wm++)for(unsigned rm=0;rm<2;rm++)for(unsigned plane=0;plane<4;plane++)for(unsigned mask=0;mask<16;mask++){
  ugh_devices_reset();ugh_devices.gc[5]=(uint8_t)(wm|(rm<<3));ugh_devices.gc[8]=(uint8_t)(0x55^(mask*17));ugh_devices.gc[3]=(uint8_t)((mask&3)*8+(mask&7));
  ugh_devices.gc[0]=(uint8_t)mask;ugh_devices.gc[1]=(uint8_t)(mask^15);ugh_devices.gc[2]=(uint8_t)(mask^5);ugh_devices.gc[7]=(uint8_t)(mask^10);ugh_devices.map_mask=(uint8_t)mask;ugh_devices.read_map=(uint8_t)plane;
  const unsigned offsets[]={0,0x3e80,0x5293,0x59cd,0xf192,0xffff};
  for(unsigned k=0;k<6;k++){
   unsigned from=offsets[k],to=(from+4)&65535;for(unsigned p=0;p<4;p++){ugh_devices.plane[p][from]=(uint8_t)(p*43+mask*7+k*13);ugh_devices.plane[p][to]=(uint8_t)(0xf1-p*17);ugh_devices.latch[p]=(uint8_t)(0x23+p*51);}
   epoch();checkpoint();uint8_t v=ugh_read(0xa0000+from);ugh_write(0xa0000+to,v);old_done();
   uint8_t now=pixel_service_copy((VideoCellAddress){{0xa000},(uint16_t)from},(VideoCellAddress){{0xa000},(uint16_t)to});if(now!=v || !match())return 12;copies++;
  }
 }
 // Two consecutive copies in one epoch, second source is the first destination.
 for(unsigned mode=0;mode<2;mode++){
  ugh_devices_reset();ugh_devices.gc[5]=(uint8_t)mode;ugh_devices.map_mask=15;ugh_devices.gc[8]=255;
  for(unsigned p=0;p<4;p++)for(unsigned i=0;i<12;i++)ugh_devices.plane[p][i]=(uint8_t)(p*17+i*13);
  epoch();checkpoint();for(unsigned i=0;i<2;i++){uint8_t v=ugh_read(0xa0000+i*4);ugh_write(0xa0004+i*4,v);}old_done();
  for(unsigned i=0;i<2;i++)pixel_service_copy((VideoCellAddress){{0xa000},(uint16_t)(i*4)},(VideoCellAddress){{0xa000},(uint16_t)(4+i*4)});
  if(!match())return 15;
 }
 for(unsigned mode=0;mode<4;mode++)for(unsigned read=0;read<2;read++)for(unsigned plane=0;plane<4;plane++){
  ugh_devices_reset();ugh_devices.gc[5]=(uint8_t)(mode|(read<<3));ugh_devices.map_mask=15;ugh_devices.read_map=(uint8_t)plane;ugh_devices.gc[8]=0x40;ugh_devices.gc[3]=0x10;
  for(unsigned p=0;p<4;p++)ugh_devices.plane[p][0x59cd]=(uint8_t)(0x11+p*7);
  checkpoint();uint8_t old=ugh_read(0xa59cd);ugh_write(0xa59cd,0x40);old_done();
  uint8_t now=pixel_service_water_mark((VideoCellAddress){{0xa000},0x59cd});if(now!=old || !match())return 13;marks++;
 }
 const unsigned delta[]={0,3,5,0x720,0x723,0x725,0x240,0x245,0x480,0x485};
 for(unsigned n=0;n<3584;n++){
  unsigned pattern=n<1024?n:0,which=(n-1024)/256,byte=n&255,origin=n&1?0xfffe:0x100,plane=n&3;
  ugh_devices_reset();ugh_devices.read_map=(uint8_t)plane;
  for(unsigned p=0;p<4;p++)for(unsigned i=0;i<10;i++)ugh_devices.plane[p][(origin+delta[i])&65535]=(uint8_t)(p==plane ? (n<1024?((pattern&(1u<<i)?128:0)|(i+1)):((i==which)?byte:0)) : p*31+i);
  Regs a={0};a.cs=GAME_SEG;a.ds=DATA_SEG;a.es=0xa000;a.si=(uint16_t)origin;a.ax=0xab34;a.flags=0xed7;a.ss=0x8000;a.sp=0x100;Regs b=a;
  checkpoint();int old=l1_SamplePlayerCollisionPixels(&a);old_done();int now=c_SamplePlayerCollisionPixels(&b);
  if(old!=now || memcmp(&a,&b,sizeof a) || !match())return 14;samples++;
 }
 // Preserve the accepted unknown-tail and noncanonical-code compatibility,
 // including the near-call error stack prefix. These are external roles.
 for(unsigned kind=0;kind<3;kind++){
  ugh_devices_reset();Regs a={0};a.cs=kind==2?0x7777:GAME_SEG;a.ss=0x8000;a.sp=0x100;a.ax=0x7134;a.dx=0xbeef;a.flags=0xed7;Regs b=a;
  unsigned target=kind==0?G(EnableAllVgaWritePlanes):kind==1?0xffff:G(DrawTransparentSprite);
  checkpoint();int old=kind==2?ugh_call_near((uint16_t)target,0xbabe,&a):ugh_dispatch(a.cs,(uint16_t)target,&a);old_done();
  int now=kind==2?pixel_peer(PIXEL_PEER_DrawTransparentSprite,0xbabe,&b):pixel_tail((uint16_t)target,&b);
  if(old!=now || memcmp(&a,&b,sizeof a) || !match())return 17;
 }
 // Direct frame entries retain noncanonical control bindings, including DAC
 // delivery and unsupported-port error/log prefixes, rather than narrowing DX.
 int (*literal_frame[])(Regs*)={l1_DrawWaterSurfaceFrame0,l1_DrawWaterSurfaceFrame1,l1_DrawWaterSurfaceFrame2};
 int (*native_frame[])(Regs*)={c_DrawWaterSurfaceFrame0,c_DrawWaterSurfaceFrame1,c_DrawWaterSurfaceFrame2};
 for(unsigned f=0;f<3;f++)for(unsigned binding=0;binding<2;binding++){
  ugh_devices_reset();Regs a={0};a.cs=GAME_SEG;a.ds=0xa000;a.ss=0x8000;a.sp=0x100;a.di=0xfff4;a.ax=0x5401;a.bx=0x5655;a.cx=0x5857;a.dx=binding?0x2222:0x3c9;a.flags=0xed7;Regs b=a;
  wr16(a.ss,a.sp,0x4321);checkpoint();int old=literal_frame[f](&a);old_done();int now=native_frame[f](&b);
  if(old!=now || memcmp(&a,&b,sizeof a) || !match())return 18;
 }
 wr16(DATA_SEG,D(LastActiveTimerSlotOffset),30);timing_cold_import(ugh_mem);palette_cold_import(ugh_mem);input_cold_import(ugh_mem);video_pages_cold_import(ugh_mem);pixel_cold_import(ugh_mem);
 unsigned owned=0;for(unsigned a=0;a<UGH_MEM_SIZE;a++){unsigned n=(unsigned)timing_is_owned(a)+(unsigned)palette_is_owned(a)+(unsigned)input_is_owned(a)+(unsigned)video_pages_is_owned(a)+(unsigned)pixel_is_owned(a);if(n>1)return 16;owned+=n;}
 if(owned!=6439)return 16;pixel_require_seal(ugh_mem);
 printf("{\"controls\":%u,\"copies\":%u,\"marks\":%u,\"sampler_cases\":%u,\"live_alias_epochs\":2,\"compatibility_continuations\":3,\"compatibility_control_frames\":6,\"native_bytes\":%u}\n",controls,copies,marks,samples,owned);return 0;
}
'''
 source=folder/'backend.c';source.write_text(code)
 command=json.loads((OUT/'children/api-raster-composed-compile.json').read_text())['command']
 platform=folder/'platform.c';units=hostbuild.selected_units()+[dict(component='pixel_world')];platform.write_text(hostbuild.composition_source('c/platform.c',(ROOT/'c/platform.c').read_text(),units))
 command=[str(platform) if x==str(OUT/'api/raster/composed/platform.c') else x for x in command]
 if fault:command.append('-DPIXEL_TEST_FAULT='+str(fault))
 command=[x for x in command if x!='-shared'];command[command.index('-o')+1]=str(folder/'backend.exe');command.extend([str(source),'-Wno-misleading-indentation'])
 bounded(command,'backend-compile-'+str(fault))
 if fault:
  capture=folder/'capture.py';capture.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n')
  r=bounded([sys.executable,capture,folder/'backend.exe'],'backend-defect-'+str(fault));actual=json.loads(r['stdout']);assert actual['returncode'] in [11,12,13,14,15],actual
  if fault==3:assert actual['returncode']==15,'Snapshot must be caught by same-epoch read-after-write'
  if fault==7:assert actual['returncode']==14,'Dropped read must be caught by the actual sampler'
  return dict(defect={1:'wrong-lane-mask',2:'stale-read-plane',3:'frame-start-copy-snapshot',4:'clipped-destination',6:'missing-OR-40h-mark',7:'dropped-collision-read'}[fault],result='DETECTED',exit=actual['returncode'])
 r=bounded([folder/'backend.exe'],'backend-run');save(OUT/'backend.json',dict(result='PASS',counts=json.loads(r['stdout']),scope='Actual model vs typed control/copy/mark; full RAM, ABI for sampler, full Devices/logs. Every write/read mode, read plane and lane mask with 16 representative coupled control tuples; all 1024 high-bit masks and 256 replies at each of ten sample positions; full inherited-domain admission retained.'))

def borrowers():
 source=inspect.getsource(palette.borrowers)
 source=source.replace("m.off('GAME:BaseRgbPalette')","m.off('GAME:SpritePlaneStateScratch')").replace("m.off('GAME:FadedRgbPalette')","m.off('GAME:RendererScratchWord')")
 source=source.replace("OUT/'api'/v/'api.dll'","OUT/'api/raster'/v/'api.dll'")
 source=source.replace('[0x681,0x682,0x981,0xc81]','[0x600]').replace('ES=game+0x400','ES=game+0x400')
 env=dict(palette.__dict__);exec(source,env);env['borrowers']()
 r=json.loads((OUT/'borrowers.json').read_text());r.pop('excluded_probe',None);r['scope']='Independent L1/composed alias windows through renderer scratch: copy, decimal, duplicate and palette source mutation; real ICE output includes the four renderer bytes and stops before page metadata. Immutable decoder tables remain disjoint.';save(OUT/'borrowers.json',r)

def census():
 target=snapshot();p=target/'verif/standalone_census.py';text=p.read_text();marker="        if source=='native/bridge/timing_world_bridge.c' and name in {";assert text.count(marker)==1
 leaves={
 'input_world':['input_field','input_field_get','input_field_put','input_is_owned','input_shared_read','input_shared_write','input_borrowed_byte','input_borrowed_store'],
 'palette_world':['palette_index','palette_get','palette_put','palette_address','palette_is_owned','palette_shared_read','palette_shared_write','palette_borrowed_byte','palette_borrowed_store'],
 'video_pages':['video_pages_index','video_pages_get_word','video_pages_put_word','video_pages_is_owned','video_pages_shared_read','video_pages_shared_write','video_pages_borrowed_byte','video_pages_borrowed_store'],
 'pixel_world':['pixel_index','pixel_get_word','pixel_put_word','pixel_is_owned','pixel_shared_read','pixel_shared_write','pixel_borrowed_byte','pixel_borrowed_store']}
 addition=''
 for unit,names in leaves.items():
  addition+="        if source=='native/bridge/"+unit+"_bridge.c' and name in "+repr(set(names))+":\n            assert not re.search(r'\\b(?:l1_\\w+|ugh_dispatch\\w*|ugh_call_near\\w*|platform_\\w+)\\s*\\(',text[b+1:e])\n            continue\n"
 p.write_text(text.replace(marker,addition+marker));bounded([sys.executable,'verif/standalone_census.py','--all'],'census-run',target)
 folder=target/'build/workers/close-adlx-19';summary=json.loads((folder/'census.json').read_text());assert len(summary['scenarios'])==21 and all(not s['fallback_calls'] and not s['l1_body_calls'] for s in summary['scenarios'])
 names={'c_'+n for n in NAMES}|{'actor_render_session_'+n for n in ['GAME_ERASE','GAME_DRAW','GAME_OVERLAY']};counts=[];edges=[]
 paths=set(BRIDGES+['native/bridge/pixel_world_bridge.c'])
 for p in sorted((folder/'detail').glob('*.json')):
  run=json.loads(p.read_text());counted={f['name']:f['count'] for f in run['bodies'] if f['path'] in paths}
  counts.append(dict(scenario=run['scenario'],entries={name:counted.get(name,0) for name in sorted(names)}))
  for edge in run['machine_edges']:
   if edge['kind'] in ['ABI-entry','interrupt-delivery']:continue
   if edge['bridge'].get('path') in paths or edge['bridge'].get('name') in names|{'pixel_peer','pixel_tail','ww_tail','ww_random','ww_respawn','physics_sample'}:edges.append(dict(scenario=run['scenario'],**edge))
 assert not edges,edges[:5]
 from closure_support import function
 for bridge in BRIDGES+['native/bridge/pixel_world_bridge.c']:
  pre=OUT/(Path(bridge).stem+'.i');bounded([timing.common.GCC,'-E','-P','-DUGH_NATIVE_PIXEL','-I',ROOT/'c','-I',ROOT/'native/bridge',ROOT/bridge,'-o',pre],'census-preprocess-'+Path(bridge).stem)
  # The preprocessor includes declarations for all old services; audit only actual definitions.
  for n in re.findall(r'\b(?:EXPORT\s+)?(?:static\s+)?(?:inline\s+)?(?:int|void|uint8_t|uint16_t|uint32_t)\s+(\w+)\([^;{}]*\)\s*\{',pre.read_text()):
   if n.startswith('platform_'):continue
   body=function(pre.read_text(),n)
   assert not re.search(r'\b(?:ugh_dispatch\w*|ugh_call_near\w*|platform_in|platform_out|platform_interrupt|platform_service_point_at|platform_frame_boundary)\s*\(',body),(bridge,n,'raw edge')
 model=json.loads((ROOT/'metadata/program-model.json').read_text());unreached=[]
 for n in NAMES:
  if any(r['entries']['c_'+n] for r in counts):continue
  routine=model['routines']['GAME:'+n];indirect=[k for k,v in model['indirect_sites'].items() if routine['address'] in v.get('targets',[])]
  unreached.append(dict(entry=n,static_callers=routine['callers'],indirect_callers=indirect,coverage='Accepted direct API cases; no synthetic caller injected into a maintained scenario'))
 save(OUT/'census.json',dict(result='PASS',summary=summary,per_scenario_counts=counts,unreached=unreached,in_island_machine_edges=edges,scope='All five migrated caller bridges plus pixel owner/peer/tail and typed pixel-IO adapters; verification provider remains external.'))


REGRESSION_C=r'''
#include "platform.h"
#include "pixel_regression.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned frame,depth,registered;static struct {unsigned kind;uint16_t ax,bx,cx;} contexts[128];
static unsigned written[4][65536],writer[4][65536];static unsigned long long seen[5],save_sprite,calls[14];
void ph_dump(void){const char *path=getenv("PIXEL_REGRESSION_OUTPUT");if(!path)return;FILE *f=fopen(path,"wb");if(!f)abort();fprintf(f,"{\"departure_292_sprite219_59CD\":%llu,\"rectangle_23_same_frame_read\":%llu,\"water_897_5293\":%llu,\"water_899_F192\":%llu,\"save_same_frame_read\":%llu,\"save_reads_prior_sprite\":%llu,\"frames\":%u}\n",seen[0],seen[1],seen[2],seen[3],seen[4],save_sprite,frame);fclose(f);char count_path[4096];if(snprintf(count_path,sizeof count_path,"%s.counts",path)<0)abort();f=fopen(count_path,"wb");if(!f)abort();fprintf(f,"[");for(unsigned i=1;i<14;i++)fprintf(f,"%s%llu",i>1?",":"",calls[i]);fprintf(f,"]\n");fclose(f);}
void ph_enter(unsigned kind,Regs *r){if(!registered){atexit(ph_dump);registered=1;}if(depth>=128)abort();calls[kind]++;contexts[depth].kind=kind;contexts[depth].ax=r->ax;contexts[depth].bx=r->bx;contexts[depth].cx=r->cx;depth++;}
void ph_leave(unsigned kind){if(!depth || contexts[depth-1].kind!=kind)abort();depth--;if(kind==4)frame++;}
void ph_read(uint32_t a){
 if(!depth)return;
 unsigned kind=contexts[depth-1].kind,o=(uint16_t)a,recent=0,sprite=0;
 for(unsigned p=0;p<4;p++)if((ugh_devices.map_mask&(1u<<p)) && written[p][o]==frame+1){recent=1;sprite|=writer[p][o]==1;}
 if(kind==2 && frame==23 && recent)seen[1]++;
 if(kind==3 && recent){seen[4]++;if(sprite)save_sprite++;}
 if(frame==899 && a==0xaf192)seen[3]++;
}
void ph_write(uint32_t a){
 unsigned o=(uint16_t)a,kind=depth?contexts[depth-1].kind:0;
 if(kind==1 && frame==292 && a==0xa59cd && contexts[depth-1].ax==219 && contexts[depth-1].bx==144 && contexts[depth-1].cx==65535)seen[0]++;
 if(frame==897 && a==0xa5293)seen[2]++;
 if(frame==899 && a==0xaf192)seen[3]++;
 for(unsigned p=0;p<4;p++)if(ugh_devices.map_mask&(1u<<p)){written[p][o]=frame+1;writer[p][o]=kind;}
}
'''

def regressions():
 from closure_support import function
 target=snapshot();folder=OUT/'regressions';folder.mkdir(exist_ok=True)
 # Generated instrumented copy; maintained host/C/native sources remain untouched.
 for top in ['c','native','host','metadata','tools','verif','src']:shutil.copytree(target/top,folder/top,dirs_exist_ok=True)
 shutil.copytree(target/'build/link',folder/'build/link',dirs_exist_ok=True)
 (folder/'c/pixel_regression.h').write_text('void ph_enter(unsigned,Regs*);void ph_leave(unsigned);void ph_read(uint32_t);void ph_write(uint32_t);\n')
 (folder/'host/pixel_regression.c').write_text(REGRESSION_C)
 p=folder/'c/memory.c';text=p.read_text().replace('uint16_t o=(uint16_t)a;','ph_read(a);uint16_t o=(uint16_t)a;',1).replace('unsigned rotate=','ph_write(a);unsigned rotate=',1);p.write_text('#include "platform.h"\n#include "pixel_regression.h"\n'+text)
 for bridge,entries in [('render_primitives',[(1,'DrawTransparentSprite'),(2,'RestoreBackgroundRectangle'),(3,'SaveDrawPageBackground')]),('video_dos',[(4,'SwapAndDisplayVgaPage')]),('water_weather',list(enumerate(['AdvanceWaterSurface','DrawWaterSurface','DrawWaterSurfaceFrame0','DrawWaterSurfaceFrame1','DrawWaterSurfaceFrame2','AdvanceRainParticles','RespawnRainParticle','DrawRainParticles','RestoreRainBackground'],5)))]:
  p=folder/('native/bridge/'+bridge+'_bridge.c');text=p.read_text();wrappers=[]
  for number,name in entries:
   body=function(text,'c_'+name);renamed=body.replace('c_'+name+'(','ph_observed_'+name+'(',1);assert renamed!=body;text=text.replace(body,renamed)
   wrappers.append('EXPORT int c_'+name+'(Regs *r){ph_enter('+str(number)+',r);int status=ph_observed_'+name+'(r);ph_leave('+str(number)+');return status;}\n')
  p.write_text('#include "platform.h"\n#include "pixel_regression.h"\n'+text+'\n'+''.join(wrappers))
 bounded([sys.executable,'tools/hostbuild.py'],'regressions-build',folder)
 import wholegame,cgen,os
 rows=[];mz,_=cgen.read_symbols()
 for name in ['departure','water-physics','random-rain']:
  script=ROOT/'verif/random_rain.txt' if name=='random-rain' else ROOT/('tests/scenarios/'+name+'.txt')
  candidates=[ROOT/('build/whole/'+name+'.ref.json'),ROOT/'build/workers/close-stones-12/rain/random-rain.ref.json']
  import vga_state_census
  spec=wholegame.scenario(script);m,initial=wholegame.fixture(spec)
  try:reference,path=vga_state_census.reference(script,m)
  except RuntimeError:
   # A tool-provenance change invalidates an old key. Rebuild only from ASM,
   # never patch an expected digest or derive a reference from the native host.
   frames,coverage,_=wholegame.original(spec,m,initial);reference=dict(key=wholegame.identity(script,m),version=wholegame.VERSION,frames=frames,coverage=coverage)
   path=folder/(name+'.ref.json');save(path,reference)
  capture=folder/'capture.py';capture.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n')
  result=folder/(name+'.json');os.environ['PIXEL_REGRESSION_OUTPUT']=str(result)
  frames=wholegame.scenario(script)['frames'];r=bounded([sys.executable,capture,folder/'build/host/ugh.exe','--headless',str(frames),'--script',script,'--timeout','590'],'regressions-'+name)
  os.environ.pop('PIXEL_REGRESSION_OUTPUT',None);actual=json.loads(r['stdout']);assert actual['returncode']==0,actual['stderr']
  records=[json.loads(line) for line in actual['stdout'].splitlines()];assert records==reference['frames'],(name,'instrumented composed host differs from independent rebuilt-ASM reference')
  seen=json.loads(result.read_text());entry_counts=json.loads(Path(str(result)+'.counts').read_text());entry_names=['DrawTransparentSprite','RestoreBackgroundRectangle','SaveDrawPageBackground','SwapAndDisplayVgaPage','AdvanceWaterSurface','DrawWaterSurface','DrawWaterSurfaceFrame0','DrawWaterSurfaceFrame1','DrawWaterSurfaceFrame2','AdvanceRainParticles','RespawnRainParticle','DrawRainParticles','RestoreRainBackground'];rows.append(dict(scenario=name,counts=seen,entries=dict(zip(entry_names,entry_counts)),reference=str(path),key=reference['key']))
  if name=='departure':assert seen['departure_292_sprite219_59CD']>0,seen
  if name=='water-physics':assert seen['water_897_5293']>0 and seen['water_899_F192']>0,seen
  if name=='random-rain':assert seen['rectangle_23_same_frame_read']>0,seen
  assert seen['save_same_frame_read']>0 and seen['save_reads_prior_sprite']>0,seen
 save(OUT/'regressions.json',dict(result='PASS',runs=rows,scope='Instrumented composed host matches every reference frame; exact named service/frame/address predicates and live per-lane same-frame provenance. Observer data never enters RAM/Devices.'))

def defects():
 rows=[backend(f) for f in [1,2,3,4,6,7]]
 target=snapshot();folder=OUT/'defects/missed-serialization'
 for top in ['c','native','host','metadata','tools','verif','src']:shutil.copytree(target/top,folder/top,dirs_exist_ok=True)
 shutil.copytree(target/'build/link',folder/'build/link',dirs_exist_ok=True)
 p=folder/'tools/hostbuild.py';s=p.read_text().replace("return (['-DUGH_NATIVE_PIXEL']","return ['-DPIXEL_TEST_FAULT=5']+(['-DUGH_NATIVE_PIXEL']",1);p.write_text(s)
 bounded([sys.executable,'tools/hostbuild.py'],'defect-serialization-build',folder)
 capture=folder/'capture.py';capture.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n')
 r=bounded([sys.executable,capture,folder/'build/host/ugh.exe','--headless','48','--script',target/'tests/scenarios/gameplay-adlib.txt','--timeout','590'],'defect-serialization-run');actual=json.loads(r['stdout']);assert actual['returncode']==88 and 'missed serialization' in actual['stderr'],actual
 rows.append(dict(defect='missed-serialization',result='DETECTED',exit=88));save(OUT/'defects.json',dict(result='PASS',controls=rows))


def inventory():
 import cgen
 _,symbols=cgen.read_symbols();model=json.loads((ROOT/'metadata/program-model.json').read_text());moved=[]
 for n in ['SpritePlaneStateScratch','RendererScratchWord']:
  s=symbols['GAME:'+n];moved.append(dict(symbol='GAME:'+n,address=(cgen.LOAD+s['frame'])*16+s['offset'],bytes=2,model=model['variables'][n]))
 assert moved[1]['address']==moved[0]['address']+2
 raw_users=[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'native').rglob('*.c')) if re.search(r'\bugh_mem\b',p.read_text())]
 allowed={'native/bridge/'+n+'_bridge.c' for n in ['adlx_loader','audio_world','decimal','far_copy','ice','ice_scratch','input_world','palette_world','timing_world','video_pages','pixel_world']};assert set(raw_users)<=allowed,set(raw_users)-allowed
 shared={n:model['variables'][n] for n in ['WaterYPixels','WaterY32','PlayerCachedSpriteIds','PlayerCachedPixelX','PlayerCachedPixelY','ActorEraseSprite','ActorEraseOverlaySprite','ActorPreviousDrawX','ActorPreviousDrawY']}
 deferred={n:v for n,v in model['variables'].items() if n.startswith(('HudCached','HudDigit','RainParticle','RainPrevious','WaterSurface')) or n in ['WaterRestorePending','WaterStepPhase','CachedTimerBarWidth','HudFareClearPending','PreviousWaterSurfaceY']}
 save(OUT/'ownership.json',dict(result='PASS',before=6435,added=4,after=TOTAL,moved=moved,shared_stay_put=shared,deferred_HUD_weather_ownership=deferred,raw_window_adapters=raw_users,
  alias_findings=['RendererScratchWord also has level-loader setup/read uses; loader is an explicit borrower of the same native word, not a second owner','Rain slot 193 continues to alias the following physical array region; its complete ownership cut must audit that finding and all allocated bytes','DecimalDigitBuffer current/prior windows are shared with decimal conversion; they are not duplicated into the renderer owner'],
  compatibility='No VGA default-state restriction. Four planes, hidden/padding cells, latches and all inherited controls remain the hardware provider. Unknown frame tails and noncanonical code bindings keep an opaque typed external continuation, decoded only by the verification provider.',
  remaining='HUD/cache/history and weather/rain state ownership; actor/player histories and Water Y stay canonical for the world cut. No raw plane service remains in the five composed caller bridges.'))


def finalize():
 results={n:json.loads((OUT/(n+'.json')).read_text()) for n in ['api-raster','api-world','router','proof','backend','borrowers','census','levels','regressions','defects']};assert all(r['result']=='PASS' for r in results.values())
 for group in ['raster','world']:
  receipt=results['api-'+group];assert not receipt['explicit_out_of_domain']
  for f,h in receipt['seam_inputs'].items():
   if f.startswith(('native/','c/')) or f=='tools/hostbuild.py':assert sha(ROOT/f)==h,(f,'API source replay required')
 runs=[json.loads(p.read_text()) for p in (OUT/'projector/runs').glob('*.json')];assert len(runs)==21 and all(r['canonical_native_owned_bytes']==TOTAL and not r['native_owned_journal_publications'] for r in runs)
 assert len(results['defects']['controls'])==7
 inventory();p=ROOT/'metadata/closure/pixel_world.json';c=json.loads(p.read_text());c['proposed_status']='migrated'
 c['purpose']='Standalone step 4 pixel-service cut: all renderer/HUD/weather/actor/physics pixel paths and exclusive renderer scratch. HUD/weather ownership remains a recorded continuation.'
 c['interface']={'inputs':'Live typed control, source/collision/copy/mark requests; native renderer words; explicit shared state borrowers','outputs':'Full read replies, ordered live pixel/control effects, native-only renderer ownership and separate observation serialization'}
 c['indirect']=['Closed native near/tail roles for ordinary GAME bindings','Accepted unknown frame tails and noncanonical bindings retain an opaque typed external continuation; verification provider preserves the old dispatch/near ABI and error prefixes; unobserved in maintained scenarios']
 c['uncertainty']=['Partial step 4: HUD/history, rain and weather native ownership remain; their buffers and the slot-193 alias need a separate ownership audit','Shared Water Y, player draw caches and actor render histories remain with their canonical world owners','Full inherited VGA controls retained. No production provider or narrower compatibility decision is chosen.']
 c['memory']['owner']='NativePixelWorld.plane_state/water_distance: GAME:45FC..45FF, four bytes; loader and byte windows are explicit borrowers'
 c['assumptions']=list(dict.fromkeys(['Accepted renderer, HUD, water/weather and player physics semantic/data/stack/resource domains remain unchanged','VGA services are synchronous: live full-byte reads update all four latches; writes obey inherited controls and unclipped word-address reductions','Opaque external compatibility continuations preserve admitted unknown/noncanonical bindings; unknown typed enum requests fail closed','Actual-C B covers the new owner and service/sampler seams; no monolithic whole-handler or complete hardware A/B theorem is claimed','Cold import is verification fixture setup only; moved RAM stays sealed and serialization is observation-only']))
 c['eliminated']=['RAM ownership of renderer scratch; raw pixel/control ports and internal machine call edges in the five composed caller bridges']
 c['retained']=['Both page layouts, hidden storage/padding, foreign latches, full inherited GC/SEQ controls, live copy sources and unclipped destinations','Full-byte ten-read collision order and independent word reductions; water OR-40 recipe; every existing branch/cursor/animation and scalar quirk','Unknown frame/noncanonical-code literal compatibility remains only through an explicit typed external service; no broken hook repaired']
 total=sum(results['api-'+g]['composed_matching'] for g in ['raster','world'])
 c['evidence']=[dict(property='New owner and pixel/sampler seams',level='B',method=results['proof']['scope'],command='python verif/pixel_composition.py --proof --router',result='PASS: three actual-C profiles; all physical router cells; 131072 word roundtrips and 1024 byte writes',date='2026-11-15'),
 dict(property='API, actual hardware provider, borrowers and retained continuation prefixes',level='C',method='Independent Unicorn and L1; compiled full RAM/Devices/ordered service effects and ABI; complete collision bit-pattern/full-byte reply slices',command='python verif/pixel_composition.py --api --backend --borrowers',result=f'PASS: {total} legacy and composed API matches each; 0 declines; 3584 generated sampler cases, 3072 copies, 32 marks; 3 compatibility continuation cases',date='2026-11-15'),
 dict(property='Composition and named regressions',level='D',method='Committed-baseline archive, scratch promotion, independent rebuilt-ASM references; all projector boundaries and exact named frame/address/provenance witnesses',command='python verif/pixel_composition.py --build --projector --census --regressions --levels',result=f'PASS: 51/0 closure; 21/21 each host variant; {sum(r["boundaries"] for r in runs)} boundaries, 6439 native bytes, 0 moved publications; zero L1 game bodies/fallbacks/island machine edges; 81+7+8 levels each variant; departure 292, rain 23, water-physics 897/899 and same-frame save regressions',date='2026-11-15'),
 dict(property='Seeded defects',level='C',method='Actual consuming service/sampler paths plus host serialization guard',command='python verif/pixel_composition.py --defects',result='PASS: all seven detected; snapshot caught in one live copy epoch and dropped read by actual ten-sample handler',date='2026-11-15')]
 save(p,c);relock(final=True)
 save(OUT/'verification-receipt.json',dict(result='PASS',status='unanalyzed',proposed_status='migrated',scope='Partial step 4: all pixel services and four renderer bytes; HUD/weather ownership deferred',baseline=json.loads((OUT/'baseline.json').read_text()),evidence={n:sha(OUT/(n+'.json')) for n in results},relocks=json.loads((OUT/'relocks.json').read_text())))


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['locks','inventory','api','api-raster','api-world','router','proof','backend','borrowers','build','projector','census','regressions','levels','defects','finalize','gate','internal']:p.add_argument('--'+n,action='store_true')
 a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
 if a.locks:relock()
 if a.api:
  for group in ['raster','world']:bounded([sys.executable,__file__,'--api-'+group,'--internal'],'api-'+group+'-child')
 if a.gate:
  relock()
  for n in ['inventory','router','proof','api-raster','api-world','backend','borrowers','build','projector','census','regressions','levels','defects']:bounded([sys.executable,__file__,'--'+n,'--internal'],n+'-child')
  finalize();build();return
 for n in ['inventory','api-raster','api-world','router','proof','backend','borrowers','build','projector','census','regressions','levels','defects','finalize']:
  if getattr(a,n.replace('-','_')):
   if a.internal:
    if n.startswith('api-'):api(n[4:])
    else:globals()[n]()
   else:bounded([sys.executable,__file__,'--'+n,'--internal'],n+'-child')
if __name__=='__main__':main()
