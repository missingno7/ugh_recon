#include "adlx_effects.h"

/* Reuse the accepted voice operations. Effects frequency/key-off always use
 * live voices, so temporarily disable the main interpreter's reservation
 * routing for those two operations. This has no external observation point
 * and the borrowed allocation word is restored before returning. Gain and
 * instrument deliberately keep the driver's original, different gates. */
static AudioMainResult audio_effects_voice(AudioState *state, AudioMainOperation operation,
    uint8_t channel, const uint8_t operands[12], AudioCursor *cursor)
{
    uint16_t reserved=state->reserved_voices;
    if(operation==AUDIO_FREQUENCY || operation==AUDIO_KEY_OFF) state->reserved_voices=0;
    AudioMainResult result=audio_main_step(state,operation,channel,operands,cursor);
    state->reserved_voices=reserved;
    return result;
}

AudioEffectsResult audio_effects_step(AudioState *state, AudioChannel *track,
    AudioMainOperation operation, uint8_t code, const uint8_t operands[12], AudioCursor *cursor)
{
    AudioEffectsResult result={0};
    uint8_t channel=(uint8_t)((code&15u)+(uint8_t)track->first_voice);
    result.channel=channel;
    switch(operation) {
    case AUDIO_LONG_WAIT:
    case AUDIO_SHORT_WAIT: {
        uint16_t raw=operation==AUDIO_LONG_WAIT ?
            (uint16_t)(((unsigned)(code&15u)*256u+operands[0])*128u) : (uint16_t)(code&127u);
        /* Retained: truncate the long raw delta before multiplying, then
         * retain all 24 result bits. Short waits need only the low word. */
        result.wait_delta=((uint32_t)raw*track->step_q8)>>8;
        result.advance=(uint16_t)(operation==AUDIO_LONG_WAIT);
        cursor->index=(uint16_t)(cursor->index+result.advance);
        track->deadline+=result.wait_delta;
        track->cursor.index=cursor->index;
        result.exit=AUDIO_EFFECTS_WAIT;
        return result;
    }
    case AUDIO_FREQUENCY:
    case AUDIO_KEY_OFF:
    case AUDIO_GAIN:
    case AUDIO_INSTRUMENT:
        if(operation==AUDIO_INSTRUMENT && channel<=9) {
            /* Retained channel-nine bug: the owner's next physical record
             * is displaced[0]. The loader rejects nine, AFTER this stamp. */
            if(channel==9) state->displaced[0].owner=state->current_channel;
            else state->live[channel].owner=state->current_channel;
        }
        if(channel<9) {
            AudioMainResult voice=audio_effects_voice(state,operation,channel,operands,cursor);
            result.advance=voice.advance;result.displaced=voice.displaced;
            result.write_count=voice.write_count;
            for(unsigned i=0;i<voice.write_count;i++) result.writes[i]=voice.writes[i];
        } else {
            result.advance=(uint16_t)(operation==AUDIO_GAIN ? 1 :
                operation==AUDIO_INSTRUMENT && channel==9 ? 11 : 0);
            cursor->index=(uint16_t)(cursor->index+result.advance);
        }
        return result;
    case AUDIO_TIMER_PERIOD: {
        uint16_t requested=(uint16_t)((unsigned)operands[0]*256u+operands[1]);
        if(!(state->playing&1u) && !state->timer_period) {
            state->timer_period=requested;
            result.requested_period=requested;result.timer_request=1;
        } else {
            uint32_t numerator=(uint32_t)requested*256u;
            if(!state->timer_period || numerator/state->timer_period>65535u) {
                result.exit=AUDIO_EFFECTS_DIVIDE_FAULT;
                return result;
            }
            track->step_q8=(uint16_t)(numerator/state->timer_period);
        }
        result.advance=2;
        break;
    }
    case AUDIO_CONTROL:
        if(code==119) {
            result.exit=AUDIO_EFFECTS_END;
            if(!(track->control&2u)) {
                uint16_t old=track->repeats;
                track->repeats=(uint16_t)(old-1u);
                if((int16_t)old<=1) {result.stop_request=1;return result;}
            }
            /* Effects repeat only the cursor, without a deadline/origin reset. */
            track->cursor=track->start;result.repeated=1;
            return result;
        }
        result.advance=(uint16_t)((code&15u)==0 ? 3u : (unsigned)operands[0]+1u);
        break;
    case AUDIO_NO_OP:break;
    }
    cursor->index=(uint16_t)(cursor->index+result.advance);
    return result;
}
