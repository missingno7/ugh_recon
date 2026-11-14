#include "platform.h"
#include "../timer_lifetime.h"

/* Projection is checked against the accepted timer bridge by the evidence driver.
 * Count is intentionally unvalidated here: installation overwrites an arbitrary
 * incoming count, while typed API requests validate their own admitted domain. */
static uint16_t lifetime_word_token(uint16_t word, unsigned position) {
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

static uint16_t lifetime_token_word(uint16_t token, const uint16_t *open) {
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

static int lifetime_project(TimerState *state, uint16_t *open) {
    uint16_t last=rd16(DATA_SEG,D(LastActiveTimerSlotOffset));
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
        slot->target.first=lifetime_word_token(open[i*2],i*2);
        slot->target.second=lifetime_word_token(open[i*2+1],i*2+1);
    }
    return 1;
}

static void lifetime_publish(const TimerState *state, const uint16_t *open) {
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
        wr16(DATA_SEG,(uint16_t)(D(TimerCallbackOffsetBySlot)+i*4),lifetime_token_word(slot->target.first,open));
        wr16(DATA_SEG,(uint16_t)(D(TimerCallbackSegmentBySlot)+i*4),lifetime_token_word(slot->target.second,open));
    }
}

static TimerExternalBinding lifetime_binding(uint16_t segment, uint16_t offset, unsigned identity) {
    TimerExternalBinding binding={TIMER_EXTERNAL_OTHER,identity};
    if (segment==0xf000 && offset==0x100) binding.role=TIMER_EXTERNAL_BIOS;
    return binding;
}

EXPORT int c_InstallTimerInterrupt(Regs *r) {
    TimerState state; uint16_t open[32]; lifetime_project(&state,open);
    state.installed=rd16(r->cs,T(TimerInterruptInstalled));
    logic(r,state.installed,16);
    TimerLifetime life={lifetime_binding(rd16(DATA_SEG,D(PreviousInt08Segment)),
                                        rd16(DATA_SEG,D(PreviousInt08Offset)),1)};
    TimerLifetimeRequest request;
    timer_lifetime_install(&state,&request);
    if (request.kind==TIMER_LIFETIME_NONE) return UGH_OK;
    if (request.kind!=TIMER_LIFETIME_READ_BINDING) return UGH_UNSUPPORTED;
    wr16(r->cs,T(TimerInterruptInstalled),state.installed);
    uint16_t saved_ds=r->ds;
    r->ds=DATA_SEG; r->ax=0x3508;
    int status=platform_interrupt(0x21,r); if (status) return status;
    uint16_t offset=r->bx,segment=r->es;
    /* The service boundary may update retained/inactive storage. Borrow the
     * owner at the continuation cut so baseline publication cannot undo it. */
    lifetime_project(&state,open); state.installed=rd16(r->cs,T(TimerInterruptInstalled));
    TimerExternalBinding reply=lifetime_binding(segment,offset,2);
    if (!timer_lifetime_consume(&state,&life,&request,TIMER_LIFETIME_READ_BINDING,reply) ||
        life.saved.identity!=2 || request.kind!=TIMER_LIFETIME_BIND_TIMER) return UGH_UNSUPPORTED;
    wr16(DATA_SEG,D(PreviousInt08Offset),offset); wr16(DATA_SEG,D(PreviousInt08Segment),segment);
    lifetime_publish(&state,open);
    /* Compatibility working-register cut: the final map-loop SUB is 0-2.
     * The native baseline keeps all stale fields; no device service intervenes. */
    r->si=sub16(r,0,2,0);
    r->ds=TIMER_SEG; r->dx=T(HandleTimerInterrupt); r->ax=0x2508;
    status=platform_interrupt(0x21,r); r->ds=saved_ds;
    if (status) return status;
    lifetime_project(&state,open); state.installed=rd16(r->cs,T(TimerInterruptInstalled));
    if (!timer_lifetime_consume(&state,&life,&request,TIMER_LIFETIME_BIND_TIMER,reply) ||
        request.kind!=TIMER_LIFETIME_NONE) return UGH_UNSUPPORTED;
    return UGH_OK;
}

EXPORT int c_RestoreTimerInterrupt(Regs *r) {
    TimerState state; uint16_t open[32]; lifetime_project(&state,open);
    state.installed=rd16(r->cs,T(TimerInterruptInstalled)); logic(r,state.installed,16);
    uint16_t offset=rd16(DATA_SEG,D(PreviousInt08Offset)),segment=rd16(DATA_SEG,D(PreviousInt08Segment));
    TimerLifetime life={lifetime_binding(segment,offset,1)};
    TimerLifetimeRequest request; timer_lifetime_restore(&state,&life,&request);
    if (request.kind==TIMER_LIFETIME_NONE) return UGH_OK;
    if (request.kind!=TIMER_LIFETIME_BIND_SAVED || request.binding.identity!=1) return UGH_UNSUPPORTED;
    wr16(r->cs,T(TimerInterruptInstalled),state.installed);
    uint16_t saved_ds=r->ds;
    r->dx=offset; r->ds=segment; r->ax=0x2508;
    int status=platform_interrupt(0x21,r); if (status) return status;
    lifetime_project(&state,open); state.installed=rd16(r->cs,T(TimerInterruptInstalled));
    if (!timer_lifetime_consume(&state,&life,&request,TIMER_LIFETIME_BIND_SAVED,life.saved) ||
        request.kind!=TIMER_LIFETIME_RESET_PIT) return UGH_UNSUPPORTED;
    set_al(r,request.pit_command); platform_out(0x43,1,(uint8_t)r->ax);
    set_al(r,(uint8_t)logic(r,request.pit_low,8)); platform_out(0x40,1,request.pit_low);
    platform_out(0x40,1,request.pit_high);
    r->ds=saved_ds;
    lifetime_project(&state,open); state.installed=rd16(r->cs,T(TimerInterruptInstalled));
    if (!timer_lifetime_consume(&state,&life,&request,TIMER_LIFETIME_RESET_PIT,life.saved) ||
        request.kind!=TIMER_LIFETIME_NONE) return UGH_UNSUPPORTED;
    return UGH_OK;
}

EXPORT int c_ChainSavedTimerInterrupt(Regs *r) {
    uint16_t segment=rd16(r->ds,D(PreviousInt08Segment)),offset=rd16(r->ds,D(PreviousInt08Offset));
    TimerLifetime life={lifetime_binding(segment,offset,1)};
    TimerLifetimeRequest request; timer_lifetime_chain(&life,&request);
    if (request.kind!=TIMER_LIFETIME_DELIVER || request.binding.identity!=1) return UGH_UNSUPPORTED;
    if (request.enable_interrupts) flag(r,IF,1);
    /* Compatibility-only frame. Native code requests a typed external delivery;
     * BIOS delivery below calls the platform role directly, without far dispatch. */
    r->sp=(uint16_t)(r->sp-6);
    wr16(r->ss,r->sp,(uint16_t)(T(ChainSavedTimerInterrupt)+6));
    wr16(r->ss,(uint16_t)(r->sp+2),r->cs); wr16(r->ss,(uint16_t)(r->sp+4),r->flags);
    int status;
    if (request.binding.role==TIMER_EXTERNAL_BIOS) {
        platform_bios_timer();
        r->ip=rd16(r->ss,r->sp); r->cs=rd16(r->ss,(uint16_t)(r->sp+2));
        r->flags=rd16(r->ss,(uint16_t)(r->sp+4)); r->sp=(uint16_t)(r->sp+6);
        status=UGH_OK;
    } else {
        /* Open bindings retain the accepted test backend's IRET roles and
         * explicit BAD_CALLBACK result. There is no implicit BIOS replacement. */
        status=ugh_dispatch_interrupt(segment,offset,r);
    }
    if (status) return status;
    if (!timer_lifetime_consume(0,&life,&request,TIMER_LIFETIME_DELIVER,life.saved) ||
        request.kind!=TIMER_LIFETIME_NONE) return UGH_UNSUPPORTED;
    return UGH_OK;
}

static int lifetime_stack(Regs *r, unsigned kind, uint16_t return_offset) {
    uint16_t saved_bp=r->bp,saved_sp=r->sp;
    TimerApiRequest request={0};
    r->ax=arg16(r,0);
    if (kind==0) {
        r->dx=arg16(r,2); r->bx=arg16(r,4); r->cx=arg16(r,6);
        TimerTarget target={lifetime_word_token(r->ax,0),lifetime_word_token(r->dx,1)};
        request.kind=TIMER_API_REGISTER; request.callback=timer_callback(target);
        request.interval=r->bx | (uint32_t)r->cx*65536u;
    } else {
        if (kind==2) { r->bx=arg16(r,2); r->cx=arg16(r,4); }
        request.kind=TIMER_API_REMOVE; request.handle=r->ax;
    }
    r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,saved_bp); r->bp=r->sp;
    r->sp=(uint16_t)(r->sp-4);
    wr16(r->ss,r->sp,return_offset); wr16(r->ss,(uint16_t)(r->sp+2),r->cs);
    TimerState state; uint16_t open[32]; lifetime_project(&state,open);
    uint16_t last=rd16(DATA_SEG,D(LastActiveTimerSlotOffset));
    TimerApiResult result;
    int admitted=!(last&1) && last<=30 && timer_lifetime_apply(&state,&request,&result);
    if (admitted) {
        lifetime_publish(&state,open); r->ax=result.handle;
        if (request.kind==TIMER_API_REMOVE) {
            r->ds=DATA_SEG; r->bx=(uint16_t)result.minimum; r->cx=(uint16_t)(result.minimum>>16);
        }
    }
    r->bp=saved_bp; r->sp=saved_sp;
    return admitted ? UGH_OK : UGH_UNSUPPORTED;
}
EXPORT int c_RegisterTimerCallbackFromStack(Regs *r) {
    return lifetime_stack(r,0,(uint16_t)(T(RegisterTimerCallbackFromStack)+0x13));
}
EXPORT int c_RemoveTimerCallbackFromStack(Regs *r) {
    return lifetime_stack(r,1,(uint16_t)(T(RemoveTimerCallbackFromStack)+0xa));
}
EXPORT int c_loc_032F(Regs *r) {
    return lifetime_stack(r,2,(uint16_t)(T(loc_032F)+0x10));
}

