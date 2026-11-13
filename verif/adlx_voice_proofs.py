"""Split actual-C driver properties; normalized physical voice0, full raw words.

Instrument copy and post-copy programming are separate cuts in the actual C
entry. Alias output domains use ordinary external/wrapped/overlapping sources.
The programming cut admits independent final-copy bytes and post-copy source.
"""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from adlx_loader_solver import cbmc
from adlx_voice_build import OUT
NAMES=['SetAdlibChannelVolume','SetAdlibChannelGain','KeyOffAdlibChannel','SetAdlibFrequency']
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['outputs','frame','dependence']);p.add_argument('--operation',choices=['volume','gain','key','frequency','copy','program','selector'],required=True);p.add_argument('--word-memory',action='store_true');p.add_argument('--kernel',action='store_true');p.add_argument('--delta',type=int,default=1);p.add_argument('--saved',type=int,choices=[0,1],default=0);p.add_argument('--source',choices=['alias','external','wrap'],default='alias');p.add_argument('--negative',action='store_true');p.add_argument('--timeout',type=int,default=180);a=p.parse_args();assert 0<a.timeout<=600
    assert -11<=a.delta<=11
    tag=f'-kernel-{a.saved}-{a.source}-{a.delta}' if a.kernel else ''
    folder=OUT/f'proof-{a.operation}-{a.mode}{tag}{"-word" if a.word_memory else ""}{"-negative" if a.negative else ""}';folder.mkdir(parents=True,exist_ok=True)
    literal=(ROOT/'c/adlib.c').read_text();native=(ROOT/'native/adlx_voice.c').read_text();main_source=(ROOT/'native/adlx_main.c').read_text();engine=(ROOT/'c/sound_engine.c').read_text()
    code='''#include "platform.h"
#include "adlx_voice.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
uint8_t ugh_mem[UGH_MEM_SIZE];AudioState nondet_audio(void);AudioVoice nondet_voice(void);uint16_t nondet_u16(void);uint8_t nondet_u8(void);int8_t nondet_i8(void);int16_t nondet_i16(void);
static AudioState reference;static uint8_t stack[1024],source_bytes[12];static uint16_t source_bank,source_offset;
static uint16_t ports[28][2];static unsigned port_count,primary_saved,profile;
static uint8_t voice_byte(const AudioVoice *v,unsigned p) {
 if(p<12) return v->instrument[p];uint16_t word=p<14 ? v->volume : p<16 ? v->gain : p<18 ? v->owner : v->frequency;return (uint8_t)(word>>(8*(p&1u)));
}
uint8_t ugh_read(uint32_t address) {
 unsigned base=(unsigned)SOUND_SEG*16u,p=address-base;uint16_t v=0;
 if(p>=S(AdlibVoiceStates) && p<S(AdlibVoiceStates)+20) return voice_byte(&reference.live[0],p-S(AdlibVoiceStates));
 if(p>=S(SavedAdlibVoiceStates) && p<S(SavedAdlibVoiceStates)+20) return voice_byte(&reference.displaced[0],p-S(SavedAdlibVoiceStates));
 if(p==S(AdlibOperatorOffsets)) return reference.operator_index[0];
 if(p==S(SoundIoDelayMultiplier)) return 1;
 if((p&65534u)==S(MainAdlxPlaying)) v=reference.playing;
 else if((p&65534u)==S(CurrentAdlxSlot)) v=reference.current_channel;
 else if((p&65534u)==S(ReservedAdlibChannelCount)) v=reference.reserved_voices;
 else {
  for(unsigned i=0;i<12;i++) if(address==(unsigned)source_bank*16u+(uint16_t)(source_offset+i)) return source_bytes[i];
  CHECK(address>=0x80000 && address<0x80400,"driver ordinary read footprint");return stack[address-0x80000];
 }
 return (uint8_t)(v>>(8*(p&1u)));
}
static void store_byte(AudioVoice *v,unsigned p,uint8_t value) {
 if(p<12) {v->instrument[p]=value;return;}uint16_t *word=p<14 ? &v->volume : p<16 ? &v->gain : p<18 ? &v->owner : &v->frequency;
 unsigned shift=8*(p&1u);*word=(uint16_t)((*word&~(255u<<shift))|((unsigned)value<<shift));
}
void ugh_write(uint32_t address,uint8_t value) {
 unsigned p=address-(unsigned)SOUND_SEG*16u;
 if(p>=S(AdlibVoiceStates) && p<S(AdlibVoiceStates)+20) {store_byte(&reference.live[0],p-S(AdlibVoiceStates),value);return;}
 if(p>=S(SavedAdlibVoiceStates) && p<S(SavedAdlibVoiceStates)+20) {
  unsigned q=p-S(SavedAdlibVoiceStates);store_byte(&reference.displaced[0],q,value);
  if((profile==0 && q==12) || (profile==1 && q==14) || (profile==4 && q<12)) primary_saved=1;return;
 }
 CHECK(address>=0x80000 && address<0x80400,"driver ordinary store footprint");stack[address-0x80000]=value;
}
void platform_out(uint16_t port,unsigned size,uint32_t value) {CHECK(port_count<28 && size==1,"driver port bound");ports[port_count][0]=port;ports[port_count++][1]=(uint16_t)value;}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r) {CHECK(bank==SOUND_SEG && target==S(SetAdlibChannelVolume),"driver peer target");return c_SetAdlibChannelVolume(r);}
'''
    if a.word_memory:
        code+='''static uint16_t word_stack[512];
static uint16_t driver_read_word(uint16_t bank,uint16_t offset) {
 if(bank==SOUND_SEG) {
  if(offset==S(MainAdlxPlaying)) return reference.playing;
  if(offset==S(CurrentAdlxSlot)) return reference.current_channel;
  if(offset==S(ReservedAdlibChannelCount)) return reference.reserved_voices;
  unsigned q;const AudioVoice *v=0;
  if(offset>=S(AdlibVoiceStates) && offset<S(AdlibVoiceStates)+20) {v=&reference.live[0];q=offset-S(AdlibVoiceStates);}
  else if(offset>=S(SavedAdlibVoiceStates) && offset<S(SavedAdlibVoiceStates)+20) {v=&reference.displaced[0];q=offset-S(SavedAdlibVoiceStates);}
  if(v) {CHECK(!(q&1) && q<19,"aligned voice word");if(q<12) return (uint16_t)(v->instrument[q]|(unsigned)v->instrument[q+1]*256u);return q==12 ? v->volume : q==14 ? v->gain : q==16 ? v->owner : v->frequency;}
 }
 CHECK(bank==0x8000 && offset<1023 && !(offset&1),"aligned driver stack word");return word_stack[offset/2];
}
static void driver_write_word(uint16_t bank,uint16_t offset,uint16_t value) {
 if(bank==SOUND_SEG) {
  unsigned q;AudioVoice *v=0;
  if(offset>=S(AdlibVoiceStates) && offset<S(AdlibVoiceStates)+20) {v=&reference.live[0];q=offset-S(AdlibVoiceStates);}
  else if(offset>=S(SavedAdlibVoiceStates) && offset<S(SavedAdlibVoiceStates)+20) {v=&reference.displaced[0];q=offset-S(SavedAdlibVoiceStates);}
  CHECK(v && !(q&1) && q>=12 && q<19,"driver voice word store");
  if(q==12) v->volume=value;else if(q==14) v->gain=value;else if(q==16) v->owner=value;else v->frequency=value;return;
 }
 CHECK(bank==0x8000 && offset<1023 && !(offset&1),"aligned driver stack store");word_stack[offset/2]=value;stack[offset]=(uint8_t)value;stack[offset+1]=(uint8_t)(value>>8);
}
static uint16_t driver_arg(Regs *r,unsigned n) {return driver_read_word(r->ss,(uint16_t)(r->sp+4+n));}
#define rd16 driver_read_word
#define wr16 driver_write_word
#define arg16 driver_arg
'''
    if a.kernel:
        code+=literal[:literal.index('/* BH=register')]
        for name in dict.fromkeys(['c_WriteAdlibRegister','c_SetAdlibChannelVolume',*(['c_'+NAMES[['volume','gain','key','frequency'].index(a.operation)]] if a.operation in ['volume','gain','key','frequency'] else [])]):
            code+=function(literal,name if name.startswith('c_') else 'c_'+name)
    else:code+=literal[:literal.index('/* No stack args.')]
    delay=function(engine,'c_DelaySoundIo');loop='    uint16_t remaining=product;\n    do { remaining=(uint16_t)(remaining-1); } while(remaining);\n';assert loop in delay;code+=delay.replace(loop,'/* Finite LOOP state contract, exhaustively checked separately. */\n')
    load=function(literal,'c_LoadAdlibInstrument')
    if a.kernel:
        original_copy='    for(unsigned k=0;k<12;k++) wr8(r->cs,(uint16_t)(dest+k),rd8(bank,(uint16_t)(source+k)));'
        assert original_copy in load
        code+='static int reference_copy(Regs *r,uint16_t source,uint16_t bank,uint16_t dest) {flag(r,DF,0);\n'+original_copy+'return 0;}\n'
    else:
        copy=load[:load.index('    if(displaced) return UGH_OK;')]+'    return UGH_OK;\n}\n';code+=copy.replace('EXPORT int c_LoadAdlibInstrument','static int reference_copy',1)
    code+='static int reference_selector(Regs *r,uint16_t ch) {\n'+load[load.index('    int displaced='):load.index('    dest=')]+ 'return displaced;}\n'
    code+='static int reference_program(Regs *r,uint16_t channel,uint16_t source,uint16_t bank) {uint8_t ch=(uint8_t)channel;uint16_t sp=r->sp,i=(uint16_t)(ch*20);\n'+load[load.index('    uint8_t op='):]
    if a.negative:
        assert a.operation=='copy'
        native=native.replace('if(alias<0) return source->bytes[i];','if(alias<0 || alias<24) return source->bytes[i];')
    if a.kernel:
        needed={'volume':['voice_append','voice_level','voice_volume'],
            'gain':['voice_append','voice_main_writes','voice_gain'],
            'key':['voice_append','voice_main_writes','voice_live'],
            'frequency':['voice_append','voice_main_writes','voice_live'],
            'copy':['voice_source_byte','voice_instrument_saved','voice_copy_instrument','voice_capture_instrument'],
            'program':['voice_append','voice_level','voice_volume','voice_program_instrument'],
            'selector':['voice_instrument_saved']}[a.operation]
        if a.operation in ['gain','key','frequency','program']:code+=main_source
        code+=''.join(function(native,n) for n in needed)
    else:code+=main_source+native
    operation=['volume','gain','key','frequency','copy','program','selector'].index(a.operation)
    code+='''static int within(uint8_t *p,void *f,unsigned n) {return p>=(uint8_t *)f && p<(uint8_t *)f+n;}
static void equal_voice(const AudioVoice *a,const AudioVoice *b) {for(unsigned i=0;i<12;i++) CHECK(a->instrument[i]==b->instrument[i],"selected instrument byte output");CHECK(a->volume==b->volume && a->gain==b->gain && a->owner==b->owner && a->frequency==b->frequency,"all selected voice word outputs");}
int main(void) {
 reference=(AudioState){0};reference.live[0]=nondet_voice();reference.displaced[0]=nondet_voice();reference.playing=nondet_u16();reference.current_channel=nondet_u16();reference.reserved_voices=nondet_u16();reference.operator_index[0]=nondet_u8();
 AudioState native=reference;AudioVoiceResult result={0};result.channel=0;result.first_reserved=(uint8_t)(9-(uint8_t)native.reserved_voices);
 AudioInstrumentSource source;for(unsigned i=0;i<12;i++) {source.bytes[i]=nondet_u8();source.alias[i]=-1;source_bytes[i]=source.bytes[i];}
 uint16_t raw_channel=nondet_u16(),value=nondet_u16();
'''+f' profile={operation};\n'
    if a.word_memory:code+='raw_channel=(uint16_t)(raw_channel&65280u);\n'
    if operation==6:code+='result.channel=nondet_u8();__CPROVER_assume(result.channel<9);\n'
    def scalar(state,res):
        if not a.kernel:return f'{res}=audio_voice_step(&{state},(AudioVoiceOperation){operation},raw_channel,value,0);'
        if operation==0:return f'{res}.displaced=voice_volume(&{state},&{res},(uint8_t)value);'
        if operation==1:return f'voice_gain(&{state},&{res},(uint8_t)value);'
        return f'voice_live(&{state},&{res},'+('AUDIO_KEY_OFF' if operation==2 else 'AUDIO_FREQUENCY')+',value);'
    if a.mode=='outputs':
        code+='''Regs r={0};r.cs=SOUND_SEG;r.ss=0x8000;r.sp=0x200;r.flags=nondet_u16();source_bank=0x6000;source_offset=0x100;
'''
        if operation<4:
            code+=f'''__CPROVER_assume((uint8_t)raw_channel==0 || (uint8_t)raw_channel>=9);wr16(r.ss,0x204,raw_channel);wr16(r.ss,0x206,value);c_{NAMES[operation]}(&r);
{scalar('native','result')}
 CHECK(result.channel==(uint8_t)raw_channel && result.displaced==primary_saved,"channel-byte rejection and primary saved routing");
'''
        elif operation==4:
            if a.kernel:
                code+=f'uint8_t kind={0 if a.source=="external" else 3 if a.source=="wrap" else 1+a.saved};int16_t delta={a.delta};\n'
            else:code+='uint8_t kind=nondet_u8();__CPROVER_assume(kind<4);int16_t delta=nondet_i16();__CPROVER_assume(delta>=-11 && delta<=11);\n'
            code+='''__CPROVER_assume((uint8_t)raw_channel==0);
 if(kind==1 || kind==2) {source_bank=SOUND_SEG;source_offset=(uint16_t)((kind==1 ? S(AdlibVoiceStates) : S(SavedAdlibVoiceStates))+delta);}else if(kind==3) source_offset=0xfff9;
 for(unsigned i=0;i<12;i++) {
  uint32_t p=(unsigned)source_bank*16u+(uint16_t)(source_offset+i),live=(unsigned)SOUND_SEG*16u+S(AdlibVoiceStates),saved=(unsigned)SOUND_SEG*16u+S(SavedAdlibVoiceStates);source.bytes[i]=ugh_read(p);
  if(p>=live && p<live+12) source.alias[i]=(int8_t)(p-live);else if(p>=saved && p<saved+12) source.alias[i]=(int8_t)(p-saved+12);
 }
'''
            if a.kernel:
                code+=f'reference_copy(&r,source_offset,source_bank,{"S(SavedAdlibVoiceStates)" if a.saved else "S(AdlibVoiceStates)"});result.displaced={a.saved};\n'
            else:code+='wr16(r.ss,0x204,raw_channel);wr16(r.ss,0x206,source_offset);wr16(r.ss,0x208,source_bank);reference_copy(&r);result.displaced=voice_instrument_saved(&native,&result);\n'
            code+='''voice_copy_instrument(&native,&result,&source);
 CHECK(result.displaced==primary_saved,"load uses exact owner12 without playing gate");uint8_t captured[12];voice_capture_instrument(&native,&result,&source,captured);
 for(unsigned i=0;i<12;i++) CHECK(captured[i]==ugh_read((unsigned)source_bank*16u+(uint16_t)(source_offset+i)),"post-copy source reread differs from copied destination");
'''
        elif operation==6:
            code+='CHECK(reference_selector(&r,result.channel)==voice_instrument_saved(&native,&result),"actual instrument owner/reservation selector");\n'
        else:
            code+='''reference_program(&r,0,source_offset,source_bank);voice_program_instrument(&native,&result,source_bytes);
'''
        code+='''equal_voice(&reference.live[0],&native.live[0]);equal_voice(&reference.displaced[0],&native.displaced[0]);CHECK(native.reserved_voices==reference.reserved_voices,"temporary live routing restored");
 CHECK(result.write_count<=14 && port_count==result.write_count*2,"ordered port count");for(unsigned i=0;i<14;i++) if(i<result.write_count) CHECK(ports[2*i][0]==0x388 && ports[2*i+1][0]==0x389 && ports[2*i][1]==result.writes[i].reg && ports[2*i+1][1]==result.writes[i].value,"exact ordered driver writes");
'''
    else:
        code+='native=nondet_audio();result.first_reserved=(uint8_t)(9-(uint8_t)native.reserved_voices);\n'
        if operation==4:code+='for(unsigned i=0;i<12;i++) {source.alias[i]=nondet_i8();__CPROVER_assume(source.alias[i]>=-1 && source.alias[i]<=23);}\n'
        def step(state,res):
            if operation<4:return scalar(state,res)
            if operation==4:return (f'{res}.displaced={a.saved};' if a.kernel else f'{res}.displaced=voice_instrument_saved(&{state},&{res});')+f'voice_copy_instrument(&{state},&{res},&source);uint8_t capture_{state}[12];voice_capture_instrument(&{state},&{res},&source,capture_{state});'
            if operation==6:return f'{res}.displaced=voice_instrument_saved(&{state},&{res});'
            return f'voice_program_instrument(&{state},&{res},source_bytes);'
        if a.mode=='frame':
            code+='''unsigned i=nondet_u16();__CPROVER_assume(i<sizeof(native));uint8_t *p=(uint8_t *)&native+i;__CPROVER_assume(!within(p,&native.live[0],sizeof(AudioVoice)) && !within(p,&native.displaced[0],sizeof(AudioVoice)));uint8_t old=*p;
'''+step('native','result')+'CHECK(*p==old,"every other native state byte unchanged");\n'
            if operation==4:code=code.replace('!within(p,&native.live[0],sizeof(AudioVoice)) && !within(p,&native.displaced[0],sizeof(AudioVoice))','!within(p,&native.live[0].instrument,12) && !within(p,&native.displaced[0].instrument,12)')
            if operation==5:code=code.replace('!within(p,&native.live[0],sizeof(AudioVoice)) && !within(p,&native.displaced[0],sizeof(AudioVoice))','!within(p,&native.live[0].volume,1) && !within(p,&native.displaced[0].volume,1) && !within(p,&native.live[0].owner,2)')
            if operation==6:code=code.replace('!within(p,&native.live[0],sizeof(AudioVoice)) && !within(p,&native.displaced[0],sizeof(AudioVoice))','1')
        else:
            code+='''AudioState other=nondet_audio();other.live[0]=native.live[0];other.displaced[0]=native.displaced[0];other.playing=native.playing;other.current_channel=native.current_channel;other.reserved_voices=native.reserved_voices;other.operator_index[0]=native.operator_index[0];AudioVoiceResult second={0};second.channel=result.channel;second.first_reserved=result.first_reserved;
'''+step('native','result')+step('other','second')+'''
 equal_voice(&native.live[0],&other.live[0]);equal_voice(&native.displaced[0],&other.displaced[0]);CHECK(result.write_count==second.write_count && result.displaced==second.displaced && result.reservation_checked==second.reservation_checked,"driver result dependence");
 CHECK(result.write_count<=14,"driver write bound");for(unsigned i=0;i<14;i++) if(i<result.write_count) CHECK(result.writes[i].reg==second.writes[i].reg && result.writes[i].value==second.writes[i].value,"no omitted driver programming input");
'''
            if operation==4:code+='for(unsigned i=0;i<12;i++) CHECK(capture_native[i]==capture_other[i],"source capture dependence");\n'
    code+='return 0;}\n';harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'native/adlx_voice.c',ROOT/'native/adlx_voice.h',ROOT/'native/adlx_main.c',ROOT/'native/audio.h',ROOT/'c/adlib.c',ROOT/'c/sound_engine.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=25,timeout=a.timeout,extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
    print(a.operation,a.mode,result['result'],result['seconds'],result['failures'],flush=True);assert result['result']==('FAIL' if a.negative else 'PASS')
if __name__=='__main__':main()
