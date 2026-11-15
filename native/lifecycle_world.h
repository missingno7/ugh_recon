#ifndef NATIVE_LIFECYCLE_WORLD_H
#define NATIVE_LIFECYCLE_WORLD_H
#include "lifecycle.h"
#include "terminal_tail.h"

/* A terminal reply retains the byte returned by the last input service. */
typedef enum GameExitKind { GAME_CONTINUE, GAME_SERVICE_FAILED, GAME_EXITED } GameExitKind;
typedef struct GameExit { GameExitKind kind; uint8_t code; } GameExit;
typedef struct LifecycleReply { GameExit result; uint16_t value; } LifecycleReply;
typedef LifecycleReply (*LifecycleService)(void *context, LifecycleRequest request);
typedef LifecycleReply (*LifecycleTerminalService)(void *context, TerminalAction action, uint8_t value);
typedef uint8_t (*LifecycleSavedModeReader)(void *context);
typedef struct NativeLifecycleWorld {
    uint8_t saved_bios_video_mode;
    LifecycleProcess continuation[4];
    TerminalTail terminal;
} NativeLifecycleWorld;
NativeLifecycleWorld *native_lifecycle_world(void);
GameExit lifecycle_world_execute(NativeLifecycleWorld *world, LifecycleTask task,
    LifecycleService service, void *context);
GameExit lifecycle_world_terminate(NativeLifecycleWorld *world,
    LifecycleTerminalService service, LifecycleSavedModeReader saved_mode, void *context);
#endif
