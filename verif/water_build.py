"""Water plus accepted itinerary/delivery/contact/item bridges, in owned scratch."""
import os,re,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
from water_shells import NAMES,ENTRIES,BRIDGE
import delivery_build,itinerary_build
OUT=ROOT/'build/workers/close-stones-5'
WATER_SOURCES=[ROOT/'native/passenger_water.c',BRIDGE]
SOURCES=list(dict.fromkeys([*WATER_SOURCES,*delivery_build.SOURCES,*itinerary_build.SOURCES]))

def includes(text,path):
    return re.sub(r'#include "([^"]+)"',lambda m:'#include "'+(path.parent/m[1]).resolve().as_posix()+'"' if (path.parent/m[1]).is_file() else m[0],text)

def build():
    folder=OUT/f'variant_{os.getpid()}';folder.mkdir(parents=True,exist_ok=True);sources=[]
    replacements=list(dict.fromkeys([*NAMES,*delivery_build.NAMES,*itinerary_build.NAMES,*delivery_build.CONTACTS,*delivery_build.ITEMS]))
    for path in sorted((ROOT/'c').glob('*.c')):
        text=path.read_text();changed=False
        for name in replacements:text,n=re.subn(r'(EXPORT int )c_'+name+r'(?=\()',r'\1l1_'+name,text);changed|=bool(n)
        if changed:generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    for path in SOURCES:
        if path==BRIDGE:
            text=includes(path.read_text(),path).replace('typedef struct WaterPlan','EXPORT uint32_t water_audit[20];\ntypedef struct WaterPlan',1)
            for i,name in enumerate(NAMES):
                body=function(text,'c_'+name);new=body.replace('{',f'{{water_audit[{i}]++;',1).replace('l1_'+name+'(r)',f'(water_audit[{i+10}]++,l1_{name}(r))');text=text.replace(body,new)
            generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    dll=folder/'water.dll';result=compile_c(sources,dll,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared','-DACTOR_VERIFY'])
    result['maintained_inputs']=hashes([*SOURCES,Path(__file__),*sorted((ROOT/'c').glob('*.[ch]')),*[ROOT/'native'/n for n in ['actors.h','actor_resources.h','passenger_water.h','passenger_delivery.h','passenger_itinerary.h']]])
    save(OUT/'build.json',result);return dll

def pair(folder):
    folder.mkdir(parents=True,exist_ok=True);raw=(ROOT/'c/actors.c').read_text()
    text='#include "'+(ROOT/'c/ugh.h').as_posix()+'"\n'
    text+='uint16_t wa_read(uint16_t,uint16_t);void wa_write(uint16_t,uint16_t,uint16_t);\n#define rd16 wa_read\n#define wr16 wa_write\n'
    helpers=['shl','sar','inc','less','greater','actor_init','actor_frame','actor_tick','surface_y','state_jump','tail']
    for name in helpers:text+='#define '+name+' wa_ref_'+name+'\n'
    text+='\n'.join(line for line in raw.splitlines() if line.startswith('#define '))+'\nstatic int state_jump(Regs *,uint16_t);static int tail(Regs *,unsigned);\n'
    for name in helpers+['c_'+n for n in NAMES]:text+=re.sub(r'\bc_(\w+)\b',r'l1_\1',function(raw,name))
    for name in helpers+['READ','WRITE','A','W','DESC']:text+='#undef '+name+'\n'
    for name in ['passenger_water.c','actor_resources.c','level_view.c']:text+='#include "'+(ROOT/'native'/name).as_posix()+'"\n'
    text+='#include "'+(ROOT/'native/bridge/actor_projection.h').as_posix()+'"\n'
    source=(ROOT/'native/bridge/actor_resources_bridge.c').read_text()
    for name in ['actor_read','actor_bridge_alias_project','actor_bridge_alias_read']:text+=function(source,name)
    text+='static unsigned wa_fallback;\n';bridge=includes(BRIDGE.read_text(),BRIDGE)
    for name in NAMES:bridge=bridge.replace('return l1_'+name+'(r)','return wa_fallback++,l1_'+name+'(r)')
    text+=bridge;(folder/'pair.inc').write_text(text)
    return [*WATER_SOURCES,ROOT/'native/passenger_water.h',ROOT/'native/actors.h',ROOT/'native/actor_resources.h',ROOT/'native/actor_resources.c',ROOT/'native/level_view.c',ROOT/'native/bridge/actor_resources_bridge.c',ROOT/'native/bridge/actor_projection.h',ROOT/'c/actors.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',ROOT/'verif/water_shells.py',Path(__file__)]
if __name__=='__main__':print(build())
