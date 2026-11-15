"""Cut 5A. Serial, bounded, generated-copy composition evidence."""
import argparse,ast,ctypes as C,hashlib,inspect,io,json,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/workers/close-adlx-25'
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

def relock(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'relock',locals())

def api(group=None,*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'api',locals())

def projector(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'projector',locals())

def census(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'census',locals())

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

def finalize(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'finalize',locals())

def main(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'main',locals())
# Scheduled by world_gate; no private CLI.
