#include "timer_lifetime.h"
void __CPROVER_assert(int,const char *);
void __CPROVER_assume(int);
TimerState nondet_state(void);
TimerExternalBinding nondet_binding(void);
unsigned nondet_unsigned(void);
#define CHECK(c) __CPROVER_assert((c),#c)
#include "../native/timer.c"
#include "../native/timer_lifetime.c"

static void same_state(const TimerState *a,const TimerState *b,int installed) {
    CHECK(a->count==b->count && a->quantum==b->quantum && a->earliest==b->earliest);
    CHECK(a->programmed_divisor==b->programmed_divisor);
    if (installed) CHECK(a->installed==b->installed);
    for (unsigned i=0;i<16;i++) {
        CHECK(a->by_handle[i]==b->by_handle[i]);
        CHECK(a->slots[i].interval==b->slots[i].interval);
        CHECK(a->slots[i].remaining==b->slots[i].remaining);
        CHECK(a->slots[i].due==b->slots[i].due);
        CHECK(a->slots[i].handle==b->slots[i].handle);
        CHECK(a->slots[i].target.first==b->slots[i].target.first);
        CHECK(a->slots[i].target.second==b->slots[i].target.second);
    }
}
int main(void) {
    TimerState state=nondet_state(),before=state;
    TimerLifetime life={nondet_binding()},old=life;
    TimerLifetimeRequest request;
    TimerExternalBinding reply=nondet_binding();
#if PROFILE==0
    timer_lifetime_install(&state,&request);
    CHECK(request.kind==(before.installed ? TIMER_LIFETIME_NONE : TIMER_LIFETIME_READ_BINDING));
    CHECK(state.installed==(before.installed ? before.installed : 1));
    same_state(&state,&before,0);
    CHECK(life.saved.role==old.saved.role && life.saved.identity==old.saved.identity);
    if (!before.installed) {
        CHECK(timer_lifetime_consume(&state,&life,&request,TIMER_LIFETIME_READ_BINDING,reply));
        CHECK(request.kind==TIMER_LIFETIME_BIND_TIMER);
        CHECK(life.saved.role==reply.role && life.saved.identity==reply.identity);
        TimerState at_bind=state;
        CHECK(timer_lifetime_consume(&state,&life,&request,TIMER_LIFETIME_BIND_TIMER,reply));
        CHECK(request.kind==TIMER_LIFETIME_NONE);same_state(&state,&at_bind,1);
    }
#elif PROFILE==1
    timer_lifetime_restore(&state,&life,&request);
    CHECK(request.kind==(before.installed ? TIMER_LIFETIME_BIND_SAVED : TIMER_LIFETIME_NONE));
    CHECK(!state.installed);same_state(&state,&before,0);
    if (before.installed) {
        CHECK(request.binding.role==old.saved.role && request.binding.identity==old.saved.identity);
        CHECK(timer_lifetime_consume(&state,&life,&request,TIMER_LIFETIME_BIND_SAVED,reply));
        CHECK(request.kind==TIMER_LIFETIME_RESET_PIT);
        CHECK(request.pit_command==0x36 && !request.pit_low && !request.pit_high);
        CHECK(timer_lifetime_consume(&state,&life,&request,TIMER_LIFETIME_RESET_PIT,reply));
        CHECK(request.kind==TIMER_LIFETIME_NONE);same_state(&state,&before,0);
    }
    CHECK(life.saved.role==old.saved.role && life.saved.identity==old.saved.identity);
#elif PROFILE==2
    timer_lifetime_chain(&life,&request);
    CHECK(request.kind==TIMER_LIFETIME_DELIVER && request.enable_interrupts==1);
    CHECK(request.binding.role==old.saved.role && request.binding.identity==old.saved.identity);
    CHECK(timer_lifetime_consume(0,&life,&request,TIMER_LIFETIME_DELIVER,reply));
    CHECK(request.kind==TIMER_LIFETIME_NONE);same_state(&state,&before,1);
    CHECK(life.saved.role==old.saved.role && life.saved.identity==old.saved.identity);
#else
    unsigned kind=nondet_unsigned(),wrong=nondet_unsigned();
    __CPROVER_assume(kind<=TIMER_LIFETIME_DELIVER && wrong<=TIMER_LIFETIME_DELIVER);
    __CPROVER_assume(kind!=wrong || wrong==TIMER_LIFETIME_NONE);
    request=(TimerLifetimeRequest){0};request.kind=(TimerLifetimeKind)kind;
    CHECK(!timer_lifetime_consume(&state,&life,&request,(TimerLifetimeKind)wrong,reply));
    CHECK(request.kind==(TimerLifetimeKind)kind);same_state(&state,&before,1);
    CHECK(life.saved.role==old.saved.role && life.saved.identity==old.saved.identity);
#endif
}
