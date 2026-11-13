"""Actual new volume journal versus the actual shared L1 OPL volume driver."""
import argparse,re
from pathlib import Path
from closure_support import ROOT,function
from adlx_loader_solver import cbmc
from adlx_voice_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['outputs','frame','dependence']);p.add_argument('--role',choices=['volume','gain','key','frequency','program'],default='volume');p.add_argument('--timeout',type=int,default=180);a=p.parse_args()
    folder=OUT/('proof-leaf-'+a.role+'-'+a.mode);folder.mkdir(parents=True,exist_ok=True)
    adlib=(ROOT/'c/adlib.c').read_text();native=(ROOT/'native/adlx_voice.c').read_text();engine=(ROOT/'c/sound_engine.c').read_text()
    prefix=adlib[:adlib.index('/* No stack args.')]
    delay=function(engine,'c_DelaySoundIo');loop='    uint16_t remaining=product;\n    do { remaining=(uint16_t)(remaining-1); } while(remaining);\n';assert loop in delay;delay=delay.replace(loop,'/* Finite state-only delay contract. */\n')
    needed={'volume':['voice_append','voice_level','voice_volume'],'gain':['voice_append','voice_main_writes','voice_gain'],'key':['voice_append','voice_main_writes','voice_live'],'frequency':['voice_append','voice_main_writes','voice_live'],'program':['voice_append','voice_level','voice_volume','voice_program_instrument']}[a.role]
    code='''#include "platform.h"
#include "adlx_voice.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
uint8_t ugh_mem[UGH_MEM_SIZE];
AudioState nondet_audio(void);AudioVoice nondet_voice(void);uint16_t nondet_u16(void);uint8_t nondet_u8(void);
static AudioState reference;static uint8_t stack[1024];static uint16_t ports[28][2];static unsigned port_count;static uint8_t post_source[12];
'''+prefix+delay+((ROOT/'native/adlx_main.c').read_text() if a.role!='volume' else '')+''.join(function(native,n) for n in needed)
    if a.role=='program':
        load=function(adlib,'c_LoadAdlibInstrument');code+='static int reference_program(Regs *r) {uint16_t sp=r->sp,i=0,source=0x100,bank=0x6000,channel=0;uint8_t ch=0;\n'+load[load.index('    uint8_t op='):]

    code+='''static uint16_t word(const AudioVoice *v,unsigned p) {
 if(p<12) return (uint16_t)(v->instrument[p]|(unsigned)v->instrument[p+1]*256u);
 return p==12 ? v->volume : p==14 ? v->gain : p==16 ? v->owner : v->frequency;
}
uint8_t ugh_read(uint32_t address) {
 unsigned base=(unsigned)SOUND_SEG*16u,p=address-base;uint16_t value=0;
 if(address>=0x60100 && address<0x6010c) return post_source[address-0x60100];
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
 if(p==S(AdlibChannelGain)) {reference.live[0].gain=(uint16_t)((reference.live[0].gain&65280u)|value);return;}
 if(p==S(DisplacedAdlibGain)) {reference.displaced[0].gain=(uint16_t)((reference.displaced[0].gain&65280u)|value);return;}
 if(p==S(AdlibPackedFrequency) || p==S(AdlibPackedFrequency)+1) {unsigned shift=8*(p-S(AdlibPackedFrequency));reference.live[0].frequency=(uint16_t)((reference.live[0].frequency&~(255u<<shift))|((unsigned)value<<shift));return;}
 if(p==S(AdlibChannelOwnerSlot) || p==S(AdlibChannelOwnerSlot)+1) {unsigned shift=8*(p-S(AdlibChannelOwnerSlot));reference.live[0].owner=(uint16_t)((reference.live[0].owner&~(255u<<shift))|((unsigned)value<<shift));return;}
 if(p==S(DisplacedAdlibVolume)) {reference.displaced[0].volume=(uint16_t)((reference.displaced[0].volume&65280u)|value);return;}
 CHECK(address>=0x80000 && address<0x80400,"volume stack write");stack[address-0x80000]=value;
}
void platform_out(uint16_t port,unsigned size,uint32_t value) {
 CHECK(port_count<28 && size==1,"volume port bound");ports[port_count][0]=port;ports[port_count][1]=(uint16_t)value;port_count++;
}
int ugh_dispatch(uint16_t b,uint16_t t,Regs *r) {CHECK(b==SOUND_SEG && t==S(SetAdlibChannelVolume),"voice refresh peer");return c_SetAdlibChannelVolume(r);}
static int within(uint8_t *p,void *f,unsigned n) {return p>=(uint8_t *)f && p<(uint8_t *)f+n;}
int main(void) {
 reference=(AudioState){0};reference.playing=nondet_u16();reference.current_channel=nondet_u16();reference.reserved_voices=nondet_u16();
 reference.operator_index[0]=nondet_u8();reference.live[0]=nondet_voice();reference.displaced[0]=nondet_voice();
 AudioState native=reference;AudioVoiceResult result={0};result.channel=0;result.first_reserved=(uint8_t)(9-(uint8_t)native.reserved_voices);uint16_t volume=nondet_u16();for(unsigned i=0;i<12;i++) post_source[i]=nondet_u8();
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
    def invoke(state,res):
        if a.role=='volume':return f'{res}.displaced=voice_volume(&{state},&{res},(uint8_t)volume);'
        if a.role=='gain':return f'voice_gain(&{state},&{res},(uint8_t)volume);'
        if a.role=='program':return f'voice_program_instrument(&{state},&{res},post_source);'
        return f'voice_live(&{state},&{res},'+('AUDIO_KEY_OFF' if a.role=='key' else 'AUDIO_FREQUENCY')+',volume);'
    code=code.replace('result.displaced=voice_volume(&native,&result,volume);',invoke('native','result')).replace('second.displaced=voice_volume(&other,&second,volume);',invoke('other','second'))
    cname={'volume':'c_SetAdlibChannelVolume(&r)','gain':'c_SetAdlibChannelGain(&r)','key':'c_KeyOffAdlibChannel(&r)','frequency':'c_SetAdlibFrequency(&r)','program':'reference_program(&r)'}[a.role]
    code=code.replace('c_SetAdlibChannelVolume(&r);',cname+';')
    # All selected word outputs are cheap to compare; the frame handles every other byte.
    code=code.replace('"live/saved stale volume words");','"live/saved stale volume words");CHECK(reference.live[0].gain==native.live[0].gain && reference.displaced[0].gain==native.displaced[0].gain && reference.live[0].owner==native.live[0].owner && reference.live[0].frequency==native.live[0].frequency,"other selected word outputs");')
    if a.role in ['gain','key','frequency','program']:
        extra=''
        if a.role=='gain':extra=' && !within(p,&native.live[0].gain,1) && !within(p,&native.displaced[0].gain,1)'
        if a.role=='key':extra=' && !within(p,(uint8_t *)&native.live[0].frequency+1,1)'
        if a.role=='frequency':extra=' && !within(p,&native.live[0].frequency,2)'
        if a.role=='program':extra=' && !within(p,&native.live[0].owner,2)'
        code=code.replace('!within(p,&native.displaced[0].volume,1))','!within(p,&native.displaced[0].volume,1)'+extra+')')
        # Conservative selected-record dependence, varying all other state independently.
        code=code.replace('other.operator_index[0]=native.operator_index[0];','other.live[0]=native.live[0];other.displaced[0]=native.displaced[0];other.operator_index[0]=native.operator_index[0];')
    code+='return 0;}\n';harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'native/adlx_voice.c',ROOT/'native/adlx_voice.h',ROOT/'native/audio.h',ROOT/'native/adlx_main.c',ROOT/'c/adlib.c',ROOT/'c/sound_engine.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',ROOT/'c/platform.h'],unwind=15,timeout=a.timeout,
        extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
    print(a.mode,result['result'],result['seconds'],result['failures'],flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
