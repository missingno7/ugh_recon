#include "platform.h"

/* All entries RETF. CS owns sound state; ES:DI is the event stream, DS is
 * dynamic. No native storage holds game state. Only specified arithmetic
 * flags are contractual; IF/DF and preserved registers always flow through.
 * Stack arguments are far cdecl words, read before the original ENTER/save
 * area is reserved. Calls use real far frames and original return addresses. */
static void push(Regs *r,uint16_t v) {
    r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v);
}
static int call(Regs *r,uint16_t seg,uint16_t off,uint16_t ret) {
    push(r,r->cs); push(r,ret);
    int rc=ugh_dispatch(seg,off,r); r->sp=(uint16_t)(r->sp+4); return rc;
}
static int args_call(Regs *r,uint16_t off,uint16_t ret,unsigned n,
                     uint16_t a,uint16_t b,uint16_t c) {
    if(n>2) push(r,c);
    if(n>1) push(r,b);
    if(n) push(r,a);
    int rc=call(r,r->cs,off,ret); r->sp=(uint16_t)(r->sp+2*n); return rc;
}
static uint16_t inc(Regs *r,uint16_t v) {
    uint16_t cf=r->flags&CF; v=add16(r,v,1,0); flag(r,CF,cf); return v;
}
static void al(Regs *r,uint8_t v) { set_al(r,v); }
static void bl(Regs *r,uint8_t v) { r->bx=(uint16_t)((r->bx&0xff00)|v); }
static void bh(Regs *r,uint8_t v) { r->bx=(uint16_t)((r->bx&255)|((uint16_t)v<<8)); }
static int emit(Regs *r,uint16_t value) { r->bx=value; return c_WriteAdlibRegister(r); }
static int delay(Regs *r,uint8_t value) { al(r,value); return c_DelaySoundIo(r); }

/* BH=register, BL=value. AX/DX/CX and all segments survive. CF/OF from
 * last unsigned byte MUL in DelaySoundIo; no input flags, IF/DF preserved. */
/* TRANSLATES SOUND:WriteAdlibRegister */
EXPORT int c_WriteAdlibRegister(Regs *r) {
    uint16_t ax=r->ax,dx=r->dx;
    r->dx=0x388; al(r,(uint8_t)(r->bx>>8)); platform_out(r->dx,1,(uint8_t)r->ax);
    r->ax=1; c_DelaySoundIo(r);
    r->dx=0x389; al(r,(uint8_t)r->bx); platform_out(r->dx,1,(uint8_t)r->ax);
    r->ax=4; c_DelaySoundIo(r); r->ax=ax; r->dx=dx; return UGH_OK;
}

/* channel,volume low bytes. Preserves all registers/segments. Live path
 * writes byte volume and carrier level, plus modulator iff WORD flags&1.
 * Two unsigned byte MULs take high bytes successively; no saturation. */
/* TRANSLATES SOUND:SetAdlibChannelVolume */
EXPORT int c_SetAdlibChannelVolume(Regs *r) {
    uint8_t channel=(uint8_t)arg16(r,0),volume=(uint8_t)arg16(r,2);
    Regs save=*r;
    if(channel<9) {
        uint16_t i=(uint16_t)(channel*20);
        if((rd16(r->cs,S(MainAdlxPlaying))&1) && rd16(r->cs,S(CurrentAdlxSlot))>=12 &&
           (rd16(r->cs,S(ReservedAdlibChannelCount))&15) &&
           channel>=(uint8_t)(9-rd8(r->cs,S(ReservedAdlibChannelCount)))) {
            wr8(r->cs,(uint16_t)(S(DisplacedAdlibVolume)+i),volume);
        } else {
            wr8(r->cs,(uint16_t)(S(AdlibChannelVolume)+i),volume);
            uint8_t gain=rd8(r->cs,(uint16_t)(S(AdlibChannelGain)+i));
            uint8_t op=rd8(r->cs,(uint16_t)(S(AdlibOperatorOffsets)+channel));
            uint8_t level=rd8(r->cs,(uint16_t)(S(AdlibCarrierLevel)+i));
            uint8_t scaled=(uint8_t)(63-(((63-(level&63))*gain>>8)*volume>>8));
            emit(r,(uint16_t)((uint8_t)(op+0x43)*256u+(scaled|(level&0xc0))));
            if(rd16(r->cs,(uint16_t)(S(AdlibConnectionFlags)+i))&1) {
                level=rd8(r->cs,(uint16_t)(S(AdlibModulatorLevel)+i));
                scaled=(uint8_t)(63-(((63-(level&63))*gain>>8)*volume>>8));
                emit(r,(uint16_t)((uint8_t)(op+0x40)*256u+(scaled|(level&0xc0))));
            }
        }
    }
    uint16_t flags=r->flags; *r=save; r->flags=flags; return UGH_OK;
}

/* channel low byte; all registers/segments survive. Clears saved HIGH byte
 * bit 5 (main displaced key-off below instead clears word bit 5). */
/* TRANSLATES SOUND:KeyOffAdlibChannel */
EXPORT int c_KeyOffAdlibChannel(Regs *r) {
    uint8_t ch=(uint8_t)arg16(r,0); uint16_t ax=r->ax,bx=r->bx,dx=r->dx;
    if(ch<9) {
        uint16_t p=(uint16_t)(S(AdlibKeyControlByte)+ch*20);
        uint8_t value=rd8(r->cs,p)&0xdf; wr8(r->cs,p,value);
        platform_out(0x388,1,(uint8_t)(ch+0xb0)); r->ax=1; c_DelaySoundIo(r);
        platform_out(0x389,1,value); r->ax=2; c_DelaySoundIo(r);
    }
    r->ax=ax; r->bx=bx; r->dx=dx; return UGH_OK;
}

/* channel low byte,packed word. Preserves general/segment registers.
 * Valid channel forces IF=1 even if entered with IF=0; invalid preserves IF. */
/* TRANSLATES SOUND:SetAdlibFrequency */
EXPORT int c_SetAdlibFrequency(Regs *r) {
    uint8_t ch=(uint8_t)arg16(r,0); uint16_t value=arg16(r,2),ax=r->ax;
    if(ch<9) {
        wr16(r->cs,(uint16_t)(S(AdlibPackedFrequency)+ch*20),value); flag(r,IF,0);
        platform_out(0x388,1,(uint8_t)(ch+0xa0)); r->ax=1; c_DelaySoundIo(r);
        platform_out(0x389,1,(uint8_t)value); r->ax=3; c_DelaySoundIo(r);
        platform_out(0x388,1,(uint8_t)(ch+0xb0)); r->ax=1; c_DelaySoundIo(r);
        platform_out(0x389,1,value>>8); flag(r,IF,1); r->ax=2; c_DelaySoundIo(r);
    }
    r->ax=ax; return UGH_OK;
}

/* channel,gain low bytes; CX/DX/SI/BP preserved, AX/BX scratch. Routing
 * tests slot>=12 and reserved low nibble, WITHOUT MainAdlxPlaying. */
/* TRANSLATES SOUND:SetAdlibChannelGain */
EXPORT int c_SetAdlibChannelGain(Regs *r) {
    uint16_t channel=arg16(r,0),gain=arg16(r,2),sp=r->sp;
    uint8_t ch=(uint8_t)channel;
    if(ch>=9) return UGH_OK;
    r->ax=(uint16_t)(ch*20);
    if(rd16(r->cs,S(CurrentAdlxSlot))>=12 && (rd16(r->cs,S(ReservedAdlibChannelCount))&15)) {
        bl(r,(uint8_t)(9-rd8(r->cs,S(ReservedAdlibChannelCount))));
        if(ch>=(uint8_t)r->bx) {
            wr8(r->cs,(uint16_t)(S(DisplacedAdlibGain)+r->ax),(uint8_t)gain); return UGH_OK;
        }
    }
    wr8(r->cs,(uint16_t)(S(AdlibChannelGain)+r->ax),(uint8_t)gain);
    uint16_t volume=rd16(r->cs,(uint16_t)(S(AdlibChannelVolume)+r->ax));
    r->sp=(uint16_t)(sp-8);
    int rc=args_call(r,S(SetAdlibChannelVolume),(uint16_t)(S(SetAdlibChannelGain)+0x5a),2,
                     (uint16_t)((r->cx&0xff00)|ch),volume,0);
    r->sp=sp; return rc;
}

/* channel low byte, far source offset/segment. Preserves CX/DX/SI/DI/DS/ES/BP;
 * AX/BX scratch. Valid clears DF. Forward byte copy is deliberately sequential
 * for aliases, copies 12 bytes despite event payload length 11. Displaced
 * routing tests slot==12, not >=12 and does not test MainAdlxPlaying. */
/* TRANSLATES SOUND:LoadAdlibInstrument */
EXPORT int c_LoadAdlibInstrument(Regs *r) {
    uint16_t channel=arg16(r,0),source=arg16(r,2),bank=arg16(r,4),sp=r->sp;
    uint8_t ch=(uint8_t)channel;
    if(ch>=9) return UGH_OK;
    uint16_t i=(uint16_t)(ch*20),dest;
    r->ax=i;
    int displaced=rd16(r->cs,S(CurrentAdlxSlot))==12 &&
        (rd16(r->cs,S(ReservedAdlibChannelCount))&15) &&
        ch>=(uint8_t)(9-rd8(r->cs,S(ReservedAdlibChannelCount)));
    dest=(uint16_t)((displaced?S(SavedAdlibVoiceStates):S(AdlibVoiceStates))+i);
    if(displaced) al(r,(uint8_t)(9-rd8(r->cs,S(ReservedAdlibChannelCount))));
    flag(r,DF,0);
    for(unsigned k=0;k<12;k++) wr8(r->cs,(uint16_t)(dest+k),rd8(bank,(uint16_t)(source+k)));
    if(displaced) return UGH_OK;
    uint8_t op=rd8(r->cs,(uint16_t)(S(AdlibOperatorOffsets)+ch));
    /* Registers follow the source reads after copying, including overlap. */
    for(unsigned k=0;k<5;k++) {
        uint8_t reg=(uint8_t)(op+(k==4?0xe0:0x20+k*0x20));
        uint8_t value=rd8(bank,(uint16_t)(source+k));
        if(k==1 && (rd8(bank,(uint16_t)(source+k+9))&1)) value|=63;
        emit(r,(uint16_t)(reg*256u+value));
    }
    op=(uint8_t)(op+3);
    for(unsigned k=0;k<4;k++) {
        uint8_t value=rd8(bank,(uint16_t)(source+5+k)); if(k==1) value|=63;
        emit(r,(uint16_t)((uint8_t)(op+0x20+k*0x20)*256u+value));
    }
    emit(r,0x120);
    emit(r,(uint16_t)((uint8_t)(op+0xe0)*256u+rd8(bank,(uint16_t)(source+9))));
    emit(r,(uint16_t)((uint8_t)(ch+0xc0)*256u+rd8(bank,(uint16_t)(source+10))));
    r->ax=rd16(r->cs,S(CurrentAdlxSlot)); r->bx=i;
    wr16(r->cs,(uint16_t)(S(AdlibChannelOwnerSlot)+i),r->ax);
    uint16_t volume=rd16(r->cs,(uint16_t)(S(AdlibChannelVolume)+i));
    r->sp=(uint16_t)(sp-14);
    int rc=args_call(r,S(SetAdlibChannelVolume),(uint16_t)(S(LoadAdlibInstrument)+0x12f),2,channel,volume,0);
    r->sp=sp; return rc;
}

/* No stack args. Cancellation calls TIMER remover, whose DS output survives.
 * Schedule register ABI sets callback address and CX:BX=1:D1EB, saves handle.
 * The existing timer adapters preserve FLAGS; no installed/valid-handle checks. */
/* TRANSLATES SOUND:CancelMusicFade */
EXPORT int c_CancelMusicFade(Regs *r) {
    if(rd16(r->cs,S(MusicFadeScheduled))&1) {
        r->ax=rd16(r->cs,S(MusicFadeTimerHandle));
        int rc=call(r,TIMER_SEG,T(RemoveTimerCallback),(uint16_t)(S(CancelMusicFade)+0x15)); if(rc) return rc;
        wr16(r->cs,S(MusicFadeScheduled),0);
    }
    return UGH_OK;
}
/* TRANSLATES SOUND:ScheduleMusicFade */
EXPORT int c_ScheduleMusicFade(Regs *r) {
    if(!(rd16(r->cs,S(MusicFadeScheduled))&1)) {
        r->bx=0xd1eb; r->cx=1; r->ax=S(AdvanceMusicFade); r->dx=SOUND_SEG;
        int rc=call(r,TIMER_SEG,T(RegisterTimerCallback),(uint16_t)(S(ScheduleMusicFade)+0x1d)); if(rc) return rc;
        wr16(r->cs,S(MusicFadeTimerHandle),r->ax); wr16(r->cs,S(MusicFadeScheduled),1);
    }
    return UGH_OK;
}

/* AX/BX/CX/DX preserved, DS follows remover/C API. Unsigned step comparison
 * precedes SIGNED IMUL/IDIV; wrap and divide faults are retained. C API is a
 * peer package: missing adapter fails, never returns invented success. */
/* TRANSLATES SOUND:AdvanceMusicFade */
EXPORT int c_AdvanceMusicFade(Regs *r) {
    Regs save=*r; r->sp=(uint16_t)(r->sp-8);
    r->dx=inc(r,rd16(r->cs,S(MusicFadeStep))); wr16(r->cs,S(MusicFadeStep),r->dx);
    r->bx=rd16(r->cs,S(MusicFadeDuration)); int rc;
    if(r->dx>r->bx) {
        r->ax=rd16(r->cs,S(MusicFadeTimerHandle));
        rc=call(r,TIMER_SEG,T(RemoveTimerCallback),(uint16_t)(S(AdvanceMusicFade)+0x43));
        if(!rc) wr16(r->cs,S(MusicFadeScheduled),0);
    } else {
        r->cx=rd16(r->cs,S(MusicFadeStartVolume));
        int32_t product=(int16_t)(rd16(r->cs,S(MusicFadeTargetVolume))-r->cx)*(int32_t)(int16_t)r->dx;
        int16_t divisor=(int16_t)r->bx;
        if(!divisor || (product==INT32_MIN && divisor==-1)) return UGH_UNSUPPORTED;
        int32_t q=product/divisor; if(q< -32768 || q>32767) return UGH_UNSUPPORTED;
        r->dx=(uint16_t)(product%divisor); r->ax=(uint16_t)(q+r->cx);
        push(r,r->ax);
        rc=call(r,UGH_SEG_C,UGH_O_C_SetMusicTrackVolume,(uint16_t)(S(AdvanceMusicFade)+0x32));
        r->sp=(uint16_t)(r->sp+2);
    }
    r->ax=save.ax; r->bx=save.bx; r->cx=save.cx; r->dx=save.dx; r->sp=save.sp; return rc;
}

/* All event entries receive AL opcode already fetched and ES:DI payload.
 * They retain the incoming far frame through the table-dispatch tail.
 * Invalid frequency/instrument consumes no payload; gain always consumes one.
 * No bounds checks. Effective channel addition wraps at BYTE width. */
/* TRANSLATES SOUND:HandleMainAdlxNoOp */
EXPORT int c_HandleMainAdlxNoOp(Regs *r) { return c_RunMainAdlxEvents(r); }
/* TRANSLATES SOUND:HandleEffectAdlxNoOp */
EXPORT int c_HandleEffectAdlxNoOp(Regs *r) { return c_RunEffectAdlxEvents(r); }

/* TRANSLATES SOUND:HandleMainAdlxFrequency */
EXPORT int c_HandleMainAdlxFrequency(Regs *r) {
    al(r,(uint8_t)r->ax&15);
    if((uint8_t)r->ax<9) {
        uint16_t dx=r->dx,cx=r->cx,si=r->si,sp=r->sp;
        uint8_t ch=(uint8_t)r->ax;
        r->cx=(uint16_t)((r->cx&0xff00)|ch); r->ax=rd16(r->es,r->di); r->di=(uint16_t)(r->di+2);
        bl(r,(uint8_t)(9-rd8(r->cs,S(ReservedAdlibChannelCount))));
        int rc=0;
        if(ch>=(uint8_t)r->bx) {
            uint16_t value=r->ax; r->ax=(uint16_t)(ch*20); r->bx=r->ax;
            wr16(r->cs,(uint16_t)(S(DisplacedAdlibFrequency)+r->bx),value);
        } else {
            r->sp=(uint16_t)(sp-6);
            rc=args_call(r,S(SetAdlibFrequency),(uint16_t)(S(HandleMainAdlxFrequency)+0x3a),2,r->cx,r->ax,0);
        }
        r->dx=dx; r->cx=cx; r->si=si; r->sp=sp; if(rc) return rc;
    }
    return c_RunMainAdlxEvents(r);
}
/* TRANSLATES SOUND:HandleMainAdlxKeyOff */
EXPORT int c_HandleMainAdlxKeyOff(Regs *r) {
    al(r,(uint8_t)r->ax&15);
    if((uint8_t)r->ax<9) {
        bl(r,(uint8_t)(9-rd8(r->cs,S(ReservedAdlibChannelCount))));
        if((uint8_t)r->ax>=(uint8_t)r->bx) {
            bl(r,(uint8_t)r->ax); r->ax=(uint16_t)((uint8_t)r->bx*20); r->bx=r->ax;
            uint16_t p=(uint16_t)(S(DisplacedAdlibFrequency)+r->bx); wr16(r->cs,p,rd16(r->cs,p)&0xffdf);
        } else { int rc=args_call(r,S(KeyOffAdlibChannel),(uint16_t)(S(HandleMainAdlxKeyOff)+0x2e),1,r->ax,0,0); if(rc) return rc; }
    }
    return c_RunMainAdlxEvents(r);
}
/* TRANSLATES SOUND:HandleMainAdlxGain */
EXPORT int c_HandleMainAdlxGain(Regs *r) {
    al(r,(uint8_t)r->ax&15);
    if((uint8_t)r->ax<9) {
        bl(r,rd8(r->es,r->di));
        int rc=args_call(r,S(SetAdlibChannelGain),(uint16_t)(S(HandleMainAdlxGain)+0x12),2,r->ax,r->bx,0); if(rc) return rc;
    }
    r->di=inc(r,r->di); return c_RunMainAdlxEvents(r);
}
/* TRANSLATES SOUND:HandleMainAdlxInstrument */
EXPORT int c_HandleMainAdlxInstrument(Regs *r) {
    al(r,(uint8_t)r->ax&15);
    if((uint8_t)r->ax<9) {
        int rc=args_call(r,S(LoadAdlibInstrument),(uint16_t)(S(HandleMainAdlxInstrument)+0x10),3,r->ax,r->di,r->es); if(rc) return rc;
        r->di=(uint16_t)(r->di+11);
    }
    return c_RunMainAdlxEvents(r);
}
static void effect_channel(Regs *r) {
    al(r,(uint8_t)r->ax&15); r->bx=rd16(r->cs,S(CurrentAdlxRecordOffset));
    al(r,(uint8_t)((uint8_t)r->ax+rd8(r->cs,(uint16_t)(r->bx+0x24))));
}
/* TRANSLATES SOUND:HandleEffectAdlxFrequency */
EXPORT int c_HandleEffectAdlxFrequency(Regs *r) {
    effect_channel(r);
    if((uint8_t)r->ax<9) {
        int rc=args_call(r,S(SetAdlibFrequency),(uint16_t)(S(HandleEffectAdlxFrequency)+0x1a),2,r->ax,rd16(r->es,r->di),0); if(rc) return rc;
        r->di=(uint16_t)(r->di+2);
    }
    return c_RunEffectAdlxEvents(r);
}
/* TRANSLATES SOUND:HandleEffectAdlxKeyOff */
EXPORT int c_HandleEffectAdlxKeyOff(Regs *r) {
    effect_channel(r);
    if((uint8_t)r->ax<9) { int rc=args_call(r,S(KeyOffAdlibChannel),(uint16_t)(S(HandleEffectAdlxKeyOff)+0x17),1,r->ax,0,0); if(rc) return rc; }
    return c_RunEffectAdlxEvents(r);
}
/* TRANSLATES SOUND:HandleEffectAdlxGain */
EXPORT int c_HandleEffectAdlxGain(Regs *r) {
    effect_channel(r);
    if((uint8_t)r->ax<9) { int rc=args_call(r,S(SetAdlibChannelGain),(uint16_t)(S(HandleEffectAdlxGain)+0x1a),2,r->ax,rd16(r->es,r->di),0); if(rc) return rc; }
    r->di=inc(r,r->di); return c_RunEffectAdlxEvents(r);
}
/* Channel NINE stamps the owner but loader rejects it. Preserve this write. */
/* TRANSLATES SOUND:HandleEffectAdlxInstrument */
EXPORT int c_HandleEffectAdlxInstrument(Regs *r) {
    effect_channel(r);
    if((uint8_t)r->ax<=9) {
        r->bx=(uint16_t)((uint8_t)r->ax*20);
        wr16(r->cs,(uint16_t)(S(AdlibChannelOwnerSlot)+r->bx),rd16(r->cs,S(CurrentAdlxSlot)));
        int rc=args_call(r,S(LoadAdlibInstrument),(uint16_t)(S(HandleEffectAdlxInstrument)+0x2e),3,r->ax,r->di,r->es); if(rc) return rc;
        r->di=(uint16_t)(r->di+11);
    }
    return c_RunEffectAdlxEvents(r);
}

/* BE16 period. CX preserved, effect also DX. Timer setter preserves DS and
 * flags; outputs AX/BX flow into tail. Existing nonzero period gives Q8 ratio,
 * with full 32-bit numerator; divide-zero/quotient-overflow is unsupported. */
/* TRANSLATES SOUND:HandleMainAdlxTimerPeriod */
EXPORT int c_HandleMainAdlxTimerPeriod(Regs *r) {
    uint16_t cx=r->cx; r->sp=(uint16_t)(r->sp-2);
    uint16_t v=rd16(r->es,r->di); r->bx=(uint16_t)((v>>8)|(v<<8));
    wr16(r->cs,S(AdlxTimerPeriod),r->bx); r->ax=rd16(r->cs,S(AdlxPlaybackTimerHandle)); r->cx=0;
    int rc=call(r,TIMER_SEG,T(SetTimerCallbackInterval),(uint16_t)(S(HandleMainAdlxTimerPeriod)+0x16));
    r->di=inc(r,inc(r,r->di)); r->cx=cx; r->sp=(uint16_t)(r->sp+2);
    return rc?rc:c_RunMainAdlxEvents(r);
}
/* TRANSLATES SOUND:HandleEffectAdlxTimerPeriod */
EXPORT int c_HandleEffectAdlxTimerPeriod(Regs *r) {
    uint16_t cx=r->cx,dx=r->dx; r->sp=(uint16_t)(r->sp-4); int rc=0;
    if(!(rd16(r->cs,S(MainAdlxPlaying))&1) && !rd16(r->cs,S(AdlxTimerPeriod))) {
        uint16_t v=rd16(r->es,r->di); r->bx=(uint16_t)((v>>8)|(v<<8));
        wr16(r->cs,S(AdlxTimerPeriod),r->bx); r->ax=rd16(r->cs,S(AdlxPlaybackTimerHandle)); r->cx=0;
        rc=call(r,TIMER_SEG,T(SetTimerCallbackInterval),(uint16_t)(S(HandleEffectAdlxTimerPeriod)+0x2f));
    } else {
        r->bx=rd16(r->cs,S(AdlxTimerPeriod)); uint16_t v=rd16(r->es,r->di);
        uint32_t numerator=((uint32_t)(uint8_t)v<<16)|(v&0xff00);
        if(!r->bx || numerator/r->bx>65535) return UGH_UNSUPPORTED;
        r->ax=(uint16_t)(numerator/r->bx); r->bx=rd16(r->cs,S(CurrentAdlxRecordOffset));
        wr16(r->cs,(uint16_t)(r->bx+0x26),r->ax);
    }
    r->di=inc(r,inc(r,r->di)); r->cx=cx; r->dx=dx; r->sp=(uint16_t)(r->sp+4);
    return rc?rc:c_RunEffectAdlxEvents(r);
}

/* Common extension skip; AL==70 consumes one length byte plus TWO bytes.
 * Other extensions skip unsigned length; 77 handled separately, returns. */
static int extension(Regs *r,int effect) {
    set_ah(r,rd8(r->es,r->di)); r->di=inc(r,r->di); al(r,(uint8_t)r->ax&15);
    if((uint8_t)r->ax==0) r->di=(uint16_t)(r->di+2);
    else { al(r,(uint8_t)(r->ax>>8)); set_ah(r,0); r->di=(uint16_t)(r->di+r->ax); }
    return effect?c_RunEffectAdlxEvents(r):c_RunMainAdlxEvents(r);
}
/* Main end clears flags bit 0, not MainAdlxPlaying, on signed DEC<=0.
 * DEC overflow from 8000 to 7FFF still takes the expiration path (JG uses OF).
 * Repeat rebases cursor, deadline and origin, leaving the current ES:DI alone. */
/* TRANSLATES SOUND:HandleMainAdlxControl */
EXPORT int c_HandleMainAdlxControl(Regs *r) {
    if((uint8_t)r->ax!=0x77) return extension(r,0);
    if(!(rd16(r->cs,S(MainAdlxFlags))&2)) {
        uint16_t old=rd16(r->cs,S(MainAdlxRepeatCount));
        wr16(r->cs,S(MainAdlxRepeatCount),dec16(r,old));
        if((int16_t)old<=1) { wr16(r->cs,S(MainAdlxFlags),rd16(r->cs,S(MainAdlxFlags))&0xfffe); return UGH_OK; }
    }
    r->ax=rd16(r->cs,S(MainAdlxStartSegment)); wr16(r->cs,S(MainAdlxCursorSegment),r->ax);
    r->ax=rd16(r->cs,S(MainAdlxStartPointer)); wr16(r->cs,S(MainAdlxCursor),r->ax);
    r->ax=rd16(r->cs,S(AdlxTickCount)); wr16(r->cs,S(MainAdlxDeadlineLow),r->ax); wr16(r->cs,S(MainAdlxTimeOrigin),r->ax);
    r->ax=rd16(r->cs,S(AdlxTickHighWord)); wr16(r->cs,S(MainAdlxDeadlineHigh),r->ax); wr16(r->cs,S(MainAdlxTimeOriginHigh),r->ax);
    return UGH_OK;
}
/* Effect expiry calls peer C API; repeat resets cursor only, no clock rebase. */
/* TRANSLATES SOUND:HandleEffectAdlxControl */
EXPORT int c_HandleEffectAdlxControl(Regs *r) {
    if((uint8_t)r->ax!=0x77) return extension(r,1);
    r->bx=rd16(r->cs,S(CurrentAdlxRecordOffset));
    if(!(rd16(r->cs,(uint16_t)(r->bx+0x28))&2)) {
        uint16_t old=rd16(r->cs,(uint16_t)(r->bx+4)); wr16(r->cs,(uint16_t)(r->bx+4),dec16(r,old));
        if((int16_t)old<=1) {
            push(r,rd16(r->cs,S(CurrentAdlxSlot)));
            int rc=call(r,UGH_SEG_C,UGH_O_C_StopAdlibTrackChannel,(uint16_t)(S(HandleEffectAdlxControl)+0x46));
            r->sp=(uint16_t)(r->sp+2); return rc;
        }
    }
    r->ax=rd16(r->cs,(uint16_t)(r->bx+8)); wr16(r->cs,(uint16_t)(r->bx+0x12),r->ax);
    r->ax=rd16(r->cs,(uint16_t)(r->bx+6)); wr16(r->cs,(uint16_t)(r->bx+0x10),r->ax); return UGH_OK;
}

/* No args. Clock increments unconditionally; unguarded wrapper increments it
 * twice, since Tick sees the already-set guard. CF preserved by INC. */
static void clock_tick(Regs *r) {
    uint16_t lo=inc(r,rd16(r->cs,S(AdlxTickCount))); wr16(r->cs,S(AdlxTickCount),lo);
    if(!lo) wr16(r->cs,S(AdlxTickHighWord),inc(r,rd16(r->cs,S(AdlxTickHighWord))));
}
/* TRANSLATES SOUND:AdvanceGuardedSoundClock */
EXPORT int c_AdvanceGuardedSoundClock(Regs *r) {
    clock_tick(r);
    if(!(rd16(r->cs,S(AdlxPlaybackGuard))&1)) {
        wr16(r->cs,S(AdlxPlaybackGuard),1);
        int rc=call(r,r->cs,S(TickAdlxPlayback),(uint16_t)(S(AdvanceGuardedSoundClock)+0x27)); if(rc) return rc;
        wr16(r->cs,S(AdlxPlaybackGuard),0);
    }
    return UGH_OK;
}

/* AX/BX/DX preserved. ES/DI preserved around interpreters, CX/SI/DS follow
 * callees. Guard clears to ZERO, never restores an even nonzero prior word.
 * Due tests are unsigned high then low. Main section compares offset only.
 * Effects 8..11 require low byte flags&5==5; all four are visited. */
/* TRANSLATES SOUND:TickAdlxPlayback */
EXPORT int c_TickAdlxPlayback(Regs *r) {
    clock_tick(r); if(rd16(r->cs,S(AdlxPlaybackGuard))&1) return UGH_OK;
    wr16(r->cs,S(AdlxPlaybackGuard),1);
    uint16_t ax=r->ax,bx=r->bx,dx=r->dx; r->sp=(uint16_t)(r->sp-6); int rc=0;
    if(rd16(r->cs,S(MainAdlxPlaying))&1) {
        r->dx=rd16(r->cs,S(AdlxTickHighWord));
        uint16_t high=rd16(r->cs,S(MainAdlxDeadlineHigh));
        int due=r->dx>high;
        if(r->dx==high) { r->ax=rd16(r->cs,S(AdlxTickCount)); due=r->ax>=rd16(r->cs,S(MainAdlxDeadlineLow)); }
        if(due) {
            wr16(r->cs,S(CurrentAdlxRecordOffset),(uint16_t)(S(AudioChannelStates)+12*42)); wr16(r->cs,S(CurrentAdlxSlot),12);
            uint16_t es=r->es,di=r->di,workbx=r->bx; r->sp=(uint16_t)(r->sp-6);
            r->di=rd16(r->cs,S(MainAdlxCursor)); r->es=rd16(r->cs,S(MainAdlxCursorSegment));
            if((rd16(r->cs,S(MainAdlxSectionLoopEnabled))&1) && r->di>=rd16(r->cs,S(MainAdlxSectionEnd))) {
                rc=call(r,UGH_SEG_C,UGH_O_C_ApplyScannedMusicEvents,(uint16_t)(S(TickAdlxPlayback)+0x84));
                if(rc) return rc;
                r->di=rd16(r->cs,S(MainAdlxCursor)); r->es=rd16(r->cs,S(MainAdlxCursorSegment));
            }
            rc=call(r,r->cs,S(RunMainAdlxEvents),(uint16_t)(S(TickAdlxPlayback)+0x8d));
            r->sp=(uint16_t)(r->sp+6); r->bx=workbx; r->di=di; r->es=es; if(rc) return rc;
        }
    }
    if(rd16(r->cs,S(ReservedAdlibChannelCount))&15) {
        r->bx=(uint16_t)(S(AudioChannelStates)+8*42); wr16(r->cs,S(CurrentAdlxSlot),8);
        do {
            al(r,rd8(r->cs,(uint16_t)(r->bx+0x28))&5);
            if((uint8_t)r->ax==5) {
                r->ax=rd16(r->cs,S(AdlxTickHighWord)); uint16_t high=rd16(r->cs,(uint16_t)(r->bx+0x20));
                int due=r->ax>high;
                if(r->ax==high) { r->ax=rd16(r->cs,S(AdlxTickCount)); due=r->ax>=rd16(r->cs,(uint16_t)(r->bx+0x1e)); }
                if(due) {
                    wr16(r->cs,S(CurrentAdlxRecordOffset),r->bx);
                    uint16_t es=r->es,di=r->di,workbx=r->bx; r->sp=(uint16_t)(r->sp-6);
                    r->di=rd16(r->cs,(uint16_t)(r->bx+0x10)); r->es=rd16(r->cs,(uint16_t)(r->bx+0x12));
                    rc=call(r,r->cs,S(RunEffectAdlxEvents),(uint16_t)(S(TickAdlxPlayback)+0xe2));
                    r->sp=(uint16_t)(r->sp+6); r->es=es; r->di=di; r->bx=workbx; if(rc) return rc;
                }
            }
            wr16(r->cs,S(CurrentAdlxSlot),inc(r,rd16(r->cs,S(CurrentAdlxSlot)))); r->bx=(uint16_t)(r->bx+42);
        } while(r->bx<(uint16_t)(S(AudioChannelStates)+12*42));
    }
    wr16(r->cs,S(AdlxPlaybackGuard),0); r->sp=(uint16_t)(r->sp+6); r->ax=ax; r->bx=bx; r->dx=dx; return UGH_OK;
}

/* No args; SI and AX/DX/segments preserved, BX/CX scratch (CX=0).
 * Writes OPL 01=0,01=20 then both total levels for 9 channels. Saved key bits
 * are untouched. Operator lookup is dynamic mutable CS data. */
/* TRANSLATES SOUND:SilenceAdlibOperators */
EXPORT int c_SilenceAdlibOperators(Regs *r) {
    emit(r,0x100); emit(r,0x120); r->cx=9;
    for(unsigned i=0;i<9;i++) {
        uint8_t op=(uint8_t)(rd8(r->cs,(uint16_t)(S(AdlibOperatorOffsets)+i))+0x40);
        emit(r,(uint16_t)(op*256u+63)); bh(r,(uint8_t)((r->bx>>8)+3)); c_WriteAdlibRegister(r); r->cx--;
    }
    return UGH_OK;
}
/* Timer remover DS change survives. Even failed init's attempted flag causes
 * stale handle removal. Restore is unconditional, followed by OPL silence. */
/* TRANSLATES SOUND:ShutdownAdlibPlayback */
EXPORT int c_ShutdownAdlibPlayback(Regs *r) {
    int rc;
    if(rd8(r->cs,S(AdlibInitAttempted))) {
        r->ax=rd16(r->cs,S(AdlxPlaybackTimerHandle));
        rc=call(r,TIMER_SEG,T(RemoveTimerCallback),(uint16_t)(S(ShutdownAdlibPlayback)+0x14)); if(rc) return rc;
    }
    rc=call(r,TIMER_SEG,T(RestoreTimerInterrupt),(uint16_t)(S(ShutdownAdlibPlayback)+0x19)); if(rc) return rc;
    wr8(r->cs,S(AdlibInitAttempted),0); return c_SilenceAdlibOperators(r);
}

/* No args, ES/DI/SI preserved; AX=0 probe fail, AX=1 success/already attempted.
 * Probe only checks status&E0 nonzero at second read (not equality C0).
 * Calibration uses the existing two explicit IRQ service-point scripts.
 * Attempted byte remains set on failure; second call succeeds immediately. */
/* TRANSLATES SOUND:InitializeAdlibPlayback */
EXPORT int c_InitializeAdlibPlayback(Regs *r) {
    uint16_t es=r->es,di=r->di,si=r->si,sp=r->sp; int rc=0;
    r->sp=(uint16_t)(sp-6);
    if(!rd8(r->cs,S(AdlibInitAttempted))) {
        wr8(r->cs,S(AdlibInitAttempted),1);
        rc=call(r,r->cs,S(CalibrateSoundDelay),(uint16_t)(S(InitializeAdlibPlayback)+0x18)); if(rc) return rc;
        emit(r,0x100); emit(r,0x460); delay(r,0x14); emit(r,0x480); delay(r,0x14);
        r->dx=0x388; al(r,(uint8_t)platform_in(r->dx,1)); if(ugh_devices.error) return UGH_UNSUPPORTED;
        if(r->ax&0xe0) goto fail;
        emit(r,0x2ff); delay(r,0x14); emit(r,0x421); delay(r,0xff);
        al(r,(uint8_t)platform_in(r->dx,1)); if(ugh_devices.error) return UGH_UNSUPPORTED;
        if(!(r->ax&0xe0)) goto fail;
        emit(r,0x460); delay(r,0x14); emit(r,0x480); delay(r,0x14); c_SilenceAdlibOperators(r); emit(r,0x120);
        rc=call(r,TIMER_SEG,T(InstallTimerInterrupt),(uint16_t)(S(InitializeAdlibPlayback)+0x90)); if(rc) return rc;
        r->bx=0x1843; r->cx=0; r->ax=S(TickAdlxPlayback); r->dx=SOUND_SEG;
        rc=call(r,TIMER_SEG,T(RegisterTimerCallback),(uint16_t)(S(InitializeAdlibPlayback)+0xa0)); if(rc) return rc;
        wr16(r->cs,S(AdlxPlaybackTimerHandle),r->ax);
    }
    r->ax=1; goto done;
fail: r->ax=logic(r,0,16);
done: r->es=es; r->di=di; r->si=si; r->sp=sp; return rc;
}
