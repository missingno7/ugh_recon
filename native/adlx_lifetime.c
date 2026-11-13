#include "adlx_lifetime.h"

void audio_lifetime_reset(AudioState *state,AudioResetCells *cells)
{
    for(unsigned i=0;i<AUDIO_CHANNEL_COUNT;i++) state->channels[i]=(AudioChannel){0};
    for(unsigned i=0;i<AUDIO_VOICE_COUNT;i++) {
        state->live[i]=(AudioVoice){0};state->displaced[i]=(AudioVoice){0};state->scanned[i]=(AudioVoice){0};
    }
    state->playback_guard=0;state->ticks_per_unit=0;state->playing=0;state->section_loop_enabled=0;
    state->ticks=0;state->time_origin=0;state->scanned_ticks=0;
    state->section_start=(AudioCursor){0};state->section_end=(AudioCursor){0};
    state->fade.step_count=0;state->fade.duration=0;state->fade.start_volume=0;state->fade.target_volume=0;state->fade.scheduled=0;
    state->timer_period=0;state->reserved_voices=0;state->current_channel=0;state->track_volume=0;
    *cells=(AudioResetCells){0};
}

AudioLifetimeWork audio_lifetime_begin(int stopping)
{AudioLifetimeWork work={0,0,(uint8_t)!!stopping};return work;}
AudioLifetimeRequest audio_lifetime_next(AudioLifetimeWork *work,uint8_t *attempted,uint16_t handle,uint16_t reply)
{
    AudioLifetimeRequest request={AUDIO_LIFETIME_DONE,0};
    if(work->stopping) {
        switch(work->stage++) {
        case 0:if(*attempted) {request.action=AUDIO_LIFETIME_REMOVE;request.value=handle;break;}
            work->stage=2;request.action=AUDIO_LIFETIME_RESTORE;break;
        case 1:request.action=AUDIO_LIFETIME_RESTORE;break;
        case 2:*attempted=0;request.action=AUDIO_LIFETIME_SILENCE;break;
        default:break;
        }
        return request;
    }
    switch(work->stage++) {
    case 0:if(*attempted) {work->result=1;work->stage=25;break;}
        *attempted=1;request.action=AUDIO_LIFETIME_CALIBRATE;break;
    case 1:request.action=AUDIO_LIFETIME_WRITE;request.value=0x100;break;
    case 2:request.action=AUDIO_LIFETIME_WRITE;request.value=0x460;break;
    case 3:request.action=AUDIO_LIFETIME_DELAY;request.value=20;break;
    case 4:request.action=AUDIO_LIFETIME_WRITE;request.value=0x480;break;
    case 5:request.action=AUDIO_LIFETIME_DELAY;request.value=20;break;
    case 6:request.action=AUDIO_LIFETIME_READ;break;
    case 7:if(reply&224u) {work->stage=25;break;}
        request.action=AUDIO_LIFETIME_WRITE;request.value=0x2ff;break;
    case 8:request.action=AUDIO_LIFETIME_DELAY;request.value=20;break;
    case 9:request.action=AUDIO_LIFETIME_WRITE;request.value=0x421;break;
    case 10:request.action=AUDIO_LIFETIME_DELAY;request.value=255;break;
    case 11:request.action=AUDIO_LIFETIME_READ;break;
    case 12:if(!(reply&224u)) {work->stage=25;break;}
        request.action=AUDIO_LIFETIME_WRITE;request.value=0x460;break;
    case 13:request.action=AUDIO_LIFETIME_DELAY;request.value=20;break;
    case 14:request.action=AUDIO_LIFETIME_WRITE;request.value=0x480;break;
    case 15:request.action=AUDIO_LIFETIME_DELAY;request.value=20;break;
    case 16:request.action=AUDIO_LIFETIME_SILENCE;break;
    case 17:request.action=AUDIO_LIFETIME_WRITE;request.value=0x120;break;
    case 18:request.action=AUDIO_LIFETIME_INSTALL;break;
    case 19:request.action=AUDIO_LIFETIME_REGISTER;request.value=0x1843;break;
    case 20:work->result=1;work->stage=25;break;
    default:break;
    }
    return request;
}

AudioCalibrationWork audio_calibration_begin(uint16_t progress_bias)
{
    AudioCalibrationWork work={0,0,progress_bias,1000000,AUDIO_CALIBRATION_WAIT_BEGIN};return work;
}
AudioCalibrationAction audio_calibration_resume(AudioCalibrationWork *work)
{
    if(work->action==AUDIO_CALIBRATION_DONE || work->action==AUDIO_CALIBRATION_BOUND) return work->action;
    if(!work->budget) {work->action=AUDIO_CALIBRATION_BOUND;return work->action;}
    work->budget--;
    if(work->action==AUDIO_CALIBRATION_WAIT_BEGIN) {
        if((work->marker>>8)==1) {work->remaining=0;work->action=AUDIO_CALIBRATION_WAIT_LOOP;}
    } else {
        work->remaining=(uint16_t)(work->remaining-1u);
        if(!work->remaining) {
            work->progress=(uint16_t)(work->progress+1u);
            if((uint8_t)work->marker==1) work->action=AUDIO_CALIBRATION_DONE;
        }
    }
    return work->action;
}
uint16_t audio_calibration_started(void) {return 256;}
AudioMeasurement audio_calibration_finished(uint16_t remaining,uint16_t progress)
{AudioMeasurement result={remaining,progress};return result;}
