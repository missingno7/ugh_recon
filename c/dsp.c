#include "platform.h"

/* SOUND state is addressed through the live CS. All five entries preserve
 * DS/ES/SS/SP and IF/DF. There are no native objects holding game state.
 * The omitted probe/lifecycle entries reach GAME:001F through a far CALL even
 * though that hook has a near RET; see the worker report for the measured ABI.
 */
static void push_word(Regs *r,uint16_t value) {
    r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,value);
}
static uint16_t pop_word(Regs *r) {
    uint16_t value=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return value;
}
/* CALL FAR owns its real return frame, including calls to pilot adapters.
 * Displacements below are measured instruction ends within generated entries. */
static int call_sound(Regs *r,uint16_t target,uint16_t return_ip) {
    push_word(r,r->cs); push_word(r,return_ip);
    int status=ugh_dispatch(r->cs,target,r);
    if(status!=UGH_CONTROL_TRANSFER) r->sp=(uint16_t)(r->sp+4);
    return status;
}

/* These are control prefixes, not completed routine translations. Status 4
 * leaves actual CS:IP/SP at the GAME landing after near RET. The unreachable
 * intended SOUND scan/vector/reset tails are not substituted for that code. */
/* CONTROL_PREFIX SOUND:ProbeSoundBlasterDmaIrq */
EXPORT int c_ProbeSoundBlasterDmaIrq(Regs *r) {
    push_word(r,r->es); push_word(r,r->ds);
    int st=call_sound(r,S(LocateDmaMixBuffers),S(ProbeSoundBlasterDmaIrq)+6);
    if(st) return st;
    wr16(r->cs,S(DspInterruptVector),1); wr16(r->cs,S(DspBasePort),0x200);
    return ugh_call_near_ret_hook(r,G(loc_001F),S(ProbeSoundBlasterDmaIrq)+0x19);
}
/* CONTROL_PREFIX SOUND:InitializeDspPlayback */
EXPORT int c_InitializeDspPlayback(Regs *r) {
    push_word(r,r->ds); push_word(r,r->es);
    int st=call_sound(r,S(CalibrateSoundDelay),S(InitializeDspPlayback)+6); if(st) return st;
    return call_sound(r,S(ProbeSoundBlasterDmaIrq),S(InitializeDspPlayback)+10);
}
/* CONTROL_PREFIX SOUND:ShutdownDspPlayback */
EXPORT int c_ShutdownDspPlayback(Regs *r) {
    push_word(r,r->ds); set_al(r,0xd3);
    int st=call_sound(r,S(WriteSoundBlasterDsp),S(ShutdownDspPlayback)+7); if(st) return st;
    return ugh_call_near_ret_hook(r,G(loc_001F),S(ShutdownDspPlayback)+12);
}
static uint16_t increment(Regs *r,uint16_t value) {
    uint16_t carry=r->flags&CF;
    value=add16(r,value,1,0); flag(r,CF,carry); return value;
}
static void compare_byte(Regs *r,uint8_t a,uint8_t b) {
    uint8_t value=(uint8_t)(a-b);
    flag(r,CF,a<b); flag(r,OF,((a^b)&(a^value)&0x80u)!=0);
    flag(r,AF,((a^b^value)&16u)!=0); szp(r,value,8);
}

/* Far, no stack arguments: CH=physical page, DX=physical offset, BX=byte
 * count. AX low byte becomes high8(count-1); AH and BX/CX/DX/SI/DI/BP survive.
 * DMA channel 1 receives count-1, even when BX=0 or the block crosses a page.
 * Flags are INC BX's defined arithmetic flags with CF from the DSP writer.
 * Ordered OUTs retain the hardware transactions of all delay-jump sequences;
 * those jumps have no polling service site or wall-clock side effect. */
/* TRANSLATES SOUND:StartDmaSampleBlock */
EXPORT int c_StartDmaSampleBlock(Regs *r) {
    push_word(r,r->cx); r->bx=dec16(r,r->bx);
    set_al(r,5); platform_out(0x0a,1,(uint8_t)r->ax);
    set_al(r,0); platform_out(0x0c,1,(uint8_t)r->ax);
    set_al(r,0x49); platform_out(0x0b,1,(uint8_t)r->ax);
    set_al(r,(uint8_t)r->dx); platform_out(2,1,(uint8_t)r->ax);
    set_al(r,(uint8_t)(r->dx>>8)); platform_out(2,1,(uint8_t)r->ax);
    set_al(r,(uint8_t)(r->cx>>8)); platform_out(0x83,1,(uint8_t)r->ax);
    set_al(r,(uint8_t)r->bx); platform_out(3,1,(uint8_t)r->ax);
    set_al(r,(uint8_t)(r->bx>>8)); platform_out(3,1,(uint8_t)r->ax);
    set_al(r,1); platform_out(0x0a,1,(uint8_t)r->ax);
    set_al(r,0x14);
    int status=call_sound(r,S(WriteSoundBlasterDsp),(uint16_t)(S(StartDmaSampleBlock)+0xb3));
    if(status) return status;
    set_al(r,(uint8_t)r->bx);
    status=call_sound(r,S(WriteSoundBlasterDsp),(uint16_t)(S(StartDmaSampleBlock)+0xb9));
    if(status) return status;
    set_al(r,(uint8_t)(r->bx>>8));
    status=call_sound(r,S(WriteSoundBlasterDsp),(uint16_t)(S(StartDmaSampleBlock)+0xbf));
    if(status) return status;
    r->bx=increment(r,r->bx); r->cx=pop_word(r); return UGH_OK;
}

/* Far cdecl unsigned word rate at entry SP+4. All registers preserved.
 * Device bit 1 gates unsigned rate>=1000. The time constant is low8 of
 * -(1000000/rate), with word NEG followed by byte truncation. Flags come from
 * the gate TEST, rejected CMP, or final DSP status TEST (AF undefined for TEST).
 * No division fault is possible after the unsigned threshold check. */
/* TRANSLATES SOUND:SetDspSampleRate */
EXPORT int c_SetDspSampleRate(Regs *r) {
    push_word(r,r->bp); r->bp=r->sp;
    push_word(r,r->ax); push_word(r,r->bx); push_word(r,r->dx);
    uint16_t devices=logic(r,rd16(r->cs,S(SoundDeviceBits))&2u,16);
    if(devices) {
        uint16_t rate=rd16(r->ss,(uint16_t)(r->bp+6)); sub16(r,rate,1000,0);
        if(rate>=1000) {
            r->ax=(uint16_t)(1000000u/rate); r->dx=(uint16_t)(1000000u%rate);
            r->ax=sub16(r,0,r->ax,0); r->bx=r->ax; set_al(r,0x40);
            int status=call_sound(r,S(WriteSoundBlasterDsp),(uint16_t)(S(SetDspSampleRate)+0x30));
            if(status) return status;
            set_al(r,(uint8_t)r->bx);
            status=call_sound(r,S(WriteSoundBlasterDsp),(uint16_t)(S(SetDspSampleRate)+0x36));
            if(status) return status;
        }
    }
    r->dx=pop_word(r); r->bx=pop_word(r); r->ax=pop_word(r);
    r->sp=r->bp; r->bp=pop_word(r); return UGH_OK;
}

/* Far, no arguments. Pulse base+6, delay with AX=3, poll base+E at most
 * 100 times. The response at base+A is read even after a timeout. AX returns
 * zero-extended response; CX=100-polls; DX=base+A. Other registers preserved.
 * CF is response!=AA; all other arithmetic flags are the byte CMP AL,AA. */
/* TRANSLATES SOUND:ResetSoundBlasterDsp */
EXPORT int c_ResetSoundBlasterDsp(Regs *r) {
    r->dx=add16(r,rd16(r->cs,S(DspBasePort)),6,0);
    set_al(r,1); platform_out(r->dx,1,(uint8_t)r->ax); r->ax=3;
    int status=call_sound(r,S(DelaySoundIo),(uint16_t)(S(ResetSoundBlasterDsp)+0x12));
    if(status) return status;
    set_al(r,(uint8_t)logic(r,0,8)); platform_out(r->dx,1,(uint8_t)r->ax);
    r->dx=add16(r,r->dx,8,0); r->cx=100;
    do {
        set_al(r,(uint8_t)platform_in(r->dx,1));
        if(ugh_devices.error) return UGH_UNSUPPORTED;
        logic(r,(uint8_t)r->ax&0x80u,8); r->cx=(uint16_t)(r->cx-1);
    } while(r->cx && !(r->ax&0x80));
    r->dx=sub16(r,r->dx,4,0); set_al(r,(uint8_t)platform_in(r->dx,1));
    if(ugh_devices.error) return UGH_UNSUPPORTED;
    compare_byte(r,(uint8_t)r->ax,0xaa); flag(r,CF,(uint8_t)r->ax!=0xaa);
    return UGH_OK;
}

/* IRET body, no arguments: all registers preserved, FLAGS restored by the
 * caller's interrupt frame. PIC EOI precedes the bit-0 reentry test. Busy entry
 * skips DSP acknowledgement. Otherwise acknowledge base+E, select the queued
 * header at stride 40Ah, start counts>=28h, clear that count and refill the
 * opposite buffer. Short counts mask the selected PIC IRQ. Busy byte is set
 * to 1 then to 0, discarding its other bits. No old-handler chaining. */
/* TRANSLATES SOUND:HandleSampleDmaInterrupt */
EXPORT int c_HandleSampleDmaInterrupt(Regs *r) {
    push_word(r,r->ax); set_al(r,0x20); platform_out(0x20,1,(uint8_t)r->ax);
    r->ax=pop_word(r);
    if(logic(r,rd8(r->cs,S(DspIrqBusy))&1u,8)) return UGH_OK;
    wr8(r->cs,S(DspIrqBusy),1);
    Regs saved=*r; uint16_t pusha_sp=r->sp;
    push_word(r,r->ax); push_word(r,r->cx); push_word(r,r->dx); push_word(r,r->bx);
    push_word(r,pusha_sp); push_word(r,r->bp); push_word(r,r->si); push_word(r,r->di);
    push_word(r,r->es); push_word(r,r->ds);
    r->dx=add16(r,rd16(r->cs,S(DspBasePort)),14,0);
    set_al(r,(uint8_t)platform_in(r->dx,1)); if(ugh_devices.error) return UGH_UNSUPPORTED;
    r->si=logic(r,0,16);
    if(!logic(r,rd8(r->cs,S(DmaMixBufferSelect))&1u,8)) r->si=0x40a;
    r->bx=rd16(r->cs,(uint16_t)(S(DmaMixBufferOneCount)+r->si));
    sub16(r,r->bx,0x28,0);
    if(r->bx>=0x28) {
        wr8(r->cs,S(DmaMixBufferSelect),(uint8_t)logic(r,rd8(r->cs,S(DmaMixBufferSelect))^1u,8));
        r->dx=rd16(r->cs,(uint16_t)(S(DmaMixBufferOneAddress)+r->si));
        r->cx=(uint16_t)((r->cx&255u)|(uint16_t)rd8(r->cs,(uint16_t)(S(DmaMixBufferOnePage)+r->si))*256u);
        int status=call_sound(r,S(StartDmaSampleBlock),(uint16_t)(S(HandleSampleDmaInterrupt)+0x55));
        if(status) return status;
        wr16(r->cs,(uint16_t)(S(DmaMixBufferOneCount)+r->si),0);
        r->si=sub16(r,0,r->si,0);
        r->dx=rd16(r->cs,(uint16_t)(S(DmaMixBufferTwoOffset)+r->si)); r->bx=0x400;
        status=call_sound(r,S(MixSampleVoicePairs),(uint16_t)(S(HandleSampleDmaInterrupt)+0x6a));
        if(status) return status;
        wr16(r->cs,(uint16_t)(S(DmaMixBufferTwoCount)+r->si),r->ax);
    } else {
        set_al(r,(uint8_t)platform_in(0x21,1));
        set_al(r,(uint8_t)logic(r,(uint8_t)r->ax|rd8(r->cs,S(DspPicIrqMask)),8));
        platform_out(0x21,1,(uint8_t)r->ax);
    }
    uint16_t flags=r->flags; *r=saved; r->flags=flags;
    wr8(r->cs,S(DspIrqBusy),0); return UGH_OK;
}

/* Far, no arguments. Disabled bit or signed active count<=0 returns early.
 * Mixer busy tests bit 0 only; finite IRQ fixtures act at the actual loop head.
 * Active path sends D0, mixes first buffer, unmasks PIC IRQ, then PUSHF/CALL FAR
 * enters the real IRET handler without clearing live IF/TF. AX/BX/DX change;
 * CX/SI/DI/BP/segments survive. Flags follow the gate/CMP or PIC AND (AF
 * undefined after TEST/AND). Mixer return-unit bugs are inherited unchanged. */
/* TRANSLATES SOUND:PrimeSampleDmaPlayback */
EXPORT int c_PrimeSampleDmaPlayback(Regs *r) {
    if(!logic(r,rd16(r->cs,S(SoundDeviceBits))&2u,16)) return UGH_OK;
    unsigned budget=1000000;
    for(;;) {
        if(!budget--) return UGH_BUDGET;
        int status=platform_service_point_at(SERVICE_TIMER_WAIT,r->cs,S(loc_1EA3),r);
        if(status) return status;
        if(!logic(r,rd16(r->cs,S(SampleMixerBusy))&1u,16)) break;
    }
    uint16_t count=rd16(r->cs,S(ActiveSampleVoiceCount)); sub16(r,count,0,0);
    if((int16_t)count<=0) return UGH_OK;
    set_al(r,0xd0);
    int status=call_sound(r,S(WriteSoundBlasterDsp),(uint16_t)(S(PrimeSampleDmaPlayback)+0x26));
    if(status) return status;
    r->dx=rd16(r->cs,S(DmaMixBufferOneOffset)); r->bx=0x400;
    status=call_sound(r,S(MixSampleVoicePairs),(uint16_t)(S(PrimeSampleDmaPlayback)+0x32));
    if(status) return status;
    wr16(r->cs,S(DmaMixBufferOneCount),r->ax); wr8(r->cs,S(DmaMixBufferSelect),1);
    set_al(r,(uint8_t)platform_in(0x21,1)); set_ah(r,(uint8_t)~rd8(r->cs,S(DspPicIrqMask)));
    set_al(r,(uint8_t)logic(r,(uint8_t)r->ax&(r->ax>>8),8));
    platform_out(0x21,1,(uint8_t)r->ax);
    push_word(r,r->flags); push_word(r,r->cs);
    push_word(r,(uint16_t)(S(PrimeSampleDmaPlayback)+0x5d));
    return ugh_dispatch_interrupt(r->cs,S(HandleSampleDmaInterrupt),r);
}
