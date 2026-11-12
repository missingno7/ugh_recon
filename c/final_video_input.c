#include "platform.h"

/* Every export is a near entry without stack arguments. All original state is
 * addressed through the live segment registers. Arithmetic flags omitted from
 * a contract are scratch/undefined; IF/DF and preserved registers are outputs.
 * CALL frames below are real original return IPs, including saved stack words,
 * so deterministic polling IRQs see the same entry state as the assembly. */
static void push(Regs *r,uint16_t x) {
    r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,x);
}
static uint16_t pop(Regs *r) {
    uint16_t x=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return x;
}
static uint16_t inc(Regs *r,uint16_t x) {
    uint16_t cf=r->flags&CF; x=add16(r,x,1,0); flag(r,CF,cf); return x;
}
static uint8_t dec8(Regs *r,uint8_t x) {
    uint8_t v=(uint8_t)(x-1); flag(r,OF,x==0x80);
    flag(r,AF,((x^v^1)&16)!=0); szp(r,v,8); return v;
}
static int call(Regs *r,uint16_t target,uint16_t ret) {
    return ugh_call_near(target,ret,r);
}

/* AL=8, DX=3DA; AH/all other registers and IF/DF preserved. Final AND
 * defines CF=OF=ZF=SF=0, PF=0; raw finite status reads remain observable. */
/* TRANSLATES GAME:WaitNextVerticalRetrace */
EXPORT int c_WaitNextVerticalRetrace(Regs *r) {
    int status=call(r,G(WaitVerticalRetraceInactive),G(WaitVerticalRetraceActive));
    return status?status:c_WaitVerticalRetraceActive(r);
}
/* AL=0, DX=3DA; other registers/IF/DF preserved; final AND defines ZF/PF=1. */
/* TRANSLATES GAME:WaitThroughVerticalRetrace */
EXPORT int c_WaitThroughVerticalRetrace(Regs *r) {
    int status=call(r,G(WaitVerticalRetraceActive),G(WaitVerticalRetraceInactive));
    return status?status:c_WaitVerticalRetraceInactive(r);
}
/* DS selects keyboard/joystick cells. DX saved; CX counts only no-input
 * retraces, including wrap from zero. AX=39h for button/timeout, else raw scan
 * plus change byte. BX/BP/SI/DI are sampler outputs if reached. Final AND CX
 * defines CF/OF/ZF/SF/PF; IF/DF preserved. IRQ service is at the polling CALL. */
/* TRANSLATES GAME:WaitForInputOrRetraceTimeout */
EXPORT int c_WaitForInputOrRetraceTimeout(Regs *r) {
    push(r,r->dx);
    int status=call(r,G(PollKeyboardScanChange),G(loc_449B)); if(status) return status;
    do {
        status=platform_service_point_at(SERVICE_IO,r->cs,G(loc_449B),r); if(status) return status;
        status=call(r,G(PollKeyboardScanChange),G(loc_449B)+3); if(status) return status;
        logic(r,r->ax>>8,8); if(r->ax>>8) break;
        push(r,r->cx);
        status=call(r,G(SampleJoystickAxesAndButtons),G(loc_449B)+14); if(status) return status;
        r->cx=pop(r);
        if(!(r->flags&ZF)) { r->ax=0x39; break; }
        status=call(r,G(WaitNextVerticalRetrace),G(loc_449B)+23); if(status) return status;
        r->cx=(uint16_t)(r->cx-1);
        if(!r->cx) { r->ax=0x39; break; }
    } while(1);
    logic(r,r->cx,16); r->dx=pop(r); return UGH_OK;
}
/* DS selects input state. Discards first change; each subsequent iteration
 * waits a complete retrace, samples buttons, then scans. AX and scratch GPRs
 * flow from those pilots. Final OR/AND defines CF/PF/ZF/SF/OF, IF/DF preserved.
 * Keyboard IRQ service precedes the actual post-retrace polling CALL. */
/* TRANSLATES GAME:WaitForScanChangeOrJoystickButton */
EXPORT int c_WaitForScanChangeOrJoystickButton(Regs *r) {
    int status=call(r,G(PollKeyboardScanChange),G(loc_44DE)); if(status) return status;
    for(unsigned budget=0;budget<1000000;budget++) {
        status=call(r,G(WaitNextVerticalRetrace),G(loc_44DE)+3); if(status) return status;
        status=call(r,G(SampleJoystickAxesAndButtons),G(loc_44DE)+6); if(status) return status;
        if(!(r->flags&ZF)) return UGH_OK;
        status=platform_service_point_at(SERVICE_IO,r->cs,G(loc_44DE)+11,r); if(status) return status;
        status=call(r,G(PollKeyboardScanChange),G(loc_44DE)+14); if(status) return status;
        logic(r,r->ax>>8,8); if(r->ax>>8) return UGH_OK;
    }
    return UGH_BUDGET;
}

/* SI=resource segment; DS/CX saved. Scratch and palette destination are far
 * pointers in incoming CS. Invalid magic still copies 384 scratch words.
 * AX/BX/DX/BP preserved; SI=FD00, DI=dest+300, ES=dest segment, DF cleared.
 * Read before write per word preserves aliases/overlap. Arithmetic scratch. */
/* TRANSLATES GAME:UnpackPictureAndCopyPalette */
EXPORT int c_UnpackPictureAndCopyPalette(Regs *r) {
    push(r,r->cx); push(r,r->ds);
    r->ds=r->si; r->si=logic(r,0,16);
    r->di=rd16(r->cs,G(IceScratchPointer));
    r->es=rd16(r->cs,G(IceScratchPointer)+2);
    int status=call(r,G(UnpackIceStream),G(UnpackPictureAndCopyPalette)+14); if(status) return status;
    r->si=0xfa00; r->ds=pop(r); push(r,r->ds); r->cx=r->es;
    r->di=rd16(r->cs,G(PicturePaletteDestination));
    r->es=rd16(r->cs,G(PicturePaletteDestination)+2); r->ds=r->cx; r->cx=0x180;
    do {
        uint16_t v=rd16(r->ds,r->si); r->si=(uint16_t)(r->si+2*step(r));
        wr16(r->es,r->di,v); r->di=(uint16_t)(r->di+2*step(r)); r->cx--;
    } while(r->cx);
    r->ds=pop(r); r->cx=pop(r); return UGH_OK;
}

/* Shared 4E72 tail, not a separately credited adapter. BX holds inclusive
 * BH:BL DAC indices; DS/CX saved, ES/DI unchanged, SI follows incoming DF.
 * AH=0, AL=last component, DX=3C9. Last INC CX defines arithmetic flags;
 * LODSB/OUT/LOOP preserve them. CLI/STI forces IF=1; DF is consumed. */
static int upload_range(Regs *r) {
    push(r,r->cx); push(r,r->ds); r->ds=r->es; r->si=r->di;
    set_ah(r,0); logic(r,0,8); r->cx&=255; logic(r,0,8); flag(r,IF,0);
    r->dx=0x3c8; set_al(r,(uint8_t)r->bx); platform_out(r->dx,1,(uint8_t)r->ax);
    r->dx=inc(r,r->dx);
    for(unsigned i=0;i<3;i++) r->si=add16(r,r->si,r->ax,0);
    uint8_t lo=(uint8_t)r->bx,hi=(uint8_t)(r->bx>>8);
    uint8_t n=(uint8_t)(hi-lo);
    flag(r,CF,hi<lo); flag(r,OF,((hi^lo)&(hi^n)&128)!=0);
    flag(r,AF,((hi^lo^n)&16)!=0); szp(r,n,8);
    r->cx=n; r->cx=inc(r,r->cx);
    do {
        for(unsigned j=0;j<3;j++) {
            set_al(r,rd8(r->ds,r->si)); r->si=(uint16_t)(r->si+step(r));
            platform_out(r->dx,1,(uint8_t)r->ax);
        }
        r->cx--;
    } while(r->cx);
    flag(r,IF,1); r->ds=pop(r); r->cx=pop(r); return UGH_OK;
}
/* DS locates base palette far pointer. Upload all 768 bytes after retrace.
 * BX=FF00; AX/DX/SI scratch, ES:DI=base, CX/DS saved; IF forced on, DF retained. */
/* TRANSLATES GAME:UploadBasePalette */
EXPORT int c_UploadBasePalette(Regs *r) {
    r->di=rd16(r->ds,D(BasePalettePointer)); r->es=rd16(r->ds,D(BasePalettePointer)+2);
    int status=call(r,G(WaitNextVerticalRetrace),G(UploadBasePalette)+7); if(status) return status;
    r->bx=0xff00; return upload_range(r);
}
/* CX factor; compute AH(byte*CX), not saturation, backwards over CS palettes.
 * DS/CX saved; ES:DI=faded pointer, BX=D800, SI=DI+651*step. Uploads only
 * colors 0..216. DX=3C9, IF=1, DF unchanged. Arithmetic as shared uploader. */
/* TRANSLATES GAME:ScaleAndUploadFadedPalette */
EXPORT int c_ScaleAndUploadFadedPalette(Regs *r) {
    r->bx=0x2ff;
    do {
        set_al(r,rd8(r->cs,(uint16_t)(G(BaseRgbPalette)+r->bx))); set_ah(r,0);
        uint32_t product=(uint32_t)r->ax*r->cx;
        r->ax=(uint16_t)product; r->dx=(uint16_t)(product>>16);
        flag(r,CF,r->dx!=0); flag(r,OF,r->dx!=0);
        wr8(r->cs,(uint16_t)(G(FadedRgbPalette)+r->bx),(uint8_t)(r->ax>>8));
        r->bx=dec16(r,r->bx);
    } while((int16_t)r->bx>=0);
    r->di=rd16(r->ds,D(FadedPalettePointer)); r->es=rd16(r->ds,D(FadedPalettePointer)+2);
    r->bx=0xd800;
    int status=call(r,G(WaitNextVerticalRetrace),G(ScaleAndUploadFadedPalette)+30); if(status) return status;
    return upload_range(r);
}
/* Eight complete retraces, 32 RGB triples per retrace. No palette RAM writes.
 * AL=0, AH unchanged, CX=0,DX=3C9; other GPRs/segments saved. IF=1,DF saved;
 * final DEC CH leaves CF=0,PF=ZF=1,AF=OF=SF=0. */
/* TRANSLATES GAME:BlackenVgaPalette */
EXPORT int c_BlackenVgaPalette(Regs *r) {
    r->dx=0x3c8; set_al(r,(uint8_t)logic(r,0,8)); platform_out(r->dx,1,0);
    r->dx=inc(r,r->dx); r->cx=(uint16_t)((r->cx&255)|0x800);
    do {
        push(r,r->dx);
        int status=call(r,G(WaitNextVerticalRetrace),G(BlackenVgaPalette)+13); if(status) return status;
        r->dx=pop(r); flag(r,IF,0); set_al(r,(uint8_t)logic(r,0,8));
        r->cx=(uint16_t)((r->cx&0xff00)|0x20);
        do {
            for(unsigned j=0;j<3;j++) platform_out(r->dx,1,(uint8_t)r->ax);
            r->cx=(uint16_t)((r->cx&0xff00)|dec8(r,(uint8_t)r->cx));
        } while(r->cx&255);
        flag(r,IF,1); r->cx=(uint16_t)((uint16_t)dec8(r,(uint8_t)(r->cx>>8))<<8);
    } while(r->cx>>8);
    return UGH_OK;
}
/* Swaps only the CS page offset words, preserves their segment words. AX/BX/DX
 * saved; other registers/segments/IF/DF unchanged. Wait inactive, then CRTC
 * indices 0Ch and 0Dh; final INC 3D4 defines arithmetic except CF (AND clears). */
/* TRANSLATES GAME:SwapAndDisplayVgaPage */
EXPORT int c_SwapAndDisplayVgaPage(Regs *r) {
    push(r,r->ax); push(r,r->bx); push(r,r->dx);
    r->bx=rd16(r->cs,G(DisplayedVgaPagePointer));
    uint16_t draw=rd16(r->cs,G(DrawPagePointer)); wr16(r->cs,G(DrawPagePointer),r->bx);
    r->bx=draw; wr16(r->cs,G(DisplayedVgaPagePointer),r->bx);
    int status=call(r,G(WaitVerticalRetraceInactive),G(SwapAndDisplayVgaPage)+21); if(status) return status;
    r->dx=0x3d4; set_al(r,12); platform_out(r->dx,1,(uint8_t)r->ax);
    r->dx=inc(r,r->dx); set_al(r,(uint8_t)(r->bx>>8)); platform_out(r->dx,1,(uint8_t)r->ax);
    r->dx=dec16(r,r->dx); set_al(r,13); platform_out(r->dx,1,(uint8_t)r->ax);
    r->dx=inc(r,r->dx); set_al(r,(uint8_t)r->bx); platform_out(r->dx,1,(uint8_t)r->ax);
    r->dx=pop(r); r->bx=pop(r); r->ax=pop(r); return UGH_OK;
}
/* DS unchanged; ES=A000,AX=CX=DI=0,DX=3C5; BX/SI/BP saved. All flags from
 * XOR DI except original IF/DF. 32768 STOSW operands consume DF; VGA write
 * mode/latches remain caller configuration, not an invented memset. */
/* TRANSLATES GAME:ClearAllVgaPlanes */
EXPORT int c_ClearAllVgaPlanes(Regs *r) {
    int status=call(r,G(EnableAllVgaWritePlanes),G(ClearAllVgaPlanes)+3); if(status) return status;
    r->es=0xa000; r->di=logic(r,0,16); r->ax=r->di; r->cx=0x8000;
    do {
        wr16(r->es,r->di,r->ax); r->di=(uint16_t)(r->di+2*step(r)); r->cx--;
    } while(r->cx);
    return UGH_OK;
}

/* Both configuration entries share this instruction-equivalent body. DS/BP/SI
 * preserved; ES=A000,AX=CX=DI=0,BX untouched,DX=3C5,IF=1; DF preserved.
 * CS dimensions/page pointers and VGA/DAC state change. Gameplay page gaps
 * are 4F80, independently of the 4800 copy length. Tail is the real page flip. */
static void out_al(Regs *r,uint16_t port,uint8_t value) {
    r->dx=port; set_al(r,value); platform_out(port,1,value);
}
static void rmw(Regs *r,uint16_t port,uint8_t mask,uint8_t bits) {
    r->dx=port; set_al(r,(uint8_t)platform_in(port,1));
    set_al(r,(uint8_t)logic(r,(uint8_t)r->ax&mask,8));
    set_al(r,(uint8_t)logic(r,(uint8_t)r->ax|bits,8)); platform_out(port,1,(uint8_t)r->ax);
}
static int configure(Regs *r,int gameplay) {
    uint16_t start=gameplay?G(ConfigureVgaGameplayPages):G(ConfigureVgaPicturePages);
    wr16(r->cs,G(PlayfieldHeight),gameplay?192:200);
    wr16(r->cs,G(VgaPlaneCopyByteCount),gameplay?0x4800:0x3e80);
    int status=call(r,G(BlackenVgaPalette),(uint16_t)(start+17)); if(status) return status;
    out_al(r,0x3c4,4); rmw(r,0x3c5,0xf7,0);
    out_al(r,0x3d4,0x14); rmw(r,0x3d5,0xbf,0);
    out_al(r,0x3d4,0x17); rmw(r,0x3d5,0xff,0x40);
    out_al(r,0x3d4,0x13); out_al(r,0x3d5,gameplay?0x30:0x28);
    out_al(r,0x3d4,0x18); out_al(r,0x3d5,gameplay?0x7f:0x8f);
    out_al(r,0x3d4,7); rmw(r,0x3d5,0xef,0x10);
    out_al(r,0x3d4,9); rmw(r,0x3d5,0xbf,0);
    status=call(r,G(WaitNextVerticalRetrace),(uint16_t)(start+91)); if(status) return status;
    out_al(r,0x3c0,0x10); r->dx=inc(r,r->dx);
    set_al(r,(uint8_t)platform_in(r->dx,1)); set_al(r,(uint8_t)logic(r,(uint8_t)r->ax|0x20,8));
    r->dx=dec16(r,r->dx); platform_out(r->dx,1,(uint8_t)r->ax); out_al(r,r->dx,0x20);
    r->ax=logic(r,0,16); wr16(r->cs,G(FixedVgaPagePointer),r->ax);
    if(gameplay) r->ax=add16(r,r->ax,0xa88,0);
    wr16(r->cs,G(DisplayedVgaPagePointer),r->ax);
    if(gameplay) r->ax=add16(r,r->ax,0x4f80,0);
    wr16(r->cs,G(DrawPagePointer),gameplay?r->ax:0x3e80);
    if(gameplay) r->ax=add16(r,r->ax,0x4f80,0);
    wr16(r->cs,G(BackgroundPagePointer),gameplay?r->ax:0x7d00);
    status=call(r,G(ClearAllVgaPlanes),(uint16_t)(start+(gameplay?136:133))); if(status) return status;
    return c_SwapAndDisplayVgaPage(r);
}
/* TRANSLATES GAME:ConfigureVgaPicturePages */
EXPORT int c_ConfigureVgaPicturePages(Regs *r) { return configure(r,0); }
/* TRANSLATES GAME:ConfigureVgaGameplayPages */
EXPORT int c_ConfigureVgaGameplayPages(Regs *r) { return configure(r,1); }

/* Calibration consumes DS centers and produces AX/BX/CX/DX/BP/SI/DI as in the
 * sampler/math, ES and DS saved. IF forced on, DF unchanged. Presence pair
 * tests use the INITIAL raw port byte saved across the first sample. Missing
 * sticks retain old threshold/control words; doubled centers wrap before the
 * unsigned maximum. No host time: discharge delays are finite DEC loops. */
static void thresholds(Regs *r,uint16_t count,uint16_t low,uint16_t high) {
    r->ax=rd16(r->ds,count); r->bx=r->ax;
    r->ax=(uint16_t)(r->ax>>1); /* SHR's flags are overwritten by SUB. */
    r->bx=sub16(r,r->bx,r->ax,0); wr16(r->ds,low,r->bx);
    r->bx=add16(r,r->bx,r->ax,0); r->bx=add16(r,r->bx,r->ax,0); wr16(r->ds,high,r->bx);
}
/* TRANSLATES GAME:DetectAndCalibrateJoysticks */
EXPORT int c_DetectAndCalibrateJoysticks(Regs *r) {
    flag(r,IF,0); r->ax=sub16(r,r->ax,r->ax,0);
    wr16(r->ds,D(JoystickPresentFlags),0); wr16(r->ds,D(SecondJoystickPresent),0);
    wr8(r->ds,D(JoystickEnabledAxisMask),0); wr16(r->ds,D(JoystickSampleLoopLimit),0xffff);
    const uint16_t clear[]={D(ds_3321),D(ds_3325),D(ds_3323),D(ds_3327),
        D(FirstJoystickXDoubleCenter),D(FirstJoystickYDoubleCenter),
        D(SecondJoystickXDoubleCenter),D(SecondJoystickYDoubleCenter)};
    for(unsigned i=0;i<8;i++) wr16(r->ds,clear[i],r->ax);
    r->dx=0x201; platform_out(r->dx,1,(uint8_t)r->ax);
    r->cx=0x1600; do { r->cx=dec16(r,r->cx); } while(r->cx);
    set_al(r,(uint8_t)platform_in(r->dx,1)); if(ugh_devices.error) return UGH_UNSUPPORTED;
    push(r,r->ax); logic(r,(uint8_t)r->ax&3,8);
    if(!((uint8_t)r->ax&3)) {
        wr16(r->ds,D(JoystickPresentFlags),0xffff); wr16(r->ds,D(PlayerOneControlMode),0);
        wr8(r->ds,D(JoystickEnabledAxisMask),(uint8_t)logic(r,rd8(r->ds,D(JoystickEnabledAxisMask))|3,8));
        int status=call(r,G(SampleJoystickAxesAndButtons),G(DetectAndCalibrateJoysticks)+89); if(status) return status;
        r->ax=rd16(r->ds,D(FirstJoystickXCount)); r->bx=rd16(r->ds,D(FirstJoystickYCount));
        r->ax=(uint16_t)(r->ax*2); r->bx=(uint16_t)(r->bx*2);
        wr16(r->ds,D(FirstJoystickXDoubleCenter),r->ax); wr16(r->ds,D(FirstJoystickYDoubleCenter),r->bx);
        thresholds(r,D(FirstJoystickXCount),D(JoystickLeftThresholds),D(JoystickRightThresholds));
        thresholds(r,D(FirstJoystickYCount),D(JoystickUpThresholds),D(JoystickDownThresholds));
    }
    r->ax=pop(r); logic(r,(uint8_t)r->ax&12,8);
    if(!((uint8_t)r->ax&12)) {
        wr16(r->ds,D(SecondJoystickPresent),0xffff); wr16(r->ds,D(PlayerTwoControlMode),1);
        wr8(r->ds,D(JoystickEnabledAxisMask),(uint8_t)logic(r,rd8(r->ds,D(JoystickEnabledAxisMask))|12,8));
        r->cx=0x1600; do { r->cx=dec16(r,r->cx); } while(r->cx);
        int status=call(r,G(SampleJoystickAxesAndButtons),G(DetectAndCalibrateJoysticks)+188); if(status) return status;
        r->cx=rd16(r->ds,D(SecondJoystickXCount)); r->dx=rd16(r->ds,D(SecondJoystickYCount));
        r->cx=(uint16_t)(r->cx*2); r->dx=(uint16_t)(r->dx*2);
        wr16(r->ds,D(SecondJoystickXDoubleCenter),r->cx); wr16(r->ds,D(SecondJoystickYDoubleCenter),r->dx);
        thresholds(r,D(SecondJoystickXCount),D(SecondJoystickXLowThreshold),D(SecondJoystickXHighThreshold));
        thresholds(r,D(SecondJoystickYCount),D(SecondJoystickYLowThreshold),D(SecondJoystickYHighThreshold));
    }
    r->ax=rd16(r->ds,D(FirstJoystickXDoubleCenter));
    const uint16_t rest[]={D(FirstJoystickYDoubleCenter),D(SecondJoystickXDoubleCenter),D(SecondJoystickYDoubleCenter)};
    for(unsigned i=0;i<3;i++) {
        uint16_t v=rd16(r->ds,rest[i]); sub16(r,r->ax,v,0); if(r->ax<v) r->ax=v;
    }
    wr16(r->ds,D(JoystickSampleLoopLimit),r->ax); flag(r,IF,1); return UGH_OK;
}
