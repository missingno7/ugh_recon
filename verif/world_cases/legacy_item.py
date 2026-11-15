"""Cut 5G operators. Scheduling, fixtures and bounds belong to world_gate."""
import ctypes as C,hashlib,json,re,subprocess,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
from job_pool import save,run
from closure_support import GCC
OUT=ROOT/'build/workers/cut-5g/gate'
def bounded(command,tag,cwd=ROOT,**kwargs):
 return run(command,cwd,OUT,tag,**kwargs)
FIELDS=['FallingItemDescriptors', 'FallingItemCallbacks', 'FallingItemSprites', 'FallingItemEraseSprite', 'FallingItemX', 'FallingItemY', 'FallingItemDrawX', 'FallingItemPreviousDrawX', 'FallingItemDrawY', 'FallingItemPreviousDrawY', 'FallingItemMotionOrLifetime', 'FallingItemVerticalStep']
BORROWER_MAP={'actor_render_bridge.c': ['RENDER', 'enemies'], 'contacts_bridge.c': ['PHYSICS', 'enemies'], 'hazards_bridge.c': ['ACTORS', 'enemies'], 'items_bridge.c': ['ITEMS', 'platforms'], 'passenger_delivery_bridge.c': ['ACTORS', 'enemies'], 'session_bridge.c': ['SESSION', 'enemies'], 'session_support.h': ['SESSION', 'platforms']}
BORROWERS=["native/bridge/"+n for n in BORROWER_MAP]
model=json.loads((ROOT/"metadata/program-model.json").read_text())
NAMES=sorted({r.split(":")[1] for n in FIELDS for k in ["readers","writers"] for r in model["variables"][n][k]}|{"LoadCurrentLevelState","InitializeLevelDisplay","InitializeDemoScripts","EraseDemoSprites","ReleaseTreeReward","DeliverPassenger","FindPlayerTouchingFallingItem","ResetSpriteEraseState"})

def proof():
 from closure_support import function
 folder=OUT/'proof';folder.mkdir(exist_ok=True);text=(ROOT/'native/bridge/item_world_bridge.c').read_text()
 prefix='#include "item_world.h"\n#include <stddef.h>\n#include "'+(ROOT/'native/item_world.c').as_posix()+'"\n'
 prefix+='void *memcpy(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}\n'
 prefix+=re.search(r'typedef struct ItemstateField.*?} ItemstateField;',text,re.S)[0]+'\n'+''.join(function(text,n) for n in ['itemstate_field_get','itemstate_field_put'])
 prefix+='void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);\n#define assert(c) __CPROVER_assert((c),#c)\n'
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe'];rows=[]
 for name in ['read','store']:
  p=folder/(name+'.c');p.write_text(('#define ITEMSTATE_PROOF_STORE\n' if name=='store' else '')+prefix+(ROOT/'verif/item_world_byte_proof.c').read_text(),encoding='utf-8');pre=p.with_suffix('.i')
  bounded([GCC,'-E','-P','-nostdinc','-DUINT16_MAX=65535','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',p,'-o',pre],'proof-'+name+'-pre')
  r=bounded([tool,pre,'--unwind','5','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-'+name);assert 'VERIFICATION SUCCESSFUL' in r['stdout'];rows.append(dict(profile=name,preprocessed=hashlib.sha256(pre.read_bytes()).hexdigest()))
 save(OUT/'proof.json',dict(result='PASS',profiles=rows,scope='Actual-C strided16-bit item field byte get/put; arbitrary complete native world, any admitted slot, lane/value, valid member in first record and arbitrary-other-byte output/frame/dependence. Layout/registration via exhaustive router, not a resource/async theorem.'))

def router():
 folder=OUT/'router';folder.mkdir(exist_ok=True);exe=folder/'router.exe'
 bounded([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/item_world_router.c',ROOT/'native/item_world.c',ROOT/'native/bridge/item_world_bridge.c'],'router-compile')
 row=bounded([exe],'router-run');save(OUT/'router.json',dict(result='PASS',counts=json.loads(row['stdout']),scope='Independent literal coordinates/member oracle; 288 lanes x256; all 144 words x65536; roles/straddles/paragraph aliases; descriptor index12 callback alias; demo EnemyEraseSprite index15 item descriptor[0] alias; resource bytes excluded; import/seal/serializer/frame.'))
def inventory():
 save(OUT/'inventory.json',dict(result='PASS',bytes=288,total=12247,region='DGROUP:2D6B..2E8B',slots=12,fields=FIELDS,readers_writers={n:model['variables'][n] for n in FIELDS},borrowers=BORROWERS,additional=['Demo16-index EnemyEraseSprite raw reset reaches item descriptor[0] at2D6B','Loader/reset bulk windows; generic far-copy, decimal and ICE borrow the world registry'],classification='One persistent 12-slot owner. Descriptor/callback words are raw compatibility identities. Descriptor resource bytes stay live mutable provider views. Single motion/lifetime word; simulation, draw and previous erase coordinates stay distinct.'))
def reuse():
 from standalone_census import bodies
 folder=OUT/'reuse';folder.mkdir(exist_ok=True);rows=[]
 for name,(role,prior) in BORROWER_MAP.items():
  rel='native/bridge/'+name;before=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT,text=True);after=(ROOT/rel).read_text()
  restored=re.sub(r'\A#include "platform.h"\n#ifndef ITEMSTATE_BORROWER\n#define ITEMSTATE_BORROWER ITEMSTATE_BORROW_\w+\n#endif\n#include "items_borrow.h"\n','',after,count=1)
  restored=re.sub(r'\bitemstate_read(8|16|32)\b',lambda m:prior+'_read'+m[1],restored);restored=re.sub(r'\bitemstate_write(8|16|32)\b',lambda m:prior+'_write'+m[1],restored)
  restored=restored.replace('samples a stable descriptor view','samples an immutable descriptor');assert restored==before,rel
  definitions=[]
  for i,text in enumerate([before,after]):
   text=re.sub(r'#include "([^\"]+)"',lambda m:'#include "'+(ROOT/rel).parent.joinpath(m[1]).resolve().as_posix()+'"' if (ROOT/rel).parent.joinpath(m[1]).is_file() else m[0],text)
   p=folder/(str(i)+'-'+Path(rel).name);p.write_text(text);pre=p.with_suffix('.i');bounded([GCC,'-E','-P','-I',ROOT/'c',p,'-o',pre],'reuse-'+str(i)+'-'+p.stem);text=pre.read_text();definitions.append({n:re.findall(r'"(?:\\.|[^"\\])*"|\w+|[^\s]',text[a:e+1]) for a,b,e,n in bodies(text)})
  assert definitions[0]==definitions[1],rel;rows.append(rel)
 pure=[]
 for p in sorted((ROOT/'native').glob('*')):
  if p.suffix not in ['.c','.h'] or p.name.startswith('item_world'):continue
  rel=p.relative_to(ROOT).as_posix();assert subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT).replace(b'\r\n',b'\n')==p.read_bytes().replace(b'\r\n',b'\n'),rel;pure.append(rel)
 save(OUT/'reuse.json',dict(result='PASS',bridges=rows,pure_sources_unchanged=pure,scope='Mechanical borrower routing only; default preprocessed function bodies unchanged. Accepted algorithm proofs/domains retained; new owner has independent state-seam proof.'))
def borrowers():
 import item_world_cases
 item_world_cases.run(ROOT,OUT,bounded,save)
def defects():
 import item_world_cases
 item_world_cases.defects(ROOT,OUT,bounded,save)
def deepcounts():
 import item_world_cases
 item_world_cases.deepcounts(ROOT,OUT,bounded,save)
