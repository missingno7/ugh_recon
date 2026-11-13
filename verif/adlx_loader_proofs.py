"""Split actual-C loader properties, with hard 8 GiB/600s solver job limits."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from adlx_loader_solver import cbmc
from adlx_loader_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['outputs','frame','dependence','gate']);p.add_argument('--slot',type=int,choices=[8,12],default=8);p.add_argument('--timeout',type=int,default=600);p.add_argument('--negative',action='store_true');p.add_argument('--canonical',action='store_true');a=p.parse_args()
    assert 0<a.timeout<=600
    folder=OUT/f'proof-{a.mode}-{a.slot}{"-cut" if a.mode=="gate" else ""}{"-canonical" if a.canonical else ""}{"-negative" if a.negative else ""}';folder.mkdir(parents=True,exist_ok=True)
    api=(ROOT/'c/sound_api.c').read_text();native=(ROOT/'native/adlx_loader.c').read_text()
    if a.negative:native=native.replace('(uint16_t)(9-state->reserved_voices)','(uint16_t)(8-state->reserved_voices)')
    if a.mode=='gate':
        body=function(native,'audio_adlx_tag');native=native.replace(body,body[:body.index('{')]+'{CHECK(0,"gate never reaches resource tag reader");return 0;}\n')
    code='''#include "ugh.h"
#include "adlx_loader.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
static uint16_t word_read(uint16_t,uint16_t);
static void word_write(uint16_t,uint16_t,uint16_t);
#define rd16 word_read
#define wr16 word_write
'''
    code+=api[:api.index('/* Word device mask;')]+function(api,'c_LoadAdlibTrackData')+function((ROOT/'c/music_clock.c').read_text(),'c_SwapDwordByteOrder')+native
    (folder/'pair.inc').write_text(code)
    source=(ROOT/'verif/adlx_loader_proof.c').read_text()
    if a.mode=='gate':
        source=source.replace('resource=nondet_resource();','resource=(Resource){0};')
        source=source.replace('return resource.bytes[address-0x60000];','{CHECK(0,"rejected gate never reads source");return resource.bytes[address-0x60000];}')
    if a.canonical:
        source=source.replace('resource=nondet_resource();devices=nondet_u16();','''resource=nondet_resource();devices=nondet_u16();
 resource.bytes[12]=resource.bytes[13]=resource.bytes[14]=0;resource.bytes[15]=10;
 resource.bytes[30]=resource.bytes[31]=resource.bytes[32]=resource.bytes[33]=0;''')
        source=source.replace('index=nondet_u16()','index=0')
    harness=folder/'harness.c';harness.write_text(source)
    inputs=[Path(__file__),ROOT/'verif/adlx_loader_proof.c',ROOT/'c/sound_api.c',ROOT/'c/music_clock.c',ROOT/'native/adlx_loader.c',ROOT/'native/adlx_loader.h',ROOT/'native/audio.h',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h']
    result=cbmc(harness,folder,inputs,unwind=6,timeout=a.timeout,defines=[f'-DSLOT={a.slot}',f'-DMODE={dict(outputs=0,frame=1,dependence=2,gate=3)[a.mode]}'],extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
    print(a.mode,a.slot,result['result'],result['seconds'],result['failures'],flush=True);assert result['result']==('FAIL' if a.negative else 'PASS')
if __name__=='__main__':main()
