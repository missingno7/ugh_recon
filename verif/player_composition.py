"""Cut5C: both native players and live command/history borrowers.
Generated copies only for instrumentation; serial 600s/8-GiB children.
"""
import argparse,ctypes as C,hashlib,inspect,io,json,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/workers/close-adlx-26'
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

def relock(final=False):
 import closure
 p=ROOT/'metadata/closure/player_world.json'
 if not p.exists():
  save(p,dict(component='player_world',status='unanalyzed',original=dict(owned=[],composes=['player_physics','input','session','render_primitives','hud','actor_types','stones','passenger_delivery','hazards']),native=dict(files=NEW,functions=['native_player_world'],bridge='One both-player native store, explicit live role/byte borrowers and observation-only serializer'),purpose='Cut5C: players, independent simulation/draw/history pixels and five command words per player',interface=dict(inputs='One cold fixture import; live physics/input/actor/session/HUD/render byte/word transactions',outputs='92 native historical bytes, sealed RAM and separate observation serialization'),callers=['Input, physics, actors/stone/passenger/hazard, session/loader, HUD/render and physical byte windows'],callees=['Existing native owner chain for foreign/unmoved views'],indirect=['No callback or dispatcher in the player storage island'],memory=dict(owner='One NativePlayerWorld.player[2],46 bytes each; command20+motion/render/carried72',total_with_prior=TOTAL),assumptions=['Accepted algorithm/resource/ABI domains unchanged','Cold import is fixture initialization only; no resynchronization'],eliminated=['RAM ownership of player state and its shared scalar reads/stores'],retained=['Independent fixed/current/cache/history words; partial IRQ bytes retain high lanes','Both players seeded in one-player mode; inclusive byte-index loop limits','Cycle bounds and impact limits remain resource/shared views; interleaved HUD words remain presentation-owned'],evidence=[dict(property='Player storage composition',level='D',method='Pending replay',command='python verif/player_composition.py --gate',result='Pending',date='2026-11-15')],amiga=dict(classification='not-used',finding='Composition over accepted DOS contracts'),uncertainty=['Storage-first: remaining control ABI orchestration and resource providers stay in their later cuts'],dependencies={},verification_inputs={},verification_input_hashing='sha256-lf-text'))
 source=inspect.getsource(run.relock);source='def refresh(final=False):\n'+source[source.index(' old='):]
 source=source.replace("'run_world'","'player_world'").replace('Run ownership and explicit shared borrowers','Both-player ownership and explicit live borrowers').replace('Pending cut 5A replay','Pending cut5C replay').replace('verif/run_composition.py','verif/player_composition.py')
 env=dict(run.__dict__,NEW=NEW,BASE=BASE,READ=READ,OUT=OUT,closure=closure);exec(source,env);env['refresh'](final)

def inventory():
 symbols=(ROOT/'c/ugh_sym.h').read_text();addresses={n:int(re.search(r'#define UGH_O_DGDATA_'+n+r' (0x[0-9A-F]+)',symbols)[1],16) for n in FIELDS}
 save(OUT/'inventory.json',dict(result='PASS',bytes=92,total=TOTAL,regions=[dict(offset='278C',length=20),dict(offset='27D0',length=48),dict(offset='2804',length=24)],named_aliases=addresses,readers_writers={n:model['variables'][n] for n in FIELDS},borrowers=BORROWERS,excluded_hud='2800..2803 belongs to presentation_world',resource_shared_view='Cycle starts0CFA/0CFC and ends0CFC/0CFE share word0CFC. No model writers; both views remain foreign resource bytes, not player ownership. Impact limits remain resource views.',semantics='Both records exist independently; pixel/draw caches and histories are not rebuilt; five16-bit command words per player preserve low-byte IRQ writes and stale high bytes. Existing loader initializes both players and movement loops retain index<=PlayerCount.'))

def api(group):
 if group=='front':
  import difftest
  selected=[c for s in ['menu','menu_helpers','game_services'] for c in difftest.load_suite(s).CASES if c.routine.split(':')[1] in NAMES]
  if not selected:
   save(OUT/'api-front.json',dict(result='PASS',composed_matching=0,legacy_matching=0,explicit_out_of_domain=[],compatibility_cases=[],seam_inputs={f:sha(ROOT/f) for f in NEW+BORROWERS+['tools/hostbuild.py']},scope='No direct player-state entry in these suites; no API or service-stream evidence claimed. Front-end integration remains covered by whole-game scenarios and unchanged-source reuse.'));return
 source=inspect.getsource(run.api)
 source=source.replace("['run_world','presentation_world'","['player_world','random_world','run_world','presentation_world'")
 source=source.replace("('RUN','run')])","('RUN','run'),('RANDOM','rng'),('PLAYER','player')])")
 source=source.replace('annotate_api(group)','run.annotate_api(group)')
 if group=='physics':
  source=source.replace("suites={'front':['menu','menu_helpers','game_services'],'world':['scene','actors','actors_states','items_water','demo_scripts'],'input':['dos_input','render','render_primitives']}[group]","suites=[]")
  source=source.replace(r'\n names=sorted',r"\n import player_physics_l0_cases\n cases += [('scene',c) for c in player_physics_l0_cases.cases()]\n names=sorted")
 env=dict(run.__dict__,NEW=NEW,BORROWERS=BORROWERS,WORLDS=WORLDS,NAMES=NAMES,OUT=OUT,run=run);exec(source,env);env['api'](group)

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

def projector():
 source=inspect.getsource(previous.palette.projector).replace('==6148','=='+str(TOTAL)).replace('Palette ownership cut only','Both-player ownership cut5C')
 env=dict(previous.palette.__dict__);exec(source,env);env['projector']()

def census():
 source=inspect.getsource(previous.census)
 leaves={'player_world':['player_field','player_field_get','player_field_put','player_is_owned','player_shared_read','player_shared_write','player_borrowed_byte','player_borrowed_store','player_borrow_read','player_borrow_write'],'random_world':['rng_lane','rng_get','rng_put','rng_is_owned','rng_shared_read','rng_shared_write','rng_borrowed_byte','rng_borrowed_store','rng_borrow_read','rng_borrow_write'],'run_world':['run_field','run_field_get','run_field_put','run_is_owned','run_shared_read','run_shared_write','run_borrowed_byte','run_borrowed_store','run_borrow_read','run_borrow_write']}
 source=source.replace("'presentation_world':['presentation_field'",''.join(repr(n)+':'+repr(v)+',\n ' for n,v in leaves.items())+"'presentation_world':['presentation_field'",1)
 source=source.replace("paths={'native/bridge/hud_bridge.c','native/bridge/water_weather_bridge.c','native/bridge/presentation_world_bridge.c'}","paths={'native/bridge/player_world_bridge.c'}")
 source=source.replace("'-DUGH_NATIVE_PRESENTATION','-I'","'-DUGH_NATIVE_PRESENTATION','-DUGH_NATIVE_RUN','-DUGH_NATIVE_RANDOM','-DUGH_NATIVE_PLAYER','-I'")
 source=source.replace('Native HUD/weather bridges and owner; session/menu/high-score callers remain explicit borrowers, not part of this machine-edge island.','Both-player storage owner and explicit live byte/role borrowers only; existing gameplay/control orchestration remains outside until its planned cuts.')
 env=dict(previous.__dict__,OUT=OUT,snapshot=snapshot,NAMES=NAMES);exec(source,env);env['census']()

def borrowers():
 import player_world_cases
 player_world_cases.run(ROOT,OUT,bounded,save)
def defects():
 import player_world_cases
 player_world_cases.defects(ROOT,OUT,bounded,save,snapshot,previous)

def finalize():
 groups=['front','world','input','physics']
 names=['inventory','router','proof','reuse',*['api-'+g for g in groups],'borrowers','census','levels','defects']
 results={n:json.loads((OUT/(n+'.json')).read_text()) for n in names};assert all(r['result']=='PASS' for r in results.values())
 coverage={}
 import difftest,player_physics_l0_cases
 suites={'front':['menu','menu_helpers','game_services'],'world':['scene','actors','actors_states','items_water','demo_scripts'],'input':['dos_input','render','render_primitives'],'physics':[]}
 for group in groups:
  receipt=results['api-'+group];assert not receipt['explicit_out_of_domain']
  assert all(sha(ROOT/f)==h for f,h in receipt['seam_inputs'].items()),'API source replay required'
  cases=[(s,c) for s in suites[group] for c in difftest.load_suite(s).CASES if c.routine.split(':')[1] in NAMES]
  if group=='physics':cases=[('scene',c) for c in player_physics_l0_cases.cases()]
  for label,profile in receipt.get('profiles',{}).items():
   if label=='reference':continue
   assert len(profile['cases'])==len(cases)*2
   for i,row in enumerate(profile['cases']):
    suite,case=cases[i//2];assert row['suite']==suite and row['case']==case.title
    row['routine']=case.routine
    if label=='composed':coverage.setdefault(case.routine,dict(runs=0,compatibility_runs=0));coverage[case.routine]['runs']+=1;coverage[case.routine]['compatibility_runs']+=bool(row['timer_fallbacks'])
  save(OUT/('api-'+group+'.json'),receipt)
 assert all(results['api-'+g]['composed_matching']>0 for g in ['world','input','physics'])
 runs=[json.loads(p.read_text()) for p in (OUT/'projector/runs').glob('*.json')];assert len(runs)==21 and all(r['canonical_native_owned_bytes']==TOTAL and not r['native_owned_journal_publications'] for r in runs)
 cpath=ROOT/'metadata/closure/player_world.json';c=json.loads(cpath.read_text());c['proposed_status']='migrated';c['original']['composes']=CONTEXT
 c['memory'].update(regions=results['inventory']['regions'],named_aliases=results['inventory']['named_aliases'],shared_resources=results['inventory']['resource_shared_view'],borrower_files=BORROWERS)
 c['interface']['borrowers']='Input: partial-byte command stores and polling words; physics/contacts/hazards, stones/passengers/items and actor passes: live player fields; session role includes descending loader seeds and ordered reset; HUD/render: current pixels, retained caches/sprites and carried/fare fields; window roles: physical copy/decimal/ICE aliases'
 c['assumptions']=['Existing accepted algorithms, code/resource/stack/provider domains unchanged; no theorem is widened','Both physical records always exist. Fixed positions, simulation pixels, draw caches/history, animation, platform, carried/destination/fare/minimum-fare and each command word are independent retained raw16-bit patterns','Two-word physical arrays map into two native player records via an explicit stride; unusual raw byte indices retain physical cross-field aliases, not invented third-player storage','Interleaved HUD icon caches2800..2803 remain presentation-owned. Cycle starts0CFA/0CFC and ends0CFC/0CFE share one existing resource word; impact limits remain resource views. No model writer is not a constness proof; foreign byte windows still preserve mutations','Cold import is verification fixture initialization only; live moved RAM stays sealed and serializers write only the separate observation view','Callbacks/service replies are synchronous under the accepted scheduler. Live reply and post-stone mutation evidence is finite; no new asynchronous delivery or backend policy','Atomic ICE has equal returned RAM/ports; internal backwards decode versus ascending completed-buffer publication is not a write-instruction stream contract']
 c['uncertainty']=['Storage-first cut: existing session/gameplay control/Regs adapters remain outside the new state island for their later sequencing cuts','Broader API compatibility fallbacks are listed by case/routine and are not credited as native algorithm executions; no such fallback occurs in maintained scenarios','Resource-provider review5R and production port decisions remain separate; cycle/impact resources are explicitly borrowed']
 total=sum(results['api-'+g]['composed_matching'] for g in groups);compat=sum(len(results['api-'+g]['compatibility_cases']) for g in groups)
 c['evidence']=[dict(property='Actual-C strided player byte seam',level='B',method=results['proof']['scope'],command='python verif/player_composition.py --router --proof',result='PASS: split read/store profiles;92 lanes x256,46 full16-bit slices, cold/frame/seal/alias/role checks and shared cycle word',date='2026-11-15'),dict(property='Independent API and live shared writers',level='C',method=results['borrowers']['scope'],command='python verif/player_composition.py --api-world --api-input --api-physics --borrowers --reuse',result=f'PASS: {total} replay runs per profile, zero new rejections; {compat} broader compatibility cases enumerated separately; every150 logical level seed and live borrower prefixes; unchanged algorithm proofs reused',date='2026-11-15'),dict(property='Player ownership integration',level='D',method='Committed HEAD archive plus only cut files; scratch certificate promotion; independent ASM references, sealed moved RAM and observation-only typed serialization',command='python verif/player_composition.py --build --projector --census --levels',result=f'PASS: closure55/0; host21/21 both variants with literal pure L1; {sum(r["boundaries"] for r in runs)} boundaries,8133 native bytes, zero moved journal publications/fallbacks/L1 bodies/in-island machine-control edges;81+7+8 levels both variants including two-player',date='2026-11-15'),dict(property='Defect sensitivity',level='C',method=results['defects']['scope'],command='python verif/player_composition.py --defects',result='PASS: command high lane, player alias, lost history/carried/motion stores, rebuilt cache, retained level fields, live post-stone state, collision read order and missed serialization controls detected',date='2026-11-15')]
 save(cpath,c);relock(final=True);save(OUT/'api-coverage.json',dict(result='PASS',entries=coverage,zero_scenario_entries=results['census']['unreached']))
 save(OUT/'verification-receipt.json',dict(result='PASS',status=c['status'],proposed_status='migrated',new_native_bytes=92,total_native_bytes=TOTAL,boundaries=sum(r['boundaries'] for r in runs),api_matches=total,compatibility_cases=compat,evidence={n:sha(OUT/(n+'.json')) for n in names},relocks=json.loads((OUT/'relocks.json').read_text())))

def main():
 p=argparse.ArgumentParser(description=__doc__);stages=['locks','inventory','router','proof','reuse','api-front','api-world','api-input','api-physics','borrowers','build','projector','census','levels','defects','finalize','gate','internal']
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
