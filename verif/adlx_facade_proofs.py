"""Small split duration theorems from the actual C switch; no interpreter model."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from adlx_facade_build import OUT
from adlx_facade_limits import cbmc
from adlx_lifetime_proofs import SOLVER

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['outputs','frame','dependence']);p.add_argument('--negative',action='store_true');a=p.parse_args();folder=OUT/('proof-facade-'+a.mode+('-negative' if a.negative else ''));folder.mkdir(parents=True,exist_ok=True)
 literal=function((ROOT/'c/music_analysis.c').read_text(),'c_GetMusicTrackDuration');cut=literal[literal.index('        switch(arm)'):literal.index('\n    }\n    /* Reload')];cut=cut.replace('rd8(segment,p)','payload').replace('return UGH_BAD_CALLBACK;','return 0;')
 code='#include "adlx_facade.h"\n#define CHECK(c,m) __CPROVER_assert(c,m)\nuint16_t nondet_u16(void);uint8_t nondet_u8(void);uint32_t nondet_u32(void);int nondet_int(void);AudioDurationWork nondet_work(void);\n'+(ROOT/'native/adlx_facade.c').read_text()
 if a.negative:code=code.replace('work->total+=code&127u','work->total+=code&63u')
 code+='static int reference(uint16_t *position,uint32_t *elapsed,uint8_t code,int arm,uint8_t payload) {uint16_t p=*position;uint32_t total=*elapsed;'+cut+'*position=p;*elapsed=total;return 1;}\n'
 code+='int main(void) {AudioDurationWork work=nondet_work(),before=work;uint8_t code=nondet_u8(),payload=nondet_u8();int arm=nondet_int();uint16_t pos=work.position;uint32_t total=work.total;int expected=reference(&pos,&total,code,arm,payload);int actual=audio_duration_step(&work,code,arm,payload);'
 if a.mode=='outputs':code+='CHECK(expected==actual && pos==work.position && total==work.total,"actual C switch output over arbitrary words and all targets");'
 elif a.mode=='frame':code+='CHECK(work.end==before.end && work.enabled==before.enabled && work.budget==before.budget,"step modifies only cursor and elapsed time");'
 else:code+='AudioDurationWork other=before;other.end=nondet_u16();other.enabled=nondet_u8();other.budget=nondet_u32();int status=audio_duration_step(&other,code,arm,payload);CHECK(status==actual && other.position==work.position && other.total==work.total,"step independent of non-input fields");'
 code+='return 0;}'
 h=folder/'harness.c';h.write_text(code);r=cbmc(h,folder,[Path(__file__),ROOT/'native/adlx_facade.c',ROOT/'native/adlx_facade.h',ROOT/'c/music_analysis.c'],unwind=3,timeout=60,extra=SOLVER);print(a.mode,r['result'],r['seconds'],r['failures']);assert r['result']==('FAIL' if a.negative else 'PASS')
if __name__=='__main__':main()
