#include "platform.h"

/* Near entry, no stack arguments. DS locates the two far-pointer cells; it is
 * restored. ES becomes the destination segment. AX is the final loaded word,
 * CX=0, SI/DI move by +/-384; BX/DX/BP and all flags are preserved.
 * Each iteration reads first, writes DI+180h, then writes DI. This order matters
 * for aliased palettes. DF is consumed, never cleared; all offsets wrap at 16 bits.
 * No callees or hardware effects. The second source half is never read. */
/* TRANSLATES GAME:DuplicateSourcePaletteHalves */
EXPORT int c_DuplicateSourcePaletteHalves(Regs *r) {
    uint16_t saved_ds=r->ds;
    r->di=rd16(r->ds,D(BasePalettePointer));
    r->es=rd16(r->ds,(uint16_t)(D(BasePalettePointer)+2));
    r->si=rd16(r->ds,D(PaletteSourcePointer));
    r->ds=rd16(r->ds,(uint16_t)(D(PaletteSourcePointer)+2));
    r->cx=0xc0;
    do {
        r->ax=rd16(r->ds,r->si);
        r->si=(uint16_t)(r->si+2*step(r));
        wr16(r->es,(uint16_t)(r->di+0x180),r->ax);
        wr16(r->es,r->di,r->ax);
        r->di=(uint16_t)(r->di+2*step(r));
        r->cx=(uint16_t)(r->cx-1);
    } while(r->cx);
    r->ds=saved_ds;
    return UGH_OK;
}

/* Near entry, no stack arguments. DS:SI is the packed stream; ES is replaced
 * by the original zero-workspace segment, DI by zero, then control falls through
 * to the accepted ICE pilot. AX/BX/CX/DX/BP/DS remain unchanged, SI/DI are decoder
 * outputs, DF=0. Bad first/second magic advances SI by 2/4 and leaves DI=0.
 * Other arithmetic flags are scratch; no platform calls. */
/* TRANSLATES GAME:UnpackIceToScratch */
EXPORT int c_UnpackIceToScratch(Regs *r) {
    r->es=UGH_S_ZERO_IceDecodeWorkspace;
    r->di=logic(r,0,16); /* XOR DI,DI precedes the decoder's saved registers. */
    return c_UnpackIceStream(r);
}

/* INT 24h entry / IRET, no arguments: AL=3, all other registers preserved.
 * STI sets live IF; the harness performs IRET and restores the saved FLAGS.
 * No DOS service is called by this handler itself. */
/* TRANSLATES GAME:FailDosCriticalError */
EXPORT int c_FailDosCriticalError(Regs *r) {
    flag(r,IF,1);
    set_al(r,3);
    return UGH_OK;
}

/* Near entry, no arguments. AX is an unsigned exclusive bound, including zero.
 * Four state words are read/written through incoming CS, never DS. The carry
 * from each ADD/ADC feeds the next, including the final update of state0.
 * AX=high word of new state0*bound; BX/CX/DX/SI/DI/BP and segments preserved.
 * MUL defines CF/OF iff its high word is nonzero; other arithmetic flags are
 * undefined. No callees or device effects. Bound zero still advances the state. */
/* TRANSLATES GAME:NextRandomBelowAx */
EXPORT int c_NextRandomBelowAx(Regs *r) {
    uint16_t bound=r->ax;
    uint16_t a=add16(r,bound,rd16(r->cs,G(RandomStateWord0)),0);
    uint16_t b=add16(r,rd16(r->cs,G(RandomStateWord1)),a,r->flags&CF);
    wr16(r->cs,G(RandomStateWord1),b);
    uint16_t c=add16(r,rd16(r->cs,G(RandomStateWord2)),b,r->flags&CF);
    wr16(r->cs,G(RandomStateWord2),c);
    uint16_t d=add16(r,rd16(r->cs,G(RandomStateWord3)),c,r->flags&CF);
    wr16(r->cs,G(RandomStateWord3),d);
    a=add16(r,a,d,r->flags&CF);
    wr16(r->cs,G(RandomStateWord0),a);
    uint32_t product=(uint32_t)a*bound;
    r->ax=(uint16_t)(product>>16);
    flag(r,CF,r->ax!=0);
    flag(r,OF,r->ax!=0);
    return UGH_OK;
}

/* Near entry, no arguments: write SEQ index 2 then map mask 0Fh, in that order.
 * AL=0Fh (AH preserved), DX=03C5h. Other registers and CF/IF/DF preserved;
 * PF/AF/ZF/SF/OF come from INC 03C4h. No RAM writes or callees. */
/* TRANSLATES GAME:EnableAllVgaWritePlanes */
EXPORT int c_EnableAllVgaWritePlanes(Regs *r) {
    r->dx=0x3c4;
    set_al(r,2);
    platform_out(r->dx,1,(uint8_t)r->ax);
    uint16_t cf=r->flags&CF;
    r->dx=add16(r,r->dx,1,0);
    flag(r,CF,cf);
    set_al(r,15);
    platform_out(r->dx,1,(uint8_t)r->ax);
    return UGH_OK;
}
/* Near polling entries: raw status scripts are finite; each IN is observable.
 * AH and other registers survive except DX; AND supplies the defined flags. */
static int retrace(Regs *r,int active) {
    r->dx=0x3da;
    for(unsigned budget=0;budget<1000000;budget++) {
        set_al(r,(uint8_t)platform_in(r->dx,1)); if(ugh_devices.error) return UGH_UNSUPPORTED;
        set_al(r,(uint8_t)logic(r,(uint8_t)r->ax&8,8));
        if(!!(r->ax&8)==active) return UGH_OK;
    }
    return UGH_BUDGET;
}
/* TRANSLATES GAME:WaitVerticalRetraceActive */
EXPORT int c_WaitVerticalRetraceActive(Regs *r) {
    int st=platform_service_point_at(SERVICE_RETRACE,r->cs,G(WaitVerticalRetraceActive),r);
    return st?st:retrace(r,1);
}
/* TRANSLATES GAME:WaitVerticalRetraceInactive */
EXPORT int c_WaitVerticalRetraceInactive(Regs *r) { return retrace(r,0); }

/* Near, DS preserved; AX/BX/SI/DI/DX/ES change as observed, IF forced on.
 * Reset only candidate bytes; BIOS head becomes tail, no scan translation. */
/* TRANSLATES GAME:InstallKeyboardSequenceInterrupt */
EXPORT int c_InstallKeyboardSequenceInterrupt(Regs *r) {
    set_al(r,0); logic(r,0,8); wr8(r->ds,D(KeyboardSequenceIndex),0); r->si=logic(r,0,16);
    for(unsigned budget=0;;budget++) {
        if(budget==32768) return UGH_BUDGET;
        uint8_t b=rd8(r->ds,(uint16_t)(D(KeyboardSequenceRecords)+r->si));
        if(b==255) break;
        wr8(r->ds,(uint16_t)(D(KeyboardSequenceCandidateState)+r->si),(uint8_t)r->ax);
        r->si=add16(r,r->si,6,0);
    }
    /* CMP byte,FF defines SF/ZF/PF/CF/OF; equal is all zero except ZF/PF. */
    sub16(r,255,255,0); flag(r,IF,0); r->di=0x40; r->es=r->di;
    r->ax=rd16(r->es,0x1c); wr16(r->es,0x1a,r->ax);
    r->ax=0x3509; int status=platform_interrupt(0x21,r); if(status) return status;
    wr16(r->ds,D(PreviousKeyboardVector),r->bx); wr16(r->ds,D(PreviousKeyboardVectorSegment),r->es);
    uint16_t ds=r->ds; r->ax=0x2509; r->dx=rd16(r->ds,D(KeyboardHandlerVector));
    r->ds=rd16(r->ds,(uint16_t)(D(KeyboardHandlerVector)+2));
    status=platform_interrupt(0x21,r); r->ds=ds; flag(r,IF,1); return status;
}
/* Near: DS preserved, ES=40, AX=BIOS tail, DI=40; IF forced on. */
/* TRANSLATES GAME:RestoreKeyboardInterrupt */
EXPORT int c_RestoreKeyboardInterrupt(Regs *r) {
    uint16_t ds=r->ds; r->ax=0x2509; r->dx=rd16(r->ds,D(PreviousKeyboardVector));
    r->ds=rd16(r->ds,D(PreviousKeyboardVectorSegment)); int status=platform_interrupt(0x21,r); r->ds=ds;
    flag(r,IF,0); r->di=0x40; r->es=r->di; r->ax=rd16(r->es,0x1c); wr16(r->es,0x1a,r->ax);
    flag(r,IF,1); return status;
}
/* IRET; AX/BX/SI/DS saved, all other registers untouched. Prefix/break bytes
 * remain raw. Candidate scans and action stores remain original RAM lvalues. */
/* TRANSLATES GAME:HandleKeyboardScanInterrupt */
EXPORT int c_HandleKeyboardScanInterrupt(Regs *r) {
    uint8_t scan=(uint8_t)platform_in(0x60,1); if(ugh_devices.error) return UGH_UNSUPPORTED;
    wr8(r->cs,G(LatestInterruptScanCode),scan);
    uint16_t si=0,bx=rd8(DATA_SEG,D(KeyboardSequenceIndex)); uint8_t matches=0;
    int reset=0;
    for(unsigned budget=0;budget<32768;budget++) {
        if(rd8(DATA_SEG,(uint16_t)(D(KeyboardSequenceCandidateState)+si))!=255) {
            if(scan!=rd8(DATA_SEG,(uint16_t)(D(KeyboardSequenceRecords)+bx+si)))
                wr8(DATA_SEG,(uint16_t)(D(KeyboardSequenceCandidateState)+si),255);
            else if(rd8(DATA_SEG,(uint16_t)(D(KeyboardSequenceNextScan)+bx+si))==255) {
                bx=rd8(DATA_SEG,(uint16_t)(D(KeyboardSequenceActionIndex)+si))&2;
                if(rd16(DATA_SEG,(uint16_t)(D(PlayerOneControlMode)+bx))&0x8000) {
                    bx=rd8(DATA_SEG,(uint16_t)(D(KeyboardSequenceActionIndex)+si));
                    uint8_t action=rd8(DATA_SEG,(uint16_t)(D(KeyboardSequenceActionValue)+si));
                    wr8(DATA_SEG,(uint16_t)(D(PlayerUpInput)+bx),action);
                }
                reset=1; break;
            } else matches++;
        }
        si=(uint16_t)(si+6);
        if(rd8(DATA_SEG,(uint16_t)(D(KeyboardSequenceRecords)+si))==255) { reset=!matches; break; }
        if(budget==32767) return UGH_BUDGET;
    }
    if(reset) {
        wr8(DATA_SEG,D(KeyboardSequenceIndex),0); si=0;
        for(unsigned budget=0;budget<32768;budget++) {
            if(rd8(DATA_SEG,(uint16_t)(D(KeyboardSequenceRecords)+si))==255) break;
            wr8(DATA_SEG,(uint16_t)(D(KeyboardSequenceCandidateState)+si),0); si=(uint16_t)(si+6);
            if(budget==32767) return UGH_BUDGET;
        }
    } else wr8(DATA_SEG,D(KeyboardSequenceIndex),(uint8_t)(rd8(DATA_SEG,D(KeyboardSequenceIndex))+1));
    platform_out(0x20,1,0x20); return UGH_OK;
}
/* Near; install vector 24 without retaining an old handler; DS restored. */
/* TRANSLATES GAME:InstallDosCriticalErrorFailHandler */
EXPORT int c_InstallDosCriticalErrorFailHandler(Regs *r) {
    uint16_t ds=r->ds; r->ds=r->cs; r->ax=0x2524; r->dx=G(FailDosCriticalError);
    int status=platform_interrupt(0x21,r); r->ds=ds; return status;
}
/* Near; DOS time is a fixture, only DH is written into the CS RNG state. */
/* TRANSLATES GAME:SeedRandomFromDosSeconds */
EXPORT int c_SeedRandomFromDosSeconds(Regs *r) {
    set_ah(r,0x2c); int status=platform_interrupt(0x21,r); if(status) return status;
    wr8(r->cs,G(RandomSecondsSeedByte),(uint8_t)(r->dx>>8)); return UGH_OK;
}
/* Near; actual trigger AL, two independent button reads and priority 1/2/4/8.
 * A detected axis does not decrement CX. Saved IF/DF survive timing section;
 * final OR supplies arithmetic outputs. No host-time decay is substituted. */
/* TRANSLATES GAME:SampleJoystickAxesAndButtons */
EXPORT int c_SampleJoystickAxesAndButtons(Regs *r) {
    uint16_t saved_flags=r->flags; flag(r,IF,0); r->dx=0x201;
    platform_out(r->dx,1,(uint8_t)r->ax); r->bx=r->bp=r->si=r->di=0;
    r->cx=rd16(r->ds,D(JoystickSampleLoopLimit));
    set_al(r,(uint8_t)platform_in(r->dx,1)); r->ax=(uint16_t)~r->ax; r->ax&=0x30;
    wr16(r->ds,D(JoystickButtonBits),r->ax);
    set_al(r,(uint8_t)platform_in(r->dx,1)); r->ax=(uint16_t)~r->ax; r->ax&=0xc0;
    wr16(r->ds,D(SecondJoystickButtonBits),r->ax);
    uint8_t mask=rd8(r->ds,D(JoystickEnabledAxisMask));
    if(mask) {
        uint8_t ah=(uint8_t)~mask;
        for(unsigned budget=0;budget<1000000;budget++) {
            uint8_t v=(uint8_t)platform_in(r->dx,1); if(ugh_devices.error) return UGH_UNSUPPORTED;
            uint8_t ended=(uint8_t)~(v|ah);
            if(ended) {
                if(ended&1) { r->bx=r->cx; ah|=1; }
                else if(ended&2) { r->bp=r->cx; ah|=2; }
                else if(ended&4) { r->si=r->cx; ah|=4; }
                else { r->di=r->cx; ah|=8; }
                if(ah==255) break;
            } else { r->cx=(uint16_t)(r->cx-1); if(!r->cx) break; }
            if(budget==999999) return UGH_BUDGET;
        }
    }
    if(ugh_devices.error) return UGH_UNSUPPORTED;
    r->flags=saved_flags; r->ax=rd16(r->ds,D(JoystickSampleLoopLimit));
    r->dx=sub16(r,r->ax,r->di,0); wr16(r->ds,D(SecondJoystickYCount),r->dx);
    r->cx=sub16(r,r->ax,r->si,0); wr16(r->ds,D(SecondJoystickXCount),r->cx);
    r->dx=sub16(r,r->ax,r->bx,0); wr16(r->ds,D(FirstJoystickXCount),r->dx);
    r->ax=sub16(r,r->ax,r->bp,0); wr16(r->ds,D(FirstJoystickYCount),r->ax);
    r->ax=logic(r,rd16(r->ds,D(JoystickButtonBits))|rd16(r->ds,D(SecondJoystickButtonBits)),16);
    return UGH_OK;
}
