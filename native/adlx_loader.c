#include "adlx_loader.h"

static uint16_t audio_adlx_word(AudioCursor input,uint16_t offset)
{
    return (uint16_t)(input.window[offset]+(unsigned)input.window[(unsigned)offset+1]*256u);
}
static uint32_t audio_adlx_size(AudioCursor input,uint16_t offset)
{
    uint16_t first=audio_adlx_word(input,offset);
    uint16_t second=audio_adlx_word(input,(uint16_t)(offset+2));
    return ((uint32_t)(uint8_t)first<<24)|((uint32_t)(first>>8)<<16)|
        ((uint32_t)(uint8_t)second<<8)|(second>>8);
}
static int audio_adlx_tag(AudioCursor input,uint16_t offset,const char tag[4])
{
    for(unsigned i=0;i<4;i++) if(input.window[(uint16_t)(offset+i)]!=(uint8_t)tag[i]) return 0;
    return 1;
}
AudioAdlxLoadResult audio_adlx_load(AudioState *state,uint16_t channel,
    AudioCursor *input,uint16_t repeats,uint16_t device_bits)
{
    AudioAdlxLoadResult result={0};result.value=65535;
    if(!(device_bits&1u) || channel<8 || channel>12) return result;
    uint16_t root=input->index;
    input->index=(uint16_t)(input->index+8);result.stage=AUDIO_ADLX_ROOT_TAG;
    if(!audio_adlx_tag(*input,root,"ADLX")) return result;
    uint16_t header=input->index;
    input->index=(uint16_t)(input->index+8);result.stage=AUDIO_ADLX_HEADER_TAG;
    if(!audio_adlx_tag(*input,header,"AHDR")) return result;
    uint32_t size=audio_adlx_size(*input,(uint16_t)(header+4));
    result.swaps++;result.swap_high=(uint16_t)(size>>16);
    /* Retained low-word chunk skips and fixed resource window. */
    input->index=(uint16_t)(input->index+(uint16_t)size);
    uint16_t map=input->index;
    input->index=(uint16_t)(input->index+8);result.stage=AUDIO_ADLX_MAP_TAG;
    if(!audio_adlx_tag(*input,map,"IMAP")) return result;
    size=audio_adlx_size(*input,(uint16_t)(map+4));
    result.swaps++;result.swap_high=(uint16_t)(size>>16);
    input->index=(uint16_t)(input->index+(uint16_t)size);
    uint16_t track=input->index;
    input->index=(uint16_t)(input->index+8);result.stage=AUDIO_ADLX_TRACK_TAG;
    if(!audio_adlx_tag(*input,track,"TRCK")) return result;
    if(channel!=AUDIO_MAIN_CHANNEL) {
        result.stage=AUDIO_ADLX_CAPACITY;
        if(input->window[(uint16_t)(header+10)]>(uint16_t)(9-state->reserved_voices)) return result;
    } else {
        result.main_map=1;result.instrument_map=*input;result.instrument_map.index=(uint16_t)(map+8);
        state->ticks_per_unit=audio_adlx_word(*input,(uint16_t)(header+14));
    }
    AudioChannel *dest=&state->channels[channel];dest->step_q8=256;
    size=audio_adlx_size(*input,(uint16_t)(root+4));
    result.swaps++;result.swap_high=(uint16_t)(size>>16);
    dest->length=(uint16_t)((uint16_t)size-34u);
    dest->voice_count=input->window[(uint16_t)(header+10)];
    dest->cursor=*input;dest->start=*input;dest->control=4;
    if(!repeats) dest->control|=2;else dest->repeats=repeats;
    result.stage=AUDIO_ADLX_LOADED;result.value=1;return result;
}
uint16_t audio_adlx_reset(AudioChannel *track)
{
    if(!(track->control&4u)) return 65535;
    track->cursor=track->start;return 1;
}
uint16_t audio_adlx_loaded_volume(AudioChannel *track,uint16_t volume,uint16_t parser_value)
{
    if(!parser_value) return 65535;
    track->volume=volume;return 1;
}
