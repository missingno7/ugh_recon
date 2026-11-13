"""Actual timer handler/native opcode: scalar outputs and byte-probed frame.
No interpreter arithmetic is rewritten. Only memory and external TIMER ABI
are normalized. All source is extracted from the maintained L1/native files.
"""
import argparse,json
from pathlib import Path
from closure_support import ROOT,function,cbmc
from adlx_effects_build import OUT

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['outputs','frame','dependencies']);p.add_argument('--timeout',type=int,default=90);a=p.parse_args()
    folder=OUT/('timer-scalar-'+a.mode);folder.mkdir(parents=True,exist_ok=True)
    source=(ROOT/'c/adlib.c').read_text()
    code='#include "ugh.h"\n#include "'+(ROOT/'native/adlx_effects.h').as_posix()+'"\n'
    code+='''#define CHECK(c,m) __CPROVER_assert(c,m)
uint16_t nondet_u16(void);uint8_t nondet_u8(void);AudioState nondet_audio(void);
uint8_t ugh_mem[UGH_MEM_SIZE];
static uint16_t playing,period,handle,scale,payload_index;
static uint8_t bytes[12],stack_bytes[32];
static unsigned timer_calls;static uint16_t timer_args[3];
static uint8_t lo(uint16_t value,unsigned high) {return (uint8_t)(value>>(high*8));}
uint8_t ugh_read(uint32_t address) {
 uint32_t b=(uint32_t)SOUND_SEG*16u;
 if(address==b+S(MainAdlxPlaying)) return lo(playing,0);
 if(address==b+S(MainAdlxPlaying)+1) return lo(playing,1);
 if(address==b+S(AdlxTimerPeriod)) return lo(period,0);
 if(address==b+S(AdlxTimerPeriod)+1) return lo(period,1);
 if(address==b+S(AdlxPlaybackTimerHandle)) return lo(handle,0);
 if(address==b+S(AdlxPlaybackTimerHandle)+1) return lo(handle,1);
 if(address==b+S(CurrentAdlxRecordOffset)) return lo((uint16_t)(S(AudioChannelStates)+8*42),0);
 if(address==b+S(CurrentAdlxRecordOffset)+1) return lo((uint16_t)(S(AudioChannelStates)+8*42),1);
 if(address==b+S(AudioChannelStates)+8*42+38) return lo(scale,0);
 if(address==b+S(AudioChannelStates)+8*42+39) return lo(scale,1);
 if(address==0x60000u+payload_index) return bytes[0];
 if(address==0x60000u+payload_index+1) return bytes[1];
 CHECK(0,"timer read footprint");return 0;
}
void ugh_write(uint32_t address,uint8_t value) {
 uint32_t b=(uint32_t)SOUND_SEG*16u;
 if(address==b+S(AdlxTimerPeriod)) {period=(uint16_t)((period&65280u)|value);return;}
 if(address==b+S(AdlxTimerPeriod)+1) {period=(uint16_t)((period&255u)|(unsigned)value*256u);return;}
 if(address==b+S(AudioChannelStates)+8*42+38) {scale=(uint16_t)((scale&65280u)|value);return;}
 if(address==b+S(AudioChannelStates)+8*42+39) {scale=(uint16_t)((scale&255u)|(unsigned)value*256u);return;}
 CHECK(address>=0x70fe0u && address<0x71000u,"timer stack write footprint");stack_bytes[address-0x70fe0u]=value;
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r) {
 CHECK(bank==TIMER_SEG && target==T(SetTimerCallbackInterval),"timer target");
 timer_calls++;timer_args[0]=r->ax;timer_args[1]=r->bx;timer_args[2]=r->cx;return UGH_OK;
}
int c_RunEffectAdlxEvents(Regs *r) {(void)r;return 0;}
AudioMainResult audio_main_step(AudioState *s,AudioMainOperation o,uint8_t c,const uint8_t b[12],AudioCursor *p) {
 (void)s;(void)o;(void)c;(void)b;(void)p;CHECK(0,"timer never calls voice");AudioMainResult result={0};return result;
}
'''
    code+=''.join(function(source,n) for n in ['push','call','inc','c_HandleEffectAdlxTimerPeriod'])
    code+='#include "'+(ROOT/'native/adlx_effects.c').as_posix()+'"\n'
    code+='''int main(void) {
 AudioState state={0};AudioCursor cursor={0};Regs r={0};
 playing=nondet_u16();period=nondet_u16();handle=nondet_u16();scale=nondet_u16();
 state.playing=playing;state.timer_period=period;state.playback_timer_handle=handle;state.channels[8].step_q8=scale;
 for(unsigned i=0;i<12;i++) bytes[i]=nondet_u8();
 r.ax=(uint16_t)(0x60|(nondet_u16()&0xff0f));r.di=nondet_u16();r.flags=nondet_u16();
 r.cs=SOUND_SEG;r.es=0x6000;r.ss=0x7000;r.sp=0x1000;payload_index=r.di;cursor.index=r.di;
'''
    if a.mode=='outputs':
        code+='''AudioEffectsResult output=audio_effects_step(&state,&state.channels[8],AUDIO_TIMER_PERIOD,(uint8_t)r.ax,bytes,&cursor);
 int status=c_HandleEffectAdlxTimerPeriod(&r);
 CHECK(status==(output.exit==AUDIO_EFFECTS_DIVIDE_FAULT ? UGH_UNSUPPORTED : UGH_OK),"timer fault domain");
 CHECK(state.timer_period==period && state.channels[8].step_q8==scale,"timer values");
 CHECK(cursor.index==r.di && output.write_count==0 && !output.stop_request,"timer consumption and effect class");
 CHECK(timer_calls==output.timer_request,"timer request multiplicity");
 if(timer_calls) CHECK(timer_args[0]==handle && timer_args[1]==output.requested_period && timer_args[2]==0,"timer ABI");
'''
    elif a.mode=='frame':
        code+='''state=nondet_audio();
 unsigned probe=nondet_u16();__CPROVER_assume(probe<sizeof(state));
 uint8_t *cell=(uint8_t *)&state+probe;
 uint8_t *period_cell=(uint8_t *)&state.timer_period,*scale_cell=(uint8_t *)&state.channels[8].step_q8;
 __CPROVER_assume(cell<period_cell || cell>=period_cell+2);
 __CPROVER_assume(cell<scale_cell || cell>=scale_cell+2);
 uint8_t before=*cell;
 audio_effects_step(&state,&state.channels[8],AUDIO_TIMER_PERIOD,(uint8_t)r.ax,bytes,&cursor);
 CHECK(*cell==before,"every other native state byte retained");
'''
    else:
        code+='''AudioState other=nondet_audio();
 other.playing=state.playing;other.timer_period=state.timer_period;
 other.playback_timer_handle=state.playback_timer_handle;other.channels[8].step_q8=state.channels[8].step_q8;
 AudioCursor c2=cursor;
 AudioEffectsResult first=audio_effects_step(&state,&state.channels[8],AUDIO_TIMER_PERIOD,(uint8_t)r.ax,bytes,&cursor);
 AudioEffectsResult second=audio_effects_step(&other,&other.channels[8],AUDIO_TIMER_PERIOD,(uint8_t)r.ax,bytes,&c2);
 CHECK(first.exit==second.exit && first.advance==second.advance && first.timer_request==second.timer_request && first.requested_period==second.requested_period,"all other state irrelevant to timer outputs");
 CHECK(state.timer_period==other.timer_period && state.channels[8].step_q8==other.channels[8].step_q8 && cursor.index==c2.index,"timer data dependence");
'''
    code+='return 0;}\n';harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'c/adlib.c',ROOT/'native/adlx_effects.c',ROOT/'native/adlx_effects.h',ROOT/'native/audio.h',ROOT/'native/adlx_main.h',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=15,timeout=a.timeout,
        extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
    print(a.mode,result['result'],result['seconds'],result['failures'],flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
