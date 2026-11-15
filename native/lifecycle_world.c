#include "lifecycle_world.h"
static NativeLifecycleWorld world;
NativeLifecycleWorld *native_lifecycle_world(void) { return &world; }

GameExit lifecycle_world_execute(NativeLifecycleWorld *owner, LifecycleTask task,
    LifecycleService service, void *context) {
    GameExit done={GAME_CONTINUE,0};
    if(task<LIFE_PROGRAM || task>LIFE_SOUND_SHUTDOWN) {
        done.kind=GAME_SERVICE_FAILED;return done;
    }
    LifecycleProcess *process=&owner->continuation[task];
    lifecycle_begin(process,task);
    for(;;) {
        LifecycleRequest request=lifecycle_next(process);
        if(request.action==LIFE_FINISHED)return done;
        if(!lifecycle_consume(process,request.action)) {
            done.kind=GAME_SERVICE_FAILED;return done;
        }
        LifecycleReply reply=service(context,request);
        if(reply.result.kind!=GAME_CONTINUE)return reply.result;
        if(request.action==LIFE_QUERY_VIDEO)lifecycle_video_reply(process,reply.value);
    }
}

GameExit lifecycle_world_terminate(NativeLifecycleWorld *owner,
    LifecycleTerminalService service, LifecycleSavedModeReader saved_mode, void *context) {
    GameExit done={GAME_CONTINUE,0};
    terminal_tail_begin(&owner->terminal);
    for(;;) {
        TerminalAction action=terminal_tail_next(&owner->terminal);
        if(action==TERMINAL_COMPLETE)return done;
        /* Neither a parent snapshot nor the post-init mode is a restore value. */
        uint8_t value=0;
        if(action==TERMINAL_RESTORE_VIDEO)value=saved_mode(context);
        if(action==TERMINAL_EXIT)value=done.code;
        LifecycleReply reply=service(context,action,value);
        /* A terminal acknowledgement need not echo its argument. The result
         * belongs to the consumed input reply, not to a provider's default. */
        if(action==TERMINAL_EXIT && reply.result.kind==GAME_EXITED) {
            done.kind=GAME_EXITED;return done;
        }
        if(reply.result.kind!=GAME_CONTINUE)return reply.result;
        if(action==TERMINAL_RESTORE_INPUT)done.code=(uint8_t)reply.value;
        if(action==TERMINAL_EXIT){done.kind=GAME_EXITED;return done;}
    }
}
