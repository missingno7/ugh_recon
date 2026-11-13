"""One actual scan-loop body versus the typed scan event, split properties."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from adlx_loader_solver import cbmc
from adlx_sections_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['outputs','frame','dependence']);p.add_argument('--arm',type=int,choices=range(9),required=True);p.add_argument('--negative',action='store_true');p.add_argument('--timeout',type=int,default=180);a=p.parse_args()
    assert 0<a.timeout<=600
    folder=OUT/f'proof-step-{a.mode}-{a.arm}{"-negative" if a.negative else ""}';folder.mkdir(parents=True,exist_ok=True)
    api=(ROOT/'c/sound_api.c').read_text();native=(ROOT/'native/adlx_sections.c').read_text()
    if a.negative:native=native.replace('((uint32_t)code<<8)','((uint32_t)(code&15u)<<8)')
    code='''#include "ugh.h"
#include "adlx_sections.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
static uint16_t word_read(uint16_t,uint16_t);
static void word_write(uint16_t,uint16_t,uint16_t);
#define rd16 word_read
#define wr16 word_write
'''
    code+=api[:api.index('/* Word device mask;')]+function(api,'scan_arm')+function((ROOT/'c/game_services.c').read_text(),'c_CopyFarBytes')
    body=function(api,'c_ScanMusicEvents');start=body.index('while(total<threshold) {')+len('while(total<threshold) {');end=start;depth=1
    while depth:
        if body[end]=='{':depth+=1
        if body[end]=='}':depth-=1
        end+=1
    fragment=body[start:end-1]
    for status,exit in [('UGH_BUDGET','AUDIO_SCAN_BUDGET'),('UGH_BAD_CALLBACK','AUDIO_SCAN_CALLBACK'),('0','AUDIO_SCAN_END')]:
        fragment=fragment.replace('return leave(r,f,'+status+');','{work->exit='+exit+';goto done;}')
    code+='''static void reference_step(Regs *r,AudioScanWork *work) {
 Frame f={r->sp,r->bp,r->si,r->di,r->ds};uint16_t p=work->cursor.index,s=0x6000;uint32_t total=work->total;unsigned budget=work->budget,pass=work->pass;
'''+fragment+'''
done:work->cursor.index=p;work->total=total;work->budget=budget;
}
'''
    code+=''.join(function(native,n) for n in ['audio_section_classify','audio_section_word','audio_section_scan_finish','audio_section_scan_step'])
    (folder/'pair.inc').write_text(code);harness=folder/'harness.c';harness.write_text((ROOT/'verif/adlx_sections_step.c').read_text())
    inputs=[Path(__file__),ROOT/'verif/adlx_sections_step.c',ROOT/'native/adlx_sections.c',ROOT/'native/adlx_sections.h',ROOT/'native/audio.h',ROOT/'c/sound_api.c',ROOT/'c/game_services.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h']
    result=cbmc(harness,folder,inputs,unwind=15,timeout=a.timeout,defines=[f'-DARM={a.arm}',f'-DMODE={dict(outputs=0,frame=1,dependence=2)[a.mode]}'],extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
    print(a.mode,a.arm,result['result'],result['seconds'],result['failures'],flush=True);assert result['result']==('FAIL' if a.negative else 'PASS')
if __name__=='__main__':main()
