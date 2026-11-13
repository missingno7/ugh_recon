"""Actual-C composition with real copies/voices and stateful tick callbacks."""
import argparse,re,subprocess,time
from pathlib import Path
from closure_support import ROOT,function,compile_c,receipt,save
from adlx_sections_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--negative',choices=['volume','clock']);p.add_argument('--budget',action='store_true');p.add_argument('--wrap',action='store_true');a=p.parse_args()
    assert sum([bool(a.negative),a.budget,a.wrap])<=1
    folder=OUT/('samples-wrap' if a.wrap else 'samples-budget' if a.budget else 'samples-'+a.negative if a.negative else 'samples');folder.mkdir(parents=True,exist_ok=True)
    api=(ROOT/'c/sound_api.c').read_text();adlib=(ROOT/'c/adlib.c').read_text();engine=(ROOT/'c/sound_engine.c').read_text()
    prefix=adlib[:adlib.index('/* No stack args.')]
    for name in ['push','call','args_call','inc','al','bl','bh','emit','delay']:prefix=re.sub(r'\b'+name+r'\b','driver_'+name,prefix)
    delay=function(engine,'c_DelaySoundIo');loop='    uint16_t remaining=product;\n    do { remaining=(uint16_t)(remaining-1); } while(remaining);\n';assert loop in delay;delay=delay.replace(loop,'/* Finite state-only busy-loop contract. */\n')
    code='''#include "platform.h"
#include <stdio.h>
#include <stdlib.h>
#define CHECK(c,m) do {if(!(c)){fprintf(stderr,"%s line%u\\n",m,__LINE__);exit(1);}} while(0)
static uint32_t seed=391852;
static uint16_t N16(void) {seed=seed*1664525u+1013904223u;return (uint16_t)(seed>>16);}
static uint8_t N8(void) {return (uint8_t)N16();}
'''
    code+=prefix+delay+function((ROOT/'c/game_services.c').read_text(),'c_CopyFarBytes')
    code+=api[:api.index('/* Word device mask;')]+function(api,'scan_arm')
    for name in ['ScanMusicEvents','ApplyScannedMusicEvents']:code+=function(api,'c_'+name).replace('EXPORT int c_','EXPORT int reference_',1)
    tick=function(adlib,'c_TickAdlxPlayback').replace('EXPORT int c_','EXPORT int reference_',1)
    for name in ['call','al']:tick=re.sub(r'\b'+name+r'\b','driver_'+name,tick)
    code+=function(adlib,'inc')+function(adlib,'clock_tick')+tick
    bridge=(ROOT/'native/bridge/adlx_sections_bridge.c').read_text().replace('#include "../adlx_sections.h"','#include "adlx_sections.h"')
    bridge=bridge.replace('l1_ScanMusicEvents','reference_ScanMusicEvents').replace('l1_ApplyScannedMusicEvents','reference_ApplyScannedMusicEvents');code+=bridge
    code+='\n#include "'+(ROOT/'native/adlx_main.c').as_posix()+'"\n'
    native=(ROOT/'native/adlx_sections.c').read_text()
    if a.negative=='volume':native=native.replace('(uint8_t)state->live[channel].volume','(uint8_t)state->scanned[channel].volume')
    if a.negative=='clock':native=native.replace('(((uint32_t)code<<8)+work->cursor.window[work->cursor.index])<<7','(uint16_t)((((uint32_t)code<<8)+work->cursor.window[work->cursor.index])<<7)')
    code+=native;(folder/'pair.inc').write_text(code)
    harness=folder/'harness.c';harness.write_text((ROOT/'verif/adlx_sections_harness.c').read_text())
    exe=folder/'harness.exe';built=compile_c([harness],exe,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-Wno-unused-function',*(['-DBUDGET_PROFILE'] if a.budget else []),*(['-DCLOCK_PROFILE'] if a.negative=='clock' else []),*(['-DWRAP_PROFILE'] if a.wrap else [])])
    start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
    inputs=[Path(__file__),ROOT/'verif/adlx_sections_harness.c',ROOT/'native/adlx_sections.c',ROOT/'native/adlx_sections.h',ROOT/'native/bridge/adlx_sections_bridge.c',ROOT/'native/audio.h',ROOT/'native/adlx_main.c',ROOT/'c/sound_api.c',ROOT/'c/adlib.c',ROOT/'c/sound_engine.c',ROOT/'c/game_services.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h']
    save(OUT/('samples-wrap.json' if a.wrap else 'samples-budget.json' if a.budget else 'samples-'+a.negative+'.json' if a.negative else 'samples.json'),receipt(['python','verif/adlx_sections_evidence.py',*(['--negative',a.negative] if a.negative else []),*(['--budget'] if a.budget else []),*(['--wrap'] if a.wrap else [])],inputs,
        result='PASS' if run.returncode==0 else 'FAIL',bound=5000000 if a.budget else 30000,cases=None if a.negative else 1 if a.budget or a.wrap else 30000,build=built,execution=[str(exe)],seconds=time.perf_counter()-start,stdout=run.stdout,stderr=run.stderr))
    print(run.stdout+run.stderr,flush=True);assert (run.returncode!=0) if a.negative else (run.returncode==0)
if __name__=='__main__':main()
