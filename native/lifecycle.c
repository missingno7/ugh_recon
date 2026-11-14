#include "lifecycle.h"

static const LifecycleAction program_actions[]={LIFE_BIND_WORLD,LIFE_INITIALIZE_PLATFORM,
    LIFE_STARTUP_PICTURES,LIFE_GAMEPLAY_VIDEO,LIFE_MAIN_MENU,LIFE_SHUTDOWN_PLATFORM};
static const LifecycleAction initialize_actions[]={LIFE_QUERY_VIDEO,LIFE_SAVE_VIDEO,
    LIFE_CPU_PROBE,LIFE_INSTALL_ERROR_HANDLER,LIFE_LOAD_SCORES,LIFE_SEED_RANDOM,
    LIFE_SET_VIDEO,LIFE_PICTURE_VIDEO,LIFE_INSTALL_KEYBOARD,LIFE_CALIBRATE_CONTROLS,
    LIFE_INITIALIZE_AUDIO,LIFE_CLEAR_VIDEO};
static const LifecycleAction sound_initialize_actions[]={LIFE_SOUND_INITIALIZE_ADLIB};
static const LifecycleAction sound_shutdown_actions[]={LIFE_STOP_MUSIC,LIFE_SOUND_STOP};

static unsigned lifecycle_length(LifecycleTask task){
    if(task==LIFE_PROGRAM)return 6;
    if(task==LIFE_PLATFORM_INIT)return 12;
    if(task==LIFE_ADLIB_INIT)return 1;
    if(task==LIFE_SOUND_SHUTDOWN)return 2;
    return 0;
}
static LifecycleAction lifecycle_action(LifecycleTask task,unsigned at){
    if(task==LIFE_PROGRAM)return program_actions[at];
    if(task==LIFE_PLATFORM_INIT)return initialize_actions[at];
    if(task==LIFE_ADLIB_INIT)return sound_initialize_actions[at];
    return sound_shutdown_actions[at];
}
void lifecycle_begin(LifecycleProcess *p,LifecycleTask task){
    p->task=task;p->saved_mode=0;p->cursor=p->pending=p->failed=0;
    if(!lifecycle_length(task))p->failed=1;
}
uint8_t lifecycle_saved_mode(uint16_t value){return (uint8_t)(value&127u);}
LifecycleRequest lifecycle_next(LifecycleProcess *p){
    LifecycleRequest r;r.argument=0;
    if(p->failed || p->pending){p->failed=1;r.action=LIFE_INVALID;return r;}
    if(p->cursor>=lifecycle_length(p->task)){r.action=LIFE_FINISHED;return r;}
    r.action=lifecycle_action(p->task,p->cursor);
    if(r.action==LIFE_SAVE_VIDEO)r.argument=p->saved_mode;
    if(r.action==LIFE_SET_VIDEO)r.argument=19;
    if(r.action==LIFE_SOUND_INITIALIZE_ADLIB)r.argument=1;
    if(r.action==LIFE_STOP_MUSIC)r.argument=17;
    p->pending=1;return r;
}
int lifecycle_consume(LifecycleProcess *p,LifecycleAction action){
    if(p->failed || !p->pending || p->cursor>=lifecycle_length(p->task) || action!=lifecycle_action(p->task,p->cursor)){
        p->failed=1;return 0;}
    p->pending=0;p->cursor=(uint8_t)(p->cursor+1u);return 1;
}
void lifecycle_video_reply(LifecycleProcess *p,uint16_t value){p->saved_mode=lifecycle_saved_mode(value);}
int lifecycle_complete(const LifecycleProcess *p){
    return !p->failed && !p->pending && p->cursor==lifecycle_length(p->task);
}
