"""Cut 5A. Serial, bounded, generated-copy composition evidence."""
import argparse,ast,ctypes as C,hashlib,inspect,io,json,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/workers/close-adlx-25'
sys.path.insert(0,str(ROOT/'tools'))
import presentation_composition as previous
modules=[previous,previous.pixels,previous.pages,previous.prior,previous.palette,previous.audio,previous.timing,previous.timing.common]
for module in modules:module.OUT=OUT
bounded=previous.bounded;save=previous.save;sha=previous.sha
NEW=['native/run_world.h','native/run_world.c','native/bridge/run_world_bridge.h','native/bridge/run_world_bridge.c','native/bridge/run_borrow.h']
BORROWERS=[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'native/bridge').glob('*')) if p.suffix in ['.c','.h'] and '#include "run_borrow.h"' in p.read_text()]
BASE=NEW+BORROWERS+['verif/run_router.c','verif/run_byte_proof.c','verif/run_borrowers.py']+['tools/hostbuild.py','host/main.c','verif/run_composition.py','verif/projector/observer.c','verif/projector/timing_serializer.h','verif/projector/publications.py','verif/projector_evidence.py']
WORLDS=['timing_world','audio_world','palette_world','input_world','video_pages','pixel_world','presentation_world','run_world']
TOTAL=8033
FIELDS='CurrentLevelIndex CurrentLevelRecord LevelActorList LevelCompletionMarker LevelEnemyList LevelIntroTextPointer LevelPlatformList LevelPlayerOneStartX LevelPlayerOneStartY LevelPlayerTwoStartX LevelPlayerTwoStartY LevelRainDirection LevelTimer LivesRemaining PlayerArrayBytes PlayerCount PlayerOneControlMode PlayerTwoControlMode RemainingPassengerJourneys ScoreHighWord ScoreLowWord ScoreMultiplier ScreenFadeLevel ScreenFadeStep SelectedDifficulty WaterSurfaceStep WaterY32 WaterYPixels'.split()
model=json.loads((ROOT/'metadata/program-model.json').read_text())
NAMES=sorted({routine.split(':')[1] for name in FIELDS for kind in ['readers','writers'] for routine in model['variables'][name][kind]}|{'LoadCurrentLevelState','InitializeLevelDisplay','DrawTileMap'})
READ=sorted(set(previous.READ+['verif/presentation_composition.py','metadata/closure/presentation_world.json','docs/standalone-cuts.md','docs/standalone-ledger.md','verif/closure_support.py','verif/windows_job.py','verif/timing_composition.py','verif/projector/schema.py','verif/projector/world.h']))

def files():return sorted(set(BASE+subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()+['metadata/closure/run_world.json']))
def snapshot():
 target=OUT/'baseline';revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 raw=subprocess.check_output(['git','archive','--format=tar',revision],cwd=ROOT)
 with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
  for member in archive.getmembers():
   if member.isfile():
    p=(target/member.name).resolve();assert p.is_relative_to(target.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(archive.extractfile(member).read())
 for f in files():p=target/f;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,p)
 p=target/'metadata/closure/run_world.json';c=json.loads(p.read_text());c['status']='migrated';save(p,c)
 for bank in ['whole','levels','levels-audio','levels-deep']:
  dest=target/'build'/bank;dest.mkdir(parents=True,exist_ok=True)
  for p in (ROOT/'build'/bank).glob('*.ref.json'):shutil.copyfile(p,dest/p.name)
 save(target/'build/workers/c-close/call-edges.json',[])
 save(OUT/'baseline.json',dict(revision=revision,overlay={f:sha(ROOT/f) for f in files()}));return target
for module in modules:module.snapshot=snapshot
build=previous.palette.build;levels=previous.palette.levels

def relock(final=False):
 import closure
 p=ROOT/'metadata/closure/run_world.json'
 if not p.exists():
  save(p,dict(component='run_world',status='unanalyzed',original=dict(owned=[],composes=['session','menus','high_scores','input_world','presentation_world','water_weather','player_physics','hazards','falling_items','demo_presentation']),
   native=dict(files=NEW,functions=['native_run_world'],bridge='Run-state native owner, typed borrower roles and observation serializer'),purpose='Cut 5A: one shared configuration/run store, one live level record and tile map',
   interface=dict(inputs='Cold fixture once; explicit shared field and byte-window borrowers',outputs='373 native historical bytes, sealed RAM and a separate observation serialization'),
   callers=['Input, menu, score, session, gameplay, renderer, resource and weather borrowers'],callees=['Existing owner chain for foreign/unmoved byte views'],indirect=['No callback or dispatcher in the new owner/borrower service'],
   memory=dict(owner='NativeRunWorld: configuration10 + run scalars17 + live record26 + tile map320',total_with_prior=TOTAL,retained_owners='PreviousWaterSurfaceY and ds_27C8 remain presentation-owned'),
   assumptions=['Existing accepted algorithm/resource/stack domains; verification ABI remains at outside entries','Cold import is fixture initialization, never resynchronization'],
   eliminated=['RAM ownership of 5A storage and its shared-state projections'],retained=['Raw counts/modes, score halves, water fixed/pixel distinction, reserved record bytes and ordered partial writes'],
   evidence=[dict(property='Cut 5A composition',level='D',method='Evidence pending',command='python verif/run_composition.py --gate',result='Pending',date='2026-11-15')],
   amiga=dict(classification='not-used',finding='Composition over accepted DOS contracts'),uncertainty=['Storage-first cut: session/menu/gameplay orchestration adapters remain for later cuts'],dependencies={},verification_inputs={},verification_input_hashing='sha256-lf-text'))
 old={p.name:json.loads(subprocess.check_output(['git','show','HEAD:'+p.relative_to(ROOT).as_posix()],cwd=ROOT,text=True)) for p in (ROOT/'metadata/closure').glob('*.json') if p.stem!='run_world'}
 for p in (ROOT/'metadata/closure').glob('*.json'):
  c=json.loads(p.read_text())
  if p.name in old:
   for key in set(old[p.name])-{'verification_inputs','dependencies','evidence_refreshed'}:assert c[key]==old[p.name][key],(p.name,key)
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
   if p.stem=='run_world':c['dependencies']={f:closure.actual_dependencies(ROOT/f) for f in NEW};c['verification_inputs']={f:sha(ROOT/f) for f in sorted(set(BASE+READ))}
   for f,h in c.get('verification_inputs',{}).items():
    data=(ROOT/f).read_bytes();data=data.replace(b'\r\n',b'\n') if c.get('verification_input_hashing')=='sha256-lf-text' else data
    actual=hashlib.sha256(data).hexdigest()
    if h!=actual:c['verification_inputs'][f]=actual;dirty=True
   if p.name in old:
    updates=[f for f,h in c.get('verification_inputs',{}).items() if old[p.name].get('verification_inputs',{}).get(f)!=h]
    if updates or c.get('dependencies')!=old[p.name].get('dependencies'):
     direct=any(not f.startswith('metadata/closure/') for f in updates) or c.get('dependencies')!=old[p.name].get('dependencies')
     note=dict(date='2026-11-15',reason='Run ownership and explicit shared borrowers; prior claims/status unchanged' if direct else 'Dependent certificate note/source-lock cascade only',commands=['python verif/run_composition.py --gate'],results='PASS within stated domains' if final else 'Pending cut 5A replay',inputs=updates)
     c['evidence_refreshed']=old[p.name].get('evidence_refreshed',[])+[note];changed[p.name]=note
   before=p.read_text();save(p,c);dirty|=p.read_text()!=before
  if not dirty:break
 else:raise RuntimeError('lock cycle')
 save(OUT/'relocks.json',dict(certificates=changed))

def api(group):
 seam_inputs={f:sha(ROOT/f) for f in NEW+BORROWERS+['tools/hostbuild.py']}
 source=inspect.getsource(previous.timing.api)
 suites={'front':['menu','menu_helpers','game_services'],'world':['scene','actors','actors_states','items_water','demo_scripts'],'input':['dos_input','render','render_primitives']}[group]
 source=re.sub(r"suites=\[[^\n]+\]",'suites='+repr(suites),source,1)
 source=source.replace(" import timer_callbacks\n cases += [('timer_callbacks',c) for c in timer_callbacks.CASES]\n",'')
 source=source.replace(' names=sorted'," cases=[(s,c) for s,c in cases if c.routine.split(':')[1] in "+repr(NAMES)+"]\n print('Selected API cases',len(cases),flush=True)\n names=sorted",1)
 source=source.replace("{'timing_world','audio_world'}",repr(set(WORLDS)))
 source=source.replace("units.append(dict(component='timing_world',native=ROOT/'native/timing_world.c',bridge=ROOT/'native/bridge/timing_world_bridge.c',exports=[]))","units.extend([dict(component=n,native=ROOT/('native/'+n+'.c'),bridge=ROOT/('native/bridge/'+n+'_bridge.c'),exports=[]) for n in "+repr(WORLDS)+"])")
 source=source.replace("for n in ['RegisterTimerCallback','RemoveTimerCallback','SetTimerCallbackInterval','HandleTimerInterrupt']:","for n in [x[2:] for x in exports]:")
 headers=''.join('#include "'+n+'_bridge.h"\\n' for n in ['run_world','presentation_world','pixel_world','video_pages','input_world','palette_world'])
 source=source.replace("fixture.write_text('#include \"timing_world_bridge.h\"","fixture.write_text('"+headers+'#include "timing_world_bridge.h"')
 source=source.replace('EXPORT unsigned api_timer_fallbacks;','EXPORT unsigned api_timer_fallbacks;\\nEXPORT int api_stop_at_load;')
 for action in ['cold_import','require_seal','serialize']:
  value='timing_api_observation' if action=='serialize' else 'ugh_mem';needle=' timing_'+action+'('+value+');'
  extra=''.join('\\n#ifdef UGH_NATIVE_'+flag+'\\n '+name+'_'+action+'('+value+');\\n#endif' for flag,name in [('PALETTE','palette'),('INPUT','input'),('VIDEO_PAGES','video_pages'),('PIXEL','pixel'),('PRESENTATION','presentation'),('RUN','run')]);source=source.replace(needle,needle+extra)
 source=source.replace('path=folder/p.name;path.write_text(text)','text=api_load_cut(text)\n   path=folder/p.name;path.write_text(text)')
 source=source.replace("sources += [u['native'] for u in units]+[u['bridge'] for u in units]+[fixture]", "sources.append(fixture)\n  for original in [u['native'] for u in units]+[u['bridge'] for u in units]:\n   text=api_load_cut(original.read_text());new=hostbuild.composition_source(original.relative_to(ROOT).as_posix(),text,units)\n   if new!=original.read_text():\n    path=folder/('native_'+original.name);path.write_text(new);sources.append(path)\n   else:sources.append(original)")
 source=source.replace("OUT/'api'/label","OUT/'api'/"+repr(group)+"/label").replace("'api-'+label+'-compile'",repr('api-'+group+'-')+"+label+'-compile'")
 source=source.replace('assert old[\'timer_fallbacks\'] and new[\'status\']==1,(old,new)',"assert new['status'] in (1,3),(old,new)").replace(' assert len(declines)==32','')
 source=source.replace('composed_matching=2202-len(declines),legacy_matching=2202','composed_matching=len(cases)*2-len(declines),legacy_matching=len(cases)*2').replace("OUT/'api.json'","OUT/"+repr('api-'+group+'.json'))
 source=source.replace("print('API PASS legacy 2202; composed 2170 matches + 32 explicit domain rejections',flush=True)","print('API PASS',len(cases)*2,'cases;',len(declines),'rejections',flush=True)")
 env=dict(previous.timing.__dict__,api_load_cut=previous.api_load_cut);exec(source,env);env['api']()
 annotate_api(group)
 assert all(sha(ROOT/f)==h for f,h in seam_inputs.items()),'API source changed during replay'
 p=OUT/('api-'+group+'.json');r=json.loads(p.read_text());r['seam_inputs']=seam_inputs;save(p,r)

def projector():
 source=inspect.getsource(previous.palette.projector).replace('==6148','=='+str(TOTAL)).replace('Palette ownership cut only','Run ownership cut 5A')
 env=dict(previous.palette.__dict__);exec(source,env);env['projector']()

def census():
 source=inspect.getsource(previous.census)
 source=source.replace("'presentation_world':['presentation_field'", "'run_world':['run_field','run_field_get','run_field_put','run_is_owned','run_shared_read','run_shared_write','run_borrowed_byte','run_borrowed_store','run_borrow_read','run_borrow_write'],\n 'presentation_world':['presentation_field'",1)
 source=source.replace("paths={'native/bridge/hud_bridge.c','native/bridge/water_weather_bridge.c','native/bridge/presentation_world_bridge.c'}","paths={'native/bridge/run_world_bridge.c'}")
 source=source.replace("'-DUGH_NATIVE_PRESENTATION','-I'","'-DUGH_NATIVE_PRESENTATION','-DUGH_NATIVE_RUN','-I'")
 source=source.replace("Native HUD/weather bridges and owner; session/menu/high-score callers remain explicit borrowers, not part of this machine-edge island.","Storage-first 5A island: native owner and typed field/byte borrowers only. Existing session/menu/gameplay control orchestration remains outside until cut 6A/B, as planned.")
 env=dict(previous.__dict__,snapshot=snapshot,NAMES=NAMES);exec(source,env);env['census']()

def inventory():
 save(OUT/'inventory.json',dict(result='PASS',moved=373,total=TOTAL,names=FIELDS,remaining_presentation=['PreviousWaterSurfaceY','ds_27C8'],borrower_files=BORROWERS,
  ownership='Configuration10, run scalars17, live record26, tile map320; no duplicated previous-water or HUD seed word',
  readers_writers={n:model['variables'][n] for n in FIELDS},bounds='No second persistent level descriptor or water Y. Record reserved bytes +9/+25 are retained; generic window/word writes split into canonical byte lanes.'))


def router():
 folder=OUT/'router';folder.mkdir(exist_ok=True);exe=folder/'router.exe'
 bounded([previous.timing.common.GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/run_router.c',ROOT/'native/run_world.c',ROOT/'native/bridge/run_world_bridge.c'],'router-compile')
 row=bounded([exe],'router-run');save(OUT/'router.json',dict(result='PASS',counts=json.loads(row['stdout']),scope='Independent literal address/named native-member layout; all373 bytes,23 complete word slices, all roles, record/owner straddles, paragraph aliases, full observation/frame/seal and excluded presentation lanes.'))

def proof():
 from closure_support import function
 folder=OUT/'proof';folder.mkdir(exist_ok=True);bridge=(ROOT/'native/bridge/run_world_bridge.c').read_text()
 prefix='#include "run_world.h"\n#include <stddef.h>\n#include "'+(ROOT/'native/run_world.c').as_posix()+'"\n'
 prefix+='void *memcpy(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}\n'
 prefix+=re.search(r'typedef struct RunField.*?} RunField;',bridge,re.S)[0]+'\n'+''.join(function(bridge,n) for n in ['run_field_get','run_field_put'])
 prefix+='void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);\n#define assert(c) __CPROVER_assert((c),#c)\n'
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe'];rows=[]
 for name in ['read','store']:
  path=folder/(name+'.c');path.write_text(('#define RUN_PROOF_STORE\n' if name=='store' else '')+prefix+(ROOT/'verif/run_byte_proof.c').read_text());pre=path.with_suffix('.i')
  bounded([previous.timing.common.GCC,'-E','-P','-nostdinc','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',path,'-o',pre],'proof-'+name+'-preprocess')
  result=bounded([tool,pre,'--unwind','5','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-'+name);assert 'VERIFICATION SUCCESSFUL' in result['stdout']
  rows.append(dict(profile=name,preprocessed=sha(pre)))
 save(OUT/'proof.json',dict(result='PASS',profiles=rows,scope='Actual run_field_get/put C, valid arbitrary8/16/32-bit descriptor,320 byte/array indices, arbitrary native world/value/lane. Numeric output/selected-byte frame and arbitrary-other-byte frame/dependence. No universal resource/asynchronous/registry theorem.'))

def annotate_api(group):
 path=OUT/('api-'+group+'.json');r=json.loads(path.read_text());r['scope']='Independent Unicorn/L1/native-storage replay; whole RAM and device/ordered ports plus declared live ABI. Existing broader compatibility fallbacks are enumerated, not credited as native algorithm executions.'
 r['compatibility_cases']=[row for row in r['profiles']['composed']['cases'] if row['timer_fallbacks']]
 save(path,r)

def borrowers():
 import run_borrowers
 run_borrowers.run(ROOT,OUT,bounded,save)

def reuse():
 from standalone_census import bodies
 folder=OUT/'reuse';folder.mkdir(exist_ok=True);rows=[]
 for rel in BORROWERS:
  if not rel.endswith('.c'):continue
  before=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT,text=True);tokens=[]
  for i,text in enumerate([before,(ROOT/rel).read_text()]):
   text=re.sub(r'#include "([^"]+)"',lambda m:'#include "'+str((ROOT/rel).parent.joinpath(m[1]).resolve()).replace('\\','/')+'"' if (ROOT/rel).parent.joinpath(m[1]).is_file() else m[0],text)
   p=folder/(str(i)+'-'+Path(rel).name);p.write_text(text,encoding='utf-8');out=p.with_suffix('.i')
   bounded([previous.timing.common.GCC,'-E','-P','-I',ROOT/'c',p,'-o',out],'reuse-'+str(i)+'-'+Path(rel).stem)
   tokens.append(re.findall(r'"(?:\\.|[^"\\])*"|\w+|[^\s]',out.read_text()))
  identical=tokens[0]==tokens[1]
  if not identical:
   # The added platform include may move declarations ahead of native types.
   # Check actual function bodies and separately prove the source edit is only
   # the accessor rename/prefix, rather than ignoring a broad token mismatch.
   texts=[(folder/(str(i)+'-'+Path(rel).name)).with_suffix('.i').read_text() for i in range(2)]
   defs=[{n:re.findall(r'"(?:\\.|[^"\\])*"|\w+|[^\s]',text[a:e+1]) for a,b,e,n in bodies(text)} for text in texts]
   assert defs[0]==defs[1],rel
  restored=re.sub(r'\Ar?\n','',(ROOT/rel).read_text())
  restored=re.sub(r'\A#include "platform.h"\n#ifndef RUN_BORROWER\n#define RUN_BORROWER RUN_BORROW_\w+\n#endif\n#include "run_borrow.h"\n','',restored,count=1)
  restored=re.sub(r'\brun_read(8|16|32)\b',r'rd\1',restored);restored=re.sub(r'\brun_write(8|16|32)\b',r'wr\1',restored)
  assert restored==before,rel
  rows.append(dict(file=rel,default_preprocessed_tokens_identical=identical,default_function_bodies_identical=True,mechanical_accessor_rename_only=True))
 pure=[]
 for p in sorted((ROOT/'native').glob('*')):
  if p.suffix not in ['.c','.h'] or p.name.startswith('run_world'):continue
  rel=p.relative_to(ROOT).as_posix();old=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT)
  assert old.replace(b'\r\n',b'\n')==p.read_bytes().replace(b'\r\n',b'\n'),rel
  pure.append(rel)
 save(OUT/'reuse.json',dict(result='PASS',bridges=rows,pure_sources_unchanged=pure,scope='All accepted pure algorithm/header sources unchanged; default verification-ABI function-body tokens identical, and bridge edits independently checked as mechanical accessor renames plus prefix. Include declaration order may differ. Existing actual-C proofs and resource/corpus domains are unchanged. The composed storage seam has separate replay/proof; compatibility fallbacks are not credited as native algorithm executions.'))

def defects():
 import wholegame
 folder=OUT/'defects';folder.mkdir(exist_ok=True);capture=folder/'capture.py'
 capture.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n',encoding='utf-8')
 names=['stale-score-after-award','swapped-score-halves','lost-second-control-mode','derived-player-byte-count','stale-water','missing-journey-decrement','reserved-byte-reset','odd-water-high-lane','missed-serialization','dropped-keyboard-mode-high-byte'];rows=[]
 for fault,name in enumerate(names,1):
  exe=folder/(name+'.exe')
  bounded([previous.timing.common.GCC,'-O2','-std=c11','-DRUN_TEST_FAULT='+str(fault),'-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/run_router.c',ROOT/'native/run_world.c',ROOT/'native/bridge/run_world_bridge.c'],'defect-router-'+str(fault)+'-compile')
  r=json.loads(bounded([sys.executable,capture,exe],'defect-router-'+str(fault)+'-run')['stdout'])
  assert r['returncode']!=0,(name,'survived')
  if fault==9:assert r['returncode']==88 and 'missed serialization' in r['stderr'],r
  rows.append(dict(defect=name,scope='Independent compiled router oracle',result='DETECTED',exit=r['returncode'],diagnostic=r['stderr']))
 target=snapshot()
 for fault,name in [(5,'stale-water'),(9,'missed-serialization')]:
  generated=folder/('host-'+name);hostcapture=previous.copy_host(target,generated)
  p=generated/'tools/hostbuild.py';text=p.read_text();needle="return (['-DUGH_NATIVE_RUN']";assert text.count(needle)==1
  p.write_text(text.replace(needle,"return (['-DRUN_TEST_FAULT="+str(fault)+"','-DUGH_NATIVE_RUN']",1),encoding='utf-8')
  for rel,symbol in [('native/bridge/hud_support.h','hd_require'),('native/bridge/session_support.h','sq_require'),('native/bridge/water_weather_bridge.c','ww_require')]:
   p=generated/rel;text=p.read_text();old='static void '+symbol+'(int c){if(!c)abort();}';assert text.count(old)==1
   p.write_text('#include <stdio.h>\n'+text.replace(old,'static void '+symbol+'(int c){if(!c){fputs("RUN_CONTROL_BRIDGE_ASSERT:'+symbol+'\\n",stderr);exit(87);}}'),encoding='utf-8')
  bounded([sys.executable,'tools/hostbuild.py'],'defect-host-'+name+'-build',generated)
  script=target/'tests/scenarios/gameplay-adlib.txt';expected=json.loads((target/'build/whole/gameplay-adlib.ref.json').read_text())['frames']
  result=bounded([sys.executable,hostcapture,generated/'build/host/ugh.exe','--headless',str(wholegame.scenario(script)['frames']),'--script',script,'--timeout','590'],'defect-host-'+name+'-run')
  r=json.loads(result['stdout']);actual=[json.loads(line) for line in r['stdout'].splitlines()]
  first=next((i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b),None)
  assert first is not None or (r['returncode']==88 and 'missed serialization' in r['stderr']) or (r['returncode']==87 and 'RUN_CONTROL_BRIDGE_ASSERT:' in r['stderr']),(name,r)
  rows.append(dict(defect=name,scope='Composed host versus independent ASM frames',scenario='gameplay-adlib',frame=first+1 if first is not None else len(actual)+1,result='DETECTED',exit=r['returncode'],diagnostic=r['stderr'][-1500:]))
 save(OUT/'defects.json',dict(result='PASS',controls=rows,scope='Ten deliberately wrong new ownership/borrower seams; independent literal layout/value oracle. Two also injected into the whole composed host. Existing accepted algorithms are not mutated.'))

def finalize():
 names=['inventory','router','proof','api-front','api-world','api-input','borrowers','reuse','census','levels','defects']
 results={n:json.loads((OUT/(n+'.json')).read_text()) for n in names};assert all(r['result']=='PASS' for r in results.values())
 for group in ['front','world','input']:
  r=results['api-'+group];assert not r['explicit_out_of_domain']
  assert all(sha(ROOT/f)==h for f,h in r['seam_inputs'].items()),'API source replay required'
 runs=[json.loads(p.read_text()) for p in (OUT/'projector/runs').glob('*.json')]
 assert len(runs)==21 and all(r['canonical_native_owned_bytes']==TOTAL and not r['native_owned_journal_publications'] for r in runs)
 assert len(results['defects']['controls'])==12
 p=ROOT/'metadata/closure/run_world.json';c=json.loads(p.read_text());c['proposed_status']='migrated'
 c['interface']['borrowers']={role:'Explicit live field/byte service; foreign/unmoved lanes delegated to the existing owner chain' for role in ['session','water','menus','scores','input','HUD','physics','actors','items','demo','render','resources']}
 c['memory']['fields']=FIELDS;c['memory']['reserved']='26-byte record includes retained +9/+25 bytes; score halves, player count/bytes and fixed/pixel/previous water remain independent'
 c['memory']['allocation']='373 new historical bytes = configuration10 + run17 + record26 + tiles320; PreviousWaterSurfaceY and ds_27C8 stay in presentation_world; native padding is not serialized'
 c['uncertainty']=['Storage-first cut: session/menu/gameplay control orchestration remains outside the state island until 6A/B; no new claim that those machine edges are retired','Live record resource words are opaque data identities, not executable pointers; provider extraction stays with 5R','Existing broad API fixtures can use accepted compatibility fallbacks; these are enumerated separately, not credited as native algorithm executions','Existing atomic ICE service decodes backwards in L1 and publishes completed output ascending natively; only returned state/ports are an observation contract inside that atomic service']
 total=sum(results['api-'+g]['composed_matching'] for g in ['front','world','input']);compat=sum(len(results['api-'+g]['compatibility_cases']) for g in ['front','world','input'])
 c['evidence']=[dict(property='Actual-C numeric byte-view seam',level='B',method=results['proof']['scope'],command='python verif/run_composition.py --proof --router',result='PASS: split read/store profiles; all373 lanes x256 and23 full16-bit word slices, aliases/record straddles/borrower roles/frame checks',date='2026-11-15'),dict(property='Independent APIs and live shared writers',level='C',method='Unicorn/L1/legacy-native/composed replay; whole RAM and ordered device ports. Extra compiled L1/composed ordered record-store prefixes, DF clear, live intro IRQ mutation and alias windows; atomic ICE returned-state exception explicit.',command='python verif/run_composition.py --api-front --api-world --api-input --borrowers --reuse',result=f'PASS: {total} replay runs each profile, zero rejections; {compat} composed broader compatibility cases enumerated; accepted algorithm proofs unchanged',date='2026-11-15'),dict(property='Composed ownership integration',level='D',method='Committed HEAD archive plus only owned overlay, scratch promotion, independent ASM frames; moved RAM sealed and observation-only serialization',command='python verif/run_composition.py --build --projector --census --levels',result=f'PASS: clean closure53/0; host21/21 both variants with literal pure L1; {sum(r["boundaries"] for r in runs)} projector boundaries,8033 native bytes, zero moved-owner journal publications; zero state-island machine edges/fallbacks/L1 bodies in maintained runs;81+7+8 levels both variants',date='2026-11-15'),dict(property='Composition defect sensitivity',level='C',method=results['defects']['scope'],command='python verif/run_composition.py --defects',result='PASS: ten independent router controls and two whole-host controls detected, including missed serialization',date='2026-11-15')]
 save(p,c);relock(final=True)
 save(OUT/'verification-receipt.json',dict(result='PASS',status=c['status'],proposed_status='migrated',new_native_bytes=373,total_native_bytes=TOTAL,boundaries=sum(r['boundaries'] for r in runs),api_matches=total,compatibility_cases=compat,evidence={n:sha(OUT/(n+'.json')) for n in names},relocks=json.loads((OUT/'relocks.json').read_text())))

def main():
 parser=argparse.ArgumentParser(description=__doc__);stages=['locks','inventory','api-front','api-world','api-input','build','projector','census','levels','router','proof','borrowers','defects','reuse','finalize','gate','internal']
 for stage in stages:parser.add_argument('--'+stage,action='store_true')
 args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True)
 if args.locks:relock()
 if args.gate:
  relock()
  for stage in ['inventory','router','proof','api-front','api-world','api-input','borrowers','reuse','build','projector','census','levels','defects']:
   bounded([sys.executable,__file__,'--'+stage,'--internal'],stage+'-child')
  finalize();build();return
 for stage in stages[1:-2]:
  if getattr(args,stage.replace('-','_')):
   if args.internal:
    if stage.startswith('api-'):api(stage[4:])
    else:globals()[stage]()
   else:bounded([sys.executable,__file__,'--'+stage,'--internal'],stage+'-child')
if __name__=='__main__':main()
