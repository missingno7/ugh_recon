/* L1 projection and platform shell. Out-of-contract machine states explicitly
 * execute the independent L1 routines; they are never silently normalized. */
#include "platform.h"
#include "../timer.h"
int l1_RegisterTimerCallback(Regs *r);
int l1_RemoveTimerCallback(Regs *r);
int l1_SetTimerCallbackInterval(Regs *r);
int l1_HandleTimerInterrupt(Regs *r);

static uint16_t timer_word_token(uint16_t word, unsigned position) {
    if(word==0) return TIMER_ZERO;
    if(word==T(ChainSavedTimerInterrupt)) return TIMER_ENTRY_CHAIN;
    if(word==S(AdvanceMusicFade)) return TIMER_ENTRY_FADE;
    if(word==S(TickAdlxPlayback)) return TIMER_ENTRY_PLAYBACK;
    if(word==S(ClearSoundState)) return TIMER_ENTRY_CLEAR;
    if(word==T(HandleTimerInterrupt)) return TIMER_ENTRY_IRQ;
    if(word==TIMER_SEG) return TIMER_GROUP_TIMER;
    if(word==SOUND_SEG) return TIMER_GROUP_SOUND;
    return (uint16_t)(32+position);
}
static uint16_t timer_token_word(uint16_t token, const uint16_t *open) {
    switch(token) {
    case TIMER_ZERO:return 0;
    case TIMER_ENTRY_CHAIN:return T(ChainSavedTimerInterrupt);
    case TIMER_ENTRY_FADE:return S(AdvanceMusicFade);
    case TIMER_ENTRY_PLAYBACK:return S(TickAdlxPlayback);
    case TIMER_ENTRY_CLEAR:return S(ClearSoundState);
    case TIMER_ENTRY_IRQ:return T(HandleTimerInterrupt);
    case TIMER_GROUP_TIMER:return TIMER_SEG;
    case TIMER_GROUP_SOUND:return SOUND_SEG;
    default:return open[token-32];
    }
}
static int timer_project(TimerState *state, uint16_t *open) {
    uint16_t last=rd16(DATA_SEG,D(LastActiveTimerSlotOffset));
    if((last&1) || last>30) return 0;
    state->count=last/2+1;
    state->quantum=rd32(DATA_SEG,D(NextPitQuantumLow));
    state->earliest=rd32(DATA_SEG,D(EarliestTimerIntervalLow));
    state->installed=rd16(TIMER_SEG,T(TimerInterruptInstalled));
    state->programmed_divisor=rd16(DATA_SEG,D(ProgrammedPitDivisor));
    for(unsigned i=0;i<16;i++) {
        TimerSlot *slot=&state->slots[i];
        slot->interval=rd16(DATA_SEG,(uint16_t)(D(TimerIntervalLowBySlot)+i*2)) |
                       (uint32_t)rd16(DATA_SEG,(uint16_t)(D(TimerIntervalHighBySlot)+i*2))*65536u;
        slot->remaining=rd16(DATA_SEG,(uint16_t)(D(TimerRemainingLowBySlot)+i*2)) |
                       (uint32_t)rd16(DATA_SEG,(uint16_t)(D(TimerRemainingHighBySlot)+i*2))*65536u;
        slot->due=rd16(DATA_SEG,(uint16_t)(D(TimerCallbackDueBySlot)+i*2));
        slot->handle=rd16(DATA_SEG,(uint16_t)(D(TimerHandleBySlot)+i*2));
        state->by_handle[i]=rd16(DATA_SEG,(uint16_t)(D(TimerSlotOffsetByHandle)+i*2));
        open[i*2]=rd16(DATA_SEG,(uint16_t)(D(TimerCallbackOffsetBySlot)+i*4));
        open[i*2+1]=rd16(DATA_SEG,(uint16_t)(D(TimerCallbackSegmentBySlot)+i*4));
        slot->target.first=timer_word_token(open[i*2],i*2);
        slot->target.second=timer_word_token(open[i*2+1],i*2+1);
    }
    return 1;
}
static void timer_publish(const TimerState *state, const uint16_t *open) {
    wr16(DATA_SEG,D(LastActiveTimerSlotOffset),(uint16_t)((state->count-1)*2));
    wr32(DATA_SEG,D(NextPitQuantumLow),state->quantum);
    wr32(DATA_SEG,D(EarliestTimerIntervalLow),state->earliest);
    wr16(DATA_SEG,D(ProgrammedPitDivisor),state->programmed_divisor);
    for(unsigned i=0;i<16;i++) {
        const TimerSlot *slot=&state->slots[i];
        wr16(DATA_SEG,(uint16_t)(D(TimerIntervalLowBySlot)+i*2),(uint16_t)slot->interval);
        wr16(DATA_SEG,(uint16_t)(D(TimerIntervalHighBySlot)+i*2),(uint16_t)(slot->interval>>16));
        wr16(DATA_SEG,(uint16_t)(D(TimerRemainingLowBySlot)+i*2),(uint16_t)slot->remaining);
        wr16(DATA_SEG,(uint16_t)(D(TimerRemainingHighBySlot)+i*2),(uint16_t)(slot->remaining>>16));
        wr16(DATA_SEG,(uint16_t)(D(TimerCallbackDueBySlot)+i*2),slot->due);
        wr16(DATA_SEG,(uint16_t)(D(TimerHandleBySlot)+i*2),slot->handle);
        wr16(DATA_SEG,(uint16_t)(D(TimerSlotOffsetByHandle)+i*2),state->by_handle[i]);
        wr16(DATA_SEG,(uint16_t)(D(TimerCallbackOffsetBySlot)+i*4),timer_token_word(slot->target.first,open));
        wr16(DATA_SEG,(uint16_t)(D(TimerCallbackSegmentBySlot)+i*4),timer_token_word(slot->target.second,open));
    }
}
EXPORT int c_RegisterTimerCallback(Regs *r) {
    TimerState state; uint16_t open[32];
    TimerTarget target={timer_word_token(r->ax,0),timer_word_token(r->dx,1)};
    TimerCallback callback=timer_callback(target);
    if(!timer_project(&state,open) || callback==TIMER_OPEN || state.count==16)
        return l1_RegisterTimerCallback(r);
    int handle=timer_register(&state,callback,r->bx | (uint32_t)r->cx*65536u);
    if(handle<0) return l1_RegisterTimerCallback(r);
    timer_publish(&state,open); r->ax=(uint16_t)handle; return UGH_OK;
}
EXPORT int c_RemoveTimerCallback(Regs *r) {
    TimerState state; uint16_t open[32];
    if(!timer_project(&state,open) || state.count<2 || timer_handle_slot(&state,r->ax)<0)
        return l1_RemoveTimerCallback(r);
    r->ax=timer_remove(&state,r->ax);
    r->bx=(uint16_t)state.earliest; r->cx=(uint16_t)(state.earliest>>16);
    r->ds=DATA_SEG; timer_publish(&state,open); return UGH_OK;
}
EXPORT int c_SetTimerCallbackInterval(Regs *r) {
    TimerState state; uint16_t open[32];
    if(!timer_project(&state,open) || timer_handle_slot(&state,r->ax)<0)
        return l1_SetTimerCallbackInterval(r);
    timer_set_interval(&state,r->ax,r->bx | (uint32_t)r->cx*65536u);
    r->bx=(uint16_t)state.earliest; r->cx=(uint16_t)(state.earliest>>16);
    timer_publish(&state,open); return UGH_OK;
}

EXPORT int c_HandleTimerInterrupt(Regs *r) {
    Regs saved=*r;
    uint16_t pushed[]={r->ax,r->bx,r->cx,r->dx,r->si,r->di,r->ds,r->es,r->bp};
    for(unsigned i=0;i<9;i++) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,pushed[i]); }
    r->ds=DATA_SEG;
    r->ax=DATA_SEG;
    TimerState state; uint16_t open[32];
    /* Validate before any native step. A malformed last offset keeps the L1 path. */
    if(!timer_project(&state,open)) { *r=saved; return l1_HandleTimerInterrupt(r); }
    TimerTickScratch scratch=timer_account_tick(&state);
    timer_publish(&state,open);
    r->ax=scratch.low; r->dx=scratch.high;
    uint16_t slot;
    unsigned budget;
    slot=rd16(DATA_SEG,D(LastActiveTimerSlotOffset));
    budget=32768;
    do {
        if(!budget--) { *r=saved; return UGH_BUDGET; }
        /* Reproject after every callback: nested API writes and removal are live.
         * Keep the cursor independent of the possibly reduced active count. */
        if(!timer_project(&state,open)) { *r=saved; return UGH_UNSUPPORTED; }
        TimerCallback callback;
        if(timer_take_due(&state,slot/2,&callback)) {
            (void)callback; /* OPEN targets stay explicit at the machine boundary. */
            timer_publish(&state,open);
            uint16_t off=rd16(DATA_SEG,(uint16_t)(D(TimerCallbackOffsetBySlot)+slot*2));
            uint16_t seg=rd16(DATA_SEG,(uint16_t)(D(TimerCallbackSegmentBySlot)+slot*2));
            /* DS and SI alone are saved at this call site. Callback clobbers flow
             * to the next callback until the ISR restores the interrupted registers. */
            r->sp=(uint16_t)(r->sp-8);
            wr16(r->ss,r->sp,(uint16_t)(T(HandleTimerInterrupt)+0x77));
            wr16(r->ss,(uint16_t)(r->sp+2),r->cs);
            wr16(r->ss,(uint16_t)(r->sp+4),slot); wr16(r->ss,(uint16_t)(r->sp+6),r->ds);
            r->si=(uint16_t)(slot*2);
            flag(r,CF,slot&0x8000); szp(r,r->si,16);
            flag(r,OF,!!(slot&0x8000)^!!(r->si&0x8000));
            int status=ugh_dispatch(seg,off,r);
            r->sp=(uint16_t)(r->sp+8); r->si=slot;
            r->ds=DATA_SEG;
            if(status) { *r=saved; return status; }
        }
        slot=(uint16_t)(slot-2);
    } while((int16_t)slot>=0);
    platform_out(0x20,1,0x20);
    uint16_t divisor=rd16(DATA_SEG,D(EarliestTimerIntervalLow));
    if(rd16(DATA_SEG,D(ProgrammedPitDivisor))!=divisor) {
        platform_out(0x43,1,0x36);
        platform_out(0x40,1,divisor&255u); platform_out(0x40,1,divisor>>8);
    }
    wr16(DATA_SEG,D(ProgrammedPitDivisor),rd16(DATA_SEG,D(EarliestTimerIntervalLow)));
    *r=saved; return UGH_OK; /* IRET restores FLAGS as well as general registers. */
}
