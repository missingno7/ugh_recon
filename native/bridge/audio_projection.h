#ifndef NATIVE_AUDIO_PROJECTION_H
#define NATIVE_AUDIO_PROJECTION_H
#include "ugh.h"
#include "../audio.h"

static AudioCursor audio_bridge_cursor(uint16_t bank,uint16_t offset)
{
    AudioCursor cursor={ugh_mem+(uint32_t)bank*16u,offset};
    return cursor;
}
static AudioCursor audio_bridge_pointer(uint16_t bank,uint16_t offset)
{
    return audio_bridge_cursor(rd16(bank,(uint16_t)(offset+2)),rd16(bank,offset));
}
static uint16_t audio_bridge_bank(AudioCursor cursor)
{
    return (uint16_t)((cursor.window-ugh_mem)/16);
}
static void audio_bridge_voice(uint16_t bank,uint16_t offset,AudioVoice *voice)
{
    for(unsigned i=0;i<12;i++) voice->instrument[i]=rd8(bank,(uint16_t)(offset+i));
    voice->volume=rd16(bank,(uint16_t)(offset+12));
    voice->gain=rd16(bank,(uint16_t)(offset+14));
    voice->owner=rd16(bank,(uint16_t)(offset+16));
    voice->frequency=rd16(bank,(uint16_t)(offset+18));
}
/* The one canonical projection of the common C/SOUND owner. PCM cells are
 * retained opaque here. Main aliases and high-word labels are not reread as
 * additional state objects. This is a serialized snapshot, not an IRQ lock. */
static void audio_bridge_project(uint16_t bank,AudioState *state)
{
    for(unsigned i=0;i<AUDIO_CHANNEL_COUNT;i++) {
        uint16_t p=(uint16_t)(S(AudioChannelStates)+42*i);
        AudioChannel *c=&state->channels[i];
        c->age=rd32(bank,p);c->repeats=rd16(bank,(uint16_t)(p+4));
        c->start=audio_bridge_pointer(bank,(uint16_t)(p+6));
        c->length=rd16(bank,(uint16_t)(p+10));c->sample_mode=rd16(bank,(uint16_t)(p+12));
        c->sample_rate=rd16(bank,(uint16_t)(p+14));c->cursor=audio_bridge_pointer(bank,(uint16_t)(p+16));
        c->sample_half_length=rd16(bank,(uint16_t)(p+20));c->reserved_word=rd16(bank,(uint16_t)(p+22));
        c->sample_selector=rd16(bank,(uint16_t)(p+24));c->sample_accumulator=rd16(bank,(uint16_t)(p+26));
        c->volume=rd16(bank,(uint16_t)(p+28));c->deadline=rd32(bank,(uint16_t)(p+30));
        c->voice_count=rd16(bank,(uint16_t)(p+34));c->first_voice=rd16(bank,(uint16_t)(p+36));
        c->step_q8=rd16(bank,(uint16_t)(p+38));c->control=rd16(bank,(uint16_t)(p+40));
    }
    for(unsigned i=0;i<AUDIO_VOICE_COUNT;i++) {
        audio_bridge_voice(bank,(uint16_t)(S(AdlibVoiceStates)+20*i),&state->live[i]);
        audio_bridge_voice(bank,(uint16_t)(S(SavedAdlibVoiceStates)+20*i),&state->displaced[i]);
        audio_bridge_voice(bank,(uint16_t)(S(ScannedAdlibVoiceStates)+20*i),&state->scanned[i]);
        state->operator_index[i]=rd8(bank,(uint16_t)(S(AdlibOperatorOffsets)+i));
    }
    state->playback_guard=rd16(bank,S(AdlxPlaybackGuard));state->ticks_per_unit=rd16(bank,S(MusicTicksPerUnit));
    state->ticks=rd32(bank,S(AdlxTickCount));state->time_origin=rd32(bank,S(MainAdlxTimeOrigin));
    state->scanned_ticks=rd32(bank,S(ScannedMusicClockTicks));state->playing=rd16(bank,S(MainAdlxPlaying));
    state->section_loop_enabled=rd16(bank,S(MainAdlxSectionLoopEnabled));
    state->section_start=audio_bridge_pointer(bank,S(FirstScannedEvent));
    state->section_end=audio_bridge_pointer(bank,S(MainAdlxSectionEnd));
    state->fade.step_count=rd16(bank,S(MusicFadeStep));state->fade.duration=rd16(bank,S(MusicFadeDuration));
    state->fade.start_volume=rd16(bank,S(MusicFadeStartVolume));state->fade.target_volume=rd16(bank,S(MusicFadeTargetVolume));
    state->fade.scheduled=rd16(bank,S(MusicFadeScheduled));state->fade.timer_handle=rd16(bank,S(MusicFadeTimerHandle));
    state->timer_period=rd16(bank,S(AdlxTimerPeriod));state->playback_timer_handle=rd16(bank,S(AdlxPlaybackTimerHandle));
    state->reserved_voices=rd16(bank,S(ReservedAdlibChannelCount));state->current_channel=rd16(bank,S(CurrentAdlxSlot));
    state->track_volume=rd16(bank,S(MusicTrackVolume));
}

static void audio_bridge_publish_voice(uint16_t bank,uint16_t offset,const AudioVoice *voice)
{
    for(unsigned i=0;i<12;i++) wr8(bank,(uint16_t)(offset+i),voice->instrument[i]);
    wr16(bank,(uint16_t)(offset+12),voice->volume);wr16(bank,(uint16_t)(offset+14),voice->gain);
    wr16(bank,(uint16_t)(offset+16),voice->owner);wr16(bank,(uint16_t)(offset+18),voice->frequency);
}
#endif
