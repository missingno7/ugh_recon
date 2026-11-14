#include "platform.h"
#include "audio_projection.h"
#include "../adlx_facade.h"
typedef struct FacadeFrame {uint16_t sp,bp,si,di,ds;} FacadeFrame;
static void facade_push(Regs *r,uint16_t value) {r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,value);}
static FacadeFrame facade_enter(Regs *r,AudioFacadeOperation operation)
{
    FacadeFrame f={r->sp,r->bp,r->si,r->di,r->ds};facade_push(r,r->bp);r->bp=r->sp;
    if(operation!=AUDIO_FACADE_SHUTDOWN) facade_push(r,r->si);
    if(operation==AUDIO_FACADE_INIT) facade_push(r,r->di);
    facade_push(r,r->ds);r->ds=UGH_S_C_SoundSystemInitialized;return f;
}
static int facade_leave(Regs *r,FacadeFrame f,int status)
{if(status==UGH_CONTROL_TRANSFER) return status;r->sp=f.sp;r->bp=f.bp;r->si=f.si;r->di=f.di;r->ds=f.ds;return status;}
static int facade_call(Regs *r,uint16_t bank,uint16_t target,uint16_t resume,const uint16_t *args,unsigned count)
{
    uint16_t sp=r->sp;for(unsigned i=count;i;i--) facade_push(r,args[i-1]);facade_push(r,r->cs);facade_push(r,resume);
    int status=ugh_dispatch(bank,target,r);if(status!=UGH_CONTROL_TRANSFER) r->sp=sp;return status;
}
static int facade_run(Regs *r,AudioFacadeOperation operation)
{
    (void)audio_bridge_publish_voice;(void)audio_bridge_bank;
    FacadeFrame f=facade_enter(r,operation);
    if(operation==AUDIO_FACADE_INIT) {
        r->si=logic(r,0,16);
        if(rd16(r->ds,UGH_O_C_SoundSystemInitialized)) {r->ax=SOUND_SEG;r->es=r->ax;}
    } else r->es=SOUND_SEG;
    AudioFacadeWork work=audio_facade_begin(operation);
    for(;;) {
        AudioState state;audio_bridge_project(SOUND_SEG,&state);
        AudioFacadeView view={&state,rd16(SOUND_SEG,S(SoundDeviceBits)),rd16(UGH_S_C_SoundSystemInitialized,UGH_O_C_SoundSystemInitialized),rd16(UGH_S_C_SoundSystemInitialized,UGH_O_C_SoundSystemShutdown),rd16(SOUND_SEG,S(ActiveSampleVoiceCount))};
        uint16_t old=work.stage,bits=work.collected,requested=operation==AUDIO_FACADE_INIT ? rd16(r->ss,(uint16_t)(f.sp+4)) : 0;
        AudioFacadeRequest request=audio_facade_next(&view,&work,requested,r->ax);
        if(operation==AUDIO_FACADE_INIT) {
            if(old==2) logic(r,requested&2u,16);
            if(old==3) logic(r,r->ax,16);
            if(old==4 || (old==3 && request.action!=AUDIO_FACADE_BROKEN_HOOK) || (old==2 && !(requested&2u))) logic(r,requested&1u,16);
            if(old==5) logic(r,r->ax,16);
            if(bits!=work.collected) r->si=logic(r,work.collected,16);
        }
        wr16(SOUND_SEG,S(AdlxPlaybackGuard),state.playback_guard);wr16(SOUND_SEG,S(SoundDeviceBits),view.devices);
        uint16_t bank=SOUND_SEG,target=0,resume=0,args[2];unsigned count=0;int status;
        switch(request.action) {
        case AUDIO_FACADE_DONE:if(operation==AUDIO_FACADE_START) r->es=SOUND_SEG;return facade_leave(r,f,UGH_OK);
        case AUDIO_FACADE_STOP_SYSTEM:bank=UGH_SEG_C;target=UGH_O_C_ShutdownSoundSystem;resume=UGH_O_C_InitializeSoundSystem+0x26;break;
        case AUDIO_FACADE_CLEAR:target=S(ClearSoundState);resume=UGH_O_C_InitializeSoundSystem+0x2b;break;
        case AUDIO_FACADE_INIT_DSP:target=S(InitializeDspPlayback);resume=UGH_O_C_InitializeSoundSystem+0x37;break;
        case AUDIO_FACADE_INIT_ADLIB:target=S(InitializeAdlibPlayback);resume=UGH_O_C_InitializeSoundSystem+0x67;break;
        case AUDIO_FACADE_CANCEL:target=S(CancelMusicFade);resume=UGH_O_C_ShutdownSoundSystem+0x30;break;
        case AUDIO_FACADE_STOP_DSP:target=S(ShutdownDspPlayback);resume=UGH_O_C_ShutdownSoundSystem+0x43;break;
        case AUDIO_FACADE_STOP_ADLIB:target=S(ShutdownAdlibPlayback);resume=UGH_O_C_ShutdownSoundSystem+0x56;break;
        case AUDIO_FACADE_PRIME:target=S(PrimeSampleDmaPlayback);resume=UGH_O_C_StartSoundOutputs+0x2a;break;
        case AUDIO_FACADE_START_CHANNEL:bank=UGH_SEG_C;target=UGH_O_C_StartAdlibTrackChannel;resume=UGH_O_C_StartSoundOutputs+0x52;args[0]=request.channel;args[1]=request.volume;count=2;break;
        case AUDIO_FACADE_BROKEN_HOOK:
            r->di=logic(r,0,16);status=ugh_call_near_ret_hook(r,G(loc_001F),UGH_O_C_InitializeSoundSystem+0x47);return facade_leave(r,f,status);
        case AUDIO_FACADE_INITIALIZED:
            r->ax=SOUND_SEG;r->es=r->ax;wr16(r->ds,UGH_O_C_SoundSystemInitialized,1);r->ax=work.collected;return facade_leave(r,f,UGH_OK);
        case AUDIO_FACADE_SHUTDOWN_LATCH:r->es=SOUND_SEG;wr16(r->ds,UGH_O_C_SoundSystemShutdown,1);return facade_leave(r,f,UGH_OK);
        default:return facade_leave(r,f,UGH_UNSUPPORTED);
        }
        status=facade_call(r,bank,target,resume,args,count);if(status) return facade_leave(r,f,status);
    }
}
EXPORT int c_InitializeSoundSystem(Regs *r) {return facade_run(r,AUDIO_FACADE_INIT);}
EXPORT int c_ShutdownSoundSystem(Regs *r) {return facade_run(r,AUDIO_FACADE_SHUTDOWN);}
EXPORT int c_StartSoundOutputs(Regs *r) {return facade_run(r,AUDIO_FACADE_START);}
static int facade_duration_arm(uint16_t bank,uint8_t code)
{
    if((code>>4)>7) return 8;
    switch(rd16(bank,(uint16_t)(UGH_O_C_DurationSwitchTable+2u*(code>>4)))) {
    case UGH_O_C_DurationLongWait:return 0;case UGH_O_C_DurationFrequency:return 1;
    case UGH_O_C_DurationKeyOff:return 2;case UGH_O_C_DurationVolume:return 3;
    case UGH_O_C_DurationInstrument:return 4;case UGH_O_C_DurationTimer:return 6;
    case UGH_O_C_DurationExtension:return 7;case UGH_O_C_DurationDefault:return 8;
    default:return -1;
    }
}
EXPORT int c_GetMusicTrackDuration(Regs *r)
{
    r->es=SOUND_SEG;uint16_t devices=rd16(SOUND_SEG,S(SoundDeviceBits)),playing=rd16(SOUND_SEG,S(MainAdlxPlaying)),rate=rd16(SOUND_SEG,S(MusicTicksPerUnit));
    AudioDurationWork work=audio_duration_begin(devices,playing,rate,rd16(SOUND_SEG,S(MainAdlxStartPointer)),rd16(SOUND_SEG,S(MusicEventStreamLength)));
    AudioCursor cursor=audio_bridge_pointer(SOUND_SEG,S(MainAdlxStartPointer));
    for(;;) {
        uint16_t at=work.position;int running=audio_duration_fetch(&work);if(running<0) return UGH_BUDGET;if(!running) break;
        uint8_t code=rd8(audio_bridge_bank(cursor),at);int arm=facade_duration_arm(r->cs,code);
        uint8_t payload=arm==0 || arm==7 ? rd8(audio_bridge_bank(cursor),work.position) : 0;
        if(!audio_duration_step(&work,code,arm,payload)) return UGH_BAD_CALLBACK;
    }
    AudioDurationResult result=audio_duration_result(&work,rd16(SOUND_SEG,S(MusicTicksPerUnit)));
    if(result.fault) return UGH_UNSUPPORTED;
    r->ax=result.value;return UGH_OK;
}

