"""Cut5F storage: five persistent enemy/hazard slots and live borrowers.
Generated copies only for instrumentation; serial 600s/8-GiB children.
"""
import argparse,ctypes as C,hashlib,inspect,io,json,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/workers/close-adlx-28'
REUSE_REVISION='57069e31a2ca27540e75a7c387d7d91af59260ac'
sys.path.insert(0,str(ROOT/'tools'))
import actor_composition as accepted
catalog=accepted.catalog
player=catalog.player;prior=player.prior;run=prior.run;previous=run.previous
modules=[accepted]+accepted.modules
for module in modules:module.OUT=OUT
bounded=run.bounded;save=run.save;sha=run.sha
# Assign a suspended child before it can exit (the shared runner races fast GCC).
import os,time
from windows_job import WindowsJob,ExtendedLimits

def bounded(command,tag,cwd=ROOT):
 OUT.mkdir(parents=True,exist_ok=True);command=list(map(str,command));start=time.perf_counter()
 env=dict(os.environ,PATH=str(previous.timing.common.GCC.parent)+os.pathsep+os.environ.get('PATH',''))
 with WindowsJob() as job:
  limits=ExtendedLimits();limits.basic.flags=0x2000|0x100|0x200;limits.process_memory=limits.job_memory=8*1024**3
  if not job.kernel.SetInformationJobObject(job.handle,9,C.byref(limits),C.sizeof(limits)):raise C.WinError(C.get_last_error())
  p=subprocess.Popen(command,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,creationflags=4);job.assign(p)
  resume=C.WinDLL('ntdll').NtResumeProcess;resume.argtypes=[C.c_void_p];resume.restype=C.c_long
  if resume(int(p._handle))!=0:job.terminate();p.wait();raise RuntimeError('resume failed')
  try:stdout,stderr=p.communicate(timeout=600)
  except subprocess.TimeoutExpired:
   job.terminate();stdout,stderr=p.communicate();save(OUT/'children'/f'{tag}.json',dict(result='TIMEOUT',stdout=stdout,stderr=stderr));raise RuntimeError(tag+' timed out')
 row=dict(command=command,cwd=str(cwd),stdout=stdout,stderr=stderr,returncode=p.returncode,seconds=time.perf_counter()-start,timeout_seconds=600,memory_limit_bytes=8*1024**3)
 save(OUT/'children'/f'{tag}.json',row)
 if p.returncode:
  save(OUT/'negative'/f'{tag}-{time.time_ns()}.json',row);raise RuntimeError(tag+': '+stdout[-2000:]+stderr[-4000:])
 print(tag,'PASS',round(row['seconds'],2),'s',flush=True);return row
for module in modules:module.bounded=bounded
NEW=['native/enemy_world.h','native/enemy_world.c','native/bridge/enemy_world_bridge.h','native/bridge/enemy_world_bridge.c','native/bridge/enemies_borrow.h']
BORROWERS=[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'native/bridge').glob('*')) if p.suffix in ['.c','.h'] and '#include "enemies_borrow.h"' in p.read_text()]
BASE=NEW+BORROWERS+['verif/enemy_composition.py','verif/enemy_world_router.c','verif/enemy_world_cases.py','verif/enemy_world_byte_proof.c','tools/hostbuild.py','host/main.c','verif/projector/observer.c','verif/projector/timing_serializer.h','verif/projector/publications.py','verif/projector_evidence.py']
READ=sorted(set(catalog.READ+['verif/resource_composition.py','metadata/closure/resource_catalog.json','verif/resource_review.py']))
CONTEXT=player.CONTEXT
for unit in CONTEXT:READ+=['metadata/closure/'+unit+'.json']+json.loads((ROOT/('metadata/closure/'+unit+'.json')).read_text())['native']['files']
READ=sorted(set(READ+['verif/actor_composition.py','metadata/closure/actor_world.json','native/actor_world.h','native/actor_world.c','native/bridge/actor_world_bridge.c','native/bridge/actor_world_bridge.h','verif/platform_composition.py','metadata/closure/platform_world.json','native/platform_world.h','native/platform_world.c','native/bridge/platform_world_bridge.c','native/bridge/platform_world_bridge.h','native/actors.h','native/actor_resources.h','native/actor_resources.c','docs/actor-storage.md','docs/standalone-cuts.md']))
WORLDS=accepted.WORLDS+['enemy_world'];TOTAL=11959
FIELDS=['EnemyDescriptors', 'EnemyPlatformIndices', 'EnemyX32', 'EnemyY32', 'EnemyAnimationOrDropLists', 'EnemyInitialDelays', 'EnemyHorizontalSpeeds', 'EnemyStateCallbacks', 'EnemyStateCounters', 'EnemyDrawX', 'EnemyPreviousDrawX', 'EnemyDrawY', 'EnemyPreviousDrawY', 'EnemyAnimationByteOffsets', 'EnemyAnimationCountdowns', 'EnemySpriteIds', 'EnemyEraseSprite', 'EnemyDirectionOrTargetPlayer', 'EnemyFlightSoundHandles']
model=json.loads((ROOT/'metadata/program-model.json').read_text())
NAMES=sorted({routine.split(':')[1] for name in FIELDS for kind in ['readers','writers'] for routine in model['variables'][name][kind]}|{'InitializeLevelDisplay','LoadCurrentLevelState'})

def files():return sorted(set(BASE+subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()+['metadata/closure/enemy_world.json']))
def snapshot():
 source=prior.RUN_SNAPSHOT_SOURCE.replace('metadata/closure/run_world.json','metadata/closure/enemy_world.json')
 env=dict(run.__dict__,OUT=OUT,files=files);exec(source,env);return env['snapshot']()
for module in modules:module.snapshot=snapshot
levels=previous.palette.levels

def build(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'build',locals())


def relock(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'relock',locals())

def inventory():
 save(OUT/'inventory.json',dict(result='PASS',bytes=190,total=TOTAL,region='DGROUP:2CAD..2D6B',fields=FIELDS,readers_writers={n:model['variables'][n] for n in FIELDS},borrowers=BORROWERS,classification='One five-slot physical lifetime, raw identity words explicitly retained; temporary checked HazardWorld is not an owner.',aliases='Descriptor index5 aliases platform[0]. Demo reset sixteen raw indices preserves overlapping and extra raw views. No sixth slot or ownership outside190 bytes.',continuation='Descriptor/callback/list/sound-handle words remain raw compatibility data; typed registries/direct continuation are later cuts.'))

def sha_bytes(data):
 return hashlib.sha256(data.replace(b'\r\n',b'\n')).hexdigest()

def api(group=None,*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'api',locals())

def router():
 folder=OUT/'router';folder.mkdir(exist_ok=True);exe=folder/'router.exe'
 bounded([previous.timing.common.GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/enemy_world_router.c',ROOT/'native/enemy_world.c',ROOT/'native/bridge/enemy_world_bridge.c'],'router-compile')
 row=bounded([exe],'router-run');save(OUT/'router.json',dict(result='PASS',counts=json.loads(row['stdout']),scope='Independent literal address/member oracle; all190 bytes x256 and95 full16-bit slices; slot independence, all roles/straddles/paragraph aliases, descriptor index5 alias, cold import, seal/serialization/frame.'))

def proof():
 from closure_support import function
 folder=OUT/'proof';folder.mkdir(exist_ok=True);text=(ROOT/'native/bridge/enemy_world_bridge.c').read_text()
 prefix='#include "enemy_world.h"\n#include <stddef.h>\n#include "'+(ROOT/'native/enemy_world.c').as_posix()+'"\n'
 prefix+='void *memcpy(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}\n'
 prefix+=re.search(r'typedef struct EnemiesField.*?} EnemiesField;',text,re.S)[0]+'\n'+''.join(function(text,n) for n in ['enemies_field_get','enemies_field_put'])
 prefix+='void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);\n#define assert(c) __CPROVER_assert((c),#c)\n'
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe'];rows=[]
 for name in ['read','store']:
  p=folder/(name+'.c');p.write_text(('#define ENEMIES_PROOF_STORE\n' if name=='store' else '')+prefix+(ROOT/'verif/enemy_world_byte_proof.c').read_text(),encoding='utf-8');pre=p.with_suffix('.i')
  bounded([previous.timing.common.GCC,'-E','-P','-nostdinc','-DUINT16_MAX=65535','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',p,'-o',pre],'proof-'+name+'-pre')
  r=bounded([tool,pre,'--unwind','5','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-'+name);assert 'VERIFICATION SUCCESSFUL' in r['stdout'];rows.append(dict(profile=name,preprocessed=sha(pre)))
 save(OUT/'proof.json',dict(result='PASS',profiles=rows,scope='Actual-C strided16-bit enemy field byte get/put; arbitrary complete native world, any admitted slot, lane/value, valid member in first record and arbitrary-other-byte output/frame/dependence. Layout/registration via exhaustive router, not a resource/async theorem.'))

def reuse():
 # Accepted algorithms are unchanged. Header declaration order can change, so
 # compare actual default function bodies plus mechanically restored source.
 from standalone_census import bodies
 folder=OUT/'reuse';folder.mkdir(exist_ok=True);rows=[]
 for rel in BORROWERS:
  before=subprocess.check_output(['git','show',REUSE_REVISION+':'+rel],cwd=ROOT,text=True);after=(ROOT/rel).read_text()
  restored=re.sub(r'\A#include "platform.h"\n#ifndef ENEMIES_BORROWER\n#define ENEMIES_BORROWER ENEMIES_BORROW_\w+\n#endif\n#include "enemies_borrow.h"\n','',after,count=1)
  restored=re.sub(r'\benemies_read(8|16|32)\b',r'actors_read\1',restored);restored=re.sub(r'\benemies_write(8|16|32)\b',r'actors_write\1',restored);assert restored==before,rel
  if not rel.endswith('.c'):continue
  definitions=[]
  for i,text in enumerate([before,after]):
   text=re.sub(r'#include "([^\"]+)"',lambda m:'#include "'+str((ROOT/rel).parent.joinpath(m[1]).resolve()).replace('\\','/')+'"' if (ROOT/rel).parent.joinpath(m[1]).is_file() else m[0],text)
   p=folder/(str(i)+'-'+Path(rel).name);p.write_text(text);pre=p.with_suffix('.i');bounded([previous.timing.common.GCC,'-E','-P','-I',ROOT/'c',p,'-o',pre],'reuse-'+str(i)+'-'+p.stem);text=pre.read_text();definitions.append({n:re.findall(r'"(?:\\.|[^"\\])*"|\w+|[^\s]',text[a:e+1]) for a,b,e,n in bodies(text)})
  assert definitions[0]==definitions[1],rel;rows.append(rel)
 pure=[]
 for p in sorted((ROOT/'native').glob('*')):
  if p.suffix not in ['.c','.h'] or p.name.startswith('enemy_world'):continue
  rel=p.relative_to(ROOT).as_posix();assert subprocess.check_output(['git','show',REUSE_REVISION+':'+rel],cwd=ROOT).replace(b'\r\n',b'\n')==p.read_bytes().replace(b'\r\n',b'\n'),rel;pure.append(rel)
 save(OUT/'reuse.json',dict(result='PASS',reference_revision=REUSE_REVISION,bridges=rows,pure_sources_unchanged=pure,scope='All accepted pure C/headers unchanged; borrower edits are mechanical accessor renames plus prefix; default bridge function bodies (including shared headers) identical. Original algorithm proofs/resource domains reused unchanged. New state seams have independent evidence.'))

def projector(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'projector',locals())

def census(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'census',locals())

def census_notes():
 p=OUT/'census.json';c=json.loads(p.read_text())
 for row in c['unreached']:row['coverage']='Compiled API/Unicorn cases where present; per-level counters in deep-counts.json. No synthetic callers added to maintained scenarios.'
 save(p,c)

def borrowers():
 import enemy_world_cases
 enemy_world_cases.run(ROOT,OUT,bounded,save)
def defects():
 import enemy_world_cases
 enemy_world_cases.defects(ROOT,OUT,bounded,save,snapshot,previous)
def deepcounts():
 import enemy_world_cases
 enemy_world_cases.deepcounts(ROOT,OUT,bounded,save,snapshot,previous)

def finalize(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'finalize',locals())

def main(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'main',locals())
# Scheduled by world_gate; no private CLI.
