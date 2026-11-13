#include "ugh.h"
#include "platform.h"

/* All exports use the original near register ABI, incoming DS/CS and SS:SP.
 * CALL sites retain the measured return IP and actual saved-word frame. There
 * are no host gameplay objects, DOS requests, or private copies of game state.
 * Sprite/rectangle calls inherit the pilot's VGA effects and DF behaviour. */
static void push(Regs *r,uint16_t v) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v); }
static uint16_t pop(Regs *r) { uint16_t v=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return v; }
static uint16_t sar(uint16_t v,unsigned n) { return (uint16_t)((v>>n)|((v&0x8000u)?(0xffffu<<(16-n)):0)); }
static void cmp8(Regs *r,uint8_t a,uint8_t b) {
    uint8_t v=(uint8_t)(a-b);
    flag(r,CF,a<b); flag(r,OF,((a^b)&(a^v)&128)!=0);
    flag(r,AF,((a^b^v)&16)!=0); szp(r,v,8);
}
static uint8_t inc8(Regs *r,uint8_t a) {
    uint8_t v=(uint8_t)(a+1); flag(r,OF,a==127); flag(r,AF,((a^v^1)&16)!=0); szp(r,v,8); return v;
}
static void set_bl(Regs *r,uint8_t v) { r->bx=(uint16_t)((r->bx&0xff00u)|v); }
#define CALL(target,owner,delta) do { int status=ugh_call_near(G(target),(uint16_t)(G(owner)+(delta)),r); if(status) return status; } while(0)
#define R(name) rd16(r->ds,D(name))
#define W(name,v) wr16(r->ds,D(name),(uint16_t)(v))
#define B(name) rd8(r->ds,D(name))
#define WB(name,v) wr8(r->ds,D(name),(uint8_t)(v))
#define RI(name,i) rd16(r->ds,(uint16_t)(D(name)+(i)))
#define WI(name,i,v) wr16(r->ds,(uint16_t)(D(name)+(i)),(uint16_t)(v))

/* Clear only the workspace's 196 words, initialize deliberately different HUD
 * caches and mode-specific cursors, then compose every real scene/actor callee.
 * STOSW obeys incoming DF; ICE later clears DF. Unused second-player cursors
 * stay stale in one-player mode. */
/* TRANSLATES GAME:InitializeLevelDisplay */
EXPORT int c_InitializeLevelDisplay(Regs *r) {
    r->cx=196; r->di=R(LevelWorkspacePointer); r->es=RI(LevelWorkspacePointer,2); r->ax=logic(r,0,16);
    do { wr16(r->es,r->di,r->ax); r->di=(uint16_t)(r->di+2*step(r)); r->cx--; } while(r->cx);
    W(LevelTimer,0x5a3b); r->ax=0xffff; W(ds_27C8,r->ax); W(ScreenFadeStep,2);
    set_al(r,(uint8_t)(B(LivesRemaining)+11)); cmp8(r,(uint8_t)r->ax,100);
    if((uint8_t)r->ax>=100) set_al(r,(uint8_t)(r->ax-100));
    WB(HudCachedLives,r->ax);
    set_al(r,(uint8_t)(B(ScoreMultiplier)+11)); cmp8(r,(uint8_t)r->ax,100);
    if((uint8_t)r->ax>=100) set_al(r,(uint8_t)(r->ax-100));
    WB(HudCachedMultiplier,r->ax);
    WB(HudCachedLevelCounter,99); W(HudCachedFare,9999);
    r->ax=R(ScoreLowWord); r->dx=R(ScoreHighWord);
    r->ax=add16(r,r->ax,0xb207,0); r->dx=add16(r,r->dx,1,!!(r->flags&CF));
    sub16(r,r->dx,15,0); int reduce=r->dx>15;
    if(r->dx==15) { sub16(r,r->ax,0x4240,0); reduce=r->ax>0x4240; }
    if(reduce) { r->ax=sub16(r,r->ax,0x4240,0); r->dx=sub16(r,r->dx,15,!!(r->flags&CF)); }
    W(HudCachedScoreLow,r->ax); W(HudCachedScoreHigh,r->dx); W(HudDigitCursorY,194);
    sub16(r,R(PlayerCount),2,0); W(HudLivesX,33);
    if(R(PlayerCount)==2) {
        W(HudScoreX,114); W(HudLevelCounterX,169); W(HudPlayerOneDestinationX,199);
        W(HudPlayerOneIconX,215); W(HudFareX,232); W(HudMultiplierX,305);
        W(HudPlayerTwoIconX,258); W(HudPlayerTwoDestinationX,274);
    } else {
        W(HudScoreX,118); W(HudLevelCounterX,177); W(HudPlayerOneDestinationX,208);
        W(HudPlayerOneIconX,224); W(HudFareX,244); W(HudMultiplierX,290);
    }
    CALL(LoadCurrentLevelState,InitializeLevelDisplay,0xef);
    CALL(ShowLevelIntroduction,InitializeLevelDisplay,0xf2);
    CALL(ClearAllVgaPlanes,InitializeLevelDisplay,0xf5);
    CALL(BlackenVgaPalette,InitializeLevelDisplay,0xf8);
    CALL(DuplicateSourcePaletteHalves,InitializeLevelDisplay,0xfb);
    CALL(DrawTileMap,InitializeLevelDisplay,0xfe);
    CALL(SaveDrawPageBackground,InitializeLevelDisplay,0x101);
    CALL(SwapAndDisplayVgaPage,InitializeLevelDisplay,0x104);
    CALL(RestorePlayfieldBackground,InitializeLevelDisplay,0x107);
    CALL(DrawHudBorders,InitializeLevelDisplay,0x10a);
    CALL(DispatchEnemyStates,InitializeLevelDisplay,0x10d);
    CALL(DispatchActorUpdates,InitializeLevelDisplay,0x110);
    return ugh_dispatch(r->cs,G(ResetSpriteEraseState),r);
}

/* BX particle byte index; water/direction/stride through DS. AX/CX/DX outputs,
 * others preserved. Byte MUL uses AL only; final AND CX,3 defines flags.
 * Calls the existing random adapter, updating its four CS state words. */
/* TRANSLATES GAME:RespawnRainParticle */
EXPORT int c_RespawnRainParticle(Regs *r) {
    r->ax=add16(r,320,R(WaterYPixels),0);
    CALL(NextRandomBelowAx,RespawnRainParticle,0x0a);
    sub16(r,r->ax,320,0);
    if(r->ax<320) { r->cx=r->ax; r->ax=logic(r,0,16); }
    else {
        r->ax=sub16(r,r->ax,320,0);
        cmp8(r,B(LevelRainDirection),1);
        if(B(LevelRainDirection)==1) r->cx=319;
        else r->cx=logic(r,0,16);
    }
    r->ax=(uint16_t)((uint8_t)r->ax*B(VgaRowStrideBytes));
    r->dx=(uint16_t)(r->cx>>2);
    r->ax=add16(r,r->ax,r->dx,0);
    WI(RainParticleOffsets,r->bx,r->ax);
    r->cx=logic(r,r->cx&3,16); WI(RainParticleXModuloFour,r->bx,r->cx);
    return UGH_OK;
}

/* BX/BP and AX/CX/DX destroyed; SI/DI and segments retained. Signed SUB/JNS
 * post-test includes waterY+1; doubled count can wrap. Direction is a byte,
 * TEST CX,00FCh deliberately ignores high bits. Final SUB defines flags. */
/* TRANSLATES GAME:AdvanceRainParticles */
EXPORT int c_AdvanceRainParticles(Regs *r) {
    r->bx=(uint16_t)((R(WaterYPixels)+1u)*2u);
    r->ax=B(LevelRainDirection); r->bp=(uint16_t)((r->ax-1u)*2u-1u);
    do {
        r->ax=RI(RainParticleOffsets,r->bx); WI(RainPreviousOffsets,r->bx,r->ax);
        r->ax=(uint16_t)(r->ax+192u);
        if(!(r->bx&2)) r->ax=(uint16_t)(r->ax+96u);
        r->cx=RI(RainParticleXModuloFour,r->bx);
        r->cx=(uint16_t)(r->cx+r->bp+r->bp);
        if(!(r->bx&2)) r->cx=(uint16_t)(r->cx+r->bp);
        if(r->cx&0xfc) r->ax=(uint16_t)(r->ax+r->bp);
        r->cx=logic(r,r->cx&3,16);
        sub16(r,r->ax,R(WaterSurfaceByteOffset),0);
        if(r->ax>=R(WaterSurfaceByteOffset)) { CALL(RespawnRainParticle,AdvanceRainParticles,0x56); }
        else { WI(RainParticleOffsets,r->bx,r->ax); WI(RainParticleXModuloFour,r->bx,r->cx); }
        r->bx=sub16(r,r->bx,2,0);
    } while(!(r->bx&0x8000u));
    return UGH_OK;
}

/* DS player mode; AX/BX/CX/BP destroyed. DX/SI/DI/DS/ES preserved.
 * Second sprite ID must survive the first draw's BP output. Tail retains frame. */
/* TRANSLATES GAME:DrawHudBorders */
EXPORT int c_DrawHudBorders(Regs *r) {
    sub16(r,R(PlayerCount),2,0);
    r->ax=R(PlayerCount)==2?0xb0:0xae; r->bp=(uint16_t)(r->ax+1);
    push(r,r->bp); r->bx=logic(r,0,16); r->cx=193;
    CALL(DrawTransparentSprite,DrawHudBorders,0x21);
    r->ax=pop(r); r->bx=255;
    return ugh_dispatch(r->cs,G(DrawTransparentSprite),r);
}

/* AL numeric digit, no range check; cursor through DS. AX saved, BX/CX cursor,
 * BP renderer output. Other registers/segments preserved; renderer flags flow. */
/* TRANSLATES GAME:DrawHudDigit */
EXPORT int c_DrawHudDigit(Regs *r) {
    push(r,r->ax); set_ah(r,0); r->ax=add16(r,r->ax,204,0);
    r->bx=R(HudDigitCursorX); r->cx=R(HudDigitCursorY);
    CALL(DrawTransparentSprite,DrawHudDigit,0x11);
    r->ax=pop(r); return UGH_OK;
}
/* Same ABI as digit; cursor wraps, final flags are ADD cursor,6. */
/* TRANSLATES GAME:DrawHudDigitAndAdvance */
EXPORT int c_DrawHudDigitAndAdvance(Regs *r) {
    CALL(DrawHudDigit,DrawHudDigitAndAdvance,3);
    W(HudDigitCursorX,add16(r,R(HudDigitCursorX),6,0)); return UGH_OK;
}

/* Shared 3EDD tail: buffers are reread live, including after sprite calls.
 * SI stops at numeric FF sentinel; AL=FF and final flags CMP AL,FF. */
static int changed_digits(Regs *r) {
    r->si=logic(r,0,16);
    for(;;) {
        set_al(r,rd8(r->ds,(uint16_t)(D(DecimalDigitBuffer)+r->si)));
        cmp8(r,(uint8_t)r->ax,255); if((uint8_t)r->ax==255) return UGH_OK;
        uint8_t old=rd8(r->ds,(uint16_t)((D(DecimalDigitBuffer)+7)+r->si));
        cmp8(r,(uint8_t)r->ax,old);
        if((uint8_t)r->ax!=old) { CALL(DrawHudDigit,RedrawChangedFourDigitNumber,0x27); }
        W(HudDigitCursorX,add16(r,R(HudDigitCursorX),6,0));
        uint16_t cf=r->flags&CF; r->si=add16(r,r->si,1,0); flag(r,CF,cf);
    }
}
/* Current DX:AX, previous CX:BX; DS buffers/divisors and cursor. Six digits.
 * General outputs follow encoder and changed tail; no leading-zero suppression. */
/* TRANSLATES GAME:RedrawChangedSixDigitNumber */
EXPORT int c_RedrawChangedSixDigitNumber(Regs *r) {
    r->si=D(DecimalDigitBuffer); CALL(EncodeSixDecimalDigits,RedrawChangedSixDigitNumber,6);
    r->ax=r->bx; r->dx=r->cx; r->si=(D(DecimalDigitBuffer)+7);
    CALL(EncodeSixDecimalDigits,RedrawChangedSixDigitNumber,0x10);
    return changed_digits(r);
}
/* Current AX, previous BX; four numeric digits. Same shared comparison tail. */
/* TRANSLATES GAME:RedrawChangedFourDigitNumber */
EXPORT int c_RedrawChangedFourDigitNumber(Regs *r) {
    r->si=D(DecimalDigitBuffer); CALL(EncodeFourDecimalDigits,RedrawChangedFourDigitNumber,6);
    r->ax=r->bx; r->si=(D(DecimalDigitBuffer)+7);
    CALL(EncodeFourDecimalDigits,RedrawChangedFourDigitNumber,0xe);
    return changed_digits(r);
}
/* Current AL, previous BL; AH/BH ignored by the two-digit encoder. */
/* TRANSLATES GAME:RedrawChangedTwoDigitNumber */
EXPORT int c_RedrawChangedTwoDigitNumber(Regs *r) {
    r->si=D(DecimalDigitBuffer); CALL(EncodeTwoDecimalDigits,RedrawChangedTwoDigitNumber,6);
    set_al(r,(uint8_t)r->bx); r->si=(D(DecimalDigitBuffer)+7);
    CALL(EncodeTwoDecimalDigits,RedrawChangedTwoDigitNumber,0xe);
    return changed_digits(r);
}

/* BX=player byte index; countdown/rate signed, single advance only. AX sprite,
 * CX cached Y, BP renderer output only if drawn. BX preserved; clipping compares
 * strict signed bounds. No extra clamping of a negative rate or large debt. */
/* TRANSLATES GAME:AnimateAndDrawPlayer */
EXPORT int c_AnimateAndDrawPlayer(Regs *r) {
    r->ax=RI(PlayerThrustAnimationRate,r->bx);
    if((int16_t)r->ax>90) r->ax=90;
    WI(PlayerAnimationCountdowns,r->bx,sub16(r,RI(PlayerAnimationCountdowns,r->bx),r->ax,0));
    r->ax=RI(PlayerAnimationCountdowns,r->bx); sub16(r,r->ax,0,0);
    if((int16_t)r->ax<0) {
        r->ax=add16(r,r->ax,200,0); WI(PlayerAnimationCountdowns,r->bx,r->ax);
        r->ax=(uint16_t)(RI(PlayerSpriteIds,r->bx)+1u);
        sub16(r,r->ax,RI(PlayerAnimationCycleEnds,r->bx),0);
        if((int16_t)r->ax>=(int16_t)RI(PlayerAnimationCycleEnds,r->bx)) r->ax=RI(PlayerAnimationCycleStarts,r->bx);
        WI(PlayerSpriteIds,r->bx,r->ax);
    }
    r->ax=RI(PlayerSpriteIds,r->bx); push(r,r->bx);
    r->cx=RI(PlayerYPixels,r->bx); sub16(r,r->cx,(uint16_t)-20,0);
    if((int16_t)r->cx>-20) {
        sub16(r,r->cx,192,0);
        if((int16_t)r->cx<192) {
            r->bx=RI(PlayerPixelX,r->bx); sub16(r,r->bx,(uint16_t)-32,0);
            if((int16_t)r->bx>-32) {
                sub16(r,r->bx,320,0);
                if((int16_t)r->bx<320) { CALL(DrawTransparentSprite,AnimateAndDrawPlayer,0x6e); }
            }
        }
    }
    r->bx=pop(r); return UGH_OK;
}

/* Rectangle wrappers. No arithmetic substitutes for the directory read: LDS
 * loads its segment, then SI is replaced by ID*4 (directory offset discarded).
 * Preserves AX/BX/DX/SI/DS/ES, returns CX width and DI; DF forced clear. */
/* TRANSLATES GAME:RestoreSpriteBackground */
EXPORT int c_RestoreSpriteBackground(Regs *r) {
    push(r,r->dx); push(r,r->si); push(r,r->ds);
    r->si=rd16(r->cs,G(SpriteDirectoryPointer)); r->ds=rd16(r->cs,G(SpriteDirectoryPointer)+2);
    r->si=(uint16_t)(r->cx*4u); r->cx=rd8(r->ds,(uint16_t)(r->si+2));
    r->dx=rd8(r->ds,(uint16_t)(r->si+3));
    CALL(RestoreBackgroundRectangle,RestoreSpriteBackground,0x1a);
    r->ds=pop(r); r->si=pop(r); r->dx=pop(r); return UGH_OK;
}
/* Full-width copy, height from CS. BX/SI preserved, AX=BX arg=0, CX=320,
 * DX=height, DI rectangle output, DS/ES retained, DF clear. */
/* TRANSLATES GAME:RestorePlayfieldBackground */
EXPORT int c_RestorePlayfieldBackground(Regs *r) {
    push(r,r->bx); push(r,r->si); r->ax=logic(r,0,16); r->bx=r->ax;
    r->cx=320; r->dx=rd16(r->cs,G(PlayfieldHeight));
    CALL(RestoreBackgroundRectangle,RestorePlayfieldBackground,0x11);
    r->si=pop(r); r->bx=pop(r); return UGH_OK;
}
/* AX/BX preserved; CX cached ID (or width if restored), DI renderer output.
 * Always calls the existing cache adapter after the same signed bounds tests. */
/* TRANSLATES GAME:RestorePlayerBackground */
EXPORT int c_RestorePlayerBackground(Regs *r) {
    push(r,r->ax); push(r,r->bx);
    r->cx=RI(PlayerCachedSpriteIds,r->bx); r->ax=RI(PlayerCachedPixelX,r->bx);
    sub16(r,r->ax,(uint16_t)-32,0);
    if((int16_t)r->ax>-32) {
        sub16(r,r->ax,320,0);
        if((int16_t)r->ax<320) {
            r->bx=RI(PlayerCachedPixelY,r->bx); sub16(r,r->bx,(uint16_t)-20,0);
            if((int16_t)r->bx>-20) {
                sub16(r,r->bx,192,0);
                if((int16_t)r->bx<192) { CALL(RestoreSpriteBackground,RestorePlayerBackground,0x32); }
            }
        }
    }
    r->bx=pop(r); CALL(CachePlayerDrawState,RestorePlayerBackground,0x36);
    r->ax=pop(r); return UGH_OK;
}
/* AL tile, DL/DH column/row. AX zero extends, BX=column*16, CX=row*12;
 * DX/SI retained, BP sprite output. No clipping. */
/* TRANSLATES GAME:DrawMapTile */
EXPORT int c_DrawMapTile(Regs *r) {
    set_ah(r,0); push(r,r->si); push(r,r->ax); push(r,r->dx);
    r->bx=(uint16_t)((r->dx&255)*16u); push(r,r->ax);
    r->ax=(uint16_t)(12u*(r->dx>>8)); r->cx=r->ax; r->ax=pop(r);
    CALL(DrawTransparentSprite,DrawMapTile,0x17);
    r->dx=pop(r); r->ax=pop(r); r->si=pop(r); return UGH_OK;
}
/* DS:SI loads map far pointer through incoming DS, then DS remains map segment.
 * LODSB honours DF, 320 entries; DX=1014h, SI advances signed 320.
 * Final flags CMP DH,10h; AL last ID; AH zeroed by DrawMapTile. */
/* TRANSLATES GAME:DrawTileMap */
EXPORT int c_DrawTileMap(Regs *r) {
    r->si=R(CurrentTileMapPointer); r->ds=rd16(r->ds,D(CurrentTileMapPointer)+2);
    r->dx&=255;
    do {
        r->dx&=0xff00;
        do {
            set_al(r,rd8(r->ds,r->si)); r->si=(uint16_t)(r->si+step(r));
            CALL(DrawMapTile,DrawTileMap,0xc);
            r->dx=(uint16_t)((r->dx&0xff00)|inc8(r,(uint8_t)r->dx));
            cmp8(r,(uint8_t)r->dx,20);
        } while((uint8_t)r->dx!=20);
        r->dx=(uint16_t)((r->dx&255)|(uint16_t)inc8(r,(uint8_t)(r->dx>>8))*256u);
        cmp8(r,(uint8_t)(r->dx>>8),16);
    } while((r->dx>>8)!=16);
    return UGH_OK;
}

/* DS live/cached HUD fields. All general registers may change; DS restored,
 * ES/SS/SP retained, IF/DF retained. Prioritized score/icon branches skip fare
 * and multiplier for this invocation. Negative timer sets -1; fade arithmetic
 * is word wrapping. Otherwise DIV is unsigned but cached-width CMP is signed.
 * Shrink clears exactly one plane column. Growth fills whole intervening bytes.
 * Only VGA SEQ index/data writes and physical timer-bar writes reach platform.
 * Final flags are the last original CMP/logic/DEC/ADD, excluding DIV-undefined.
 * Zero divisor is unsupported INT 0, never a fabricated width. */
/* TRANSLATES GAME:RefreshHudAndTimerBar */
EXPORT int c_RefreshHudAndTimerBar(Regs *r) {
    W(HudDigitCursorY,194);
    set_al(r,B(LivesRemaining)); set_bl(r,B(HudCachedLives));
    cmp8(r,(uint8_t)r->ax,(uint8_t)r->bx);
    if((uint8_t)r->ax!=(uint8_t)r->bx) {
        WB(HudCachedLives,r->ax); r->bp=R(HudLivesX); W(HudDigitCursorX,r->bp);
        CALL(RedrawChangedTwoDigitNumber,RefreshHudAndTimerBar,0x22);
    }
    r->ax=R(ScoreLowWord); r->dx=R(ScoreHighWord);
    sub16(r,r->dx,15,0);
    if(r->dx==15) sub16(r,r->ax,0x423f,0);
    if(r->dx>15 || (r->dx==15 && r->ax>0x423f)) {
        r->dx=15; r->ax=0x423f; W(ScoreLowWord,r->ax); W(ScoreHighWord,r->dx);
    }
    r->bx=R(HudCachedScoreLow); r->cx=R(HudCachedScoreHigh);
    sub16(r,r->ax,r->bx,0);
    if(r->ax==r->bx) sub16(r,r->dx,r->cx,0);
    if(r->ax!=r->bx || r->dx!=r->cx) {
        W(HudCachedScoreLow,r->ax); W(HudCachedScoreHigh,r->dx);
        r->bp=R(HudScoreX); W(HudDigitCursorX,r->bp);
        CALL(RedrawChangedSixDigitNumber,RefreshHudAndTimerBar,0x73);
        goto timer;
    }
    set_al(r,B(RemainingPassengerJourneys)); set_bl(r,B(HudCachedLevelCounter));
    cmp8(r,(uint8_t)r->ax,(uint8_t)r->bx);
    if((uint8_t)r->ax!=(uint8_t)r->bx) {
        WB(HudCachedLevelCounter,r->ax); r->bp=R(HudLevelCounterX); W(HudDigitCursorX,r->bp);
        CALL(RedrawChangedTwoDigitNumber,RefreshHudAndTimerBar,0x92);
    }
    r->ax=R(PlayerCarriedKinds); sub16(r,r->ax,R(HudCachedPlayerOneIconState),0);
    if(r->ax!=R(HudCachedPlayerOneIconState)) {
        W(HudCachedPlayerOneIconState,r->ax); r->ax=add16(r,r->ax,0xb2,0);
        r->bx=R(HudPlayerOneIconX); r->cx=193;
        CALL(DrawTransparentSprite,RefreshHudAndTimerBar,0xae);
        r->ax=add16(r,R(PlayerDestinationIcons),0xb7,0); r->bx=R(HudPlayerOneDestinationX);
        CALL(DrawTransparentSprite,RefreshHudAndTimerBar,0xbb);
        goto timer;
    }
    sub16(r,R(PlayerCount),2,0);
    if(R(PlayerCount)==2) {
        r->ax=R(PlayerTwoPassengerIconState); sub16(r,r->ax,R(HudCachedPlayerTwoIconState),0);
        if(r->ax!=R(HudCachedPlayerTwoIconState)) {
            W(HudCachedPlayerTwoIconState,r->ax); r->ax=add16(r,r->ax,0xbf,0);
            r->bx=R(HudPlayerTwoIconX); r->cx=193;
            CALL(DrawTransparentSprite,RefreshHudAndTimerBar,0xe4);
            r->ax=add16(r,R(PlayerTwoDestinationIconIndex),0xc4,0); r->bx=R(HudPlayerTwoDestinationX);
            CALL(DrawTransparentSprite,RefreshHudAndTimerBar,0xf1);
            goto timer;
        }
    }
    r->bp=R(HudFareX); W(HudDigitCursorX,r->bp);
    sub16(r,R(PlayerCarriedKinds),0,0);
    if(R(PlayerCarriedKinds)) { r->di=logic(r,0,16); r->ax=RI(PlayerPassengerFares,r->di); goto fare; }
    sub16(r,R(PlayerCount),2,0);
    if(R(PlayerCount)==2) {
        sub16(r,R(PlayerTwoPassengerIconState),0,0);
        if(R(PlayerTwoPassengerIconState)) { r->di=2; r->ax=RI(PlayerPassengerFares,r->di); goto fare; }
    }
    cmp8(r,B(HudFareClearPending),0);
    if(!B(HudFareClearPending)) goto multiplier;
    r->ax=logic(r,0,16);
fare:
    r->bx=R(HudCachedFare); sub16(r,r->ax,r->bx,0);
    if(r->ax!=r->bx) { W(HudCachedFare,r->ax); CALL(RedrawChangedFourDigitNumber,RefreshHudAndTimerBar,0x143); }
    WB(HudFareClearPending,0);
multiplier:
    set_al(r,B(ScoreMultiplier)); set_bl(r,B(HudCachedMultiplier));
    cmp8(r,(uint8_t)r->ax,(uint8_t)r->bx);
    if((uint8_t)r->ax!=(uint8_t)r->bx) {
        WB(HudCachedMultiplier,r->ax); r->bp=R(HudMultiplierX); W(HudDigitCursorX,r->bp);
        CALL(RedrawChangedTwoDigitNumber,RefreshHudAndTimerBar,0x165);
    }
timer:
    r->ax=R(LevelTimer); sub16(r,r->ax,0,0);
    if((int16_t)r->ax<0) {
        W(LevelTimer,0xffff); sub16(r,R(ScreenFadeStep),0,0);
        if((int16_t)R(ScreenFadeStep)>=0) {
            r->ax=0xfffe; W(ScreenFadeStep,r->ax); W(ScreenFadeLevel,add16(r,R(ScreenFadeLevel),r->ax,0));
        }
        return UGH_OK;
    }
    push(r,r->ds); r->dx=logic(r,0,16);
    uint16_t divisor=R(TimerBarDivisor); if(!divisor) return UGH_UNSUPPORTED;
    r->dx=(uint16_t)(r->ax%divisor); r->ax=(uint16_t)(r->ax/divisor); push(r,r->ax);
    sub16(r,r->ax,R(CachedTimerBarWidth),0);
    if(r->ax==R(CachedTimerBarWidth)) goto timer_done;
    if((int16_t)r->ax<(int16_t)R(CachedTimerBarWidth)) {
        r->bp=r->ax; r->bx=logic(r,r->ax&3,16);
        r->dx=0x3c4; set_al(r,2); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=0x3c5; set_al(r,rd8(r->ds,(uint16_t)(D(VgaSinglePlaneMasks)+r->bx)));
        platform_out(r->dx,1,(uint8_t)r->ax); r->bp>>=2;
        r->si=R(TimerBarPointer); r->ds=rd16(r->ds,D(TimerBarPointer)+2);
        r->si=add16(r,r->si,r->bp,0); set_al(r,(uint8_t)logic(r,0,8));
        wr8(r->ds,r->si,(uint8_t)r->ax); wr8(r->ds,(uint16_t)(r->si+96),(uint8_t)r->ax);
        wr8(r->ds,(uint16_t)(r->si+192),(uint8_t)r->ax);
        set_al(r,15); platform_out(r->dx,1,(uint8_t)r->ax);
    } else {
        r->di=(uint16_t)(R(CachedTimerBarWidth)>>2); r->ax=dec16(r,r->ax);
        r->bp=r->ax; r->bx=logic(r,r->ax&3,16);
        r->dx=0x3c4; set_al(r,2); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=0x3c5; set_al(r,rd8(r->ds,(uint16_t)(D(VgaCumulativePlaneMasks)+r->bx)));
        platform_out(r->dx,1,(uint8_t)r->ax); r->bp>>=2;
        r->si=R(TimerBarPointer); r->ds=rd16(r->ds,D(TimerBarPointer)+2);
        r->si=add16(r,r->si,r->bp,0); set_al(r,50);
        wr8(r->ds,r->si,(uint8_t)r->ax); wr8(r->ds,(uint16_t)(r->si+96),(uint8_t)r->ax);
        wr8(r->ds,(uint16_t)(r->si+192),(uint8_t)r->ax);
        set_al(r,15); platform_out(r->dx,1,(uint8_t)r->ax);
        r->bp=sub16(r,r->bp,r->di,0);
        if(r->bp) {
            set_al(r,50);
            do {
                r->si=dec16(r,r->si); wr8(r->ds,r->si,(uint8_t)r->ax);
                wr8(r->ds,(uint16_t)(r->si+96),(uint8_t)r->ax);
                wr8(r->ds,(uint16_t)(r->si+192),(uint8_t)r->ax);
                r->bp=dec16(r,r->bp);
            } while(r->bp);
        }
    }
timer_done:
    r->ax=pop(r); r->ds=pop(r); W(CachedTimerBarWidth,r->ax); return UGH_OK;
}

static void lodsw(Regs *r) { r->ax=rd16(r->ds,r->si); r->si=(uint16_t)(r->si+2*step(r)); }
/* DS level tables and all output state; no cdecl arguments. ES becomes DGROUP,
 * DF clears in ICE; other general registers destroyed, SS/SP unchanged.
 * Copies record backwards (13 words) then 160 map words. Every list is consumed
 * from live RAM: platform terminates on ANY sign bit, actors/enemies only FFFF.
 * Positions and signed scaling wrap; descriptor identity branches are literal
 * original addresses expressed with generated data macros. Stores callback
 * addresses only, never invokes the other packages' enemy/actor handlers.
 * Rain initialization performs 193 respawns and 577 advances if direction !=0.
 * No hardware/DOS effects. Final flags CMP direction,0 or final DEC SI.
 * The two level-start X words are already X32; their Y words are scaled as-is. */
/* TRANSLATES GAME:LoadCurrentLevelState */
EXPORT int c_LoadCurrentLevelState(Regs *r) {
    r->bx=(uint16_t)((R(PlayerCount)-1u)*2u); r->bx=RI(LevelOrderTables,r->bx);
    r->si=(uint16_t)(R(CurrentLevelIndex)*2u); r->bx=rd16(r->ds,(uint16_t)(r->bx+r->si));
    r->si=24;
    do {
        r->ax=rd16(r->ds,(uint16_t)(r->bx+r->si)); WI(CurrentLevelRecord,r->si,r->ax);
        r->si=sub16(r,r->si,2,0);
    } while(!(r->si&0x8000));
    wr16(r->cs,G(RendererScratchWord),r->ax); push(r,r->ds);
    r->si=R(CompressedTileMapsPointer); r->ds=rd16(r->ds,D(CompressedTileMapsPointer)+2);
    CALL(UnpackIceToScratch,LoadCurrentLevelState,0x2e);
    r->ds=r->es; r->si=rd16(r->cs,G(RendererScratchWord));
    r->dx=DATA_SEG; r->es=r->dx; r->di=D(Data_264C); r->cx=160;
    do {
        wr16(r->es,r->di,rd16(r->ds,r->si));
        r->si=(uint16_t)(r->si+2*step(r)); r->di=(uint16_t)(r->di+2*step(r)); r->cx--;
    } while(r->cx);
    r->ds=pop(r);
    r->ax=sub16(r,R(LevelPlayerOneStartX),512,0); W(PlayerX32,r->ax);
    r->ax=sar(r->ax,5); W(PlayerPixelX,r->ax); W(PlayerCachedPixelX,r->ax);
    r->ax=R(LevelPlayerOneStartY); CALL(ScaleLevelYToThreeQuarters,LoadCurrentLevelState,0x5b);
    r->ax=sub16(r,r->ax,320,0); W(PlayerY32,r->ax); r->ax=sar(r->ax,5);
    W(PlayerYPixels,r->ax); W(PlayerCachedPixelY,r->ax);
    r->ax=sub16(r,R(LevelPlayerTwoStartX),512,0); W(PlayerTwoFixedX,r->ax);
    r->ax=sar(r->ax,5); W(PlayerTwoPixelX,r->ax); W(PlayerTwoCachedPixelX,r->ax);
    r->ax=R(LevelPlayerTwoStartY); CALL(ScaleLevelYToThreeQuarters,LoadCurrentLevelState,0x82);
    r->ax=sub16(r,r->ax,320,0); W(PlayerTwoFixedY,r->ax); r->ax=sar(r->ax,5);
    W(SecondPlayerYPixels,r->ax); W(PlayerTwoCachedPixelY,r->ax);
    r->ax=0xffff;
    W(PlayerPlatformIndices,r->ax); W(ds_27FA,r->ax);
    W(PlayerAnimationCountdowns,r->ax); W(PlayerTwoAnimationCountdown,r->ax);
    W(PlayerSpriteIds,218); W(PlayerTwoSpriteId,224);
    W(HudCachedPlayerOneIconState,r->ax); W(HudCachedPlayerTwoIconState,r->ax); WB(HudFareClearPending,r->ax);
    r->ax=0;
    W(PlayerCarriedKinds,r->ax); W(PlayerTwoPassengerIconState,r->ax);
    W(PlayerDestinationIcons,r->ax); W(PlayerTwoDestinationIconIndex,r->ax);
    W(PlayerPassengerFares,r->ax); W(PlayerTwoFare,r->ax);
    W(PlayerHorizontalVelocities,r->ax); W(ds_2812,r->ax);
    W(PlayerVerticalVelocities,r->ax); W(ds_2816,r->ax);
    r->ax=R(WaterY32); CALL(ScaleLevelYToThreeQuarters,LoadCurrentLevelState,0xda);
    sub16(r,r->ax,0x17e0,0); if(r->ax>0x17e0) r->ax=0x17e0;
    W(WaterY32,r->ax); r->ax=sar(r->ax,5); W(WaterYPixels,r->ax); W(PreviousWaterSurfaceY,r->ax);
    r->si=R(LevelPlatformList); r->di=logic(r,0,16);
    for(;;) {
        lodsw(r); WI(PlatformLeftEdges,r->di,r->ax); r->ax=logic(r,r->ax,16);
        if(r->ax&0x8000) break;
        lodsw(r); WI(PlatformRightEdges,r->di,r->ax);
        lodsw(r); CALL(ScaleLevelYToThreeQuarters,LoadCurrentLevelState,0x10d); WI(PlatformHeights,r->di,r->ax);
        lodsw(r); WI(PlatformArrivalPointsX,r->di,r->ax);
        lodsw(r); WI(PlatformWaitingPointsX,r->di,r->ax);
        lodsw(r); WI(PlatformSpawnX,r->di,r->ax);
        lodsw(r); WI(PlatformDestinationIcons,r->di,r->ax);
        r->si=(uint16_t)(r->si+2); WI(PlatformActorOccupants,r->di,0xffff); r->di=(uint16_t)(r->di+2);
    }
    r->si=R(LevelActorList); r->di=logic(r,0,16);
    for(;;) {
        lodsw(r); WI(ActorDescriptors,r->di,r->ax); sub16(r,r->ax,0xffff,0);
        if(r->ax==0xffff) break;
        r->bx=r->ax; lodsw(r); WI(ActorInitialPlatformIndices,r->di,r->ax);
        lodsw(r); WI(ActorJourneyCursors,r->di,r->ax); r->ax=0xffff;
        WI(ActorSpriteIds,r->di,r->ax); WI(ActorEraseSprite,r->di,r->ax);
        WI(ActorOverlayOrScriptCallbacks,r->di,r->ax); WI(ActorEraseOverlaySprite,r->di,r->ax);
        if(r->bx!=D(Data_78DC)) {
            r->ax=rd16(r->ds,(uint16_t)(r->bx+8)); WI(ActorUpdateOrScriptCursor,r->di,r->ax);
        } else {
            r->ax=rd16(r->ds,(uint16_t)(r->bx+16)); WI(ActorUpdateOrScriptCursor,r->di,r->ax);
            r->bx=(uint16_t)(RI(ActorInitialPlatformIndices,r->di)*2u);
            r->ax=(uint16_t)((RI(PlatformSpawnX,r->bx)-8u)*32u); WI(ActorX32,r->di,r->ax);
            r->ax=(uint16_t)((RI(PlatformHeights,r->bx)-11u)*32u); WI(ActorY32,r->di,r->ax);
        }
        r->di=(uint16_t)(r->di+2);
    }
    r->si=R(LevelEnemyList); r->di=logic(r,0,16);
    for(;;) {
        lodsw(r); WI(EnemyDescriptors,r->di,r->ax); sub16(r,r->ax,0xffff,0);
        if(r->ax==0xffff) break;
        if(r->ax==D(Data_76E4)) {
            lodsw(r); WI(EnemyPlatformIndices,r->di,r->ax); r->bx=(uint16_t)(r->ax*2u);
            r->ax=(uint16_t)((RI(PlatformSpawnX,r->bx)-16u)*32u); WI(EnemyX32,r->di,r->ax);
            r->ax=(uint16_t)((RI(PlatformHeights,r->bx)-24u)*32u); WI(EnemyY32,r->di,r->ax);
            lodsw(r); WI(EnemyAnimationOrDropLists,r->di,r->ax); WI(EnemyStateCallbacks,r->di,G(InitializeFruitTreeAnimation));
        } else if(r->ax==D(Data_7630)) {
            r->si=(uint16_t)(r->si+2); lodsw(r);
            CALL(ScaleLevelSpeedToThreeHalves,LoadCurrentLevelState,0x205); WI(EnemyInitialDelays,r->di,r->ax);
            lodsw(r); WI(EnemyHorizontalSpeeds,r->di,r->ax); WI(EnemyDirectionOrTargetPlayer,r->di,1);
            WI(EnemyStateCallbacks,r->di,G(BeginBirdDelay));
        } else if(r->ax==D(Data_76A8)) {
            lodsw(r); r->ax=(uint16_t)(r->ax*32u); WI(EnemyX32,r->di,r->ax);
            lodsw(r); r->ax=(uint16_t)(r->ax*32u);
            CALL(ScaleLevelYToThreeQuarters,LoadCurrentLevelState,0x233);
            r->ax=sub16(r,r->ax,704,0); WI(EnemyY32,r->di,r->ax); r->si=(uint16_t)(r->si+4);
            WI(EnemyStateCallbacks,r->di,G(loc_295B));
        } else {
            lodsw(r); WI(EnemyPlatformIndices,r->di,r->ax); r->bx=(uint16_t)(r->ax*2u);
            r->ax=(uint16_t)((RI(PlatformSpawnX,r->bx)-16u)*32u); WI(EnemyX32,r->di,r->ax);
            r->ax=(uint16_t)((RI(PlatformHeights,r->bx)-22u)*32u); WI(EnemyY32,r->di,r->ax);
            r->si=(uint16_t)(r->si+2); lodsw(r); r->ax=(uint16_t)-sar(r->ax,2);
            r->ax=(uint16_t)(r->ax+rd16(r->ds,(uint16_t)(r->si-2))); r->ax=(uint16_t)-r->ax;
            WI(EnemyHorizontalSpeeds,r->di,r->ax); WI(EnemyDirectionOrTargetPlayer,r->di,0);
            WI(EnemyStateCallbacks,r->di,G(BeginDinosaurPatrol));
        }
        r->di=(uint16_t)(r->di+2);
    }
    r->bx=384; r->ax=logic(r,0,16);
    do {
        WI(RainParticleOffsets,r->bx,r->ax); WI(RainPreviousOffsets,r->bx,r->ax);
        r->bx=sub16(r,r->bx,2,0);
    } while(!(r->bx&0x8000));
    cmp8(r,B(LevelRainDirection),0);
    if(B(LevelRainDirection)) {
        r->bx=384;
        do {
            CALL(RespawnRainParticle,LoadCurrentLevelState,0x2b0);
            r->bx=sub16(r,r->bx,2,0);
        } while(!(r->bx&0x8000));
        r->si=576;
        do {
            CALL(AdvanceRainParticles,LoadCurrentLevelState,0x2bb); r->si=dec16(r,r->si);
        } while(!(r->si&0x8000));
    }
    return UGH_OK;
}
