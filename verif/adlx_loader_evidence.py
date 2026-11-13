"""Actual-C generated header/reset/wrapper comparisons and negative control."""
import argparse,subprocess,time
from pathlib import Path
from closure_support import ROOT,function,compile_c,receipt,save
from adlx_loader_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--negative',action='store_true');a=p.parse_args()
    folder=OUT/('samples-negative' if a.negative else 'samples');folder.mkdir(parents=True,exist_ok=True)
    api=(ROOT/'c/sound_api.c').read_text();analysis=(ROOT/'c/music_analysis.c').read_text();bridge=(ROOT/'native/bridge/adlx_loader_bridge.c').read_text()
    code='''#include "ugh.h"
#include <stdio.h>
#include <stdlib.h>
#define CHECK(c,m) do {if(!(c)){fprintf(stderr,"%s line%u\\n",m,__LINE__);exit(1);}} while(0)
static uint32_t seed=918357;
static uint16_t N16(void) {seed=seed*1664525u+1013904223u;return (uint16_t)(seed>>16);}
static uint8_t N8(void) {return (uint8_t)N16();}
static unsigned stages[7];
'''
    code+=api[:api.index('/* Word device mask;')]
    for name,source in [('LoadAdlibTrackData',api),('LoadAdlibChannel',api),('ResetAdlibTrackChannelCursor',analysis)]:
        code+=function(source,'c_'+name).replace('EXPORT int c_'+name+'(','EXPORT int reference_'+name+'(',1)
    code+=function((ROOT/'c/music_clock.c').read_text(),'c_SwapDwordByteOrder')
    bridge=bridge.replace('#include "../adlx_loader.h"','#include "adlx_loader.h"').replace('l1_LoadAdlibTrackData','reference_LoadAdlibTrackData')
    bridge=bridge.replace('if(result.stage!=AUDIO_ADLX_GATE)', 'stages[result.stage]++;\n if(result.stage!=AUDIO_ADLX_GATE)',1)
    code+=bridge
    native=(ROOT/'native/adlx_loader.c').read_text()
    if a.negative:native=native.replace('if(!parser_value) return 65535;','if((int16_t)parser_value<0 || !parser_value) return 65535;')
    code+=native
    (folder/'pair.inc').write_text(code)
    harness=folder/'harness.c';harness.write_text((ROOT/'verif/adlx_loader_harness.c').read_text().replace(',stages[7]',''))
    exe=folder/'harness.exe';built=compile_c([harness],exe,[ROOT/'c',ROOT/'native'],['-Wno-unused-function'])
    start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
    inputs=[Path(__file__),ROOT/'verif/adlx_loader_harness.c',ROOT/'native/adlx_loader.c',ROOT/'native/adlx_loader.h',ROOT/'native/bridge/adlx_loader_bridge.c',ROOT/'native/audio.h',ROOT/'c/sound_api.c',ROOT/'c/music_analysis.c',ROOT/'c/music_clock.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h']
    save(OUT/('samples-negative.json' if a.negative else 'samples.json'),receipt(["python","verif/adlx_loader_evidence.py",*(['--negative'] if a.negative else [])],inputs,
        result='PASS' if run.returncode==0 else 'FAIL',bound=30000,cases=None if a.negative else 30000,build=built,execution=[str(exe)],seconds=time.perf_counter()-start,stdout=run.stdout,stderr=run.stderr))
    print(run.stdout+run.stderr,flush=True);assert (run.returncode!=0) if a.negative else (run.returncode==0)
if __name__=='__main__':main()
