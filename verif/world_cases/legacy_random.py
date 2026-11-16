"""Cut 5B: single native random-state owner; serial 600s/8-GiB replay."""
import argparse,ctypes as C,hashlib,inspect,io,json,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/workers/close-stones-23'
sys.path.insert(0,str(ROOT/'tools'))
import run_composition as run
RUN_SNAPSHOT_SOURCE=inspect.getsource(run.snapshot)
previous=run.previous
modules=[run]+run.modules
for module in modules:module.OUT=OUT
bounded=run.bounded;save=run.save;sha=run.sha
NEW=['native/random_world.h','native/random_world.c','native/bridge/random_world_bridge.h','native/bridge/random_world_bridge.c','native/bridge/random_borrow.h']
BORROWERS=['native/bridge/random_bridge.c']
BASE=NEW+BORROWERS+['verif/random_composition.py','verif/random_world_router.c','verif/random_world_cases.py','tools/hostbuild.py','host/main.c','verif/projector/observer.c','verif/projector/timing_serializer.h','verif/projector/publications.py','verif/projector_evidence.py']
READ=sorted(set(run.READ+['verif/run_composition.py','metadata/closure/run_world.json','native/random.c','native/random.h','metadata/closure/random.json','c/dos_input.c','verif/random_evidence.py','verif/random_cbmc.c','verif/random_enumeration.c','verif/random_cases.py','native/bridge/lifecycle_bridge.c','native/bridge/pixel_world_bridge.c','native/bridge/water_weather_bridge.c']))
WORLDS=run.WORLDS+['random_world'];TOTAL=8041
FIELDS=['RandomSecondsSeedByte','RandomStateStorage','RandomStateWord0','RandomStateWord1','RandomStateWord2','RandomStateWord3']
NAMES=['NextRandomBelowAx','SeedRandomFromDosSeconds','RespawnRainParticle','AdvanceRainParticles','DrawRainParticles','RestoreRainBackground','LoadCurrentLevelState','InitializeDosVideoInputAndSound']

def files():return sorted(set(BASE+subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()+['metadata/closure/random_world.json']))

def snapshot():
 source=RUN_SNAPSHOT_SOURCE.replace("metadata/closure/run_world.json","metadata/closure/random_world.json")
 env=dict(run.__dict__,OUT=OUT,files=files);exec(source,env);return env['snapshot']()
for module in modules:module.snapshot=snapshot
build=previous.palette.build;levels=previous.palette.levels

def relock(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'relock',locals())

def inventory():
 m=json.loads((ROOT/'metadata/program-model.json').read_text());callers={n:m['routines']['GAME:'+n]['callers'] for n in NAMES[:2]}
 assert callers=={'NextRandomBelowAx':['GAME:RespawnRainParticle'],'SeedRandomFromDosSeconds':['GAME:InitializeDosVideoInputAndSound']}
 indirect={n:[k for k,v in m['indirect_sites'].items() if m['routines']['GAME:'+n]['address'] in v.get('targets',[])] for n in NAMES[:2]}
 save(OUT/'inventory.json',dict(result='PASS',bytes=8,total=TOTAL,region='GAME:4EF7..4EFE',seconds_alias='GAME:4EF8, high byte of word0; aliases are not allocations',fields={n:m['variables'][n] for n in FIELDS},callers=callers,indirect=indirect,consumer_correction='Rain is the only static draw caller; no hazard calls/reads found. Hazards use deterministic counters. Unresolved external ABI callers remain admitted by the accepted bridge.',borrowers=['random_bridge: explicit generator storage view; projection after the time reply; stores preserve 1,2,3,0 order','water: accepted WW_RANDOM request through PIXEL_PEER_NextRandomBelowAx','lifecycle: accepted LIFE_SEED_RANDOM request at the single initialization point','Physical byte windows, streaming palette/ICE audio workspace access and decimal/far-copy live views'],decision_5R='Deferred: registry constness, active-code/workspace aliasing and mutable reveal metadata need their separate provider review/certificate. Not mixed into 5B.'))

def reuse():
 from standalone_census import bodies
 rel=BORROWERS[0];before=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT,text=True);after=(ROOT/rel).read_text()
 def direct_accessors(source):
  return source.removeprefix('#include "random_borrow.h"\n').replace('rng_read16(','rd16(').replace('rng_write16(','wr16(').replace('rng_write8(','wr8(')
 assert direct_accessors(after)==direct_accessors(before)
 folder=OUT/'reuse';folder.mkdir(exist_ok=True);definitions=[]
 for i,text in enumerate([before,after]):
  text=re.sub(r'#include "([^\"]+)"',lambda m:'#include "'+str((ROOT/rel).parent.joinpath(m[1]).resolve()).replace('\\','/')+'"' if (ROOT/rel).parent.joinpath(m[1]).is_file() else m[0],text)
  source=folder/(str(i)+'.c');source.write_text(text);pre=source.with_suffix('.i');bounded([previous.timing.common.GCC,'-E','-P','-I',ROOT/'c',source,'-o',pre],'reuse-'+str(i));text=pre.read_text();definitions.append({n:re.findall(r'\w+|[^\s]',text[a:e+1]) for a,b,e,n in bodies(text)})
 assert definitions[0]==definitions[1]
 for rel in ['native/random.c','native/random.h']:
  assert (ROOT/rel).read_bytes().replace(b'\r\n',b'\n')==subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT).replace(b'\r\n',b'\n')
 save(OUT/'reuse.json',dict(result='PASS',scope='Accepted recurrence/header unchanged; bridge only accessor renames plus header, default function-body tokens identical. Existing random A arithmetic/seed/reduction claims reused without extension; actual bridge proof replayed as well.'))

def api(group=None,*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'api',locals())

def router():
 folder=OUT/'router';folder.mkdir(exist_ok=True);exe=folder/'router.exe'
 bounded([previous.timing.common.GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/random_world_router.c',ROOT/'native/random_world.c',ROOT/'native/bridge/random_world_bridge.c'],'router-compile')
 row=bounded([exe],'router-run');save(OUT/'router.json',dict(result='PASS',counts=json.loads(row['stdout']),scope='Independent numeric lane/word layout, all8 lanes x256 and4 complete16-bit word slices, all physical non-owner addresses, partial writes/paragraph aliases/neighbor frames, serialization/seal and typed borrowers.'))

def proof():
 from closure_support import function
 folder=OUT/'proof';folder.mkdir(exist_ok=True)
 source='#include "random_world.h"\n#include "'+(ROOT/'native/random_world.c').as_posix()+'"\n'
 text=(ROOT/'native/bridge/random_world_bridge.c').read_text();source+=''.join(function(text,n) for n in ['rng_get','rng_put'])
 source+='\nvoid __CPROVER_assume(int);void __CPROVER_assert(int,const char*);\nRandomState nondet_state(void);unsigned nondet_uint(void);uint8_t nondet_byte(void);\nint main(void){world=nondet_state();RandomState before=world;unsigned lane=nondet_uint(),other=nondet_uint();uint8_t value=nondet_byte();\n __CPROVER_assume(lane<8 && other<8 && lane!=other);uint8_t old_other=rng_get(other);\n __CPROVER_assert(rng_get(lane)==(uint8_t)(before.word[lane/2]>>((lane&1)*8)),"numeric byte read");\n rng_put(lane,value);__CPROVER_assert(rng_get(lane)==value,"output");__CPROVER_assert(rng_get(other)==old_other,"arbitrary other byte frame and dependence");\n unsigned shift=(lane&1)*8;__CPROVER_assert(world.word[lane/2]==(uint16_t)((before.word[lane/2]&~(255u<<shift))|((unsigned)value<<shift)),"unchanged word companion lane");\n}\n'
 path=folder/'fields.c';path.write_text(source);pre=path.with_suffix('.i');bounded([previous.timing.common.GCC,'-E','-P','-nostdinc','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',path,'-o',pre],'proof-fields-pre')
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe'];r=bounded([tool,pre,'--unwind','3','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-fields');assert 'VERIFICATION SUCCESSFUL' in r['stdout']
 import random_evidence as revidence
 revidence.OUT=folder/'accepted';revidence.prove('next',60);revidence.prove('seed',60)
 save(OUT/'proof.json',dict(result='PASS',byte_profile=sha(pre),scope='Actual native-owner byte get/put: arbitrary full64-bit state, selected lane/value and arbitrary-other-byte output/frame/dependence. Accepted actual-C L1/native/bridge recurrence and partial seed proofs replayed, all64 state bits/16 bound bits and full service replies/status under their ordinary-RAM assumptions.'))

def projector(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'projector',locals())

def census(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'census',locals())

def weather():
 # Reuse entry-only observation for all rainy physical records and the existing witness.
 source=inspect.getsource(previous.weather_runs).replace("names=NAMES[8:17]+['RefreshHudAndTimerBar','InitializeLevelDisplay','LoadCurrentLevelState']","names=previous.NAMES[8:17]+['RefreshHudAndTimerBar','InitializeLevelDisplay','LoadCurrentLevelState','NextRandomBelowAx','SeedRandomFromDosSeconds']")
 source=source.replace("('session',names[10:])", "('session',names[10:12]),('random',names[12:])")
 source=source.replace("counts=dict(zip(names,json.loads(result.read_text())));", "counts=dict(zip(names,json.loads(result.read_text())));assert counts['NextRandomBelowAx']==counts['RespawnRainParticle']>0;assert counts['SeedRandomFromDosSeconds']==0;")
 env=dict(previous.__dict__,previous=previous,snapshot=snapshot,rain_reference=rain_reference);exec(source,env);env['weather_runs']()

def rain_reference(target):return previous.rain_reference(target)

def borrowers():
 import random_world_cases
 random_world_cases.run(ROOT,OUT,bounded,save)

def defects():
 import random_world_cases
 random_world_cases.defects(ROOT,OUT,bounded,save,snapshot,previous)

def finalize(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'finalize',locals())

def main(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'main',locals())
# Scheduled by world_gate; no private CLI.
