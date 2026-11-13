#include "ugh.h"
#include "platform.h"

/* Near actor/enemy/item callbacks. DS is always live; BX is a byte index
 * into parallel word arrays. All entries preserve BX/CS/DS/ES/SS/SP except
 * for documented callee effects. AX/CX/DX/SI/DI/BP and arithmetic flags follow
 * the instructions, including stale outputs. IF/DF survive except the VGA
 * restore tail clears DF. Descriptor fields below are byte displacements.
 * Sound boundaries dispatch original addresses with real far-cdecl frames;
 * an unavailable callee fails, never acts as a successful empty callback. */
#define R(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define W(n,i,v) wr16(r->ds,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define A(n) R(n,r->bx)
#define B(n,v) W(n,r->bx,v)
#define F(n) rd16(r->ds,(uint16_t)(r->si+(n)))
static int lt(const Regs *r) { return !!(r->flags&SF)!=!!(r->flags&OF); }
static int gt(const Regs *r) { return !(r->flags&ZF)&&!lt(r); }
static uint16_t shift(Regs *r,uint16_t v,unsigned n,int right) {
    for(unsigned i=0;i<n;i++) {
        flag(r,CF,right?(v&1):(v&0x8000));
        v=right?(uint16_t)((v>>1)|(v&0x8000)):(uint16_t)(v<<1);
    }
    szp(r,v,16); if(n==1) flag(r,OF,right?0:(!!(v&0x8000)^!!(r->flags&CF)));
    return v;
}
static uint8_t byte_sub(Regs *r,uint8_t a,uint8_t b) {
    uint8_t v=(uint8_t)(a-b);
    flag(r,CF,a<b); flag(r,OF,((a^b)&(a^v)&128)!=0);
    flag(r,AF,((a^b^v)&16)!=0); szp(r,v,8); return v;
}
static uint8_t byte_add(Regs *r,uint8_t a,uint8_t b) {
    uint8_t v=(uint8_t)(a+b);
    flag(r,CF,(unsigned)a+b>255); flag(r,OF,((~(a^b))&(a^v)&128)!=0);
    flag(r,AF,((a^b^v)&16)!=0); szp(r,v,8); return v;
}
static uint8_t byte_dec(Regs *r,uint8_t a) {
    uint16_t cf=r->flags&CF; uint8_t v=byte_sub(r,a,1); flag(r,CF,cf); return v;
}
static uint16_t inc(Regs *r,uint16_t v) {
    uint16_t cf=r->flags&CF; v=add16(r,v,1,0); flag(r,CF,cf); return v;
}
static int tail(Regs *r,unsigned field) { return ugh_dispatch(r->cs,F(field),r); }
static void push(Regs *r,uint16_t v) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v); }
static uint16_t pop(Regs *r) { uint16_t v=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return v; }
static int effect(Regs *r,uint16_t segment,uint16_t offset,uint16_t ret) {
    push(r,1); push(r,255); push(r,segment); push(r,offset);
    push(r,r->cs); push(r,ret);
    int status=ugh_dispatch(UGH_S_C_PlayAdlibEffect,UGH_O_C_PlayAdlibEffect,r);
    if(status) return status;
    r->sp=(uint16_t)(r->sp+4); r->sp=add16(r,r->sp,8,0); return UGH_OK;
}

/* Real far-cdecl call, retaining the enemy/descriptor save words. */
/* TRANSLATES GAME:StopBirdFlightSound */
EXPORT int c_StopBirdFlightSound(Regs *r) {
    push(r,r->bx); push(r,r->si); push(r,A(EnemyFlightSoundHandles));
    push(r,r->cs); push(r,G(StopBirdFlightSound)+11);
    int st=ugh_dispatch(UGH_S_C_StopAdlibTrackChannel,UGH_O_C_StopAdlibTrackChannel,r);
    if(st) return st;
    r->sp=(uint16_t)(r->sp+4); r->sp=add16(r,r->sp,2,0);
    r->si=pop(r); r->bx=pop(r); return UGH_OK;
}
/* Stone velocity takes signed pixel units from the carrying player; positions
 * and descriptor-selected exit state are stored before the sound call. */
/* TRANSLATES GAME:ThrowCarriedStone */
EXPORT int c_ThrowCarriedStone(Regs *r) {
    r->si=A(ActorDescriptors); r->ax=logic(r,0,16);
    W(PlayerCarriedKinds,r->di,r->ax); W(PlayerDestinationIcons,r->di,r->ax);
    r->ax=shift(r,R(PlayerHorizontalVelocities,r->di),5,1); B(ActorMotionWaitOrDemoRepeats,r->ax);
    r->ax=shift(r,R(PlayerVerticalVelocities,r->di),5,1); B(ActorVerticalOrDemoPeriod,r->ax);
    r->ax=R(PlayerX32,r->di); r->bp=R(PlayerY32,r->di);
    r->ax=add16(r,r->ax,0x200,0); r->bp=add16(r,r->bp,0x140,0);
    r->di=shift(r,F(0),5,0); r->ax=sub16(r,r->ax,r->di,0); B(ActorX32,r->ax);
    r->di=shift(r,F(2),4,0); r->bp=sub16(r,r->bp,r->di,0); B(ActorY32,r->bp);
    B(ActorSpriteIds,0x221); r->ax=F(0x26); B(ActorUpdateOrScriptCursor,r->ax);
    push(r,r->bx);
    int st=effect(r,UGH_S_B3632_ext_3632,0,G(ThrowCarriedStone)+0x68);
    if(st) return st;
    r->bx=pop(r); return UGH_OK;
}
/* Warn for 70 ticks, saving ES across the original sound API. */
/* TRANSLATES GAME:BeginBirdWarning */
EXPORT int c_BeginBirdWarning(Regs *r) {
    r->si=A(EnemyDescriptors); r->ax=F(0xe); B(EnemyStateCallbacks,r->ax);
    B(EnemyStateCounters,70); push(r,r->bx); push(r,r->es);
    int st=effect(r,UGH_S_B325B_ext_325B,0,G(BeginBirdWarning)+0x23);
    if(st) return st;
    r->es=pop(r); r->bx=pop(r); return UGH_OK;
}
/* Target toggle uses signed PlayerCount, then doubles the selected word.
 * Spawn opposite the player and clamp Y with signed, wrapped comparisons. */
/* TRANSLATES GAME:LaunchBirdTowardPlayer */
EXPORT int c_LaunchBirdTowardPlayer(Regs *r) {
    r->si=A(EnemyDescriptors); r->di=logic(r,A(EnemyDirectionOrTargetPlayer)^1,16);
    sub16(r,r->di,R(PlayerCount,0),0); if(!lt(r)) r->di=logic(r,0,16);
    B(EnemyDirectionOrTargetPlayer,r->di); r->di=shift(r,r->di,1,0);
    sub16(r,R(PlayerX32,r->di),0x1400,0);
    if(lt(r)) {
        r->ax=logic(r,A(EnemyHorizontalSpeeds),16);
        if(!(r->flags&SF)) { r->ax=sub16(r,0,r->ax,0); B(EnemyHorizontalSpeeds,r->ax); }
        r->ax=0x27e0; r->cx=F(0x22);
    } else {
        r->ax=logic(r,A(EnemyHorizontalSpeeds),16);
        if(r->flags&SF) { r->ax=sub16(r,0,r->ax,0); B(EnemyHorizontalSpeeds,r->ax); }
        r->ax=0xfc20; r->cx=F(0x24);
    }
    B(EnemyX32,r->ax); B(EnemyAnimationOrDropLists,r->cx);
    r->ax=add16(r,R(PlayerY32,r->di),0x340,0); sub16(r,r->ax,R(WaterY32,0),0);
    if(gt(r)) r->ax=R(WaterY32,0);
    r->ax=sub16(r,r->ax,0x340,0); sub16(r,r->ax,0xff80,0);
    if(lt(r)) r->ax=0xff80;
    B(EnemyY32,r->ax); r->ax=F(0x12); B(EnemyStateCallbacks,r->ax);
    push(r,r->es); push(r,r->bx);
    push(r,0); push(r,255); push(r,UGH_S_B3260_ext_3260); push(r,0);
    push(r,r->cs); push(r,G(LaunchBirdTowardPlayer)+0x9f);
    int st=ugh_dispatch(UGH_S_C_PlayAdlibEffect,UGH_O_C_PlayAdlibEffect,r);
    if(st) return st;
    r->sp=(uint16_t)(r->sp+4); r->sp=add16(r,r->sp,8,0);
    r->bx=pop(r); r->es=pop(r); B(EnemyFlightSoundHandles,r->ax); return UGH_OK;
}
/* Allocation is an actual descriptor CALL. Its full-pool RET corrupts control
 * flow by consuming saved BX; no successful continuation is invented here. */
/* TRANSLATES GAME:ReleaseTreeReward */
EXPORT int c_ReleaseTreeReward(Regs *r) {
    r->ax=F(0x1e); B(EnemyStateCallbacks,r->ax); B(EnemyStateCounters,210); B(EnemySpriteIds,0xe8);
    r->ax=R(ActorX32,r->di); r->bp=R(ActorY32,r->di);
    r->cx=R(ActorMotionWaitOrDemoRepeats,r->di); r->dx=shift(r,sub16(r,0,R(ActorVerticalOrDemoPeriod,r->di),0),2,1);
    r->si=A(EnemyAnimationOrDropLists); r->si=rd16(r->ds,r->si);
    int st=ugh_call_near(F(4),G(ReleaseTreeReward)+0x31,r); if(st) return st;
    B(EnemyAnimationOrDropLists,add16(r,A(EnemyAnimationOrDropLists),2,0));
    push(r,r->bx); st=effect(r,UGH_S_B3274_ext_3274,0,G(ReleaseTreeReward)+0x47);
    if(st) return st;
    r->bx=pop(r); return UGH_OK;
}
/* Equality-only FFFF sentinel; offset reset retries the same sequence now. */
static int frame(Regs *r,int enemy,unsigned field,int directional) {
    for(unsigned budget=0;budget<32768;budget++) {
        if(directional) r->bp=A(EnemyDirectionOrTargetPlayer);
        r->di=rd16(r->ds,(uint16_t)(r->si+field+(directional?r->bp:0)));
        r->di=add16(r,r->di,enemy?A(EnemyAnimationByteOffsets):A(ActorAnimationByteOffsets),0);
        r->ax=rd16(r->ds,r->di); sub16(r,r->ax,0xffff,0);
        if(r->ax!=0xffff) {
            if(enemy) B(EnemySpriteIds,r->ax); else B(ActorSpriteIds,r->ax);
            return UGH_OK;
        }
        if(enemy) B(EnemyAnimationByteOffsets,0); else B(ActorAnimationByteOffsets,0);
    }
    return UGH_BUDGET;
}
static int actor_tick(Regs *r) {
    uint16_t count=dec16(r,A(ActorAnimationCountdowns)); B(ActorAnimationCountdowns,count);
    if(count) return 0;
    r->ax=F(0x3e); B(ActorAnimationCountdowns,r->ax);
    B(ActorAnimationByteOffsets,add16(r,A(ActorAnimationByteOffsets),2,0)); return 1;
}
/* Water tests JS on the wrapped subtraction, not a signed mathematical compare. */
static int submerged(Regs *r) {
    r->ax=shift(r,F(2),1,1); r->ax=add16(r,r->ax,A(ActorPixelY),0);
    r->ax=sub16(r,r->ax,R(WaterYPixels,0),0); return !(r->flags&SF);
}
static int water_swap(Regs *r,int place) {
    if(place) {
        r->ax=add16(r,R(WaterYPixels,0),F(2),0); r->ax=shift(r,r->ax,5,0); B(ActorY32,r->ax);
        r->di=A(ActorSourcePlatformByteIndices); r->ax=0xffff;
        W(PlatformActorOccupants,r->di,r->ax); B(ActorOverlayOrScriptCallbacks,r->ax);
    }
    r->si=F(0x48); B(ActorDescriptors,r->si); return tail(r,8);
}
/* Scan termination is DI == PlayerArrayBytes, even for malformed lengths. */
static int platform_player(Regs *r,int empty) {
    r->ax=A(ActorPlatformOrScriptDone); r->di=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        sub16(r,r->ax,R(PlayerPlatformIndices,r->di),0);
        if(r->flags&ZF) {
            if(!empty) return 1;
            sub16(r,R(PlayerCarriedKinds,r->di),0,0); if(r->flags&ZF) return 1;
        }
        r->di=add16(r,r->di,2,0); sub16(r,r->di,R(PlayerArrayBytes,0),0);
        if(r->flags&ZF) return 0;
    }
    return -1;
}

/* Journey cursor reads +4 destination, current source and +2 delay. DEC8
 * completion tests SF; AX=FFFE makes the completion marker FE (not zero). */
/* TRANSLATES GAME:ReadPassengerJourneyLeg */
EXPORT int c_ReadPassengerJourneyLeg(Regs *r) {
    r->di=A(ActorJourneyCursors); r->ax=rd16(r->ds,(uint16_t)(r->di+4)); sub16(r,r->ax,0xffff,0);
    if(r->ax==0xffff) {
        set_al(r,rd8(r->ds,D(RemainingPassengerJourneys))); set_al(r,byte_dec(r,(uint8_t)r->ax));
        if(!(r->flags&SF)) {
            wr8(r->ds,D(RemainingPassengerJourneys),(uint8_t)r->ax);
            if(r->flags&ZF) {
                r->ax=0xfffe; W(ScreenFadeStep,0,r->ax);
                W(ScreenFadeLevel,0,add16(r,R(ScreenFadeLevel,0),r->ax,0));
                wr8(r->ds,D(LevelCompletionMarker),(uint8_t)r->ax);
            }
        }
        B(ActorSpriteIds,0xffff); r->si=A(ActorDescriptors); r->ax=F(0x2c);
        B(ActorUpdateOrScriptCursor,r->ax); return ugh_dispatch(r->cs,r->ax,r);
    }
    B(ActorDestinationPlatforms,r->ax); r->ax=shift(r,r->ax,1,0); B(ActorDestinationPlatformByteIndices,r->ax);
    r->ax=rd16(r->ds,r->di); B(ActorPlatformOrScriptDone,r->ax);
    r->ax=shift(r,r->ax,1,0); B(ActorSourcePlatformByteIndices,r->ax);
    r->ax=rd16(r->ds,(uint16_t)(r->di+2));
    int status=ugh_call_near(G(ScaleLevelSpeedToThreeHalves),(uint16_t)(G(ReadPassengerJourneyLeg)+0x5d),r); if(status) return status;
    B(ActorMotionWaitOrDemoRepeats,r->ax); r->si=A(ActorDescriptors); r->ax=F(0x0a); B(ActorUpdateOrScriptCursor,r->ax); return UGH_OK;
}

/* Platform-wait movement is tick gated; contact and empty-player scans run
 * every call. DS:SI survives the contact helper. */
/* TRANSLATES GAME:UpdatePassengerPlatformWait */
EXPORT int c_UpdatePassengerPlatformWait(Regs *r) {
    r->di=A(ActorSourcePlatformByteIndices); r->si=A(ActorDescriptors);
    if(submerged(r)) return water_swap(r,1);
    if(actor_tick(r)) {
        r->ax=add16(r,A(ActorPixelX),F(0),0); sub16(r,r->ax,R(PlatformWaitingPointsX,r->di),0);
        if(!(r->flags&ZF)) {
            B(ActorPhaseOrDemoLoopCursor,0); int left=!lt(r), status=frame(r,0,left?0x32:0x34,0); if(status) return status;
            B(ActorX32,left?sub16(r,A(ActorX32),32,0):add16(r,A(ActorX32),32,0));
        } else {
            sub16(r,A(ActorPhaseOrDemoLoopCursor),1,0); if(!(r->flags&ZF)) B(ActorAnimationByteOffsets,0);
            int status=frame(r,0,0x2e,0); if(status) return status; B(ActorPhaseOrDemoLoopCursor,1);
        }
    }
    int status=ugh_call_near(G(FindPlayerTouchingActor),(uint16_t)(G(UpdatePassengerPlatformWait)+0xe2),r); if(status) return status;
    if(!(r->flags&SF)) { sub16(r,r->ax,0xffff,0); if(r->flags&ZF) return water_swap(r,0); }
    int found=platform_player(r,1); if(found<0) return UGH_BUDGET; return found?tail(r,0x14):UGH_OK;
}

/* Destination and question update share water/contact and looping animation;
 * destination rejects the FIRST matching occupied vehicle immediately. */
static int display(Regs *r,int question) {
    r->si=A(ActorDescriptors); if(submerged(r)) return water_swap(r,1);
    int status=ugh_call_near(G(FindPlayerTouchingActor),(uint16_t)((question?G(UpdatePassengerQuestionDisplay)+0x3f:G(UpdatePassengerDestinationDisplay)+0x3f)),r);
    if(status) return status;
    if(!(r->flags&SF)) { sub16(r,r->ax,0xffff,0); if(r->flags&ZF) return water_swap(r,0); }
    if(!question) {
        int found=platform_player(r,0); if(found<0) return UGH_BUDGET;
        if(!found) return tail(r,0x18);
        sub16(r,R(PlayerCarriedKinds,r->di),0,0); if(!(r->flags&ZF)) return tail(r,0x18);
    }
    if(actor_tick(r)) { status=frame(r,0,0x30,0); if(status) return status; }
    uint16_t count=dec16(r,A(ActorPhaseOrDemoLoopCursor)); B(ActorPhaseOrDemoLoopCursor,count); if(count) return UGH_OK;
    if(!question) return tail(r,0x1c);
    r->di=A(ActorSourcePlatformByteIndices);
    int found=platform_player(r,1); if(found<0) return UGH_BUDGET; return tail(r,found?0x14:0x10);
}
/* TRANSLATES GAME:UpdatePassengerDestinationDisplay */
EXPORT int c_UpdatePassengerDestinationDisplay(Regs *r) { return display(r,0); }
/* TRANSLATES GAME:UpdatePassengerQuestionDisplay */
EXPORT int c_UpdatePassengerQuestionDisplay(Regs *r) { return display(r,1); }

/* Approach tests platform presence (not carried-kind), selects a frame even
 * between ticks, and moves only when CX was incremented on expiry. */
/* TRANSLATES GAME:UpdatePassengerApproach */
EXPORT int c_UpdatePassengerApproach(Regs *r) {
    r->si=A(ActorDescriptors); if(submerged(r)) return water_swap(r,1);
    int status=ugh_call_near(G(FindPlayerTouchingActor),(uint16_t)(G(UpdatePassengerApproach)+0x3f),r); if(status) return status;
    if(!(r->flags&SF)) { sub16(r,r->ax,0xffff,0); if(r->flags&ZF) return water_swap(r,0); }
    int found=platform_player(r,0); if(found<0) return UGH_BUDGET; if(!found) return tail(r,0x18);
    r->cx=logic(r,0,16); if(actor_tick(r)) r->cx=inc(r,r->cx);
    r->ax=add16(r,A(ActorPixelX),F(0),0); r->ax=sub16(r,r->ax,16,0); sub16(r,r->ax,R(PlayerPixelX,r->di),0);
    if(r->flags&ZF) return tail(r,0x20);
    int left=gt(r); status=frame(r,0,left?0x32:0x34,0); if(status) return status;
    logic(r,r->cx,16); if(r->cx) B(ActorX32,left?sub16(r,A(ActorX32),32,0):add16(r,A(ActorX32),32,0));
    return UGH_OK;
}

/* Old descriptor supplies fares; paired land descriptor supplies all fields
 * in the shared 1A0D boarding tail. DI enters as player and exits as platform. */
/* TRANSLATES GAME:BoardWaterbornePassenger */
EXPORT int c_BoardWaterbornePassenger(Regs *r) {
    r->si=A(ActorDescriptors); r->ax=F(0x40); W(PlayerPassengerFares,r->di,r->ax);
    r->ax=F(0x42); W(PlayerMinimumFares,r->di,r->ax); r->si=F(0x48); B(ActorDescriptors,r->si);
    r->ax=F(0x22); B(ActorUpdateOrScriptCursor,r->ax); r->ax=F(0x46); W(PlayerCarriedKinds,r->di,r->ax);
    r->si=A(ActorDestinationPlatformByteIndices); r->ax=R(PlatformDestinationIcons,r->si); W(PlayerDestinationIcons,r->di,r->ax);
    B(ActorPhaseOrDemoLoopCursor,r->di); B(ActorSpriteIds,0xffff); B(PassengerQuickDeliveryCountdowns,200);
    r->di=A(ActorSourcePlatformByteIndices); W(PlatformActorOccupants,r->di,0xffff); return UGH_OK;
}

/* Fare uses unsigned MUL by a WORD multiplier, then ADD/ADC. Reward allocation
 * and sound are real calls, retained as unverified boundaries in this worktree. */
/* TRANSLATES GAME:DeliverPassenger */
EXPORT int c_DeliverPassenger(Regs *r) {
    r->si=A(ActorDescriptors); r->ax=F(0x26); B(ActorUpdateOrScriptCursor,r->ax);
    r->ax=logic(r,0,16); W(PlayerCarriedKinds,r->di,r->ax); W(PlayerDestinationIcons,r->di,r->ax);
    r->ax=sub16(r,16,F(0),0); r->ax=shift(r,r->ax,5,0); r->di=A(ActorPhaseOrDemoLoopCursor);
    r->ax=add16(r,r->ax,R(PlayerX32,r->di),0); B(ActorX32,r->ax); r->ax=R(PlayerPassengerFares,r->di);
    uint32_t product=(uint32_t)r->ax*R(ScoreMultiplier,0); r->ax=(uint16_t)product; r->dx=(uint16_t)(product>>16);
    flag(r,CF,r->dx!=0); flag(r,OF,r->dx!=0);
    W(ScoreLowWord,0,add16(r,R(ScoreLowWord,0),r->ax,0));
    W(ScoreHighWord,0,add16(r,R(ScoreHighWord,0),r->dx,!!(r->flags&CF)));
    logic(r,A(PassengerQuickDeliveryCountdowns),16);
    if(!(r->flags&ZF)) {
        push(r,r->si); r->ax=R(ScoreMultiplier,0); r->si=shift(r,R(SelectedDifficulty,0),1,0);
        sub16(r,r->ax,R(MultiplierLimitsByDifficulty,r->si),0);
        if(r->flags&CF) {
            r->ax=add16(r,R(PlayerX32,r->di),0x200,0); r->bp=add16(r,R(PlayerY32,r->di),0x140,0);
            r->cx=logic(r,0,16); r->dx=logic(r,0,16); r->si=D(FallingDescriptor_7A38);
            int status=ugh_call_near(F(4),(uint16_t)(G(DeliverPassenger)+0x70),r); if(status) return status;
            push(r,r->bx); status=effect(r,UGH_S_B3274_ext_3274,UGH_O_B3274_ext_3274,(uint16_t)(G(DeliverPassenger)+0x81));
            if(status) return status;
            r->bx=pop(r);
        }
        r->si=pop(r);
    }
    r->di=A(ActorDestinationPlatformByteIndices); r->ax=sub16(r,0,F(2),0);
    r->ax=add16(r,r->ax,R(PlatformHeights,r->di),0); r->ax=shift(r,r->ax,5,0); B(ActorY32,r->ax);
    B(ActorAnimationByteOffsets,0xfffe); r->ax=1; B(ActorAnimationCountdowns,r->ax); wr8(r->ds,D(HudFareClearPending),(uint8_t)r->ax); return UGH_OK;
}

/* SF from collision precedes carried-kind TEST; the miss sprite is always 220. */
/* TRANSLATES GAME:UpdateStonePickupWait */
EXPORT int c_UpdateStonePickupWait(Regs *r) {
    r->si=A(ActorDescriptors); int status=ugh_call_near(G(FindPlayerTouchingActor),(uint16_t)(G(UpdateStonePickupWait)+0x07),r); if(status) return status;
    if(!(r->flags&SF)) { logic(r,R(PlayerCarriedKinds,r->di),16); if(r->flags&ZF) return tail(r,0x20); }
    B(ActorSpriteIds,0x220); return UGH_OK;
}

static int enemy_stone(Regs *r,uint16_t return_ip,int sprite) {
    int status=ugh_call_near(G(FindThrownStoneHittingEnemy),return_ip,r); if(status) return status;
    if(r->flags&SF) return UGH_OK;
    W(ActorVerticalOrDemoPeriod,r->di,sub16(r,0,R(ActorVerticalOrDemoPeriod,r->di),0));
    if(sprite) W(ActorSpriteIds,r->di,0x222);
    return tail(r,0x1c);
}
static int enemy_player(Regs *r) {
    r->ax=A(EnemyPlatformIndices); r->di=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        sub16(r,r->ax,R(PlayerPlatformIndices,r->di),0); if(r->flags&ZF) return 1;
        r->di=add16(r,r->di,2,0); sub16(r,r->di,R(PlayerArrayBytes,0),0); if(r->flags&ZF) return 0;
    }
    return -1;
}
static void face_player(Regs *r) {
    r->cx=A(EnemyHorizontalSpeeds); r->ax=A(EnemyX32); sub16(r,r->ax,R(PlayerX32,r->di),0);
    if(!lt(r)) { r->ax=logic(r,0,16); logic(r,r->cx,16); if(!(r->flags&SF)) r->cx=sub16(r,0,r->cx,0); }
    else { r->ax=2; logic(r,r->cx,16); if(r->flags&SF) r->cx=sub16(r,0,r->cx,0); }
    B(EnemyDirectionOrTargetPlayer,r->ax); B(EnemyHorizontalSpeeds,r->cx);
}
static int enemy_tick(Regs *r,uint16_t period) {
    uint16_t count=dec16(r,A(EnemyAnimationCountdowns)); B(EnemyAnimationCountdowns,count); if(count) return 0;
    B(EnemyAnimationCountdowns,period); B(EnemyAnimationByteOffsets,add16(r,A(EnemyAnimationByteOffsets),2,0)); return 1;
}

/* Moves only every fourth update; contact with a player is a platform equality
 * scan before the thrown-stone collision. Reversal doesn't clip position. */
/* TRANSLATES GAME:UpdateTriopterusPatrol */
EXPORT int c_UpdateTriopterusPatrol(Regs *r) {
    r->si=A(EnemyDescriptors);
    uint16_t count=dec16(r,A(EnemyAnimationCountdowns)); B(EnemyAnimationCountdowns,count);
    if(!count) {
        r->di=shift(r,A(EnemyPlatformIndices),1,0); r->ax=add16(r,A(EnemyHorizontalSpeeds),A(EnemyX32),0); B(EnemyX32,r->ax);
        r->ax=shift(r,r->ax,5,1); sub16(r,r->ax,R(PlatformLeftEdges,r->di),0); int turn=lt(r);
        if(!turn) { r->ax=add16(r,r->ax,32,0); sub16(r,r->ax,R(PlatformRightEdges,r->di),0); turn=!lt(r); }
        if(turn) { B(EnemyHorizontalSpeeds,sub16(r,0,A(EnemyHorizontalSpeeds),0)); B(EnemyDirectionOrTargetPlayer,logic(r,A(EnemyDirectionOrTargetPlayer)^2,16)); }
        B(EnemyAnimationCountdowns,4); B(EnemyAnimationByteOffsets,add16(r,A(EnemyAnimationByteOffsets),2,0));
        int status=frame(r,1,0x22,1); if(status) return status;
    }
    int found=enemy_player(r); if(found<0) return UGH_BUDGET; if(found) return tail(r,0x0c);
    return enemy_stone(r,(uint16_t)(G(UpdateTriopterusPatrol)+0x8b),1);
}

/* Alert timer is equality-only; five-tick animation and collision precede
 * platform loss. Facing compares signed wrapped x32 words. */
/* TRANSLATES GAME:UpdateTriopterusAlert */
EXPORT int c_UpdateTriopterusAlert(Regs *r) {
    r->si=A(EnemyDescriptors); uint16_t count=dec16(r,A(EnemyStateCounters)); B(EnemyStateCounters,count); if(!count) return tail(r,0x10);
    if(enemy_tick(r,5)) { int status=frame(r,1,0x2e,1); if(status) return status; }
    int status=ugh_call_near(G(FindThrownStoneHittingEnemy),(uint16_t)(G(UpdateTriopterusAlert)+0x49),r); if(status) return status;
    if(!(r->flags&SF)) { W(ActorVerticalOrDemoPeriod,r->di,sub16(r,0,R(ActorVerticalOrDemoPeriod,r->di),0)); W(ActorSpriteIds,r->di,0x222); return tail(r,0x1c); }
    int found=enemy_player(r); if(found<0) return UGH_BUDGET; if(!found) return tail(r,8);
    face_player(r); return UGH_OK;
}

/* Charge acceleration uses direction-1 plus counter, then speed and position.
 * Impact uses SHL5 horizontal and SHL4 vertical, preserving their word wraps. */
/* TRANSLATES GAME:UpdateTriopterusCharge */
EXPORT int c_UpdateTriopterusCharge(Regs *r) {
    r->si=A(EnemyDescriptors); if(enemy_tick(r,4)) { int status=frame(r,1,0x26,1); if(status) return status; }
    int status=ugh_call_near(G(FindThrownStoneHittingEnemy),(uint16_t)(G(UpdateTriopterusCharge)+0x3d),r); if(status) return status;
    if(!(r->flags&SF)) { W(ActorVerticalOrDemoPeriod,r->di,sub16(r,0,R(ActorVerticalOrDemoPeriod,r->di),0)); W(ActorSpriteIds,r->di,0x222); return tail(r,0x1c); }
    int found=enemy_player(r); if(found<0) return UGH_BUDGET; if(!found) return tail(r,0x14);
    face_player(r); r->ax=dec16(r,A(EnemyDirectionOrTargetPlayer)); r->ax=add16(r,r->ax,A(EnemyStateCounters),0); B(EnemyStateCounters,r->ax);
    r->ax=add16(r,r->ax,A(EnemyHorizontalSpeeds),0); r->ax=add16(r,r->ax,A(EnemyX32),0); B(EnemyX32,r->ax);
    status=ugh_call_near(G(FindPlayerTouchingEnemy),(uint16_t)(G(UpdateTriopterusCharge)+0xbc),r); if(status) return status; if(r->flags&SF) return UGH_OK;
    W(PlayerY32,r->di,sub16(r,R(PlayerY32,r->di),32,0)); r->ax=add16(r,A(EnemyHorizontalSpeeds),A(EnemyStateCounters),0);
    push(r,r->ax); r->ax=shift(r,r->ax,5,0); W(PlayerHorizontalVelocities,r->di,r->ax); r->ax=pop(r);
    r->ax=shift(r,r->ax,4,0); W(PlayerVerticalVelocities,r->di,r->ax); W(PlayerPlatformIndices,r->di,0xffff); return tail(r,0x18);
}
/* Finite sequences tail on FFFF instead of looping; collision runs between
 * ticks as well. Initializer +16 discrepancy is deliberately left intact. */
static int recover(Regs *r,int impact) {
    r->si=A(EnemyDescriptors);
    if(enemy_tick(r,4)) {
        r->bp=A(EnemyDirectionOrTargetPlayer); r->di=rd16(r->ds,(uint16_t)(r->bp+r->si+(impact?0x32:0x2a)));
        r->di=add16(r,r->di,A(EnemyAnimationByteOffsets),0); r->ax=rd16(r->ds,r->di); sub16(r,r->ax,0xffff,0);
        if(r->flags&ZF) return tail(r,8);
        B(EnemySpriteIds,r->ax);
    }
    return enemy_stone(r,(uint16_t)(impact?G(AnimateTriopterusImpactRecovery)+0x38:G(AnimateTriopterusRecovery)+0x38),1);
}
/* TRANSLATES GAME:AnimateTriopterusRecovery */
EXPORT int c_AnimateTriopterusRecovery(Regs *r) { return recover(r,0); }
/* TRANSLATES GAME:AnimateTriopterusImpactRecovery */
EXPORT int c_AnimateTriopterusImpactRecovery(Regs *r) { return recover(r,1); }

/* Bird contact happens only on animation expiry. Stop sound calls a package
 * routine left absent here because its C sound dependency is unavailable. */
/* TRANSLATES GAME:UpdateBirdFlight */
EXPORT int c_UpdateBirdFlight(Regs *r) {
    r->si=A(EnemyDescriptors); r->ax=add16(r,A(EnemyHorizontalSpeeds),A(EnemyX32),0);
    sub16(r,r->ax,0xfc00,0); int gone=lt(r)||(r->flags&ZF);
    if(!gone) { sub16(r,r->ax,0x2800,0); gone=!lt(r); }
    if(gone) {
        int status=ugh_call_near(G(StopBirdFlightSound),(uint16_t)(G(UpdateBirdFlight)+0x1f),r); if(status) return status; return tail(r,8);
    }
    B(EnemyX32,r->ax); if(!enemy_tick(r,4)) return UGH_OK;
    /* Bird's sequence pointer is stored in its array, not the descriptor. */
    for(unsigned budget=0;;budget++) {
        if(budget==32768) return UGH_BUDGET;
        r->di=add16(r,A(EnemyAnimationOrDropLists),A(EnemyAnimationByteOffsets),0); r->ax=rd16(r->ds,r->di); sub16(r,r->ax,0xffff,0);
        if(r->ax!=0xffff) break;
        B(EnemyAnimationByteOffsets,0);
    }
    B(EnemySpriteIds,r->ax); int status=ugh_call_near(G(FindThrownStoneHittingEnemy),(uint16_t)(G(UpdateBirdFlight)+0x5b),r); if(status) return status;
    if(!(r->flags&SF)) {
        status=ugh_call_near(G(StopBirdFlightSound),(uint16_t)(G(UpdateBirdFlight)+0x63),r); if(status) return status;
        W(ActorVerticalOrDemoPeriod,r->di,sub16(r,0,R(ActorVerticalOrDemoPeriod,r->di),0)); W(ActorSpriteIds,r->di,0x222); return tail(r,0x1c);
    }
    status=ugh_call_near(G(FindPlayerTouchingEnemy),(uint16_t)(G(UpdateBirdFlight)+0x73),r); if(status) return status; if(r->flags&SF) return UGH_OK;
    uint16_t old=r->di; r->di=(uint16_t)(old>>1); flag(r,CF,old&1); flag(r,OF,old&0x8000); szp(r,r->di,16);
    sub16(r,r->di,A(EnemyDirectionOrTargetPlayer),0); if(!(r->flags&ZF)) return UGH_OK;
    sub16(r,R(ScreenFadeStep,0),0,0); if(lt(r)) return UGH_OK;
    r->ax=0xfffe; W(ScreenFadeStep,0,r->ax); W(ScreenFadeLevel,0,add16(r,R(ScreenFadeLevel,0),r->ax,0)); return UGH_OK;
}

/* Stationary hazard: scan retries on equality to PlayerCount, not array bytes.
 * Sound occurs only when a tick increments the animation offset to six. */
/* TRANSLATES GAME:UpdateDinoForce */
EXPORT int c_UpdateDinoForce(Regs *r) {
    r->si=A(EnemyDescriptors);
    if(enemy_tick(r,15)) {
        sub16(r,A(EnemyAnimationByteOffsets),6,0);
        if(r->flags&ZF) {
            push(r,r->bx); push(r,r->si); int status=effect(r,UGH_S_B3265_ext_3265,UGH_O_B3265_ext_3265,(uint16_t)(G(UpdateDinoForce)+0x34));
            if(status) return status;
            r->si=pop(r); r->bx=pop(r);
        }
        int status=frame(r,1,0x26,0); if(status) return status;
    }
    r->di=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        r->ax=shift(r,sub16(r,F(2),9,0),5,0); r->ax=add16(r,r->ax,A(EnemyY32),0); sub16(r,r->ax,R(PlayerY32,r->di),0); if(lt(r)) goto next;
        r->ax=shift(r,sub16(r,F(2),30,0),5,0); r->ax=add16(r,r->ax,A(EnemyY32),0); sub16(r,r->ax,R(PlayerY32,r->di),0); if(gt(r)) goto next;
        r->ax=shift(r,sub16(r,F(0),16,0),5,0); r->ax=add16(r,r->ax,A(EnemyX32),0); sub16(r,r->ax,R(PlayerX32,r->di),0); if(lt(r)) goto next;
        r->ax=shift(r,sub16(r,F(0),104,0),5,0); r->ax=add16(r,r->ax,A(EnemyX32),0); r->ax=sub16(r,r->ax,0x340,0); sub16(r,r->ax,R(PlayerX32,r->di),0); if(gt(r)) goto next;
        sub16(r,A(EnemyAnimationByteOffsets),5,0); r->ax=lt(r)?41:0xffd7; W(PlayerHorizontalVelocities,r->di,add16(r,R(PlayerHorizontalVelocities,r->di),r->ax,0));
next:   r->di=add16(r,r->di,2,0); sub16(r,r->di,R(PlayerCount,0),0); if(!(r->flags&ZF)) break;
        if(budget==32767) return UGH_BUDGET;
    }
    return enemy_stone(r,(uint16_t)(G(UpdateDinoForce)+0xd3),0);
}

/* Tree contacts only every sixth update; NEG then SAR rounds odd descending
 * stone speed downward. Its reward tail is an unavailable sound boundary. */
/* TRANSLATES GAME:UpdateFruitTreeAnimation */
EXPORT int c_UpdateFruitTreeAnimation(Regs *r) {
    uint16_t count=dec16(r,A(EnemyAnimationCountdowns)); B(EnemyAnimationCountdowns,count); if(count) return UGH_OK;
    r->si=A(EnemyDescriptors); B(EnemyAnimationCountdowns,6); B(EnemyAnimationByteOffsets,add16(r,A(EnemyAnimationByteOffsets),2,0));
    int status=frame(r,1,0x22,0); if(status) return status;
    status=ugh_call_near(G(FindThrownStoneHittingEnemy),(uint16_t)(G(UpdateFruitTreeAnimation)+0x38),r); if(status) return status;
    if(r->flags&SF) return UGH_OK;
    r->ax=sub16(r,0,R(ActorVerticalOrDemoPeriod,r->di),0); r->ax=shift(r,r->ax,1,1); W(ActorVerticalOrDemoPeriod,r->di,r->ax); W(ActorSpriteIds,r->di,0x222);
    r->si=A(EnemyDescriptors); return tail(r,0x1c);
}

/* Item lifetime DEC wraps zero. Benefits use unsigned caps AFTER wrapped ADD.
 * Lives/multiplier stores write AL only, retaining the adjacent stale byte. */
/* TRANSLATES GAME:ExpireOrCollectFallingItem */
EXPORT int c_ExpireOrCollectFallingItem(Regs *r) {
    uint16_t count=dec16(r,A(FallingItemMotionOrLifetime)); B(FallingItemMotionOrLifetime,count); if(!count) goto remove;
    r->si=A(FallingItemDescriptors); int status=ugh_call_near(G(FindPlayerTouchingFallingItem),(uint16_t)(G(ExpireOrCollectFallingItem)+0x18),r); if(status) return status;
    if(r->flags&SF) return UGH_OK;
    r->ax=F(0x12); sub16(r,r->ax,0,0);
    if(r->flags&ZF) {
        r->ax=add16(r,F(0x0e),R(LevelTimer,0),0); sub16(r,r->ax,0x5a3b,0);
        if(!(r->flags&(CF|ZF))) r->ax=0x5a3b;
        W(LevelTimer,0,r->ax); goto remove;
    }
    sub16(r,r->ax,1,0);
    if(r->flags&ZF) {
        r->ax=F(0x0e); set_al(r,byte_add(r,(uint8_t)r->ax,rd8(r->ds,D(LivesRemaining)))); byte_sub(r,(uint8_t)r->ax,99);
        if(!(r->flags&(CF|ZF))) set_al(r,99);
        wr8(r->ds,D(LivesRemaining),(uint8_t)r->ax); goto remove;
    }
    r->ax=R(ScoreMultiplier,0); r->di=shift(r,R(SelectedDifficulty,0),1,0); sub16(r,r->ax,R(MultiplierLimitsByDifficulty,r->di),0);
    if(r->flags&CF) {
        uint16_t cf=r->flags&CF; set_al(r,byte_add(r,(uint8_t)r->ax,1)); flag(r,CF,cf); wr8(r->ds,D(ScoreMultiplier),(uint8_t)r->ax);
    }
remove: B(FallingItemSprites,0xffff); return UGH_OK;
}

/* Water uses AL(Y)*byte(stride), descending 80 byte latch reads/writes,
 * then real RestoreBackgroundRectangle tail; pending skips advancement. */
/* TRANSLATES GAME:AdvanceWaterSurface */
EXPORT int c_AdvanceWaterSurface(Regs *r) {
    logic(r,rd8(r->ds,D(WaterRestorePending)),8);
    if(!(r->flags&ZF)) wr8(r->ds,D(WaterRestorePending),0);
    else {
        r->ax=R(WaterYPixels,0); W(PreviousWaterSurfaceY,0,r->ax); r->ax=R(WaterY32,0);
        uint8_t phase=(uint8_t)logic(r,rd8(r->ds,D(WaterStepPhase))^1,8); wr8(r->ds,D(WaterStepPhase),phase);
        if(!phase) { r->ax=add16(r,r->ax,R(WaterSurfaceStep,0),0); if(r->flags&SF) r->ax=logic(r,0,16); }
        W(WaterY32,0,r->ax); r->ax=shift(r,r->ax,5,1); W(WaterYPixels,0,r->ax); sub16(r,r->ax,R(PreviousWaterSurfaceY,0),0);
        if(r->flags&ZF) return UGH_OK;
        push(r,r->ds); r->dx=0x3ce; set_al(r,8); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=inc(r,r->dx); set_al(r,0x40); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=dec16(r,r->dx); set_al(r,3); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=inc(r,r->dx); set_al(r,0x10); platform_out(r->dx,1,(uint8_t)r->ax);
        r->ax=R(PreviousWaterSurfaceY,0); r->ax=(uint16_t)((uint8_t)r->ax*rd8(r->ds,D(VgaRowStrideBytes)));
        flag(r,CF,r->ax>255); flag(r,OF,r->ax>255);
        r->si=rd16(r->cs,G(BackgroundPagePointer)); r->ds=rd16(r->cs,(uint16_t)(G(BackgroundPagePointer)+2)); r->si=add16(r,r->si,r->ax,0);
        r->bx=79; set_al(r,0x40);
        do { set_ah(r,rd8(r->ds,(uint16_t)(r->bx+r->si))); wr8(r->ds,(uint16_t)(r->bx+r->si),(uint8_t)r->ax); r->bx=dec16(r,r->bx); } while(!(r->flags&SF));
        r->dx=0x3ce; set_al(r,8); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=inc(r,r->dx); set_al(r,255); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=dec16(r,r->dx); set_al(r,3); platform_out(r->dx,1,(uint8_t)r->ax);
        r->dx=inc(r,r->dx); set_al(r,(uint8_t)logic(r,0,8)); platform_out(r->dx,1,(uint8_t)r->ax);
        r->ds=pop(r); wr8(r->ds,D(WaterRestorePending),byte_dec(r,rd8(r->ds,D(WaterRestorePending))));
    }
    r->ax=logic(r,0,16); r->bx=R(PreviousWaterSurfaceY,0); r->cx=320; r->dx=1;
    return ugh_dispatch(r->cs,G(RestoreBackgroundRectangle),r);
}
