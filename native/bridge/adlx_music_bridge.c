#include "platform.h"
#include "audio_projection.h"
#include "../adlx_music.h"

typedef struct MusicFrame {uint16_t sp,bp,si,di,ds;} MusicFrame;
static void music_push(Regs *r,uint16_t value) {r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,value);}
static MusicFrame music_enter(Regs *r,unsigned locals)
{
    MusicFrame f={r->sp,r->bp,r->si,r->di,r->ds};music_push(r,r->bp);r->bp=r->sp;r->sp=(uint16_t)(r->sp-locals);
    music_push(r,r->si);music_push(r,r->di);music_push(r,r->ds);r->ds=UGH_S_C_SoundSystemInitialized;return f;
}
static int music_leave(Regs *r,MusicFrame f,int status)
{if(status==UGH_CONTROL_TRANSFER) return status;r->sp=f.sp;r->bp=f.bp;r->si=f.si;r->di=f.di;r->ds=f.ds;return status;}
static int music_call(Regs *r,uint16_t bank,uint16_t target,uint16_t resume,const uint16_t *args,unsigned count)
{
    uint16_t sp=r->sp;for(unsigned i=count;i;i--) music_push(r,args[i-1]);
    music_push(r,r->cs);music_push(r,resume);int status=ugh_dispatch(bank,target,r);
    if(status!=UGH_CONTROL_TRANSFER) r->sp=sp;
    return status;
}
static uint16_t music_inc(Regs *r,uint16_t value)
{uint16_t carry=r->flags&CF;value=add16(r,value,1,0);flag(r,CF,carry);return value;}
static void music_delay_flags(Regs *r)
{unsigned product=4u*rd8(SOUND_SEG,S(SoundIoDelayMultiplier));flag(r,CF,product>255);flag(r,OF,product>255);}
static void music_emit(const AudioRegisterWrite *writes,unsigned count)
{for(unsigned i=0;i<count;i++) {platform_out(0x388,1,writes[i].reg);platform_out(0x389,1,writes[i].value);}}
static void music_publish_policy(const AudioState *state)
{
    wr16(SOUND_SEG,S(MainAdlxPlaying),state->playing);wr16(SOUND_SEG,S(MusicTrackVolume),state->track_volume);
    wr32(SOUND_SEG,S(MainAdlxTimeOrigin),state->time_origin);wr16(SOUND_SEG,S(CurrentAdlxSlot),state->current_channel);
    wr16(SOUND_SEG,S(MusicFadeStartVolume),state->fade.start_volume);wr16(SOUND_SEG,S(MusicFadeTargetVolume),state->fade.target_volume);
    wr16(SOUND_SEG,S(MusicFadeStep),state->fade.step_count);wr16(SOUND_SEG,S(MusicFadeDuration),state->fade.duration);
}
static int music_run(Regs *r,AudioMusicOperation operation)
{
    uint16_t duration=arg16(r,operation==AUDIO_MUSIC_START ? 4 : 0),volume=operation==AUDIO_MUSIC_START ? arg16(r,6) : 0;
    AudioCursor resource={0};if(operation==AUDIO_MUSIC_START) resource=audio_bridge_cursor(arg16(r,2),arg16(r,0));
    AudioMusicWork work=audio_music_begin(operation,resource,duration,volume,rd16(SOUND_SEG,S(SoundDeviceBits)));
    MusicFrame f=music_enter(r,0);r->es=SOUND_SEG;r->ax=65535;
    for(;;) {
        AudioState state;audio_bridge_project(SOUND_SEG,&state);AudioMusicRequest request=audio_music_next(&state,&work,r->ax);
        music_publish_policy(&state);
        if(request.action==AUDIO_MUSIC_DONE) {if(work.result==1) r->es=SOUND_SEG;r->ax=work.result;return music_leave(r,f,UGH_OK);}
        if(request.action==AUDIO_MUSIC_WAIT_BOUND) return music_leave(r,f,UGH_BUDGET);
        int status;uint16_t args[4];unsigned count=0;uint16_t bank=SOUND_SEG,target=0,resume=0;
        switch(request.action) {
        case AUDIO_MUSIC_CANCEL:target=S(CancelMusicFade);resume=operation==AUDIO_MUSIC_START ? UGH_O_C_StartMusicTrack+0x2a : work.stage==2 ? UGH_O_C_StopMusicTrack+0x48 : UGH_O_C_StopMusicTrack+0xb3;break;
        case AUDIO_MUSIC_LOAD:bank=UGH_SEG_C;target=UGH_O_C_LoadAdlibTrackData;resume=UGH_O_C_StartMusicTrack+0x38;args[0]=request.channel;args[1]=request.resource.index;args[2]=audio_bridge_bank(request.resource);args[3]=0;count=4;break;
        case AUDIO_MUSIC_START_CHANNEL:bank=UGH_SEG_C;target=UGH_O_C_StartAdlibTrackChannel;resume=UGH_O_C_StartMusicTrack+(duration ? 0x6c : 0x58);args[0]=request.channel;args[1]=request.volume;count=2;break;
        case AUDIO_MUSIC_SET_VOLUME:bank=UGH_SEG_C;target=UGH_O_C_SetMusicTrackVolume;resume=UGH_O_C_StartMusicTrack+0x61;args[0]=request.volume;count=1;break;
        case AUDIO_MUSIC_SCHEDULE:target=S(ScheduleMusicFade);resume=operation==AUDIO_MUSIC_START ? UGH_O_C_StartMusicTrack+0xa0 : UGH_O_C_StopMusicTrack+0x93;break;
        case AUDIO_MUSIC_STOP_CHANNEL:bank=UGH_SEG_C;target=UGH_O_C_StopAdlibTrackChannel;resume=UGH_O_C_StopMusicTrack+0x2d;args[0]=request.channel;count=1;break;
        case AUDIO_MUSIC_SILENCE:target=S(SilenceAdlibOperators);resume=UGH_O_C_StopMusicTrack+0xc4;break;
        case AUDIO_MUSIC_TIMER_WAIT:
            status=platform_service_point_at(SERVICE_TIMER_WAIT,UGH_SEG_C,UGH_O_C_StopMusicTrack+0x95,r);
            if(status) return music_leave(r,f,status);
            continue;
        default:return music_leave(r,f,UGH_UNSUPPORTED);
        }
        status=music_call(r,bank,target,resume,args,count);if(status) return music_leave(r,f,status);
    }
}
EXPORT int c_StartMusicTrack(Regs *r) {return music_run(r,AUDIO_MUSIC_START);}
EXPORT int c_StopMusicTrack(Regs *r) {return music_run(r,AUDIO_MUSIC_STOP);}
EXPORT int c_SetMusicTrackVolume(Regs *r)
{
    uint16_t volume=arg16(r,0);AudioState state;audio_bridge_project(SOUND_SEG,&state);
    AudioMusicVolume result=audio_music_volume(&state,rd16(SOUND_SEG,S(SoundDeviceBits)),volume);
    MusicFrame f=music_enter(r,2);r->es=SOUND_SEG;r->ax=result.result;
    if(result.result==1) {
        wr16(SOUND_SEG,S(MusicTrackVolume),state.track_volume);wr16(SOUND_SEG,S(CurrentAdlxSlot),state.current_channel);
        for(unsigned i=0;i<9;i++) {audio_bridge_publish_voice(SOUND_SEG,(uint16_t)(S(AdlibVoiceStates)+20*i),&state.live[i]);audio_bridge_publish_voice(SOUND_SEG,(uint16_t)(S(SavedAdlibVoiceStates)+20*i),&state.displaced[i]);}
        music_emit(result.writes,result.write_count);if(result.write_count) music_delay_flags(r);
    }
    return music_leave(r,f,UGH_OK);
}
EXPORT int c_ScheduleMusicFade(Regs *r)
{
    AudioState state;audio_bridge_project(r->cs,&state);AudioFadeRequest request=audio_music_schedule(&state);
    if(request.action==AUDIO_FADE_REGISTER) {
        r->bx=(uint16_t)request.interval;r->cx=(uint16_t)(request.interval>>16);r->ax=S(AdvanceMusicFade);r->dx=SOUND_SEG;
        int status=music_call(r,TIMER_SEG,T(RegisterTimerCallback),S(ScheduleMusicFade)+0x1d,0,0);if(status) return status;
        /* Callback storage may have changed during the service; publish only
         * this completion's two owned words, never an old AudioState. */
        audio_music_registered(&state,r->ax);wr16(r->cs,S(MusicFadeTimerHandle),state.fade.timer_handle);wr16(r->cs,S(MusicFadeScheduled),state.fade.scheduled);
    }
    return UGH_OK;
}
EXPORT int c_CancelMusicFade(Regs *r)
{
    AudioState state;audio_bridge_project(r->cs,&state);AudioFadeRequest request=audio_music_cancel(&state);
    if(request.action==AUDIO_FADE_REMOVE) {
        r->ax=request.handle;int status=music_call(r,TIMER_SEG,T(RemoveTimerCallback),S(CancelMusicFade)+0x15,0,0);if(status) return status;
        audio_music_cancelled(&state);wr16(r->cs,S(MusicFadeScheduled),state.fade.scheduled);
    }
    return UGH_OK;
}
EXPORT int c_AdvanceMusicFade(Regs *r)
{
    Regs save=*r;AudioState state;audio_bridge_project(r->cs,&state);
    r->sp=(uint16_t)(r->sp-8);r->dx=music_inc(r,state.fade.step_count);r->bx=state.fade.duration;
    AudioFadeRequest request=audio_music_fade_step(&state);wr16(r->cs,S(MusicFadeStep),state.fade.step_count);
    if(request.action!=AUDIO_FADE_REMOVE) r->cx=state.fade.start_volume;
    if(request.action==AUDIO_FADE_FAULT) return UGH_UNSUPPORTED;
    int status;
    if(request.action==AUDIO_FADE_REMOVE) {
        r->ax=request.handle;status=music_call(r,TIMER_SEG,T(RemoveTimerCallback),S(AdvanceMusicFade)+0x43,0,0);
        if(!status) {audio_music_cancelled(&state);wr16(r->cs,S(MusicFadeScheduled),state.fade.scheduled);}
    } else {
        r->dx=request.remainder;r->ax=request.volume;uint16_t args[1]={request.volume};
        status=music_call(r,UGH_SEG_C,UGH_O_C_SetMusicTrackVolume,S(AdvanceMusicFade)+0x32,args,1);
    }
    r->ax=save.ax;r->bx=save.bx;r->cx=save.cx;r->dx=save.dx;r->sp=save.sp;return status;
}
EXPORT int c_AdvanceGuardedSoundClock(Regs *r)
{
    AudioState state;audio_bridge_project(r->cs,&state);uint32_t old=state.ticks;
    int entered=audio_music_guard_begin(&state);music_inc(r,(uint16_t)old);if(!(uint16_t)state.ticks) music_inc(r,(uint16_t)(old>>16));
    wr32(r->cs,S(AdlxTickCount),state.ticks);
    if(entered) {
        wr16(r->cs,S(AdlxPlaybackGuard),state.playback_guard);int status=music_call(r,r->cs,S(TickAdlxPlayback),S(AdvanceGuardedSoundClock)+0x27,0,0);if(status) return status;
        audio_music_guard_end(&state);wr16(r->cs,S(AdlxPlaybackGuard),state.playback_guard);
    }
    return UGH_OK;
}
EXPORT int c_SilenceAdlibOperators(Regs *r)
{
    AudioState state;audio_bridge_project(r->cs,&state);AudioRegisterWrite writes[20];audio_music_silence(&state,writes);
    music_emit(writes,20);r->bx=(uint16_t)((unsigned)writes[19].reg*256u+writes[19].value);r->cx=0;music_delay_flags(r);return UGH_OK;
}
