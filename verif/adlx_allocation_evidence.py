"""Actual-C differential harness for allocation, stop and restoration."""
import argparse,re,subprocess,time
from pathlib import Path
from closure_support import ROOT,function,compile_c,receipt,save
from adlx_allocation_build import OUT
INPUTS=[ROOT/'c'/n for n in ['sound_api.c','adlib.c','sound_engine.c','game_services.c','ugh.h','ugh_sym.h','platform.h']]+[ROOT/'native'/n for n in ['adlx_allocation.c','adlx_allocation.h','adlx_main.c','adlx_main.h','audio.h','bridge/adlx_allocation_bridge.c','bridge/audio_projection.h']]+[Path(__file__),ROOT/'verif/adlx_allocation_harness.c']
def pair(folder,negative=False):
    folder.mkdir(parents=True,exist_ok=True)
    api=(ROOT/'c/sound_api.c').read_text();driver=(ROOT/'c/adlib.c').read_text();engine=(ROOT/'c/sound_engine.c').read_text()
    prefix=driver[:driver.index('/* No stack args.')]
    for name in ['push','call','args_call','inc','al','bl','bh','emit','delay']:
        prefix=re.sub(r'\b'+name+r'\b','driver_'+name,prefix)
    delay=function(engine,'c_DelaySoundIo');loop='    uint16_t remaining=product;\n    do { remaining=(uint16_t)(remaining-1); } while(remaining);\n'
    assert loop in delay;delay=delay.replace(loop,'    /* Terminating busy loop has no state effects. */\n')
    code='''#include "platform.h"
#include <stdio.h>
#include <stdlib.h>
#define CHECK(c,m) do {if(!(c)){fprintf(stderr,"%s at %u\\n",m,__LINE__);exit(1);}} while(0)
static uint32_t seed=38517;
static uint16_t N16(void) {seed=seed*1664525u+1013904223u;return (uint16_t)(seed>>16);}
static uint8_t N8(void) {return (uint8_t)N16();}
'''
    code+=prefix+delay+function((ROOT/'c/game_services.c').read_text(),'c_CopyFarBytes')
    code+=api[:api.index('/* Word device mask;')]
    for name in ['StopAdlibTrackChannel','RestoreAdlibVoiceAllocation','StartAdlibTrackChannel']:
        code+=function(api,'c_'+name).replace('EXPORT int c_'+name+'(','EXPORT int reference_'+name+'(',1)
    bridge=(ROOT/'native/bridge/adlx_allocation_bridge.c').read_text().split('/* Parsing remains')[0]
    bridge=bridge.replace('#include "../adlx_allocation.h"',f'#include "{(ROOT/"native/adlx_allocation.h").as_posix()}"')
    for name in ['StopAdlibTrackChannel','RestoreAdlibVoiceAllocation','StartAdlibTrackChannel']:
        code=code.replace('reference_'+name+'(', 'reference_'+name+'(')
        bridge=bridge.replace('l1_'+name,'reference_'+name)
    bridge='static unsigned native_counts[3],literal_counts[3];\n'+bridge
    bridge=bridge.replace('if(operation==AUDIO_ALLOCATION_STOP) return reference_', 'literal_counts[operation]++;\n if(operation==AUDIO_ALLOCATION_STOP) return reference_',1)
    bridge=bridge.replace('AllocationFrame frame=allocation_enter(r,operation','native_counts[operation]++;\n AllocationFrame frame=allocation_enter(r,operation',1)
    native=ROOT/'native/adlx_allocation.c'
    if negative:
        native=folder/'mutant.c';native.write_text((ROOT/'native/adlx_allocation.c').read_text().replace('state->current_channel=12;dest->owner=12;','state->current_channel=channel;dest->owner=12;'))
    code+=bridge+'\n#include "'+(ROOT/'native/adlx_main.c').as_posix()+'"\n#include "'+native.as_posix()+'"\n'
    (folder/'pair.inc').write_text(code)
    harness=folder/'harness.c';harness.write_text((ROOT/'verif/adlx_allocation_harness.c').read_text());return harness
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--negative',action='store_true');a=p.parse_args()
    folder=OUT/('samples-negative' if a.negative else 'samples');harness=pair(folder,a.negative);exe=folder/'harness.exe'
    built=compile_c([harness],exe,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-Wno-unused-function'])
    start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
    result=receipt(['python','verif/adlx_allocation_evidence.py',*(['--negative'] if a.negative else [])],INPUTS,result='PASS' if run.returncode==0 else 'FAIL',cases=None if a.negative else 90000,bound=90000,
        build=built,execution=[str(exe)],seconds=time.perf_counter()-start,stdout=run.stdout,stderr=run.stderr)
    result['negative']=a.negative
    save(OUT/('samples-negative.json' if a.negative else 'samples.json'),result);print(run.stdout+run.stderr,flush=True)
    assert (run.returncode!=0) if a.negative else (run.returncode==0)
if __name__=='__main__':main()
