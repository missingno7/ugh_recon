#include "compose_audio.h"
#include "game_startup.h"
#include "adlx_allocation.h"
#include "adlx_loader.h"
#include "adlx_effects.h"
#include "adlx_music.h"
#include "adlx_facade.h"
#include <string.h>
#define TRY(call) do{GSStatus status=(call);if(status!=GS_OK)return status;}while(0)
/* Generated from data object identities only; the same pack is validated before
 * constructing any world. Borrowed resources remain live provider data. */
#include "audio_data.h"
static GameAudioResult result(GSStatus s,uint16_t value){return (GameAudioResult){s,value};}
GSResourceId game_audio_resource_id(unsigned i){return i<11?game_audio_specs[i].id:0;}
GSResourceId game_audio_game_over_resource(void){return game_audio_specs[GAME_AUDIO_GAME_OVER].id;}
GSResourceId game_audio_menu_resource(void){return game_audio_specs[GAME_AUDIO_MENU].id;}
GSResourceId game_audio_score_resource(void){return game_audio_specs[GAME_AUDIO_SCORE].id;}
GSResourceId game_audio_intro_resource(void){return game_audio_specs[GAME_AUDIO_INTRO].id;}
GSStatus game_audio_construct(GameWorld *w,GameServices *s){
    for(unsigned i=0;i<11;i++){
        const GameAudioResourceSpec *r=&game_audio_specs[i];GSBytes bytes;GSResourceClass kind;
        TRY(s->resources.view(s->resources_context,r->allocation,&bytes,&kind));
        if(r->offset>bytes.size||r->size>bytes.size-r->offset)return GS_INVALID;
        w->audio_data[i]=(GSBytes){bytes.data+r->offset,r->size};
        if(w->audio_data[i].size<42||w->audio_data[i].size>65536||memcmp(w->audio_data[i].data,"ADLX",4))return GS_INVALID;
    }return GS_OK;
}
static GSStatus resource(GameWorld *w,GSResourceId id,AudioCursor *cursor){
    for(unsigned i=0;i<11;i++)if(game_audio_specs[i].id==id){*cursor=(AudioCursor){w->audio_data[i].data,0};return GS_OK;}return GS_UNSUPPORTED;
}
static size_t capacity(const GameWorld *w,AudioCursor c){
    for(unsigned i=0;i<11;i++)if(w->audio_data[i].data==c.window)return w->audio_data[i].size;return 0;
}
static GSStatus emit(GameServices *s,const AudioRegisterWrite *writes,unsigned count){
    for(unsigned i=0;i<count;i++)TRY(s->audio.opl(s->audio_context,(GSRegisterWrite){writes[i].reg,writes[i].value}));return GS_OK;
}
static GSStatus timer_api(GameWorld *w,TimerApiKind kind,TimerCallback callback,uint32_t interval,uint16_t handle,uint16_t *reply){
    TimerApiRequest request={kind,callback,interval,handle};TimerApiResult answer;
    if(w->timer.count<1||w->timer.count>TIMER_CAPACITY||!timer_lifetime_apply(&w->timer,&request,&answer))return GS_UNSUPPORTED;
    if(reply)*reply=answer.handle;return GS_OK;
}
GameAudioResult game_audio_channel(GameWorld *w,GameServices *s,unsigned channel,int start,uint16_t volume){
    AudioAllocationOperation op=start?AUDIO_ALLOCATION_START:AUDIO_ALLOCATION_STOP;
    if(channel>12||!audio_allocation_supported(&w->audio,op,(uint16_t)channel,w->audio_reset.devices))return result(GS_UNSUPPORTED,65535);
    AudioAllocationResult r=audio_allocation_run(&w->audio,op,(uint16_t)channel,volume,w->audio_reset.devices);
    return result(emit(s,r.writes,r.write_count),r.value);
}
/* Effect handles include FFFF after a no-card start. The accepted allocation
 * kernel admits every word on STOP and rejects inactive handles itself. */
GSStatus game_audio_effect_stop(GameWorld *w,GameServices *s,uint16_t handle){
    if(!audio_allocation_supported(&w->audio,AUDIO_ALLOCATION_STOP,handle,w->audio_reset.devices))return GS_UNSUPPORTED;
    AudioAllocationResult r=audio_allocation_run(&w->audio,AUDIO_ALLOCATION_STOP,handle,0,w->audio_reset.devices);
    return emit(s,r.writes,r.write_count);
}
static GSStatus stop_channel(GameWorld *w,GameServices *s,unsigned channel){return game_audio_channel(w,s,channel,0,0).status;}
static GSStatus load(GameWorld *w,unsigned channel,AudioCursor input,uint16_t repeats,uint16_t *reply){
    /* Validate each chunk header before the accepted unchecked parser borrows
     * it. Unadmitted/malformed resource reads stop, never zero-fill a RAM image. */
    size_t size=capacity(w,input),at=input.index;
    if(channel<8||channel>12)return GS_UNSUPPORTED;
    for(unsigned i=0;i<4;i++){
        if(at>size||size-at<8)return GS_UNSUPPORTED;
        if(i==0){at+=8;continue;}
        if(i<3){uint16_t n=(uint16_t)((unsigned)input.window[at+6]*256u+input.window[at+7]);at+=8u+n;}
    }
    AudioAdlxLoadResult r=audio_adlx_load(&w->audio,(uint16_t)channel,&input,repeats,w->audio_reset.devices);
    if(r.main_map)w->audio_reset.instrument_map=r.instrument_map;*reply=r.value;return GS_OK;
}
GSStatus game_audio_volume(GameWorld *w,GameServices *s,uint16_t volume){AudioMusicVolume r=audio_music_volume(&w->audio,w->audio_reset.devices,volume);return emit(s,r.writes,r.write_count);}
GSStatus game_audio_cancel_fade(GameWorld *w,GameServices *s){
    (void)s;AudioFadeRequest r=audio_music_cancel(&w->audio);
    if(r.action==AUDIO_FADE_REMOVE){TRY(timer_api(w,TIMER_API_REMOVE,TIMER_OPEN,0,r.handle,0));audio_music_cancelled(&w->audio);}return GS_OK;
}
GSStatus game_audio_schedule_fade(GameWorld *w,GameServices *s){
    (void)s;AudioFadeRequest r=audio_music_schedule(&w->audio);uint16_t handle;
    if(r.action==AUDIO_FADE_REGISTER){TRY(timer_api(w,TIMER_API_REGISTER,TIMER_MUSIC_FADE,r.interval,0,&handle));audio_music_registered(&w->audio,handle);}return GS_OK;
}
static GSStatus silence(GameWorld *w,GameServices *s){AudioRegisterWrite writes[20];audio_music_silence(&w->audio,writes);return emit(s,writes,20);}
static GameAudioResult music(GameWorld *w,GameServices *s,AudioMusicOperation op,AudioCursor cursor,uint16_t duration,uint16_t volume){
    AudioMusicWork work=audio_music_begin(op,cursor,duration,volume,w->audio_reset.devices);uint16_t reply=65535;
    for(;;){AudioMusicRequest r=audio_music_next(&w->audio,&work,reply);GSStatus status=GS_OK;
        switch(r.action){
        case AUDIO_MUSIC_DONE:return result(GS_OK,work.result);
        case AUDIO_MUSIC_CANCEL:status=game_audio_cancel_fade(w,s);break;
        case AUDIO_MUSIC_LOAD:status=load(w,r.channel,r.resource,0,&reply);break;
        case AUDIO_MUSIC_START_CHANNEL:{GameAudioResult a=game_audio_channel(w,s,r.channel,1,r.volume);reply=a.value;status=a.status;break;}
        case AUDIO_MUSIC_SET_VOLUME:status=game_audio_volume(w,s,r.volume);break;
        case AUDIO_MUSIC_SCHEDULE:status=game_audio_schedule_fade(w,s);break;
        case AUDIO_MUSIC_STOP_CHANNEL:status=stop_channel(w,s,r.channel);break;
        case AUDIO_MUSIC_TIMER_WAIT:status=game_audio_timer(w,s);break;
        case AUDIO_MUSIC_SILENCE:status=silence(w,s);break;
        default:status=GS_OVERFLOW;break;
        }if(status!=GS_OK)return result(status,65535);
    }
}
GameAudioResult game_audio_music_start(GameWorld *w,GameServices *s,GSResourceId id,uint16_t duration,uint16_t volume){
    AudioCursor cursor={0};if(w->audio_reset.devices&2u)return result(GS_UNSUPPORTED,65535);
    if(w->audio_reset.devices&1u){GSStatus status=resource(w,id,&cursor);if(status!=GS_OK)return result(status,65535);}
    return music(w,s,AUDIO_MUSIC_START,cursor,duration,volume);
}
GameAudioResult game_audio_music_stop(GameWorld *w,GameServices *s,uint16_t duration){
    if(w->audio_reset.devices&2u)return result(GS_UNSUPPORTED,65535);return music(w,s,AUDIO_MUSIC_STOP,(AudioCursor){0},duration,0);
}
GameAudioResult game_audio_effect(GameWorld *w,GameServices *s,GSResourceId id,uint16_t volume,uint16_t repeats){
    if(w->audio_reset.devices&2u)return result(GS_UNSUPPORTED,65535);
    if(!(w->audio_reset.devices&1u))return result(GS_OK,65535);
    AudioCursor cursor;GSStatus status=resource(w,id,&cursor);if(status!=GS_OK)return result(status,65535);
    AudioEffectSelection choice=audio_effect_select(&w->audio);unsigned channel=choice.channel;
    if(choice.replace){status=stop_channel(w,s,channel);if(status!=GS_OK)return result(status,65535);if(w->audio.channels[channel].control&1u)return result(GS_OK,65535);}
    status=stop_channel(w,s,channel);if(status!=GS_OK)return result(status,65535);
    uint16_t reply;status=load(w,channel,cursor,repeats,&reply);if(status!=GS_OK)return result(status,65535);
    reply=audio_adlx_loaded_volume(&w->audio.channels[channel],volume,reply);
    if((int16_t)reply>=0){GameAudioResult r=game_audio_channel(w,s,channel,1,volume);if(r.status!=GS_OK)return r;if(choice.replace&&(int16_t)r.value<0)return r;}
    else if(choice.replace)return result(GS_OK,65535);
    return result(GS_OK,(uint16_t)channel);
}
GSStatus game_audio_events(GameWorld *w,GameServices *s,unsigned record){
    if(record<8||record>12||(w->audio_reset.devices&2u))return GS_UNSUPPORTED;
    AudioCursor cursor=w->audio.channels[record].cursor;
    for(unsigned budget=0;budget<1000000;budget++){
        size_t size=capacity(w,cursor);if(cursor.index>=size)return GS_UNSUPPORTED;
        uint8_t code=cursor.window[cursor.index++],bytes[12]={0};AudioMainOperation op=audio_main_operation(code);
        /* Only operands consumed by this event are read. Instrument byte12 is
         * the intentional next-event alias in the accepted voice contract. */
        unsigned physical=(uint8_t)((code&15u)+(record==12?0:(uint8_t)w->audio.channels[record].first_voice));
        unsigned count=op==AUDIO_INSTRUMENT?(physical<9?12:0):op==AUDIO_FREQUENCY?(physical<9?2:0):op==AUDIO_TIMER_PERIOD?2:op==AUDIO_GAIN||op==AUDIO_LONG_WAIT|| (op==AUDIO_CONTROL&&code!=119)?1:0;
        if(record!=12&&op==AUDIO_INSTRUMENT&&physical==9)count=0;
        for(unsigned i=0;i<count;i++){unsigned at=(uint16_t)(cursor.index+i);if(at>=size)return GS_UNSUPPORTED;bytes[i]=cursor.window[at];}
        uint8_t timer_request;unsigned ended;
        if(record==12){AudioMainResult r=audio_main_step(&w->audio,op,code,bytes,&cursor);TRY(emit(s,r.writes,r.write_count));timer_request=r.timer_request;ended=r.exit!=AUDIO_CONTINUE;}
        else {AudioEffectsResult r=audio_effects_step(&w->audio,&w->audio.channels[record],op,code,bytes,&cursor);
            TRY(emit(s,r.writes,r.write_count));if(r.exit==AUDIO_EFFECTS_DIVIDE_FAULT)return GS_UNSUPPORTED;
            if(r.stop_request)TRY(stop_channel(w,s,w->audio.current_channel));timer_request=r.timer_request;ended=r.exit!=AUDIO_EFFECTS_CONTINUE;}
        if(timer_request){if(w->timer.count<1||w->timer.count>TIMER_CAPACITY||timer_handle_slot(&w->timer,w->audio.playback_timer_handle)<0)return GS_UNSUPPORTED;timer_set_interval(&w->timer,w->audio.playback_timer_handle,w->audio.timer_period);}
        if(ended)return GS_OK;
    }return GS_OVERFLOW;
}
GSStatus game_audio_tick(GameWorld *w,GameServices *s){
    if(w->audio_reset.devices&2u)return GS_UNSUPPORTED;
    if(!audio_section_tick_begin(&w->audio))return GS_OK;
    if(audio_section_main_due(&w->audio)){
        w->audio_record=12;audio_section_main_context(&w->audio);
        if(audio_section_apply_due(&w->audio)){
            if(w->audio.channels[12].voice_count>9)return GS_UNSUPPORTED;
            AudioSectionApply r=audio_section_apply(&w->audio,w->audio_reset.devices);TRY(emit(s,r.writes,r.write_count));
        }TRY(game_audio_events(w,s,12));
    }
    if(w->audio.reserved_voices&15u){audio_section_effects_begin(&w->audio);
        for(unsigned i=8;i<12;i++){if(audio_section_effect_due(&w->audio,i)){w->audio_record=(uint16_t)i;TRY(game_audio_events(w,s,i));}audio_section_effect_next(&w->audio);}
    }audio_section_tick_end(&w->audio);return GS_OK;
}
GSStatus game_audio_guarded_tick(GameWorld *w,GameServices *s){
    if(!audio_music_guard_begin(&w->audio))return GS_OK;
    TRY(game_audio_tick(w,s));audio_music_guard_end(&w->audio);return GS_OK;
}
GSStatus game_audio_callback(GameWorld *w,GameServices *s,TimerCallback callback){
    if(callback==TIMER_ADLX_PLAYBACK)return game_audio_tick(w,s);
    if(callback==TIMER_BIOS_CHAIN){if(w->timer_life.saved.role!=TIMER_EXTERNAL_BIOS)return GS_UNSUPPORTED;return s->audio.clock(s->audio_context,GS_CLOCK_BIOS_CHAIN);}
    if(callback==TIMER_MUSIC_FADE){AudioFadeRequest r=audio_music_fade_step(&w->audio);
        if(r.action==AUDIO_FADE_FAULT)return GS_UNSUPPORTED;
        if(r.action==AUDIO_FADE_REMOVE){TRY(timer_api(w,TIMER_API_REMOVE,TIMER_OPEN,0,r.handle,0));audio_music_cancelled(&w->audio);return GS_OK;}
        if(r.action==AUDIO_FADE_VOLUME)return game_audio_volume(w,s,r.volume);
    }return GS_UNSUPPORTED;
}
GSStatus game_audio_timer(GameWorld *w,GameServices *s){
    if(!w->timer.installed)return GS_OK;
    if(w->timer.count<1||w->timer.count>TIMER_CAPACITY)return GS_UNSUPPORTED;
    uint32_t clocks=w->timer.programmed_divisor?w->timer.programmed_divisor:65536;
    GSStatus status=s->time.interrupt(s->time_context,0,clocks,1);if(status==GS_EMPTY)return GS_OK;if(status!=GS_OK)return status;
    GSEvent event;TRY(s->time.deliver(s->time_context,GS_TIMER_OPPORTUNITY,&event));
    (void)timer_account_tick(&w->timer);unsigned cursor=w->timer.count;
    while(cursor){TimerCallback callback;if(timer_take_due(&w->timer,--cursor,&callback))TRY(game_audio_callback(w,s,callback));}
    TRY(s->time.acknowledge(s->time_context));uint16_t divisor=(uint16_t)w->timer.earliest;
    if(divisor!=w->timer.programmed_divisor){TRY(s->time.pit_command(s->time_context,54));TRY(s->time.pit_counter(s->time_context,(uint8_t)divisor));TRY(s->time.pit_counter(s->time_context,(uint8_t)(divisor>>8)));}
    w->timer.programmed_divisor=divisor;return GS_OK;
}
static GSStatus restore_timer(GameWorld *w,GameServices *s){
    TimerLifetimeRequest r;timer_lifetime_restore(&w->timer,&w->timer_life,&r);
    while(r.kind!=TIMER_LIFETIME_NONE){GSBinding reply={0};
        if(r.kind==TIMER_LIFETIME_BIND_SAVED){if(r.binding.role!=TIMER_EXTERNAL_BIOS)return GS_UNSUPPORTED;TRY(s->audio.timer_lifetime(s->audio_context,(GSTimerLifetimeRequest){.kind=GS_TIMER_BIND_SAVED,.binding={r.binding.identity}},&reply));}
        else if(r.kind==TIMER_LIFETIME_RESET_PIT){TRY(s->time.pit_command(s->time_context,r.pit_command));TRY(s->time.pit_counter(s->time_context,r.pit_low));TRY(s->time.pit_counter(s->time_context,r.pit_high));}
        else return GS_UNSUPPORTED;
        if(!timer_lifetime_consume(&w->timer,&w->timer_life,&r,r.kind,(TimerExternalBinding){0}))return GS_INVALID;
    }return GS_OK;
}
GSStatus game_audio_shutdown(GameWorld *w,GameServices *s){
    if(w->audio_reset.devices&2u)return GS_UNSUPPORTED;
    /* The historical live-DS latch is a foreign terminal observation after
     * timer removal. It is not the canonical C shutdown flag. */
    AudioFacadeWork flow=audio_facade_begin(AUDIO_FACADE_SHUTDOWN);
    AudioFacadeView view={.audio=&w->audio,.initialized=w->audio_initialized,.shutdown_latch=w->audio_shutdown};
    int foreign=0;
    for(;;){view.devices=w->audio_reset.devices;AudioFacadeRequest r=audio_facade_next(&view,&flow,0,0);
        switch(r.action){
        case AUDIO_FACADE_DONE:return GS_OK;
        case AUDIO_FACADE_CANCEL:foreign=!!(w->audio.fade.scheduled&1u);TRY(game_audio_cancel_fade(w,s));break;
        case AUDIO_FACADE_STOP_ADLIB:{AudioLifetimeWork life=audio_lifetime_begin(1);
            for(;;){AudioLifetimeRequest q=audio_lifetime_next(&life,&w->audio_attempted,w->audio.playback_timer_handle,0);
                if(q.action==AUDIO_LIFETIME_DONE)break;
                if(q.action==AUDIO_LIFETIME_REMOVE){TRY(timer_api(w,TIMER_API_REMOVE,TIMER_OPEN,0,q.value,0));foreign=1;}
                else if(q.action==AUDIO_LIFETIME_RESTORE)TRY(restore_timer(w,s));
                else if(q.action==AUDIO_LIFETIME_SILENCE)TRY(silence(w,s));else return GS_UNSUPPORTED;
            }break;}
        case AUDIO_FACADE_SHUTDOWN_LATCH:w->audio_reset.devices=view.devices;if(foreign)w->terminal_audio_latch=1;else w->audio_shutdown=1;break;
        default:return GS_UNSUPPORTED;
        }
    }
}
GSStatus game_audio_terminal(GameWorld *w,GameServices *s){
    LifecycleProcess flow;lifecycle_begin(&flow,LIFE_SOUND_SHUTDOWN);
    for(;;){LifecycleRequest r=lifecycle_next(&flow);if(r.action==LIFE_FINISHED)return GS_OK;
        if(!lifecycle_consume(&flow,r.action))return GS_INVALID;
        if(r.action==LIFE_STOP_MUSIC)TRY(game_audio_music_stop(w,s,r.argument).status);
        else if(r.action==LIFE_SOUND_STOP)TRY(game_audio_shutdown(w,s));else return GS_UNSUPPORTED;
    }
}
MusicClockResult game_audio_elapsed(const GameWorld *w){return music_clock_elapsed(w->audio.ticks,w->audio.time_origin,w->audio.ticks_per_unit);}
