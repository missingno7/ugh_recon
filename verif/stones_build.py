"""Build an isolated stone bridge and extract actual maintained L1 C."""
import os,re,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
sys.path.insert(0,str(ROOT/'tools'))
OUT=ROOT/'build/workers/close-stones'
NAMES=['BeginStonePickupWait','UpdateStonePickupWait','AttachStoneToPlayer','WaitForStoneRelease','ThrowCarriedStone','UpdateThrownStone']
BRIDGE=ROOT/'native/bridge/stones_bridge.c'
SOURCES=[ROOT/'native/stones.c',BRIDGE,ROOT/'native/actor_resources.c',ROOT/'native/bridge/actor_resources_bridge.c',
         ROOT/'native/level_view.c',ROOT/'native/bridge/level_view_bridge.c',ROOT/'native/contacts.c']
def build():
    folder=OUT/f'variant_{os.getpid()}';folder.mkdir(parents=True,exist_ok=True);sources=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        text=path.read_text();changed=False
        for name in NAMES:
            text,n=re.subn(r'(EXPORT int )c_'+name+r'(?=\()',r'\1l1_'+name,text);changed|=bool(n)
        if changed:
            generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    text=BRIDGE.read_text().replace('#include "../stones.h"','#include "'+(ROOT/'native/stones.h').as_posix()+'"')
    text=text.replace('int l1_BeginStonePickupWait','EXPORT uint32_t stones_audit[12];\nint l1_BeginStonePickupWait',1)
    for i,name in enumerate(NAMES):
        body=function(text,'c_'+name);new=body.replace('{',f'{{ stones_audit[{i}]++;',1)
        new=new.replace(f'l1_{name}(r)',f'(stones_audit[{i+6}]++,l1_{name}(r))');text=text.replace(body,new)
    generated=folder/'stones_bridge.c';generated.write_text(text)
    raw=(ROOT/'c/scene.c').read_text();body=function(raw,'c_RunGameFromPassword')
    marker='CALL(DispatchFallingItems,G(RunGameFromPassword)+0x1e0); '
    start=body.index(marker)+len(marker);end=body.index('        st=draw_enemy_layer(r,0);',start)
    draw='#include "ugh.h"\n'+'\n'.join(line for line in raw.splitlines() if line.startswith('#define '))+'\n'
    draw+=function(raw,'sar')+'int stones_actual_gameplay_draw(Regs *r) {\n'+body[start:end]+'return UGH_OK; }\n'
    generated_draw=folder/'gameplay_draw.c';generated_draw.write_text(draw)
    dll=folder/'stones.dll';result=compile_c(sources+[p for p in SOURCES if p!=BRIDGE]+[generated,generated_draw,ROOT/'verif/stones_cross_mode.c'],dll,
        [ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared','-DACTOR_VERIFY'])
    result['maintained_inputs']=hashes([*SOURCES,Path(__file__),ROOT/'verif/stones_cross_mode.c',*sorted((ROOT/'c').glob('*.[ch]')),*sorted((ROOT/'native').rglob('*.h'))])
    save(OUT/'build.json',result);return dll
def pair(folder):
    folder.mkdir(parents=True,exist_ok=True)
    text=f'#include "{(ROOT/"c/ugh.h").as_posix()}"\n'
    text+='uint16_t st_read(uint16_t,uint16_t);void st_write(uint16_t,uint16_t,uint16_t);uint8_t st_byte(uint16_t,uint16_t);\n'
    text+='#define rd16 st_read\n#define wr16 st_write\n#define rd8 st_byte\n'
    groups=[('actors.c',['state_jump','tail','shl','sar','less','greater','actor_init','contact'],
             ['BeginStonePickupWait','AttachStoneToPlayer','WaitForStoneRelease','UpdateThrownStone','FindPlayerTouchingActor']),
            ('actors_states.c',['tail','shift','push','pop','effect'],['UpdateStonePickupWait','ThrowCarriedStone'])]
    for group,(module,helpers,names) in enumerate(groups):
        raw=(ROOT/'c'/module).read_text()
        for name in helpers:text+=f'#define {name} ref{group}_{name}\n'
        text+='\n'.join(line for line in raw.splitlines() if line.startswith('#define '))+'\n'
        if group==0:text+='static int state_jump(Regs *,uint16_t);\n'
        for name in helpers+['c_'+n for n in names]:
            body=function(raw,name);body=re.sub(r'\bc_(\w+)\b',r'l1_\1',body);text+=body
        for name in helpers+['READ','WRITE','A','W','DESC','R','B','F']:text+=f'#undef {name}\n'
    for path in [ROOT/'native/stones.c',ROOT/'native/contacts.c',ROOT/'native/actor_resources.c',ROOT/'native/level_view.c']:
        text+=f'#include "{path.as_posix()}"\n'
    raw=(ROOT/'native/bridge/actor_resources_bridge.c').read_text()
    text+=f'#include "{(ROOT/"native/bridge/actor_projection.h").as_posix()}"\n'
    for name in ['actor_read','actor_bridge_alias_project','actor_bridge_alias_read']:text+=function(raw,name)
    text+='static unsigned st_fallback;\n'
    bridge=BRIDGE.read_text().replace('#include "../stones.h"','#include "'+(ROOT/'native/stones.h').as_posix()+'"')
    bridge=bridge.replace('#include "actor_projection.h"','#include "'+(ROOT/'native/bridge/actor_projection.h').as_posix()+'"')
    for name in NAMES:bridge=bridge.replace(f'return l1_{name}(r)',f'return st_fallback++, l1_{name}(r)')
    text+=bridge
    (folder/'pair.inc').write_text(text)
    return [*SOURCES,ROOT/'c/actors.c',ROOT/'c/actors_states.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',
            ROOT/'native/actors.h',ROOT/'native/stones.h',ROOT/'native/actor_resources.h',Path(__file__)]
if __name__=='__main__':print(build())
