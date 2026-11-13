"""Isolated hazard + native contacts/items variant, without writes to L0/L1."""
import os,re,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
sys.path.insert(0,str(ROOT/'tools'))
OUT=ROOT/'build/workers/close-hazards'
BRIDGE=ROOT/'native/bridge/hazards_bridge.c'
NAMES=re.findall(r'EXPORT int c_(\w+)\(',BRIDGE.read_text())
ENTRIES=dict(re.findall(r'if\(target==G\((\w+)\)\) \{ \*entry=(H_\w+);',BRIDGE.read_text()))
ENTRIES.pop('IgnoreActorState',None)
SOURCES=[ROOT/'native/hazards.c',BRIDGE,ROOT/'native/contacts.c',ROOT/'native/bridge/contacts_bridge.c',
         ROOT/'native/items.c',ROOT/'native/bridge/items_bridge.c',ROOT/'native/level_view.c',ROOT/'native/bridge/level_view_bridge.c']

def build():
    folder=OUT/f'variant_{os.getpid()}';folder.mkdir(parents=True,exist_ok=True)
    replacements=NAMES+['FindPlayerTouchingEnemy','FindPlayerTouchingActor','FindPlayerTouchingFallingItem','FindThrownStoneHittingEnemy',
        'SpawnFallingItem','LandFallingItem','AdvanceFallingItem','ExpireOrCollectFallingItem','DispatchFallingItems']
    sources=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        text=path.read_text();changed=False
        for name in replacements:
            text,n=re.subn(r'(EXPORT int )c_'+name+r'(?=\()',r'\1l1_'+name,text);changed|=bool(n)
        if changed:
            generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    text=BRIDGE.read_text().replace('#include "../hazards.h"','#include "'+(ROOT/'native/hazards.h').as_posix()+'"')
    text=text.replace('typedef struct HazardPlan','EXPORT uint32_t hazards_audit[64];\ntypedef struct HazardPlan',1)
    for i,name in enumerate(NAMES):
        body=function(text,'c_'+name)
        body2=body.replace('{',f'{{ hazards_audit[{i}]++;',1)
        body2=body2.replace(f'return l1_{name}(r);',f'return hazards_audit[{i+32}]++, l1_{name}(r);')
        text=text.replace(body,body2)
    generated=folder/'hazards_bridge.c';generated.write_text(text)
    dll=folder/'hazards.dll'
    result=compile_c(sources+[p for p in SOURCES if p!=BRIDGE]+[generated],dll,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared'])
    result['maintained_inputs']=hashes([*SOURCES,*sorted((ROOT/'c').glob('*.[ch]')),*sorted((ROOT/'native').rglob('*.h')),Path(__file__)])
    save(OUT/'build.json',result);return dll

if __name__=='__main__':print(build())
