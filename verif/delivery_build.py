"""Coupled passenger bridge plus actual native contact/item dependencies."""
import os,re,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
from delivery_shells import NAMES,ENTRIES,BRIDGE
sys.path.insert(0,str(ROOT/'tools'))
OUT=ROOT/'build/workers/close-stones-3'
CONTACTS=['FindPlayerTouchingActor','FindPlayerTouchingEnemy','FindPlayerTouchingFallingItem','FindThrownStoneHittingEnemy']
ITEMS=['SpawnFallingItem','AdvanceFallingItem','LandFallingItem','ExpireOrCollectFallingItem','DispatchFallingItems']
SOURCES=[ROOT/'native/passenger_delivery.c',BRIDGE,ROOT/'native/actor_resources.c',ROOT/'native/bridge/actor_resources_bridge.c',
    ROOT/'native/level_view.c',ROOT/'native/bridge/level_view_bridge.c',ROOT/'native/contacts.c',ROOT/'native/bridge/contacts_bridge.c',
    ROOT/'native/items.c',ROOT/'native/bridge/items_bridge.c']
def build():
    folder=OUT/f'variant_{os.getpid()}';folder.mkdir(parents=True,exist_ok=True);sources=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        text=path.read_text();changed=False
        for name in NAMES+CONTACTS+ITEMS:
            text,n=re.subn(r'(EXPORT int )c_'+name+r'(?=\()',r'\1l1_'+name,text);changed|=bool(n)
        if changed:
            generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    text=BRIDGE.read_text().replace('#include "../passenger_delivery.h"','#include "'+(ROOT/'native/passenger_delivery.h').as_posix()+'"')
    text=text.replace('typedef struct DeliveryPlan','EXPORT uint32_t delivery_audit[24];\ntypedef struct DeliveryPlan',1)
    for i,name in enumerate(NAMES):
        body=function(text,'c_'+name);new=body.replace('{',f'{{ delivery_audit[{i}]++;',1)
        new=new.replace(f'l1_{name}(r)',f'(delivery_audit[{i+12}]++,l1_{name}(r))');text=text.replace(body,new)
    generated=folder/'passenger_delivery_bridge.c';generated.write_text(text)
    dll=folder/'delivery.dll';result=compile_c(sources+[p for p in SOURCES if p!=BRIDGE]+[generated],dll,
        [ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared','-DACTOR_VERIFY'])
    result['maintained_inputs']=hashes([*SOURCES,Path(__file__),*sorted((ROOT/'c').glob('*.[ch]')),*sorted((ROOT/'native').rglob('*.h'))])
    save(OUT/'build.json',result);return dll
def pair(folder):
    folder.mkdir(parents=True,exist_ok=True)
    text=f'#include "{(ROOT/"c/ugh.h").as_posix()}"\n'
    text+='uint16_t dl_read(uint16_t,uint16_t);void dl_write(uint16_t,uint16_t,uint16_t);uint8_t dl_byte(uint16_t,uint16_t);void dl_byte_write(uint16_t,uint16_t,uint8_t);\n'
    text+='#define rd16 dl_read\n#define wr16 dl_write\n#define rd8 dl_byte\n#define wr8 dl_byte_write\n'
    groups=[('actors.c',['shl','less','greater','actor_init','tail','state_jump','contact'],[NAMES[i] for i in [0,2,4,6,9,10]]+['FindPlayerTouchingActor','BeginPassengerResurfacing']),
        ('actors_states.c',['lt','gt','shift','inc','push','pop','effect','frame','actor_tick','submerged','water_swap','platform_player','display','tail'],[NAMES[i] for i in [1,3,5,7,8,11]]),
        ('items_water.c',['cell'],['IgnoreExhaustedTree','SpawnFallingItem'])]
    for group,(module,helpers,names) in enumerate(groups):
        raw=(ROOT/'c'/module).read_text()
        for name in helpers:text+=f'#define {name} dl_ref{group}_{name}\n'
        text+='\n'.join(line for line in raw.splitlines() if line.startswith('#define '))+'\n'
        if group==0:text+='static int state_jump(Regs *,uint16_t);static int tail(Regs *,unsigned);\n'
        if group==1:text+='static int tail(Regs *,unsigned);\n'
        for name in helpers+['c_'+n for n in names]:text+=re.sub(r'\bc_(\w+)\b',r'l1_\1',function(raw,name))
        for name in helpers+['READ','WRITE','A','W','DESC','R','B','F']:text+=f'#undef {name}\n'
    for path in [ROOT/'native/passenger_delivery.c',ROOT/'native/actor_resources.c',ROOT/'native/level_view.c',ROOT/'native/contacts.c']:
        text+=f'#include "{path.as_posix()}"\n'
    text+='static unsigned native_item_calls;\n'
    raw=(ROOT/'native/items.c').read_text();body=function(raw,'items_spawn')
    text+=raw.replace(body,body.replace('{','{ native_item_calls++;',1))
    text+=f'#include "{(ROOT/"native/bridge/actor_projection.h").as_posix()}"\n'
    raw=(ROOT/'native/bridge/actor_resources_bridge.c').read_text()
    for name in ['actor_read','actor_bridge_alias_project','actor_bridge_alias_read']:text+=function(raw,name)
    # Real contact bridge and geometry sampler, not a query model.
    raw=(ROOT/'native/bridge/level_view_bridge.c').read_text();text+=function(raw,'level_bridge_geometry')
    raw=(ROOT/'native/bridge/contacts_bridge.c').read_text()
    for name in ['contact_position','player_bridge','c_FindPlayerTouchingActor']:text+=function(raw,name)
    # Actual item allocation bridge (and its helpers); other item entries are
    # not referenced by this unit and are independently closed.
    raw=(ROOT/'native/bridge/items_bridge.c').read_text()
    for name in ['item_word','item_type','item_publish','item_ordinary','c_SpawnFallingItem']:text+=function(raw,name)
    text+='static unsigned dl_fallback;\n'
    bridge=BRIDGE.read_text().replace('#include "../passenger_delivery.h"','#include "'+(ROOT/'native/passenger_delivery.h').as_posix()+'"')
    bridge=bridge.replace('#include "actor_projection.h"','#include "'+(ROOT/'native/bridge/actor_projection.h').as_posix()+'"')
    for name in NAMES:bridge=bridge.replace(f'return l1_{name}(r)',f'return dl_fallback++, l1_{name}(r)')
    text+=bridge;(folder/'pair.inc').write_text(text)
    return [*SOURCES,ROOT/'c/actors.c',ROOT/'c/actors_states.c',ROOT/'c/items_water.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',
        ROOT/'native/actors.h',ROOT/'native/passenger_delivery.h',ROOT/'native/actor_resources.h',Path(__file__),ROOT/'verif/delivery_shells.py']
if __name__=='__main__':print(build())
