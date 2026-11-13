"""Actual polling-body cuts for arbitrary counters, markers and budget edges."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from adlx_loader_solver import cbmc
from adlx_lifetime_build import OUT
from adlx_lifetime_proofs import SOLVER
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['outputs','frame','dependence']);p.add_argument('--negative',action='store_true');a=p.parse_args()
    folder=OUT/f'proof-poll-{a.mode}{"-negative" if a.negative else ""}';folder.mkdir(parents=True,exist_ok=True)
    source=function((ROOT/'c/sound_engine.c').read_text(),'c_CalibrateSoundDelay')
    start=source.index('    do {');stop=source.index('    } while((r->ax>>8)!=1);');begin=source[start+len('    do {\n'):stop]
    start=source.index('        do {');stop=source.index('        } while(r->cx);');loop=source[start+len('        do {\n'):stop]
    start=source.index('        uint16_t cf=');stop=source.index('    } while((uint8_t)r->ax!=1);');increment=source[start:stop]
    # The service has already supplied the live fields at this cut; status=0
    # is the successful-delivery condition. Tag the original budget return.
    def adapt(text):
        return text.replace('return UGH_BUDGET;','return AUDIO_CALIBRATION_BOUND;')
    code='''#include "platform.h"
#include "adlx_lifetime.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
uint16_t nondet_u16(void);unsigned nondet_uint(void);AudioCalibrationWork nondet_work(void);
int platform_service_point_at(ServicePoint p,uint16_t bank,uint16_t offset,Regs *r)
{(void)p;(void)bank;(void)offset;(void)r;return 0;}
static AudioCalibrationAction reference_cut(Regs *r,unsigned budget,int first) {int status;
if(first) {
'''+adapt(begin)+'''if((r->ax>>8)==1) {r->cx=0;return AUDIO_CALIBRATION_WAIT_LOOP;}return AUDIO_CALIBRATION_WAIT_BEGIN;}
'''+adapt(loop)+'''if(!r->cx) {
'''+increment+'''if((uint8_t)r->ax==1) return AUDIO_CALIBRATION_DONE;}return AUDIO_CALIBRATION_WAIT_LOOP;}
'''
    native=(ROOT/'native/adlx_lifetime.c').read_text()
    if a.negative:
        changed=native.replace('work->progress+1u','work->progress+2u');assert changed!=native;native=changed
    code+=native+'''int main(void) {
AudioCalibrationWork work=nondet_work();__CPROVER_assume(work.action==AUDIO_CALIBRATION_WAIT_BEGIN || work.action==AUDIO_CALIBRATION_WAIT_LOOP);__CPROVER_assume(work.budget<=1000000);
AudioCalibrationWork before=work;Regs r={0};r.ax=work.marker;r.cx=work.remaining;r.dx=work.progress;
AudioCalibrationAction left=reference_cut(&r,work.budget,work.action==AUDIO_CALIBRATION_WAIT_BEGIN),right=audio_calibration_resume(&work);
'''
    if a.mode=='outputs':code+='''CHECK(left==right,"same polling continuation or exhausted budget");CHECK(work.marker==r.ax && work.remaining==r.cx && work.progress==r.dx,"all counter/marker values at next cut");if(before.budget) CHECK(work.budget==before.budget-1,"one budget unit");else CHECK(work.budget==0,"budget bound state");'''
    elif a.mode=='frame':code+='''CHECK(work.marker==before.marker,"service-provided marker preserved");if(!before.budget) CHECK(work.remaining==before.remaining && work.progress==before.progress && work.budget==before.budget,"no counter work after exhausted budget");if(before.action==AUDIO_CALIBRATION_WAIT_BEGIN) CHECK(work.progress==before.progress,"no block progress during begin wait");'''
    else:code+='''AudioCalibrationWork other=before;other.marker=nondet_u16();if(before.action==AUDIO_CALIBRATION_WAIT_BEGIN) other.marker=(uint16_t)((before.marker&65280u)|(other.marker&255u));else other.marker=(uint16_t)((before.marker&255u)|(other.marker&65280u));audio_calibration_resume(&other);CHECK(other.remaining==work.remaining && other.progress==work.progress && other.budget==work.budget && other.action==work.action,"begin reads only high marker byte; loop reads only low byte");'''
    code+='return 0;}\n';harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'native/adlx_lifetime.c',ROOT/'native/adlx_lifetime.h',ROOT/'native/audio.h',ROOT/'c/sound_engine.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=2,timeout=180,extra=SOLVER)
    print('poll',a.mode,result['result'],result['seconds'],result['failures'],flush=True);assert result['result']==('FAIL' if a.negative else 'PASS')
if __name__=='__main__':main()
