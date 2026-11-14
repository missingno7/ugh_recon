#include "platform.h"
#include "../lifecycle.h"
#include <stdlib.h>
static void lc_require(int condition){if(!condition)abort();}
static uint16_t lc_word(uint16_t native_value,uint16_t literal){lc_require(native_value==literal);return native_value;}
static LifecycleRequest lc_take(LifecycleProcess *p,LifecycleAction expected){LifecycleRequest e=lifecycle_next(p);lc_require(e.action==expected && lifecycle_consume(p,e.action));return e;}
static void lc_finish(LifecycleProcess *p){lc_require(lifecycle_complete(p));}
static void push(Regs *r,uint16_t x) {
    r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,x);
}

static uint16_t pop(Regs *r) {
    uint16_t x=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return x;
}

static int video_far_call(Regs *r,uint16_t seg,uint16_t off,uint16_t ret) {
    push(r,r->cs); push(r,ret); int st=ugh_dispatch(seg,off,r);
    if(st!=UGH_CONTROL_TRANSFER) r->sp=(uint16_t)(r->sp+4);
    return st;
}

static int lc_call(Regs *r,LifecycleProcess *p,uint16_t target,uint16_t ret){
 LifecycleAction action;
 if(target==G(InitializeDosVideoInputAndSound))action=LIFE_INITIALIZE_PLATFORM;
 else if(target==G(ShowStartupPictures))action=LIFE_STARTUP_PICTURES;
 else if(target==G(ConfigureVgaGameplayPages))action=LIFE_GAMEPLAY_VIDEO;
 else if(target==G(RunMainMenuAndAttractLoop))action=LIFE_MAIN_MENU;
 else if(target==G(InstallDosCriticalErrorFailHandler))action=LIFE_INSTALL_ERROR_HANDLER;
 else if(target==G(LoadHighScores))action=LIFE_LOAD_SCORES;
 else if(target==G(SeedRandomFromDosSeconds))action=LIFE_SEED_RANDOM;
 else if(target==G(ConfigureVgaPicturePages))action=LIFE_PICTURE_VIDEO;
 else if(target==G(InstallKeyboardSequenceInterrupt))action=LIFE_INSTALL_KEYBOARD;
 else if(target==G(DetectAndCalibrateJoysticks))action=LIFE_CALIBRATE_CONTROLS;
 else {lc_require(target==G(InitializeAdLibSound));action=LIFE_INITIALIZE_AUDIO;}
 lc_take(p,action);return ugh_call_near(target,ret,r);
}
#define MCALL(n,ret) do{int status=lc_call(r,&plan,G(n),ret);if(status)return status;}while(0)
EXPORT int c_RunDosGame(Regs *r) {
    LifecycleProcess plan;lifecycle_begin(&plan,LIFE_PROGRAM);lc_take(&plan,LIFE_BIND_WORLD);
    r->dx=DATA_SEG; r->ds=r->dx;
    MCALL(InitializeDosVideoInputAndSound,G(RunDosGame)+8);
    MCALL(ShowStartupPictures,G(RunDosGame)+11);
    MCALL(ConfigureVgaGameplayPages,G(RunDosGame)+14);
    MCALL(RunMainMenuAndAttractLoop,G(RunDosGame)+17);
    lc_take(&plan,LIFE_SHUTDOWN_PLATFORM);lc_finish(&plan);return ugh_dispatch(r->cs,G(loc_4EE6),r);
}

EXPORT int c_InitializeDosVideoInputAndSound(Regs *r) {
    LifecycleProcess plan;lifecycle_begin(&plan,LIFE_PLATFORM_INIT);lc_take(&plan,LIFE_QUERY_VIDEO);
    set_ah(r,15); int st=platform_interrupt(0x10,r); if(st) return st;
    lifecycle_video_reply(&plan,r->ax);LifecycleRequest mode=lc_take(&plan,LIFE_SAVE_VIDEO);
    set_al(r,(uint8_t)logic(r,r->ax&0x7f,8)); wr8(r->ds,D(SavedBiosVideoMode),(uint8_t)lc_word(mode.argument,(uint8_t)r->ax));lc_take(&plan,LIFE_CPU_PROBE);
    r->ax=logic(r,0,16); push(r,r->ax); r->flags=(uint16_t)(pop(r)|2);
    push(r,r->flags); r->ax=pop(r); r->ax=logic(r,r->ax&0xf000,16); sub16(r,r->ax,0xf000,0);
    st=lc_call(r,&plan,G(InstallDosCriticalErrorFailHandler),G(InitializeDosVideoInputAndSound)+0x20); if(st) return st;
    st=lc_call(r,&plan,G(LoadHighScores),G(InitializeDosVideoInputAndSound)+0x23); if(st) return st;
    st=lc_call(r,&plan,G(SeedRandomFromDosSeconds),G(InitializeDosVideoInputAndSound)+0x26); if(st) return st;
    LifecycleRequest video_mode=lc_take(&plan,LIFE_SET_VIDEO);
    flag(r,DF,0); r->ax=lc_word(video_mode.argument,0x13); st=platform_interrupt(0x10,r); if(st) return st;
    st=lc_call(r,&plan,G(ConfigureVgaPicturePages),G(InitializeDosVideoInputAndSound)+0x2f); if(st) return st;
    st=lc_call(r,&plan,G(InstallKeyboardSequenceInterrupt),G(InitializeDosVideoInputAndSound)+0x32); if(st) return st;
    st=lc_call(r,&plan,G(DetectAndCalibrateJoysticks),G(InitializeDosVideoInputAndSound)+0x35); if(st) return st;
    st=lc_call(r,&plan,G(InitializeAdLibSound),G(InitializeDosVideoInputAndSound)+0x38); if(st) return st;
    lc_take(&plan,LIFE_CLEAR_VIDEO);lc_finish(&plan);return c_ClearAllVgaPlanes(r);
}

EXPORT int c_InitializeAdLibSound(Regs *r) {
    LifecycleProcess plan;lifecycle_begin(&plan,LIFE_ADLIB_INIT);LifecycleRequest e=lc_take(&plan,LIFE_SOUND_INITIALIZE_ADLIB);
    push(r,lc_word(e.argument,1)); int st=video_far_call(r,UGH_S_C_InitializeSoundSystem,UGH_O_C_InitializeSoundSystem,G(InitializeAdLibSound)+7);
    if(st) return st;
    r->sp=add16(r,r->sp,2,0);lc_finish(&plan);return UGH_OK;
}

EXPORT int c_FadeAndShutdownSound(Regs *r) {
    LifecycleProcess plan;lifecycle_begin(&plan,LIFE_SOUND_SHUTDOWN);LifecycleRequest e=lc_take(&plan,LIFE_STOP_MUSIC);
    push(r,lc_word(e.argument,0x11)); int st=video_far_call(r,UGH_S_C_StopMusicTrack,UGH_O_C_StopMusicTrack,G(FadeAndShutdownSound)+7);
    if(st) return st;
    r->sp=add16(r,r->sp,2,0);
    lc_take(&plan,LIFE_SOUND_STOP);lc_finish(&plan);return video_far_call(r,UGH_S_C_ShutdownSoundSystem,UGH_O_C_ShutdownSoundSystem,G(FadeAndShutdownSound)+15);
}

