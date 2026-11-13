"""Actual compiled music C/bridge composition with stateful service contracts."""
import argparse,re,subprocess,time
from pathlib import Path
from closure_support import ROOT,function,compile_c,receipt,save
from adlx_music_build import OUT
NAMES=['StartMusicTrack','StopMusicTrack','SetMusicTrackVolume','ScheduleMusicFade','CancelMusicFade','AdvanceMusicFade','AdvanceGuardedSoundClock','SilenceAdlibOperators']
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--negative',choices=['signed','wait','volume']);p.add_argument('--budget',action='store_true');a=p.parse_args()
    folder=OUT/('samples-'+a.negative if a.negative else 'samples-budget' if a.budget else 'samples');folder.mkdir(parents=True,exist_ok=True)
    adlib=(ROOT/'c/adlib.c').read_text();api=(ROOT/'c/sound_api.c').read_text();engine=(ROOT/'c/sound_engine.c').read_text()
    prefix=adlib[:adlib.index('/* BH=register')]
    for name in ['push','call','args_call','inc','al','bl','bh','emit','delay']:prefix=re.sub(r'\b'+name+r'\b','driver_'+name,prefix)
    def driver(text):
        for name in ['push','call','args_call','inc','al','bl','bh','emit','delay']:text=re.sub(r'\b'+name+r'\b','driver_'+name,text)
        return text
    delay=function(engine,'c_DelaySoundIo');loop='    uint16_t remaining=product;\n    do { remaining=(uint16_t)(remaining-1); } while(remaining);\n';assert loop in delay;delay=delay.replace(loop,'/* Finite state-only delay contract. */\n')
    code='#include "platform.h"\n#include "adlx_music.h"\n#include <stdio.h>\n#include <stdlib.h>\n#define CHECK(c,m) do {if(!(c)){fprintf(stderr,"%s line%u\\n",m,__LINE__);exit(1);}} while(0)\n'
    code+=prefix+delay+driver(function(adlib,'c_WriteAdlibRegister'))+driver(function(adlib,'c_SetAdlibChannelVolume'))+driver(function(adlib,'clock_tick'))
    code+=api[:api.index('/* Word device mask;')]
    for name in NAMES:
        f=function(api if name in NAMES[:3] else adlib,'c_'+name).replace('EXPORT int c_','EXPORT int reference_',1)
        code+=f if name in NAMES[:3] else driver(f)
    # Real accepted Tick clock/guard branch, reached only with guard already set.
    code+=driver(function(adlib,'c_TickAdlxPlayback'))
    code+=(ROOT/'native/bridge/adlx_music_bridge.c').read_text().replace('#include "../adlx_music.h"','#include "adlx_music.h"')
    sections=(ROOT/'native/adlx_sections.c').read_text();code+=''.join(function(sections,n) for n in ['audio_section_tick_begin','audio_section_tick_end'])
    native=(ROOT/'native/adlx_music.c').read_text()
    if a.negative=='signed':native=native.replace('state->fade.step_count>state->fade.duration','(int16_t)state->fade.step_count>(int16_t)state->fade.duration')
    if a.negative=='wait':native=native.replace('if(state->fade.scheduled) return audio_music_wait(work);','if(state->fade.scheduled&1u) return audio_music_wait(work);')
    if a.negative=='volume':native=native.replace('if((uint8_t)i<9)','if(i<9)')
    code+=native;(folder/'pair.inc').write_text(code)
    harness=folder/'harness.c';harness.write_text((ROOT/'verif/adlx_music_harness.c').read_text());exe=folder/'harness.exe'
    built=compile_c([harness],exe,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-Wno-unused-function',*(['-DBUDGET_PROFILE'] if a.budget else [])])
    started=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
    save(OUT/(folder.name+'.json'),receipt(['python','verif/adlx_music_evidence.py',*(['--negative',a.negative] if a.negative else []),*(['--budget'] if a.budget else [])],[Path(__file__),ROOT/'verif/adlx_music_harness.c',ROOT/'native/adlx_music.c',ROOT/'native/adlx_music.h',ROOT/'native/bridge/adlx_music_bridge.c',ROOT/'native/audio.h',ROOT/'c/adlib.c',ROOT/'c/sound_api.c',ROOT/'c/sound_engine.c'],result='FAIL' if run.returncode else 'PASS',expected_failure=bool(a.negative),build=built,seconds=time.perf_counter()-started,stdout=run.stdout,stderr=run.stderr))
    print(run.stdout+run.stderr,flush=True);assert (run.returncode!=0) if a.negative else (run.returncode==0)
if __name__=='__main__':main()
