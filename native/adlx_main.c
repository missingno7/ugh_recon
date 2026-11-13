#include "adlx_main.h"

static void audio_write(AudioMainResult *result, uint8_t reg, uint8_t value)
{
    result->writes[result->write_count].reg=reg;
    result->writes[result->write_count].value=value;
    result->write_count++;
}

static uint8_t audio_level(uint8_t level, uint8_t gain, uint8_t volume)
{
    /* Retained: two truncating high-byte products, with no saturation. */
    unsigned scaled=(((63u-(level&63u))*gain)>>8)*volume;
    return (uint8_t)((63u-(scaled>>8))|(level&192u));
}

static void audio_volume(AudioState *state, uint8_t channel, uint8_t volume,
                         AudioMainResult *result)
{
    uint8_t first=(uint8_t)(9u-(uint8_t)state->reserved_voices);
    if((state->playing&1u) && state->current_channel>=12 &&
       (state->reserved_voices&15u) && channel>=first) {
        state->displaced[channel].volume=(uint16_t)((state->displaced[channel].volume&65280u)|volume);
        return;
    }
    AudioVoice *voice=&state->live[channel];
    voice->volume=(uint16_t)((voice->volume&65280u)|volume);
    uint8_t op=state->operator_index[channel];
    audio_write(result,(uint8_t)(op+67u),audio_level(voice->instrument[6],(uint8_t)voice->gain,volume));
    if(voice->instrument[10]&1u)
        audio_write(result,(uint8_t)(op+64u),audio_level(voice->instrument[1],(uint8_t)voice->gain,volume));
}

AudioMainOperation audio_main_operation(uint8_t code)
{
    return code>=128 ? AUDIO_SHORT_WAIT : (AudioMainOperation)(code>>4);
}

AudioMainResult audio_main_step(AudioState *state, AudioMainOperation operation,
                               uint8_t code, const uint8_t operands[12], AudioCursor *cursor)
{
    AudioMainResult result={0};
    AudioChannel *main=&state->channels[AUDIO_MAIN_CHANNEL];
    uint8_t channel=(uint8_t)(code&15u);
    uint8_t first=(uint8_t)(9u-(uint8_t)state->reserved_voices);
    result.channel=channel;
    switch(operation) {
    case AUDIO_LONG_WAIT:
    case AUDIO_SHORT_WAIT:
        /* Retained original bug: the long delta wraps to SIXTEEN bits before
         * the 32-bit deadline addition. This differs from the format dumper. */
        result.wait_delta=operation==AUDIO_LONG_WAIT ?
            (uint16_t)(((unsigned)channel*256u+operands[0])*128u) : (uint16_t)(code&127u);
        result.advance=(uint16_t)(operation==AUDIO_LONG_WAIT);
        cursor->index=(uint16_t)(cursor->index+result.advance);
        main->deadline+=result.wait_delta;
        /* Only the index is published: a wait never stores the window half. */
        main->cursor.index=cursor->index;
        result.exit=AUDIO_WAIT;
        return result;
    case AUDIO_FREQUENCY:
        if(channel<9) {
            uint16_t value=(uint16_t)(operands[0]+(unsigned)operands[1]*256u);
            result.advance=2;
            if(channel>=first) {
                state->displaced[channel].frequency=value;
                result.displaced=1;
            } else {
                state->live[channel].frequency=value;
                audio_write(&result,(uint8_t)(channel+160u),operands[0]);
                audio_write(&result,(uint8_t)(channel+176u),operands[1]);
            }
        }
        break;
    case AUDIO_KEY_OFF:
        if(channel<9) {
            if(channel>=first) {
                /* Retained: displaced main key-off clears LOW word bit five,
                 * unlike the live path's B0 high-byte key bit. */
                state->displaced[channel].frequency&=65503u;
                result.displaced=1;
            } else {
                state->live[channel].frequency&=57343u;
                audio_write(&result,(uint8_t)(channel+176u),(uint8_t)(state->live[channel].frequency>>8));
            }
        }
        break;
    case AUDIO_GAIN:
        result.advance=1; /* Invalid channels still consume their byte. */
        if(channel<9) {
            if(state->current_channel>=12 && (state->reserved_voices&15u) && channel>=first) {
                state->displaced[channel].gain=(uint16_t)((state->displaced[channel].gain&65280u)|operands[0]);
                result.displaced=1;
            } else {
                AudioVoice *voice=&state->live[channel];
                voice->gain=(uint16_t)((voice->gain&65280u)|operands[0]);
                audio_volume(state,channel,(uint8_t)voice->volume,&result);
            }
        }
        break;
    case AUDIO_INSTRUMENT:
        if(channel<9) {
            result.advance=11;
            result.displaced=(uint8_t)(state->current_channel==12 &&
                (state->reserved_voices&15u) && channel>=first);
            AudioVoice *voice=result.displaced ? &state->displaced[channel] : &state->live[channel];
            for(unsigned i=0;i<12;i++) voice->instrument[i]=operands[i];
            if(!result.displaced) {
                uint8_t op=state->operator_index[channel];
                for(unsigned i=0;i<5;i++) {
                    uint8_t reg=(uint8_t)(op+(i==4 ? 224u : 32u+i*32u));
                    uint8_t value=operands[i];
                    if(i==1 && (operands[10]&1u)) value|=63u;
                    audio_write(&result,reg,value);
                }
                for(unsigned i=0;i<4;i++) {
                    uint8_t value=operands[5+i];
                    if(i==1) value|=63u;
                    audio_write(&result,(uint8_t)(op+35u+i*32u),value);
                }
                audio_write(&result,1,32);
                audio_write(&result,(uint8_t)(op+227u),operands[9]);
                audio_write(&result,(uint8_t)(channel+192u),operands[10]);
                voice->owner=state->current_channel;
                audio_volume(state,channel,(uint8_t)voice->volume,&result);
            }
        }
        break;
    case AUDIO_TIMER_PERIOD:
        result.advance=2;
        result.requested_period=(uint16_t)((unsigned)operands[0]*256u+operands[1]);
        state->timer_period=result.requested_period;
        result.timer_request=1;
        break;
    case AUDIO_CONTROL:
        if(code==119) {
            result.exit=AUDIO_END;
            if(!(main->control&2u)) {
                uint16_t old=main->repeats;
                main->repeats=(uint16_t)(old-1u);
                /* Signed DEC/JG uses the old value, including 8000 overflow. */
                if((int16_t)old<=1) {
                    main->control&=65534u;
                    return result;
                }
            }
            main->cursor=main->start;
            main->deadline=state->ticks;
            state->time_origin=state->ticks;
            result.repeated=1;
            return result;
        }
        result.advance=(uint16_t)(channel==0 ? 3u : (unsigned)operands[0]+1u);
        break;
    case AUDIO_NO_OP: break;
    }
    cursor->index=(uint16_t)(cursor->index+result.advance);
    return result;
}
