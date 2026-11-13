#include "platform.h"
#include "audio_projection.h"
#include "../adlx_voice.h"
int l1_LoadAdlibInstrument(Regs *r);

static void voice_delay_flags(Regs *r,uint8_t factor)
{AudioIoDelay delay=audio_voice_delay(factor,rd8(r->cs,S(SoundIoDelayMultiplier)));flag(r,CF,delay.overflow);flag(r,OF,delay.overflow);}
static void voice_emit(const AudioRegisterWrite *writes,unsigned count)
{for(unsigned i=0;i<count;i++) {platform_out(0x388,1,writes[i].reg);platform_out(0x389,1,writes[i].value);}}
static int voice_source(Regs *r,uint8_t channel,AudioInstrumentSource *source)
{
    AudioCursor cursor=audio_bridge_cursor(arg16(r,4),arg16(r,2));
    uint16_t offset=cursor.index,bank=audio_bridge_bank(cursor);
    uint32_t live=lin(r->cs,(uint16_t)(S(AdlibVoiceStates)+20u*channel));
    uint32_t saved=lin(r->cs,(uint16_t)(S(SavedAdlibVoiceStates)+20u*channel));
    /* Test all wrapping effective offsets before reading MMIO or invoking L2. */
    for(unsigned i=0;i<12;i++) {uint32_t p=lin(bank,(uint16_t)(offset+i));if(p>=0xa0000 && p<0xc0000) return 0;}
    for(unsigned i=0;i<12;i++) {
        uint16_t at=(uint16_t)(offset+i);uint32_t p=lin(bank,at);source->bytes[i]=rd8(bank,at);source->alias[i]=-1;
        if(p>=live && p<live+12) source->alias[i]=(int8_t)(p-live);
        else if(p>=saved && p<saved+12) source->alias[i]=(int8_t)(p-saved+12);
    }
    return 1;
}
static int voice_entry(Regs *r,AudioVoiceOperation operation)
{
    uint16_t channel=arg16(r,0),value=operation==AUDIO_VOICE_KEY_OFF || operation==AUDIO_VOICE_INSTRUMENT ? 0 : arg16(r,2);
    if((uint8_t)channel>=9) return UGH_OK;
    AudioInstrumentSource source={{0},{0}};
    if(operation==AUDIO_VOICE_INSTRUMENT && !voice_source(r,(uint8_t)channel,&source)) return l1_LoadAdlibInstrument(r);
    AudioState state;audio_bridge_project(r->cs,&state);
    AudioVoiceResult result=audio_voice_step(&state,operation,channel,value,&source);
    audio_bridge_publish_voice(r->cs,(uint16_t)(S(AdlibVoiceStates)+20u*result.channel),&state.live[result.channel]);
    audio_bridge_publish_voice(r->cs,(uint16_t)(S(SavedAdlibVoiceStates)+20u*result.channel),&state.displaced[result.channel]);
    voice_emit(result.writes,result.write_count);
    if(operation==AUDIO_VOICE_GAIN) {
        r->ax=(uint16_t)(result.channel*20u);
        if(result.reservation_checked) r->bx=(uint16_t)((r->bx&65280u)|result.first_reserved);
    } else if(operation==AUDIO_VOICE_INSTRUMENT) {
        flag(r,DF,0);r->ax=(uint16_t)(result.channel*20u);
        if(result.displaced) set_al(r,result.first_reserved);
        else {r->ax=state.current_channel;r->bx=(uint16_t)(result.channel*20u);}
    } else if(operation==AUDIO_VOICE_FREQUENCY) flag(r,IF,1);
    if(result.write_count) voice_delay_flags(r,operation==AUDIO_VOICE_KEY_OFF || operation==AUDIO_VOICE_FREQUENCY ? 2 : 4);
    return UGH_OK;
}
EXPORT int c_SetAdlibChannelVolume(Regs *r) {return voice_entry(r,AUDIO_VOICE_VOLUME);}
EXPORT int c_SetAdlibChannelGain(Regs *r) {return voice_entry(r,AUDIO_VOICE_GAIN);}
EXPORT int c_KeyOffAdlibChannel(Regs *r) {return voice_entry(r,AUDIO_VOICE_KEY_OFF);}
EXPORT int c_SetAdlibFrequency(Regs *r) {return voice_entry(r,AUDIO_VOICE_FREQUENCY);}
EXPORT int c_LoadAdlibInstrument(Regs *r) {return voice_entry(r,AUDIO_VOICE_INSTRUMENT);}
EXPORT int c_WriteAdlibRegister(Regs *r)
{AudioRegisterWrite write=audio_voice_register(r->bx);voice_emit(&write,1);voice_delay_flags(r,4);return UGH_OK;}
EXPORT int c_DelaySoundIo(Regs *r) {voice_delay_flags(r,(uint8_t)r->ax);return UGH_OK;}
