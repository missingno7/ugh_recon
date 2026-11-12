#include "platform.h"

/* TRANSLATES TIMER:RegisterTimerCallback */
EXPORT int c_RegisterTimerCallback(Regs *r) {
    uint16_t slot=(uint16_t)(rd16(DATA_SEG,D(LastActiveTimerSlotOffset))+2);
    wr16(DATA_SEG,(uint16_t)(D(TimerIntervalLowBySlot)+slot),r->bx);
    wr16(DATA_SEG,(uint16_t)(D(TimerIntervalHighBySlot)+slot),r->cx);
    wr16(DATA_SEG,(uint16_t)(D(TimerRemainingLowBySlot)+slot),r->bx);
    wr16(DATA_SEG,(uint16_t)(D(TimerRemainingHighBySlot)+slot),r->cx);
    /* SHL/SHR round trip deliberately discards bit 15. */
    uint16_t twice=(uint16_t)(slot*2);
    wr16(DATA_SEG,(uint16_t)(D(TimerCallbackOffsetBySlot)+twice),r->ax);
    wr16(DATA_SEG,(uint16_t)(D(TimerCallbackSegmentBySlot)+twice),r->dx);
    slot=twice>>1;
    uint32_t interval=r->bx | (uint32_t)r->cx*65536u;
    if(interval<rd32(DATA_SEG,D(EarliestTimerIntervalLow))) {
        /* Low and high arrays are adjacent scalar words here, not interleaved arrays. */
        wr16(DATA_SEG,D(EarliestTimerIntervalLow),r->bx);
        wr16(DATA_SEG,D(EarliestTimerIntervalHigh),r->cx);
    }
    uint16_t handle=slot;
    for(unsigned budget=0;budget<32768;budget++,handle=(uint16_t)(handle-2)) {
        if(rd16(DATA_SEG,(uint16_t)(D(TimerSlotOffsetByHandle)+handle))&0x8000u) {
            wr16(DATA_SEG,(uint16_t)(D(TimerHandleBySlot)+slot),handle);
            wr16(DATA_SEG,(uint16_t)(D(TimerSlotOffsetByHandle)+handle),slot);
            wr16(DATA_SEG,D(LastActiveTimerSlotOffset),slot);
            r->ax=handle; return UGH_OK;
        }
    }
    return UGH_BUDGET;
}

/* TRANSLATES TIMER:HandleTimerInterrupt */
EXPORT int c_HandleTimerInterrupt(Regs *r) {
    Regs saved=*r;
    r->ds=DATA_SEG;
    uint16_t slot=rd16(DATA_SEG,D(LastActiveTimerSlotOffset));
    unsigned budget=32768;
    do {
        if(!budget--) { *r=saved; return UGH_BUDGET; }
        uint16_t lo=rd16(DATA_SEG,(uint16_t)(D(TimerRemainingLowBySlot)+slot));
        uint16_t hi=rd16(DATA_SEG,(uint16_t)(D(TimerRemainingHighBySlot)+slot));
        uint16_t qlo=rd16(DATA_SEG,D(NextPitQuantumLow));
        uint16_t qhi=rd16(DATA_SEG,D(NextPitQuantumHigh));
        uint16_t newlo=(uint16_t)(lo-qlo);
        uint16_t newhi=(uint16_t)(hi-qhi-(lo<qlo));
        wr16(DATA_SEG,(uint16_t)(D(TimerRemainingLowBySlot)+slot),newlo);
        wr16(DATA_SEG,(uint16_t)(D(TimerRemainingHighBySlot)+slot),newhi);
        if((int16_t)newhi<0 || !(newlo|newhi)) {
            wr16(DATA_SEG,(uint16_t)(D(TimerCallbackDueBySlot)+slot),0x8000);
            uint32_t total=newlo | (uint32_t)newhi*65536u;
            total+=rd16(DATA_SEG,(uint16_t)(D(TimerIntervalLowBySlot)+slot)) |
                   (uint32_t)rd16(DATA_SEG,(uint16_t)(D(TimerIntervalHighBySlot)+slot))*65536u;
            wr16(DATA_SEG,(uint16_t)(D(TimerRemainingLowBySlot)+slot),(uint16_t)total);
            wr16(DATA_SEG,(uint16_t)(D(TimerRemainingHighBySlot)+slot),(uint16_t)(total>>16));
        }
        slot=(uint16_t)(slot-2);
    } while((int16_t)slot>=0);
    wr16(DATA_SEG,D(NextPitQuantumLow),rd16(DATA_SEG,D(EarliestTimerIntervalLow)));
    wr16(DATA_SEG,D(NextPitQuantumHigh),rd16(DATA_SEG,D(EarliestTimerIntervalHigh)));
    slot=rd16(DATA_SEG,D(LastActiveTimerSlotOffset));
    budget=32768;
    do {
        if(!budget--) { *r=saved; return UGH_BUDGET; }
        if(rd16(DATA_SEG,(uint16_t)(D(TimerCallbackDueBySlot)+slot))&0x8000u) {
            wr16(DATA_SEG,(uint16_t)(D(TimerCallbackDueBySlot)+slot),0);
            uint16_t off=rd16(DATA_SEG,(uint16_t)(D(TimerCallbackOffsetBySlot)+slot*2));
            uint16_t seg=rd16(DATA_SEG,(uint16_t)(D(TimerCallbackSegmentBySlot)+slot*2));
            /* DS and SI alone are saved at this call site. Callback clobbers flow
             * to the next callback until the ISR restores the interrupted registers. */
            r->si=(uint16_t)(slot*2);
            int status=ugh_dispatch(seg,off,r);
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

int ugh_dispatch(uint16_t seg,uint16_t off,Regs *r) {
    if(seg==SOUND_SEG && off==S(ClearSoundState)) return c_ClearSoundState(r);
    return UGH_BAD_CALLBACK;
}
