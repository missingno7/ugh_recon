"""Coherent5R catalog cut, with a separate conservative provider review.
Serial600s/8-GiB children; only the scratch certificate is promoted.
"""
import argparse,ctypes as C,hashlib,inspect,io,json,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/workers/close-stones-24'
sys.path.insert(0,str(ROOT/'tools'))
import player_composition as player
prior=player.prior;run=prior.run;previous=run.previous
for m in [player]+player.modules:m.OUT=OUT
bounded=player.bounded;save=player.save;sha=player.sha
NEW=['native/resource_catalog.h','native/resource_catalog.c','native/bridge/resource_catalog_bridge.h','native/bridge/resource_catalog_bridge.c']
BORROWERS=['native/bridge/actor_resources_bridge.c']
BASE=NEW+BORROWERS+['verif/resource_composition.py','verif/resource_review.py','verif/resource_catalog_router.c','verif/resource_catalog_cases.py','tools/hostbuild.py','host/main.c','verif/projector/observer.c','verif/projector/timing_serializer.h','verif/projector/publications.py','verif/projector_evidence.py']
READ=sorted(set(player.READ+['verif/player_composition.py','metadata/closure/player_world.json','native/ice.c','native/ice_scratch.c','native/bridge/ice_bridge.c','native/bridge/ice_scratch_bridge.c','native/bridge/pictures_bridge.c','native/bridge/demo_presentation_bridge.c','native/bridge/actor_projection.h','tools/dataprobe.py']))
WORLDS=player.WORLDS+['resource_catalog'];TOTAL=10841
NAMES=['DrawTransparentSprite','RestoreSpriteBackground','SetDemoRevealSpriteWidth','PlaySpriteRevealDemo','RunScriptedDemo','InitializeDemoScripts','AdvanceDemoScripts','DrawDemoSprites','EraseDemoSprites','UnpackIceStream','UnpackIceToScratch','UnpackPictureAndCopyPalette']

def files():return sorted(set(BASE+subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()+['metadata/closure/resource_catalog.json']))
def snapshot():
 source=prior.RUN_SNAPSHOT_SOURCE.replace('metadata/closure/run_world.json','metadata/closure/resource_catalog.json');env=dict(run.__dict__,OUT=OUT,files=files);exec(source,env);return env['snapshot']()
for m in [player]+player.modules:m.snapshot=snapshot
build=previous.palette.build;levels=previous.palette.levels

def relock(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'relock',locals())

def inventory():
 r=json.loads((OUT/'provider-review.json').read_text());assert r['result']=='PASS' and not r['codec_tables'][0]['observed_writes']
 save(OUT/'inventory.json',dict(result='PASS',provider_review=sha(OUT/'provider-review.json'),mutable=2648,readonly=60,total=TOTAL,classification=r['scope'],directory=r['directory'],codec_tables=r['codec_tables'],continuation='Other43-name bindings/nonmodel resources keep conservative mutable classifications; workspace ownership is not moved, full window+audio4+packed-map-prefix752 remain live.'))

def api(group=None,*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'api',locals())

def reuse():
 from standalone_census import bodies
 rel=BORROWERS[0];old=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT,text=True);new=(ROOT/rel).read_text();folder=OUT/'reuse';folder.mkdir(exist_ok=True);defs=[]
 for i,text in enumerate([old,new]):
  text=re.sub(r'#include "([^\"]+)"',lambda m:'#include "'+(ROOT/rel).parent.joinpath(m[1]).resolve().as_posix()+'"' if (ROOT/rel).parent.joinpath(m[1]).is_file() else m[0],text);p=folder/(str(i)+'.c');p.write_text(text);pre=p.with_suffix('.i');bounded([previous.timing.common.GCC,'-E','-P','-I',ROOT/'c',p,'-o',pre],'reuse-'+str(i));text=pre.read_text();defs.append({n:re.findall(r'\w+|[^\s]',text[a:e+1]) for a,b,e,n in bodies(text)})
 assert defs[0]==defs[1]
 pure=[]
 for p in (ROOT/'native').glob('*'):
  if p.suffix not in ['.h','.c'] or p.name.startswith('resource_catalog'):continue
  rel=p.relative_to(ROOT).as_posix();assert p.read_bytes().replace(b'\r\n',b'\n')==subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT).replace(b'\r\n',b'\n'),rel;pure.append(rel)
 save(OUT/'reuse.json',dict(result='PASS',scope='Accepted ordinary algorithms/headers unchanged. Actor-resource default bridge function bodies identical; composed callback decoder alone consumes registered effect tokens. No old assumption/status widened.',pure_sources=pure))

def router():
 folder=OUT/'router';folder.mkdir(exist_ok=True);exe=folder/'router.exe';bounded([previous.timing.common.GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/resource_catalog_router.c',ROOT/'native/resource_catalog.c',ROOT/'native/bridge/resource_catalog_bridge.c'],'router-compile');r=bounded([exe],'router-run');save(OUT/'router.json',dict(result='PASS',counts=json.loads(r['stdout'])))

def proof():
 from closure_support import function
 folder=OUT/'proof';folder.mkdir(exist_ok=True);text=(ROOT/'native/resource_catalog.c').read_text();prefix='#include "resource_catalog.h"\n'+''.join(function(text,n) for n in ['resource_sprite_byte','resource_sprite_put'])
 code=r'''void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);
ResourceSpriteRecord nondet_record(void);unsigned nondet_uint(void);uint8_t nondet_byte(void);
int main(void){ResourceSpriteRecord s=nondet_record(),before=s;unsigned lane=nondet_uint(),other=nondet_uint();uint8_t v=nondet_byte();__CPROVER_assume(lane<4 && other<4 && lane!=other);
 uint16_t word=lane<2?before.source_offset:before.dimensions;uint8_t frame=resource_sprite_byte(&s,other);
 __CPROVER_assert(resource_sprite_byte(&s,lane)==(uint8_t)(word>>((lane&1)*8)),"numeric byte read");resource_sprite_put(&s,lane,v);
 __CPROVER_assert(resource_sprite_byte(&s,lane)==v,"published byte");__CPROVER_assert(resource_sprite_byte(&s,other)==frame,"arbitrary other byte frame and dependence");
 unsigned shift=(lane&1)*8;__CPROVER_assert((lane<2?s.source_offset:s.dimensions)==(uint16_t)((word&~(255u<<shift))|((unsigned)v<<shift)),"word companion lane");}
'''
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe'];rows=[]
 for name,source,unwind in [('sprite-byte',prefix+code,2),('immutable-policy','#include "'+(ROOT/'native/resource_catalog.c').as_posix()+'"\n'+r'''void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);unsigned nondet_uint(void);uint8_t nondet_byte(void);
int main(void){unsigned table=nondet_uint(),lane=nondet_uint();uint8_t v=nondet_byte();__CPROVER_assume(table<5);ResourceToken t={RESOURCE_CODEC_TABLE,(uint16_t)table};ResourceTableView view;__CPROVER_assert(resource_table(t,&view)==RESOURCE_OK,"registered table");__CPROVER_assume(lane<view.size);codec[0]=nondet_byte();uint8_t before=codec[0];__CPROVER_assert(resource_store(t,lane,v)==RESOURCE_IMMUTABLE,"immutable store rejected");__CPROVER_assert(codec[0]==before,"table frame");}
''',2)]:
  p=folder/(name+'.c');p.write_text(source);pre=p.with_suffix('.i');bounded([previous.timing.common.GCC,'-E','-P','-nostdinc','-DUINT16_MAX=65535','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',p,'-o',pre],'proof-'+name+'-pre');r=bounded([tool,pre,'--unwind',str(unwind),'--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-'+name);assert 'VERIFICATION SUCCESSFUL' in r['stdout'];rows.append(dict(profile=name,preprocessed=sha(pre)))
 save(OUT/'proof.json',dict(result='PASS',profiles=rows,scope='Actual-C mutable record lane output/frame/dependence and readonly store rejection. Kernel is called only after token/index/lane checks; exhaustive router covers all662 records and all token mappings. No whole-catalog symbolic-world or universal constness theorem.'))

def projector(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'projector',locals())

def census(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'census',locals())

def borrowers():
 import resource_catalog_cases
 resource_catalog_cases.run(ROOT,OUT,bounded,save)
def defects():
 import resource_catalog_cases
 resource_catalog_cases.defects(ROOT,OUT,bounded,save,snapshot,previous)

def finalize(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'finalize',locals())

def main(*args,**kwargs):
 from world_gate import legacy_stage
 return legacy_stage(__name__,'main',locals())
# Scheduled by world_gate; no private CLI.
