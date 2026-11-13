#include "ugh.h"
#include "platform.h"

/* Publish these in a shared timer interface for later packages. */

/* Inline implementation of the two separate minimum-scan loops (0291/02DD).
 * BX:CX is the current low:high candidate. CMP is unsigned; only SUB SI,2/JNS
 * uses signedness. Even a negative initial slot is visited once, and 8000h
 * wraps to 7FFEh before the next signed termination test. */
static void scan_timer_minimum(Regs *r, uint16_t slot) {
    do {
        uint16_t high=rd16(r->ds,(uint16_t)(D(TimerIntervalHighBySlot)+slot));
        if(r->cx>high ||
           (r->cx==high &&
            r->bx>=rd16(r->ds,(uint16_t)(D(TimerIntervalLowBySlot)+slot)))) {
            r->bx=rd16(r->ds,(uint16_t)(D(TimerIntervalLowBySlot)+slot));
            r->cx=rd16(r->ds,(uint16_t)(D(TimerIntervalHighBySlot)+slot));
        }
        slot=(uint16_t)(slot-2);
    } while((int16_t)slot>=0);
    wr16(r->ds,D(EarliestTimerIntervalLow),r->bx);
    wr16(r->ds,D(EarliestTimerIntervalHigh),r->cx);
}

/* Far register ABI, no stack arguments: AX is a byte-offset handle.
 * DS becomes DGROUP and is NOT restored (021E..0221, unlike the setter).
 * AX survives tail removal; otherwise it ends as the old tail's handle.
 * BX:CX returns the unsigned minimum, capped initially at 0001:0000.
 * DX, SI, DI, BP, ES, CS, SS, SP and all FLAGS survive; PUSHF/CLI/POPF means
 * no asynchronous delivery inside this deterministic adapter.
 * Writes LastActiveTimerSlotOffset, the free-handle word, earliest interval,
 * and, on the moved path, the seven literal destination words below. The old
 * tail and countdown/due fields not explicitly written remain stale.
 * No direct/indirect calls, ports, DOS requests or external dependencies. */
/* TRANSLATES TIMER:RemoveTimerCallback */
EXPORT int c_RemoveTimerCallback(Regs *r) {
    uint16_t handle=r->ax;
    uint16_t tail;
    r->ds=DATA_SEG;
    tail=rd16(r->ds,D(LastActiveTimerSlotOffset));
    wr16(r->ds,D(LastActiveTimerSlotOffset),(uint16_t)(tail-2));
    if(tail!=rd16(r->ds,(uint16_t)(D(TimerSlotOffsetByHandle)+handle))) {
        r->bx=rd16(r->ds,(uint16_t)(D(TimerSlotOffsetByHandle)+handle));
        r->ax=rd16(r->ds,(uint16_t)(D(TimerIntervalLowBySlot)+tail));
        wr16(r->ds,(uint16_t)(D(TimerIntervalLowBySlot)+r->bx),r->ax);
        r->ax=rd16(r->ds,(uint16_t)(D(TimerIntervalHighBySlot)+tail));
        wr16(r->ds,(uint16_t)(D(TimerIntervalHighBySlot)+r->bx),r->ax);
        r->ax=rd16(r->ds,(uint16_t)(D(TimerRemainingLowBySlot)+tail));
        wr16(r->ds,(uint16_t)(D(TimerRemainingLowBySlot)+r->bx),r->ax);
        r->ax=rd16(r->ds,(uint16_t)(D(TimerRemainingHighBySlot)+tail));
        wr16(r->ds,(uint16_t)(D(TimerRemainingHighBySlot)+r->bx),r->ax);
        /* 025C..0268 add the UNDOUBLED slot to the interleaved far-pointer
         * table. A slot of 2 therefore copies a segment and the next offset,
         * not the callback pair at index 1. Keep this bug and write order. */
        r->ax=rd16(r->ds,(uint16_t)(D(TimerCallbackOffsetBySlot)+tail));
        wr16(r->ds,(uint16_t)(D(TimerCallbackOffsetBySlot)+r->bx),r->ax);
        r->ax=rd16(r->ds,(uint16_t)(D(TimerCallbackSegmentBySlot)+tail));
        wr16(r->ds,(uint16_t)(D(TimerCallbackSegmentBySlot)+r->bx),r->ax);
        r->ax=rd16(r->ds,(uint16_t)(D(TimerCallbackDueBySlot)+tail));
        wr16(r->ds,(uint16_t)(D(TimerCallbackDueBySlot)+r->bx),r->ax);
        /* 0274..027E self-store the old tail handle, then overwrite handle
         * ZERO's mapping with that handle. Neither intended repair occurs. */
        r->ax=rd16(r->ds,(uint16_t)(D(TimerHandleBySlot)+tail));
        wr16(r->ds,(uint16_t)(D(TimerHandleBySlot)+tail),r->ax);
        wr16(r->ds,D(TimerSlotOffsetByHandle),r->ax);
    }
    wr16(r->ds,(uint16_t)(D(TimerSlotOffsetByHandle)+handle),0x8000);
    r->cx=1;
    r->bx=0;
    scan_timer_minimum(r,rd16(r->ds,D(LastActiveTimerSlotOffset)));
    return UGH_OK;
}

/* Far register ABI, no stack arguments: AX is a byte-offset handle and CX:BX
 * is the new unsigned interval high:low. Resolve the handle without validation;
 * only period words change, not remaining clocks or due flags (02D1..02D5).
 * Scan starts with the supplied interval, not the remover's 65536-clock cap.
 * BX:CX returns the unsigned minimum. AX, DX, SI, DI, BP, DS, ES, CS, SS, SP
 * and all FLAGS survive. Writes period and earliest words; no device effects
 * or call edges. Memory lvalues always use original DGROUP, never native state. */
/* TRANSLATES TIMER:SetTimerCallbackInterval */
EXPORT int c_SetTimerCallbackInterval(Regs *r) {
    uint16_t saved_ds=r->ds;
    uint16_t slot;
    r->ds=DATA_SEG;
    slot=rd16(r->ds,(uint16_t)(D(TimerSlotOffsetByHandle)+r->ax));
    wr16(r->ds,(uint16_t)(D(TimerIntervalLowBySlot)+slot),r->bx);
    wr16(r->ds,(uint16_t)(D(TimerIntervalHighBySlot)+slot),r->cx);
    scan_timer_minimum(r,rd16(r->ds,D(LastActiveTimerSlotOffset)));
    r->ds=saved_ds;
    return UGH_OK;
}
/* Far register ABI, no arguments. Installation initializes only slot zero and
 * the handle maps; countdown/due/callback residue in other slots survives. */
/* TRANSLATES TIMER:InstallTimerInterrupt */
EXPORT int c_InstallTimerInterrupt(Regs *r) {
    uint16_t installed=rd16(r->cs,T(TimerInterruptInstalled));
    logic(r,installed,16); if(installed) return UGH_OK;
    wr16(r->cs,T(TimerInterruptInstalled),1);
    uint16_t ds=r->ds; r->ds=DATA_SEG; r->ax=0x3508;
    int status=platform_interrupt(0x21,r); if(status) return status;
    wr16(r->ds,D(PreviousInt08Offset),r->bx); wr16(r->ds,D(PreviousInt08Segment),r->es);
    r->ax=T(ChainSavedTimerInterrupt); wr16(r->ds,D(TimerCallbackOffsetBySlot),r->ax);
    r->ax=TIMER_SEG; wr16(r->ds,D(TimerCallbackSegmentBySlot),r->ax);
    wr16(r->ds,D(NextPitQuantumLow),0); wr16(r->ds,D(NextPitQuantumHigh),1);
    wr16(r->ds,D(EarliestTimerIntervalLow),0); wr16(r->ds,D(EarliestTimerIntervalHigh),1);
    wr16(r->ds,D(TimerIntervalLowBySlot),0); wr16(r->ds,D(TimerIntervalHighBySlot),1);
    wr16(r->ds,D(TimerRemainingLowBySlot),0); wr16(r->ds,D(TimerRemainingHighBySlot),1);
    r->si=30;
    do { wr16(r->ds,(uint16_t)(D(TimerSlotOffsetByHandle)+r->si),0x8000); r->si=sub16(r,r->si,2,0); } while((int16_t)r->si>=0);
    wr16(r->ds,D(TimerSlotOffsetByHandle),0); wr16(r->ds,D(TimerHandleBySlot),0); wr16(r->ds,D(LastActiveTimerSlotOffset),0);
    r->ax=TIMER_SEG; r->ds=r->ax; r->dx=T(HandleTimerInterrupt); r->ax=0x2508;
    status=platform_interrupt(0x21,r); r->ds=ds; return status;
}
/* Far register ABI. Active path restores DS and leaves AL=0, DX=old offset;
 * inactive path performs just TEST. IF/DF survive; PIT zero means 65536. */
/* TRANSLATES TIMER:RestoreTimerInterrupt */
EXPORT int c_RestoreTimerInterrupt(Regs *r) {
    uint16_t installed=rd16(r->cs,T(TimerInterruptInstalled));
    logic(r,installed,16); if(!installed) return UGH_OK;
    wr16(r->cs,T(TimerInterruptInstalled),0); uint16_t ds=r->ds;
    r->ax=DATA_SEG; r->ds=r->ax; r->dx=rd16(r->ds,D(PreviousInt08Offset));
    r->ds=rd16(r->ds,D(PreviousInt08Segment)); r->ax=0x2508;
    int status=platform_interrupt(0x21,r); if(status) return status;
    set_al(r,0x36); platform_out(0x43,1,(uint8_t)r->ax);
    set_al(r,(uint8_t)logic(r,0,8)); platform_out(0x40,1,0); platform_out(0x40,1,0);
    r->ds=ds; return UGH_OK;
}
/* STI/PUSHF/CALL FAR to an IRET handler. The six-byte frame is real RAM.
 * The saved external BIOS handler has no implicit/default implementation. */
/* TRANSLATES TIMER:ChainSavedTimerInterrupt */
EXPORT int c_ChainSavedTimerInterrupt(Regs *r) {
    flag(r,IF,1); r->sp=(uint16_t)(r->sp-6);
    wr16(r->ss,r->sp,(uint16_t)(T(ChainSavedTimerInterrupt)+6));
    wr16(r->ss,(uint16_t)(r->sp+2),r->cs); wr16(r->ss,(uint16_t)(r->sp+4),r->flags);
    return ugh_dispatch_interrupt(rd16(r->ds,D(PreviousInt08Segment)),rd16(r->ds,D(PreviousInt08Offset)),r);
}
