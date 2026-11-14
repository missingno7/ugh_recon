#include "adlx_facade.h"
AudioFacadeWork audio_facade_begin(AudioFacadeOperation operation)
{AudioFacadeWork work={operation,0,0,8};return work;}
AudioFacadeRequest audio_facade_next(AudioFacadeView *view,AudioFacadeWork *work,uint16_t requested,uint16_t reply)
{
    AudioFacadeRequest request={AUDIO_FACADE_DONE,0,0};
    for(;;) {
        if(work->operation==AUDIO_FACADE_INIT) switch(work->stage++) {
        case 0:if(view->initialized && view->devices) {request.action=AUDIO_FACADE_STOP_SYSTEM;return request;}break;
        case 1:request.action=AUDIO_FACADE_CLEAR;return request;
        case 2:if(requested&2u) {request.action=AUDIO_FACADE_INIT_DSP;return request;}work->stage=4;break;
        case 3:if(reply) {work->collected|=2;work->stage=99;request.action=AUDIO_FACADE_BROKEN_HOOK;return request;}break;
        case 4:if(requested&1u) {request.action=AUDIO_FACADE_INIT_ADLIB;return request;}work->stage=6;break;
        case 5:if(reply) work->collected|=1;break;
        case 6:view->devices=work->collected;request.action=AUDIO_FACADE_INITIALIZED;return request;
        default:return request;
        }
        else if(work->operation==AUDIO_FACADE_SHUTDOWN) switch(work->stage++) {
        case 0:if(view->shutdown_latch && !view->devices) {work->stage=99;return request;}
            view->audio->playback_guard=1;request.action=AUDIO_FACADE_CANCEL;return request;
        case 1:if(view->devices&2u) {request.action=AUDIO_FACADE_STOP_DSP;return request;}break;
        case 2:if(view->devices&1u) {request.action=AUDIO_FACADE_STOP_ADLIB;return request;}break;
        case 3:view->devices=0;request.action=AUDIO_FACADE_SHUTDOWN_LATCH;return request;
        default:return request;
        }
        else switch(work->stage++) {
        case 0:if((view->devices&2u) && view->sample_count) {request.action=AUDIO_FACADE_PRIME;return request;}break;
        case 1:if(!(view->devices&1u)) {work->stage=99;return request;}break;
        case 2:
            if(work->channel>=12) return request;
            request.action=AUDIO_FACADE_START_CHANNEL;request.channel=work->channel;
            request.volume=view->audio->channels[work->channel].volume;work->channel++;work->stage=2;return request;
        default:return request;
        }
    }
}
AudioDurationWork audio_duration_begin(uint16_t devices,uint16_t playing,uint16_t rate,uint16_t start,uint16_t length)
{AudioDurationWork work={start,(uint16_t)(start+length),0,5000000,(uint8_t)!!((devices&1u) && playing && rate)};return work;}
int audio_duration_fetch(AudioDurationWork *work)
{
    if(!work->enabled || work->position>=work->end) return 0;
    if(!work->budget) return -1;
    work->budget--;work->position=(uint16_t)(work->position+1u);return 1;
}
int audio_duration_step(AudioDurationWork *work,uint8_t code,int arm,uint8_t payload)
{
    switch(arm) {
    case 0:work->total+=(uint16_t)(((uint32_t)code*256u+payload)*128u);work->position=(uint16_t)(work->position+1u);break;
    case 1:case 6:work->position=(uint16_t)(work->position+2u);break;
    case 2:break;
    case 3:work->position=(uint16_t)(work->position+1u);break;
    case 4:work->position=(uint16_t)(work->position+11u);break;
    case 7:work->position=(uint16_t)(work->position+payload+1u);break;
    case 8:work->total+=code&127u;break;
    default:return 0;
    }
    return 1;
}
AudioDurationResult audio_duration_result(const AudioDurationWork *work,uint16_t live_rate)
{
    AudioDurationResult result={0,0};if(!work->enabled) return result;
    if(!live_rate) {result.fault=1;return result;}
    result.value=(uint16_t)(work->total/live_rate);return result;
}
