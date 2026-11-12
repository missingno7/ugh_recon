#include "platform.h"

/* All entries are near, without arguments. DS owns the parallel state arrays;
 * CS owns page pointers. SS:SP and IF/DF survive. Arithmetic is word-sized.
 * Calls retain the measured original return words, including the tail transfer
 * from initialization into the already translated script interpreter. */
#define R(n) rd16(r->ds,D(n))
#define W(n,v) wr16(r->ds,D(n),(uint16_t)(v))
#define RX(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define WX(n,i,v) wr16(r->ds,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define CALL(n,ret) do { int status=ugh_call_near(G(n),ret,r); if(status) return status; } while(0)
static uint16_t sar(uint16_t v,unsigned n) {
    return (uint16_t)((v>>n)|((v&0x8000u) ? (0xffffu<<(16-n)) : 0));
}
static void push(Regs *r,uint16_t v) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v); }
static uint16_t pop(Regs *r) { uint16_t v=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return v; }

/* DS:SI vector; each header is pixel X,Y,period,near callback. Shifts wrap,
 * and the whole vector is read before ResetSpriteEraseState destroys SI.
 * No array bound or malformed-vector normalization. Out follows AdvanceDemoScripts:
 * BX=sentinel index, SI=FFFF; AX and callback effects flow through. */
/* TRANSLATES GAME:InitializeDemoScripts */
EXPORT int c_InitializeDemoScripts(Regs *r) {
    r->bx=logic(r,0,16);
    for(unsigned budget=0;;budget++) {
        if(budget==32768) return UGH_BUDGET;
        r->di=rd16(r->ds,(uint16_t)(r->bx+r->si));
        sub16(r,r->di,0xffff,0);
        if(r->di==0xffff) break;
        r->ax=rd16(r->ds,r->di);
        WX(ActorPixelX,r->bx,r->ax); WX(ActorPreviousDrawX,r->bx,r->ax);
        r->ax=(uint16_t)(r->ax<<5); WX(ActorX32,r->bx,r->ax);
        r->ax=rd16(r->ds,(uint16_t)(r->di+2));
        WX(ActorPixelY,r->bx,r->ax); WX(ActorPreviousDrawY,r->bx,r->ax);
        r->ax=(uint16_t)(r->ax<<5); WX(ActorY32,r->bx,r->ax);
        r->ax=rd16(r->ds,(uint16_t)(r->di+4)); WX(ds_2C6D,r->bx,r->ax);
        r->ax=rd16(r->ds,(uint16_t)(r->di+6)); WX(ActorOverlayOrScriptCallbacks,r->bx,r->ax);
        r->di=add16(r,r->di,8,0); WX(ActorUpdateOrScriptCursor,r->bx,r->di);
        WX(ActorAnimationCountdowns,r->bx,1);
        r->ax=logic(r,0,16); WX(ds_2ACD,r->bx,r->ax); WX(ActorPlatformOrScriptDone,r->bx,r->ax);
        r->bx=add16(r,r->bx,2,0);
    }
    WX(ActorUpdateOrScriptCursor,r->bx,r->di);
    CALL(ResetSpriteEraseState,(uint16_t)(G(InitializeDemoScripts)+0x60));
    return ugh_dispatch(r->cs,G(AdvanceDemoScripts),r);
}

/* DS arrays; visible sprites update both cache generations BEFORE clipping.
 * Only upper signed bounds are checked. AX/BX/CX are the final slot's work
 * values, SI=sentinel index, BP may be changed by the real sprite renderer.
 * DX/DI/DS/ES survive; final CMP sentinel supplies arithmetic flags. */
/* TRANSLATES GAME:DrawDemoSprites */
EXPORT int c_DrawDemoSprites(Regs *r) {
    r->si=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        uint16_t cursor=RX(ActorUpdateOrScriptCursor,r->si);
        sub16(r,cursor,0xffff,0); if(cursor==0xffff) return UGH_OK;
        r->ax=RX(ActorSpriteIds,r->si); sub16(r,r->ax,0x7fff,0);
        if(r->ax!=0x7fff) {
            r->bx=RX(ActorPixelX,r->si); r->cx=RX(ActorPixelY,r->si);
            WX(ActorPreviousDrawX,r->si,r->bx); WX(ActorPreviousDrawY,r->si,r->cx);
            r->bx=sar(RX(ActorX32,r->si),5); WX(ActorPixelX,r->si,r->bx);
            r->cx=sar(RX(ActorY32,r->si),5); WX(ActorPixelY,r->si,r->cx);
            sub16(r,r->bx,320,0);
            if((int16_t)r->bx<320) {
                sub16(r,r->cx,192,0);
                if((int16_t)r->cx<192) { CALL(DrawTransparentSprite,(uint16_t)(G(DrawDemoSprites)+0x53)); }
            }
        }
        r->si=add16(r,r->si,2,0);
    }
    return UGH_BUDGET;
}

/* Keyboard-mode action words retain their stale high bytes. Joystick words
 * are cleared then decremented to FFFF; signed inclusive thresholds apply.
 * The original JE at 108B visits slot 1 only when PlayerCount==2.
 * Out AL scan/AH XOR change; BX/SI and joystick scratch outputs flow through;
 * final flags are CMP BX,PlayerCount, DX/DI/BP survive without sampling. */
/* TRANSLATES GAME:PollPlayerControls */
EXPORT int c_PollPlayerControls(Regs *r) {
    CALL(PollKeyboardScanChange,(uint16_t)(G(PollPlayerControls)+3));
    logic(r,R(PlayerOneControlMode),16);
    if((int16_t)R(PlayerOneControlMode)>=0) { CALL(SampleJoystickAxesAndButtons,(uint16_t)(G(PollPlayerControls)+0x26)); }
    else {
        logic(r,R(PlayerTwoControlMode),16);
        if((int16_t)R(PlayerTwoControlMode)>=0) {
            sub16(r,R(PlayerCount),2,0);
            if(R(PlayerCount)==2) { CALL(SampleJoystickAxesAndButtons,(uint16_t)(G(PollPlayerControls)+0x26)); }
        }
    }
    r->bx=logic(r,0,16);
    do {
        r->si=(uint16_t)(RX(PlayerOneControlMode,r->bx)<<1);
        logic(r,r->si,16);
        if((int16_t)r->si>=0) {
            r->ax=logic(r,0,16);
            WX(PlayerUpInput,r->bx,0); WX(PlayerDownInput,r->bx,0);
            WX(PlayerLeftInput,r->bx,0); WX(PlayerRightInput,r->bx,0); WX(PlayerActionInput,r->bx,0);
            r->ax=RX(FirstJoystickXCount,r->si);
            if((int16_t)r->ax<=(int16_t)RX(JoystickLeftThresholds,r->si)) WX(PlayerLeftInput,r->bx,0xffff);
            else if((int16_t)r->ax>=(int16_t)RX(JoystickRightThresholds,r->si)) WX(PlayerRightInput,r->bx,0xffff);
            r->ax=RX(FirstJoystickYCount,r->si);
            if((int16_t)r->ax<=(int16_t)RX(JoystickUpThresholds,r->si)) WX(PlayerUpInput,r->bx,0xffff);
            else if((int16_t)r->ax>=(int16_t)RX(JoystickDownThresholds,r->si)) WX(PlayerDownInput,r->bx,0xffff);
            if(RX(JoystickButtonBits,r->si)) WX(PlayerActionInput,r->bx,0xffff);
        }
        r->bx=add16(r,r->bx,2,0); sub16(r,r->bx,R(PlayerCount),0);
    } while(r->bx==R(PlayerCount));
    set_al(r,rd8(r->ds,D(CurrentKeyboardScanCode)));
    set_ah(r,rd8(r->ds,D(KeyboardScanCodeChangeBits)));
    return UGH_OK;
}

/* Compute the same signed IMUL low/high words and the wrapped plane address.
 * The second invocation leaves DX=IMUL high word, AFTER the port selection. */
static void collision_address(Regs *r) {
    r->ax=RX(PlayerYPixels,r->bx);
    int32_t product=(int32_t)(int16_t)r->ax*(int16_t)R(VgaRowStrideBytes);
    r->ax=(uint16_t)product; r->dx=(uint16_t)((uint32_t)product>>16);
    r->si=RX(PlayerPixelX,r->bx); r->si=(uint16_t)(r->si+5); r->si=sar(r->si,2);
    r->ax=(uint16_t)(r->ax+r->si);
    r->si=rd16(r->cs,G(BackgroundPagePointer));
    r->es=rd16(r->cs,(uint16_t)(G(BackgroundPagePointer)+2));
    r->si=(uint16_t)(r->si+r->ax);
}
static void select_collision_plane(Regs *r) {
    r->dx=0x3ce; set_al(r,4); platform_out(r->dx,1,(uint8_t)r->ax);
    r->dx=(uint16_t)(r->dx+1);
    r->ax=(uint16_t)(RX(PlayerPixelX,r->bx)+0x25); r->ax=logic(r,r->ax&3,16);
}
static uint16_t limit_velocity(uint16_t v) {
    if((int16_t)v < -6144) return 0xe800;
    if((int16_t)v > 6144) return 0x1800;
    return v;
}
static void reflect_velocity(Regs *r,uint16_t offset) {
    r->ax=(uint16_t)(0-rd16(r->ds,offset)); r->ax=sar(r->ax,1);
    wr16(r->ds,offset,r->ax); r->ax=(uint16_t)(r->ax<<1);
    if((int16_t)r->ax<0) r->ax=(uint16_t)(0-r->ax);
}

/* Player BX is preserved. Out AX/CX/DX/SI/DI/BP/ES and arithmetic flags
 * follow the original instruction ordering. VGA read-map selection/latches
 * and ordered ports are observable. No host pixel cache exists.
 * Left/up scans intentionally re-read one address; right/down scans advance.
 * Impact comparisons, clamps and SAR rounding are signed with word wrapping.
 * There is no timer saturation, velocity friction or lower-level clipping. */
/* TRANSLATES GAME:MovePlayerWithVgaCollisions */
EXPORT int c_MovePlayerWithVgaCollisions(Regs *r) {
    W(LevelTimer,dec16(r,R(LevelTimer)));
    r->ax=logic(r,0,16); WX(PlayerImpactMagnitude,r->bx,0); WX(PlayerThrustAnimationRate,r->bx,0);
    r->cx=(uint16_t)(RX(PlayerYPixels,r->bx)-R(WaterYPixels)+18);
    if((int16_t)r->cx>0) r->cx=(uint16_t)((r->cx&255)|0x100);
    if((int16_t)RX(PlayerPlatformIndices,r->bx)<0) {
        if((int8_t)(r->cx>>8)<0) {
            set_al(r,rd8(r->ds,D(LevelRainDirection)));
            if((uint8_t)r->ax) {
                set_ah(r,0); r->ax=(uint16_t)((((r->ax-1)*2)-1)*32);
                WX(PlayerHorizontalVelocities,r->bx,RX(PlayerHorizontalVelocities,r->bx)+r->ax);
                r->ax=sar(r->ax,1); if((int16_t)r->ax<0) r->ax=(uint16_t)(0-r->ax);
                WX(PlayerVerticalVelocities,r->bx,RX(PlayerVerticalVelocities,r->bx)+r->ax);
            }
        }
        r->ax=RX(PlayerHorizontalVelocities,r->bx);
        if(RX(PlayerLeftInput,r->bx)) {
            r->ax=(uint16_t)(r->ax-63); WX(PlayerThrustAnimationRate,r->bx,RX(PlayerThrustAnimationRate,r->bx)+63);
        } else if(RX(PlayerRightInput,r->bx)) {
            r->ax=(uint16_t)(r->ax+63); WX(PlayerThrustAnimationRate,r->bx,RX(PlayerThrustAnimationRate,r->bx)+63);
        }
        r->ax=limit_velocity(r->ax); WX(PlayerHorizontalVelocities,r->bx,r->ax);
        r->ax=(uint16_t)(sar(r->ax,6)+RX(PlayerX32,r->bx));
        if((int16_t)r->ax<-512) { r->ax=0xfe00; WX(PlayerHorizontalVelocities,r->bx,0); }
        else if((int16_t)r->ax>9728) { r->ax=0x2600; WX(PlayerHorizontalVelocities,r->bx,0); }
        r->di=r->ax; push(r,r->cx);
        collision_address(r); select_collision_plane(r);
        r->cx=(uint16_t)((r->cx&0xff00)|(uint8_t)r->ax); platform_out(r->dx,1,(uint8_t)r->ax);
        r->bp=r->di; r->ax=sar(r->di,5);
        if(r->ax!=RX(PlayerPixelX,r->bx)) {
            r->bp=RX(PlayerX32,r->bx);
            int hit=0;
            if((int16_t)r->di<=(int16_t)r->bp) {
                uint8_t cl=(uint8_t)((uint8_t)r->cx-1);
                if((int8_t)cl<0) { cl&=3; r->si=(uint16_t)(r->si-1); }
                r->cx=(uint16_t)((r->cx&0xff00)|cl); set_al(r,cl); platform_out(r->dx,1,cl);
                do {
                    CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x12f));
                    if(r->flags&SF) { r->bp=(uint16_t)((r->bp&0xffe0)+32); hit=1; break; }
                    r->bp=(uint16_t)(r->bp-32);
                } while((int16_t)r->bp>(int16_t)r->di);
            } else {
                do {
                    uint8_t cl=(uint8_t)((uint8_t)r->cx+1);
                    if(cl>=4) { cl&=3; r->si=(uint16_t)(r->si+1); }
                    r->cx=(uint16_t)((r->cx&0xff00)|cl); set_al(r,cl); platform_out(r->dx,1,cl);
                    CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x159));
                    if(r->flags&SF) { r->bp&=0xffe0; hit=1; break; }
                    r->bp=(uint16_t)(r->bp+32);
                } while((int16_t)r->bp<(int16_t)r->di);
            }
            if(hit) {
                reflect_velocity(r,(uint16_t)(D(PlayerHorizontalVelocities)+r->bx));
                WX(PlayerImpactMagnitude,r->bx,r->ax);
            } else r->bp=r->di;
        }
        WX(PlayerX32,r->bx,r->bp); r->bp=sar(r->bp,5); WX(PlayerPixelX,r->bx,r->bp);
        r->cx=pop(r);
    }
    r->ax=RX(PlayerVerticalVelocities,r->bx);
    int8_t water_state=(int8_t)(r->cx>>8);
    if(water_state>0) {
        W(LevelTimer,R(LevelTimer)-2);
        if((int16_t)r->ax>0) r->ax=(uint16_t)(r->ax-193);
        else { r->ax=(uint16_t)(r->ax-21); WX(PlayerPlatformIndices,r->bx,0xffff); }
    } else {
        if(water_state<0 && (int16_t)RX(PlayerPlatformIndices,r->bx)<0) {
            r->ax=(uint16_t)(r->ax+27); W(LevelTimer,R(LevelTimer)-2);
            if(RX(PlayerDownInput,r->bx)) {
                r->ax=(uint16_t)(r->ax+70); WX(PlayerThrustAnimationRate,r->bx,RX(PlayerThrustAnimationRate,r->bx)+90);
                goto vertical_limit;
            }
        }
        if(RX(PlayerUpInput,r->bx)) {
            W(LevelTimer,R(LevelTimer)-3); r->ax=(uint16_t)(r->ax-70);
            WX(PlayerThrustAnimationRate,r->bx,RX(PlayerThrustAnimationRate,r->bx)+90);
            WX(PlayerPlatformIndices,r->bx,0xffff);
        }
    }
vertical_limit:
    r->ax=limit_velocity(r->ax); WX(PlayerVerticalVelocities,r->bx,r->ax);
    r->ax=(uint16_t)(sar(r->ax,6)+RX(PlayerY32,r->bx));
    if((int16_t)r->ax<-608) { r->ax=0xfda0; WX(PlayerVerticalVelocities,r->bx,0); }
    else if((int16_t)r->ax>6112) { r->ax=0x17e0; WX(PlayerVerticalVelocities,r->bx,0); }
    if(water_state>0) {
        r->dx=(uint16_t)(sar(r->ax,5)-R(WaterYPixels)+18);
        if((int16_t)r->dx<=0) {
            WX(PlayerVerticalVelocities,r->bx,0); r->ax=(uint16_t)((R(WaterYPixels)<<5)-0x240);
        }
    }
    r->di=r->ax; select_collision_plane(r); platform_out(r->dx,1,(uint8_t)r->ax);
    collision_address(r); r->bp=r->di; r->ax=sar(r->di,5);
    if(r->ax!=RX(PlayerYPixels,r->bx)) {
        r->bp=RX(PlayerY32,r->bx); int hit=0;
        if((int16_t)r->di<=(int16_t)r->bp) {
            r->si=(uint16_t)(r->si-0x60);
            do {
                CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x2d4));
                if(r->flags&SF) { r->bp=(uint16_t)((r->bp&0xffe0)+32); hit=1; break; }
                r->bp=(uint16_t)(r->bp-32);
            } while((int16_t)r->bp>(int16_t)r->di);
        } else {
            do {
                r->si=(uint16_t)(r->si+0x60);
                CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x2f1));
                if(r->flags&SF) { r->bp&=0xffe0; hit=1; break; }
                r->bp=(uint16_t)(r->bp+32);
            } while((int16_t)r->bp<(int16_t)r->di);
        }
        if(hit) {
            reflect_velocity(r,(uint16_t)(D(PlayerVerticalVelocities)+r->bx));
            if((int16_t)r->ax>(int16_t)RX(PlayerImpactMagnitude,r->bx)) WX(PlayerImpactMagnitude,r->bx,r->ax);
            if((int16_t)RX(PlayerVerticalVelocities,r->bx)<0) {
                r->ax=RX(PlayerImpactMagnitude,r->bx); r->si=(uint16_t)(R(SelectedDifficulty)<<1);
                if((int16_t)r->ax<(int16_t)RX(PlayerImpactLimits,r->si)) {
                    r->si=0; r->ax=(uint16_t)(sar(r->bp,5)+20);
                    for(unsigned budget=0;;budget++) {
                        if(budget==32768) return UGH_BUDGET;
                        if((int16_t)RX(PlatformLeftEdges,r->si)<0) break;
                        if(RX(PlatformHeights,r->si)==r->ax) {
                            r->cx=(uint16_t)(RX(PlayerPixelX,r->bx)+16);
                            if((int16_t)r->cx>=(int16_t)RX(PlatformLeftEdges,r->si) &&
                               (int16_t)r->cx<=(int16_t)RX(PlatformRightEdges,r->si)) {
                                r->si>>=1; WX(PlayerPlatformIndices,r->bx,r->si); r->ax=logic(r,0,16);
                                WX(PlayerHorizontalVelocities,r->bx,0); WX(PlayerVerticalVelocities,r->bx,0); break;
                            }
                        }
                        r->si=(uint16_t)(r->si+2);
                    }
                }
            }
        } else r->bp=r->di;
    }
    WX(PlayerY32,r->bx,r->bp); r->bp=sar(r->bp,5); WX(PlayerYPixels,r->bx,r->bp);
    r->ax=RX(PlayerImpactMagnitude,r->bx); r->si=(uint16_t)(R(SelectedDifficulty)<<1);
    sub16(r,r->ax,RX(PlayerImpactLimits,r->si),0);
    if((int16_t)r->ax>=(int16_t)RX(PlayerImpactLimits,r->si)) {
        sub16(r,R(ScreenFadeStep),0,0);
        if((int16_t)R(ScreenFadeStep)>=0) {
            r->ax=0xfffe; W(ScreenFadeStep,r->ax); W(ScreenFadeLevel,add16(r,R(ScreenFadeLevel),r->ax,0));
        }
    }
    return UGH_OK;
}
