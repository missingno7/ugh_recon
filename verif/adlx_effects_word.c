/* A normalized word-backed projection, not an interpreter model. Actual L1
 * bodies use the real ugh.h byte/word accessors over these bindings. Every
 * owned scalar/byte is arbitrary; unbound memory accesses are assertions.
 * A native step is compared at the STOP/TIMER request boundary, before C.
 * Full physical-memory/register bridge comparisons run in the compiled DLLs. */
#include "pair.inc"
uint8_t ugh_mem[UGH_MEM_SIZE];
static AudioState reference_state;
static uint16_t selected_record,payload_index,delay_word;
static unsigned selected_index;
static uint8_t operands[12],stack_bytes[128];
static uint32_t ports[28][3],port_count,timer_count,stop_count;
static uint16_t timer_args[3],stop_slot;
#ifdef VOICE_CONTRACT
static int reference_voice(Regs *r,AudioMainOperation operation);
#endif
#ifdef __CPROVER__
AudioState nondet_audio(void);
#endif

static uint16_t channel_word(const AudioChannel *c,unsigned field)
{
    switch(field) {
    case 0:return (uint16_t)c->age;case 2:return (uint16_t)(c->age>>16);
    case 4:return c->repeats;case 6:return c->start.index;
    case 8:return (uint16_t)((c->start.window-ugh_mem)/16);
    case 10:return c->length;case 12:return c->sample_mode;case 14:return c->sample_rate;
    case 16:return c->cursor.index;case 18:return (uint16_t)((c->cursor.window-ugh_mem)/16);
    case 20:return c->sample_half_length;case 22:return c->reserved_word;
    case 24:return c->sample_selector;case 26:return c->sample_accumulator;
    case 28:return c->volume;case 30:return (uint16_t)c->deadline;case 32:return (uint16_t)(c->deadline>>16);
    case 34:return c->voice_count;case 36:return c->first_voice;case 38:return c->step_q8;case 40:return c->control;
    }
    CHECK(0,"channel word read footprint");return 0;
}
static void put_channel_word(AudioChannel *c,unsigned field,uint16_t value)
{
    switch(field) {
    case 4:c->repeats=value;return;
    case 16:c->cursor.index=value;return;
    case 18:c->cursor.window=ugh_mem+(uint32_t)value*16u;return;
    case 30:c->deadline=(c->deadline&0xffff0000u)|value;return;
    case 32:c->deadline=(c->deadline&65535u)|((uint32_t)value<<16);return;
    case 38:c->step_q8=value;return;
    }
    CHECK(0,"channel word write footprint");
}
static uint16_t voice_word(const AudioVoice *v,unsigned field)
{
    if(field<12) return (uint16_t)(v->instrument[field]+(unsigned)v->instrument[field+1]*256u);
    switch(field) {
    case 12:return v->volume;case 14:return v->gain;case 16:return v->owner;case 18:return v->frequency;
    }
    CHECK(0,"voice word read footprint");return 0;
}
static void put_voice_word(AudioVoice *v,unsigned field,uint16_t value)
{
    if(field<12) {v->instrument[field]=(uint8_t)value;v->instrument[field+1]=(uint8_t)(value>>8);return;}
    switch(field) {
    case 12:v->volume=value;return;case 14:v->gain=value;return;
    case 16:v->owner=value;return;case 18:v->frequency=value;return;
    }
    CHECK(0,"voice word write footprint");
}
static AudioVoice *voice_at(unsigned offset,unsigned *field)
{
    unsigned relative=offset-S(AdlibVoiceStates);*field=(relative%20u)&65534u;
    if(relative<180) return &reference_state.live[relative/20];
    if(relative<360) return &reference_state.displaced[(relative-180)/20];
    CHECK(0,"voice view footprint");return &reference_state.live[0];
}
static uint16_t global_word(unsigned offset)
{
    if(offset==S(MainAdlxPlaying)) return reference_state.playing;
    if(offset==S(CurrentAdlxSlot)) return reference_state.current_channel;
    if(offset==S(ReservedAdlibChannelCount)) return reference_state.reserved_voices;
    if(offset==S(AdlxTimerPeriod)) return reference_state.timer_period;
    if(offset==S(AdlxPlaybackTimerHandle)) return reference_state.playback_timer_handle;
    CHECK(0,"global read footprint");return 0;
}
static uint16_t word_read(uint16_t bank,uint16_t offset)
{
    if(bank==SOUND_SEG) {
        if(offset==S(CurrentAdlxRecordOffset)) return selected_record;
        if(offset>=selected_record && offset<selected_record+42u) {
            unsigned relative=offset-selected_record;
            CHECK(!(relative&1u),"aligned channel word");return channel_word(&reference_state.channels[selected_index],relative%42);
        }
        if(offset>=S(AdlibVoiceStates) && offset<S(SavedAdlibVoiceStates)+180) {
            unsigned field;AudioVoice *v=voice_at(offset,&field);CHECK(!(offset&1u),"aligned voice word");return voice_word(v,field);
        }
        return global_word(offset);
    }
    if(bank==0x6000) {
        CHECK(offset==payload_index,"word operand starts at payload cursor");
        return (uint16_t)(operands[0]+(unsigned)operands[1]*256u);
    }
    uint32_t address=(uint32_t)bank*16u+offset;
    return (uint16_t)(ugh_read(address)|(unsigned)ugh_read(address+1)*256u);
}
static void word_write(uint16_t bank,uint16_t offset,uint16_t value)
{
    if(bank==SOUND_SEG) {
        if(offset>=selected_record && offset<selected_record+42u) {
            unsigned relative=offset-selected_record;
            CHECK(!(relative&1u),"aligned channel store");put_channel_word(&reference_state.channels[selected_index],relative%42,value);return;
        }
        if(offset>=S(AdlibVoiceStates) && offset<S(SavedAdlibVoiceStates)+180) {
#ifdef VOICE_CONTRACT
            CHECK(native_channel<=9 && offset==S(AdlibChannelOwnerSlot)+20u*native_channel,"pre-loader owner address binding");
            CHECK(S(AdlibChannelOwnerSlot)+20u*9==S(SavedAdlibVoiceStates)+16,"physical9 alias layout");
            if(native_channel==9) reference_state.displaced[0].owner=value;
            else reference_state.live[native_channel].owner=value;
#else
            unsigned field;AudioVoice *v=voice_at(offset,&field);CHECK(!(offset&1u),"aligned voice store");put_voice_word(v,field,value);return;
#endif
            return;
        }
        CHECK(offset==S(AdlxTimerPeriod),"global word store");reference_state.timer_period=value;return;
    }
    uint32_t address=(uint32_t)bank*16u+offset;ugh_write(address,(uint8_t)value);ugh_write(address+1,(uint8_t)(value>>8));
}
uint8_t ugh_read(uint32_t address)
{
    uint32_t base=(uint32_t)SOUND_SEG*16u;
    if(address>=base && address<base+65536u) {
        unsigned offset=address-base;
        if(offset>=S(CurrentAdlxRecordOffset) && offset<S(CurrentAdlxRecordOffset)+2)
            return (uint8_t)(selected_record>>(8u*(offset-S(CurrentAdlxRecordOffset))));
        if(offset>=S(AdlibOperatorOffsets) && offset<S(AdlibOperatorOffsets)+9)
            return reference_state.operator_index[offset-S(AdlibOperatorOffsets)];
        if(offset==S(SoundIoDelayMultiplier)) return (uint8_t)delay_word;
        if(offset>=selected_record && offset<selected_record+42u) {
            unsigned relative=offset-selected_record;
            uint16_t value=channel_word(&reference_state.channels[selected_index],(relative%42)&65534u);
            return (uint8_t)(value>>(8u*(relative&1u)));
        }
        if(offset>=S(AdlibVoiceStates) && offset<S(SavedAdlibVoiceStates)+180) {
            unsigned field;AudioVoice *v=voice_at(offset,&field);
            return (uint8_t)(voice_word(v,field)>>(8u*(offset&1u)));
        }
        return (uint8_t)(global_word(offset&65534u)>>(8u*(offset&1u)));
    }
    if(address>=0x60000u && address<=0x70000u) {
        if(address==0x60000u+payload_index) return operands[0];
        uint16_t index=(uint16_t)((uint16_t)(address-0x60000u)-payload_index);
        CHECK(index<12,"operand footprint");return operands[index];
    }
    CHECK(address>=0x70f80u && address<0x71000u,"stack read footprint");return stack_bytes[address-0x70f80u];
}
void ugh_write(uint32_t address,uint8_t byte)
{
    uint32_t base=(uint32_t)SOUND_SEG*16u;
    if(address>=base && address<base+65536u) {
        unsigned offset=address-base,shift=8u*(offset&1u);
        uint16_t value=(uint16_t)((ugh_read(address-(offset&1u))|((unsigned)ugh_read(address-(offset&1u)+1)*256u))&~(255u<<shift));
        value=(uint16_t)(value|((unsigned)byte<<shift));
        if(offset>=selected_record && offset<selected_record+42u) {
            unsigned relative=offset-selected_record;
            put_channel_word(&reference_state.channels[selected_index],(relative%42)&65534u,value);return;
        }
        if(offset>=S(AdlibVoiceStates) && offset<S(SavedAdlibVoiceStates)+180) {
            unsigned field;AudioVoice *v=voice_at(offset,&field);put_voice_word(v,field,value);return;
        }
        CHECK((offset&65534u)==S(AdlxTimerPeriod),"global write footprint");reference_state.timer_period=value;return;
    }
    CHECK(address>=0x70f80u && address<0x71000u,"stack write footprint");stack_bytes[address-0x70f80u]=byte;
}
void platform_out(uint16_t port,unsigned size,uint32_t value)
{
    CHECK(port_count<28,"port count");ports[port_count][0]=port;ports[port_count][1]=size;ports[port_count][2]=value;port_count++;
}
int ugh_dispatch(uint16_t segment,uint16_t offset,Regs *r)
{
    if(segment==SOUND_SEG) {
#ifdef VOICE_CONTRACT
        if(offset==S(SetAdlibFrequency)) return reference_voice(r,AUDIO_FREQUENCY);
        if(offset==S(KeyOffAdlibChannel)) return reference_voice(r,AUDIO_KEY_OFF);
        if(offset==S(SetAdlibChannelGain)) return reference_voice(r,AUDIO_GAIN);
        if(offset==S(LoadAdlibInstrument)) return reference_voice(r,AUDIO_INSTRUMENT);
#else
        if(offset==S(SetAdlibFrequency)) return c_SetAdlibFrequency(r);
        if(offset==S(KeyOffAdlibChannel)) return c_KeyOffAdlibChannel(r);
        if(offset==S(SetAdlibChannelGain)) return c_SetAdlibChannelGain(r);
        if(offset==S(SetAdlibChannelVolume)) return c_SetAdlibChannelVolume(r);
        if(offset==S(LoadAdlibInstrument)) return c_LoadAdlibInstrument(r);
#endif
    }
    if(segment==UGH_SEG_C && offset==UGH_O_C_StopAdlibTrackChannel) {
        stop_count++;stop_slot=arg16(r,0);return UGH_OK;
    }
    CHECK(segment==TIMER_SEG && offset==T(SetTimerCallbackInterval),"complete external targets");
    timer_count++;timer_args[0]=r->ax;timer_args[1]=r->bx;timer_args[2]=r->cx;return UGH_OK;
}
int c_RunMainAdlxEvents(Regs *r) {(void)r;return 0;}
int c_RunEffectAdlxEvents(Regs *r) {(void)r;return 0;}

/* COMPARE_HELPERS */
#ifdef VOICE_CONTRACT
#include "adlx_effects_voice_contract.h"
#endif

int main(void)
{
    reference_state=nondet_audio();
    for(unsigned i=0;i<13;i++) {
        reference_state.channels[i].start.window=ugh_mem+(uint32_t)N16()*16u;
        reference_state.channels[i].cursor.window=ugh_mem+(uint32_t)N16()*16u;
    }
    reference_state.section_start.window=ugh_mem;reference_state.section_end.window=ugh_mem;
    unsigned selected=8u+(N16()&3u);
#if RECORD >= 0
    selected=RECORD;
#endif
    selected_record=(uint16_t)(S(AudioChannelStates)+selected*42u);selected_index=selected;
    Regs r={0};r.ax=N16();r.flags=N16();r.di=N16();r.cs=SOUND_SEG;r.es=0x6000;r.ss=0x7000;r.sp=0x1000;
    r.ax=OP<8 ? (uint16_t)((r.ax&0xff0fu)|OP*16) : (uint16_t)((r.ax&0xff7fu)|128);
    payload_index=r.di;delay_word=N16();
    for(unsigned i=0;i<12;i++) operands[i]=N8();
#if CHANNEL >= 0 && CHANNEL < 10
    reference_state.channels[selected].first_voice=(uint16_t)((reference_state.channels[selected].first_voice&65280u)|(uint8_t)(CHANNEL-(r.ax&15u)));
#elif CHANNEL == 10
    __CPROVER_assume((uint8_t)((r.ax&15u)+(uint8_t)reference_state.channels[selected].first_voice)>=10);
#endif
    AudioState native=reference_state;
    AudioCursor cursor={ugh_mem+0x60000u,r.di};
    AudioEffectsResult output=audio_effects_step(&native,&native.channels[selected],(AudioMainOperation)OP,(uint8_t)r.ax,operands,&cursor);
    int result=reference_event(&r);
    compare_state(&native,&reference_state);
    CHECK(r.di==cursor.index,"event consumption");
    CHECK(result==(output.exit==AUDIO_EFFECTS_DIVIDE_FAULT ? UGH_UNSUPPORTED : UGH_OK),"step status");
    CHECK(port_count==2u*output.write_count,"ordered OPL count");
    for(unsigned i=0;i<output.write_count;i++) {
        CHECK(ports[2*i][0]==0x388 && ports[2*i][1]==1 && ports[2*i][2]==output.writes[i].reg,"ordered OPL address");
        CHECK(ports[2*i+1][0]==0x389 && ports[2*i+1][1]==1 && ports[2*i+1][2]==output.writes[i].value,"ordered OPL value");
    }
    CHECK(stop_count==output.stop_request,"stop request count");
    if(stop_count) CHECK(stop_slot==native.current_channel,"stop raw identity");
    CHECK(timer_count==output.timer_request,"timer request count");
    if(timer_count) CHECK(timer_args[0]==native.playback_timer_handle && timer_args[1]==output.requested_period && timer_args[2]==0,"timer request tuple");
#ifdef VOICE_CONTRACT
    CHECK(native_voice_calls==reference_voice_calls,"voice call multiplicity");
#endif
    return 0;
}
