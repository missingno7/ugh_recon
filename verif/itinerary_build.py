"""Isolated passenger itinerary bridge and actual-L1 relational extraction."""
import os,re,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
from itinerary_shells import NAMES,ENTRIES,BRIDGE
sys.path.insert(0,str(ROOT/'tools'))
OUT=ROOT/'build/workers/close-stones-2'
SOURCES=[ROOT/'native/passenger_itinerary.c',BRIDGE,ROOT/'native/actor_resources.c',ROOT/'native/bridge/actor_resources_bridge.c',
         ROOT/'native/coordinate_scale.c',ROOT/'native/level_view.c',ROOT/'native/bridge/level_view_bridge.c']
def build():
    folder=OUT/f'variant_{os.getpid()}';folder.mkdir(parents=True,exist_ok=True);sources=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        text=path.read_text();changed=False
        for name in NAMES:
            text,n=re.subn(r'(EXPORT int )c_'+name+r'(?=\()',r'\1l1_'+name,text);changed|=bool(n)
        if changed:
            generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    text=BRIDGE.read_text().replace('#include "../passenger_itinerary.h"','#include "'+(ROOT/'native/passenger_itinerary.h').as_posix()+'"')
    text=text.replace('typedef struct ItineraryPlan','EXPORT uint32_t itinerary_audit[16];\ntypedef struct ItineraryPlan',1)
    for i,name in enumerate(NAMES):
        body=function(text,'c_'+name);new=body.replace('{',f'{{ itinerary_audit[{i}]++;',1)
        new=new.replace(f'l1_{name}(r)',f'(itinerary_audit[{i+8}]++,l1_{name}(r))');text=text.replace(body,new)
    generated=folder/'passenger_itinerary_bridge.c';generated.write_text(text)
    dll=folder/'itinerary.dll';result=compile_c(sources+[p for p in SOURCES if p!=BRIDGE]+[generated],dll,
        [ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared','-DACTOR_VERIFY'])
    result['maintained_inputs']=hashes([*SOURCES,Path(__file__),*sorted((ROOT/'c').glob('*.[ch]')),*sorted((ROOT/'native').rglob('*.h'))])
    save(OUT/'build.json',result);return dll
def pair(folder):
    folder.mkdir(parents=True,exist_ok=True)
    text=f'#include "{(ROOT/"c/ugh.h").as_posix()}"\n'
    text+='uint16_t it_read(uint16_t,uint16_t);void it_write(uint16_t,uint16_t,uint16_t);uint8_t it_byte(uint16_t,uint16_t);void it_byte_write(uint16_t,uint16_t,uint8_t);\n'
    text+='#define rd16 it_read\n#define wr16 it_write\n#define rd8 it_byte\n#define wr8 it_byte_write\n'
    groups=[('actors.c',['shl','sar','less','actor_init','actor_tick','actor_frame','state_jump','tail'],NAMES[1:]+['BeginPassengerPlatformWait']),
            ('actors_states.c',['shift','byte_sub','byte_dec'],NAMES[:1])]
    for group,(module,helpers,names) in enumerate(groups):
        raw=(ROOT/'c'/module).read_text()
        for name in helpers:text+=f'#define {name} it_ref{group}_{name}\n'
        text+='\n'.join(line for line in raw.splitlines() if line.startswith('#define '))+'\n'
        if group==0:text+='static int state_jump(Regs *,uint16_t);static int tail(Regs *,unsigned);\n'
        for name in helpers+['c_'+n for n in names]:
            text+=re.sub(r'\bc_(\w+)\b',r'l1_\1',function(raw,name))
        for name in helpers+['READ','WRITE','A','W','DESC','R','B','F']:text+=f'#undef {name}\n'
    raw=(ROOT/'c/render_primitives.c').read_text()
    for name in ['sar_word','c_ScaleLevelSpeedToThreeHalves']:text+=function(raw,name).replace('c_ScaleLevelSpeedToThreeHalves','l1_ScaleLevelSpeedToThreeHalves')
    for path in [ROOT/'native/passenger_itinerary.c',ROOT/'native/actor_resources.c',ROOT/'native/coordinate_scale.c',ROOT/'native/level_view.c']:
        text+=f'#include "{path.as_posix()}"\n'
    text+=f'#include "{(ROOT/"native/bridge/actor_projection.h").as_posix()}"\n'
    raw=(ROOT/'native/bridge/actor_resources_bridge.c').read_text()
    for name in ['actor_read','actor_bridge_journey','actor_bridge_alias_project','actor_bridge_alias_read']:text+=function(raw,name)
    text+='static unsigned it_fallback;\n'
    bridge=BRIDGE.read_text().replace('#include "../passenger_itinerary.h"','#include "'+(ROOT/'native/passenger_itinerary.h').as_posix()+'"')
    bridge=bridge.replace('#include "actor_projection.h"','#include "'+(ROOT/'native/bridge/actor_projection.h').as_posix()+'"')
    for name in NAMES[:-1]:bridge=bridge.replace(f'return l1_{name}(r)',f'return it_fallback++, l1_{name}(r)')
    text+=bridge;(folder/'pair.inc').write_text(text)
    return [*SOURCES,ROOT/'c/actors.c',ROOT/'c/actors_states.c',ROOT/'c/render_primitives.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',
            ROOT/'native/actors.h',ROOT/'native/passenger_itinerary.h',ROOT/'native/actor_resources.h',Path(__file__),ROOT/'verif/itinerary_shells.py']
if __name__=='__main__':print(build())
