"""Actual-C symbolic policy and state-transition profiles; exact domains below."""
import argparse
from pathlib import Path
from closure_support import ROOT,function,cbmc
from adlx_allocation_build import OUT
from adlx_allocation_evidence import INPUTS
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',type=int,choices=range(4));p.add_argument('--timeout',type=int,default=120);p.add_argument('--negative',action='store_true');p.add_argument('--scalar-capacity',action='store_true');a=p.parse_args()
    if a.scalar_capacity:assert a.profile==2 and not a.negative
    for profile in range(4) if a.profile is None else [a.profile]:
        folder=OUT/('capacity' if a.scalar_capacity else f'policy-proof-{profile}{"-negative" if a.negative else ""}');folder.mkdir(parents=True,exist_ok=True)
        api=(ROOT/'c/sound_api.c').read_text();bridge=(ROOT/'native/bridge/adlx_allocation_bridge.c').read_text()
        prefix='''#include "ugh.h"
#include "adlx_allocation.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
static uint16_t word_read(uint16_t,uint16_t);
static void word_write(uint16_t,uint16_t,uint16_t);
#define rd16 word_read
#define wr16 word_write
static void audio_bridge_project(uint16_t,AudioState *);
'''
        code=prefix+api[:api.index('/* Word device mask;')]
        for name in ['PlayAdlibEffect','StopAdlibTrackChannel','StartAdlibTrackChannel','RestoreAdlibVoiceAllocation']:
            code+=function(api,'c_'+name).replace('EXPORT int c_'+name+'(','EXPORT int reference_'+name+'(',1)
        code+='typedef struct AllocationFrame {uint16_t sp,bp,si,di,ds;} AllocationFrame;\n'
        for name in ['allocation_push','allocation_enter','allocation_leave','allocation_call','c_PlayAdlibEffect']:code+=function(bridge,name)
        native=(ROOT/'native/adlx_allocation.c').read_text()
        # These domains have no driver calls. Assert, rather than assume,
        # that excluded callees are unreachable. This avoids unwinding their
        # large bodies along already-infeasible paths during symex.
        for name in ['audio_allocation_voice','audio_allocation_volume']:
            body=function(native,name);header=body[:body.index('{')]
            native=native.replace(body,header+'{CHECK(0,"excluded native voice call");}\n')
        if profile in [1,2]:
            body=function(native,'audio_allocation_restore');header=body[:body.index('{')]
            native=native.replace(body,header+'{CHECK(0,"excluded native restoration call");}\n')
        if a.negative:native=native.replace('.age<state->channels[result.channel].age','.age<=state->channels[result.channel].age')
        code+=native
        (folder/'pair.inc').write_text(code)
        compare=(ROOT/'verif/adlx_effects_harness.c').read_text().split('#ifdef SEMANTIC\n')[1].split('\n#endif')[0]
        compare=compare.replace('for(unsigned i=0;i<12;i++) CHECK','unsigned i=nondet_u8();__CPROVER_assume(i<12);CHECK')
        compare=compare.replace('for(unsigned i=0;i<13;i++) {','{ unsigned i=nondet_u8();__CPROVER_assume(i<13);')
        compare=compare.replace('for(unsigned i=0;i<9;i++) {','{ unsigned i=nondet_u8();__CPROVER_assume(i<9);')
        source=(ROOT/'verif/adlx_allocation_proof.c').read_text()
        if a.scalar_capacity:
            compare='''static void compare_state(const AudioState *a,const AudioState *b) {
 CHECK(a->playback_guard==b->playback_guard && a->reserved_voices==b->reserved_voices && a->current_channel==b->current_channel,"capacity globals");
 CHECK(a->channels[8].volume==b->channels[8].volume && a->channels[8].control==b->channels[8].control && a->channels[8].first_voice==b->channels[8].first_voice,"capacity selected record");
}'''
            source=source.replace('state[0]=nondet_audio();devices=nondet_u16();','''state[0]=(AudioState){0};devices=1;
 state[0].playback_guard=nondet_u16();state[0].reserved_voices=nondet_u16();state[0].current_channel=nondet_u16();
 state[0].channels[8].volume=nondet_u16();state[0].channels[8].first_voice=nondet_u16();
 state[0].channels[8].voice_count=nondet_u16();state[0].channels[8].control=(uint16_t)((nondet_u16()&65534u)|4u);''')
            source=source.replace('channel=nondet_u16(),volume=nondet_u16()','channel=8,volume=nondet_u16()')
        harness=folder/'harness.c';harness.write_text(source.replace('/* COMPARE */',compare))
        result=cbmc(harness,folder,[*INPUTS,Path(__file__),ROOT/'verif/adlx_allocation_proof.c'],unwind=15,timeout=a.timeout,
            defines=[f'-DPROFILE={profile}'],extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
        print(profile,result['result'],result['seconds'],result['failures'],flush=True)
        assert result['result']==('FAIL' if a.negative else 'PASS')
if __name__=='__main__':main()
