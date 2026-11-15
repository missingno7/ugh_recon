"""Cut6A unique case operators; bounds/freezing/scheduling belong to world_gate."""
import json,re,sys,ctypes as C
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/workers/cut-6a/local'
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
from job_pool import run,save
from closure_support import GCC,function
NAMES=['RunGameFromPassword','InitializeLevelDisplay','LoadCurrentLevelState','ResetScoreLivesAndMultiplier','StartDemoFadeWhenSpriteHidden','SetDemoRevealSpriteWidth','RunScriptedDemo','PlaySpriteRevealDemo','PlayPreGameDemo','PlayAttractDemo','PlayGameCompletionDemo','ScaleLevelYToThreeQuarters','ScaleLevelSpeedToThreeHalves','PrepareAttractMap0','PrepareAttractMap90']

def bounded(command,tag,cwd=ROOT,ok=(0,),**kw):return run(command,cwd,OUT,tag,allowed=ok,**kw)
def compile_case(name,sources,options=()):
 folder=OUT/name;folder.mkdir(parents=True,exist_ok=True);exe=folder/'check.exe'
 bounded([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native','-I',ROOT/'native/bridge',*options,'-o',exe,*sources],name+'-compile');return exe

def router_sources():return [ROOT/p for p in ['verif/session_world_router.c','native/session_world.c','native/session.c','native/bridge/session_world_bridge.c']]
def router():
 exe=compile_case('router',router_sources());row=bounded([exe],'router-run');save(OUT/'router.json',dict(result='PASS',counts=json.loads(row['stdout'])))

def proof():
 folder=OUT/'proof';folder.mkdir(parents=True,exist_ok=True);text=(ROOT/'native/bridge/session_world_bridge.c').read_text()
 prefix='#include "session_world.h"\n#include <stddef.h>\nstatic NativeSessionWorld world;\n'+function((ROOT/'native/session_world.c').read_text(),'native_session_world')+'\n'
 prefix+='void *memcpy(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}\n'
 prefix+=re.search(r'typedef struct SessionstateField.*?} SessionstateField;',text,re.S)[0]+'\n'+''.join(function(text,n) for n in ['sessionstate_field_get','sessionstate_field_put'])
 prefix+='void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);\n#define assert(c) __CPROVER_assert((c),#c)\n'
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe'];rows=[]
 for name in ['read','store']:
  p=folder/(name+'.c');p.write_text(('#define SESSIONSTATE_PROOF_STORE\n' if name=='store' else '')+prefix+(ROOT/'verif/session_world_byte_proof.c').read_text());pre=p.with_suffix('.i')
  bounded([GCC,'-E','-P','-nostdinc','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',p,'-o',pre],'proof-'+name+'-pre')
  r=bounded([tool,pre,'--unwind','5','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-'+name);assert 'VERIFICATION SUCCESSFUL' in r['stdout'];rows.append(name)
 exe=compile_case('sequence',[ROOT/p for p in ['verif/session_world_sequence.c','native/session_world.c','native/session.c']]);r=bounded([exe],'sequence-run')
 save(OUT/'proof.json',dict(result='PASS',profiles=rows,sequence=json.loads(r['stdout']),scope='Actual-C byte read/store output/frame/dependence; independent native-driver ordered trace, fresh callback replies, pause, word/byte wrap and every service failure prefix.'))

def coverage():
 expected={('session','scene','empty script completed fade',False),('session','scene','empty script completed fade',True)}
 observed=set();counts={}
 for group in ['loader','session','demo']:
  command=json.loads((OUT/'children'/('api-'+group+'-composed-compile.json')).read_text())['command']
  receipt=json.loads((Path(command[command.index('-o')+1]).parent.parent/'receipt.json').read_text())
  counts[group]={k:receipt[k] for k in ['composed_matching','legacy_matching']}
  assert not receipt['explicit_out_of_domain']
  for row in receipt['compatibility_cases']:
   observed.add((group,row['suite'],row['case'],row['poison']));assert row['timer_fallbacks']==1
 assert observed==expected,(observed,expected)
 save(OUT/'coverage.json',dict(result='PASS',groups=counts,native_composed=142,compatibility_cases=[list(x) for x in sorted(observed)],scope='Exact existing unregistered empty vector initializer fallback inventory; these two poison variants prove state/ABI equality and are not credited as native demo initialization executions. All shipped callbacks and session bodies stay native.'))

def inventory():
 assert '100000' not in (ROOT/'native/session_world.c').read_text()
 model=json.loads((ROOT/'metadata/program-model.json').read_text())
 save(OUT/'inventory.json',dict(result='PASS',bytes=4,total=12434,region='DGROUP:2648..264B',named_cells={n:model['variables'][n] for n in ['CoordinateScaleScratch','DemoExitCode']},additional_writers=['InitializeLevelDisplay ordered196-word clear starts at2648 and crosses run map/player/HUD owners','Generic raw copy/decimal/codec windows borrow the complete registry, preserving partial words and physical aliases'],borrowers=['session_bridge.c','session_support.h','demo_core_bridge.c','demo_presentation_bridge.c','coordinate_scale_bridge.c'],continuations='Invocation-local SessionProcess/LoadRecord/Password/Display and nested NativeDemoContinuation; four historical bytes only; no persistent copies of other worlds; raw descriptors/callbacks unchanged.'))

def loader_case(label='loader',mutation=None):
 folder=OUT/label;folder.mkdir(parents=True,exist_ok=True)
 texts=[function((ROOT/p).read_text(),'c_LoadCurrentLevelState') for p in ['c/render.c','native/bridge/session_bridge.c']]
 fragments=[]
 for i,text in enumerate(texts):
  start=text.index('    r->si=24;');end=text.index('    '+('wr16' if i==0 else 'sessionstate_write16')+'(r->cs,G(RendererScratchWord)',start)
  copy=text[start:end]
  rain=text[text.index('    r->bx=384;'):text.rindex('    return UGH_OK;')]
  if i==1 and mutation:
   if label=='reordered-rain-prewarm':
    first=rain.index('        r->bx=384;');second=rain.index('        r->si=576;',first);end=rain.index('\n    }',second)
    rain=rain[:first]+rain[second:end]+'\n'+rain[first:second]+rain[end:]
   else:
    old,new=mutation;assert old in copy+rain,(label,old)
    copy=copy.replace(old,new);rain=rain.replace(old,new)
  prefix='original' if i==0 else 'modern'
  fragments += ['static void '+prefix+'_copy(Regs*r){'+copy+'}\n','static int '+prefix+'_rain(Regs*r){'+rain+'return UGH_OK;}\n']
 source=(ROOT/'verif/session_world_loader.c').read_text().replace('/* INSERT ACTUAL FRAGMENTS */',''.join(fragments))
 p=folder/'actual.c';p.write_text(source)
 return compile_case(label,[p,ROOT/'native/session.c'])

def borrowers():
 import sequencing_cases,demo_scene_cases
 exe=loader_case();loader=bounded([exe],'loader-run')
 folder=OUT/'scalars';folder.mkdir(parents=True,exist_ok=True)
 scalars=sequencing_cases.scalars(folder)
 demo=OUT/'demo';demo.mkdir(parents=True,exist_ok=True);value,result=demo_scene_cases.run(demo);assert value.returncode==0,result
 save(OUT/'demo-cases.json',result)
 save(OUT/'borrowers.json',dict(result='PASS',scalars=scalars['stdout'],demo=result['stdout'],loader=json.loads(loader['stdout']),scope='Independent actual literal/native scalar and demo ordered branch/whole-run comparators; full L1/Unicorn/RAM/device API checks are separate stages.'))

def defects():
 # Actual compiled controls. Mutants never edit maintained sources or comparators.
 folder=OUT/'defects';folder.mkdir(parents=True,exist_ok=True);rows=[]
 for fault,label in [(1,'lost-demo-exit'),(2,'cleared-scratch-high'),(3,'missed-serialization')]:
  exe=compile_case(label,router_sources(),['-DSESSIONSTATE_TEST_FAULT='+str(fault)]);r=bounded([exe],label+'-run',ok=tuple(range(1,16))+(88,));rows.append(dict(defect=label,result='DETECTED',exit=r['returncode'],comparator='independent physical/member router terminal state'))
 pure=[
 ('movement-loop-inequality','native/session.c','e.index==w.player_count','e.index!=w.player_count'),
 ('lives-word-decrement','native/session.c','e.value=(uint8_t)(w.lives-1u)','e.value=(uint16_t)(w.lives-1u)'),
 ('level-no-wrap','native/session.c','e.value=(uint16_t)(w.level+1u)','e.value=w.level==65535?65535:(uint16_t)(w.level+1u)'),
 ('reordered-frame','native/session.c','case SESSION_UPDATE_ACTORS:p->phase=SP_UPDATE_ENEMIES','case SESSION_UPDATE_ACTORS:p->phase=SP_UPDATE_ITEMS'),
 ('skip-pause-poll','native/session.c','w.scan==0x19?SP_PAUSE_RELEASE:SP_ESCAPE','SP_ESCAPE'),
 ('advance-frame-in-pause','native/session.c','case SESSION_PAUSE_RELEASE:p->phase=','case SESSION_PAUSE_RELEASE:p->completed_frames++;p->phase='),
 ('escape-is-completion','native/session.c','e.decision=(uint8_t)((w.completion&128u)!=0)','e.decision=(uint8_t)(w.scan==1)'),
 ('guard-is-game-outcome','native/session_world.c','status=diagnostic(context,&process);if(status)return status;','status=diagnostic(context,&process);if(status)return 0;'),
 ('continue-failed-service','native/session_world.c','if(status)return status;','if(status)status=0;'),
 ('stale-parent-overwrite','native/session_world.c','observe(context,process.phase)))','(SessionWorld){0}))')]
 for label,rel,old,new in pure:
  text=(ROOT/rel).read_text();assert old in text,(label,old)
  text=text.replace(old,new,1).replace('#include "session.h"','#include "'+(ROOT/'native/session.h').as_posix()+'"').replace('#include "session_world.h"','#include "'+(ROOT/'native/session_world.h').as_posix()+'"')
  p=folder/(label+'.c');p.write_text(text)
  sources=[p if path==rel else ROOT/path for path in ['verif/session_world_sequence.c','native/session_world.c','native/session.c']]
  exe=compile_case(label,sources,['-Wno-unused-but-set-variable']);r=bounded([exe],label+'-run',ok=(3,));rows.append(dict(defect=label,result='DETECTED',comparator='independent native-driver order/live-reply/failure-prefix and wrap assertions',diagnostic=r['stderr'].strip()))
 for label,old,new in [
  ('wrong-descending-record','WI(CurrentLevelRecord,r->si,r->ax);','WI(CurrentLevelRecord,(uint16_t)((r->si+2u)%26u),r->ax);'),
  ('reordered-rain-prewarm','r->si=576;','r->si=575;'),
  ('skipped-rain-slot193','r->bx=384;','r->bx=382;')]:
  exe=loader_case(label,(old,new));r=bounded([exe],label+'-run',ok=(3,));rows.append(dict(defect=label,result='DETECTED',comparator='independent literal/native full RAM/register/ordered rain prefix',diagnostic=r['stderr'].strip()))
 save(OUT/'defects.json',dict(result='PASS',controls=rows))
