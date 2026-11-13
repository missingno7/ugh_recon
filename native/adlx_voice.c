#include "adlx_voice.h"

static void voice_append(AudioVoiceResult *result,AudioRegisterWrite write)
{result->writes[result->write_count++]=write;}
static void voice_main_writes(AudioVoiceResult *result,const AudioMainResult *main)
{
    /* Only gain/key-off/frequency use this adapter: at most two writes. */
    for(unsigned i=0;i<2;i++) if(i<main->write_count) voice_append(result,main->writes[i]);
    result->displaced=main->displaced;
}
static uint8_t voice_level(uint8_t level,uint8_t gain,uint8_t volume)
{
    /* Retained: two separately truncated high-byte products, no saturation. */
    unsigned scaled=(((63u-(level&63u))*gain)>>8)*volume;
    return (uint8_t)((63u-(scaled>>8))|(level&192u));
}
static uint8_t voice_volume(AudioState *state,AudioVoiceResult *result,uint8_t volume)
{
    unsigned channel=result->channel;
    if((state->playing&1u) && state->current_channel>=12 &&
       (state->reserved_voices&15u) && channel>=result->first_reserved) {
        state->displaced[channel].volume=(uint16_t)((state->displaced[channel].volume&65280u)|volume);return 1;
    }
    AudioVoice *voice=&state->live[channel];voice->volume=(uint16_t)((voice->volume&65280u)|volume);
    uint8_t op=state->operator_index[channel];
    AudioRegisterWrite carrier={(uint8_t)(op+67u),voice_level(voice->instrument[6],(uint8_t)voice->gain,volume)};
    voice_append(result,carrier);
    if(voice->instrument[10]&1u) {
        AudioRegisterWrite modulator={(uint8_t)(op+64u),voice_level(voice->instrument[1],(uint8_t)voice->gain,volume)};
        voice_append(result,modulator);
    }
    return 0;
}
static uint8_t voice_source_byte(const AudioState *state,const AudioInstrumentSource *source,unsigned channel,unsigned i)
{
    int alias=source->alias[i];
    if(alias<0) return source->bytes[i];
    return alias<12 ? state->live[channel].instrument[alias] : state->displaced[channel].instrument[alias-12];
}
static uint8_t voice_instrument_saved(const AudioState *state,const AudioVoiceResult *result)
{return (uint8_t)(state->current_channel==12 && (state->reserved_voices&15u) && result->channel>=result->first_reserved);}
static void voice_copy_instrument(AudioState *state,const AudioVoiceResult *result,const AudioInstrumentSource *source)
{
    unsigned channel=result->channel;
    AudioVoice *destination=result->displaced ? &state->displaced[channel] : &state->live[channel];
    for(unsigned i=0;i<12;i++) destination->instrument[i]=voice_source_byte(state,source,channel,i);
}
static void voice_capture_instrument(const AudioState *state,const AudioVoiceResult *result,const AudioInstrumentSource *source,uint8_t programmed[12])
{for(unsigned i=0;i<12;i++) programmed[i]=voice_source_byte(state,source,result->channel,i);}
static void voice_program_instrument(AudioState *state,AudioVoiceResult *result,const uint8_t programmed[12])
{
    unsigned channel=result->channel;
    /* Retained: programming rereads the SOURCE after the sequential copy.
     * These bytes need not equal the final copied destination (overlap).
     * Reuse the accepted programmer's twelve-write prefix in private working
     * state; its extra copy/level stores must not replace the real copy. */
    AudioState programming=*state;programming.reserved_voices=0;AudioCursor cursor={0};
    AudioMainResult loaded=audio_main_step(&programming,AUDIO_INSTRUMENT,(uint8_t)channel,programmed,&cursor);
    for(unsigned i=0;i<12;i++) voice_append(result,loaded.writes[i]);
    state->live[channel].owner=state->current_channel;
    voice_volume(state,result,(uint8_t)state->live[channel].volume);
}
static void voice_instrument(AudioState *state,AudioVoiceResult *result,const AudioInstrumentSource *source)
{
    result->displaced=voice_instrument_saved(state,result);voice_copy_instrument(state,result,source);
    if(!result->displaced) {
        uint8_t programmed[12];voice_capture_instrument(state,result,source,programmed);
        voice_program_instrument(state,result,programmed);
    }
}
static void voice_gain(AudioState *state,AudioVoiceResult *result,uint8_t value)
{
    result->reservation_checked=(uint8_t)(state->current_channel>=12 && (state->reserved_voices&15u));
    uint8_t bytes[12]={0};bytes[0]=value;AudioCursor cursor={0};
    AudioMainResult gain=audio_main_step(state,AUDIO_GAIN,result->channel,bytes,&cursor);voice_main_writes(result,&gain);
}
static void voice_live(AudioState *state,AudioVoiceResult *result,AudioMainOperation operation,uint16_t value)
{
    /* Standalone key-off/frequency always address LIVE, independently of
     * music ownership. The accepted event's live branch is the same service. */
    uint8_t bytes[12]={0};bytes[0]=(uint8_t)value;bytes[1]=(uint8_t)(value>>8);AudioCursor cursor={0};
    uint16_t reserved=state->reserved_voices;state->reserved_voices=0;
    AudioMainResult live=audio_main_step(state,operation,result->channel,bytes,&cursor);
    state->reserved_voices=reserved;voice_main_writes(result,&live);
}
AudioVoiceResult audio_voice_step(AudioState *state,AudioVoiceOperation operation,
                                 uint16_t channel,uint16_t value,const AudioInstrumentSource *source)
{
    AudioVoiceResult result={0};result.channel=(uint8_t)channel;
    if(result.channel>=9) return result;
    result.first_reserved=(uint8_t)(9u-(uint8_t)state->reserved_voices);
    if(operation==AUDIO_VOICE_VOLUME) {result.displaced=voice_volume(state,&result,(uint8_t)value);return result;}
    if(operation==AUDIO_VOICE_INSTRUMENT) {voice_instrument(state,&result,source);return result;}
    if(operation==AUDIO_VOICE_GAIN) voice_gain(state,&result,(uint8_t)value);
    else voice_live(state,&result,operation==AUDIO_VOICE_KEY_OFF ? AUDIO_KEY_OFF : AUDIO_FREQUENCY,value);
    return result;
}
AudioIoDelay audio_voice_delay(uint8_t factor,uint8_t calibration)
{
    unsigned product=(unsigned)factor*calibration;
    AudioIoDelay delay={product ? product : 65536u,(uint8_t)(product>255)};return delay;
}
AudioRegisterWrite audio_voice_register(uint16_t packed)
{AudioRegisterWrite write={(uint8_t)(packed>>8),(uint8_t)packed};return write;}
