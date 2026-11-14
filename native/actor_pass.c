#include "actor_pass.h"
void actor_pass_begin(ActorPass *pass) {
    pass->cursor=0; pass->remaining=32768u;
}
ActorPassAction actor_pass_select(const ActorPass *pass,uint16_t descriptor,ActorCallback callback) {
    if (!pass->remaining) return ACTOR_PASS_LIMIT;
    if (descriptor==UINT16_MAX) return ACTOR_PASS_DONE;
    if (callback<=ACTOR_CALLBACK_UNSUPPORTED || callback>=ACTOR_CALLBACK_COUNT)
        return ACTOR_PASS_UNSUPPORTED;
    return ACTOR_PASS_CALL;
}
void actor_pass_resume(ActorPass *pass,uint16_t live_cursor) {
    /* Deliberately advance the returned cursor, not the pre-call cursor. */
    pass->cursor=(uint16_t)(live_cursor+2u); --pass->remaining;
}
void actor_reserved_return(void) {}
