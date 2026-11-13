"""Compile the independent six literal bodies and native adapters together."""
import argparse,re,subprocess,time
from pathlib import Path
from closure_support import ROOT,function,compile_c,receipt,save
from adlx_lifetime_build import OUT,NAMES
def pair_code(negative=None):
    adlib=(ROOT/'c/adlib.c').read_text();engine=(ROOT/'c/sound_engine.c').read_text()
    code='#include "platform.h"\n#include "adlx_lifetime.h"\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#define CHECK(c,m) do {if(!(c)){fprintf(stderr,"%s line%u case%u operation%u\\n",m,__LINE__,case_number,operation);exit(1);}} while(0)\nstatic unsigned case_number,operation;\n'
    for n in NAMES:code+='int reference_'+n+'(Regs *r);\n'
    for n in ['push','call','al','bh','emit','delay','c_WriteAdlibRegister','c_SilenceAdlibOperators']:code+=function(adlib,n)
    code+=function(engine,'c_DelaySoundIo')
    for n in NAMES:
        source=(ROOT/'c/sound_state.c').read_text() if n=='ClearSoundState' else engine if n in NAMES[3:] else adlib
        code+=function(source,'c_'+n).replace('c_'+n,'reference_'+n,1)
    bridge=(ROOT/'native/bridge/adlx_lifetime_bridge.c').read_text().replace('#include "../adlx_lifetime.h"','#include "adlx_lifetime.h"')
    native=(ROOT/'native/adlx_lifetime.c').read_text()
    mutations={'reset':('state->fade.scheduled=0','state->fade.scheduled=1'),'probe':('if(!(reply&224u))','if((reply&224u)!=192u)'),'measure':('AudioMeasurement result={remaining,progress}','AudioMeasurement result={remaining,(uint16_t)(progress+1u)}')}
    if negative:
        old,new=mutations[negative];changed=native.replace(old,new);assert changed!=native;native=changed
    return code+bridge+native
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--negative',choices=['reset','probe','measure']);p.add_argument('--exhaustive-probe',action='store_true');a=p.parse_args()
    folder=OUT/('samples-'+a.negative if a.negative else 'probe-enumeration' if a.exhaustive_probe else 'samples');folder.mkdir(parents=True,exist_ok=True)
    (folder/'pair.inc').write_text(pair_code(a.negative))
    harness=folder/'harness.c';harness.write_text((ROOT/'verif/adlx_lifetime_harness.c').read_text());exe=folder/'harness.exe'
    built=compile_c([harness],exe,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-Wno-unused-function',*(['-DEXHAUSTIVE_PROBE'] if a.exhaustive_probe else [])])
    started=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
    save(OUT/(folder.name+'.json'),receipt(['python','verif/adlx_lifetime_evidence.py',*(['--negative',a.negative] if a.negative else []),*(['--exhaustive-probe'] if a.exhaustive_probe else [])],[Path(__file__),ROOT/'verif/adlx_lifetime_harness.c',ROOT/'native/adlx_lifetime.c',ROOT/'native/adlx_lifetime.h',ROOT/'native/bridge/adlx_lifetime_bridge.c',ROOT/'native/audio.h',ROOT/'native/bridge/audio_projection.h',ROOT/'c/adlib.c',ROOT/'c/sound_engine.c',ROOT/'c/sound_state.c'],result='FAIL' if run.returncode else 'PASS',expected_failure=bool(a.negative),build=built,seconds=time.perf_counter()-started,stdout=run.stdout,stderr=run.stderr))
    print(run.stdout+run.stderr,flush=True);assert (run.returncode!=0) if a.negative else (run.returncode==0)
if __name__=='__main__':main()
