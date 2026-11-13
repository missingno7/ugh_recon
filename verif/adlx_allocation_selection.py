"""Prove selection against the real C Play entry, before parser/allocation."""
import argparse
from pathlib import Path
from closure_support import ROOT,function,cbmc
from adlx_allocation_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--negative',action='store_true');p.add_argument('--timeout',type=int,default=120);a=p.parse_args()
    folder=OUT/('selection-negative' if a.negative else 'selection');folder.mkdir(parents=True,exist_ok=True)
    api=(ROOT/'c/sound_api.c').read_text()
    native=function((ROOT/'native/adlx_allocation.c').read_text(),'audio_effect_select')
    if a.negative:native=native.replace('.age<state->channels[result.channel].age','.age<=state->channels[result.channel].age')
    code='''#include "ugh.h"
#include "adlx_allocation.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
uint8_t ugh_mem[UGH_MEM_SIZE];
uint16_t nondet_u16(void);uint32_t nondet_u32(void);
static uint32_t age[4];static uint16_t control[4];static uint8_t stack[128];
static unsigned calls;static uint16_t chosen,target0;
uint8_t ugh_read(uint32_t address) {
 uint32_t base=(uint32_t)SOUND_SEG*16;
 if(address==base+S(SoundDeviceBits)) return 1;
 if(address==base+S(SoundDeviceBits)+1) return 0;
 for(unsigned i=0;i<4;i++) {
  unsigned p=S(AudioChannelStates)+(i+8)*42;
  for(unsigned j=0;j<4;j++) if(address==base+p+j) return (uint8_t)(age[i]>>(8*j));
  if(address==base+p+40) return (uint8_t)control[i];
  if(address==base+p+41) return (uint8_t)(control[i]>>8);
 }
 CHECK(address>=0x70fc0 && address<0x71040,"selection stack read footprint");return stack[address-0x70fc0];
}
void ugh_write(uint32_t address,uint8_t value) {
 CHECK(address>=0x70fc0 && address<0x71040,"selection stack write footprint");stack[address-0x70fc0]=value;
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r) {
 CHECK(bank==UGH_SEG_C,"selection external bank");
 if(!calls) {chosen=arg16(r,0);target0=target;}
 calls++;
 CHECK(chosen>=8 && chosen<12,"selected effect record");
 if(target==UGH_O_C_StopAdlibTrackChannel) control[chosen-8]=0;
 else CHECK(target==UGH_O_C_LoadAdlibChannel,"cut after selection at loader");
 r->ax=65535;return 0; /* deliberately fail loader, no START reaches this cut */
}
'''
    code+=api[:api.index('/* Word device mask;')]+function(api,'c_PlayAdlibEffect')+native
    code+='''int main(void) {
 AudioState state={0};
 for(unsigned i=0;i<4;i++) {age[i]=nondet_u32();control[i]=nondet_u16();state.channels[i+8].age=age[i];state.channels[i+8].control=control[i];}
 Regs r={0};r.cs=UGH_SEG_C;r.ss=0x7000;r.sp=0x1000;
 c_PlayAdlibEffect(&r);AudioEffectSelection selection=audio_effect_select(&state);
 CHECK(calls>=1 && calls<=2,"finite selection cut");
 CHECK(selection.channel==chosen,"selected physical effect record");
 CHECK(selection.replace==(target0==UGH_O_C_StopAdlibTrackChannel),"free versus replacement branch");
 return 0;
}
'''
    harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'c/sound_api.c',ROOT/'native/adlx_allocation.c',ROOT/'native/adlx_allocation.h',ROOT/'native/audio.h',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=6,timeout=a.timeout,
        extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
    print(result['result'],result['seconds'],result['failures'],flush=True)
    assert result['result']==('FAIL' if a.negative else 'PASS')
if __name__=='__main__':main()
