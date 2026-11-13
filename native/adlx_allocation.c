#include "adlx_allocation.h"

static int audio_effect_slot(uint16_t channel)
{
    return channel>=AUDIO_FIRST_EFFECT_CHANNEL && channel<AUDIO_MAIN_CHANNEL;
}

int audio_allocation_supported(const AudioState *state, AudioAllocationOperation operation,
    uint16_t channel, uint16_t device_bits)
{
    if(operation==AUDIO_ALLOCATION_STOP) {
        if(!(device_bits&1u) || !audio_effect_slot(channel)) return 1;
        if((state->channels[channel].control&5u)!=5u) return 1;
    } else if(operation==AUDIO_ALLOCATION_START) {
        if(!(device_bits&1u) || channel<8 || channel>12) return 1;
        const AudioChannel *track=&state->channels[channel];
        if(!(track->control&4u) || (track->control&1u)) return 1;
        uint16_t reserved=(uint16_t)(state->reserved_voices+track->voice_count);
        if(channel<12 && reserved>9) return 1; /* failure before any voice */
        uint16_t first=channel<12 ? (uint16_t)(9-reserved) : track->first_voice;
        return first<=9 && track->voice_count<=9-first;
    } else if(!audio_effect_slot(channel)) return 0;
    const AudioChannel *track=&state->channels[channel];
    return state->reserved_voices<=9 && track->voice_count<=state->reserved_voices &&
        track->first_voice<=9 && track->voice_count<=9-track->first_voice;
}

static AudioAllocationAction *audio_allocation_action(AudioState *state, AudioAllocationResult *result,
    AudioAllocationActionKind kind, uint16_t channel)
{
    AudioAllocationAction *action=&result->actions[result->action_count++];
    action->kind=kind;action->channel=channel;action->current_channel=state->current_channel;
    action->first_reserved=(uint8_t)(9-(uint8_t)state->reserved_voices);
    action->write_count=0;action->displaced=0;
    return action;
}

static uint8_t audio_allocation_level(uint8_t level,uint8_t gain,uint8_t volume)
{
    unsigned scaled=(((63u-(level&63u))*gain)>>8)*volume;
    return (uint8_t)((63u-(scaled>>8))|(level&192u));
}
static void audio_allocation_volume(AudioState *state, AudioAllocationResult *result,uint16_t channel,uint8_t volume)
{
    AudioAllocationAction *action=audio_allocation_action(state,result,AUDIO_ALLOCATION_VOLUME,channel);
    if((state->playing&1u) && state->current_channel>=12 && (state->reserved_voices&15u) &&
       channel>=action->first_reserved) {
        state->displaced[channel].volume=(uint16_t)((state->displaced[channel].volume&65280u)|volume);
        action->displaced=1;return;
    }
    AudioVoice *voice=&state->live[channel];
    voice->volume=(uint16_t)((voice->volume&65280u)|volume);
    uint8_t op=state->operator_index[channel];
    AudioRegisterWrite carrier={(uint8_t)(op+67u),audio_allocation_level(voice->instrument[6],(uint8_t)voice->gain,volume)};
    result->writes[result->write_count++]=carrier;action->write_count++;
    if(voice->instrument[10]&1u) {
        AudioRegisterWrite modulator={(uint8_t)(op+64u),audio_allocation_level(voice->instrument[1],(uint8_t)voice->gain,volume)};
        result->writes[result->write_count++]=modulator;action->write_count++;
    }
}
static void audio_allocation_voice(AudioState *state,AudioAllocationResult *result,
    AudioAllocationActionKind kind,uint16_t channel,uint16_t value,const uint8_t instrument[12])
{
    AudioAllocationAction *action=audio_allocation_action(state,result,kind,channel);
    uint8_t bytes[12]={0};
    for(unsigned i=0;i<12;i++) if(instrument) bytes[i]=instrument[i];
    AudioMainOperation operation=kind==AUDIO_ALLOCATION_INSTRUMENT ? AUDIO_INSTRUMENT :
        kind==AUDIO_ALLOCATION_FREQUENCY ? AUDIO_FREQUENCY : AUDIO_KEY_OFF;
    if(operation==AUDIO_FREQUENCY) {bytes[0]=(uint8_t)value;bytes[1]=(uint8_t)(value>>8);}
    uint16_t reserved=state->reserved_voices;
    if(operation!=AUDIO_INSTRUMENT) state->reserved_voices=0;
    AudioCursor cursor={0};
    AudioMainResult voice=audio_main_step(state,operation,(uint8_t)channel,bytes,&cursor);
    state->reserved_voices=reserved;
    action->displaced=voice.displaced;action->write_count=voice.write_count;
    for(unsigned i=0;i<voice.write_count;i++) result->writes[result->write_count++]=voice.writes[i];
}

static void audio_allocation_restore(AudioState *state,uint16_t channel,AudioAllocationResult *result)
{
    AudioChannel *track=&state->channels[channel];
    uint16_t count=track->voice_count,begin=(uint16_t)(9-state->reserved_voices),end=(uint16_t)(begin+count);
    track->control=0;state->reserved_voices=(uint16_t)(state->reserved_voices-count);
    for(unsigned k=8;k<12;k++) if(k!=channel && (state->channels[k].control&4u) &&
        state->channels[k].first_voice<track->first_voice)
        state->channels[k].first_voice=(uint16_t)(state->channels[k].first_voice+count);
    if(track->first_voice>begin) {
        int i=(int)track->first_voice+count-1;
        for(;i>=(int)end;i--) {
            AudioVoice *dest=&state->live[i],*source=&state->live[i-count];
            for(unsigned k=0;k<12;k++) dest->instrument[k]=source->instrument[k];
            audio_allocation_action(state,result,AUDIO_ALLOCATION_COPY,(uint16_t)i);
            /* Retained assignment order. Copies are disjoint or identical in
             * this domain; saved music records never move with effect voices. */
            dest->volume=source->volume;dest->gain=source->gain;
            dest->frequency=source->frequency;dest->owner=source->owner;
            state->current_channel=dest->owner;
            uint16_t frequency=dest->frequency;
            audio_allocation_voice(state,result,AUDIO_ALLOCATION_KEY_OFF,(uint16_t)i,0,0);
            audio_allocation_voice(state,result,AUDIO_ALLOCATION_INSTRUMENT,(uint16_t)i,0,dest->instrument);
            audio_allocation_voice(state,result,AUDIO_ALLOCATION_FREQUENCY,(uint16_t)i,frequency,0);
        }
    }
    for(uint16_t i=begin;i<end;i++) {
        AudioVoice *dest=&state->live[i],*saved=&state->displaced[i];
        if(i<state->channels[AUDIO_MAIN_CHANNEL].voice_count) {
            dest->volume=state->track_volume;dest->gain=saved->gain;
            state->current_channel=12;dest->owner=12;
            audio_allocation_voice(state,result,AUDIO_ALLOCATION_KEY_OFF,i,0,0);
            audio_allocation_voice(state,result,AUDIO_ALLOCATION_INSTRUMENT,i,0,saved->instrument);
            audio_allocation_action(state,result,AUDIO_ALLOCATION_MUSIC_RESULT,i);
            audio_allocation_voice(state,result,AUDIO_ALLOCATION_FREQUENCY,i,saved->frequency,0);
        } else {
            audio_allocation_voice(state,result,AUDIO_ALLOCATION_KEY_OFF,i,0,0);
            audio_allocation_action(state,result,AUDIO_ALLOCATION_EMPTY_RESULT,i);
            audio_allocation_volume(state,result,i,0);
        }
    }
}

AudioAllocationResult audio_allocation_run(AudioState *state,AudioAllocationOperation operation,
    uint16_t channel,uint16_t volume,uint16_t device_bits)
{
    AudioAllocationResult result={0};result.value=65535;result.old_guard=state->playback_guard;
    result.volume=volume;
    if(operation==AUDIO_ALLOCATION_RESTORE) {
        result.performed=1;result.first_voice=state->channels[channel].first_voice;
        audio_allocation_restore(state,channel,&result);return result;
    }
    if(operation==AUDIO_ALLOCATION_STOP) {
        if(!(device_bits&1u) || !audio_effect_slot(channel) || (state->channels[channel].control&5u)!=5u) return result;
        AudioChannel *track=&state->channels[channel];result.performed=1;result.first_voice=track->first_voice;
        state->playback_guard=1;track->control=0;track->cursor=track->start;
        for(uint16_t i=0;i<track->voice_count;i++)
            audio_allocation_voice(state,&result,AUDIO_ALLOCATION_KEY_OFF,(uint16_t)(track->first_voice+i),0,0);
        audio_allocation_restore(state,channel,&result);
        state->playback_guard=result.old_guard;return result;
    }
    if(!(device_bits&1u)) return result;
    state->current_channel=channel;
    if(volume&65280u) {volume=255;result.volume=volume;result.clamped=1;}
    if(channel<8 || channel>12) return result;
    AudioChannel *track=&state->channels[channel];
    if(!(track->control&4u) || (track->control&1u)) return result;
    state->playback_guard=1;track->volume=volume;
    if(channel<12) {
        /* The original stop call is necessarily inactive at this point. */
        state->reserved_voices=(uint16_t)(state->reserved_voices+track->voice_count);
        if(state->reserved_voices>9) {
            state->reserved_voices=(uint16_t)(state->reserved_voices-track->voice_count);
            result.capacity_failure=1;return result; /* retained guard leak */
        }
        track->first_voice=(uint16_t)(9-state->reserved_voices);
    }
    for(uint16_t i=track->first_voice;i<(uint16_t)(track->first_voice+track->voice_count);i++) {
        AudioVoice *voice=&state->live[i],*saved=&state->displaced[i];
        if(i<state->channels[AUDIO_MAIN_CHANNEL].voice_count) {
            saved->frequency=voice->frequency;
            for(unsigned k=0;k<12;k++) saved->instrument[k]=voice->instrument[k];
            audio_allocation_action(state,&result,AUDIO_ALLOCATION_COPY,i);
            saved->volume=state->track_volume;saved->gain=voice->gain;
            /* Retained: saved owner is NOT assigned on acquisition. */
        }
        audio_allocation_volume(state,&result,i,0);
        audio_allocation_voice(state,&result,AUDIO_ALLOCATION_KEY_OFF,i,0,0);
        voice->volume=volume;
    }
    track->control|=1u;track->deadline=state->ticks+3u;
    state->playback_guard=result.old_guard;result.performed=1;result.value=1;
    return result;
}

AudioEffectSelection audio_effect_select(const AudioState *state)
{
    AudioEffectSelection result={8,0};
    for(uint16_t i=8;i<12;i++) if(!(state->channels[i].control&1u)) {result.channel=i;return result;}
    result.replace=1;
    for(uint16_t i=8;i<12;i++) if(state->channels[i].age<state->channels[result.channel].age) result.channel=i;
    return result;
}
