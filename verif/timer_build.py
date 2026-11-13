"""Isolated timer bridge build; no generated or maintained L1 edits."""
import os,re,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
sys.path.insert(0,str(ROOT/'tools'))
import nbuild
OUT=ROOT/'build/workers/close-timer'
REPLACE={'timer.c':['RegisterTimerCallback','HandleTimerInterrupt'],
         'timer_system.c':['RemoveTimerCallback','SetTimerCallbackInterval']}

def build():
    folder=OUT/f'variant_{os.getpid()}';folder.mkdir(parents=True,exist_ok=True)
    sources=[];inputs=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        inputs.append(path)
        if path.name in REPLACE:
            text=path.read_text()
            for name in REPLACE[path.name]:text=re.sub(r'\bc_'+name+r'\b','l1_'+name,text)
            generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    bridge=ROOT/'native/bridge/timer_bridge.c'
    text=bridge.read_text()
    for index,name in enumerate(['RegisterTimerCallback','RemoveTimerCallback','SetTimerCallbackInterval','HandleTimerInterrupt']):
        body=function(text,'c_'+name)
        audited=body.replace('return l1_'+name+'(r);',f'return timer_audit[{index*2+1}]++, l1_{name}(r);')
        # Native hits count only after the guard, not wrapper entry.
        marker={'RegisterTimerCallback':'timer_publish(&state,open); r->ax=',
                'RemoveTimerCallback':'r->ax=timer_remove',
                'SetTimerCallbackInterval':'timer_set_interval(&state',
                'HandleTimerInterrupt':'TimerTickScratch scratch='}[name]
        audited=audited.replace(marker,f'timer_audit[{index*2}]++; '+marker)
        text=text.replace(body,audited)
    text=text.replace('#include "../timer.h"','#include "'+(ROOT/'native/timer.h').as_posix()+'"')
    generated=folder/'timer_bridge.c'
    generated.write_text(text.replace('int l1_RegisterTimerCallback','EXPORT uint32_t timer_audit[8];\nint l1_RegisterTimerCallback',1))
    sources += [ROOT/'native/timer.c',generated]
    inputs.append(bridge)
    dll=folder/'timer.dll'
    result=compile_c(sources,dll,[ROOT/'c',ROOT/'native'],['-shared'])
    result['maintained_inputs']=hashes([*inputs,ROOT/'native/timer.h',Path(__file__),
        *sorted((ROOT/'c').glob('*.h')),*sorted((ROOT/'c').glob('*.inc'))])
    save(OUT/'build.json',result)
    return dll

if __name__=='__main__':print(build())
