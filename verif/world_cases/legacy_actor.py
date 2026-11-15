"""Cut5E storage: sixteen persistent actor slots and live borrowers.
Generated copies only for instrumentation; serial 600s/8-GiB children.
"""
import argparse,ctypes as C,hashlib,inspect,io,json,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/workers/close-stones-25'
REUSE_REVISION='38d51d3d4d5f5aa6207ba0c89de9bbd39201b17a'
sys.path.insert(0,str(ROOT/'tools'))
import resource_composition as catalog
player=catalog.player;prior=player.prior;run=prior.run;previous=run.previous
modules=[catalog,player]+player.modules
for module in modules:module.OUT=OUT
bounded=run.bounded;save=run.save;sha=run.sha
NEW=['native/actor_world.h','native/actor_world.c','native/bridge/actor_world_bridge.h','native/bridge/actor_world_bridge.c','native/bridge/actors_borrow.h']
BORROWERS=[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'native/bridge').glob('*')) if p.suffix in ['.c','.h'] and '#include "actors_borrow.h"' in p.read_text()]
BASE=NEW+BORROWERS+['verif/actor_composition.py','verif/actor_world_router.c','verif/actor_world_cases.py','verif/actor_world_byte_proof.c','tools/hostbuild.py','host/main.c','verif/projector/observer.c','verif/projector/timing_serializer.h','verif/projector/publications.py','verif/projector_evidence.py']
READ=sorted(set(catalog.READ+['verif/resource_composition.py','metadata/closure/resource_catalog.json','verif/resource_review.py']))
CONTEXT=player.CONTEXT
for unit in CONTEXT:READ+=['metadata/closure/'+unit+'.json']+json.loads((ROOT/('metadata/closure/'+unit+'.json')).read_text())['native']['files']
READ=sorted(set(READ+['verif/platform_composition.py','metadata/closure/platform_world.json','native/platform_world.h','native/platform_world.c','native/bridge/platform_world_bridge.c','native/bridge/platform_world_bridge.h','native/actors.h','native/actor_resources.h','native/actor_resources.c','docs/actor-storage.md','docs/standalone-cuts.md']))
WORLDS=catalog.WORLDS+['platform_world','actor_world'];TOTAL=11769
FIELDS=['ActorDescriptors', 'ActorInitialPlatformIndices', 'ActorJourneyCursors', 'ActorUpdateOrScriptCursor', 'ds_2A2D', 'ActorPlatformOrScriptDone', 'ActorDestinationPlatforms', 'ActorSourcePlatformByteIndices', 'ActorDestinationPlatformByteIndices', 'ds_2ACD', 'ActorX32', 'ActorY32', 'ActorPixelX', 'ActorPreviousDrawX', 'ActorPixelY', 'ActorPreviousDrawY', 'ActorAnimationByteOffsets', 'ActorAnimationCountdowns', 'ActorSpriteIds', 'ActorEraseSprite', 'ActorOverlayOrScriptCallbacks', 'ActorEraseOverlaySprite', 'ds_2C6D', 'PassengerQuickDeliveryCountdowns']
model=json.loads((ROOT/'metadata/program-model.json').read_text())
NAMES=sorted({routine.split(':')[1] for name in FIELDS for kind in ['readers','writers'] for routine in model['variables'][name][kind]}|{'InitializeLevelDisplay','LoadCurrentLevelState'})

def files():return sorted(set(BASE+subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()+['metadata/closure/actor_world.json']))
def snapshot():
 source=prior.RUN_SNAPSHOT_SOURCE.replace('metadata/closure/run_world.json','metadata/closure/actor_world.json')
 env=dict(run.__dict__,OUT=OUT,files=files);exec(source,env);return env['snapshot']()
for module in modules:module.snapshot=snapshot
build=previous.palette.build;levels=previous.palette.levels

def relock(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'relock',locals())

def inventory():
 assert sha(ROOT/'native/actors.h')==sha_bytes(subprocess.check_output(['git','show','HEAD:native/actors.h'],cwd=ROOT))
 assert sha(ROOT/'native/actor_resources.c')==sha_bytes(subprocess.check_output(['git','show','HEAD:native/actor_resources.c'],cwd=ROOT))
 save(OUT/'inventory.json',dict(result='PASS',bytes=768,total=TOTAL,region='DGROUP:29AD..2CAD',fields=FIELDS,readers_writers={n:model['variables'][n] for n in FIELDS},borrowers=BORROWERS,classification='One sixteen-slot physical lifetime; phase/mode adapters remain temporary checked views. All histories/inactive aliases and all raw identity words survive.',aliases='Platform occupant index10 aliases ActorDescriptors[0]; descriptor slot16 aliases next array, final actor cell ends before enemy storage. No spare slot or phase alias.',continuation='Storage-first 5E1 only. Stable descriptor/journey identities and direct callback/resume services remain in their existing checked adapters; no production raw-code resolver added.'))
def sha_bytes(data):
 return hashlib.sha256(data.replace(b'\r\n',b'\n')).hexdigest()

def api(group=None,*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'api',locals())

def router():
 folder=OUT/'router';folder.mkdir(exist_ok=True);exe=folder/'router.exe'
 bounded([previous.timing.common.GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/actor_world_router.c',ROOT/'native/actor_world.c',ROOT/'native/bridge/actor_world_bridge.c'],'router-compile')
 row=bounded([exe],'router-run');save(OUT/'router.json',dict(result='PASS',counts=json.loads(row['stdout']),scope='Independent literal address/member oracle; all768 bytes x256 and384 full16-bit slices; slot independence, all roles/straddles/paragraph aliases, platform occupant10 alias, cold import, seal/serialization/frame.'))

def proof():
 from closure_support import function
 folder=OUT/'proof';folder.mkdir(exist_ok=True);text=(ROOT/'native/bridge/actor_world_bridge.c').read_text()
 prefix='#include "actor_world.h"\n#include <stddef.h>\n#include "'+(ROOT/'native/actor_world.c').as_posix()+'"\n'
 prefix+='void *memcpy(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}\n'
 prefix+=re.search(r'typedef struct ActorsField.*?} ActorsField;',text,re.S)[0]+'\n'+''.join(function(text,n) for n in ['actors_field_get','actors_field_put'])
 prefix+='void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);\n#define assert(c) __CPROVER_assert((c),#c)\n'
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe'];rows=[]
 for name in ['read','store']:
  p=folder/(name+'.c');p.write_text(('#define ACTORS_PROOF_STORE\n' if name=='store' else '')+prefix+(ROOT/'verif/actor_world_byte_proof.c').read_text(),encoding='utf-8');pre=p.with_suffix('.i')
  bounded([previous.timing.common.GCC,'-E','-P','-nostdinc','-DUINT16_MAX=65535','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',p,'-o',pre],'proof-'+name+'-pre')
  r=bounded([tool,pre,'--unwind','5','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-'+name);assert 'VERIFICATION SUCCESSFUL' in r['stdout'];rows.append(dict(profile=name,preprocessed=sha(pre)))
 save(OUT/'proof.json',dict(result='PASS',profiles=rows,scope='Actual-C strided16-bit actor field byte get/put; arbitrary complete native world, any admitted slot, lane/value, valid member in first record and arbitrary-other-byte output/frame/dependence. Layout/registration via exhaustive router, not a resource/async theorem.'))

def reuse():
 # Accepted algorithms are unchanged. Header declaration order can change, so
 # compare actual default function bodies plus mechanically restored source.
 from standalone_census import bodies
 folder=OUT/'reuse';folder.mkdir(exist_ok=True);rows=[]
 for rel in BORROWERS:
  before=subprocess.check_output(['git','show',REUSE_REVISION+':'+rel],cwd=ROOT,text=True);after=(ROOT/rel).read_text()
  restored=re.sub(r'\A#include "platform.h"\n#ifndef ACTORS_BORROWER\n#define ACTORS_BORROWER ACTORS_BORROW_\w+\n#endif\n#include "actors_borrow.h"\n','',after,count=1)
  restored=re.sub(r'\bactors_read(8|16|32)\b',r'platforms_read\1',restored);restored=re.sub(r'\bactors_write(8|16|32)\b',r'platforms_write\1',restored);assert restored==before,rel
  if not rel.endswith('.c'):continue
  definitions=[]
  for i,text in enumerate([before,after]):
   text=re.sub(r'#include "([^\"]+)"',lambda m:'#include "'+str((ROOT/rel).parent.joinpath(m[1]).resolve()).replace('\\','/')+'"' if (ROOT/rel).parent.joinpath(m[1]).is_file() else m[0],text)
   p=folder/(str(i)+'-'+Path(rel).name);p.write_text(text);pre=p.with_suffix('.i');bounded([previous.timing.common.GCC,'-E','-P','-I',ROOT/'c',p,'-o',pre],'reuse-'+str(i)+'-'+p.stem);text=pre.read_text();definitions.append({n:re.findall(r'"(?:\\.|[^"\\])*"|\w+|[^\s]',text[a:e+1]) for a,b,e,n in bodies(text)})
  assert definitions[0]==definitions[1],rel;rows.append(rel)
 pure=[]
 for p in sorted((ROOT/'native').glob('*')):
  if p.suffix not in ['.c','.h'] or p.name.startswith('actor_world'):continue
  rel=p.relative_to(ROOT).as_posix();assert subprocess.check_output(['git','show',REUSE_REVISION+':'+rel],cwd=ROOT).replace(b'\r\n',b'\n')==p.read_bytes().replace(b'\r\n',b'\n'),rel;pure.append(rel)
 save(OUT/'reuse.json',dict(result='PASS',reference_revision=REUSE_REVISION,bridges=rows,pure_sources_unchanged=pure,scope='All accepted pure C/headers unchanged; borrower edits are mechanical accessor renames plus prefix; default bridge function bodies (including shared headers) identical. Original algorithm proofs/resource domains reused unchanged. New state seams have independent evidence.'))

def projector(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'projector',locals())

def census(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'census',locals())

def borrowers():
 import actor_world_cases
 actor_world_cases.run(ROOT,OUT,bounded,save)
def defects():
 import actor_world_cases
 actor_world_cases.defects(ROOT,OUT,bounded,save,snapshot,previous)
def deepcounts():
 import actor_world_cases
 actor_world_cases.deepcounts(ROOT,OUT,bounded,save,snapshot,previous)

def finalize(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'finalize',locals())

def main(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'main',locals())
# Scheduled by world_gate; no private CLI.
