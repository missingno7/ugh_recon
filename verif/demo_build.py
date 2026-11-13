"""Build the three demo bridges in isolation; never regenerate L0/L1."""
import os,re,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
sys.path.insert(0,str(ROOT/'tools'))
OUT=ROOT/'build/workers/close-demo'
NAMES=['InitializeDemoScripts','AdvanceDemoScripts','TestAllDemoScriptsFinished']
SOURCES=[ROOT/'native/demo_core.c',ROOT/'native/actor_resources.c',
    ROOT/'native/bridge/demo_core_bridge.c',ROOT/'native/bridge/actor_resources_bridge.c',
    ROOT/'native/level_view.c',ROOT/'native/bridge/level_view_bridge.c']
def build(harness=True):
    folder=OUT/f'variant_{os.getpid()}';folder.mkdir(parents=True,exist_ok=True);sources=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        text=path.read_text();changed=False
        for name in NAMES:
            text,n=re.subn(r'(EXPORT int )c_'+name+r'(?=\()',r'\1l1_'+name,text);changed|=bool(n)
        if changed:
            generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    bridge=ROOT/'native/bridge/demo_core_bridge.c'
    text=bridge.read_text().replace('#include "../demo_core.h"','#include "'+(ROOT/'native/demo_core.h').as_posix()+'"')
    text=text.replace('int l1_InitializeDemoScripts','EXPORT uint32_t demo_audit[6];\nint l1_InitializeDemoScripts',1)
    for i,name in enumerate(NAMES):
        body=function(text,'c_'+name)
        body2=body.replace('{',f'{{ demo_audit[{i}]++;',1)
        body2=body2.replace(f'l1_{name}(r)',f'(demo_audit[{i+3}]++,l1_{name}(r))')
        text=text.replace(body,body2)
    generated=folder/'demo_core_bridge.c';generated.write_text(text)
    sources += [p for p in SOURCES if p!=bridge]+[generated]
    if harness:
        raw=(ROOT/'c/scene.c').read_text();body=function(raw,'c_RunGameFromPassword')
        marker='CALL(DispatchFallingItems,G(RunGameFromPassword)+0x1e0); '
        start=body.index(marker)+len(marker);end=body.index('        st=draw_enemy_layer(r,0);',start)
        text='#include "ugh.h"\n'+'\n'.join(line for line in raw.splitlines() if line.startswith('#define '))+'\n'
        text+=function(raw,'sar')+'int demo_actual_gameplay_draw(Regs *r) {\n'+body[start:end]+'return UGH_OK; }\n'
        generated_draw=folder/'gameplay_draw.c';generated_draw.write_text(text)
        sources += [ROOT/'verif/demo_harness.c',generated_draw]
    dll=folder/'demo.dll';result=compile_c(sources,dll,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared','-DACTOR_VERIFY'])
    result['maintained_inputs']=hashes([*SOURCES,Path(__file__),ROOT/'verif/demo_harness.c',
        *sorted((ROOT/'c').glob('*.[ch]')),*sorted((ROOT/'native').rglob('*.h'))])
    save(OUT/'build.json',result);return dll
if __name__=='__main__':print(build())
