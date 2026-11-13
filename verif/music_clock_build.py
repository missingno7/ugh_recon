"""Isolated music-clock bridge build using the shared closure compiler."""
import os,re,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
sys.path.insert(0,str(ROOT/'tools'))
import nbuild

OUT=ROOT/'build/workers/close-musicclock'
NAMES=['SwapDwordByteOrder','DisableMusicSectionLoop','GetElapsedMusicTime']

def build():
    folder=OUT/f'variant_{os.getpid()}';folder.mkdir(parents=True,exist_ok=True)
    sources=[];inputs=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        inputs.append(path)
        if path.name=='music_clock.c':
            text=path.read_text()
            for name in NAMES:text=re.sub(r'\bc_'+name+r'\b','l1_'+name,text)
            generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    bridge=ROOT/'native/bridge/music_clock_bridge.c';text=bridge.read_text()
    for index,name in enumerate(NAMES):
        body=function(text,'c_'+name)
        text=text.replace(body,body.replace('{',f'{{ music_clock_audit[{index}]++;',1))
    text=text.replace('#include "../music_clock.h"','#include "'+(ROOT/'native/music_clock.h').as_posix()+'"')
    text=text.replace('EXPORT int c_SwapDwordByteOrder','EXPORT uint32_t music_clock_audit[3];\nEXPORT int c_SwapDwordByteOrder',1)
    generated=folder/'music_clock_bridge.c';generated.write_text(text)
    sources += [ROOT/'native/music_clock.c',generated]
    dll=folder/'music_clock.dll'
    result=compile_c(sources,dll,[ROOT/'c',ROOT/'native'],['-shared'])
    result['maintained_inputs']=hashes([*inputs,bridge,ROOT/'native/music_clock.c',ROOT/'native/music_clock.h',Path(__file__),
        *sorted((ROOT/'c').glob('*.h')),*sorted((ROOT/'c').glob('*.inc'))])
    save(OUT/'build.json',result)
    return dll

if __name__=='__main__':print(build())
