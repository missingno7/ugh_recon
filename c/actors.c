#include "ugh.h"

/* GAME's actor/enemy state callbacks are near calls. DS is the incoming
 * data bank; BX is a byte index into parallel word arrays, not a record.
 * All adapters preserve CS/DS/ES/SS/SP, IF and DF. Working AX/CX/DX/SI/DI/BP
 * follow the instructions, including stale values on untaken paths.
 * Descriptor offsets below are byte displacements established by GAME.ASM.
 * No platform requests occur in this package. Untranslated callback targets
 * fail explicitly; they are never treated as empty callbacks. */
#define READ(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define WRITE(n,i,v) wr16(r->ds,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define A(n) READ(n,r->bx)
#define W(n,v) WRITE(n,r->bx,v)
#define DESC(n) rd16(r->ds,(uint16_t)(r->si+(n)))

static int state_jump(Regs *r, uint16_t target);
static int tail(Regs *r, unsigned field) { return state_jump(r,DESC(field)); }
static uint16_t shl(Regs *r,uint16_t v,unsigned n) {
    for(unsigned i=0;i<n;i++) { flag(r,CF,v&0x8000u); v=(uint16_t)(v<<1); }
    szp(r,v,16); if(n==1) flag(r,OF,!!(v&0x8000u)^!!(r->flags&CF));
    return v;
}
/* Explicit sign extension avoids implementation-defined right shift. */
static uint16_t sar(Regs *r,uint16_t v,unsigned n) {
    for(unsigned i=0;i<n;i++) { flag(r,CF,v&1); v=(uint16_t)((v>>1)|(v&0x8000u)); }
    szp(r,v,16); if(n==1) flag(r,OF,0); return v;
}
static uint16_t inc(Regs *r,uint16_t v) {
    uint16_t cf=r->flags&CF; v=add16(r,v,1,0); flag(r,CF,cf); return v;
}
static int less(const Regs *r) { return !!(r->flags&SF)!=!!(r->flags&OF); }
static int greater(const Regs *r) { return !(r->flags&ZF) && !less(r); }
static void actor_init(Regs *r,unsigned field) {
    r->si=A(ActorDescriptors); r->ax=DESC(field);
    W(ActorUpdateOrScriptCursor,r->ax);
    W(ActorAnimationByteOffsets,0xfffe); W(ActorAnimationCountdowns,1);
}
static void enemy_init(Regs *r,unsigned field,int load_descriptor) {
    if(load_descriptor) r->si=A(EnemyDescriptors);
    r->ax=DESC(field); W(EnemyStateCallbacks,r->ax);
    W(EnemyAnimationByteOffsets,0xfffe); W(EnemyAnimationCountdowns,1);
}
/* Select a looping sequence. FFFF is an equality sentinel, not a sign test.
 * Resetting an offset to zero retries the read in this same update. */
static int actor_frame(Regs *r,unsigned field) {
    for(unsigned budget=0;budget<32768;budget++) {
        r->di=DESC(field);
        r->di=add16(r,r->di,A(ActorAnimationByteOffsets),0);
        r->ax=rd16(r->ds,r->di); sub16(r,r->ax,0xffff,0);
        if(r->ax!=0xffff) { W(ActorSpriteIds,r->ax); return UGH_OK; }
        W(ActorAnimationByteOffsets,0);
    }
    return UGH_BUDGET;
}
static int enemy_frame(Regs *r,unsigned field) {
    for(unsigned budget=0;budget<32768;budget++) {
        r->bp=A(EnemyDirectionOrTargetPlayer);
        r->di=rd16(r->ds,(uint16_t)(r->bp+r->si+field));
        r->di=add16(r,r->di,A(EnemyAnimationByteOffsets),0);
        r->ax=rd16(r->ds,r->di); sub16(r,r->ax,0xffff,0);
        if(r->ax!=0xffff) { W(EnemySpriteIds,r->ax); return UGH_OK; }
        W(EnemyAnimationByteOffsets,0);
    }
    return UGH_BUDGET;
}
static int actor_tick(Regs *r) {
    uint16_t count=dec16(r,A(ActorAnimationCountdowns));
    W(ActorAnimationCountdowns,count);
    if(count) return 0;
    r->ax=DESC(0x3e); W(ActorAnimationCountdowns,r->ax);
    W(ActorAnimationByteOffsets,add16(r,A(ActorAnimationByteOffsets),2,0));
    return 1;
}
static void score(Regs *r) {
    r->ax=DESC(0x3a);
    WRITE(ScoreLowWord,0,add16(r,READ(ScoreLowWord,0),r->ax,0));
    WRITE(ScoreHighWord,0,add16(r,READ(ScoreHighWord,0),0,!!(r->flags&CF)));
}

/* TRANSLATES GAME:WaitForPassengerPlatform */
EXPORT int c_WaitForPassengerPlatform(Regs *r) {
    W(ActorSpriteIds,0xffff); r->ax=A(ds_2ACD); sub16(r,r->ax,0,0);
    if(r->ax) { r->ax=dec16(r,r->ax); W(ds_2ACD,r->ax); if(r->ax) return UGH_OK; }
    r->di=A(ActorSourcePlatformByteIndices);
    sub16(r,READ(PlatformActorOccupants,r->di),0xffff,0);
    if(!(r->flags&ZF)) return UGH_OK;
    r->si=A(ActorDescriptors); return tail(r,0x0c);
}

/* TRANSLATES GAME:PlacePassengerOnPlatform */
EXPORT int c_PlacePassengerOnPlatform(Regs *r) {
    r->si=A(ActorDescriptors); r->ax=DESC(0x0e); W(ActorUpdateOrScriptCursor,r->ax);
    r->di=A(ActorSourcePlatformByteIndices); WRITE(PlatformActorOccupants,r->di,r->bx);
    r->ax=sub16(r,0,DESC(2),0); r->ax=add16(r,r->ax,READ(PlatformHeights,r->di),0);
    W(ActorPixelY,r->ax); r->ax=shl(r,r->ax,5); W(ActorY32,r->ax);
    r->ax=sub16(r,0,DESC(0),0); r->ax=add16(r,r->ax,READ(PlatformArrivalPointsX,r->di),0);
    W(ActorPixelX,r->ax); r->ax=shl(r,r->ax,5); W(ActorX32,r->ax);
    W(ActorAnimationByteOffsets,0xfffe); W(ActorAnimationCountdowns,1); return UGH_OK;
}

/* TRANSLATES GAME:AnimatePassengerArrival */
EXPORT int c_AnimatePassengerArrival(Regs *r) {
    uint16_t count=dec16(r,A(ActorAnimationCountdowns)); W(ActorAnimationCountdowns,count);
    if(count) return UGH_OK;
    r->si=A(ActorDescriptors); r->ax=DESC(0x3e); W(ActorAnimationCountdowns,r->ax);
    W(ActorAnimationByteOffsets,add16(r,A(ActorAnimationByteOffsets),2,0));
    r->di=DESC(0x36); r->di=add16(r,r->di,A(ActorAnimationByteOffsets),0);
    r->ax=rd16(r->ds,r->di); sub16(r,r->ax,0xffff,0);
    if(r->ax==0xffff) return tail(r,0x10);
    W(ActorSpriteIds,r->ax); return UGH_OK;
}

/* TRANSLATES GAME:BeginPassengerPlatformWait */
EXPORT int c_BeginPassengerPlatformWait(Regs *r) {
    actor_init(r,0x12); r->ax=0xffff;
    W(ds_2A2D,r->ax); W(ActorOverlayOrScriptCallbacks,r->ax); return UGH_OK;
}

/* TRANSLATES GAME:BeginPassengerDestinationDisplay */
EXPORT int c_BeginPassengerDestinationDisplay(Regs *r) {
    actor_init(r,0x16); r->ax=add16(r,A(ActorDestinationPlatforms),0x10c,0);
    sub16(r,r->ax,0x112,0); if(!(r->flags&CF)) r->ax=0x111;
    W(ActorOverlayOrScriptCallbacks,r->ax); W(ds_2A2D,140); return UGH_OK;
}

/* TRANSLATES GAME:BeginPassengerQuestionDisplay */
EXPORT int c_BeginPassengerQuestionDisplay(Regs *r) {
    actor_init(r,0x1a); W(ActorOverlayOrScriptCallbacks,0x112); W(ds_2A2D,140); return UGH_OK;
}

/* TRANSLATES GAME:BeginPassengerApproach */
EXPORT int c_BeginPassengerApproach(Regs *r) {
    actor_init(r,0x1e); W(ActorOverlayOrScriptCallbacks,0xffff); return UGH_OK;
}

/* TRANSLATES GAME:BoardPassenger */
EXPORT int c_BoardPassenger(Regs *r) {
    r->si=A(ActorDescriptors); r->ax=DESC(0x40); WRITE(PlayerPassengerFares,r->di,r->ax);
    r->ax=DESC(0x42); WRITE(PlayerMinimumFares,r->di,r->ax);
    r->ax=DESC(0x22); W(ActorUpdateOrScriptCursor,r->ax);
    r->ax=DESC(0x46); WRITE(PlayerCarriedKinds,r->di,r->ax);
    r->si=A(ActorDestinationPlatformByteIndices); r->ax=READ(PlatformDestinationIcons,r->si);
    WRITE(PlayerDestinationIcons,r->di,r->ax); W(ds_2A2D,r->di);
    W(ActorSpriteIds,0xffff); W(PassengerQuickDeliveryCountdowns,200);
    r->di=A(ActorSourcePlatformByteIndices); WRITE(PlatformActorOccupants,r->di,0xffff); return UGH_OK;
}

/* TRANSLATES GAME:UpdateCarriedPassenger */
EXPORT int c_UpdateCarriedPassenger(Regs *r) {
    r->di=A(ds_2A2D); r->ax=READ(PlayerPassengerFares,r->di);
    sub16(r,r->ax,READ(PlayerMinimumFares,r->di),0);
    if(!(r->flags&(CF|ZF))) { r->ax=dec16(r,r->ax); WRITE(PlayerPassengerFares,r->di,r->ax); }
    r->ax=A(PassengerQuickDeliveryCountdowns); sub16(r,r->ax,0,0);
    if(greater(r)) { r->ax=dec16(r,r->ax); W(PassengerQuickDeliveryCountdowns,r->ax); }
    r->ax=A(ActorDestinationPlatforms); sub16(r,r->ax,READ(PlayerPlatformIndices,r->di),0);
    if(!(r->flags&ZF)) return UGH_OK;
    r->si=A(ActorDescriptors); return tail(r,0x24);
}

/* TRANSLATES GAME:WalkPassengerToExit */
EXPORT int c_WalkPassengerToExit(Regs *r) {
    r->di=A(ActorDestinationPlatformByteIndices); r->si=A(ActorDescriptors);
    if(!actor_tick(r)) return UGH_OK;
    r->ax=add16(r,A(ActorPixelX),DESC(0),0);
    sub16(r,r->ax,READ(PlatformArrivalPointsX,r->di),0);
    if(r->flags&ZF) return tail(r,0x28);
    int left=!less(r), status=actor_frame(r,left?0x32:0x34); if(status) return status;
    W(ActorX32,left?sub16(r,A(ActorX32),32,0):add16(r,A(ActorX32),32,0));
    r->di=A(ActorDestinationPlatformByteIndices); r->cx=logic(r,0,16);
    r->ax=sar(r,A(ActorX32),5); r->ax=add16(r,r->ax,DESC(0),0);
    sub16(r,r->ax,READ(PlatformArrivalPointsX,r->di),0);
    return (r->flags&ZF)?tail(r,0x28):UGH_OK;
}

/* TRANSLATES GAME:BeginPassengerDeparture */
EXPORT int c_BeginPassengerDeparture(Regs *r) { actor_init(r,0x2a); return UGH_OK; }

/* TRANSLATES GAME:AnimatePassengerDeparture */
EXPORT int c_AnimatePassengerDeparture(Regs *r) {
    uint16_t count=dec16(r,A(ActorAnimationCountdowns)); W(ActorAnimationCountdowns,count);
    if(count) return UGH_OK;
    r->si=A(ActorDescriptors); r->ax=DESC(0x3e); W(ActorAnimationCountdowns,r->ax);
    W(ActorAnimationByteOffsets,add16(r,A(ActorAnimationByteOffsets),2,0));
    r->di=DESC(0x38); r->di=add16(r,r->di,A(ActorAnimationByteOffsets),0);
    r->ax=rd16(r->ds,r->di); W(ActorSpriteIds,r->ax);
    sub16(r,rd16(r->ds,(uint16_t)(r->di+2)),0xffff,0);
    if(!(r->flags&ZF)) return UGH_OK;
    W(ActorJourneyCursors,add16(r,A(ActorJourneyCursors),4,0)); return tail(r,8);
}

/* TRANSLATES GAME:IgnoreActorState */
EXPORT int c_IgnoreActorState(Regs *r) { (void)r; return UGH_OK; }

/* TRANSLATES GAME:BeginStonePickupWait */
EXPORT int c_BeginStonePickupWait(Regs *r) { actor_init(r,0x12); return UGH_OK; }

/* TRANSLATES GAME:AttachStoneToPlayer */
EXPORT int c_AttachStoneToPlayer(Regs *r) {
    r->si=A(ActorDescriptors); r->ax=DESC(0x22); W(ActorUpdateOrScriptCursor,r->ax);
    r->ax=DESC(0x46); WRITE(PlayerCarriedKinds,r->di,r->ax); WRITE(PlayerDestinationIcons,r->di,7);
    W(ds_2A2D,r->di); W(ActorSpriteIds,0xffff); return UGH_OK;
}

/* TRANSLATES GAME:WaitForStoneRelease */
EXPORT int c_WaitForStoneRelease(Regs *r) {
    r->di=A(ds_2A2D); logic(r,rd8(r->ds,(uint16_t)(D(PlayerActionInput)+r->di)),8);
    if(!(r->flags&SF)) return UGH_OK;
    r->si=A(ActorDescriptors); return tail(r,0x24);
}

/* TRANSLATES GAME:UpdateThrownStone */
EXPORT int c_UpdateThrownStone(Regs *r) {
    r->si=A(ActorDescriptors); r->ax=add16(r,A(ds_2ACD),A(ActorX32),0);
    sub16(r,r->ax,0xfe00,0); if(less(r)||(r->flags&ZF)) goto gone;
    sub16(r,r->ax,0x2800,0); if(!less(r)) goto gone;
    W(ActorX32,r->ax); r->ax=add16(r,A(ds_2C6D),2,0); W(ds_2C6D,r->ax);
    logic(r,r->ax,16);
    if(r->flags&SF) { W(ActorY32,add16(r,A(ActorY32),r->ax,0)); return UGH_OK; }
    r->cx=A(ActorY32); r->ax=add16(r,r->ax,A(ActorY32),0);
    sub16(r,r->ax,0x1800,0); if(!less(r)) goto gone;
    W(ActorY32,r->ax); r->ax=sar(r,r->ax,5); r->cx=sar(r,r->cx,5);
    r->ax=add16(r,r->ax,DESC(2),0); r->cx=add16(r,r->cx,DESC(2),0); r->di=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        logic(r,READ(PlatformLeftEdges,r->di),16); if(r->flags&SF) return UGH_OK;
        sub16(r,r->cx,READ(PlatformHeights,r->di),0); if(greater(r)) goto next;
        sub16(r,r->ax,READ(PlatformHeights,r->di),0); if(less(r)) goto next;
        r->dx=sar(r,A(ActorX32),5); r->dx=add16(r,r->dx,DESC(0),0);
        sub16(r,r->dx,READ(PlatformLeftEdges,r->di),0); if(less(r)) goto next;
        sub16(r,r->dx,READ(PlatformRightEdges,r->di),0); if(greater(r)) goto next;
        r->ax=sub16(r,READ(PlatformHeights,r->di),DESC(2),0); r->ax=shl(r,r->ax,5);
        W(ActorY32,r->ax); return tail(r,0x10);
next:   r->di=add16(r,r->di,2,0);
    }
    return UGH_BUDGET;
gone:
    W(ActorSpriteIds,0xffff); r->ax=DESC(0x2c); W(ActorUpdateOrScriptCursor,r->ax); return UGH_OK;
}

/* TRANSLATES GAME:BeginPassengerResurfacing */
EXPORT int c_BeginPassengerResurfacing(Regs *r) {
    r->si=A(ActorDescriptors); r->ax=DESC(0x0a); W(ActorUpdateOrScriptCursor,r->ax);
    r->di=A(ActorSourcePlatformByteIndices); r->ax=0xffff;
    WRITE(PlatformActorOccupants,r->di,r->ax); W(ActorOverlayOrScriptCallbacks,r->ax);
    W(ActorAnimationByteOffsets,0xfffe); W(ActorAnimationCountdowns,1); W(ds_2C6D,0); return UGH_OK;
}

/* TRANSLATES GAME:UpdatePassengerResurfacing */
EXPORT int c_UpdatePassengerResurfacing(Regs *r) {
    r->si=A(ActorDescriptors); actor_tick(r);
    int status=actor_frame(r,0x2e); if(status) return status;
    r->cx=sub16(r,A(ActorPixelY),DESC(2),0); r->cx=sub16(r,r->cx,READ(WaterYPixels,0),0);
    if(!(r->flags&(SF|ZF))) r->cx=(uint16_t)((r->cx&255u)|0x100u);
    r->ax=A(ds_2C6D); logic(r,r->cx>>8,8);
    if(r->flags&SF) r->ax=add16(r,r->ax,0x27,0);
    else { sub16(r,r->ax,0,0); r->ax=sub16(r,r->ax,greater(r)?0x175:0x5c,0); }
    logic(r,r->ax,16);
    if(r->flags&SF) { sub16(r,r->ax,0xe800,0); if(less(r)) r->ax=0xe800; }
    else { sub16(r,r->ax,0x1800,0); if(greater(r)) r->ax=0x1800; }
    W(ds_2C6D,r->ax); r->ax=sar(r,r->ax,6); r->ax=add16(r,r->ax,A(ActorY32),0); W(ActorY32,r->ax);
    sub16(r,A(ds_2C6D),0,0); if(!less(r)) return UGH_OK;
    r->ax=sar(r,r->ax,5); r->ax=sub16(r,r->ax,DESC(2),0);
    sub16(r,r->ax,READ(WaterYPixels,0),0); if(greater(r)) return UGH_OK;
    r->ax=sub16(r,READ(WaterYPixels,0),DESC(2),0); r->ax=shl(r,r->ax,5);
    W(ActorY32,r->ax); return tail(r,0x10);
}

/* TRANSLATES GAME:BeginPassengerSinking */
EXPORT int c_BeginPassengerSinking(Regs *r) {
    actor_init(r,0x0e); W(ActorOverlayOrScriptCallbacks,0xffff); W(ds_2C6D,0); return UGH_OK;
}

/* TRANSLATES GAME:UpdatePassengerSinking */
EXPORT int c_UpdatePassengerSinking(Regs *r) {
    r->si=A(ActorDescriptors); actor_tick(r); int status=actor_frame(r,0x2e); if(status) return status;
    r->ax=add16(r,A(ds_2C6D),0x27,0); W(ds_2C6D,r->ax);
    r->ax=sar(r,r->ax,6); r->ax=add16(r,r->ax,A(ActorY32),0); sub16(r,r->ax,0x1800,0);
    if(r->flags&CF) W(ActorY32,r->ax);
    else { r->ax=DESC(0x2c); W(ActorUpdateOrScriptCursor,r->ax); W(ActorSpriteIds,0xffff); }
    return UGH_OK;
}

/* TRANSLATES GAME:BeginPassengerFloating */
EXPORT int c_BeginPassengerFloating(Regs *r) {
    actor_init(r,0x12); r->ax=DESC(0x44); W(ds_2ACD,r->ax); return UGH_OK;
}

static void surface_y(Regs *r) {
    r->ax=READ(WaterYPixels,0); sub16(r,r->ax,A(ActorPixelY),0);
    if(!(r->flags&ZF)) { r->ax=sub16(r,r->ax,DESC(2),0); r->ax=shl(r,r->ax,5); W(ActorY32,r->ax); }
}

/* TRANSLATES GAME:UpdatePassengerFloating */
EXPORT int c_UpdatePassengerFloating(Regs *r) {
    r->si=A(ActorDescriptors); actor_tick(r); int status=actor_frame(r,0x30); if(status) return status;
    surface_y(r); sub16(r,r->si,D(Data_77FE),0);
    if(!(r->flags&ZF)) {
        r->di=logic(r,0,16);
        for(;;) {
            sub16(r,READ(PlayerVerticalVelocities,r->di),0,0);
            if(!(r->flags&ZF)) goto next;
            sub16(r,READ(PlayerCarriedKinds,r->di),0,0); if(!(r->flags&ZF)) goto next;
            r->cx=sub16(r,READ(PlayerYPixels,r->di),READ(WaterYPixels,0),0);
            r->cx=add16(r,r->cx,18,0); if(r->flags&ZF) return tail(r,0x14);
next:       r->di=add16(r,r->di,2,0); sub16(r,r->di,4,0); if(!(r->flags&CF)) break;
            sub16(r,READ(PlayerCount,0),2,0); if(!(r->flags&ZF)) break;
        }
    }
    uint16_t count=dec16(r,A(ds_2ACD)); W(ds_2ACD,count);
    return count?UGH_OK:tail(r,0x0c);
}

/* TRANSLATES GAME:UpdateFloatingDestinationDisplay */
EXPORT int c_UpdateFloatingDestinationDisplay(Regs *r) {
    r->si=A(ActorDescriptors); surface_y(r);
    r->cx=sub16(r,READ(PlayerYPixels,0),READ(WaterYPixels,0),0); r->cx=add16(r,r->cx,18,0);
    if(!(r->flags&ZF)) {
        sub16(r,READ(PlayerCount,0),2,0); if(!(r->flags&ZF)) return tail(r,0x18);
        r->cx=sub16(r,READ(SecondPlayerYPixels,0),READ(WaterYPixels,0),0); r->cx=add16(r,r->cx,18,0);
        if(!(r->flags&ZF)) return tail(r,0x18);
    }
    if(actor_tick(r)) { int status=actor_frame(r,0x30); if(status) return status; }
    uint16_t count=dec16(r,A(ds_2A2D)); W(ds_2A2D,count); return count?UGH_OK:tail(r,0x1c);
}

/* TRANSLATES GAME:UpdateFloatingQuestionDisplay */
EXPORT int c_UpdateFloatingQuestionDisplay(Regs *r) {
    r->si=A(ActorDescriptors); surface_y(r);
    if(actor_tick(r)) { int status=actor_frame(r,0x30); if(status) return status; }
    uint16_t count=dec16(r,A(ds_2A2D)); W(ds_2A2D,count); return count?UGH_OK:tail(r,0x0c);
}

/* TRANSLATES GAME:UpdateFloatingPassengerApproach */
EXPORT int c_UpdateFloatingPassengerApproach(Regs *r) {
    r->si=A(ActorDescriptors); surface_y(r); r->di=logic(r,0,16);
    for(;;) {
        sub16(r,READ(PlayerCarriedKinds,r->di),0,0);
        if(r->flags&ZF) {
            r->cx=sub16(r,READ(PlayerYPixels,r->di),READ(WaterYPixels,0),0); r->cx=add16(r,r->cx,18,0);
            if(r->flags&ZF) break;
        }
        r->di=add16(r,r->di,2,0); sub16(r,r->di,4,0); if(!(r->flags&CF)) return tail(r,0x18);
        sub16(r,READ(PlayerCount,0),2,0); if(!(r->flags&ZF)) return tail(r,0x18);
    }
    r->cx=logic(r,0,16); if(actor_tick(r)) r->cx=inc(r,r->cx);
    r->ax=add16(r,A(ActorPixelX),DESC(0),0); r->ax=sub16(r,r->ax,16,0);
    sub16(r,r->ax,READ(PlayerPixelX,r->di),0);
    if(r->flags&ZF) return tail(r,0x20);
    int left=greater(r), status=actor_frame(r,left?0x32:0x34); if(status) return status;
    logic(r,r->cx,16);
    if(r->cx) W(ActorX32,left?sub16(r,A(ActorX32),32,0):add16(r,A(ActorX32),32,0));
    return UGH_OK;
}

/* TRANSLATES GAME:IgnoreWaterbornePassengerState */
EXPORT int c_IgnoreWaterbornePassengerState(Regs *r) { (void)r; return UGH_OK; }

/* TRANSLATES GAME:FindThrownStoneHittingEnemy */
EXPORT int c_FindThrownStoneHittingEnemy(Regs *r) {
    r->di=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        r->ax=READ(ActorDescriptors,r->di); sub16(r,r->ax,0xffff,0);
        if(r->flags&ZF) { r->di=0xffff; break; }
        sub16(r,r->ax,D(Data_78DC),0); if(!(r->flags&ZF)) goto next;
        sub16(r,READ(ActorUpdateOrScriptCursor,r->di),G(UpdateThrownStone),0); if(!(r->flags&ZF)) goto next;
        logic(r,READ(ds_2C6D,r->di),16); if(r->flags&SF) goto next;
        r->ax=add16(r,READ(ActorY32,r->di),0x100,0); sub16(r,r->ax,A(EnemyY32),0); if(less(r)) goto next;
        r->ax=sub16(r,r->ax,0x380,0); sub16(r,r->ax,A(EnemyY32),0); if(greater(r)) goto next;
        r->ax=add16(r,READ(ActorX32,r->di),0x180,0); sub16(r,r->ax,A(EnemyX32),0); if(less(r)) goto next;
        r->ax=sub16(r,r->ax,0x4c0,0); sub16(r,r->ax,A(EnemyX32),0); if(!greater(r)) break;
next:   r->di=add16(r,r->di,2,0);
        if(budget==32767) return UGH_BUDGET;
    }
    logic(r,r->di,16); return UGH_OK;
}

/* Shared contact-box computation, retaining word wrapping before each signed
 * CMP. The retry condition is DI == PlayerCount, not DI < array byte size.
 * Only count=2 retries after the first miss; other counts stop immediately. */
static int contact(Regs *r,uint16_t xbase,uint16_t ybase,int falling,int actor) {
    r->di=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        r->ax=shl(r,DESC(2),5); r->ax=add16(r,r->ax,rd16(r->ds,(uint16_t)(ybase+r->bx)),0);
        sub16(r,r->ax,READ(PlayerY32,r->di),0); if(less(r)) goto next;
        r->ax=DESC(2);
        if(falling) r->ax=sub16(r,r->ax,6,0);
        else { r->ax=sub16(r,r->ax,DESC(6),0); r->ax=sub16(r,r->ax,DESC(6),0); }
        r->ax=shl(r,r->ax,5); r->ax=add16(r,r->ax,rd16(r->ds,(uint16_t)(ybase+r->bx)),0);
        r->ax=sub16(r,r->ax,0x280,0); sub16(r,r->ax,READ(PlayerY32,r->di),0); if(greater(r)) goto next;
        r->ax=add16(r,DESC(0),falling?3:DESC(4),0); r->ax=shl(r,r->ax,5);
        r->ax=add16(r,r->ax,rd16(r->ds,(uint16_t)(xbase+r->bx)),0); r->ax=sub16(r,r->ax,0xa0,0);
        sub16(r,r->ax,READ(PlayerX32,r->di),0); if(less(r)) goto next;
        r->ax=sub16(r,DESC(0),falling?3:DESC(4),0); r->ax=shl(r,r->ax,5);
        r->ax=add16(r,r->ax,rd16(r->ds,(uint16_t)(xbase+r->bx)),0); r->ax=sub16(r,r->ax,0x340,0);
        sub16(r,r->ax,READ(PlayerX32,r->di),0); if(!greater(r)) break;
next:   r->di=add16(r,r->di,2,0); sub16(r,r->di,READ(PlayerCount,0),0);
        if(!(r->flags&ZF)) { r->di=0xffff; break; }
        if(budget==32767) return UGH_BUDGET;
    }
    logic(r,r->di,16); if(actor && !(r->flags&SF)) r->ax=READ(PlayerPlatformIndices,r->di);
    return UGH_OK;
}

/* TRANSLATES GAME:FindPlayerTouchingFallingItem */
EXPORT int c_FindPlayerTouchingFallingItem(Regs *r) { return contact(r,D(FallingItemX),D(FallingItemY),1,0); }

/* TRANSLATES GAME:FindPlayerTouchingActor */
EXPORT int c_FindPlayerTouchingActor(Regs *r) { return contact(r,D(ActorX32),D(ActorY32),0,1); }

/* TRANSLATES GAME:FindPlayerTouchingEnemy */
EXPORT int c_FindPlayerTouchingEnemy(Regs *r) { return contact(r,D(EnemyX32),D(EnemyY32),0,0); }

/* TRANSLATES GAME:DispatchEnemyStates */
EXPORT int c_DispatchEnemyStates(Regs *r) {
    r->bx=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        sub16(r,A(EnemyDescriptors),0xffff,0); if(r->flags&ZF) return UGH_OK;
        /* Real near CALL scratch is below the adapter's return frame. Callees
         * in this package consume no stack arguments and preserve SS/SP. */
        int status=ugh_call_near(A(EnemyStateCallbacks),(uint16_t)(G(DispatchEnemyStates)+0x10),r); if(status) return status;
        r->bx=add16(r,r->bx,2,0);
    }
    return UGH_BUDGET;
}

/* TRANSLATES GAME:BeginBirdDelay */
EXPORT int c_BeginBirdDelay(Regs *r) {
    enemy_init(r,0x0a,1); W(EnemySpriteIds,0xffff); r->ax=A(EnemyInitialDelays); W(EnemyStateCounters,r->ax); return UGH_OK;
}

static int enemy_wait(Regs *r,unsigned field) {
    uint16_t count=dec16(r,A(EnemyStateCounters)); W(EnemyStateCounters,count);
    if(count) return UGH_OK;
    r->si=A(EnemyDescriptors); return tail(r,field);
}

/* TRANSLATES GAME:WaitForBirdFlight */
EXPORT int c_WaitForBirdFlight(Regs *r) { return enemy_wait(r,0x0c); }

/* TRANSLATES GAME:WaitForBirdWarning */
EXPORT int c_WaitForBirdWarning(Regs *r) { return enemy_wait(r,0x10); }

/* TRANSLATES GAME:StunBirdAndAwardScore */
EXPORT int c_StunBirdAndAwardScore(Regs *r) {
    r->ax=DESC(0x1e); W(EnemyStateCallbacks,r->ax); score(r); W(EnemyStateCounters,0);
    logic(r,A(EnemyHorizontalSpeeds),16); r->si=DESC((r->flags&SF)?0x36:0x38);
    r->ax=rd16(r->ds,r->si); W(EnemySpriteIds,r->ax); return UGH_OK;
}

/* TRANSLATES GAME:UpdateStunnedBird */
EXPORT int c_UpdateStunnedBird(Regs *r) {
    r->ax=add16(r,A(EnemyHorizontalSpeeds),A(EnemyX32),0); sub16(r,r->ax,0xfc00,0);
    if(less(r)||(r->flags&ZF)) goto gone;
    sub16(r,r->ax,0x2800,0); if(!less(r)) goto gone;
    W(EnemyX32,r->ax); r->ax=A(EnemyStateCounters); sub16(r,r->ax,40,0);
    if(less(r)) { r->ax=inc(r,r->ax); W(EnemyStateCounters,r->ax); }
    r->ax=add16(r,r->ax,A(EnemyY32),0); sub16(r,r->ax,0x1800,0); if(!less(r)) goto gone;
    W(EnemyY32,r->ax); return UGH_OK;
gone: r->si=A(EnemyDescriptors); return tail(r,8);
}

/* TRANSLATES GAME:BeginDinosaurPatrol */
EXPORT int c_BeginDinosaurPatrol(Regs *r) { enemy_init(r,0x0a,1); return UGH_OK; }

/* TRANSLATES GAME:BeginDinosaurAlert */
EXPORT int c_BeginDinosaurAlert(Regs *r) { enemy_init(r,0x0e,0); W(EnemyStateCounters,140); return UGH_OK; }

/* TRANSLATES GAME:BeginDinosaurCharge */
EXPORT int c_BeginDinosaurCharge(Regs *r) { enemy_init(r,0x12,0); W(EnemyStateCounters,0); return UGH_OK; }

/* TRANSLATES GAME:BeginDinosaurRecovery */
EXPORT int c_BeginDinosaurRecovery(Regs *r) { enemy_init(r,0x16,0); return UGH_OK; }

/* TRANSLATES GAME:BeginDinosaurImpactRecovery */
EXPORT int c_BeginDinosaurImpactRecovery(Regs *r) {
    /* Original installs +16 (ordinary recovery), despite its +18 caller. */
    enemy_init(r,0x16,0); return UGH_OK;
}

/* TRANSLATES GAME:StunDinosaurAndAwardScore */
EXPORT int c_StunDinosaurAndAwardScore(Regs *r) {
    r->ax=DESC(0x1e); W(EnemyStateCallbacks,r->ax); score(r);
    W(EnemyAnimationByteOffsets,0xfffe); W(EnemyAnimationCountdowns,1); W(EnemyStateCounters,350); return UGH_OK;
}

/* TRANSLATES GAME:UpdateStunnedDinosaur */
EXPORT int c_UpdateStunnedDinosaur(Regs *r) {
    r->si=A(EnemyDescriptors);
    uint16_t count=dec16(r,A(EnemyStateCounters)); W(EnemyStateCounters,count); if(!count) return tail(r,8);
    count=dec16(r,A(EnemyAnimationCountdowns)); W(EnemyAnimationCountdowns,count); if(count) return UGH_OK;
    W(EnemyAnimationCountdowns,4); W(EnemyAnimationByteOffsets,add16(r,A(EnemyAnimationByteOffsets),2,0));
    return enemy_frame(r,0x36);
}

/* TRANSLATES GAME:loc_295B */
EXPORT int c_loc_295B(Regs *r) { enemy_init(r,0x12,1); return UGH_OK; }

/* TRANSLATES GAME:loc_2A53 */
EXPORT int c_loc_2A53(Regs *r) {
    r->ax=DESC(0x1e); W(EnemyStateCallbacks,r->ax); score(r); W(EnemyStateCounters,350);
    r->si=DESC(0x36); r->ax=rd16(r->ds,r->si); W(EnemySpriteIds,r->ax); return UGH_OK;
}

/* TRANSLATES GAME:loc_2A76 */
EXPORT int c_loc_2A76(Regs *r) { return enemy_wait(r,0x10); }

/* TRANSLATES GAME:InitializeFruitTreeAnimation */
EXPORT int c_InitializeFruitTreeAnimation(Regs *r) {
    enemy_init(r,0x0a,1);
    /* Actual SHL, not SAR: retain the original cached-coordinate bug. */
    r->ax=shl(r,A(EnemyX32),5); W(EnemyDrawX,r->ax);
    r->ax=shl(r,A(EnemyY32),5); W(EnemyDrawY,r->ax); return UGH_OK;
}

/* Tail transfers retain the incoming near return frame. */
static int state_jump(Regs *r,uint16_t target) { return ugh_dispatch(r->cs,target,r); }
