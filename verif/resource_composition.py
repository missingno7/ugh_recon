"""Coherent5R catalog cut, with a separate conservative provider review.
Serial600s/8-GiB children; only the scratch certificate is promoted.
"""
import argparse,ctypes as C,hashlib,inspect,io,json,re,shutil,subprocess,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/workers/close-stones-24'
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

def relock(final=False):
 import closure
 p=ROOT/'metadata/closure/resource_catalog.json'
 if not p.exists():save(p,dict(component='resource_catalog',status='unanalyzed',original=dict(owned=[],composes=['actor_types','render_primitives','demo_core','demo_presentation','ice','ice_scratch','player_world']),native=dict(files=NEW,functions=['native_resource_catalog','resource_token_valid','resource_sprite','resource_table','resource_effect','resource_read','resource_store','resource_provider_load_codec'],bridge='Registered resource tokens, native live sprite metadata, provider codec-table views, physical borrower and observation serialization'),purpose='Coherent5R1: live mutable sprite records and registered immutable codec-table views; broader registry/workspace ownership deferred',interface=dict(inputs='Relocated rebuilt-image provider at cold initialization; registered typed tokens and live mutable byte borrowers',outputs='2648 mutable metadata bytes plus60 provider ROM bytes, sealed RAM and separate observation serialization'),callers=['Renderer and demo width mutation; actor demo callback decoder; copy/decimal/streaming/ICE byte windows'],callees=['Accepted native owner chain for unmoved views'],indirect=['Three whitelisted demo effect roles; no code-address resolver'],memory=dict(new_mutable=2648,new_provider_readonly=60,total_native_observation_bytes=TOTAL),assumptions=['Accepted ordinary disjoint active code/resource/table/stack domains; codec table writes are outside the accepted ICE admission and fail closed','No constness inferred from missing model writers; all deferred resources remain mutable/unsettled','Cold provider initialization only; no resynchronization'],retained=['Whole raw sprite offset/dimension records; zero/wrapping dimensions and cursor behavior unchanged','Biased codec subviews and entire60-byte data block; no instruction bytes copied','Full65536-byte ICE borrowing, seeded tail, audio/map-prefix aliases unchanged'],eliminated=['RAM ownership of canonical sprite metadata and codec table view bytes'],amiga=dict(classification='not-used',finding='DOS provider/storage composition only'),uncertainty=['Partial5R: other identities/aliases and the canonical scratch allocation remain explicit continuations; D3/D5 not selected'],evidence=[dict(property='Resource catalog composition',level='D',method='Pending replay',command='python verif/resource_composition.py --gate',result='Pending',date='2026-11-15')],dependencies={},verification_inputs={},verification_input_hashing='sha256-lf-text'))
 source=inspect.getsource(run.relock);source='def refresh(final=False):\n'+source[source.index(' old='):];source=source.replace("'run_world'","'resource_catalog'").replace('Run ownership and explicit shared borrowers','Reviewed resource catalog and explicit live borrowers').replace('Pending cut 5A replay','Pending5R catalog replay').replace('verif/run_composition.py','verif/resource_composition.py');env=dict(run.__dict__,NEW=NEW,BASE=BASE,READ=READ,OUT=OUT,closure=closure);exec(source,env);env['refresh'](final)

def inventory():
 r=json.loads((OUT/'provider-review.json').read_text());assert r['result']=='PASS' and not r['codec_tables'][0]['observed_writes']
 save(OUT/'inventory.json',dict(result='PASS',provider_review=sha(OUT/'provider-review.json'),mutable=2648,readonly=60,total=TOTAL,classification=r['scope'],directory=r['directory'],codec_tables=r['codec_tables'],continuation='Other43-name bindings/nonmodel resources keep conservative mutable classifications; workspace ownership is not moved, full window+audio4+packed-map-prefix752 remain live.'))

def api(group):
 source=inspect.getsource(run.api);source=source.replace("suites={'front':['menu','menu_helpers','game_services'],'world':['scene','actors','actors_states','items_water','demo_scripts'],'input':['dos_input','render','render_primitives']}[group]", "suites="+repr(['render','render_primitives'] if group=='sprites' else ['demo_scripts','scene','ice','dos_input','game_services']))
 source=source.replace("['run_world','presentation_world'","['resource_catalog','player_world','random_world','run_world','presentation_world'")
 source=source.replace("('RUN','run')])","('RUN','run'),('RANDOM','rng'),('PLAYER','player'),('RESOURCES','resources')])");source=source.replace('annotate_api(group)','run.annotate_api(group)')
 env=dict(run.__dict__,NEW=NEW,BORROWERS=BORROWERS,WORLDS=WORLDS,NAMES=NAMES,OUT=OUT,run=run);exec(source,env);env['api'](group)

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

def projector():
 source=inspect.getsource(previous.palette.projector).replace('==6148','=='+str(TOTAL)).replace('Palette ownership cut only','Reviewed resource catalog5R1');env=dict(previous.palette.__dict__);exec(source,env);env['projector']()

def census():
 source=inspect.getsource(previous.census)
 leaves={'resource_catalog':['sprite_base','codec_base','resources_field','resources_is_owned','resources_shared_read','resources_shared_write','resources_borrowed_byte','resources_borrowed_store','resource_sprite_from_legacy','resource_effect_from_legacy','resource_table_from_legacy','resource_token_to_legacy'],'player_world':['player_field','player_field_get','player_field_put','player_is_owned','player_shared_read','player_shared_write','player_borrowed_byte','player_borrowed_store','player_borrow_read','player_borrow_write'],'random_world':['rng_lane','rng_get','rng_put','rng_is_owned','rng_shared_read','rng_shared_write','rng_borrowed_byte','rng_borrowed_store','rng_borrow_read','rng_borrow_write'],'run_world':['run_field','run_field_get','run_field_put','run_is_owned','run_shared_read','run_shared_write','run_borrowed_byte','run_borrowed_store','run_borrow_read','run_borrow_write']}
 source=source.replace("'presentation_world':['presentation_field'",''.join(repr(n)+':'+repr(v)+',\n ' for n,v in leaves.items())+"'presentation_world':['presentation_field'",1).replace("paths={'native/bridge/hud_bridge.c','native/bridge/water_weather_bridge.c','native/bridge/presentation_world_bridge.c'}","paths={'native/bridge/resource_catalog_bridge.c'}").replace("'-DUGH_NATIVE_PRESENTATION','-I'","'-DUGH_NATIVE_PRESENTATION','-DUGH_NATIVE_RUN','-DUGH_NATIVE_RANDOM','-DUGH_NATIVE_PLAYER','-DUGH_NATIVE_RESOURCES','-I'")
 source=source.replace('Native HUD/weather bridges and owner; session/menu/high-score callers remain explicit borrowers, not part of this machine-edge island.','Registered resource catalog/byte-borrow island. Incoming renderer/demo/codec sequencing remains at the accepted outer API boundary.')
 env=dict(previous.__dict__,snapshot=snapshot,NAMES=NAMES);exec(source,env);env['census']()

def borrowers():
 import resource_catalog_cases
 resource_catalog_cases.run(ROOT,OUT,bounded,save)
def defects():
 import resource_catalog_cases
 resource_catalog_cases.defects(ROOT,OUT,bounded,save,snapshot,previous)

def finalize():
 names=['inventory','reuse','router','proof','api-sprites','api-resources','borrowers','defects','census','levels'];results={n:json.loads((OUT/(n+'.json')).read_text()) for n in names};assert all(r['result']=='PASS' for r in results.values())
 assert any(r.get('seeded_codec_table_reference') for r in results['borrowers']['cases'])
 for g in ['sprites','resources']:
  r=results['api-'+g];assert not r['explicit_out_of_domain'];assert all(sha(ROOT/f)==h for f,h in r['seam_inputs'].items())
 runs=[json.loads(p.read_text()) for p in (OUT/'projector/runs').glob('*.json')];assert len(runs)==21 and all(r['canonical_native_owned_bytes']==TOTAL and not r['native_owned_journal_publications'] for r in runs)
 cpath=ROOT/'metadata/closure/resource_catalog.json';c=json.loads(cpath.read_text());c['proposed_status']='migrated';c['memory']['classification']='2648 mutable directory bytes +60 private provider codec-table bytes; original data source remains relocated rebuilt image';c['memory']['continuation']=results['inventory']['continuation']
 c['assumptions']=[
  'Only the explicit60-byte IceDecoderTables data block is registered immutable; its match names are biased views, not allocations. Accepted ICE uses the shipped table values and disjoint source-read/output-write footprints, active code/tables and stack',
  'Provider initialization is privileged cold construction once per resource lifetime. Consumers borrow const codec views; game stores go through the checked API/byte router. No client casts away const or calls the provider initializer as a runtime store',
  'All662 raw source-offset/dimension records remain mutable, including fields with no observed normal writer. The reveal byte aliases record214 lane2; generic partial/straddling/paragraph aliases refer to the same owner',
  'Tokens are closed kind/index identities. Verification alone maps historical words. Directory-record identity does not force a pixel-bank identity; raw renderer index reductions and independent bank selection remain unchanged',
  'Codec windows still borrow all65536 bytes, including seeded retained tails. Audio flags and the752-byte packed-map prefix are not duplicated or clipped; actual table writes are outside accepted codec admission and fail closed',
  'Cold import is fixture/provider setup only. Live moved RAM stays sealed; serialization is observation-only, never writeback or resynchronization; working native policy views are temporary',
  'Every deferred resource remains mutable/unsettled pending alias review; no constness is inferred from absent model writers or finite no-write counts. No D3/D5 or missing-data policy is chosen']
 count=sum(results['api-'+g]['composed_matching'] for g in ['sprites','resources']);c['evidence']=[dict(property='Provider review and field policy',level='B',method=results['proof']['scope'],command='python verif/resource_composition.py --proof --router',result='PASS: actual-C byte/immutable-policy profiles; all token/physical/word/lane/frame/readonly checks',date='2026-11-15'),dict(property='Provider writer classification',level='D',method='Pre-cut HEAD-only generated write census; static source writers plus decoded allocations; no constness inferred from absent names',command='python verif/resource_review.py --observe',result='PASS:20 scenarios and81+7+8 level runs, every reference frame;43 named and764 nonmodel/decoded regions; biased60-byte codec span retained, workspace audio/map-prefix overlaps identified',date='2026-11-15'),dict(property='API and byte-window/codec composition',level='C',method='Independent Unicorn and compiled L1/native comparisons; full returned RAM, live replies and ordered ports/requests; atomic decoder prefix exception retained',command='python verif/resource_composition.py --api-sprites --api-resources --borrowers',result=f'PASS:{count} API runs per profile, zero new rejections; mutable metadata, typed token, retained full-window and readonly guard witnesses',date='2026-11-15'),dict(property='Composed ownership',level='D',method='Committed HEAD archive plus owned overlay, scratch certificate promotion, independent ASM references, sealed RAM and observation-only serialization',command='python verif/resource_composition.py --build --projector --census --levels',result=f'PASS:closure56/0, host21/21 both variants,17,955 boundaries,10841 native observation bytes, zero owner journal publications/fallbacks/L1 bodies/catalog machine edges;81+7+8 levels both variants',date='2026-11-15'),dict(property='Seeded seams',level='C',method=results['defects']['scope'],command='python verif/resource_composition.py --defects',result='PASS: immutable write fails closed; stale reveal width, wrong token map, missed serialization and full-window controls detected',date='2026-11-15')];save(cpath,c);relock(final=True);save(OUT/'verification-receipt.json',dict(result='PASS',status='unanalyzed',proposed_status='migrated',scope='Partial5R catalog only; classification for all remaining resources recorded',new_native_observation_bytes=2708,total=TOTAL,evidence={n:sha(OUT/(n+'.json')) for n in names},relocks=json.loads((OUT/'relocks.json').read_text())))

def main():
 p=argparse.ArgumentParser(description=__doc__);stages=['locks','inventory','reuse','router','proof','api-sprites','api-resources','borrowers','build','projector','census','levels','defects','finalize','gate','internal']
 for s in stages:p.add_argument('--'+s,action='store_true')
 a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
 if a.locks:relock()
 if a.gate:
  if not (OUT/'provider-review.json').exists():bounded([sys.executable,ROOT/'verif/resource_review.py','--observe'],'provider-review-replay')
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
