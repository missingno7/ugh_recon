#include "game_startup.h"
#include "adlx_facade.h"
#include "adlx_voice.h"
#include "adlx_music.h"
#define TRY(call) do{GSStatus status=(call);if(status!=GS_OK)return status;}while(0)
static GSStatus timer_install(GameWorld *w,GameServices *s) {
    TimerLifetimeRequest request;timer_lifetime_install(&w->timer,&request);
    while(request.kind!=TIMER_LIFETIME_NONE) {
        GSTimerLifetimeRequest q={0};GSBinding reply={0};
        q.kind=request.kind==TIMER_LIFETIME_READ_BINDING?GS_TIMER_READ_BINDING:GS_TIMER_BIND_HANDLER;
        TRY(s->audio.timer_lifetime(s->audio_context,q,&reply));
        if(!timer_lifetime_consume(&w->timer,&w->timer_life,&request,request.kind,(TimerExternalBinding){TIMER_EXTERNAL_BIOS,(uint32_t)reply.token}))return GS_INVALID;
    }
    return GS_OK;
}
static GSStatus calibrate(GameWorld *w,GameServices *s) {
    GSCalibrationReply reply={0};
    TRY(s->audio.calibration(s->audio_context,GS_CALIBRATION_BEGIN,&reply));
    /* The backend supplies measurement replies, never an engine decision. */
    AudioCalibrationWork work=audio_calibration_begin(reply.progress);
    work.marker=reply.marker;audio_calibration_resume(&work);
    TRY(s->audio.calibration(s->audio_context,GS_CALIBRATION_WAIT,&reply));
    work.marker=reply.marker;work.remaining=reply.remainder;work.progress=reply.progress;
    while(audio_calibration_resume(&work)!=AUDIO_CALIBRATION_DONE)if(work.action==AUDIO_CALIBRATION_BOUND)return GS_OVERFLOW;
    TRY(s->audio.calibration(s->audio_context,GS_CALIBRATION_FINISH,&reply));
    AudioMeasurement measured=audio_calibration_finished(reply.remainder,reply.progress);
    w->calibration_remainder=measured.remainder;w->delay_multiplier=measured.multiplier;return GS_OK;
}
static GSStatus adlib(GameWorld *w,GameServices *s,uint16_t *result) {
    AudioLifetimeWork work=audio_lifetime_begin(0);uint16_t reply=0;
    for(;;) {
        AudioLifetimeRequest request=audio_lifetime_next(&work,&w->audio_attempted,w->audio.playback_timer_handle,reply);
        switch(request.action) {
        case AUDIO_LIFETIME_DONE:*result=work.result;return GS_OK;
        case AUDIO_LIFETIME_CALIBRATE:TRY(calibrate(w,s));break;
        case AUDIO_LIFETIME_WRITE: {
            AudioRegisterWrite write=audio_voice_register(request.value);
            TRY(s->audio.opl(s->audio_context,(GSRegisterWrite){write.reg,write.value}));break;}
        case AUDIO_LIFETIME_DELAY:(void)audio_voice_delay((uint8_t)request.value,(uint8_t)w->delay_multiplier);break;
        case AUDIO_LIFETIME_READ: {
            uint8_t value;TRY(s->audio.status(s->audio_context,&value));reply=value;break;}
        case AUDIO_LIFETIME_SILENCE: {
            AudioRegisterWrite writes[20];audio_music_silence(&w->audio,writes);
            for(unsigned i=0;i<20;i++)TRY(s->audio.opl(s->audio_context,(GSRegisterWrite){writes[i].reg,writes[i].value}));break;}
        case AUDIO_LIFETIME_INSTALL:TRY(timer_install(w,s));break;
        case AUDIO_LIFETIME_REGISTER: {
            TimerApiResult answer;TimerApiRequest call={TIMER_API_REGISTER,TIMER_ADLX_PLAYBACK,request.value,0};
            if(!timer_lifetime_apply(&w->timer,&call,&answer))return GS_UNSUPPORTED;
            w->audio.playback_timer_handle=answer.handle;break;}
        default:return GS_UNSUPPORTED;
        }
    }
}
GSStatus game_initialize_audio(GameWorld *w,GameServices *s) {
    LifecycleProcess plan;lifecycle_begin(&plan,LIFE_ADLIB_INIT);LifecycleRequest initial=lifecycle_next(&plan);
    if(initial.action!=LIFE_SOUND_INITIALIZE_ADLIB||!lifecycle_consume(&plan,initial.action))return GS_INVALID;
    AudioFacadeWork work=audio_facade_begin(AUDIO_FACADE_INIT);uint16_t reply=0;
    AudioFacadeView view={0};view.audio=&w->audio;view.initialized=w->audio_initialized;view.devices=w->audio_reset.devices;
    for(;;) {
        AudioFacadeRequest request=audio_facade_next(&view,&work,initial.argument,reply);
        switch(request.action) {
        case AUDIO_FACADE_CLEAR:audio_lifetime_reset(&w->audio,&w->audio_reset);break;
        case AUDIO_FACADE_INIT_ADLIB:TRY(adlib(w,s,&reply));break;
        case AUDIO_FACADE_INITIALIZED:w->audio_reset.devices=view.devices;w->audio_initialized=1;return GS_OK;
        case AUDIO_FACADE_DONE:return GS_OK;
        default:return GS_UNSUPPORTED;
        }
    }
}
GSStatus game_startup_timer(GameWorld *w,GameServices *s) {
    if(!w->timer.installed)return GS_OK;
    uint32_t clocks=w->timer.programmed_divisor?w->timer.programmed_divisor:65536;
    GSStatus status=s->time.interrupt(s->time_context,0,clocks,1);
    if(status==GS_EMPTY)return GS_OK;
    if(status!=GS_OK)return status;
    GSEvent event;TRY(s->time.deliver(s->time_context,GS_TIMER_OPPORTUNITY,&event));
    (void)timer_account_tick(&w->timer);
    unsigned cursor=w->timer.count;
    while(cursor){TimerCallback callback;if(!timer_take_due(&w->timer,--cursor,&callback))continue;
        if(callback==TIMER_BIOS_CHAIN)TRY(s->audio.clock(s->audio_context,GS_CLOCK_BIOS_CHAIN));
        else if(callback==TIMER_ADLX_PLAYBACK){
            int entered=audio_section_tick_begin(&w->audio);
            if(entered){
                /* No track has been started in this slice. Unadmitted live
                 * event streams stop at the consumed timer prefix. */
                if(w->audio.playing||w->audio.reserved_voices)return GS_UNSUPPORTED;
                audio_section_tick_end(&w->audio);
            }
        }else return GS_UNSUPPORTED;
    }
    TRY(s->time.acknowledge(s->time_context));
    uint16_t divisor=(uint16_t)w->timer.earliest;
    if(divisor!=w->timer.programmed_divisor){
        TRY(s->time.pit_command(s->time_context,54));TRY(s->time.pit_counter(s->time_context,(uint8_t)divisor));TRY(s->time.pit_counter(s->time_context,(uint8_t)(divisor>>8)));
    }
    w->timer.programmed_divisor=divisor;return GS_OK;
}
