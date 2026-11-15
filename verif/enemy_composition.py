"""Cut5F storage: five persistent enemy/hazard slots and live borrowers.
Generated copies only for instrumentation; serial 600s/8-GiB children.
"""
import argparse,ctypes as C,hashlib,inspect,io,json,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/workers/close-adlx-28'
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

def build():
 relock(final=(OUT/'verification-receipt.json').exists());previous.palette.build()


def relock(final=False):
 import closure
 p=ROOT/'metadata/closure/enemy_world.json'
 if not p.exists():
  save(p,dict(component='enemy_world',status='unanalyzed',original=dict(owned=[],composes=CONTEXT+['actor_pass','actor_render','demo_core','demo_presentation','actor_types','stones','passenger_itinerary','passenger_delivery','passenger_water','platform_world']),native=dict(files=NEW,functions=['native_enemy_world'],bridge='One persistent five-slot enemy owner, explicit live state borrowers, observation-only serialization'),purpose='Coherent cut5F: shared physical enemy storage and borrowers; identity/direct-continuation conversion remains separate',interface=dict(inputs='One cold provider fixture and live ordered byte/word mutations',outputs='190 native enemy bytes; sealed RAM and separate observation view'),callers=['Actor pass, actor render, demo, session, passenger/stone and hazard/contact borrowers'],callees=['Accepted platform/resource/player/run owner chain for unmoved views'],indirect=['Existing checked hazard callbacks remain; storage island adds no dispatcher'],memory=dict(owner='NativeEnemyWorld.slot[5],19 retained word fields per slot',total_with_prior=TOTAL),assumptions=['Existing valid physical slot/prefix, ordinary code/resource/stack domains and synchronous service cuts unchanged','Existing checked hazard descriptor/callback/animation/resource domains unchanged; inactive fields retained without interpretation','Cold import once, observation-only serialize, no writeback/resynchronization'],eliminated=['RAM ownership of all190 enemy bytes'],retained=['Persistent histories across modes and explicit scene/placement seeds','Raw identity transport words retain all byte values; existing adapters alone decode them','Enemy descriptor index5 aliases first platform-index word; longer raw reset aliases retained'],evidence=[dict(property='Enemy ownership seam',level='D',method='Pending replay',command='python verif/enemy_composition.py --gate',result='Pending',date='2026-11-15')],amiga=dict(classification='not-used',finding='Composition over accepted DOS contracts'),uncertainty=['Cut5F: stable registry identities and direct typed callback/resume conversion remain recorded continuation'],dependencies={},verification_inputs={},verification_input_hashing='sha256-lf-text'))
 source=inspect.getsource(run.relock);source='def refresh(final=False):\n'+source[source.index(' old='):]
 source=source.replace("'run_world'","'enemy_world'").replace('Run ownership and explicit shared borrowers','Shared enemy-slot ownership and explicit live borrowers').replace('Pending cut 5A replay','Pending cut5F storage replay').replace('verif/run_composition.py','verif/enemy_composition.py')
 env=dict(run.__dict__,NEW=NEW,BASE=BASE,READ=READ,OUT=OUT,closure=closure);exec(source,env);env['refresh'](final)

def inventory():
 save(OUT/'inventory.json',dict(result='PASS',bytes=190,total=TOTAL,region='DGROUP:2CAD..2D6B',fields=FIELDS,readers_writers={n:model['variables'][n] for n in FIELDS},borrowers=BORROWERS,classification='One five-slot physical lifetime, raw identity words explicitly retained; temporary checked HazardWorld is not an owner.',aliases='Descriptor index5 aliases platform[0]. Demo reset sixteen raw indices preserves overlapping and extra raw views. No sixth slot or ownership outside190 bytes.',continuation='Descriptor/callback/list/sound-handle words remain raw compatibility data; typed registries/direct continuation are later cuts.'))

def sha_bytes(data):
 return hashlib.sha256(data.replace(b'\r\n',b'\n')).hexdigest()

def api(group):
 if group=='front':
  import difftest
  cases=[c for s in ['menu','menu_helpers','game_services'] for c in difftest.load_suite(s).CASES if c.routine.split(':')[1] in NAMES];assert not cases
  save(OUT/'api-front.json',dict(result='PASS',composed_matching=0,legacy_matching=0,compatibility_cases=[],explicit_out_of_domain=[],seam_inputs={f:sha(ROOT/f) for f in NEW+BORROWERS+['tools/hostbuild.py']},scope='Unaffected front-end suites have no enemy-field readers/writers; zero cases explicitly inventoried, not evidence of native executions.'));return
 source=inspect.getsource(run.api)
 source=source.replace("['run_world','presentation_world'","['enemy_world','actor_world','platform_world','resource_catalog','player_world','random_world','run_world','presentation_world'")
 source=source.replace("('RUN','run')])","('RUN','run'),('RANDOM','rng'),('PLAYER','player'),('RESOURCES','resources'),('PLATFORMS','platforms'),('ACTORS','actors'),('ENEMIES','enemies')])")
 source=source.replace('annotate_api(group)','run.annotate_api(group)')
 if group=='physics':
  source=source.replace("suites={'front':['menu','menu_helpers','game_services'],'world':['scene','actors','actors_states','items_water','demo_scripts'],'input':['dos_input','render','render_primitives']}[group]","suites=[]")
  source=source.replace(r'\n names=sorted',r"\n import player_physics_l0_cases\n cases += [('scene',c) for c in player_physics_l0_cases.cases()]\n names=sorted")
 env=dict(run.__dict__,NEW=NEW,BORROWERS=BORROWERS,WORLDS=WORLDS,NAMES=NAMES,OUT=OUT,run=run);exec(source,env);env['api'](group)

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

def projector():
 source=inspect.getsource(previous.palette.projector).replace('==6148','=='+str(TOTAL)).replace('Palette ownership cut only','Enemy ownership cut5F')
 env=dict(previous.palette.__dict__);exec(source,env);env['projector']()
 runs=[json.loads(p.read_text()) for p in (OUT/'projector/runs').glob('*.json')]
 assert len(runs)==21
 for r in runs:
  enemy=next(x for x in r['owners'] if x['name']=='enemies');assert enemy['typed_bytes']==190 and enemy['write_deliveries']==0 and enemy['touched_bytes']==0
 save(OUT/'projector-owned.json',dict(result='PASS',boundaries=sum(r['boundaries'] for r in runs),enemy_native_bytes=190,enemy_journal_publications=0,total_native_before=11769,total_native_after=TOTAL,scope='Every enemy byte serialized only from canonical NativeEnemyWorld; no moved byte imported from a journal or retained shadow. Frozen-boundary control targets the canonical raw enemy descriptor.'))

def census():
 source=inspect.getsource(previous.census)
 leaves={'platform_world':['platforms_field','platforms_field_get','platforms_field_put','platforms_is_owned','platforms_shared_read','platforms_shared_write','platforms_borrowed_byte','platforms_borrowed_store','platforms_borrow_read','platforms_borrow_write'],'actor_world':['actors_field','actors_field_get','actors_field_put','actors_is_owned','actors_shared_read','actors_shared_write','actors_borrowed_byte','actors_borrowed_store','actors_borrow_read','actors_borrow_write'],'enemy_world':['enemies_field','enemies_field_get','enemies_field_put','enemies_is_owned','enemies_shared_read','enemies_shared_write','enemies_borrowed_byte','enemies_borrowed_store','enemies_borrow_read','enemies_borrow_write'],'resource_catalog':['sprite_base','codec_base','resources_field','resources_is_owned','resources_shared_read','resources_shared_write','resources_borrowed_byte','resources_borrowed_store','resource_sprite_from_legacy','resource_effect_from_legacy','resource_table_from_legacy','resource_token_to_legacy'],'player_world':['player_field','player_field_get','player_field_put','player_is_owned','player_shared_read','player_shared_write','player_borrowed_byte','player_borrowed_store','player_borrow_read','player_borrow_write'],'random_world':['rng_lane','rng_get','rng_put','rng_is_owned','rng_shared_read','rng_shared_write','rng_borrowed_byte','rng_borrowed_store','rng_borrow_read','rng_borrow_write'],'run_world':['run_field','run_field_get','run_field_put','run_is_owned','run_shared_read','run_shared_write','run_borrowed_byte','run_borrowed_store','run_borrow_read','run_borrow_write']}
 source=source.replace("'presentation_world':['presentation_field'",''.join(repr(n)+':'+repr(v)+',\n ' for n,v in leaves.items())+"'presentation_world':['presentation_field'",1).replace("paths={'native/bridge/hud_bridge.c','native/bridge/water_weather_bridge.c','native/bridge/presentation_world_bridge.c'}","paths={'native/bridge/enemy_world_bridge.c'}").replace("'-DUGH_NATIVE_PRESENTATION','-I'","'-DUGH_NATIVE_PRESENTATION','-DUGH_NATIVE_RUN','-DUGH_NATIVE_RANDOM','-DUGH_NATIVE_PLAYER','-DUGH_NATIVE_RESOURCES','-DUGH_NATIVE_PLATFORMS','-DUGH_NATIVE_ACTORS','-DUGH_NATIVE_ENEMIES','-I'")
 source=source.replace('Native HUD/weather bridges and owner; session/menu/high-score callers remain explicit borrowers, not part of this machine-edge island.','Five-slot enemy state/borrower island. Existing sequencing remains outside until its planned cuts.')
 env=dict(previous.__dict__,snapshot=snapshot,NAMES=NAMES);exec(source,env);env['census']()
 census_notes()

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

def finalize():
 census_notes()
 names=['inventory','router','proof','reuse','api-front','api-world','api-input','api-physics','borrowers','census','levels','deep-counts','defects']
 results={n:json.loads((OUT/(n+'.json')).read_text()) for n in names};assert all(r['result']=='PASS' for r in results.values())
 for g in ['front','world','input','physics']:
  r=results['api-'+g];assert not r['explicit_out_of_domain'];assert all(sha(ROOT/f)==h for f,h in r['seam_inputs'].items())
 runs=[json.loads(p.read_text()) for p in (OUT/'projector/runs').glob('*.json')];assert len(runs)==21 and all(r['canonical_native_owned_bytes']==TOTAL and not r['native_owned_journal_publications'] for r in runs)
 p=ROOT/'metadata/closure/enemy_world.json';c=json.loads(p.read_text());c['proposed_status']='migrated';c['memory'].update(region='DGROUP:2CAD..2D6B',bytes=190,slots=5,fields=FIELDS,borrowers=BORROWERS)
 total=sum(results['api-'+g]['composed_matching'] for g in ['front','world','input','physics']);compat=sum(len(results['api-'+g]['compatibility_cases']) for g in ['front','world','input','physics'])
 c['assumptions']=['Existing checked hazard descriptor/callback/animation/resource domains unchanged; inactive fields retained without interpretation','Exactly five physical slots; foreign and longer raw indexed views retain the accepted owners','Cold import once; historical RAM is sealed and serialization never writes back or resynchronizes']
 c['memory'].update(native_bytes_before=11769,native_bytes_after=TOTAL,observation='All190 bytes emitted from NativeEnemyWorld only; zero moved-owner journal publications',registry_continuation='Raw descriptor/callback/animation-list/sound-handle words remain compatibility data, as actor_world; typed registries/direct continuations remain later work')
 c['evidence']=[dict(property='Actual-C byte state seam',level='B',method=results['proof']['scope'],command='python verif/enemy_composition.py --router --proof',result='PASS: exhaustive byte/word/address/slot/alias plus split actual-C output/frame/dependence',date='2026-11-15'),dict(property='API and live borrowers',level='C',method=results['borrowers']['scope'],command='python verif/enemy_composition.py --api-front --api-world --api-input --api-physics --borrowers --reuse',result=f'PASS: {total} matching cases per profile; zero new rejections; {compat} existing broader compatibility cases explicitly enumerated and not credited as native algorithm executions',date='2026-11-15'),dict(property='Composed storage',level='D',method='Committed baseline plus owned overlay, scratch promotion and independent ASM references',command='python verif/enemy_composition.py --build --projector --census --levels --deepcounts',result=f'PASS: closure59/0; host21/21 both variants; {sum(r["boundaries"] for r in runs)} boundaries,11959 native bytes; zero owner journals/fallbacks/L1 game bodies/enemy storage island machine edges;81+7+8 levels both variants',date='2026-11-15'),dict(property='Defect sensitivity',level='C',method=results['defects']['scope'],command='python verif/enemy_composition.py --defects',result='PASS: all generated controls detected; unchanged callback/phase algorithm evidence reused without stronger claims',date='2026-11-15')]
 save(p,c);relock(final=True);save(OUT/'verification-receipt.json',dict(result='PASS',status=c['status'],proposed_status='migrated',scope='Cut5F storage+borrowers only',bytes=190,total=TOTAL,evidence={n:sha(OUT/(n+'.json')) for n in results},relocks=json.loads((OUT/'relocks.json').read_text())))

def main():
 p=argparse.ArgumentParser(description=__doc__);stages=['locks','inventory','router','proof','reuse','api-front','api-world','api-input','api-physics','borrowers','build','projector','census','levels','deepcounts','defects','finalize','gate','internal']
 for s in stages:p.add_argument('--'+s,action='store_true')
 a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
 if a.locks:relock()
 if a.gate:
  relock()
  for s in stages[1:-3]:bounded([sys.executable,__file__,'--'+s,'--internal'],s+'-child')
  finalize();build();return
 for s in stages[1:-2]:
  if getattr(a,s.replace('-','_')):
   if a.internal:
    if s.startswith('api-'):api(s[4:])
    else:globals()[s]()
   else:bounded([sys.executable,__file__,'--'+s,'--internal'],s+'-child')
if __name__=='__main__':main()
