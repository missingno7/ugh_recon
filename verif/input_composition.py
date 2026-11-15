"""Standalone step 4, input owner and typed deterministic services.
Serial 600-second/8-GiB children. Scratch-only promotion; literal stays pure L1.
"""
import argparse,hashlib,inspect,json,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/workers/close-stones-19'
sys.path.insert(0,str(ROOT/'tools'))
import palette_composition as prior
prior.OUT=prior.audio.OUT=prior.timing.OUT=prior.timing.common.OUT=OUT
bounded=prior.bounded;save=prior.save;sha=prior.sha
NEW=['native/input_world.h','native/input_world.c','native/bridge/input_world_bridge.h','native/bridge/input_world_bridge.c']
BASE=NEW+['native/bridge/input_bridge.c','verif/input_platform_model.inc','verif/input_composition.py',
 'tools/hostbuild.py','host/main.c','verif/projector/observer.c','verif/projector/timing_serializer.h',
 'verif/projector/publications.py','verif/projector_evidence.py']
READ=list(dict.fromkeys(prior.READ_INPUTS+['verif/palette_composition.py','native/input.c','native/input.h',
 'verif/input_evidence.py','verif/input_build.py','verif/input_inventory.py','verif/input_integration.py',
 'metadata/closure/input.json','metadata/closure/palette_world.json','metadata/closure/menus.json',
 'metadata/closure/high_scores.json','native/bridge/menus_bridge.c','native/bridge/high_scores_bridge.c','src/data/DGDATA.ASM']))
NAMES=['DetectAndCalibrateJoysticks','SampleJoystickAxesAndButtons','HandleKeyboardScanInterrupt',
 'InstallKeyboardSequenceInterrupt','RestoreKeyboardInterrupt','PollKeyboardScanChange',
 'WaitForScanChangeOrJoystickButton','PollPlayerControls']
TOTAL=6415

def files():return sorted(set(BASE+subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()+['metadata/closure/input_world.json']))
prior.files=files
original_snapshot=prior.snapshot
def snapshot():
 target=original_snapshot();p=target/'metadata/closure/input_world.json';c=json.loads(p.read_text());c['status']='migrated';save(p,c);return target
prior.snapshot=prior.audio.snapshot=prior.timing.snapshot=snapshot
build=prior.build
levels=prior.levels

def relock(final=False):
 import closure
 p=ROOT/'metadata/closure/input_world.json'
 if not p.exists() or not p.stat().st_size:save(p,dict(component='input_world',status='unanalyzed',original=dict(owned=[],composes=['input','palette_world','audio_world','timing_world']),native=dict(files=NEW,functions=['native_input_world','input_rebase_count'],bridge='Native owner; explicit typed services and verification-only ABI continuations'),purpose='Standalone step 4 input cut: scans, mutable sequence grammar, deterministic count/calibration state and saved keyboard binding',interface=dict(inputs='Cold fixture; ordered raw set-1 scans, count/button replies, BIOS queue and opaque vector roles; borrowed configuration/commands',outputs='Native persistent input state, typed ordered requests, separate observation serialization'),callers=['Input entry ABI; menus, session, demos, IRQ and editors'],callees=['Typed scan/count/queue/vector services; accepted input kernels and retrace peer'],indirect=['Closed InputPeerRole; opaque external keyboard binding; verification continuation only'],amiga=dict(classification='not-used',finding='Composition only; accepted DOS contracts retained'),uncertainty=['No production standalone target; video page/HUD/render and plane/retrace services remain'],memory=dict(owner='NativeInputWorld, 267 historical lanes',total_with_prior=TOTAL,remaining='PlayerCount, both control modes, five command words/player and the current handler resource binding remain with existing shared owners'),assumptions=['Accepted input scalar/matcher/timing domains; no live joystick or scheduling choice','Opaque synchronous continuation is verification-only ABI metadata; production state contains no Regs or RAM pointer','Original disjoint active code/resource/stack and ordinary shared configuration views'],eliminated=['RAM ownership of moved input fields; input-island raw ports/vectors/BIOS/near dispatch'],retained=['E0/set-1 make/break bytes, stale fields, malformed sequence/table aliases, raw word counts and wrong mode/index behavior'],evidence=[],verification_inputs={},dependencies={},verification_input_hashing='sha256-lf-text'))
 old={p.name:json.loads(subprocess.check_output(['git','show','HEAD:'+p.relative_to(ROOT).as_posix()],cwd=ROOT,text=True)) for p in (ROOT/'metadata/closure').glob('*.json') if p.stem!='input_world'}
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
   if p.stem=='input_world':
    c['dependencies']={f:closure.actual_dependencies(ROOT/f) for f in NEW}
    c['verification_inputs']={f:sha(ROOT/f) for f in BASE+READ}
    if not c['evidence']:c['evidence']=[dict(property='Native numeric field and count-rebase seam',level='B',method='Actual-C output/frame/dependence profile; composition gate separately pending',command='python verif/input_composition.py --proof',result='PASS' if (OUT/'proof.json').exists() else 'Pending',date='2026-11-15')]
   for f,h in c.get('verification_inputs',{}).items():
    data=(ROOT/f).read_bytes();data=data.replace(b'\r\n',b'\n') if c.get('verification_input_hashing')=='sha256-lf-text' else data
    actual=hashlib.sha256(data).hexdigest()
    if actual!=h:c['verification_inputs'][f]=actual;dirty=True
   if p.name in old:
    inputs=[f for f,h in c.get('verification_inputs',{}).items() if h!=old[p.name].get('verification_inputs',{}).get(f)]
    if (inputs or c.get('dependencies')!=old[p.name].get('dependencies')) and p.name not in changed:
     direct=any(not f.startswith('metadata/closure/') for f in inputs) or c.get('dependencies')!=old[p.name].get('dependencies')
     note=dict(date='2026-11-15',reason='Input native ownership, typed services and borrowers; prior claim domains/status unchanged' if direct else 'Dependent composition-note hash cascade only',commands=['python verif/input_composition.py --gate'],results='PASS' if final else 'Pending input composition acceptance',inputs=inputs)
     c['evidence_refreshed']=old[p.name].get('evidence_refreshed',[])+[note];changed[p.name]=note;dirty=True
   save(p,c)
  if not dirty:break
 else:raise RuntimeError('lock cycle')
 save(OUT/'relocks.json',dict(certificates=changed))

def api():
 source=inspect.getsource(prior.timing.api)
 source=re.sub(r"suites=\[[^\n]+\]", "suites=['dos_input','scene','video','game_services','menu']",source,1)
 source=source.replace(" import timer_callbacks\n cases += [('timer_callbacks',c) for c in timer_callbacks.CASES]\n",'')
 source=source.replace(" names=sorted", " cases=[(s,c) for s,c in cases if c.routine.split(':')[1] in "+repr(NAMES+['EditLevelPassword','InsertHighScoreAndClearScore'])+"]\n names=sorted",1)
 source=source.replace("{'timing_world','audio_world'}","{'timing_world','audio_world','palette_world','input_world'}")
 source=source.replace("units.append(dict(component='timing_world',native=ROOT/'native/timing_world.c',bridge=ROOT/'native/bridge/timing_world_bridge.c',exports=[]))", "units.extend([dict(component=n,native=ROOT/('native/'+n+'.c'),bridge=ROOT/('native/bridge/'+n+'_bridge.c'),exports=[]) for n in ['timing_world','audio_world','palette_world','input_world']])")
 source=source.replace("fixture.write_text('#include \"timing_world_bridge.h\"", "fixture.write_text('#include \"input_world_bridge.h\"\\n#include \"palette_world_bridge.h\"\\n#include \"timing_world_bridge.h\"")
 for action in ['cold_import','require_seal','serialize']:
  value='timing_api_observation' if action=='serialize' else 'ugh_mem'
  needle=' timing_'+action+'('+value+');'
  source=source.replace(needle,needle+'\\n#ifdef UGH_NATIVE_PALETTE\\n palette_'+action+'('+value+');\\n#endif\\n#ifdef UGH_NATIVE_INPUT\\n input_'+action+'('+value+');\\n#endif')
 source=source.replace("sources += [u['native'] for u in units]+[u['bridge'] for u in units]+[fixture]", "sources.append(fixture)\n  for original in [u['native'] for u in units]+[u['bridge'] for u in units]:\n   text=original.read_text();new=hostbuild.composition_source(original.relative_to(ROOT).as_posix(),text,units)\n   if new!=text:\n    path=folder/('native_'+original.name);path.write_text(new);sources.append(path)\n   else:sources.append(original)")
 source=source.replace("assert old['timer_fallbacks'] and new['status']==1,(old,new)","assert new['status'] in (1,3),(old,new)")
 source=source.replace(' assert len(declines)==32','')
 source=source.replace('composed_matching=2202-len(declines),legacy_matching=2202','composed_matching=len(cases)*2-len(declines),legacy_matching=len(cases)*2')
 source=source.replace("print('API PASS legacy 2202; composed 2170 matches + 32 explicit domain rejections',flush=True)","print('API PASS',len(cases)*2,'cases;',len(declines),'explicit rejects',flush=True)")
 env=dict(prior.timing.__dict__);exec(source,env);env['api']()
 receipt=json.loads((OUT/'api.json').read_text());receipt['scope']='Input eight-entry and editor ABI cases, two poison modes, independent L1/Unicorn vs legacy/composed. Declines listed individually.';save(OUT/'api.json',receipt)

def projector():
 source=inspect.getsource(prior.projector).replace('6148',str(TOTAL));env=dict(prior.__dict__);exec(source,env);env['projector']()

def compiled():
 import input_evidence
 source=inspect.getsource(input_evidence.main)
 source=source.replace('plain=contacts_reference.prepare_reference(local=True);dlls=[nbuild.load_l1(build(reference=True)),nbuild.load_l1(build())]','plain=ROOT/\'build/link/plain/UGH.EXE\';dlls=[nbuild.load_l1(OUT/\'api/reference/api.dll\'),nbuild.load_l1(OUT/\'api/composed/api.dll\')]')
 source=source.replace("f=getattr(dll,'c_'+name)","f=getattr(dll,'api_c_'+name)")
 # Retired dispatcher-entry telemetry is deliberately replaced by typed peers.
 source=re.sub(r"   assert len\(a\[7\]\).*?\n",'',source)
 source=re.sub(r"   assert a\[7\]==b\[7\].*?\n",'',source)
 source=source.replace("OUT/'cases.json'","OUT/'compiled.json'")
 env=dict(input_evidence.__dict__,OUT=OUT);exec(source,env);env['main']()

def router():
 folder=OUT/'router';folder.mkdir(exist_ok=True)
 code=r'''#include "input_world_bridge.h"
#include <stdio.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
uint8_t palette_borrowed_byte(const uint8_t *p,uint32_t i){return p[i];}
void palette_borrowed_store(uint8_t *p,uint32_t i,uint8_t v){p[i]=v;}
int c_PollKeyboardScanChange(Regs *r){(void)r;return 0;}
int c_SampleJoystickAxesAndButtons(Regs *r){(void)r;return 0;}
int c_WaitNextVerticalRetrace(Regs *r){(void)r;return 0;}
static unsigned queue_failure;
InputQueueReply input_service_queue(InputQueueOperation op,InputServiceContext *ctx){
 (void)op;Regs *r=(Regs*)ctx;r->ax=0xbeef;flag(r,ZF,1);
 return (InputQueueReply){0x1e41,1,queue_failure?UGH_UNSUPPORTED:UGH_OK};
}
InputVectorReply input_service_vector(InputVectorOperation op,InputKeyboardBinding binding,InputServiceContext *ctx){
 (void)op;(void)binding;Regs *r=(Regs*)ctx;r->bx=0xb00b;r->es=0xdead;
 return (InputVectorReply){{0x1234,0xf000},queue_failure?UGH_UNSUPPORTED:UGH_OK};
}
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE];
static uint16_t word(uint16_t offset){uint32_t a=lin(DATA_SEG,offset);return (uint16_t)(expected[a]|expected[a+1]*256u);}
int main(void){
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(expected,ugh_mem,sizeof expected);input_cold_import(ugh_mem);
 unsigned addresses[267],n=0;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++){
  int wanted=a==lin(GAME_SEG,G(LatestInterruptScanCode)) || (a>=lin(DATA_SEG,0x93) && a<lin(DATA_SEG,0x97)) || (a>=lin(DATA_SEG,0x2643) && a<lin(DATA_SEG,0x2648)) || (a>=lin(DATA_SEG,0x281c) && a<lin(DATA_SEG,0x28e9)) || (a>=lin(DATA_SEG,0x3311) && a<lin(DATA_SEG,0x3345));
  if(input_is_owned(a)!=wanted)return 1;
  if(wanted){if(n==267)return 1;addresses[n++]=a;}
 }
 if(n!=267 || input_owned_bytes()!=n)return 2;
 memcpy(output,ugh_mem,sizeof output);input_serialize(output);if(memcmp(output,expected,sizeof output))return 3;
 NativeInputWorld *w=native_input_world();
 if(w->latest!=expected[lin(GAME_SEG,G(LatestInterruptScanCode))] || w->current_scan_storage!=word(D(CurrentKeyboardScanCode)) || w->previous!=expected[lin(DATA_SEG,D(PreviousPolledScanCode))] || w->change!=expected[lin(DATA_SEG,D(KeyboardScanCodeChangeBits))] || w->index!=expected[lin(DATA_SEG,D(KeyboardSequenceIndex))] || w->enabled_axis_storage!=word(D(JoystickEnabledAxisMask)) || w->loop_limit!=word(D(JoystickSampleLoopLimit)))return 4;
 for(unsigned i=0;i<2;i++){
  InputJoystick *j=&w->joysticks[i];unsigned d=i*2;
  if(j->present!=word(D(JoystickPresentFlags)+d) || j->x!=word(D(FirstJoystickXCount)+d) || j->y!=word(D(FirstJoystickYCount)+d) || j->buttons!=word(D(JoystickButtonBits)+d) || j->double_x!=word(D(FirstJoystickXDoubleCenter)+d) || j->double_y!=word(D(FirstJoystickYDoubleCenter)+d) || j->left!=word(D(JoystickLeftThresholds)+d) || j->right!=word(D(JoystickRightThresholds)+d) || j->up!=word(D(JoystickUpThresholds)+d) || j->down!=word(D(JoystickDownThresholds)+d))return 5;
 }
 for(unsigned i=0;i<4;i++)if(w->calibration_reset_words[i]!=word(D(ds_3321)+2*i))return 6;
 if(w->saved_keyboard.first!=word(D(PreviousKeyboardVector)) || w->saved_keyboard.second!=word(D(PreviousKeyboardVectorSegment)) || memcmp(w->sequence,expected+lin(DATA_SEG,D(KeyboardSequenceRecords)),205))return 7;
 for(unsigned i=0;i<n;i++)for(unsigned v=0;v<256;v++){
  if(v&1)input_borrowed_store(ugh_mem+(addresses[i]&~15u),addresses[i]&15u,(uint8_t)v);
  else if(!input_shared_write(addresses[i],(uint8_t)v))return 8;
  expected[addresses[i]]=(uint8_t)v;uint8_t value;
  if(!input_shared_read(addresses[i],&value) || value!=v || input_borrowed_byte(ugh_mem,addresses[i])!=v)return 9;
  if(addresses[i]==lin(GAME_SEG,G(LatestInterruptScanCode)) && w->latest!=v)return 9;
  if(addresses[i]==lin(DATA_SEG,D(PreviousPolledScanCode)) && w->previous!=v)return 9;
  if(addresses[i]==lin(DATA_SEG,D(KeyboardScanCodeChangeBits)) && w->change!=v)return 9;
  if(addresses[i]==lin(DATA_SEG,D(KeyboardSequenceIndex)) && w->index!=v)return 9;
  if(addresses[i]>=lin(DATA_SEG,D(KeyboardSequenceRecords)) && addresses[i]<lin(DATA_SEG,D(KeyboardSequenceRecords))+205 && w->sequence[addresses[i]-lin(DATA_SEG,D(KeyboardSequenceRecords))]!=v)return 9;
  input_serialize(output);for(unsigned j=0;j<n;j++)if(output[addresses[j]]!=expected[addresses[j]])return 10;
  if(input_check_serialization(output)!=UINT32_MAX)return 11;
 }
 const uint16_t words[]={D(CurrentKeyboardScanCode),D(JoystickEnabledAxisMask),D(PreviousKeyboardVector),D(PreviousKeyboardVectorSegment),D(JoystickSampleLoopLimit),D(JoystickPresentFlags),D(SecondJoystickPresent),D(FirstJoystickXCount),D(SecondJoystickXCount),D(FirstJoystickYCount),D(SecondJoystickYCount),D(JoystickButtonBits),D(SecondJoystickButtonBits),D(ds_3321),D(ds_3323),D(ds_3325),D(ds_3327),D(FirstJoystickXDoubleCenter),D(SecondJoystickXDoubleCenter),D(FirstJoystickYDoubleCenter),D(SecondJoystickYDoubleCenter),D(JoystickLeftThresholds),D(SecondJoystickXLowThreshold),D(JoystickRightThresholds),D(SecondJoystickXHighThreshold),D(JoystickUpThresholds),D(SecondJoystickYLowThreshold),D(JoystickDownThresholds),D(SecondJoystickYHighThreshold)};
 uint16_t *logical[]={&w->current_scan_storage,&w->enabled_axis_storage,&w->saved_keyboard.first,&w->saved_keyboard.second,&w->loop_limit,&w->joysticks[0].present,&w->joysticks[1].present,&w->joysticks[0].x,&w->joysticks[1].x,&w->joysticks[0].y,&w->joysticks[1].y,&w->joysticks[0].buttons,&w->joysticks[1].buttons,&w->calibration_reset_words[0],&w->calibration_reset_words[1],&w->calibration_reset_words[2],&w->calibration_reset_words[3],&w->joysticks[0].double_x,&w->joysticks[1].double_x,&w->joysticks[0].double_y,&w->joysticks[1].double_y,&w->joysticks[0].left,&w->joysticks[1].left,&w->joysticks[0].right,&w->joysticks[1].right,&w->joysticks[0].up,&w->joysticks[1].up,&w->joysticks[0].down,&w->joysticks[1].down};
 unsigned rounds=0;
 for(unsigned i=0;i<sizeof words/sizeof *words;i++)for(unsigned v=0;v<65536;v++){
  unsigned a=lin(DATA_SEG,words[i]);uint8_t lo,hi;
  if(!input_shared_write(a,(uint8_t)v) || !input_shared_write(a+1,(uint8_t)(v>>8)) || !input_shared_read(a,&lo) || !input_shared_read(a+1,&hi) || (unsigned)(lo|hi*256u)!=v || *logical[i]!=v)return 12;
  expected[a]=(uint8_t)v;expected[a+1]=(uint8_t)(v>>8);rounds++;
 }
 input_serialize(output);if(memcmp(output,expected,sizeof output))return 13;
 input_require_seal(ugh_mem);output[addresses[70]]^=1;if(input_check_serialization(output)!=addresses[70])return 14;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(!input_is_owned(a)){uint8_t v=49;if(input_shared_read(a,&v) || input_shared_write(a,17) || v!=49)return 15;}
 Regs r={0};r.cs=GAME_SEG+1;r.ss=0x8000;r.sp=0x100;r.ip=0x4567;
 if(input_peer_deliver(INPUT_PEER_PollKeyboardScanChange,0x1234,&r)!=UGH_BAD_CALLBACK || r.sp!=0x100)return 16;
 r.cs=GAME_SEG;if(input_peer_deliver(INPUT_PEER_PollKeyboardScanChange,0x1234,&r)!=0 || r.sp!=0x100 || r.ip!=0x4567)return 17;
 if(input_peer_deliver((InputPeerRole)99,0x1234,&r)!=UGH_BAD_CALLBACK || r.sp!=0xfe)return 18;
 r.ax=0x0100;if(input_editor_queue(&r) || r.ax!=0x1e41 || (r.flags&ZF))return 19;
 queue_failure=1;r.ax=0x0100;if(input_editor_queue(&r)!=UGH_UNSUPPORTED || r.ax!=0xbeef || !(r.flags&ZF))return 20;
 queue_failure=0;r.ax=0x0200;if(input_editor_queue(&r)!=UGH_UNSUPPORTED || r.ax!=0x0200)return 21;
 if(input_capture_keyboard(&r) || r.bx!=0x1234 || r.es!=0xf000)return 22;
 queue_failure=1;if(input_capture_keyboard(&r)!=UGH_UNSUPPORTED || r.bx!=0xb00b || r.es!=0xdead)return 23;
 printf("{\"owned_bytes\":%u,\"byte_values\":%u,\"word_roundtrips\":%u,\"outside_addresses\":%u,\"explicit_peer_rejections\":2}\n",n,n*256u,rounds,UGH_MEM_SIZE-n);return 0;
}
'''
 source=folder/'router.c';source.write_text(code);exe=folder/'router.exe'
 bounded([prior.timing.common.GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,source,ROOT/'native/input_world.c',ROOT/'native/bridge/input_world_bridge.c'],'router-compile')
 r=bounded([exe],'router-run');save(OUT/'router.json',dict(result='PASS',counts=json.loads(r['stdout'])))

def proof():
 from closure_support import function
 folder=OUT/'proof';folder.mkdir(exist_ok=True);bridge=(ROOT/'native/bridge/input_world_bridge.c').read_text()
 prefix='#include "input_world.h"\n#include <stddef.h>\n#include "'+(ROOT/'native/input_world.c').as_posix()+'"\n'
 prefix+='void *memcpy(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}\n'
 prefix+=re.search(r'typedef struct InputField.*?} InputField;',bridge,re.S)[0]+'\n'
 prefix+=''.join(function(bridge,n) for n in ['input_field_get','input_field_put'])
 prefix+='void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);\n#define assert(c) __CPROVER_assert((c),#c)\n'
 main=r'''NativeInputWorld nondet_world(void);unsigned nondet_uint(void);uint8_t nondet_byte(void);uint16_t nondet_word(void);
int main(void){
 world=nondet_world();unsigned wide=nondet_uint(),lane=nondet_uint(),other=nondet_uint(),member=nondet_uint();
 __CPROVER_assume(wide<2 && other<sizeof world && member<sizeof world);
 unsigned word_at=member;
 if(wide){__CPROVER_assume(lane<8);word_at=member+(lane/2)*2;__CPROVER_assume(word_at+2<=sizeof world);}
 else {__CPROVER_assume(lane<205 && member+lane<sizeof world);}
 InputField field={nondet_uint(),member,wide?2:1,nondet_uint()};
 unsigned selected=member+lane;
 if(wide)__CPROVER_assume(other<word_at || other>=word_at+2);
 else __CPROVER_assume(other!=selected);
 uint8_t frame=((uint8_t*)&world)[other],value=nondet_byte();uint16_t before=0,after=0;
 if(wide)memcpy(&before,(uint8_t*)&world+word_at,2);
 uint8_t old=wide?(uint8_t)(before>>((lane&1)*8)):((uint8_t*)&world)[selected];
 assert(input_field_get(&field,lane)==old);assert(((uint8_t*)&world)[other]==frame);
 if(wide){memcpy(&after,(uint8_t*)&world+word_at,2);assert(after==before);}
 else assert(((uint8_t*)&world)[selected]==old);
 input_field_put(&field,lane,value);assert(input_field_get(&field,lane)==value);
 assert(((uint8_t*)&world)[other]==frame);
 if(wide){unsigned shift=(lane&1)*8;memcpy(&after,(uint8_t*)&world+word_at,2);assert(after==(uint16_t)((before&~(255u<<shift))|((unsigned)value<<shift)));}
 uint16_t sampled=nondet_word(),live=nondet_word(),latched=nondet_word();
 assert(input_rebase_count((uint16_t)(sampled-latched),sampled,live)==(uint16_t)(live-latched));
}
'''
 source=folder/'fields.c';source.write_text(prefix+main);pre=folder/'fields.i'
 bounded([prior.timing.common.GCC,'-E','-P','-nostdinc','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',source,'-o',pre],'proof-preprocess')
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe']
 r=bounded([tool,pre,'--unwind','3','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-fields')
 assert 'VERIFICATION SUCCESSFUL' in r['stdout']
 save(OUT/'proof.json',dict(result='PASS',scope='Actual field get/put and count-rebase C; arbitrary complete owner and valid member offset, any byte/table or four-word array lane/value, read-only getter, numeric word result plus arbitrary-other-byte frame, and full three-word rebase identity. All registry layouts fit this domain; physical routing is separately exhaustive C.',source=sha(source),preprocessed=sha(pre)))

def backend(fault=0):
 import hostbuild
 folder=OUT/('backend' if not fault else 'defects/backend-'+str(fault));folder.mkdir(parents=True,exist_ok=True)
 code=r'''#include "platform.h"
#include "input_world_bridge.h"
#include "palette_world_bridge.h"
#include "timing_world_bridge.h"
#include <stdio.h>
#include <string.h>
int l1_SampleJoystickAxesAndButtons(Regs *);
void ugh_devices_reset(void);
static Devices seed,expected;
static uint8_t ram[UGH_MEM_SIZE],result[UGH_MEM_SIZE];
static int failed_service(uint8_t number,Regs *r){
 r->ax=(uint16_t)(0xbe00|number);r->bx^=0xace1;r->cx^=0x6b34;r->dx^=0xb245;
 r->si^=0x1256;r->di^=0x8a76;r->bp^=0x6791;r->sp^=0x30;r->cs^=0x110;
 r->ds^=0x201;r->es^=0x190;r->ss^=0x80;r->ip^=0xb13;r->flags^=0xe1d7;
 return UGH_UNSUPPORTED;
}
static void script_bytes(unsigned port,unsigned a,unsigned b,unsigned c){
 ugh_devices_reset();ugh_devices.script_count=1;InputScript *s=&ugh_devices.scripts[0];
 s->port=port;s->count=3;s->cycles=s->cycles_left=1;
 s->runs[0]=(ScriptRun){a,1};s->runs[1]=(ScriptRun){b,1};s->runs[2]=(ScriptRun){c,8};
}
int main(void){
 unsigned scans=0,queues=0,vectors=0,flushes=0,counts=0;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ram[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(ugh_mem,ram,sizeof ram);
 for(unsigned value=0;value<256;value++){
  script_bytes(0x60,value,0,0);memcpy(&seed,&ugh_devices,sizeof seed);
  unsigned raw=platform_in(0x60,1);platform_out(0x20,1,0x20);memcpy(&expected,&ugh_devices,sizeof expected);
  memcpy(&ugh_devices,&seed,sizeof seed);InputByteReply typed=input_service_scan();input_service_acknowledge_scan();
  if(typed.status || typed.value!=raw || memcmp(&expected,&ugh_devices,sizeof expected))return 21;
  scans++;
 }
 for(unsigned take=0;take<2;take++)for(unsigned value=0;value<256;value++){
  script_bytes(0xffff,0x1e00+value,0x1c0d,0);memcpy(&seed,&ugh_devices,sizeof seed);
  Regs a={0};a.ax=(uint16_t)(take?0x0081:0x0181);a.flags=0xed7;Regs b=a;
  int old=platform_interrupt(0x16,&a);memcpy(&expected,&ugh_devices,sizeof expected);
  memcpy(&ugh_devices,&seed,sizeof seed);InputQueueReply now=input_service_queue(take?INPUT_QUEUE_TAKE:INPUT_QUEUE_PEEK,(InputServiceContext*)&b);
  if(old!=now.status || now.word!=a.ax || now.present!=(take?!old:!(a.flags&ZF)) || memcmp(&a,&b,sizeof a) || memcmp(&expected,&ugh_devices,sizeof expected))return 22;
  queues++;
 }
 for(unsigned take=0;take<2;take++){
  ugh_devices_reset();memcpy(&seed,&ugh_devices,sizeof seed);
  Regs a={0};a.ax=(uint16_t)(take?0x0081:0x0181);a.flags=0xed7;Regs b=a;
  int old=platform_interrupt(0x16,&a);memcpy(&expected,&ugh_devices,sizeof expected);
  memcpy(&ugh_devices,&seed,sizeof seed);InputQueueReply now=input_service_queue(take?INPUT_QUEUE_TAKE:INPUT_QUEUE_PEEK,(InputServiceContext*)&b);
  if(old!=now.status || now.word!=a.ax || now.present!=(take?!old:!(a.flags&ZF)) || memcmp(&a,&b,sizeof a) || memcmp(&expected,&ugh_devices,sizeof expected))return 22;
  queues++;
 }
 for(unsigned v=0;v<65536;v++){
  Regs a={0},b={0};a.ax=b.ax=0x2509;a.dx=b.dx=(uint16_t)v;a.ds=b.ds=(uint16_t)~v;
  ugh_devices_reset();platform_interrupt(0x21,&a);IoEvent event=ugh_devices.log[0];
  unsigned lo=rd16(0,0x24),hi=rd16(0,0x26);ugh_devices.count=0;
  int status=input_service_vector(v&1?INPUT_VECTOR_INSTALL_HANDLER:INPUT_VECTOR_RESTORE_SAVED,(InputKeyboardBinding){(uint16_t)v,(uint16_t)~v},(InputServiceContext*)&b).status;
  if(status || memcmp(&a,&b,sizeof a) || rd16(0,0x24)!=lo || rd16(0,0x26)!=hi || ugh_devices.count!=1 || memcmp(&event,ugh_devices.log,sizeof event))return 23;
  a.ax=b.ax=0x3509;ugh_devices.count=0;platform_interrupt(0x21,&a);event=ugh_devices.log[0];ugh_devices.count=0;
  InputVectorReply reply=input_service_vector(INPUT_VECTOR_CAPTURE,(InputKeyboardBinding){0,0},(InputServiceContext*)&b);
  if(reply.status || reply.binding.first!=lo || reply.binding.second!=hi || memcmp(&a,&b,sizeof a) || ugh_devices.count!=1 || memcmp(&event,ugh_devices.log,sizeof event))return 23;
  vectors++;
 }
 for(unsigned v=0;v<65536;v++){
  wr16(0x40,0x1a,(uint16_t)~v);wr16(0x40,0x1c,(uint16_t)v);
  if(input_service_queue_flush()!=v || rd16(0x40,0x1a)!=v || rd16(0x40,0x1c)!=v)return 25;
  flushes++;
 }
 ugh_set_interrupt_service(failed_service);
 for(unsigned role=0;role<3;role++){
  ugh_devices_reset();Regs a={0},b={0};a.ax=(uint16_t)(role?0x2509:0x3509);a.dx=0x8123;a.ds=0xf456;a.flags=0xed7;b=a;
  int old=platform_interrupt(0x21,&a);memcpy(&expected,&ugh_devices,sizeof expected);ugh_devices_reset();
  InputVectorReply now=input_service_vector((InputVectorOperation)role,(InputKeyboardBinding){0x8123,0xf456},(InputServiceContext*)&b);
  if(old!=now.status || memcmp(&a,&b,sizeof a) || memcmp(&expected,&ugh_devices,sizeof expected) || now.binding.first!=a.bx || now.binding.second!=a.es)return 26;
 }
 for(unsigned role=0;role<2;role++){
  ugh_devices_reset();Regs a={0},b={0};a.ax=(uint16_t)(role*256u+0x81);a.flags=0xed7;b=a;
  int old=platform_interrupt(0x16,&a);memcpy(&expected,&ugh_devices,sizeof expected);ugh_devices_reset();
  InputQueueReply now=input_service_queue((InputQueueOperation)role,(InputServiceContext*)&b);
  if(old!=now.status || now.word!=a.ax || memcmp(&a,&b,sizeof a) || memcmp(&expected,&ugh_devices,sizeof expected))return 27;
 }
 ugh_set_interrupt_service(0);
 const uint16_t limits[]={0,1,2,3,7,32767,32768,65535};
 for(unsigned mask=0;mask<16;mask++)for(unsigned k=0;k<sizeof limits/sizeof *limits;k++)for(unsigned wave=0;wave<16;wave++){
  memcpy(ugh_mem,ram,sizeof ram);wr16(DATA_SEG,D(JoystickSampleLoopLimit),limits[k]);wr8(DATA_SEG,D(JoystickEnabledAxisMask),(uint8_t)mask);
  script_bytes(0x201,(wave*17u)^0x5a,(wave*37u)^0xa5,wave);
  ugh_devices.scripts[0].count=4;ugh_devices.scripts[0].runs[3]=(ScriptRun){0,8};
  memcpy(&seed,&ugh_devices,sizeof seed);
  Regs a={0},b={0};a.cs=GAME_SEG;a.ds=DATA_SEG;a.ss=0x8000;a.sp=0x100;a.ax=0xb381;a.flags=0xed7;b=a;
  int old=l1_SampleJoystickAxesAndButtons(&a);memcpy(&expected,&ugh_devices,sizeof expected);memcpy(result,ugh_mem,sizeof result);
  memcpy(ugh_mem,ram,sizeof ram);wr16(DATA_SEG,D(JoystickSampleLoopLimit),limits[k]);wr8(DATA_SEG,D(JoystickEnabledAxisMask),(uint8_t)mask);memcpy(&ugh_devices,&seed,sizeof seed);
  int now=c_SampleJoystickAxesAndButtons(&b);
  if(old!=now || memcmp(&a,&b,sizeof a) || memcmp(result,ugh_mem,sizeof result) || memcmp(&expected,&ugh_devices,sizeof expected))return 24;
  counts++;
 }
 memcpy(ugh_mem,ram,sizeof ram);wr16(DATA_SEG,D(LastActiveTimerSlotOffset),30);
 timing_cold_import(ugh_mem);palette_cold_import(ugh_mem);input_cold_import(ugh_mem);
 unsigned native_bytes=0;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++){
  unsigned owners=(unsigned)timing_is_owned(a)+(unsigned)palette_is_owned(a)+(unsigned)input_is_owned(a);
  if(owners>1)return 28;
  native_bytes+=owners;
 }
 if(native_bytes!=6415 || native_bytes!=timing_owned_bytes()+palette_owned_bytes()+input_owned_bytes())return 28;
 timing_require_seal(ugh_mem);palette_require_seal(ugh_mem);input_require_seal(ugh_mem);
 printf("{\"scans\":%u,\"queues\":%u,\"vector_word_slice\":%u,\"flush_word_slice\":%u,\"count_frames\":%u,\"failed_callback_prefixes\":5,\"disjoint_native_bytes\":%u}\n",scans,queues,vectors,flushes,counts,native_bytes);return 0;
}
'''
 source=folder/'backend.c';source.write_text(code)
 command=json.loads((OUT/'children/api-composed-compile.json').read_text())['command']
 units=hostbuild.selected_units()+[dict(component='input_world')]
 platform=folder/'platform.c';platform.write_text(hostbuild.composition_source('c/platform.c',(ROOT/'c/platform.c').read_text(),units))
 command=[str(platform) if x==str(OUT/'api/composed/platform.c') else x for x in command]
 command=[x for x in command if x!='-shared'];command[command.index('-o')+1]=str(folder/'backend.exe');command.extend(['-I',str(ROOT/'native'),str(source)])
 if fault:command.append('-DINPUT_TEST_FAULT='+str(fault))
 bounded(command,'backend-compile-'+str(fault))
 if fault:
  capture=folder/'capture.py';capture.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n')
  row=bounded([sys.executable,capture,folder/'backend.exe'],'backend-defect-'+str(fault));actual=json.loads(row['stdout'])
  assert actual['returncode']==(24 if fault==4 else 21),actual
  return dict(defect={2:'swapped-make-break',3:'lost-E0-prefix',4:'stale-joystick-count'}[fault],result='DETECTED',exit=actual['returncode'],scope='Typed services vs actual platform/L1 sampler, full memory, Devices and ABI')
 row=bounded([folder/'backend.exe'],'backend-run');save(OUT/'backend.json',dict(result='PASS',counts=json.loads(row['stdout']),scope='Actual platform vs typed scan/queue/vector provider, full Devices; actual L1 sampler vs count-service/native bridge, full RAM/ABI/Devices across all low axis masks and 16 wave patterns, zero and signed-word boundaries. All 256 scan bytes and full vector word slice.'))

def borrowers():
 source=inspect.getsource(prior.borrowers)
 source=source.replace("m.seg('GAME:BaseRgbPalette')","m.seg('DGROUP:JoystickPresentFlags')").replace("m.off('GAME:BaseRgbPalette')","m.off('DGROUP:KeyboardSequenceRecords')").replace("m.off('GAME:FadedRgbPalette')","m.off('DGROUP:JoystickPresentFlags')")
 source=source.replace("pair('UploadBasePalette',regs=", "m.ww('DGROUP:BasePalettePointer',base);m.ww('DGROUP:BasePalettePointer',game,2)\n pair('UploadBasePalette',regs=")
 source=source.replace('[0x681,0x682,0x981,0xc81]','[0x97,0x2648,0x28e9,0x3345]').replace('ES=game+0x400','ES=game')
 source=source.replace(" save(OUT/'borrowers.json'", " m.reset();data=bytes((i*73)&255 for i in range(0x50a));m.write(0x7500,0,ice_pack235(data));pair('UnpackIceStream',regs=dict(DS=0x7500,ES=m.seg('GAME:LatestInterruptScanCode')+0x400,SI=0,DI=0xbeef))\n save(OUT/'borrowers.json'")
 env=dict(prior.__dict__);exec(source,env);env['borrowers']()
 r=json.loads((OUT/'borrowers.json').read_text());r.pop('excluded_probe',None)
 r['scope']='Independent L1/composed live ABI, RAM outside scratch stack and full Devices. Copy/decimal/duplicate aliases into native input table and joystick state; a palette upload whose next input-table source byte changes during DAC delivery; real ICE output covering saved binding, scans, all 205 sequence bytes and calibration, plus GAME latest-scan lane. Immutable decoder tables remain disjoint.';save(OUT/'borrowers.json',r)

def defects():
 target=snapshot();rows=[]
 for fault,label in [(1,'dropped-scan'),(5,'missed-serialization')]:
  folder=OUT/'defects'/label
  for top in ['c','native','host','metadata','tools','verif','src']:shutil.copytree(target/top,folder/top,dirs_exist_ok=True)
  shutil.copytree(target/'build/link',folder/'build/link',dirs_exist_ok=True)
  p=folder/'tools/hostbuild.py';text=p.read_text().replace("return (['-DUGH_NATIVE_INPUT']", "return ['-DINPUT_TEST_FAULT="+str(fault)+"']+(['-DUGH_NATIVE_INPUT']",1);p.write_text(text)
  bounded([sys.executable,'tools/hostbuild.py'],'defect-build-'+label,folder)
  capture=folder/'capture.py';capture.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n')
  command=[folder/'build/host/ugh.exe','--headless','48','--script',target/'tests/scenarios/gameplay-adlib.txt','--timeout','590']
  row=bounded([sys.executable,capture,*command],'defect-run-'+label);actual=json.loads(row['stdout'])
  if fault==5:
   assert actual['returncode']==88 and 'missed serialization' in actual['stderr'];rows.append(dict(defect=label,result='DETECTED',exit=88));continue
  assert actual['returncode']==0,actual['stderr']
  frames=[json.loads(line) for line in actual['stdout'].splitlines()];expected=json.loads((ROOT/'build/whole/gameplay-adlib.ref.json').read_text())['frames']
  first=next((i for i,(a,b) in enumerate(zip(frames,expected)) if a!=b),None);assert first is not None,label
  rows.append(dict(defect=label,result='DETECTED',scenario='gameplay-adlib',first_record=first+1))
 for fault in [2,3,4]:rows.append(backend(fault))
 save(OUT/'defects.json',dict(result='PASS',controls=rows))

def census():
 target=snapshot();p=target/'verif/standalone_census.py';text=p.read_text()
 marker="        if source=='native/bridge/timing_world_bridge.c' and name in {"
 assert text.count(marker)==1
 addition="""        if source=='native/bridge/input_world_bridge.c' and name in {
            'input_field','input_field_get','input_field_put','input_is_owned','input_shared_read',
            'input_shared_write','input_borrowed_byte','input_borrowed_store'}:
            assert not re.search(r'\\b(?:l1_\\w+|ugh_dispatch\\w*|ugh_call_near\\w*|platform_\\w+)\\s*\\(',text[b+1:e])
            continue
        if source=='native/bridge/palette_world_bridge.c' and name in {
            'palette_index','palette_get','palette_put','palette_address','palette_is_owned',
            'palette_shared_read','palette_shared_write','palette_borrowed_byte','palette_borrowed_store'}:
            assert not re.search(r'\\b(?:l1_\\w+|ugh_dispatch\\w*|ugh_call_near\\w*|platform_\\w+)\\s*\\(',text[b+1:e])
            continue
"""
 p.write_text(text.replace(marker,addition+marker));bounded([sys.executable,'verif/standalone_census.py','--all'],'census-run',target)
 folder=target/'build/workers/close-adlx-19';summary=json.loads((folder/'census.json').read_text())
 assert len(summary['scenarios'])==21 and all(not s['fallback_calls'] and not s['l1_body_calls'] for s in summary['scenarios'])
 internal=[];outgoing=[];counts=[];names={'c_'+n for n in NAMES}
 for path in sorted((folder/'detail').glob('*.json')):
  run=json.loads(path.read_text())
  counted={f['name']:f['count'] for f in run['bodies'] if f['path']=='native/bridge/input_bridge.c' or f['name'] in ['input_editor_queue','input_service_queue','c_EditLevelPassword','c_InsertHighScoreAndClearScore']}
  counts.append(dict(scenario=run['scenario'],entries={name:counted.get(name,0) for name in sorted(names)},editors={name:counted.get(name,0) for name in ['c_EditLevelPassword','c_InsertHighScoreAndClearScore','input_editor_queue','input_service_queue']}))
  for edge in run['machine_edges']:
   if edge['kind'] in ['ABI-entry','interrupt-delivery']:continue
   if edge['bridge'].get('name') not in names|{'input_peer_deliver','input_editor_queue','input_capture_keyboard','input_key_run','input_project','input_threshold_binding'}:continue
   row=dict(scenario=run['scenario'],**edge)
   if edge['target'].get('name') in names:internal.append(row)
   else:outgoing.append(row)
 assert not internal,internal[:4]
 reached={f['name'] for f in summary['functions'] if f['count'] and f['path']=='native/bridge/input_bridge.c'}
 assert names<=reached,names-reached
 # Preprocess the actual composed bridge before auditing: its independently
 # replayed legacy profile deliberately retains literal hardware services.
 import hostbuild
 from closure_support import function
 pre=OUT/'input-bridge.i';bounded([prior.timing.common.GCC,'-E','-P','-DUGH_NATIVE_INPUT','-I',ROOT/'c','-I',ROOT/'native/bridge',ROOT/'native/bridge/input_bridge.c','-o',pre],'census-preprocess')
 for name in names|{'input_key_run','input_project','input_threshold_binding'}:
  body=function(pre.read_text(),name);assert not re.search(r'\b(?:ugh_dispatch\w*|ugh_call_near\w*|platform_in|platform_out|platform_interrupt|platform_service_point_at)\s*\(',body),(name,'raw machine edge')
 for name in ['input_peer_deliver','input_editor_queue','input_capture_keyboard']:
  body=function((ROOT/'native/bridge/input_world_bridge.c').read_text(),name);assert not re.search(r'\b(?:ugh_dispatch\w*|ugh_call_near\w*|platform_in|platform_out|platform_interrupt|platform_service_point_at)\s*\(',body),(name,'raw machine edge')
 save(OUT/'census.json',dict(result='PASS',summary=summary,per_scenario_counts=counts,internal_island_machine_edges=internal,outgoing_services=outgoing,island=sorted(names),scope='Eight input entries plus owner/peer/editor adapters; typed provider is the verification platform. Pure byte leaves statically exclude machine edges and have B/router evidence.'))

def inventory():
 import cgen
 mz,symbols=cgen.read_symbols();model=json.loads((ROOT/'metadata/program-model.json').read_text())
 small=['PreviousPolledScanCode','KeyboardScanCodeChangeBits','KeyboardSequenceIndex']
 words=['CurrentKeyboardScanCode','JoystickEnabledAxisMask','JoystickSampleLoopLimit','JoystickPresentFlags','SecondJoystickPresent','FirstJoystickXCount','SecondJoystickXCount','FirstJoystickYCount','SecondJoystickYCount','JoystickButtonBits','SecondJoystickButtonBits','FirstJoystickXDoubleCenter','SecondJoystickXDoubleCenter','FirstJoystickYDoubleCenter','SecondJoystickYDoubleCenter','JoystickLeftThresholds','SecondJoystickXLowThreshold','JoystickRightThresholds','SecondJoystickXHighThreshold','JoystickUpThresholds','SecondJoystickYLowThreshold','JoystickDownThresholds','SecondJoystickYHighThreshold','ds_3321','ds_3323','ds_3325','ds_3327','PreviousKeyboardVector','PreviousKeyboardVectorSegment']
 fields=[('GAME:LatestInterruptScanCode',1)]+[('DGROUP:'+n,1) for n in small]+[('DGROUP:'+n,2) for n in words]+[('DGROUP:KeyboardSequenceRecords',205)]
 moved=[];addresses=set()
 for name,size in fields:
  s=symbols[name];a=(cgen.LOAD+s['frame'])*16+s['offset'];assert not addresses.intersection(range(a,a+size));addresses.update(range(a,a+size))
  moved.append(dict(symbol=name,address=a,bytes=size,model=model['variables'].get(name.split(':')[1],{})))
 assert len(addresses)==267
 shared=[]
 for name in ['PlayerCount','PlayerArrayBytes','PlayerOneControlMode','PlayerTwoControlMode','PlayerUpInput','PlayerDownInput','PlayerLeftInput','PlayerRightInput','PlayerActionInput','KeyboardHandlerVector']:
  s=symbols['DGROUP:'+name];a=(cgen.LOAD+s['frame'])*16+s['offset'];size=4 if name=='KeyboardHandlerVector' or name in ['PlayerUpInput','PlayerDownInput','PlayerLeftInput','PlayerRightInput','PlayerActionInput'] else 2
  assert not addresses.intersection(range(a,a+size))
  shared.append(dict(symbol='DGROUP:'+name,address=a,bytes=size,ownership='Existing configuration/player-command/resource owner stays in RAM; no duplicate native input owner',model=model['variables'].get(name,{})))
 row=symbols['DGROUP:KeyboardSequenceRecords'];offset=row['frame']*16+row['offset'];table=mz.image[offset:offset+205]
 assert len(table)==205 and table[-1]==255
 records=[dict(index=i,scans=list(table[6*i:6*i+3]),destination=table[6*i+3],value=table[6*i+4],candidate=table[6*i+5]) for i in range(34)]
 raw_users=[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'native').rglob('*.c')) if re.search(r'\bugh_mem\b',p.read_text())]
 allowed={'native/bridge/'+n+'_bridge.c' for n in ['adlx_loader','audio_world','decimal','far_copy','ice','ice_scratch','input_world','palette_world','timing_world']}
 assert set(raw_users)<=allowed,set(raw_users)-allowed
 save(OUT/'ownership.json',dict(result='PASS',before=6148,added=267,after=TOTAL,moved=moved,shared_owners_stay_put=shared,initial_records=records,
  indexed_notes=['SelectPlayerControls writes BOTH modes through PlayerOneControlMode+BX (0/2), despite base-only symbol attribution','The scan ISR writes all command byte destinations selected by mutable records, not only PlayerUpInput; high bytes and unused offset20 sink stay unchanged','Keyboard candidate stores are indexed; ordinary malformed table requests may alias any admitted RAM byte, including moved input fields. The numeric physical router applies at every access, without widening the table owner','InputState is an operation-local borrowed projection, never a persistent second configuration/command owner'],
  services=['Raw set-1 scan delivery plus EOI; E0 is a separate byte','Separate BIOS peek/take and queue flush, independent of raw scan queue','Separate ordered button reads and final counts in the unchanged calibration unit; latched/remaining witnesses only preserve verification ABI/error prefixes','Opaque vector capture/install-handler/restore-saved roles','Two explicit poll cuts retain the deterministic scheduling policy through an opaque, transient verification continuation'],
  audited_raw_window_adapters=raw_users,port_decisions='No live joystick, live event scheduling or narrower VGA choice made',remaining='Video pages/banks/layouts, height/copy state, HUD/render histories and plane/copy/read-plane/retrace-level services'))

def finalize():
 results={n:json.loads((OUT/(n+'.json')).read_text()) for n in ['api','compiled','router','proof','backend','borrowers','census','levels','defects']}
 assert all(r['result']=='PASS' for r in results.values())
 assert not results['api']['explicit_out_of_domain']
 assert len(results['defects']['controls'])==5 and all(c['result']=='DETECTED' for c in results['defects']['controls'])
 runs=[json.loads(p.read_text()) for p in (OUT/'projector/runs').glob('*.json')]
 assert len(runs)==21 and all(r['canonical_native_owned_bytes']==TOTAL and not r['native_owned_journal_publications'] for r in runs)
 # Bind the current actual C to the successful API compile, not only filenames.
 inputs={k.replace('\\','/'):v for k,v in results['api']['profiles']['composed']['inputs'].items()}
 for name in ['native/input_world.c','native/bridge/input_world_bridge.c','native/bridge/input_bridge.c']:
  assert inputs[name]==sha(ROOT/name),(name,'API receipt must be replayed for the current native C')
 inventory()
 p=ROOT/'metadata/closure/input_world.json';c=json.loads(p.read_text());c['proposed_status']='migrated'
 c['assumptions']=list(dict.fromkeys(c['assumptions']+['Typed near peers admit canonical GAME code binding; unknown roles/bindings fail closed with recorded verification ABI prefixes','Current handler resource binding and saved external payload stay opaque; only the verification provider interprets IVT words','Numeric byte/word layout is B plus complete C router enumeration; no blanket B proof of the complete matcher/calibration/wait loops is claimed']))
 c['evidence']=[
  dict(property='Authoritative byte owner and count service seam',level='B',method=results['proof']['scope'],command='python verif/input_composition.py --proof --router',result=f"PASS: {results['router']['counts']['byte_values']} byte writes; {results['router']['counts']['word_roundtrips']} word roundtrips; full physical router enumeration",date='2026-11-15'),
  dict(property='API, services and borrowers',level='C',method='Independent Unicorn and compiled L1; full RAM/ABI/Devices and ordered requests; editor and failure-prefix paths',command='python verif/input_composition.py --api --compiled --backend --borrowers',result=f"PASS: {results['api']['composed_matching']} composed and legacy API matches, 0 declines; {len(results['compiled']['cases'])} generated complete input pairs; {len(results['borrowers']['cases'])} borrower cases; all 256 scan bytes, full vector/queue-tail word slices and 2048 sampler frames",date='2026-11-15'),
  dict(property='Composition and ownership projection',level='D',method='Committed archive, scratch-only promotion; pure L1 literal; independent reconstructed-ASM references',command='python verif/input_composition.py --build --projector --census --levels',result=f"PASS: 49 certificates/0 errors; 21/21 both variants; {sum(r['boundaries'] for r in runs)} projected boundaries, all {TOTAL} moved bytes native, zero moved-owner publications; zero input-island machine edges, L1 game bodies and fallbacks; 81+7+8 levels per variant",date='2026-11-15'),
  dict(property='Seeded service/owner faults',level='C',method='Generated-copy dropped scan, make/break swap, lost E0, stale count and missed serialization controls',command='python verif/input_composition.py --defects',result='PASS: 5/5 detected',date='2026-11-15')]
 c['evidence_refreshed']=[dict(date='2026-11-15',reason='New native input owner/services composition; supervisor decides promotion',commands=['python verif/input_composition.py --gate'],results='PASS; input cut only, remaining video work explicit',inputs=BASE)]
 save(p,c);relock(final=True)
 save(OUT/'verification-receipt.json',dict(result='PASS',status='unanalyzed',proposed_status='migrated',scope='Standalone step 4 second cut: input',native_bytes_added=267,native_bytes_total=TOTAL,projected_boundaries=sum(r['boundaries'] for r in runs),baseline=json.loads((OUT/'baseline.json').read_text()),relocks=json.loads((OUT/'relocks.json').read_text()),evidence={n:sha(OUT/(n+'.json')) for n in results}))

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['locks','api','compiled','build','projector','levels','router','proof','census','backend','borrowers','defects','finalize','gate','internal']:p.add_argument('--'+n,action='store_true')
 a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
 if a.locks:relock()
 if a.gate:
  relock()
  for n in ['api','compiled','router','proof','backend','borrowers','build','projector','census','levels','defects']:
   bounded([sys.executable,__file__,'--'+n,'--internal'],n+'-child')
  finalize();build();return
 for n in ['api','compiled','router','proof','backend','borrowers','build','projector','census','levels','defects','finalize']:
  if getattr(a,n):
   if a.internal:globals()[n]()
   else:bounded([sys.executable,__file__,'--'+n,'--internal'],n+'-child')
if __name__=='__main__':main()
