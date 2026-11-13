"""Actual new volume journal versus the actual shared L1 OPL volume driver."""
import argparse,re
from pathlib import Path
from closure_support import ROOT,function
from adlx_loader_solver import cbmc
from adlx_voice_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['outputs','frame','dependence']);p.add_argument('--timeout',type=int,default=180);a=p.parse_args()
    folder=OUT/('proof-volume-'+a.mode);folder.mkdir(parents=True,exist_ok=True)
    adlib=(ROOT/'c/adlib.c').read_text();native=(ROOT/'native/adlx_voice.c').read_text();engine=(ROOT/'c/sound_engine.c').read_text()
    prefix=adlib[:adlib.index('/* No stack args.')]
    delay=function(engine,'c_DelaySoundIo');loop='    uint16_t remaining=product;\n    do { remaining=(uint16_t)(remaining-1); } while(remaining);\n';assert loop in delay;delay=delay.replace(loop,'/* Finite state-only delay contract. */\n')
    code='''#include "platform.h"
#include "adlx_voice.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
uint8_t ugh_mem[UGH_MEM_SIZE];
AudioState nondet_audio(void);AudioVoice nondet_voice(void);uint16_t nondet_u16(void);uint8_t nondet_u8(void);
static AudioState reference;static uint8_t stack[1024];static uint16_t ports[4][2];static unsigned port_count;
'''+prefix+delay+''.join(function(native,n) for n in ['voice_append','voice_level','voice_volume'])
    code+='''static uint16_t word(const AudioVoice *v,unsigned p) {
 if(p<12) return (uint16_t)(v->instrument[p]|(unsigned)v->instrument[p+1]*256u);
 return p==12 ? v->volume : p==14 ? v->gain : p==16 ? v->owner : v->frequency;
}
uint8_t ugh_read(uint32_t address) {
 unsigned base=(unsigned)SOUND_SEG*16u,p=address-base;uint16_t value=0;
 if(p>=S(AdlibVoiceStates) && p<S(AdlibVoiceStates)+20) {unsigned q=p-S(AdlibVoiceStates);return (uint8_t)(word(&reference.live[0],q&65534u)>>(8*(q&1u)));}
 if(p>=S(SavedAdlibVoiceStates) && p<S(SavedAdlibVoiceStates)+20) {unsigned q=p-S(SavedAdlibVoiceStates);return (uint8_t)(word(&reference.displaced[0],q&65534u)>>(8*(q&1u)));}
 if(p==S(AdlibOperatorOffsets)) return reference.operator_index[0];
 if(p==S(SoundIoDelayMultiplier)) return 1;
 if((p&65534u)==S(MainAdlxPlaying)) value=reference.playing;
 else if((p&65534u)==S(CurrentAdlxSlot)) value=reference.current_channel;
 else if((p&65534u)==S(ReservedAdlibChannelCount)) value=reference.reserved_voices;
 else {CHECK(address>=0x80000 && address<0x80400,"volume stack read");return stack[address-0x80000];}
 return (uint8_t)(value>>(8*(p&1u)));
}
void ugh_write(uint32_t address,uint8_t value) {
 unsigned p=address-(unsigned)SOUND_SEG*16u;
 if(p==S(AdlibChannelVolume)) {reference.live[0].volume=(uint16_t)((reference.live[0].volume&65280u)|value);return;}
 if(p==S(DisplacedAdlibVolume)) {reference.displaced[0].volume=(uint16_t)((reference.displaced[0].volume&65280u)|value);return;}
 CHECK(address>=0x80000 && address<0x80400,"volume stack write");stack[address-0x80000]=value;
}
void platform_out(uint16_t port,unsigned size,uint32_t value) {
 CHECK(port_count<4 && size==1,"volume port bound");ports[port_count][0]=port;ports[port_count][1]=(uint16_t)value;port_count++;
}
int ugh_dispatch(uint16_t b,uint16_t t,Regs *r) {(void)b;(void)t;(void)r;CHECK(0,"volume has no dispatch callee");return 1;}
static int within(uint8_t *p,void *f,unsigned n) {return p>=(uint8_t *)f && p<(uint8_t *)f+n;}
int main(void) {
 reference=(AudioState){0};reference.playing=nondet_u16();reference.current_channel=nondet_u16();reference.reserved_voices=nondet_u16();
 reference.operator_index[0]=nondet_u8();reference.live[0]=nondet_voice();reference.displaced[0]=nondet_voice();
 AudioState native=reference;AudioVoiceResult result={0};result.channel=0;result.first_reserved=(uint8_t)(9-(uint8_t)native.reserved_voices);uint8_t volume=nondet_u8();
'''
    if a.mode=='outputs':
        code+='''Regs r={0};r.cs=SOUND_SEG;r.ss=0x8000;r.sp=0x200;r.flags=nondet_u16();
 wr16(r.ss,0x204,0);wr16(r.ss,0x206,volume);c_SetAdlibChannelVolume(&r);
 result.displaced=voice_volume(&native,&result,volume);
 CHECK(reference.live[0].volume==native.live[0].volume && reference.displaced[0].volume==native.displaced[0].volume,"live/saved stale volume words");
 CHECK(port_count==result.write_count*2,"ordered journal counts");
 for(unsigned i=0;i<result.write_count;i++) CHECK(ports[2*i][0]==0x388 && ports[2*i+1][0]==0x389 && ports[2*i][1]==result.writes[i].reg && ports[2*i+1][1]==result.writes[i].value,"carrier then additive-modulator exact values");
'''
    elif a.mode=='frame':
        code+='''native=nondet_audio();unsigned i=nondet_u16();__CPROVER_assume(i<sizeof(native));uint8_t *p=(uint8_t *)&native+i,old=*p;
 __CPROVER_assume(!within(p,&native.live[0].volume,1) && !within(p,&native.displaced[0].volume,1));
 result.first_reserved=(uint8_t)(9-(uint8_t)native.reserved_voices);result.displaced=voice_volume(&native,&result,volume);CHECK(*p==old,"every other native volume state byte unchanged");
'''
    else:
        code+='''AudioState other=nondet_audio();other.playing=native.playing;other.current_channel=native.current_channel;other.reserved_voices=native.reserved_voices;
 other.operator_index[0]=native.operator_index[0];other.live[0].volume=native.live[0].volume;other.live[0].gain=native.live[0].gain;
 other.live[0].instrument[1]=native.live[0].instrument[1];other.live[0].instrument[6]=native.live[0].instrument[6];other.live[0].instrument[10]=native.live[0].instrument[10];
 other.displaced[0].volume=native.displaced[0].volume;AudioVoiceResult second={0};second.channel=0;second.first_reserved=result.first_reserved;
 result.displaced=voice_volume(&native,&result,volume);second.displaced=voice_volume(&other,&second,volume);
 CHECK(native.live[0].volume==other.live[0].volume && native.displaced[0].volume==other.displaced[0].volume && result.write_count==second.write_count,"volume read dependence");
 for(unsigned i=0;i<result.write_count;i++) CHECK(result.writes[i].reg==second.writes[i].reg && result.writes[i].value==second.writes[i].value,"no omitted programming input");
'''
    code+='return 0;}\n';harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'native/adlx_voice.c',ROOT/'native/adlx_voice.h',ROOT/'native/audio.h',ROOT/'c/adlib.c',ROOT/'c/sound_engine.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',ROOT/'c/platform.h'],unwind=15,timeout=a.timeout,
        extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
    print(a.mode,result['result'],result['seconds'],result['failures'],flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
