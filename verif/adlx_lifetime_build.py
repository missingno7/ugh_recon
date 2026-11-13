"""Compiled eight-unit audio chain, or lifetime-only adapters over literal peers."""
import os,re
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
OUT=ROOT/'build/workers/close-adlx-8'
UNITS=['main','effects','allocation','loader','sections','music','voice','lifetime']
NAMES=['ClearSoundState','InitializeAdlibPlayback','ShutdownAdlibPlayback','CalibrateSoundDelay','BeginSoundDelayMeasurement','FinishSoundDelayMeasurement']
def build(reference=False,lifetime_only=False):
    units=['lifetime'] if lifetime_only else UNITS
    folder=OUT/f'{"reference" if reference else "lifetime" if lifetime_only else "variant"}_{os.getpid()}'
    folder.mkdir(parents=True,exist_ok=True);sources=[];inputs=[]
    bridges=[ROOT/'native/bridge'/f'adlx_{u}_bridge.c' for u in units]
    names=[n for p in bridges for n in re.findall(r'EXPORT int c_(\w+)\(',p.read_text())]
    for p in sorted((ROOT/'c').glob('*.c')):
        text=p.read_text();original=text
        if not reference:
            for n in names:text=re.sub(r'(EXPORT int )c_'+n+r'(?=\()',r'\1l1_'+n,text)
        if text!=original:
            target=folder/p.name;target.write_text(text);sources.append(target)
        else:sources.append(p)
        inputs.append(p)
    if not reference:
        for p in bridges:
            text=p.read_text();inputs.append(p)
            for u in UNITS:text=text.replace(f'#include "../adlx_{u}.h"',f'#include "{(ROOT/"native"/f"adlx_{u}.h").as_posix()}"')
            if p.name=='adlx_lifetime_bridge.c':
                text=text.replace('static void lifetime_push','EXPORT uint32_t adlx_lifetime_audit[16];\nstatic void lifetime_push',1)
                for i,n in enumerate(NAMES):
                    body=function(text,'c_'+n);text=text.replace(body,body.replace('{',f'{{adlx_lifetime_audit[{i}]++;',1))
                text=text.replace('AudioCalibrationAction before=work.action;','AudioCalibrationAction before=work.action;adlx_lifetime_audit[6+(before==AUDIO_CALIBRATION_WAIT_LOOP)]++;')
                text=text.replace('switch(request.action) {','adlx_lifetime_audit[8+(request.action==AUDIO_LIFETIME_READ)]++;switch(request.action) {',1)
            if p.name=='adlx_effects_bridge.c':
                # Existing integration runner expects this audit interface.
                text=text.replace('static int effects_bridge_literal','EXPORT uint32_t adlx_effects_audit[32];\nstatic int effects_bridge_literal',1)
                text=text.replace('AudioState state;','adlx_effects_audit[16]++;AudioState state;',1)
            target=folder/p.name;target.write_text(text);sources.append(target)
        for u in units:sources.append(ROOT/'native'/f'adlx_{u}.c');inputs.extend([ROOT/'native'/f'adlx_{u}.c',ROOT/'native'/f'adlx_{u}.h'])
    dll=folder/'adlx.dll';result=compile_c(sources,dll,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared'])
    result['maintained_inputs']=hashes([*inputs,*sorted((ROOT/'c').glob('*.h')),ROOT/'native/audio.h',ROOT/'native/bridge/audio_projection.h',Path(__file__)])
    save(OUT/('reference-build.json' if reference else 'lifetime-build.json' if lifetime_only else 'build.json'),result);return dll
if __name__=='__main__':print(build())
