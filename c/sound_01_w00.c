#include "platform.h"

/* All entries are far-returning except the IRET probe handler. No cdecl
 * arguments. CS owns mutable sound state; DS/ES are never implicitly SOUND.
 * SS/SP and unmentioned registers, IF and DF are preserved. Arithmetic flags
 * are outputs only where defined below. No native object owns game state. */

/* AX/CX preserved. AL and the LOW byte of the calibration word are inputs.
 * MUL defines CF/OF; other arithmetic flags are undefined. LOOP has no device
 * service point; count zero executes 65536 iterations, otherwise product
 * iterations, leaving the restored CX and MUL flags. No host clock is used. */
/* TRANSLATES SOUND:DelaySoundIo */
EXPORT int c_DelaySoundIo(Regs *r) {
    uint16_t product=(uint16_t)((uint8_t)r->ax * rd8(r->cs,S(SoundIoDelayMultiplier)));
    flag(r,CF,product>255); flag(r,OF,product>255);
    uint16_t remaining=product;
    do { remaining=(uint16_t)(remaining-1); } while(remaining);
    return UGH_OK;
}

/* AL contains an already-fetched opcode; ES:DI supplies its payload byte.
 * DI advances with word wrap. DX and AX preserved; arithmetic flags come from
 * the high-word ADC. The left shift discards high delta bits BEFORE addition. */
/* TRANSLATES SOUND:HandleMainAdlxLongWait */
EXPORT int c_HandleMainAdlxLongWait(Regs *r) {
    uint16_t delta=(uint16_t)((((r->ax&15u)<<8)|rd8(r->es,r->di))<<7);
    r->di=(uint16_t)(r->di+1);
    uint16_t low=add16(r,rd16(r->cs,S(MainAdlxDeadlineLow)),delta,0);
    wr16(r->cs,S(MainAdlxDeadlineLow),low);
    uint16_t high=add16(r,rd16(r->cs,S(MainAdlxDeadlineHigh)),0,r->flags&CF);
    wr16(r->cs,S(MainAdlxDeadlineHigh),high);
    wr16(r->cs,S(MainAdlxCursor),r->di);
    return UGH_OK;
}

/* AX becomes AX&7Fh; DI already points past the opcode. Flags = high ADC. */
/* TRANSLATES SOUND:HandleMainAdlxShortWait */
EXPORT int c_HandleMainAdlxShortWait(Regs *r) {
    r->ax &= 127u;
    uint16_t low=add16(r,rd16(r->cs,S(MainAdlxDeadlineLow)),r->ax,0);
    wr16(r->cs,S(MainAdlxDeadlineLow),low);
    uint16_t high=add16(r,rd16(r->cs,S(MainAdlxDeadlineHigh)),0,r->flags&CF);
    wr16(r->cs,S(MainAdlxDeadlineHigh),high);
    wr16(r->cs,S(MainAdlxCursor),r->di);
    return UGH_OK;
}

/* AL opcode, ES:DI byte; record offset is reloaded from CS. BX returns record,
 * AX returns low16(product>>8); DX preserved. Long wait retains all 24 product
 * bits after shifting; deadline stores occur low then high, then cursor. */
/* TRANSLATES SOUND:HandleEffectAdlxLongWait */
EXPORT int c_HandleEffectAdlxLongWait(Regs *r) {
    uint16_t delta=(uint16_t)((((r->ax&15u)<<8)|rd8(r->es,r->di))<<7);
    r->di=(uint16_t)(r->di+1);
    r->bx=rd16(r->cs,S(CurrentAdlxRecordOffset));
    uint32_t scaled=((uint32_t)delta*rd16(r->cs,(uint16_t)(r->bx+0x26)))>>8;
    r->ax=(uint16_t)scaled;
    uint16_t low=add16(r,rd16(r->cs,(uint16_t)(r->bx+0x1e)),r->ax,0);
    wr16(r->cs,(uint16_t)(r->bx+0x1e),low);
    uint16_t high=add16(r,rd16(r->cs,(uint16_t)(r->bx+0x20)),(uint16_t)(scaled>>16),r->flags&CF);
    wr16(r->cs,(uint16_t)(r->bx+0x20),high);
    wr16(r->cs,(uint16_t)(r->bx+0x10),r->di);
    return UGH_OK;
}

/* AX&7Fh times unsigned word Q8 scale; BX returns record, AX returns scaled
 * low word, DX preserved; arithmetic flags = high-word ADC. */
/* TRANSLATES SOUND:HandleEffectAdlxShortWait */
EXPORT int c_HandleEffectAdlxShortWait(Regs *r) {
    r->bx=rd16(r->cs,S(CurrentAdlxRecordOffset));
    r->ax=(uint16_t)(((uint32_t)(r->ax&127u)*rd16(r->cs,(uint16_t)(r->bx+0x26)))>>8);
    uint16_t low=add16(r,rd16(r->cs,(uint16_t)(r->bx+0x1e)),r->ax,0);
    wr16(r->cs,(uint16_t)(r->bx+0x1e),low);
    uint16_t high=add16(r,rd16(r->cs,(uint16_t)(r->bx+0x20)),0,r->flags&CF);
    wr16(r->cs,(uint16_t)(r->bx+0x20),high);
    wr16(r->cs,(uint16_t)(r->bx+0x10),r->di);
    return UGH_OK;
}

/* AX voice index is unchecked; AX returns low16(index*42). BX/DX preserved.
 * CF/OF report unsigned multiply overflow. Address arithmetic wraps to 16 bits. */
/* TRANSLATES SOUND:ResetSampleVoiceCursor */
EXPORT int c_ResetSampleVoiceCursor(Regs *r) {
    uint32_t product=(uint32_t)r->ax*42u;
    r->ax=(uint16_t)product;
    flag(r,CF,product>65535u); flag(r,OF,product>65535u);
    wr16(r->cs,(uint16_t)(S(SampleVoicePairCursor)+r->ax),0);
    return UGH_OK;
}

/* Inline hardware address calculation. buffer/header positions are derived
 * from generated symbols; 400h is transfer length, 40Ah is buffer/header stride.
 * Equality at a page end selects the fallback, matching ADD's carry test. */
static void locate_buffer(Regs *r, uint16_t page, uint16_t address,
                          uint16_t offset, uint16_t buffer, uint16_t skip) {
    uint16_t segment=SOUND_SEG;
    uint16_t page_byte=(uint16_t)(segment>>12);
    r->cx=segment;
    r->ax=(uint16_t)(segment<<4);
    uint32_t start=(uint32_t)r->ax+buffer;
    r->ax=(uint16_t)start;
    page_byte=(uint8_t)(page_byte+(start>65535u));
    wr16(r->cs,address,r->ax); wr16(r->cs,offset,buffer);
    wr8(r->cs,page,(uint8_t)page_byte);
    uint16_t before=r->ax;
    r->ax=add16(r,r->ax,0x400,0);
    if(r->flags&CF) {
        /* SUB restores the start; the original adds the fallback displacement
         * from that value, and carries into the physical page byte. */
        uint32_t fallback=(uint32_t)before+skip;
        r->ax=(uint16_t)fallback;
        uint8_t old=(uint8_t)page_byte, carry=(fallback>65535u);
        uint8_t v=(uint8_t)(old+carry);
        flag(r,CF,(unsigned)old+carry>255u);
        flag(r,OF,old==127 && carry); flag(r,AF,((old^carry^v)&16u)!=0);
        szp(r,v,8); page_byte=v;
        wr8(r->cs,page,v); wr16(r->cs,address,r->ax);
        wr16(r->cs,offset,(uint16_t)(S(DmaMixBufferTwoOffset)+2+0x40a));
    }
    r->cx=(uint16_t)((r->cx&255u)|(page_byte<<8));
}

/* No register inputs. AX/CX clobbered, all other registers preserved.
 * Flags are from the last buffer's final ADD (or fallback page ADC).
 * SOUND_SEG is the relocated immediate, not the incoming DS or CS value. */
/* TRANSLATES SOUND:LocateDmaMixBuffers */
EXPORT int c_LocateDmaMixBuffers(Regs *r) {
    locate_buffer(r,S(DmaMixBufferOnePage),S(DmaMixBufferOneAddress),S(DmaMixBufferOneOffset),
                  (uint16_t)(S(DmaMixBufferOneOffset)+2),0x814);
    locate_buffer(r,S(DmaMixBufferTwoPage),S(DmaMixBufferTwoAddress),S(DmaMixBufferTwoOffset),
                  (uint16_t)(S(DmaMixBufferTwoOffset)+2),0x40a);
    return UGH_OK;
}

/* Signed IMUL high byte followed by CBW, expressed without a signed C shift.
 * The volume byte is logically shifted first, so the multiplier is 0..127. */
static uint16_t scaled_sample(uint8_t sample, uint8_t volume) {
    int16_t product=(int16_t)((int8_t)sample * (int16_t)(volume>>1));
    return (uint16_t)(int16_t)(int8_t)((uint16_t)product>>8);
}

/* BX=request bytes, DX=CS destination; no stack args. PUSHA+DS preserve every
 * register except AX. No-active flags = CMP count,0; otherwise flags = final
 * SUB original_BX,remaining_pairs. Signed JLE governs repeats and active count.
 * Writes busy/pairs/sums, voice cursors/repeats/mask/count and output bytes.
 * No calls/ports. Unsupported IDIV faults return UGH_UNSUPPORTED, never success.
 * Zero/odd requests enter once. Repeat resets a cursor but contributes no pair.
 * Early return is original bytes minus remaining PAIRS, an original unit bug. */
/* TRANSLATES SOUND:MixSampleVoicePairs */
EXPORT int c_MixSampleVoicePairs(Regs *r) {
    r->ax=0;
    uint16_t count=rd16(r->cs,S(ActiveSampleVoiceCount));
    sub16(r,count,0,0);
    if(!count) return UGH_OK;
    wr16(r->cs,S(SampleMixerBusy),1);
    wr16(r->cs,S(SampleMixPairsRemaining),r->bx>>1);
    uint16_t destination=r->dx;
    wr16(r->cs,S(SampleMixFirstSum),0); wr16(r->cs,S(SampleMixSecondSum),0);
    for(unsigned budget=0;budget<65536u;budget++) {
        uint16_t voice=0;
        for(unsigned bit=1;bit<256;bit<<=1,voice=(uint16_t)(voice+42)) {
            if(!(rd8(r->cs,S(ActiveSampleVoiceMask))&bit)) continue;
            uint16_t base=rd16(r->cs,(uint16_t)(S(SampleVoiceDataPointer)+voice));
            uint16_t bank=rd16(r->cs,(uint16_t)(S(SampleVoiceDataPointer)+voice+2));
            uint16_t cursor=rd16(r->cs,(uint16_t)(S(SampleVoicePairCursor)+voice));
            uint16_t sample_offset=(uint16_t)(((uint32_t)cursor*
                rd16(r->cs,(uint16_t)(S(SampleVoiceStepQ8)+voice)))>>8);
            if(sample_offset>=rd16(r->cs,(uint16_t)(S(SampleVoiceByteLength)+voice))) {
                if(!(rd16(r->cs,(uint16_t)(S(SampleVoiceFlags)+voice))&2)) {
                    uint16_t old=rd16(r->cs,(uint16_t)(S(SampleVoiceRepeatCount)+voice));
                    wr16(r->cs,(uint16_t)(S(SampleVoiceRepeatCount)+voice),(uint16_t)(old-1));
                    if((int16_t)old<=1) {
                        wr8(r->cs,S(ActiveSampleVoiceMask),(uint8_t)(rd8(r->cs,S(ActiveSampleVoiceMask))^bit));
                        old=rd16(r->cs,S(ActiveSampleVoiceCount));
                        wr16(r->cs,S(ActiveSampleVoiceCount),(uint16_t)(old-1));
                        if((int16_t)old<=1) goto finished;
                        continue;
                    }
                }
                wr16(r->cs,(uint16_t)(S(SampleVoicePairCursor)+voice),0);
                continue;
            }
            uint16_t samples=rd16(bank,(uint16_t)(base+sample_offset));
            uint8_t volume=rd8(r->cs,(uint16_t)(S(SampleVoiceVolume)+voice));
            wr16(r->cs,S(SampleMixFirstSum),(uint16_t)(rd16(r->cs,S(SampleMixFirstSum))+
                scaled_sample((uint8_t)samples,volume)));
            wr16(r->cs,S(SampleMixSecondSum),(uint16_t)(rd16(r->cs,S(SampleMixSecondSum))+
                scaled_sample((uint8_t)(samples>>8),volume)));
            /* Reload cursor: sample/output aliases must not be normalized away. */
            cursor=rd16(r->cs,(uint16_t)(S(SampleVoicePairCursor)+voice));
            wr16(r->cs,(uint16_t)(S(SampleVoicePairCursor)+voice),(uint16_t)(cursor+1));
        }
        int16_t divisor=(int16_t)rd16(r->cs,S(ActiveSampleVoiceCount));
        if(!divisor) return UGH_UNSUPPORTED;
        int32_t quotient=(int16_t)rd16(r->cs,S(SampleMixFirstSum))/(int32_t)divisor;
        if(quotient>32767 || quotient< -32768) return UGH_UNSUPPORTED;
        wr8(r->cs,destination,(uint8_t)(quotient+127)); destination=(uint16_t)(destination+1);
        divisor=(int16_t)rd16(r->cs,S(ActiveSampleVoiceCount));
        if(!divisor) return UGH_UNSUPPORTED;
        quotient=(int16_t)rd16(r->cs,S(SampleMixSecondSum))/(int32_t)divisor;
        if(quotient>32767 || quotient< -32768) return UGH_UNSUPPORTED;
        wr8(r->cs,destination,(uint8_t)(quotient+127)); destination=(uint16_t)(destination+1);
        uint16_t remaining=(uint16_t)(rd16(r->cs,S(SampleMixPairsRemaining))-1);
        wr16(r->cs,S(SampleMixPairsRemaining),remaining);
        if((int16_t)remaining<=0) goto finished;
        wr16(r->cs,S(SampleMixFirstSum),0); wr16(r->cs,S(SampleMixSecondSum),0);
    }
    return UGH_BUDGET;
finished:
    wr16(r->cs,S(SampleMixerBusy),0);
    r->ax=sub16(r,r->bx,rd16(r->cs,S(SampleMixPairsRemaining)),0);
    return UGH_OK;
}

/* IRQ probe: AL clobbered to 20h (AH preserved), CS probe byte set to one;
 * all other registers preserved. PIC EOI is the sole ordered device event.
 * IRET flag restoration belongs to the harness, including IF/DF. */
/* TRANSLATES SOUND:HandleDspProbeInterrupt */
EXPORT int c_HandleDspProbeInterrupt(Regs *r) {
    set_al(r,0x20); platform_out(0x20,1,0x20);
    wr8(r->cs,S(DspProbeIrqSeen),1);
    return UGH_OK;
}
/* IRET entries. DOS vector service owns only IVT storage. The interrupted
 * AX/CX changes are deliberately visible to the calibration polling loop. */
/* TRANSLATES SOUND:BeginSoundDelayMeasurement */
EXPORT int c_BeginSoundDelayMeasurement(Regs *r) {
    uint16_t ds=r->ds,dx=r->dx; set_al(r,0x20); platform_out(0x20,1,0x20);
    r->ax=SOUND_SEG; r->ds=r->ax; r->dx=S(FinishSoundDelayMeasurement); r->ax=0x2508;
    int status=platform_interrupt(0x21,r); r->ds=ds; r->dx=dx;
    set_ah(r,1); set_al(r,(uint8_t)logic(r,0,8)); return status;
}
/* TRANSLATES SOUND:FinishSoundDelayMeasurement */
EXPORT int c_FinishSoundDelayMeasurement(Regs *r) {
    uint16_t ds=r->ds,dx=r->dx; set_al(r,0x20); platform_out(0x20,1,0x20);
    r->dx=rd16(r->cs,S(PreviousCalibrationTimerVector)); r->ds=rd16(r->cs,S(PreviousCalibrationTimerSegment));
    r->ax=0x2508; int status=platform_interrupt(0x21,r);
    wr16(r->cs,S(CalibrationLoopRemainder),r->cx); r->dx=dx;
    wr16(r->cs,S(SoundIoDelayMultiplier),r->dx); r->cx=1; set_al(r,1); r->ds=ds; return status;
}
/* Far, preserves all registers/segments. Flags follow final CMP AL,1.
 * IRQs occur only at the two named original polling instructions. DX starts
 * at Begin's offset, retaining the original measured-delay offset bias. */
/* TRANSLATES SOUND:CalibrateSoundDelay */
EXPORT int c_CalibrateSoundDelay(Regs *r) {
    Regs saved=*r; r->sp=(uint16_t)(r->sp-12);
    r->ax=0x3508; int status=platform_interrupt(0x21,r); if(status) return status;
    wr16(r->cs,S(PreviousCalibrationTimerVector),r->bx); wr16(r->cs,S(PreviousCalibrationTimerSegment),r->es);
    r->ax=SOUND_SEG; r->ds=r->ax; r->dx=S(BeginSoundDelayMeasurement); r->ax=0x2508;
    status=platform_interrupt(0x21,r); if(status) return status; r->ax=logic(r,0,16);
    unsigned budget=1000000;
    do {
        if(!budget--) return UGH_BUDGET;
        status=platform_service_point_at(SERVICE_TIMER_WAIT,r->cs,S(loc_1163),r); if(status) return status;
        sub16(r,r->ax>>8,1,0);
    } while((r->ax>>8)!=1);
    do {
        r->cx=0;
        do {
            if(!budget--) return UGH_BUDGET;
            status=platform_service_point_at(SERVICE_TIMER_WAIT,r->cs,S(loc_116B),r); if(status) return status;
            r->cx=(uint16_t)(r->cx-1);
        } while(r->cx);
        uint16_t cf=r->flags&CF; r->dx=add16(r,r->dx,1,0); flag(r,CF,cf);
        sub16(r,(uint8_t)r->ax,1,0);
    } while((uint8_t)r->ax!=1);
    uint16_t flags=r->flags; *r=saved; r->flags=flags; return UGH_OK;
}
/* Far; original timeout still writes the command after 65536 busy reads.
 * Preserves AX/CX/DX, flags from the last TEST AL,80. */
/* TRANSLATES SOUND:WriteSoundBlasterDsp */
EXPORT int c_WriteSoundBlasterDsp(Regs *r) {
    uint16_t ax=r->ax,cx=r->cx,dx=r->dx;
    set_ah(r,(uint8_t)r->ax); r->dx=add16(r,rd16(r->cs,S(DspBasePort)),12,0); r->cx=logic(r,0,16);
    do {
        set_al(r,(uint8_t)platform_in(r->dx,1)); if(ugh_devices.error) return UGH_UNSUPPORTED;
        logic(r,(uint8_t)r->ax&0x80,8); r->cx=(uint16_t)(r->cx-1);
    } while(r->cx && (r->ax&0x80));
    set_al(r,(uint8_t)(r->ax>>8)); platform_out(r->dx,1,(uint8_t)r->ax);
    r->ax=ax; r->cx=cx; r->dx=dx; return UGH_OK;
}
/* Far-returning interpreters; table tails retain the original caller's frame.
 * Available wait handlers terminate; other handlers may tail back here. */
static int adlx_dispatch(Regs *r,uint16_t table) {
    set_al(r,rd8(r->es,r->di));
    uint16_t cf=r->flags&CF; r->di=add16(r,r->di,1,0); flag(r,CF,cf);
    set_ah(r,(uint8_t)logic(r,0,8)); r->bx=r->ax;
    r->bx=logic(r,(r->bx>>3)&0xfffe,16); r->bx=add16(r,r->bx,table,0);
    return ugh_dispatch(r->cs,rd16(r->cs,r->bx),r);
}
/* TRANSLATES SOUND:RunMainAdlxEvents */
EXPORT int c_RunMainAdlxEvents(Regs *r) { return adlx_dispatch(r,S(MainAdlxDispatchTable)); }
/* TRANSLATES SOUND:RunEffectAdlxEvents */
EXPORT int c_RunEffectAdlxEvents(Regs *r) { return adlx_dispatch(r,S(EffectAdlxDispatchTable)); }
