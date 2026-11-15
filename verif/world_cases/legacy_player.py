"""Cut5C: both native players and live command/history borrowers.
Generated copies only for instrumentation; serial 600s/8-GiB children.
"""
import argparse,ctypes as C,hashlib,inspect,io,json,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/workers/close-adlx-26'
sys.path.insert(0,str(ROOT/'tools'))
import random_composition as prior
run=prior.run;previous=run.previous
modules=[prior]+prior.modules
for module in modules:module.OUT=OUT
bounded=run.bounded;save=run.save;sha=run.sha
NEW=['native/player_world.h','native/player_world.c','native/bridge/player_world_bridge.h','native/bridge/player_world_bridge.c','native/bridge/player_borrow.h']
BORROWERS=[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'native/bridge').glob('*')) if p.suffix in ['.c','.h'] and '#include "player_borrow.h"' in p.read_text()]
BASE=NEW+BORROWERS+['verif/player_composition.py','verif/player_world_router.c','verif/player_world_cases.py','verif/player_world_byte_proof.c','tools/hostbuild.py','host/main.c','verif/projector/observer.c','verif/projector/timing_serializer.h','verif/projector/publications.py','verif/projector_evidence.py']
READ=sorted(set(prior.READ+['verif/random_composition.py','metadata/closure/random_world.json','verif/run_composition.py','verif/player_physics_l0_cases.py','verif/player_physics_harness.c','verif/player_physics_pair.py','native/bridge/render_primitives_support.h']))
CONTEXT=['player_physics','input','session','render_primitives','hud','contacts','stones','passenger_delivery','passenger_itinerary','passenger_water','hazards','falling_items','actor_types','actor_render','actor_pass','level_view','demo_core','demo_presentation','water_weather']
for unit in CONTEXT:
 p=ROOT/('metadata/closure/'+unit+'.json');READ+=['metadata/closure/'+unit+'.json']+json.loads(p.read_text())['native']['files']
READ=sorted(set(READ))
WORLDS=prior.WORLDS+['player_world'];TOTAL=8133
plan=(ROOT/'docs/standalone-cuts.md').read_text(encoding='utf-8');FIELDS=re.findall('`(.*?)`',plan.split('### 5C:')[1].split('**Owner:**')[0])
model=json.loads((ROOT/'metadata/program-model.json').read_text())
NAMES=sorted({routine.split(':')[1] for name in FIELDS for kind in ['readers','writers'] for routine in model['variables'][name][kind]}|{'HandleKeyboardScanInterrupt','InstallKeyboardSequenceInterrupt','InitializeLevelDisplay','LoadCurrentLevelState','DrawTileMap'})

def files():return sorted(set(BASE+subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()+['metadata/closure/player_world.json']))
def snapshot():
 source=prior.RUN_SNAPSHOT_SOURCE.replace('metadata/closure/run_world.json','metadata/closure/player_world.json')
 env=dict(run.__dict__,OUT=OUT,files=files);exec(source,env);return env['snapshot']()
for module in modules:module.snapshot=snapshot
build=previous.palette.build;levels=previous.palette.levels

def relock(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'relock',locals())

def inventory():
 symbols=(ROOT/'c/ugh_sym.h').read_text();addresses={n:int(re.search(r'#define UGH_O_DGDATA_'+n+r' (0x[0-9A-F]+)',symbols)[1],16) for n in FIELDS}
 save(OUT/'inventory.json',dict(result='PASS',bytes=92,total=TOTAL,regions=[dict(offset='278C',length=20),dict(offset='27D0',length=48),dict(offset='2804',length=24)],named_aliases=addresses,readers_writers={n:model['variables'][n] for n in FIELDS},borrowers=BORROWERS,excluded_hud='2800..2803 belongs to presentation_world',resource_shared_view='Cycle starts0CFA/0CFC and ends0CFC/0CFE share word0CFC. No model writers; both views remain foreign resource bytes, not player ownership. Impact limits remain resource views.',semantics='Both records exist independently; pixel/draw caches and histories are not rebuilt; five16-bit command words per player preserve low-byte IRQ writes and stale high bytes. Existing loader initializes both players and movement loops retain index<=PlayerCount.'))

def api(group=None,*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'api',locals())

def router():
 folder=OUT/'router';folder.mkdir(exist_ok=True);exe=folder/'router.exe'
 bounded([previous.timing.common.GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/player_world_router.c',ROOT/'native/player_world.c',ROOT/'native/bridge/player_world_bridge.c'],'router-compile')
 row=bounded([exe],'router-run');save(OUT/'router.json',dict(result='PASS',counts=json.loads(row['stdout']),scope='Independent literal address/member oracle; all92 bytes x256 and46 full16-bit slices; both-record independence, all roles/straddles/paragraph aliases, HUD exclusions, shared cycle alias, cold import, seal/serialization/frame.'))

def proof():
 from closure_support import function
 folder=OUT/'proof';folder.mkdir(exist_ok=True);text=(ROOT/'native/bridge/player_world_bridge.c').read_text()
 prefix='#include "player_world.h"\n#include <stddef.h>\n#include "'+(ROOT/'native/player_world.c').as_posix()+'"\n'
 prefix+='void *memcpy(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}\n'
 prefix+=re.search(r'typedef struct PlayerField.*?} PlayerField;',text,re.S)[0]+'\n'+''.join(function(text,n) for n in ['player_field_get','player_field_put'])
 prefix+='void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);\n#define assert(c) __CPROVER_assert((c),#c)\n'
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe'];rows=[]
 for name in ['read','store']:
  p=folder/(name+'.c');p.write_text(('#define PLAYER_PROOF_STORE\n' if name=='store' else '')+prefix+(ROOT/'verif/player_world_byte_proof.c').read_text(),encoding='utf-8');pre=p.with_suffix('.i')
  bounded([previous.timing.common.GCC,'-E','-P','-nostdinc','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',p,'-o',pre],'proof-'+name+'-pre')
  r=bounded([tool,pre,'--unwind','5','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-'+name);assert 'VERIFICATION SUCCESSFUL' in r['stdout'];rows.append(dict(profile=name,preprocessed=sha(pre)))
 save(OUT/'proof.json',dict(result='PASS',profiles=rows,scope='Actual-C strided16-bit player field byte get/put; arbitrary complete native world, either player, lane/value, valid member in first record and arbitrary-other-byte output/frame/dependence. Layout/registration via exhaustive router, not a resource/async theorem.'))

def reuse():
 # Accepted algorithms are unchanged. Header declaration order can change, so
 # compare actual default function bodies plus mechanically restored source.
 from standalone_census import bodies
 folder=OUT/'reuse';folder.mkdir(exist_ok=True);rows=[]
 for rel in BORROWERS:
  before=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT,text=True);after=(ROOT/rel).read_text()
  restored=re.sub(r'\A#include "platform.h"\n#ifndef PLAYER_BORROWER\n#define PLAYER_BORROWER PLAYER_BORROW_\w+\n#endif\n#include "player_borrow.h"\n','',after,count=1)
  original='rd' if Path(rel).name in ['contacts_bridge.c','render_primitives_support.h'] else 'run_read'
  restored=re.sub(r'\bplayer_read(8|16|32)\b',original+r'\1',restored)
  original='wr' if Path(rel).name in ['contacts_bridge.c','render_primitives_support.h'] else 'run_write'
  restored=re.sub(r'\bplayer_write(8|16|32)\b',original+r'\1',restored);assert restored==before,rel
  if not rel.endswith('.c'):continue
  definitions=[]
  for i,text in enumerate([before,after]):
   text=re.sub(r'#include "([^\"]+)"',lambda m:'#include "'+str((ROOT/rel).parent.joinpath(m[1]).resolve()).replace('\\','/')+'"' if (ROOT/rel).parent.joinpath(m[1]).is_file() else m[0],text)
   p=folder/(str(i)+'-'+Path(rel).name);p.write_text(text);pre=p.with_suffix('.i');bounded([previous.timing.common.GCC,'-E','-P','-I',ROOT/'c',p,'-o',pre],'reuse-'+str(i)+'-'+p.stem);text=pre.read_text();definitions.append({n:re.findall(r'"(?:\\.|[^"\\])*"|\w+|[^\s]',text[a:e+1]) for a,b,e,n in bodies(text)})
  assert definitions[0]==definitions[1],rel;rows.append(rel)
 pure=[]
 for p in sorted((ROOT/'native').glob('*')):
  if p.suffix not in ['.c','.h'] or p.name.startswith('player_world'):continue
  rel=p.relative_to(ROOT).as_posix();assert subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT).replace(b'\r\n',b'\n')==p.read_bytes().replace(b'\r\n',b'\n'),rel;pure.append(rel)
 save(OUT/'reuse.json',dict(result='PASS',bridges=rows,pure_sources_unchanged=pure,scope='All accepted pure C/headers unchanged; borrower edits are mechanical accessor renames plus prefix; default bridge function bodies (including shared headers) identical. Original algorithm proofs/resource domains reused unchanged. New state seams have independent evidence.'))

def projector(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'projector',locals())

def census(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'census',locals())

def borrowers():
 import player_world_cases
 player_world_cases.run(ROOT,OUT,bounded,save)
def defects():
 import player_world_cases
 player_world_cases.defects(ROOT,OUT,bounded,save,snapshot,previous)

def finalize(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'finalize',locals())

def main(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'main',locals())
# Scheduled by world_gate; no private CLI.
