"""Actual compiled standalone drivers versus native adapters, including aliases."""
import argparse,re,subprocess,time
from pathlib import Path
from closure_support import ROOT,function,compile_c,receipt,save
from adlx_voice_build import OUT
NAMES=['SetAdlibChannelVolume','SetAdlibChannelGain','KeyOffAdlibChannel','SetAdlibFrequency','LoadAdlibInstrument','WriteAdlibRegister','DelaySoundIo']
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--negative',choices=['source','gain','delay']);p.add_argument('--exhaustive-delay',action='store_true');a=p.parse_args()
    folder=OUT/('samples-'+a.negative if a.negative else 'delay-enumeration' if a.exhaustive_delay else 'samples');folder.mkdir(parents=True,exist_ok=True)
    literal=(ROOT/'c/adlib.c').read_text();engine=(ROOT/'c/sound_engine.c').read_text()
    code='#include "platform.h"\n#include "adlx_voice.h"\n#include <stdio.h>\n#include <stdlib.h>\n#define CHECK(c,m) do {if(!(c)){fprintf(stderr,"%s line%u\\n",m,__LINE__);exit(1);}} while(0)\n'
    code+=''.join('int reference_'+name+'(Regs *r);\n' for name in NAMES)
    delay=function(engine,'c_DelaySoundIo')
    if a.exhaustive_delay:
        code+='uint32_t reference_iterations;\n'
        delay=delay.replace('    uint16_t remaining=product;','    reference_iterations=0;uint16_t remaining=product;').replace('do { remaining=(uint16_t)(remaining-1); }','do { reference_iterations++;remaining=(uint16_t)(remaining-1); }')
    code+=literal[:literal.index('/* No stack args.')]+delay
    for name in NAMES:code=re.sub(r'\bc_'+name+r'\b','reference_'+name,code)
    code+=(ROOT/'native/bridge/adlx_voice_bridge.c').read_text().replace('#include "../adlx_voice.h"','#include "adlx_voice.h"').replace('l1_LoadAdlibInstrument','reference_LoadAdlibInstrument')
    main=(ROOT/'native/adlx_main.c').read_text()
    if a.negative=='gain':
        changed=main.replace('if(state->current_channel>=12 && (state->reserved_voices&15u) && channel>=first)','if((state->playing&1u) && state->current_channel>=12 && (state->reserved_voices&15u) && channel>=first)');assert changed!=main;main=changed
    code+=main
    native=(ROOT/'native/adlx_voice.c').read_text()
    if a.negative=='source':
        changed=native.replace('programmed[i]=voice_source_byte(state,source,result->channel,i)','programmed[i]=((void)source,state->live[result->channel].instrument[i])');assert changed!=native;native=changed
    if a.negative=='delay':
        changed=native.replace('(uint8_t)(product>255)','(uint8_t)(product>=255)');assert changed!=native;native=changed
    code+=native;(folder/'pair.inc').write_text(code)
    harness=folder/'harness.c';harness.write_text((ROOT/'verif/adlx_voice_harness.c').read_text());exe=folder/'harness.exe'
    built=compile_c([harness],exe,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-Wno-unused-function',*(['-DEXHAUSTIVE_DELAY'] if a.exhaustive_delay else [])])
    started=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
    save(OUT/(folder.name+'.json'),receipt(['python','verif/adlx_voice_evidence.py',*(['--negative',a.negative] if a.negative else []),*(['--exhaustive-delay'] if a.exhaustive_delay else [])],[Path(__file__),ROOT/'verif/adlx_voice_harness.c',ROOT/'native/adlx_voice.c',ROOT/'native/adlx_voice.h',ROOT/'native/bridge/adlx_voice_bridge.c',ROOT/'native/adlx_main.c',ROOT/'native/audio.h',ROOT/'c/adlib.c',ROOT/'c/sound_engine.c'],result='FAIL' if run.returncode else 'PASS',expected_failure=bool(a.negative),build=built,seconds=time.perf_counter()-started,stdout=run.stdout,stderr=run.stderr))
    print(run.stdout+run.stderr,flush=True);assert (run.returncode!=0) if a.negative else (run.returncode==0)
if __name__=='__main__':main()
