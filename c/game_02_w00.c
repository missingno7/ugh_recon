#include "ugh.h"

/* All entries are near, have no stack arguments, preserve SS:SP, CS, DS,
 * BP and IF/DF, and use the incoming DS/ES rather than implicit DGROUP.
 * Arithmetic outputs are specified per entry below; undefined AF after OR
 * and undefined shift flags are not promises. No DOS or port operations occur.
 */

/* In BX=word-array byte index. Out AX unchanged unless sprite==7FFF;
 * then AX=FFFC, fade step=-4 and level wraps after adding -4. All other
 * registers survive. Flags are CMP or ADD, including the original carry.
 */
/* TRANSLATES GAME:StartDemoFadeWhenSpriteHidden */
EXPORT int c_StartDemoFadeWhenSpriteHidden(Regs *r) {
    uint16_t sprite=rd16(r->ds,(uint16_t)(D(ActorSpriteIds)+r->bx));
    sub16(r,sprite,0x7fff,0);
    if(sprite==0x7fff) {
        r->ax=0xfffc;
        wr16(r->ds,D(ScreenFadeStep),r->ax);
        wr16(r->ds,D(ScreenFadeLevel),
             add16(r,rd16(r->ds,D(ScreenFadeLevel)),r->ax,0));
    }
    return UGH_OK;
}

/* In BX indexes X32. SAR rounds negative X downward, then a signed upper
 * clamp changes AL only (AH can remain nonzero). No lower clamp exists.
 * CS owns the writable far pointer. Out AX, CX=X SAR 5, ES:DI one byte
 * beyond the destination in the incoming DF direction; flags from CMP.
 * BX, DX, SI, BP and DS survive. Only one pointed byte is written.
 */
/* TRANSLATES GAME:SetDemoRevealSpriteWidth */
EXPORT int c_SetDemoRevealSpriteWidth(Regs *r) {
    uint16_t x=rd16(r->ds,(uint16_t)(D(ActorX32)+r->bx));
    r->cx=(uint16_t)((x>>5) | ((x&0x8000) ? 0xf800u : 0));
    r->ax=sub16(r,320,r->cx,0);
    sub16(r,r->ax,127,0);
    if((int16_t)r->ax>127) set_al(r,127);
    r->di=rd16(r->cs,G(DemoRevealWidthPointer));
    r->es=rd16(r->cs,(uint16_t)(G(DemoRevealWidthPointer)+2));
    wr8(r->es,r->di,(uint8_t)r->ax);
    r->di=(uint16_t)(r->di+step(r));
    return UGH_OK;
}

/* An actual unexplained RET seed, not a substitute for IgnoreActorState. */
/* TRANSLATES GAME:loc_0B4E */
EXPORT int c_loc_0B4E(Regs *r) {
    (void)r;
    return UGH_OK;
}

/* The three descending loops reset 5 enemy, 16 actor and 12 falling-item
 * current/erase sprite words. Nothing clears adjacent positions or cursors.
 * Out AX=FFFF, SI=FFFE, flags from 0-2; other registers survive.
 */
/* TRANSLATES GAME:ResetSpriteEraseState */
EXPORT int c_ResetSpriteEraseState(Regs *r) {
    r->ax=0xffff;
    r->si=8;
    do {
        wr16(r->ds,(uint16_t)(D(EnemySpriteIds)+r->si),r->ax);
        wr16(r->ds,(uint16_t)(D(EnemyEraseSprite)+r->si),r->ax);
        r->si=sub16(r,r->si,2,0);
    } while((int16_t)r->si>=0);
    r->si=30;
    do {
        wr16(r->ds,(uint16_t)(D(ActorSpriteIds)+r->si),r->ax);
        wr16(r->ds,(uint16_t)(D(ActorEraseSprite)+r->si),r->ax);
        r->si=sub16(r,r->si,2,0);
    } while((int16_t)r->si>=0);
    r->si=22;
    do {
        wr16(r->ds,(uint16_t)(D(FallingItemSprites)+r->si),r->ax);
        wr16(r->ds,(uint16_t)(D(FallingItemEraseSprite)+r->si),r->ax);
        r->si=sub16(r,r->si,2,0);
    } while((int16_t)r->si>=0);
    return UGH_OK;
}

/* ES:SI need not be VGA. Each effective offset wraps at 16 bits; VGA
 * reads use the existing physical aperture service and update its latches.
 * Out AL=OR of ten samples, CF=OF=0 and SZP describe AL. AH and all other
 * registers survive. Order matters: the last VGA read supplies the latches.
 */
/* TRANSLATES GAME:SamplePlayerCollisionPixels */
EXPORT int c_SamplePlayerCollisionPixels(Regs *r) {
    static const uint16_t delta[]={0,3,5,0x720,0x723,0x725,0x240,0x245,0x480,0x485};
    set_al(r,rd8(r->es,r->si));
    for(unsigned i=1;i<sizeof(delta)/sizeof(delta[0]);i++)
        set_al(r,(uint8_t)logic(r,(uint8_t)r->ax |
               rd8(r->es,(uint16_t)(r->si+delta[i])),8));
    return UGH_OK;
}

/* Local resolver for the two translated callbacks found in real demo data.
 * IgnoreActorState (1C0E), used by other scripts, belongs to game_03_w00:
 * it is deliberately unsupported until that package is available. No fake RET.
 * Reproduce the near CALL frame at this call site. The unlabelled return
 * instruction at 0A19 is +42h from the generated AdvanceDemoScripts entry.
 */
static int demo_callback(Regs *r, uint16_t target) {
    int status;
    if(r->cs!=GAME_SEG) return UGH_BAD_CALLBACK;
    r->sp=(uint16_t)(r->sp-2);
    wr16(r->ss,r->sp,(uint16_t)(G(AdvanceDemoScripts)+0x42));
    if(target==G(StartDemoFadeWhenSpriteHidden)) status=c_StartDemoFadeWhenSpriteHidden(r);
    else if(target==G(SetDemoRevealSpriteWidth)) status=c_SetDemoRevealSpriteWidth(r);
    else if(target==G(loc_0B4E)) status=c_loc_0B4E(r);
    else status=UGH_BAD_CALLBACK;
    r->sp=(uint16_t)(r->sp+2);
    return status;
}

/* In DS owns the FFFF-terminated cursor array, scripts and parallel state.
 * Countdown DEC preserves CF; zero reloads its period (including zero).
 * Negative script words install a signed repeat count and restart pointer.
 * 8000 increments a nonzero repeat count toward zero; zero pins that marker
 * and marks completion. Sprite deltas are signed bytes times four, wrapping.
 * LODS follows DF even on malformed/reverse streams. No capacity guard/clamp.
 * Out BX=sentinel byte index, SI=FFFF and flags from CMP SI,FFFF. AX and any
 * callback outputs flow through; DX/BP and DS survive supported callbacks.
 * Unknown callback targets fail explicitly, never pretend success.
 */
/* TRANSLATES GAME:AdvanceDemoScripts */
EXPORT int c_AdvanceDemoScripts(Regs *r) {
    unsigned budget=2000000;
    r->bx=logic(r,0,16);
    for(;;) {
        if(!budget--) return UGH_BUDGET;
        r->si=rd16(r->ds,(uint16_t)(D(ActorUpdateOrScriptCursor)+r->bx));
        sub16(r,r->si,0xffff,0);
        if(r->si==0xffff) return UGH_OK;
        uint16_t tick=(uint16_t)(D(ActorAnimationCountdowns)+r->bx);
        uint16_t count=dec16(r,rd16(r->ds,tick));
        wr16(r->ds,tick,count);
        if(!count) {
            r->ax=rd16(r->ds,(uint16_t)(D(ds_2C6D)+r->bx));
            wr16(r->ds,tick,r->ax);
            for(;;) {
                if(!budget--) return UGH_BUDGET;
                r->ax=rd16(r->ds,r->si);
                r->si=(uint16_t)(r->si+2*step(r));
                sub16(r,r->ax,0,0);
                if((int16_t)r->ax>=0) {
                    wr16(r->ds,(uint16_t)(D(ActorSpriteIds)+r->bx),r->ax);
                    for(unsigned axis=0;axis<2;axis++) {
                        int16_t delta=(int8_t)rd8(r->ds,r->si);
                        r->si=(uint16_t)(r->si+step(r));
                        r->ax=(uint16_t)((uint16_t)delta<<2);
                        uint16_t pos=(uint16_t)((axis ? D(ActorY32) : D(ActorX32))+r->bx);
                        wr16(r->ds,pos,add16(r,rd16(r->ds,pos),r->ax,0));
                    }
                    int status=demo_callback(r,rd16(r->ds,
                                  (uint16_t)(D(ActorOverlayOrScriptCallbacks)+r->bx)));
                    if(status) return status;
                    break;
                }
                sub16(r,r->ax,0x8000,0);
                if(r->ax!=0x8000) {
                    wr16(r->ds,(uint16_t)(D(ds_2ACD)+r->bx),r->ax);
                    wr16(r->ds,(uint16_t)(D(ds_2A2D)+r->bx),r->si);
                    continue;
                }
                r->ax=logic(r,rd16(r->ds,(uint16_t)(D(ds_2ACD)+r->bx)),16);
                if(r->ax) {
                    uint16_t cf=r->flags&CF;
                    r->ax=add16(r,r->ax,1,0); flag(r,CF,cf);
                    wr16(r->ds,(uint16_t)(D(ds_2ACD)+r->bx),r->ax);
                    if(r->ax) r->si=rd16(r->ds,(uint16_t)(D(ds_2A2D)+r->bx));
                } else {
                    r->si=sub16(r,r->si,2,0);
                    wr16(r->ds,(uint16_t)(D(ActorPlatformOrScriptDone)+r->bx),0xffff);
                    break;
                }
            }
            wr16(r->ds,(uint16_t)(D(ActorUpdateOrScriptCursor)+r->bx),r->si);
        }
        r->bx=add16(r,r->bx,2,0);
    }
}

/* DispatchActorUpdates is intentionally absent: every real nonempty actor
 * table calls other packages of this wave. See the report's unresolved edges.
 */
