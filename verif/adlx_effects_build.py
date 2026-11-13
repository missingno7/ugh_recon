"""Combined accepted main + new effects bridge; generated copies only."""
import os,re,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
sys.path.insert(0,str(ROOT/'tools'))
OUT=ROOT/'build/workers/close-adlx-2'
BRIDGE=ROOT/'native/bridge/adlx_effects_bridge.c'
MAIN_BRIDGE=ROOT/'native/bridge/adlx_main_bridge.c'
NAMES=re.findall(r'EXPORT int c_(\w+)\(',BRIDGE.read_text())
MAIN_NAMES=re.findall(r'EXPORT int c_(\w+)\(',MAIN_BRIDGE.read_text())

def build(reference=False):
    folder=OUT/f'{"reference" if reference else "variant"}_{os.getpid()}'
    folder.mkdir(parents=True,exist_ok=True);sources=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        text=path.read_text();changed=False
        if not reference:
            for name in NAMES+MAIN_NAMES:
                text,n=re.subn(r'(EXPORT int )c_'+name+r'(?=\()',r'\1l1_'+name,text);changed|=bool(n)
        if changed:
            generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    if not reference:
        text=BRIDGE.read_text().replace('#include "../adlx_effects.h"','#include "'+(ROOT/'native/adlx_effects.h').as_posix()+'"')
        text=text.replace('static int effects_bridge_literal','EXPORT uint32_t adlx_effects_audit[32];\nstatic int effects_bridge_literal',1)
        text=text.replace('switch(operation) {','adlx_effects_audit[17]++;\n    switch(operation) {',1)
        text=text.replace('AudioState state;','adlx_effects_audit[16]++;\n    AudioState state;',1)
        text=text.replace('return l1_RunEffectAdlxEvents(r);','return adlx_effects_audit[18]++, l1_RunEffectAdlxEvents(r);')
        text=text.replace('if(result.stop_request) {','if(result.stop_request) { adlx_effects_audit[19]++;',1)
        text=text.replace('if(result.timer_request) {','if(result.timer_request) { adlx_effects_audit[20]++;',1)
        text=text.replace('{r->bx=state.timer_period;return UGH_UNSUPPORTED;}','{adlx_effects_audit[21]++;r->bx=state.timer_period;return UGH_UNSUPPORTED;}',1)
        for i,name in enumerate(NAMES):
            body=function(text,'c_'+name);text=text.replace(body,body.replace('{',f'{{ adlx_effects_audit[{i}]++;',1))
        generated=folder/'adlx_effects_bridge.c';generated.write_text(text)
        sources += [ROOT/'native/adlx_main.c',MAIN_BRIDGE,ROOT/'native/adlx_effects.c',generated]
    dll=folder/'adlx.dll'
    result=compile_c(sources,dll,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared'])
    result['maintained_inputs']=hashes([BRIDGE,MAIN_BRIDGE,ROOT/'native/adlx_main.c',ROOT/'native/adlx_effects.c',
        ROOT/'native/audio.h',ROOT/'native/adlx_main.h',ROOT/'native/adlx_effects.h',ROOT/'native/bridge/audio_projection.h',
        *sorted((ROOT/'c').glob('*.[ch]')),Path(__file__)])
    save(OUT/('reference-build.json' if reference else 'build.json'),result);return dll
if __name__=='__main__':print(build())
