"""Isolated audio variant; shared builders and maintained L1 remain unchanged."""
import os,re,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
sys.path.insert(0,str(ROOT/'tools'))
OUT=ROOT/'build/workers/close-adlx'
BRIDGE=ROOT/'native/bridge/adlx_main_bridge.c'
NAMES=re.findall(r'EXPORT int c_(\w+)\(',BRIDGE.read_text())

def build(reference=False):
    folder=OUT/f'{"reference" if reference else "variant"}_{os.getpid()}'
    folder.mkdir(parents=True,exist_ok=True);sources=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        text=path.read_text();changed=False
        if not reference:
            for name in NAMES:
                text,n=re.subn(r'(EXPORT int )c_'+name+r'(?=\()',r'\1l1_'+name,text);changed|=bool(n)
        if changed:
            generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    if not reference:
        text=BRIDGE.read_text().replace('#include "../adlx_main.h"','#include "'+(ROOT/'native/adlx_main.h').as_posix()+'"')
        text=text.replace('static void audio_bridge_delay','EXPORT uint32_t adlx_main_audit[32];\nstatic void audio_bridge_delay',1)
        text=text.replace('AudioState state;','adlx_main_audit[16]++;\n    AudioState state;',1)
        text=text.replace('return l1_HandleMainAdlxInstrument(r);','return adlx_main_audit[17]++, l1_HandleMainAdlxInstrument(r);')
        text=text.replace('return l1_RunMainAdlxEvents(r);','return adlx_main_audit[18]++, l1_RunMainAdlxEvents(r);')
        for i,name in enumerate(NAMES):
            body=function(text,'c_'+name);text=text.replace(body,body.replace('{',f'{{ adlx_main_audit[{i}]++;',1))
        generated=folder/'adlx_main_bridge.c';generated.write_text(text)
        sources += [ROOT/'native/adlx_main.c',generated]
    dll=folder/'adlx.dll'
    result=compile_c(sources,dll,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared'])
    result['maintained_inputs']=hashes([BRIDGE,ROOT/'native/adlx_main.c',*sorted((ROOT/'c').glob('*.[ch]')),
        ROOT/'native/audio.h',ROOT/'native/adlx_main.h',ROOT/'native/bridge/audio_projection.h',Path(__file__)])
    save(OUT/('reference-build.json' if reference else 'build.json'),result);return dll

if __name__=='__main__':print(build())
