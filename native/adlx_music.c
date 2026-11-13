#include "adlx_music.h"

AudioMusicWork audio_music_begin(AudioMusicOperation operation,AudioCursor resource,uint16_t duration,uint16_t volume,uint16_t devices)
{
    AudioMusicWork work={0};work.operation=operation;work.resource=resource;
    work.duration=duration;work.volume=volume;work.result=65535;work.wait_budget=5000000;
    if(!(devices&1u)) work.stage=100;
    return work;
}
static AudioMusicRequest audio_music_request(AudioMusicAction action,const AudioMusicWork *work,uint16_t channel,uint16_t volume)
{AudioMusicRequest request={action,work->resource,channel,volume};return request;}
static AudioMusicRequest audio_music_wait(AudioMusicWork *work)
{
    if(!work->wait_budget) return audio_music_request(AUDIO_MUSIC_WAIT_BOUND,work,0,0);
    work->wait_budget--;work->stage=4;
    return audio_music_request(AUDIO_MUSIC_TIMER_WAIT,work,0,0);
}
AudioMusicRequest audio_music_next(AudioState *state,AudioMusicWork *work,uint16_t reply)
{
    if(work->stage==100) return audio_music_request(AUDIO_MUSIC_DONE,work,0,0);
    if(work->operation==AUDIO_MUSIC_START) {
        switch(work->stage) {
        case 0:work->stage=1;return audio_music_request(AUDIO_MUSIC_CANCEL,work,0,0);
        case 1:work->stage=2;return audio_music_request(AUDIO_MUSIC_LOAD,work,AUDIO_MAIN_CHANNEL,0);
        case 2:
            if((int16_t)reply<0) {work->stage=100;break;}
            state->playing=1;work->stage=work->duration ? 4 : 3;
            return audio_music_request(AUDIO_MUSIC_START_CHANNEL,work,AUDIO_MAIN_CHANNEL,work->duration ? 0 : work->volume);
        case 3:work->stage=5;return audio_music_request(AUDIO_MUSIC_SET_VOLUME,work,0,work->volume);
        case 4:
            state->fade.start_volume=0;state->fade.target_volume=work->volume;
            state->fade.step_count=0;state->fade.duration=work->duration;work->stage=5;
            return audio_music_request(AUDIO_MUSIC_SCHEDULE,work,0,0);
        case 5:
            /* Retained: start/volume API negatives are ignored; the caller's
             * original full volume word survives their internal clamp. */
            state->track_volume=work->volume;state->time_origin=state->ticks;
            work->result=1;work->stage=100;break;
        }
    } else {
        switch(work->stage) {
        case 0:work->channel=AUDIO_FIRST_EFFECT_CHANNEL;work->stage=1;
            return audio_music_request(AUDIO_MUSIC_STOP_CHANNEL,work,work->channel,0);
        case 1:
            if(++work->channel<AUDIO_MAIN_CHANNEL) return audio_music_request(AUDIO_MUSIC_STOP_CHANNEL,work,work->channel,0);
            if(!state->playing) {work->stage=100;break;}
            work->stage=2;return audio_music_request(AUDIO_MUSIC_CANCEL,work,0,0);
        case 2:
            if(!work->duration) {state->playing=0;work->result=1;work->stage=100;break;}
            state->fade.target_volume=0;state->fade.start_volume=state->track_volume;
            state->fade.step_count=0;state->fade.duration=work->duration;work->stage=3;
            return audio_music_request(AUDIO_MUSIC_SCHEDULE,work,0,0);
        case 3:return audio_music_wait(work);
        case 4:
            /* Whole word, not the scheduler's bit-zero test. Always deliver
             * at least one service point before looking at this word. */
            if(state->fade.scheduled) return audio_music_wait(work);
            state->playing=0;work->stage=5;return audio_music_request(AUDIO_MUSIC_CANCEL,work,0,0);
        case 5:state->current_channel=0;work->stage=6;return audio_music_request(AUDIO_MUSIC_SILENCE,work,0,0);
        case 6:work->result=1;work->stage=100;break;
        }
    }
    return audio_music_request(AUDIO_MUSIC_DONE,work,0,0);
}
AudioFadeRequest audio_music_schedule(const AudioState *state)
{AudioFadeRequest request={AUDIO_FADE_NONE,0,0,0,119275};if(!(state->fade.scheduled&1u)) request.action=AUDIO_FADE_REGISTER;return request;}
AudioFadeRequest audio_music_cancel(const AudioState *state)
{AudioFadeRequest request={AUDIO_FADE_NONE,state->fade.timer_handle,0,0,0};if(state->fade.scheduled&1u) request.action=AUDIO_FADE_REMOVE;return request;}
void audio_music_registered(AudioState *state,uint16_t handle) {state->fade.timer_handle=handle;state->fade.scheduled=1;}
void audio_music_cancelled(AudioState *state) {state->fade.scheduled=0;}
AudioFadeRequest audio_music_fade_step(AudioState *state)
{
    AudioFadeRequest request={AUDIO_FADE_NONE,state->fade.timer_handle,0,0,0};
    state->fade.step_count=(uint16_t)(state->fade.step_count+1u);
    if(state->fade.step_count>state->fade.duration) {request.action=AUDIO_FADE_REMOVE;return request;}
    /* Retained: unsigned completion test, then signed WORD difference,
     * multiplication and division. Zero/overflow is a CPU divide fault. */
    int32_t product=(int16_t)(state->fade.target_volume-state->fade.start_volume)*(int32_t)(int16_t)state->fade.step_count;
    int16_t divisor=(int16_t)state->fade.duration;
    if(!divisor || (product==INT32_MIN && divisor==-1)) {request.action=AUDIO_FADE_FAULT;return request;}
    int32_t quotient=product/divisor;
    if(quotient< -32768 || quotient>32767) {request.action=AUDIO_FADE_FAULT;return request;}
    request.action=AUDIO_FADE_VOLUME;request.volume=(uint16_t)(quotient+state->fade.start_volume);request.remainder=(uint16_t)(product%divisor);return request;
}
int audio_music_guard_begin(AudioState *state) {return audio_section_tick_begin(state);}
void audio_music_guard_end(AudioState *state) {audio_section_tick_end(state);}
static uint8_t audio_music_level(uint8_t level,uint8_t gain,uint8_t volume)
{return (uint8_t)((63u-(((((63u-(level&63u))*gain)>>8)*volume)>>8))|(level&192u));}
static void audio_music_voice_volume(AudioState *state,AudioMusicVolume *result,uint8_t channel,uint8_t volume)
{
    if((state->playing&1u) && state->current_channel>=12 && (state->reserved_voices&15u) && channel>=(uint8_t)(9-(uint8_t)state->reserved_voices)) {
        state->displaced[channel].volume=(uint16_t)((state->displaced[channel].volume&65280u)|volume);return;
    }
    AudioVoice *voice=&state->live[channel];voice->volume=(uint16_t)((voice->volume&65280u)|volume);
    uint8_t op=state->operator_index[channel];
    AudioRegisterWrite carrier={(uint8_t)(op+67),audio_music_level(voice->instrument[6],(uint8_t)voice->gain,volume)};
    result->writes[result->write_count++]=carrier;
    if(voice->instrument[10]&1u) {AudioRegisterWrite modulator={(uint8_t)(op+64),audio_music_level(voice->instrument[1],(uint8_t)voice->gain,volume)};result->writes[result->write_count++]=modulator;}
}
AudioMusicVolume audio_music_volume(AudioState *state,uint16_t devices,uint16_t volume)
{
    AudioMusicVolume result={0};result.result=65535;
    if(!(devices&1u) || !state->playing) return result;
    uint16_t old=state->current_channel;state->track_volume=volume;state->current_channel=AUDIO_MAIN_CHANNEL;
    for(uint32_t i=0;i<state->channels[AUDIO_MAIN_CHANNEL].voice_count;i++) if((uint8_t)i<9) audio_music_voice_volume(state,&result,(uint8_t)i,(uint8_t)volume);
    state->current_channel=old;result.result=1;return result;
}
void audio_music_silence(const AudioState *state,AudioRegisterWrite writes[20])
{
    AudioRegisterWrite zero={1,0},enable={1,32};writes[0]=zero;writes[1]=enable;
    for(unsigned i=0;i<9;i++) {AudioRegisterWrite mod={(uint8_t)(state->operator_index[i]+64),63},carrier={(uint8_t)(state->operator_index[i]+67),63};writes[2+2*i]=mod;writes[3+2*i]=carrier;}
}
