#include "timer_lifetime.h"

void timer_lifetime_install(TimerState *state, TimerLifetimeRequest *request) {
    *request=(TimerLifetimeRequest){0};
    if (state->installed) return;
    state->installed=1;
    request->kind=TIMER_LIFETIME_READ_BINDING;
}
void timer_lifetime_restore(TimerState *state, const TimerLifetime *life, TimerLifetimeRequest *request) {
    *request=(TimerLifetimeRequest){0};
    if (!state->installed) return;
    state->installed=0;
    request->kind=TIMER_LIFETIME_BIND_SAVED;
    request->binding=life->saved;
}
void timer_lifetime_chain(const TimerLifetime *life, TimerLifetimeRequest *request) {
    *request=(TimerLifetimeRequest){0};
    request->kind=TIMER_LIFETIME_DELIVER;
    request->binding=life->saved;
    request->enable_interrupts=1;
}
int timer_lifetime_consume(TimerState *state, TimerLifetime *life,
    TimerLifetimeRequest *request, TimerLifetimeKind completed, TimerExternalBinding reply) {
    if (completed==TIMER_LIFETIME_NONE || request->kind!=completed) return 0;
    switch (completed) {
    case TIMER_LIFETIME_READ_BINDING:
        life->saved=reply;
        state->slots[0].target=timer_target(TIMER_BIOS_CHAIN);
        state->quantum=65536u; state->earliest=65536u;
        state->slots[0].interval=65536u; state->slots[0].remaining=65536u;
        for (unsigned i=0;i<TIMER_CAPACITY;i++) state->by_handle[i]=TIMER_FREE;
        state->by_handle[0]=0; state->slots[0].handle=0; state->count=1;
        /* Due, inactive records and programmed_divisor deliberately stay stale. */
        request->kind=TIMER_LIFETIME_BIND_TIMER;
        break;
    case TIMER_LIFETIME_BIND_SAVED:
        request->kind=TIMER_LIFETIME_RESET_PIT;
        request->pit_command=0x36; request->pit_low=0; request->pit_high=0;
        break;
    case TIMER_LIFETIME_BIND_TIMER:
    case TIMER_LIFETIME_RESET_PIT:
    case TIMER_LIFETIME_DELIVER:
        request->kind=TIMER_LIFETIME_NONE;
        break;
    default: return 0;
    }
    return 1;
}
int timer_lifetime_apply(TimerState *state, const TimerApiRequest *request, TimerApiResult *result) {
    if (request->kind==TIMER_API_REGISTER) {
        if (request->callback<TIMER_BIOS_CHAIN || request->callback>TIMER_FIXTURE_IRQ) return 0;
        int handle=timer_register(state,request->callback,request->interval);
        if (handle<0) return 0;
        result->handle=(uint16_t)handle;
    } else if (request->kind==TIMER_API_REMOVE) {
        if (state->count<2 || state->count>TIMER_CAPACITY || timer_handle_slot(state,request->handle)<0) return 0;
        result->handle=timer_remove(state,request->handle);
    } else return 0;
    result->minimum=state->earliest;
    return 1;
}
