#include "timer.h"

TimerTarget timer_target(TimerCallback callback) {
    TimerTarget target={TIMER_ZERO,TIMER_ZERO};
    switch(callback) {
    case TIMER_BIOS_CHAIN: target.first=TIMER_ENTRY_CHAIN; target.second=TIMER_GROUP_TIMER; break;
    case TIMER_MUSIC_FADE: target.first=TIMER_ENTRY_FADE; target.second=TIMER_GROUP_SOUND; break;
    case TIMER_ADLX_PLAYBACK: target.first=TIMER_ENTRY_PLAYBACK; target.second=TIMER_GROUP_SOUND; break;
    case TIMER_FIXTURE_CLEAR: target.first=TIMER_ENTRY_CLEAR; target.second=TIMER_GROUP_SOUND; break;
    case TIMER_FIXTURE_IRQ: target.first=TIMER_ENTRY_IRQ; target.second=TIMER_GROUP_TIMER; break;
    default: break;
    }
    return target;
}
TimerCallback timer_callback(TimerTarget target) {
    for(unsigned k=TIMER_BIOS_CHAIN;k<=TIMER_FIXTURE_IRQ;k++) {
        TimerTarget candidate=timer_target((TimerCallback)k);
        if(target.first==candidate.first && target.second==candidate.second) return (TimerCallback)k;
    }
    return TIMER_OPEN;
}
int timer_handle_slot(const TimerState *state, uint16_t handle) {
    if(handle>=32 || (handle&1)) return -1;
    unsigned value=state->by_handle[handle/2];
    if((value&1) || value>=state->count*2) return -1;
    return (int)(value/2);
}
static void timer_minimum(TimerState *state, uint32_t candidate) {
    for(unsigned i=state->count;i;i--)
        if(state->slots[i-1].interval<=candidate) candidate=state->slots[i-1].interval;
    state->earliest=candidate;
}
int timer_register(TimerState *state, TimerCallback callback, uint32_t interval) {
    if(state->count==0 || state->count>=TIMER_CAPACITY || callback==TIMER_OPEN) return -1;
    unsigned index=state->count;
    int handle=(int)index;
    while(handle>=0 && !(state->by_handle[handle]&TIMER_FREE)) handle--;
    if(handle<0) return -1;
    TimerSlot *slot=&state->slots[index];
    slot->interval=interval; slot->remaining=interval;
    slot->target=timer_target(callback);
    /* Due is intentionally stale across reuse. */
    if(interval<state->earliest) state->earliest=interval;
    slot->handle=(uint16_t)(handle*2);
    state->by_handle[handle]=(uint16_t)(index*2);
    state->count++;
    return handle*2;
}
static uint16_t timer_fragment(const TimerState *state, unsigned word) {
    return word&1 ? state->slots[word/2].target.second : state->slots[word/2].target.first;
}
static void timer_put_fragment(TimerState *state, unsigned word, uint16_t value) {
    if(word&1) state->slots[word/2].target.second=value;
    else state->slots[word/2].target.first=value;
}
void timer_remove_wrong_stride(TimerState *state, unsigned tail, unsigned destination) {
    /* Retained defect: word positions use slot index, not twice slot index.
     * Separate reads preserve overlapping-copy order (second read sees first write). */
    timer_put_fragment(state,destination,timer_fragment(state,tail));
    timer_put_fragment(state,destination+1,timer_fragment(state,tail+1));
}
uint16_t timer_remove(TimerState *state, uint16_t handle) {
    unsigned destination=(unsigned)timer_handle_slot(state,handle);
    unsigned tail=state->count-1;
    uint16_t result=handle;
    state->count--;
    if(tail!=destination) {
        state->slots[destination].interval=state->slots[tail].interval;
        state->slots[destination].remaining=state->slots[tail].remaining;
        timer_remove_wrong_stride(state,tail,destination);
        state->slots[destination].due=state->slots[tail].due;
        result=state->slots[tail].handle;
        /* Retained second defect: destination handle is NOT repaired; handle
         * zero receives the tail HANDLE rather than the destination slot. */
        state->by_handle[0]=result;
    }
    state->by_handle[handle/2]=TIMER_FREE;
    timer_minimum(state,65536u);
    return result;
}
void timer_set_interval(TimerState *state, uint16_t handle, uint32_t interval) {
    state->slots[timer_handle_slot(state,handle)].interval=interval;
    /* Countdown and due do not change. Setter starts with supplied interval. */
    timer_minimum(state,interval);
}
TimerTickScratch timer_account_tick(TimerState *state) {
    TimerTickScratch scratch={0,0};
    for(unsigned i=state->count;i;i--) {
        TimerSlot *slot=&state->slots[i-1];
        scratch.low=(uint16_t)state->quantum; scratch.high=(uint16_t)(state->quantum>>16);
        slot->remaining-=state->quantum;
        /* Original tests sign of high word, NOT unsigned borrow; reload once,
         * even for zero intervals, huge quanta and intervals below overshoot. */
        if((slot->remaining&2147483648u) || slot->remaining==0) {
            slot->due=TIMER_FREE;
            scratch.low=(uint16_t)slot->interval; scratch.high=(uint16_t)(slot->interval>>16);
            slot->remaining+=slot->interval;
        }
    }
    state->quantum=state->earliest;
    scratch.low=(uint16_t)(state->earliest>>16);
    return scratch;
}
int timer_take_due(TimerState *state, unsigned index, TimerCallback *callback) {
    /* index may now exceed count after callback removal; the ISR still visits
     * its original descending cursor and stale storage. */
    if(!(state->slots[index].due&TIMER_FREE)) return 0;
    state->slots[index].due=0;
    *callback=timer_callback(state->slots[index].target);
    return 1;
}
