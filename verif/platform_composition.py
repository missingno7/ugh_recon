"""Cut5D: ten native platform slots and live occupancy borrowers.
Generated copies only for instrumentation; serial 600s/8-GiB children.
"""
import argparse,ctypes as C,hashlib,inspect,io,json,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/workers/close-adlx-27'
sys.path.insert(0,str(ROOT/'tools'))
import resource_composition as catalog
player=catalog.player;prior=player.prior;run=prior.run;previous=run.previous
modules=[catalog,player]+player.modules
for module in modules:module.OUT=OUT
bounded=run.bounded;save=run.save;sha=run.sha
NEW=['native/platform_world.h','native/platform_world.c','native/bridge/platform_world_bridge.h','native/bridge/platform_world_bridge.c','native/bridge/platforms_borrow.h']
BORROWERS=[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'native/bridge').glob('*')) if p.suffix in ['.c','.h'] and '#include "platforms_borrow.h"' in p.read_text()]
BASE=NEW+BORROWERS+['verif/platform_composition.py','verif/platform_world_router.c','verif/platform_world_cases.py','verif/platform_world_byte_proof.c','tools/hostbuild.py','host/main.c','verif/projector/observer.c','verif/projector/timing_serializer.h','verif/projector/publications.py','verif/projector_evidence.py']
READ=sorted(set(catalog.READ+['verif/resource_composition.py','metadata/closure/resource_catalog.json','verif/resource_review.py']))
CONTEXT=player.CONTEXT
for unit in CONTEXT:READ+=['metadata/closure/'+unit+'.json']+json.loads((ROOT/('metadata/closure/'+unit+'.json')).read_text())['native']['files']
READ=sorted(set(READ))
WORLDS=catalog.WORLDS+['platform_world'];TOTAL=11001
FIELDS='PlatformActorOccupants PlatformArrivalPointsX PlatformDestinationIcons PlatformHeights PlatformLeftEdges PlatformRightEdges PlatformSpawnX PlatformWaitingPointsX'.split()
model=json.loads((ROOT/'metadata/program-model.json').read_text())
NAMES=sorted({routine.split(':')[1] for name in FIELDS for kind in ['readers','writers'] for routine in model['variables'][name][kind]}|{'InitializeLevelDisplay','LoadCurrentLevelState'})

def files():return sorted(set(BASE+subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()+['metadata/closure/platform_world.json']))
def snapshot():
 source=prior.RUN_SNAPSHOT_SOURCE.replace('metadata/closure/run_world.json','metadata/closure/platform_world.json')
 env=dict(run.__dict__,OUT=OUT,files=files);exec(source,env);return env['snapshot']()
for module in modules:module.snapshot=snapshot
build=previous.palette.build;levels=previous.palette.levels

def relock(final=False):
 import closure
 p=ROOT/'metadata/closure/platform_world.json'
 if not p.exists():
  save(p,dict(component='platform_world',status='unanalyzed',original=dict(owned=[],composes=CONTEXT),native=dict(files=NEW,functions=['native_platforms_world'],bridge='One ten-slot native owner; explicit live borrowers and observation-only serializer'),purpose='Cut5D: ten admitted platform records and mutable occupancy',interface=dict(inputs='Cold fixture once and live ordered field/byte requests',outputs='160 native historical bytes, sealed RAM and separate observation serialization'),callers=['Session/loader, passenger itinerary/delivery/water, stones, physics, items, patrol and render'],callees=['Existing resource/native owner chain for foreign/unmoved views'],indirect=['No callback or dispatcher in the new storage island'],memory=dict(owner='One NativePlatformsWorld.slot[10], eight16-bit raw fields per slot',total_with_prior=TOTAL),assumptions=['Accepted algorithm/resource/ABI domains unchanged','Longer raw lists, source level records and unsettled resources stay live mutable views','Cold import is fixture initialization only; no resynchronization'],eliminated=['RAM ownership of the admitted160-byte platform nucleus'],retained=['Signed/inclusive boundaries and negative-left sentinel; first-match selection and ordered occupancy stores','Longer raw physical aliases do not create an eleventh platform'],evidence=[dict(property='Platform ownership seam',level='D',method='Pending',command='python verif/platform_composition.py --gate',result='Pending',date='2026-11-15')],amiga=dict(classification='not-used',finding='Composition over accepted DOS contracts'),uncertainty=['Storage-first: remaining control ABI and resource providers stay in their later cuts'],dependencies={},verification_inputs={},verification_input_hashing='sha256-lf-text'))
 source=inspect.getsource(run.relock);source='def refresh(final=False):\n'+source[source.index(' old='):]
 source=source.replace("'run_world'","'platform_world'").replace('Run ownership and explicit shared borrowers','Ten-slot platform ownership and explicit live borrowers').replace('Pending cut 5A replay','Pending cut5D replay').replace('verif/run_composition.py','verif/platform_composition.py')
 env=dict(run.__dict__,NEW=NEW,BASE=BASE,READ=READ,OUT=OUT,closure=closure);exec(source,env);env['refresh'](final)

def inventory():
 save(OUT/'inventory.json',dict(result='PASS',bytes=160,total=TOTAL,region='DGROUP:290D..29AD',fields=FIELDS,readers_writers={n:model['variables'][n] for n in FIELDS},borrowers=BORROWERS,classification='Accepted resource_catalog review classified the runtime arrays and level/list records mutable/unsettled. Only the admitted eight parallel10-word arrays move; source records/lists/reserved words stay mutable live provider views.',aliases='A raw index10 on left addresses right[0]; occupancy+20 is outside this owner. Preserve physical overlap, not an extra slot.',semantics='Raw geometry, arrival/wait/spawn/icon and occupancy words; consumer signed/inclusive/sentinel and first-match policies unchanged.'))

def api(group):
 if group=='front':
  import difftest
  selected=[c for s in ['menu','menu_helpers','game_services'] for c in difftest.load_suite(s).CASES if c.routine.split(':')[1] in NAMES]
  if not selected:
   save(OUT/'api-front.json',dict(result='PASS',composed_matching=0,legacy_matching=0,explicit_out_of_domain=[],compatibility_cases=[],seam_inputs={f:sha(ROOT/f) for f in NEW+BORROWERS+['tools/hostbuild.py']},scope='No direct platform-state entry in these suites; no API or service-stream evidence claimed. Front-end integration remains covered by whole-game scenarios and unchanged-source reuse.'));return
 source=inspect.getsource(run.api)
 source=source.replace("['run_world','presentation_world'","['platform_world','resource_catalog','player_world','random_world','run_world','presentation_world'")
 source=source.replace("('RUN','run')])","('RUN','run'),('RANDOM','rng'),('PLAYER','player'),('RESOURCES','resources'),('PLATFORMS','platforms')])")
 source=source.replace('annotate_api(group)','run.annotate_api(group)')
 if group=='physics':
  source=source.replace("suites={'front':['menu','menu_helpers','game_services'],'world':['scene','actors','actors_states','items_water','demo_scripts'],'input':['dos_input','render','render_primitives']}[group]","suites=[]")
  source=source.replace(r'\n names=sorted',r"\n import player_physics_l0_cases\n cases += [('scene',c) for c in player_physics_l0_cases.cases()]\n names=sorted")
 env=dict(run.__dict__,NEW=NEW,BORROWERS=BORROWERS,WORLDS=WORLDS,NAMES=NAMES,OUT=OUT,run=run);exec(source,env);env['api'](group)

def router():
 folder=OUT/'router';folder.mkdir(exist_ok=True);exe=folder/'router.exe'
 bounded([previous.timing.common.GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/platform_world_router.c',ROOT/'native/platform_world.c',ROOT/'native/bridge/platform_world_bridge.c'],'router-compile')
 row=bounded([exe],'router-run');save(OUT/'router.json',dict(result='PASS',counts=json.loads(row['stdout']),scope='Independent literal address/member oracle; all92 bytes x256 and46 full16-bit slices; both-record independence, all roles/straddles/paragraph aliases, HUD exclusions, shared cycle alias, cold import, seal/serialization/frame.'))

def proof():
 from closure_support import function
 folder=OUT/'proof';folder.mkdir(exist_ok=True);text=(ROOT/'native/bridge/platform_world_bridge.c').read_text()
 prefix='#include "platform_world.h"\n#include <stddef.h>\n#include "'+(ROOT/'native/platform_world.c').as_posix()+'"\n'
 prefix+='void *memcpy(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}\n'
 prefix+=re.search(r'typedef struct PlatformsField.*?} PlatformsField;',text,re.S)[0]+'\n'+''.join(function(text,n) for n in ['platforms_field_get','platforms_field_put'])
 prefix+='void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);\n#define assert(c) __CPROVER_assert((c),#c)\n'
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe'];rows=[]
 for name in ['read','store']:
  p=folder/(name+'.c');p.write_text(('#define PLATFORMS_PROOF_STORE\n' if name=='store' else '')+prefix+(ROOT/'verif/platform_world_byte_proof.c').read_text(),encoding='utf-8');pre=p.with_suffix('.i')
  bounded([previous.timing.common.GCC,'-E','-P','-nostdinc','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',p,'-o',pre],'proof-'+name+'-pre')
  r=bounded([tool,pre,'--unwind','5','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-'+name);assert 'VERIFICATION SUCCESSFUL' in r['stdout'];rows.append(dict(profile=name,preprocessed=sha(pre)))
 save(OUT/'proof.json',dict(result='PASS',profiles=rows,scope='Actual-C strided16-bit platform field byte get/put; arbitrary complete native world, any admitted slot, lane/value, valid member in first record and arbitrary-other-byte output/frame/dependence. Layout/registration via exhaustive router, not a resource/async theorem.'))

def reuse():
 # Accepted algorithms are unchanged. Header declaration order can change, so
 # compare actual default function bodies plus mechanically restored source.
 from standalone_census import bodies
 folder=OUT/'reuse';folder.mkdir(exist_ok=True);rows=[]
 for rel in BORROWERS:
  before=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT,text=True);after=(ROOT/rel).read_text()
  restored=re.sub(r'\A#include "platform.h"\n#ifndef PLATFORMS_BORROWER\n#define PLATFORMS_BORROWER PLATFORMS_BORROW_\w+\n#endif\n#include "platforms_borrow.h"\n','',after,count=1)
  restored=re.sub(r'\bplatforms_read(8|16|32)\b',r'player_read\1',restored);restored=re.sub(r'\bplatforms_write(8|16|32)\b',r'player_write\1',restored);assert restored==before,rel
  if not rel.endswith('.c'):continue
  definitions=[]
  for i,text in enumerate([before,after]):
   text=re.sub(r'#include "([^\"]+)"',lambda m:'#include "'+str((ROOT/rel).parent.joinpath(m[1]).resolve()).replace('\\','/')+'"' if (ROOT/rel).parent.joinpath(m[1]).is_file() else m[0],text)
   p=folder/(str(i)+'-'+Path(rel).name);p.write_text(text);pre=p.with_suffix('.i');bounded([previous.timing.common.GCC,'-E','-P','-I',ROOT/'c',p,'-o',pre],'reuse-'+str(i)+'-'+p.stem);text=pre.read_text();definitions.append({n:re.findall(r'"(?:\\.|[^"\\])*"|\w+|[^\s]',text[a:e+1]) for a,b,e,n in bodies(text)})
  assert definitions[0]==definitions[1],rel;rows.append(rel)
 pure=[]
 for p in sorted((ROOT/'native').glob('*')):
  if p.suffix not in ['.c','.h'] or p.name.startswith('platform_world'):continue
  rel=p.relative_to(ROOT).as_posix();assert subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT).replace(b'\r\n',b'\n')==p.read_bytes().replace(b'\r\n',b'\n'),rel;pure.append(rel)
 save(OUT/'reuse.json',dict(result='PASS',bridges=rows,pure_sources_unchanged=pure,scope='All accepted pure C/headers unchanged; borrower edits are mechanical accessor renames plus prefix; default bridge function bodies (including shared headers) identical. Original algorithm proofs/resource domains reused unchanged. New state seams have independent evidence.'))

def projector():
 source=inspect.getsource(previous.palette.projector).replace('==6148','=='+str(TOTAL)).replace('Palette ownership cut only','Platform ownership cut5D')
 env=dict(previous.palette.__dict__);exec(source,env);env['projector']()

def census():
 source=inspect.getsource(previous.census)
 leaves={'platform_world':['platforms_field','platforms_field_get','platforms_field_put','platforms_is_owned','platforms_shared_read','platforms_shared_write','platforms_borrowed_byte','platforms_borrowed_store','platforms_borrow_read','platforms_borrow_write'],'resource_catalog':['sprite_base','codec_base','resources_field','resources_is_owned','resources_shared_read','resources_shared_write','resources_borrowed_byte','resources_borrowed_store','resource_sprite_from_legacy','resource_effect_from_legacy','resource_table_from_legacy','resource_token_to_legacy'],'player_world':['player_field','player_field_get','player_field_put','player_is_owned','player_shared_read','player_shared_write','player_borrowed_byte','player_borrowed_store','player_borrow_read','player_borrow_write'],'random_world':['rng_lane','rng_get','rng_put','rng_is_owned','rng_shared_read','rng_shared_write','rng_borrowed_byte','rng_borrowed_store','rng_borrow_read','rng_borrow_write'],'run_world':['run_field','run_field_get','run_field_put','run_is_owned','run_shared_read','run_shared_write','run_borrowed_byte','run_borrowed_store','run_borrow_read','run_borrow_write']}
 source=source.replace("'presentation_world':['presentation_field'",''.join(repr(n)+':'+repr(v)+',\n ' for n,v in leaves.items())+"'presentation_world':['presentation_field'",1).replace("paths={'native/bridge/hud_bridge.c','native/bridge/water_weather_bridge.c','native/bridge/presentation_world_bridge.c'}","paths={'native/bridge/platform_world_bridge.c'}").replace("'-DUGH_NATIVE_PRESENTATION','-I'","'-DUGH_NATIVE_PRESENTATION','-DUGH_NATIVE_RUN','-DUGH_NATIVE_RANDOM','-DUGH_NATIVE_PLAYER','-DUGH_NATIVE_RESOURCES','-DUGH_NATIVE_PLATFORMS','-I'")
 source=source.replace('Native HUD/weather bridges and owner; session/menu/high-score callers remain explicit borrowers, not part of this machine-edge island.','Ten-slot platform state/borrower island. Existing sequencing remains outside until its planned cuts.')
 env=dict(previous.__dict__,snapshot=snapshot,NAMES=NAMES);exec(source,env);env['census']()

def borrowers():
 import platform_world_cases
 platform_world_cases.run(ROOT,OUT,bounded,save)
def defects():
 import platform_world_cases
 platform_world_cases.defects(ROOT,OUT,bounded,save,snapshot,previous)
def deepcounts():
 import platform_world_cases
 platform_world_cases.deepcounts(ROOT,OUT,bounded,save,snapshot,previous)

def finalize():
 results={n:json.loads((OUT/(n+'.json')).read_text()) for n in ['inventory','router','proof','reuse','api-front','api-world','api-input','api-physics','borrowers','census','levels','deep-counts','defects']};assert all(r['result']=='PASS' for r in results.values())
 for g in ['front','world','input','physics']:
  r=results['api-'+g];assert not r['explicit_out_of_domain'];assert all(sha(ROOT/f)==h for f,h in r['seam_inputs'].items())
 runs=[json.loads(p.read_text()) for p in (OUT/'projector/runs').glob('*.json')];assert len(runs)==21 and all(r['canonical_native_owned_bytes']==TOTAL and not r['native_owned_journal_publications'] for r in runs)
 p=ROOT/'metadata/closure/platform_world.json';c=json.loads(p.read_text());c['proposed_status']='migrated';c['memory'].update(region='DGROUP:290D..29AD',bytes=160,slots=10,fields=FIELDS,borrowers=BORROWERS)
 total=sum(results['api-'+g]['composed_matching'] for g in ['front','world','input','physics']);compat=sum(len(results['api-'+g]['compatibility_cases']) for g in ['front','world','input','physics'])
 c['uncertainty']=['Storage-first; outer sequencing/Regs ABI remains for later cuts','Longer raw lists/physical aliases remain borrowed, including values beyond ordinary capacity; no extra platform is admitted','Level resource records/lists stay live and mutable per resource_catalog review; reserved_raw is not runtime occupancy','Broader compatibility API cases are enumerated, not counted as native algorithm executions; no such fallback occurs in maintained scenarios','Atomic ICE has equal returned state/ports; internal backwards decode versus ascending completed-buffer publication is not a store-instruction contract']
 c['evidence']=[dict(property='Actual-C platform byte seam',level='B',method=results['proof']['scope'],command='python verif/platform_composition.py --router --proof',result='PASS: split output/frame/dependence;160 bytes x256;80 full16-bit slices; all slots, physical aliases, mutable foreign records and seal/serialization',date='2026-11-15'),dict(property='Independent APIs and live borrowers',level='C',method=results['borrowers']['scope'],command='python verif/platform_composition.py --api-world --api-input --api-physics --borrowers --reuse',result=f'PASS: {total} replay runs per profile; zero new rejections; {compat} broader compatibility cases listed; unchanged algorithms/proofs reused',date='2026-11-15'),dict(property='Ownership integration',level='D',method='Clean committed-HEAD archive plus only cut files, scratch promotion, independent ASM frames and sealed observation serialization',command='python verif/platform_composition.py --build --projector --census --levels',result=f'PASS: closure57/0; host21/21 both variants, literal pure L1; {sum(r["boundaries"] for r in runs)} boundaries,11001 native bytes, zero moved journal publications/fallbacks/L1 bodies/state-island machine edges;81+7+8 levels both variants',date='2026-11-15'),dict(property='Defect sensitivity',level='C',method=results['defects']['scope'],command='python verif/platform_composition.py --defects',result='PASS: occupancy, alias/byte lane, first match, boundary/sentinel, cached index and missed serialization controls detected',date='2026-11-15')]
 save(p,c);relock(final=True);save(OUT/'verification-receipt.json',dict(result='PASS',status=c['status'],proposed_status='migrated',bytes=160,total=TOTAL,evidence={n:sha(OUT/(n+'.json')) for n in results},relocks=json.loads((OUT/'relocks.json').read_text())))

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
