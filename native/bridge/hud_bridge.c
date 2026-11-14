#include "hud_support.h"
static void push(Regs *r,uint16_t v) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v); }

static uint16_t pop(Regs *r) { uint16_t v=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return v; }

static void cmp8(Regs *r,uint8_t a,uint8_t b) {
    uint8_t v=(uint8_t)(a-b);
    flag(r,CF,a<b); flag(r,OF,((a^b)&(a^v)&128)!=0);
    flag(r,AF,((a^b^v)&16)!=0); szp(r,v,8);
}

static void set_bl(Regs *r,uint8_t v) { r->bx=(uint16_t)((r->bx&0xff00u)|v); }

#define CALL(target,owner,delta) do { int status=ugh_call_near(G(target),(uint16_t)(G(owner)+(delta)),r); if(status) return status; } while(0)
#define R(name) rd16(r->ds,D(name))
#define W(name,v) wr16(r->ds,D(name),(uint16_t)(v))
#define B(name) rd8(r->ds,D(name))
#define WB(name,v) wr8(r->ds,D(name),(uint8_t)(v))
#define RI(name,i) rd16(r->ds,(uint16_t)(D(name)+(i)))
#define WI(name,i,v) wr16(r->ds,(uint16_t)(D(name)+(i)),(uint16_t)(v))
#define HW(n,v) hd_store(r,&plan,D(n),(uint16_t)(v),2)
#define HWB(n,v) hd_store(r,&plan,D(n),(uint8_t)(v),1)
#define HP_CALL(target,owner,delta) do{hd_service(r,&plan,G(target));int status=ugh_call_near(G(target),(uint16_t)(G(owner)+(delta)),r);if(status)return status;hd_returned(&plan);}while(0)
static int changed_digits(Regs *r) {
    r->si=logic(r,0,16);
    for(;;) {
        set_al(r,rd8(r->ds,(uint16_t)(D(DecimalDigitBuffer)+r->si)));
        cmp8(r,(uint8_t)r->ax,255); if((uint8_t)r->ax==255) {HudDigitDecision end=hud_changed_digit((uint8_t)r->ax,0,R(HudDigitCursorX),r->si);hd_require(end.done && !end.draw);return UGH_OK;}
        uint8_t old=rd8(r->ds,(uint16_t)((D(DecimalDigitBuffer)+7)+r->si));
        HudDigitDecision decision=hud_changed_digit((uint8_t)r->ax,old,R(HudDigitCursorX),r->si);hd_require(!decision.done);unsigned consumed=0;
        cmp8(r,(uint8_t)r->ax,old);
        if((uint8_t)r->ax!=old) { hd_require(decision.draw);consumed++;CALL(DrawHudDigit,RedrawChangedFourDigitNumber,0x27); }
        hd_require(consumed==decision.draw);W(HudDigitCursorX,hd_word(decision.next_x,add16(r,R(HudDigitCursorX),6,0)));
        uint16_t cf=r->flags&CF; r->si=add16(r,r->si,1,0); flag(r,CF,cf);r->si=hd_word(decision.next_index,r->si);
    }
}
EXPORT int c_DrawHudBorders(Regs *r) {
    uint16_t players=R(PlayerCount);RenderDrawRequest first=hud_border(players,0),second=hud_border(players,1);
    sub16(r,R(PlayerCount),2,0);
    r->ax=R(PlayerCount)==2?0xb0:0xae; r->bp=(uint16_t)(r->ax+1);
    push(r,r->bp); r->bx=logic(r,0,16); r->cx=193;
    hd_draw(r,first);
    CALL(DrawTransparentSprite,DrawHudBorders,0x21);
    r->ax=pop(r); r->bx=255;
    hd_draw(r,second);return ugh_dispatch(r->cs,G(DrawTransparentSprite),r);
}

EXPORT int c_DrawHudDigit(Regs *r) {
    RenderDrawRequest request=hud_digit((uint8_t)r->ax,R(HudDigitCursorX),R(HudDigitCursorY));
    push(r,r->ax); set_ah(r,0); r->ax=add16(r,r->ax,204,0);
    r->bx=R(HudDigitCursorX); r->cx=R(HudDigitCursorY);
    hd_draw(r,request);
    CALL(DrawTransparentSprite,DrawHudDigit,0x11);
    r->ax=pop(r); return UGH_OK;
}

EXPORT int c_DrawHudDigitAndAdvance(Regs *r) {
    CALL(DrawHudDigit,DrawHudDigitAndAdvance,3);
    W(HudDigitCursorX,hd_word(hud_advance(R(HudDigitCursorX)),add16(r,R(HudDigitCursorX),6,0))); return UGH_OK;
}

EXPORT int c_RedrawChangedTwoDigitNumber(Regs *r) {
    r->si=D(DecimalDigitBuffer); CALL(EncodeTwoDecimalDigits,RedrawChangedTwoDigitNumber,6);
    set_al(r,(uint8_t)r->bx); r->si=(D(DecimalDigitBuffer)+7);
    CALL(EncodeTwoDecimalDigits,RedrawChangedTwoDigitNumber,0xe);
    return changed_digits(r);
}

EXPORT int c_RedrawChangedFourDigitNumber(Regs *r) {
    r->si=D(DecimalDigitBuffer); CALL(EncodeFourDecimalDigits,RedrawChangedFourDigitNumber,6);
    r->ax=r->bx; r->si=(D(DecimalDigitBuffer)+7);
    CALL(EncodeFourDecimalDigits,RedrawChangedFourDigitNumber,0xe);
    return changed_digits(r);
}

EXPORT int c_RedrawChangedSixDigitNumber(Regs *r) {
    r->si=D(DecimalDigitBuffer); CALL(EncodeSixDecimalDigits,RedrawChangedSixDigitNumber,6);
    r->ax=r->bx; r->dx=r->cx; r->si=(D(DecimalDigitBuffer)+7);
    CALL(EncodeSixDecimalDigits,RedrawChangedSixDigitNumber,0x10);
    return changed_digits(r);
}

EXPORT int c_RefreshHudAndTimerBar(Regs *r) {
    HudPlan plan;hd_open(r,&plan,HUD_LIVES);
    HW(HudDigitCursorY,194);
    set_al(r,B(LivesRemaining)); set_bl(r,B(HudCachedLives));
    cmp8(r,(uint8_t)r->ax,(uint8_t)r->bx);
    if((uint8_t)r->ax!=(uint8_t)r->bx) {
        HWB(HudCachedLives,r->ax); r->bp=R(HudLivesX); HW(HudDigitCursorX,r->bp);
        HP_CALL(RedrawChangedTwoDigitNumber,RefreshHudAndTimerBar,0x22);
    }
    hd_advance(r,&plan,HUD_SCORE);
    r->ax=R(ScoreLowWord); r->dx=R(ScoreHighWord);
    sub16(r,r->dx,15,0);
    if(r->dx==15) sub16(r,r->ax,0x423f,0);
    if(r->dx>15 || (r->dx==15 && r->ax>0x423f)) {
        r->dx=15; r->ax=0x423f; HW(ScoreLowWord,r->ax); HW(ScoreHighWord,r->dx);
    }
    r->bx=R(HudCachedScoreLow); r->cx=R(HudCachedScoreHigh);
    sub16(r,r->ax,r->bx,0);
    if(r->ax==r->bx) sub16(r,r->dx,r->cx,0);
    if(r->ax!=r->bx || r->dx!=r->cx) {
        HW(HudCachedScoreLow,r->ax); HW(HudCachedScoreHigh,r->dx);
        r->bp=R(HudScoreX); HW(HudDigitCursorX,r->bp);
        HP_CALL(RedrawChangedSixDigitNumber,RefreshHudAndTimerBar,0x73);
        hd_finish(&plan,HUD_TIMER);goto timer;
    }
    hd_advance(r,&plan,HUD_JOURNEYS);
    set_al(r,B(RemainingPassengerJourneys)); set_bl(r,B(HudCachedLevelCounter));
    cmp8(r,(uint8_t)r->ax,(uint8_t)r->bx);
    if((uint8_t)r->ax!=(uint8_t)r->bx) {
        HWB(HudCachedLevelCounter,r->ax); r->bp=R(HudLevelCounterX); HW(HudDigitCursorX,r->bp);
        HP_CALL(RedrawChangedTwoDigitNumber,RefreshHudAndTimerBar,0x92);
    }
    hd_advance(r,&plan,HUD_ICON_ONE);
    r->ax=R(PlayerCarriedKinds); sub16(r,r->ax,R(HudCachedPlayerOneIconState),0);
    if(r->ax!=R(HudCachedPlayerOneIconState)) {
        HW(HudCachedPlayerOneIconState,r->ax); r->ax=add16(r,r->ax,0xb2,0);
        r->bx=R(HudPlayerOneIconX); r->cx=193;
        HP_CALL(DrawTransparentSprite,RefreshHudAndTimerBar,0xae);
        r->ax=add16(r,R(PlayerDestinationIcons),0xb7,0); r->bx=R(HudPlayerOneDestinationX);
        HP_CALL(DrawTransparentSprite,RefreshHudAndTimerBar,0xbb);
        hd_finish(&plan,HUD_TIMER);goto timer;
    }
    hd_advance(r,&plan,HUD_ICON_TWO);
    sub16(r,R(PlayerCount),2,0);
    if(R(PlayerCount)==2) {
        r->ax=R(PlayerTwoPassengerIconState); sub16(r,r->ax,R(HudCachedPlayerTwoIconState),0);
        if(r->ax!=R(HudCachedPlayerTwoIconState)) {
            HW(HudCachedPlayerTwoIconState,r->ax); r->ax=add16(r,r->ax,0xbf,0);
            r->bx=R(HudPlayerTwoIconX); r->cx=193;
            HP_CALL(DrawTransparentSprite,RefreshHudAndTimerBar,0xe4);
            r->ax=add16(r,R(PlayerTwoDestinationIconIndex),0xc4,0); r->bx=R(HudPlayerTwoDestinationX);
            HP_CALL(DrawTransparentSprite,RefreshHudAndTimerBar,0xf1);
            hd_finish(&plan,HUD_TIMER);goto timer;
        }
    }
    hd_advance(r,&plan,HUD_FARE);
    r->bp=R(HudFareX); HW(HudDigitCursorX,r->bp);
    sub16(r,R(PlayerCarriedKinds),0,0);
    if(R(PlayerCarriedKinds)) { r->di=logic(r,0,16); r->ax=RI(PlayerPassengerFares,r->di); goto fare; }
    sub16(r,R(PlayerCount),2,0);
    if(R(PlayerCount)==2) {
        sub16(r,R(PlayerTwoPassengerIconState),0,0);
        if(R(PlayerTwoPassengerIconState)) { r->di=2; r->ax=RI(PlayerPassengerFares,r->di); goto fare; }
    }
    cmp8(r,B(HudFareClearPending),0);
    if(!B(HudFareClearPending)) {hd_finish(&plan,HUD_MULTIPLIER);goto multiplier;}
    r->ax=logic(r,0,16);
fare:
    r->bx=R(HudCachedFare); sub16(r,r->ax,r->bx,0);
    if(r->ax!=r->bx) { HW(HudCachedFare,r->ax); HP_CALL(RedrawChangedFourDigitNumber,RefreshHudAndTimerBar,0x143); }
    HWB(HudFareClearPending,0);
    hd_finish(&plan,HUD_MULTIPLIER);
multiplier:
    hd_open(r,&plan,HUD_MULTIPLIER);
    set_al(r,B(ScoreMultiplier)); set_bl(r,B(HudCachedMultiplier));
    cmp8(r,(uint8_t)r->ax,(uint8_t)r->bx);
    if((uint8_t)r->ax!=(uint8_t)r->bx) {
        HWB(HudCachedMultiplier,r->ax); r->bp=R(HudMultiplierX); HW(HudDigitCursorX,r->bp);
        HP_CALL(RedrawChangedTwoDigitNumber,RefreshHudAndTimerBar,0x165);
    }
    hd_finish(&plan,HUD_TIMER);
timer:
    hd_open(r,&plan,HUD_TIMER);
    r->ax=R(LevelTimer); sub16(r,r->ax,0,0);
    if((int16_t)r->ax<0) {
        HW(LevelTimer,0xffff); sub16(r,R(ScreenFadeStep),0,0);
        if((int16_t)R(ScreenFadeStep)>=0) {
            r->ax=0xfffe; HW(ScreenFadeStep,r->ax); HW(ScreenFadeLevel,add16(r,R(ScreenFadeLevel),r->ax,0));
        }
        hd_finish(&plan,HUD_DONE);return UGH_OK;
    }
    push(r,r->ds); r->dx=logic(r,0,16);
    uint16_t divisor=R(TimerBarDivisor); if(!divisor){hd_error(&plan);return UGH_UNSUPPORTED;}
    r->dx=(uint16_t)(r->ax%divisor); r->ax=(uint16_t)(r->ax/divisor); push(r,r->ax);
    sub16(r,r->ax,R(CachedTimerBarWidth),0);
    if(r->ax==R(CachedTimerBarWidth)) goto timer_done;
    hd_bar_begin(&plan,r->ax,R(CachedTimerBarWidth));
    if((int16_t)r->ax<(int16_t)R(CachedTimerBarWidth)) {
        r->bp=r->ax; r->bx=logic(r,r->ax&3,16);
        r->dx=0x3c4; set_al(r,2); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=0x3c5; set_al(r,hd_mask(&plan,0,r->bx,rd8(r->ds,(uint16_t)(D(VgaSinglePlaneMasks)+r->bx))));
        platform_out(r->dx,1,(uint8_t)r->ax); r->bp>>=2;
        r->si=R(TimerBarPointer); r->ds=rd16(r->ds,D(TimerBarPointer)+2);
        r->si=add16(r,r->si,r->bp,0); set_al(r,(uint8_t)logic(r,0,8));
        hd_bar_pixels(r,&plan,(uint8_t)r->ax,0);
        set_al(r,15); platform_out(r->dx,1,(uint8_t)r->ax);
    } else {
        r->di=(uint16_t)(R(CachedTimerBarWidth)>>2); r->ax=dec16(r,r->ax);
        r->bp=r->ax; r->bx=logic(r,r->ax&3,16);
        r->dx=0x3c4; set_al(r,2); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=0x3c5; set_al(r,hd_mask(&plan,1,r->bx,rd8(r->ds,(uint16_t)(D(VgaCumulativePlaneMasks)+r->bx))));
        platform_out(r->dx,1,(uint8_t)r->ax); r->bp>>=2;
        r->si=R(TimerBarPointer); r->ds=rd16(r->ds,D(TimerBarPointer)+2);
        r->si=add16(r,r->si,r->bp,0); set_al(r,50);
        hd_bar_pixels(r,&plan,(uint8_t)r->ax,0);
        set_al(r,15); platform_out(r->dx,1,(uint8_t)r->ax);
        r->bp=sub16(r,r->bp,r->di,0);
        if(r->bp) {
            set_al(r,50);
            do {
                r->si=dec16(r,r->si); hd_bar_pixels(r,&plan,(uint8_t)r->ax,1);
                r->bp=dec16(r,r->bp);r->bp=hd_word(plan.bar.remaining,r->bp);
            } while(r->bp);
        }
    }
timer_done:
    hd_bar_end(&plan);
    r->ax=pop(r); r->ds=pop(r); HW(CachedTimerBarWidth,r->ax);hd_finish(&plan,HUD_DONE);return UGH_OK;
}

