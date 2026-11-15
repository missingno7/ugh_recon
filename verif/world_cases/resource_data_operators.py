"""Remaining5R allocation operators. Scheduling and bounds are world_gate's."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/workers/cut-5r2'
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
from cbuild import GCC
from job_pool import save,run
def bounded(command,tag,cwd=ROOT,ok=(0,)):
 return run(command,cwd,OUT,tag,allowed=ok)
NAMES=['DrawTransparentSprite','RestoreSpriteBackground','SetDemoRevealSpriteWidth','PlaySpriteRevealDemo','RunScriptedDemo','InitializeDemoScripts','AdvanceDemoScripts','DrawDemoSprites','EraseDemoSprites','UnpackIceStream','UnpackIceToScratch','UnpackPictureAndCopyPalette']
def compiler(exe,fault=0):
 return [GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-DRESOURCE_DATA_TEST_FAULT='+str(fault),'-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/resource_world_router.c',ROOT/'native/resource_world.c',ROOT/'native/bridge/resource_world_bridge.c']
def router():
 exe=OUT/'router.exe';bounded(compiler(exe),'router-build');r=bounded([exe],'router-run')
 import hostbuild
 # Preserve the original integer promotions as well as numeric byte values.
 # The generic borrower transports a uint32_t; its ABI read views must retain
 # their byte/word result types when used in signed C expressions.
 text='#include "platform.h"\n'+''.join('_Static_assert(_Generic(rd'+str(bits)+'(0,0),uint'+str(bits)+'_t:1,default:0),"resource read type '+str(bits)+'");\n' for bits in [8,16,32])
 p=OUT/'read-types.c';p.write_text(hostbuild.composition_source('native/bridge/player_physics_bridge.c',text,hostbuild.selected_units()))
 bounded([GCC,'-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native/bridge','-c',p,'-o',OUT/'read-types.o'],'router-read-types')
 save(OUT/'router.json',dict(result='PASS',counts=json.loads(r['stdout']),read_types=[8,16,32]))
def proof():
 # Actual checked kernel with arbitrary tokens/positions; unwind applies only
 # to the test harness (the resource functions contain no loops).
 folder=OUT/'proof';folder.mkdir(exist_ok=True)
 p=folder/'bounds.c';p.write_text('#include "'+(ROOT/'native/resource_world.c').as_posix()+'"\n'+r'''
void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);
unsigned nondet_uint(void);uint8_t nondet_byte(void);
int main(void){unsigned t=nondet_uint(),p=nondet_uint(),role=nondet_uint();uint8_t v=nondet_byte(),out=0;
 __CPROVER_assume(t<RESOURCE_WORLD_VIEWS&&role<RESOURCE_BORROW_COUNT);
 ResourceWorldToken token={(uint16_t)t};ResourceWorldView view;resource_world_view(token,&view);
 __CPROVER_assume(p<view.size);uint32_t index;
 __CPROVER_assert(resource_world_position((ResourceBorrower)role,token,p,&index),"valid view position");
 __CPROVER_assert(index<RESOURCE_WORLD_BYTES,"allocation bounds");
 __CPROVER_assert(!resource_world_position((ResourceBorrower)role,token,view.size,&index),"one past view rejected");
}
''')
 pre=p.with_suffix('.i');bounded([GCC,'-E','-P','-nostdinc','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',p,'-o',pre],'proof-pre')
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe']
 r=bounded([tool,pre,'--unwind','2','--unwinding-assertions','--bounds-check','--pointer-check','--slice-formula'],'proof-bounds')
 assert 'VERIFICATION SUCCESSFUL' in r['stdout'];save(OUT/'proof.json',dict(result='PASS',scope='Actual C checked view lookup and allocation bounds; arbitrary v1 view/role/position. Exhaustive router checks byte store/read/frame, aliases and serialization; no symbolic whole-workspace claim.'))
def borrowers():
 import resource_catalog_cases
 resource_catalog_cases.run(ROOT,OUT,bounded,save)
def defects():
 rows=[]
 for fault,name,exit_code in [(1,'lost-shared-animation-word',2),(2,'missed-serialization',88),(3,'clipped-workspace',2),(4,'wrong-view-token',15)]:
  exe=OUT/(name+'.exe');bounded(compiler(exe,fault),'defect-'+name+'-build');r=bounded([exe],'defect-'+name+'-run',ok=(exit_code,));rows.append(dict(defect=name,result='DETECTED',exit=r['returncode'],case='All physical lanes, live shared player boundary and whole separate observation comparator'))
 # Mutate the audio owner between the codec's seed and its publication. The
 # retained tail must borrow the live owner; publishing the stale seed loses it.
 import ctypes as C,nbuild,difftest,resource_catalog_cases as rc
 from dataprobe import ice_pack235
 command=json.loads((OUT/'children/api-resources-composed-compile.json').read_text())['command']
 results=[]
 for stale in [False,True]:
  folder=OUT/('tail-stale' if stale else 'tail-live');folder.mkdir(exist_ok=True);cmd=list(command);cmd[cmd.index('-o')+1]=str(folder/'api.dll')
  for i,arg in enumerate(cmd):
   if arg.endswith('audio_world_bridge.c'):
    p=Path(arg);text=p.read_text();needle='void audio_workspace_publish(uint32_t base,const uint8_t *source,unsigned count,unsigned extent,size_t written){';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n ugh_write(lin(UGH_S_ZERO_IceDecodeWorkspace,64768),0x39);ugh_write(lin(UGH_S_ZERO_IceDecodeWorkspace,64769),0x17);')
    if stale:
     assert text.count('if(written>distance)')==1;text=text.replace('if(written>distance)','if(written>distance || address==lin(UGH_S_ZERO_IceDecodeWorkspace,64768) || address==lin(UGH_S_ZERO_IceDecodeWorkspace,64769))')
    import re
    text=re.sub(r'#include "([^\"]+)"',lambda m:'#include "'+(p.parent/m[1]).resolve().as_posix()+'"' if (p.parent/m[1]).is_file() else m[0],text)
    q=folder/p.name;q.write_text(text);cmd[i]=str(q)
  bounded(cmd,'tail-'+str(stale)+'-compile');dll=nbuild.load_l1(folder/'api.dll');m=difftest.Machine();m.reset();m.write(0x8500,0,ice_pack235(b'\x51'))
  got=rc.pair(m,[dll],'UnpackIceToScratch',dict(DS=0x8500,SI=0))[0]
  address=m.seg('ZERO:IceDecodeWorkspace')*16+64768;results.append(got[2][address:address+2])
 assert results[0]==b'\x39\x17' and results[1]!=results[0],results
 rows.append(dict(defect='stale-parent-tail-overwrite',result='DETECTED',case='UnpackIceToScratch one-byte output; audio flag mutation after seed, before retained-tail publication',expected=results[0].hex(),mutant=results[1].hex()))
 save(OUT/'defects.json',dict(result='PASS',controls=rows))
def inventory():
 m=json.loads((ROOT/'metadata/resource-world.json').read_text())
 assert m['workspace']['window']==65536 and sum(r['size'] for r in m['regions'])==m['storage_bytes']
 for a,b in zip(m['regions'],m['regions'][1:]):assert a['image_start']+a['size']<=b['image_start']
 for v in m['views']:assert v['offset']+v['size']<=m['regions'][v['region']]['size']
 save(OUT/'inventory.json',dict(result='PASS',bytes=m['storage_bytes'],native_total=m['native_after'],views=len(m['views']),classification=m['classification'],workspace=m['workspace']))
