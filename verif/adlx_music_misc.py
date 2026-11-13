"""Actual guarded C clock and silence writes; native frame/dependence split."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from adlx_loader_solver import cbmc
from adlx_music_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['guard','silence','frame','dependence']);p.add_argument('--word-memory',action='store_true');p.add_argument('--timeout',type=int,default=180);a=p.parse_args();assert 0<a.timeout<=600
    folder=OUT/f'proof-misc-{a.mode}{"-word" if a.word_memory else ""}';folder.mkdir(parents=True,exist_ok=True)
    native=(ROOT/'native/adlx_music.c').read_text();literal=(ROOT/'c/adlib.c').read_text();sections=(ROOT/'native/adlx_sections.c').read_text();engine=(ROOT/'c/sound_engine.c').read_text()
    code='''#include "platform.h"
#include "adlx_music.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
uint8_t ugh_mem[UGH_MEM_SIZE];AudioState nondet_audio(void);uint16_t nondet_u16(void);uint8_t nondet_u8(void);
static AudioState reference;static uint8_t stack[1024];static unsigned ports;static uint16_t log[40][2];
uint8_t ugh_read(uint32_t address) {
 unsigned p=address-(unsigned)SOUND_SEG*16u;
 if(p>=S(AdlibOperatorOffsets) && p<S(AdlibOperatorOffsets)+9) return reference.operator_index[p-S(AdlibOperatorOffsets)];
 if(p==S(SoundIoDelayMultiplier)) return 1;
 if(p>=S(AdlxTickCount) && p<S(AdlxTickCount)+4) return (uint8_t)(reference.ticks>>(8*(p-S(AdlxTickCount))));
 if((p&65534u)==S(AdlxPlaybackGuard)) return (uint8_t)(reference.playback_guard>>(8*(p&1u)));
 CHECK(address>=0x80000 && address<0x80400,"misc stack read");return stack[address-0x80000];
}
void ugh_write(uint32_t address,uint8_t value) {
 unsigned p=address-(unsigned)SOUND_SEG*16u;
 if(p>=S(AdlxTickCount) && p<S(AdlxTickCount)+4) {unsigned shift=8*(p-S(AdlxTickCount));reference.ticks=(reference.ticks&~((uint32_t)255<<shift))|((uint32_t)value<<shift);return;}
 if((p&65534u)==S(AdlxPlaybackGuard)) {unsigned shift=8*(p&1u);reference.playback_guard=(uint16_t)((reference.playback_guard&~(255u<<shift))|((unsigned)value<<shift));return;}
 CHECK(address>=0x80000 && address<0x80400,"misc stack write");stack[address-0x80000]=value;
}
void platform_out(uint16_t port,unsigned size,uint32_t value) {CHECK(ports<40 && size==1,"silence output bound");log[ports][0]=port;log[ports++][1]=(uint16_t)value;}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r) {CHECK(bank==SOUND_SEG && target==S(TickAdlxPlayback) && (reference.playback_guard&1),"guarded Tick boundary");return c_TickAdlxPlayback(r);}
'''
    if a.word_memory:
        code+='''static uint16_t misc_read_word(uint16_t bank,uint16_t offset) {
 if(bank==SOUND_SEG) {
  if(offset==S(AdlxTickCount)) return (uint16_t)reference.ticks;
  if(offset==S(AdlxTickHighWord)) return (uint16_t)(reference.ticks>>16);
  if(offset==S(AdlxPlaybackGuard)) return reference.playback_guard;
 }
 CHECK(bank==0x8000 && offset<1023 && !(offset&1),"misc aligned stack read");return (uint16_t)(stack[offset]|(unsigned)stack[offset+1]*256u);
}
static void misc_write_word(uint16_t bank,uint16_t offset,uint16_t value) {
 if(bank==SOUND_SEG) {
  if(offset==S(AdlxTickCount)) {reference.ticks=(reference.ticks&0xffff0000u)|value;return;}
  if(offset==S(AdlxTickHighWord)) {reference.ticks=(reference.ticks&65535u)|((uint32_t)value<<16);return;}
  if(offset==S(AdlxPlaybackGuard)) {reference.playback_guard=value;return;}
 }
 CHECK(bank==0x8000 && offset<1023 && !(offset&1),"misc aligned stack store");stack[offset]=(uint8_t)value;stack[offset+1]=(uint8_t)(value>>8);
}
#define rd16 misc_read_word
#define wr16 misc_write_word
'''
    for name in ['push','call','inc','al','bh','emit','clock_tick','c_WriteAdlibRegister','c_TickAdlxPlayback','c_AdvanceGuardedSoundClock','c_SilenceAdlibOperators']:code+=function(literal,name)
    delay=function(engine,'c_DelaySoundIo');loop='    uint16_t remaining=product;\n    do { remaining=(uint16_t)(remaining-1); } while(remaining);\n';assert loop in delay;code+=delay.replace(loop,'/* Finite state-only delay contract. */\n')
    for name in ['audio_section_tick_begin','audio_section_tick_end']:code+=function(sections,name)
    for name in ['audio_music_guard_begin','audio_music_guard_end','audio_music_silence']:code+=function(native,name)
    code+='int main(void) {AudioState native=nondet_audio();reference=native;\n'
    if a.mode=='guard':
        code+='''Regs r={0};r.cs=SOUND_SEG;r.ss=0x8000;r.sp=0x200;r.flags=nondet_u16();CHECK(c_AdvanceGuardedSoundClock(&r)==0,"normal guarded return");
 if(audio_music_guard_begin(&native)) {CHECK(!audio_section_tick_begin(&native),"nested accepted Tick sees guard");audio_music_guard_end(&native);}
 CHECK(reference.ticks==native.ticks && reference.playback_guard==native.playback_guard && !ports,"double increment only on admitted guard");
'''
    elif a.mode=='silence':
        code+='''Regs r={0};r.cs=SOUND_SEG;r.ss=0x8000;r.sp=0x200;c_SilenceAdlibOperators(&r);AudioRegisterWrite writes[20];audio_music_silence(&native,writes);CHECK(ports==40,"twenty silence writes");
 for(unsigned i=0;i<20;i++) CHECK(log[2*i][0]==0x388 && log[2*i+1][0]==0x389 && log[2*i][1]==writes[i].reg && log[2*i+1][1]==writes[i].value,"ordered silence values and register wrap");
'''
    elif a.mode=='frame':
        code+='''unsigned i=nondet_u16();__CPROVER_assume(i<sizeof(native));uint8_t *p=(uint8_t *)&native+i,*t=(uint8_t *)&native.ticks,*g=(uint8_t *)&native.playback_guard;__CPROVER_assume((p<t || p>=t+4) && (p<g || p>=g+2));uint8_t old=*p;AudioRegisterWrite writes[20];audio_music_silence(&native,writes);audio_music_guard_begin(&native);audio_music_guard_end(&native);CHECK(*p==old,"misc whole-state frame");
'''
    else:
        code+='''AudioState other=nondet_audio();other.ticks=native.ticks;other.playback_guard=native.playback_guard;for(unsigned i=0;i<9;i++) other.operator_index[i]=native.operator_index[i];AudioRegisterWrite x[20],y[20];audio_music_silence(&native,x);audio_music_silence(&other,y);for(unsigned i=0;i<20;i++) CHECK(x[i].reg==y[i].reg && x[i].value==y[i].value,"silence dependence");CHECK(audio_music_guard_begin(&native)==audio_music_guard_begin(&other) && native.ticks==other.ticks && native.playback_guard==other.playback_guard,"guard dependence");
'''
    code+='return 0;}\n';harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'native/adlx_music.c',ROOT/'native/adlx_music.h',ROOT/'native/adlx_sections.c',ROOT/'native/audio.h',ROOT/'c/adlib.c',ROOT/'c/sound_engine.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=25,timeout=a.timeout,extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
    print(a.mode,result['result'],result['seconds'],result['failures'],flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
