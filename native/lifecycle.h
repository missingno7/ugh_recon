#ifndef NATIVE_LIFECYCLE_H
#define NATIVE_LIFECYCLE_H
#include <stdint.h>

typedef enum LifecycleTask {LIFE_PROGRAM,LIFE_PLATFORM_INIT,LIFE_ADLIB_INIT,LIFE_SOUND_SHUTDOWN} LifecycleTask;
typedef enum LifecycleAction {
    LIFE_BIND_WORLD,LIFE_INITIALIZE_PLATFORM,LIFE_STARTUP_PICTURES,LIFE_GAMEPLAY_VIDEO,
    LIFE_MAIN_MENU,LIFE_SHUTDOWN_PLATFORM,LIFE_QUERY_VIDEO,LIFE_SAVE_VIDEO,
    LIFE_CPU_PROBE,LIFE_INSTALL_ERROR_HANDLER,LIFE_LOAD_SCORES,LIFE_SEED_RANDOM,
    LIFE_SET_VIDEO,LIFE_PICTURE_VIDEO,LIFE_INSTALL_KEYBOARD,LIFE_CALIBRATE_CONTROLS,
    LIFE_INITIALIZE_AUDIO,LIFE_CLEAR_VIDEO,LIFE_SOUND_INITIALIZE_ADLIB,
    LIFE_STOP_MUSIC,LIFE_SOUND_STOP,LIFE_FINISHED,LIFE_INVALID
} LifecycleAction;
typedef struct LifecycleRequest {LifecycleAction action;uint16_t argument;} LifecycleRequest;
typedef struct LifecycleProcess {
    LifecycleTask task;
    uint16_t saved_mode;
    uint8_t cursor,pending,failed;
} LifecycleProcess;

void lifecycle_begin(LifecycleProcess *process,LifecycleTask task);
LifecycleRequest lifecycle_next(LifecycleProcess *process);
/* Consume before entering a synchronous service. Failure propagates immediately
 * in the caller: there is no synthesized rollback or shutdown on an error. */
int lifecycle_consume(LifecycleProcess *process,LifecycleAction action);
void lifecycle_video_reply(LifecycleProcess *process,uint16_t value);
int lifecycle_complete(const LifecycleProcess *process);
uint8_t lifecycle_saved_mode(uint16_t value);
#endif
