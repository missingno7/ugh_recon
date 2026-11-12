#include "ugh.h"

/* Publish these in a shared timer interface for later packages. */
/* SHARED-REQUEST */
EXPORT int c_RemoveTimerCallback(Regs *r);
EXPORT int c_SetTimerCallbackInterval(Regs *r);

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
