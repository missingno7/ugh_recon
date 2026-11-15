#include "audio_world.h"
void audio_world_borrow(const NativeAudioStorage *owner,AudioState *view,
                        uint32_t ticks,uint32_t origin,uint16_t rate,
                        uint16_t playing,uint16_t section_loop)
{
    for(unsigned i=0;i<AUDIO_CHANNEL_COUNT;i++)view->channels[i]=owner->channels[i];
    for(unsigned i=0;i<AUDIO_VOICE_COUNT;i++){
        view->live[i]=owner->live[i];view->displaced[i]=owner->displaced[i];
        view->scanned[i]=owner->scanned[i];view->operator_index[i]=owner->operator_index[i];
    }
    view->playback_guard=owner->playback_guard;view->scanned_ticks=owner->scanned_ticks;
    view->section_start=owner->section_start;view->section_end=owner->section_end;
    view->fade=owner->fade;view->timer_period=owner->timer_period;
    view->playback_timer_handle=owner->playback_timer_handle;view->reserved_voices=owner->reserved_voices;
    view->current_channel=owner->current_channel;view->track_volume=owner->track_volume;
    view->ticks=ticks;view->time_origin=origin;view->ticks_per_unit=rate;
    view->playing=playing;view->section_loop_enabled=section_loop;
}
