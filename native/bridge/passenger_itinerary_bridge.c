#include "ugh.h"
#include "../passenger_itinerary.h"
#include "actor_projection.h"
typedef struct ItineraryPlan {
    PassengerStoneSlot slot;ActorType type;ActorRenderHistory render;
    ItineraryWorld world;LevelPlatform platforms[10];ItineraryPlatformUse uses[10];
    PassengerJourney journey;PassengerJourneyLeg legs[256];uint16_t frames[4][256];
    ItineraryResult result;size_t consumed;uint16_t journey_base;int bad;
} ItineraryPlan;
static uint16_t itinerary_word(Regs *r,uint16_t base,uint16_t index) {return rd16(r->ds,(uint16_t)(base+index));}
static uint16_t itinerary_phase_code(uint16_t phase) {
    if(phase==ACTOR_WAIT_FOR_PLATFORM) return G(WaitForPassengerPlatform);
    if(phase==ACTOR_ARRIVING) return G(AnimatePassengerArrival);
    if(phase==ACTOR_DEPARTING) return G(AnimatePassengerDeparture);
    if(phase==ACTOR_RETIRED) return G(IgnoreActorState);
    return 0; /* unknown phases never silently become retirement */
}
static uint16_t itinerary_consume(ItineraryPlan *plan,Regs *r,uint16_t address,uint16_t expected,int byte) {
    if(plan->consumed>=plan->result.count) {plan->bad=1;return 0;}
    ItineraryWrite write=plan->result.writes[plan->consumed++];uint16_t base=0,index=r->bx,value=write.value;int width=0;
    if(write.field!=IT_OCCUPANT && write.index!=0) plan->bad=1;
    switch(write.field) {
    case IT_PHASE:base=D(ActorUpdateOrScriptCursor);value=itinerary_phase_code(value);break;
    case IT_SOURCE:base=D(ActorPlatformOrScriptDone);break;
    case IT_DESTINATION:base=D(ActorDestinationPlatforms);break;
    case IT_SOURCE_INDEX:base=D(ActorSourcePlatformByteIndices);value=(uint16_t)(2u*value);break;
    case IT_DESTINATION_INDEX:base=D(ActorDestinationPlatformByteIndices);value=(uint16_t)(2u*value);break;
    case IT_DELAY:base=D(ActorMotionWaitOrDemoRepeats);break;
    case IT_X:base=D(ActorX32);break;case IT_Y:base=D(ActorY32);break;
    case IT_PIXEL_X:base=D(ActorPixelX);break;case IT_PIXEL_Y:base=D(ActorPixelY);break;
    case IT_CURSOR:base=D(ActorAnimationByteOffsets);break;case IT_COUNTDOWN:base=D(ActorAnimationCountdowns);break;
    case IT_SPRITE:base=D(ActorSpriteIds);break;
    case IT_JOURNEY:base=D(ActorJourneyCursors);value=(uint16_t)(plan->journey_base+4u*value);break;
    case IT_OCCUPANT:base=D(PlatformActorOccupants);index=(uint16_t)(2u*write.index);value=(uint16_t)(2u*value);break;
    case IT_REMAINING:base=D(RemainingPassengerJourneys);index=0;width=1;break;
    case IT_COMPLETION:base=D(LevelCompletionMarker);index=0;width=1;break;
    case IT_FADE_RATE:base=D(ScreenFadeStep);index=0;break;
    case IT_FADE_LEVEL:base=D(ScreenFadeLevel);index=0;break;
    }
    if((uint16_t)(base+index)!=address || width!=byte || value!=expected) plan->bad=1;
    return value;
}
static void itinerary_write16(ItineraryPlan *plan,Regs *r,uint16_t address,uint16_t expected) {
    uint16_t value=itinerary_consume(plan,r,address,expected,0);wr16(r->ds,address,value);
}
static void itinerary_write8(ItineraryPlan *plan,Regs *r,uint16_t address,uint8_t expected) {
    uint16_t value=itinerary_consume(plan,r,address,expected,1);wr8(r->ds,address,(uint8_t)value);
}
static int itinerary_dispatch(Regs *r,ItineraryPlan *plan,uint16_t target) {
    uint16_t expected=0;
    switch(plan->result.next) {
    case IT_NEXT_PLACE:expected=G(PlacePassengerOnPlatform);break;
    case IT_NEXT_PLATFORM_WAIT:expected=G(BeginPassengerPlatformWait);break;
    case IT_NEXT_DEPARTURE:expected=G(BeginPassengerDeparture);break;
    case IT_NEXT_READ:expected=G(ReadPassengerJourneyLeg);break;
    case IT_NEXT_IGNORE:expected=G(IgnoreActorState);break;
    default:plan->bad=1;break;
    }
    if(plan->bad || plan->consumed!=plan->result.count || expected!=target) {plan->bad=1;return UGH_BAD_CALLBACK;}
    return ugh_dispatch(r->cs,target,r);
}
static int itinerary_vector(Regs *r,uint16_t pointer,uint16_t *words,ActorAnimation *animation) {
    size_t count=0;
    /* This unit borrows the registered immutable animation bank. Modified
     * references outside it keep L1, including mutable-output aliases. */
    while(pointer>=D(Animation_0E20) && pointer<0x1020u && count<256) {
        uint16_t sprite=rd16(r->ds,pointer);
        if(sprite==65535u) {animation->sprites=words;animation->count=count;return 1;}
        words[count++]=sprite;pointer=(uint16_t)(pointer+2);
    }
    return 0;
}
static int itinerary_prepare(Regs *r,ItineraryEntry entry,ItineraryPlan *plan) {
    if(r->ds!=DATA_SEG || r->cs!=GAME_SEG || (r->bx&1u) || r->bx>=32u) return 0;
    uint16_t descriptor=itinerary_word(r,D(ActorDescriptors),r->bx);
    if(descriptor!=D(Data_7720) && descriptor!=D(Data_77B4) && descriptor!=D(Data_7848)) return 0;
    const unsigned fields[]={8,10,12,14,16,38,40,42,44};
    const uint16_t targets[]={G(ReadPassengerJourneyLeg),G(WaitForPassengerPlatform),G(PlacePassengerOnPlatform),G(AnimatePassengerArrival),
        G(BeginPassengerPlatformWait),G(WalkPassengerToExit),G(BeginPassengerDeparture),G(AnimatePassengerDeparture),G(IgnoreActorState)};
    for(size_t i=0;i<9;i++) if(rd16(r->ds,(uint16_t)(descriptor+fields[i]))!=targets[i]) return 0;
    *plan=(ItineraryPlan){0};plan->slot.type=&plan->type;
    plan->type.id=descriptor==D(Data_7720)?ACTOR_PASSENGER_ONE_LAND:descriptor==D(Data_77B4)?ACTOR_PASSENGER_TWO_LAND:ACTOR_PASSENGER_THREE_LAND;
    plan->type.geometry.anchor_x=rd16(r->ds,descriptor);plan->type.geometry.anchor_y=rd16(r->ds,(uint16_t)(descriptor+2));
    plan->type.animation_period=rd16(r->ds,(uint16_t)(descriptor+62));
    ActorPhase phase=entry==IT_WAIT || entry==IT_PLACE?ACTOR_WAIT_FOR_PLATFORM:entry==IT_ARRIVAL?ACTOR_ARRIVING:
        entry==IT_WALK || entry==IT_BEGIN_DEPARTURE?ACTOR_WALK_TO_EXIT:entry==IT_DEPARTURE?ACTOR_DEPARTING:ACTOR_READ_JOURNEY;
    if(!actor_bridge_alias_project(r->ds,r->bx/2u,phase,&plan->slot)) return 0;
    plan->slot.source_platform=itinerary_word(r,D(ActorPlatformOrScriptDone),r->bx);
    plan->slot.destination_platform=itinerary_word(r,D(ActorDestinationPlatforms),r->bx);
    if((entry==IT_WAIT || entry==IT_PLACE) && (plan->slot.source_platform>=10 || itinerary_word(r,D(ActorSourcePlatformByteIndices),r->bx)!=2u*plan->slot.source_platform)) return 0;
    if(entry==IT_WALK && (plan->slot.destination_platform>=10 || itinerary_word(r,D(ActorDestinationPlatformByteIndices),r->bx)!=2u*plan->slot.destination_platform)) return 0;
    plan->slot.position.x32=itinerary_word(r,D(ActorX32),r->bx);plan->slot.position.y32=itinerary_word(r,D(ActorY32),r->bx);
    plan->slot.sprite=itinerary_word(r,D(ActorSpriteIds),r->bx);
    plan->slot.animation.byte_offset=itinerary_word(r,D(ActorAnimationByteOffsets),r->bx);
    plan->slot.animation.countdown=itinerary_word(r,D(ActorAnimationCountdowns),r->bx);
    plan->render.pixel_x=itinerary_word(r,D(ActorPixelX),r->bx);plan->render.pixel_y=itinerary_word(r,D(ActorPixelY),r->bx);
    plan->render.previous_x=itinerary_word(r,D(ActorPreviousDrawX),r->bx);plan->render.previous_y=itinerary_word(r,D(ActorPreviousDrawY),r->bx);
    plan->render.erase_sprite=itinerary_word(r,D(ActorEraseSprite),r->bx);plan->render.erase_overlay_sprite=itinerary_word(r,D(ActorEraseOverlaySprite),r->bx);
    plan->world.platforms=plan->platforms;plan->world.uses=plan->uses;plan->world.platform_count=10;plan->world.actor=r->bx/2u;
    for(unsigned i=0;i<10;i++) {
        plan->platforms[i].surface_y=itinerary_word(r,D(PlatformHeights),(uint16_t)(2u*i));
        plan->platforms[i].arrival_x=itinerary_word(r,D(PlatformArrivalPointsX),(uint16_t)(2u*i));
        plan->uses[i].available=itinerary_word(r,D(PlatformActorOccupants),(uint16_t)(2u*i))==65535u;
    }
    plan->world.remaining=rd8(r->ds,D(RemainingPassengerJourneys));plan->world.completion=rd8(r->ds,D(LevelCompletionMarker));
    plan->world.fade_rate=rd16(r->ds,D(ScreenFadeStep));plan->world.fade_level=rd16(r->ds,D(ScreenFadeLevel));
    plan->journey_base=itinerary_word(r,D(ActorJourneyCursors),r->bx);
    if(entry==IT_READ) {
        uint16_t pointer=plan->journey_base;
        if(pointer>65529u || (pointer< D(ActorDescriptors)+768u && pointer+6u>D(ActorDescriptors))) return 0;
        if(!actor_bridge_journey(r->ds,pointer,plan->legs,&plan->journey) || !plan->journey.count) return 0;
        plan->slot.journey.journey=&plan->journey;
    }
    if(plan->slot.animation.countdown==1 && (entry==IT_ARRIVAL || entry==IT_WALK || entry==IT_DEPARTURE)) {
        const unsigned offsets[]={50,52,54,56};const ActorAnimationKind kinds[]={ACTOR_WALK_LEFT_ANIMATION,ACTOR_WALK_RIGHT_ANIMATION,ACTOR_ARRIVAL_ANIMATION,ACTOR_DEPARTURE_ANIMATION};
        for(unsigned i=0;i<4;i++) {
            if(entry==IT_ARRIVAL && i!=2) continue;
            if(entry==IT_DEPARTURE && i!=3) continue;
            if(entry==IT_WALK && i>1) continue;
            if(!itinerary_vector(r,rd16(r->ds,(uint16_t)(descriptor+offsets[i])),plan->frames[i],&plan->type.animations[kinds[i]])) return 0;
        }
    }
    plan->result=itinerary_apply(entry,&plan->slot,&plan->render,&plan->world);return !plan->result.failed;
}
/* ITINERARY_SHELLS_BEGIN */
/* Derived machine shell: expected expressions are diagnostics; native journal values alone are published. */
#define READ(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define WRITE(n,i,v) itinerary_write16(plan,r,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define A(n) READ(n,r->bx)
#define W(n,v) WRITE(n,r->bx,v)
#define DESC(n) rd16(r->ds,(uint16_t)(r->si+(n)))
static int it_shell0_state_jump(Regs *r,ItineraryPlan *plan,uint16_t target);
static int it_shell0_tail(Regs *r,ItineraryPlan *plan,unsigned field);
static uint16_t it_shell0_shl(Regs *r,uint16_t v,unsigned n) {
    for(unsigned i=0;i<n;i++) { flag(r,CF,v&0x8000u); v=(uint16_t)(v<<1); }
    szp(r,v,16); if(n==1) flag(r,OF,!!(v&0x8000u)^!!(r->flags&CF));
    return v;
}

static uint16_t it_shell0_sar(Regs *r,uint16_t v,unsigned n) {
    for(unsigned i=0;i<n;i++) { flag(r,CF,v&1); v=(uint16_t)((v>>1)|(v&0x8000u)); }
    szp(r,v,16); if(n==1) flag(r,OF,0); return v;
}

static int it_shell0_less(const Regs *r) { return !!(r->flags&SF)!=!!(r->flags&OF); }

static void it_shell0_actor_init(Regs *r,ItineraryPlan *plan,unsigned field) {
    r->si=A(ActorDescriptors); r->ax=DESC(field);
    W(ActorUpdateOrScriptCursor,r->ax);
    W(ActorAnimationByteOffsets,0xfffe); W(ActorAnimationCountdowns,1);
}

static int it_shell0_actor_tick(Regs *r,ItineraryPlan *plan) {
    uint16_t count=dec16(r,A(ActorAnimationCountdowns));
    W(ActorAnimationCountdowns,count);
    if(count) return 0;
    r->ax=DESC(0x3e); W(ActorAnimationCountdowns,r->ax);
    W(ActorAnimationByteOffsets,add16(r,A(ActorAnimationByteOffsets),2,0));
    return 1;
}

static int it_shell0_actor_frame(Regs *r,ItineraryPlan *plan,unsigned field) {
    for(unsigned budget=0;budget<32768;budget++) {
        r->di=DESC(field);
        r->di=add16(r,r->di,A(ActorAnimationByteOffsets),0);
        r->ax=rd16(r->ds,r->di); sub16(r,r->ax,0xffff,0);
        if(r->ax!=0xffff) { W(ActorSpriteIds,r->ax); return UGH_OK; }
        W(ActorAnimationByteOffsets,0);
    }
    return UGH_BUDGET;
}

static int it_shell0_tail(Regs *r,ItineraryPlan *plan, unsigned field) { return it_shell0_state_jump(r,plan,DESC(field)); }

static int it_shell0_state_jump(Regs *r,ItineraryPlan *plan,uint16_t target) { return itinerary_dispatch(r,plan,target); }

static int shell_WaitForPassengerPlatform(Regs *r,ItineraryPlan *plan) {
    W(ActorSpriteIds,0xffff); r->ax=A(ActorMotionWaitOrDemoRepeats); sub16(r,r->ax,0,0);
    if(r->ax) { r->ax=dec16(r,r->ax); W(ActorMotionWaitOrDemoRepeats,r->ax); if(r->ax) return UGH_OK; }
    r->di=A(ActorSourcePlatformByteIndices);
    sub16(r,READ(PlatformActorOccupants,r->di),0xffff,0);
    if(!(r->flags&ZF)) return UGH_OK;
    r->si=A(ActorDescriptors); return it_shell0_tail(r,plan,0x0c);
}

static int shell_PlacePassengerOnPlatform(Regs *r,ItineraryPlan *plan) {
    r->si=A(ActorDescriptors); r->ax=DESC(0x0e); W(ActorUpdateOrScriptCursor,r->ax);
    r->di=A(ActorSourcePlatformByteIndices); WRITE(PlatformActorOccupants,r->di,r->bx);
    r->ax=sub16(r,0,DESC(2),0); r->ax=add16(r,r->ax,READ(PlatformHeights,r->di),0);
    W(ActorPixelY,r->ax); r->ax=it_shell0_shl(r,r->ax,5); W(ActorY32,r->ax);
    r->ax=sub16(r,0,DESC(0),0); r->ax=add16(r,r->ax,READ(PlatformArrivalPointsX,r->di),0);
    W(ActorPixelX,r->ax); r->ax=it_shell0_shl(r,r->ax,5); W(ActorX32,r->ax);
    W(ActorAnimationByteOffsets,0xfffe); W(ActorAnimationCountdowns,1); return UGH_OK;
}

static int shell_AnimatePassengerArrival(Regs *r,ItineraryPlan *plan) {
    uint16_t count=dec16(r,A(ActorAnimationCountdowns)); W(ActorAnimationCountdowns,count);
    if(count) return UGH_OK;
    r->si=A(ActorDescriptors); r->ax=DESC(0x3e); W(ActorAnimationCountdowns,r->ax);
    W(ActorAnimationByteOffsets,add16(r,A(ActorAnimationByteOffsets),2,0));
    r->di=DESC(0x36); r->di=add16(r,r->di,A(ActorAnimationByteOffsets),0);
    r->ax=rd16(r->ds,r->di); sub16(r,r->ax,0xffff,0);
    if(r->ax==0xffff) return it_shell0_tail(r,plan,0x10);
    W(ActorSpriteIds,r->ax); return UGH_OK;
}

static int shell_WalkPassengerToExit(Regs *r,ItineraryPlan *plan) {
    r->di=A(ActorDestinationPlatformByteIndices); r->si=A(ActorDescriptors);
    if(!it_shell0_actor_tick(r,plan)) return UGH_OK;
    r->ax=add16(r,A(ActorPixelX),DESC(0),0);
    sub16(r,r->ax,READ(PlatformArrivalPointsX,r->di),0);
    if(r->flags&ZF) return it_shell0_tail(r,plan,0x28);
    int left=!it_shell0_less(r), status=it_shell0_actor_frame(r,plan,left?0x32:0x34); if(status) return status;
    W(ActorX32,left?sub16(r,A(ActorX32),32,0):add16(r,A(ActorX32),32,0));
    r->di=A(ActorDestinationPlatformByteIndices); r->cx=logic(r,0,16);
    r->ax=it_shell0_sar(r,A(ActorX32),5); r->ax=add16(r,r->ax,DESC(0),0);
    sub16(r,r->ax,READ(PlatformArrivalPointsX,r->di),0);
    return (r->flags&ZF)?it_shell0_tail(r,plan,0x28):UGH_OK;
}

static int shell_BeginPassengerDeparture(Regs *r,ItineraryPlan *plan) { it_shell0_actor_init(r,plan,0x2a); return UGH_OK; }

static int shell_AnimatePassengerDeparture(Regs *r,ItineraryPlan *plan) {
    uint16_t count=dec16(r,A(ActorAnimationCountdowns)); W(ActorAnimationCountdowns,count);
    if(count) return UGH_OK;
    r->si=A(ActorDescriptors); r->ax=DESC(0x3e); W(ActorAnimationCountdowns,r->ax);
    W(ActorAnimationByteOffsets,add16(r,A(ActorAnimationByteOffsets),2,0));
    r->di=DESC(0x38); r->di=add16(r,r->di,A(ActorAnimationByteOffsets),0);
    r->ax=rd16(r->ds,r->di); W(ActorSpriteIds,r->ax);
    sub16(r,rd16(r->ds,(uint16_t)(r->di+2)),0xffff,0);
    if(!(r->flags&ZF)) return UGH_OK;
    W(ActorJourneyCursors,add16(r,A(ActorJourneyCursors),4,0)); return it_shell0_tail(r,plan,8);
}

#undef READ
#undef WRITE
#undef A
#undef W
#undef DESC
#undef R
#undef B
#undef F
#define R(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define W(n,i,v) itinerary_write16(plan,r,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define A(n) R(n,r->bx)
#define B(n,v) W(n,r->bx,v)
#define F(n) rd16(r->ds,(uint16_t)(r->si+(n)))
static uint16_t it_shell1_shift(Regs *r,uint16_t v,unsigned n,int right) {
    for(unsigned i=0;i<n;i++) {
        flag(r,CF,right?(v&1):(v&0x8000));
        v=right?(uint16_t)((v>>1)|(v&0x8000)):(uint16_t)(v<<1);
    }
    szp(r,v,16); if(n==1) flag(r,OF,right?0:(!!(v&0x8000)^!!(r->flags&CF)));
    return v;
}

static uint8_t it_shell1_byte_sub(Regs *r,uint8_t a,uint8_t b) {
    uint8_t v=(uint8_t)(a-b);
    flag(r,CF,a<b); flag(r,OF,((a^b)&(a^v)&128)!=0);
    flag(r,AF,((a^b^v)&16)!=0); szp(r,v,8); return v;
}

static uint8_t it_shell1_byte_dec(Regs *r,uint8_t a) {
    uint16_t cf=r->flags&CF; uint8_t v=it_shell1_byte_sub(r,a,1); flag(r,CF,cf); return v;
}

static int shell_ReadPassengerJourneyLeg(Regs *r,ItineraryPlan *plan) {
    r->di=A(ActorJourneyCursors); r->ax=rd16(r->ds,(uint16_t)(r->di+4)); sub16(r,r->ax,0xffff,0);
    if(r->ax==0xffff) {
        set_al(r,rd8(r->ds,D(RemainingPassengerJourneys))); set_al(r,it_shell1_byte_dec(r,(uint8_t)r->ax));
        if(!(r->flags&SF)) {
            itinerary_write8(plan,r,D(RemainingPassengerJourneys),(uint8_t)r->ax);
            if(r->flags&ZF) {
                r->ax=0xfffe; W(ScreenFadeStep,0,r->ax);
                W(ScreenFadeLevel,0,add16(r,R(ScreenFadeLevel,0),r->ax,0));
                itinerary_write8(plan,r,D(LevelCompletionMarker),(uint8_t)r->ax);
            }
        }
        B(ActorSpriteIds,0xffff); r->si=A(ActorDescriptors); r->ax=F(0x2c);
        B(ActorUpdateOrScriptCursor,r->ax); return itinerary_dispatch(r,plan,r->ax);
    }
    B(ActorDestinationPlatforms,r->ax); r->ax=it_shell1_shift(r,r->ax,1,0); B(ActorDestinationPlatformByteIndices,r->ax);
    r->ax=rd16(r->ds,r->di); B(ActorPlatformOrScriptDone,r->ax);
    r->ax=it_shell1_shift(r,r->ax,1,0); B(ActorSourcePlatformByteIndices,r->ax);
    r->ax=rd16(r->ds,(uint16_t)(r->di+2));
    int status=ugh_call_near(G(ScaleLevelSpeedToThreeHalves),(uint16_t)(G(ReadPassengerJourneyLeg)+0x5d),r); if(status) return status;
    B(ActorMotionWaitOrDemoRepeats,r->ax); r->si=A(ActorDescriptors); r->ax=F(0x0a); B(ActorUpdateOrScriptCursor,r->ax); return UGH_OK;
}

#undef READ
#undef WRITE
#undef A
#undef W
#undef DESC
#undef R
#undef B
#undef F
/* ITINERARY_SHELLS_END */
/* ITINERARY_EXPORTS_BEGIN */
int l1_ReadPassengerJourneyLeg(Regs *r);
int l1_WaitForPassengerPlatform(Regs *r);
int l1_PlacePassengerOnPlatform(Regs *r);
int l1_AnimatePassengerArrival(Regs *r);
int l1_WalkPassengerToExit(Regs *r);
int l1_BeginPassengerDeparture(Regs *r);
int l1_AnimatePassengerDeparture(Regs *r);
EXPORT int c_ReadPassengerJourneyLeg(Regs *r) {
    ItineraryPlan plan;
    if(!itinerary_prepare(r,IT_READ,&plan)) return l1_ReadPassengerJourneyLeg(r);
    int status=shell_ReadPassengerJourneyLeg(r,&plan);
    if(plan.bad || plan.consumed!=plan.result.count) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_WaitForPassengerPlatform(Regs *r) {
    ItineraryPlan plan;
    if(!itinerary_prepare(r,IT_WAIT,&plan)) return l1_WaitForPassengerPlatform(r);
    int status=shell_WaitForPassengerPlatform(r,&plan);
    if(plan.bad || plan.consumed!=plan.result.count) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_PlacePassengerOnPlatform(Regs *r) {
    ItineraryPlan plan;
    if(!itinerary_prepare(r,IT_PLACE,&plan)) return l1_PlacePassengerOnPlatform(r);
    int status=shell_PlacePassengerOnPlatform(r,&plan);
    if(plan.bad || plan.consumed!=plan.result.count) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_AnimatePassengerArrival(Regs *r) {
    ItineraryPlan plan;
    if(!itinerary_prepare(r,IT_ARRIVAL,&plan)) return l1_AnimatePassengerArrival(r);
    int status=shell_AnimatePassengerArrival(r,&plan);
    if(plan.bad || plan.consumed!=plan.result.count) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_WalkPassengerToExit(Regs *r) {
    ItineraryPlan plan;
    if(!itinerary_prepare(r,IT_WALK,&plan)) return l1_WalkPassengerToExit(r);
    int status=shell_WalkPassengerToExit(r,&plan);
    if(plan.bad || plan.consumed!=plan.result.count) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_BeginPassengerDeparture(Regs *r) {
    ItineraryPlan plan;
    if(!itinerary_prepare(r,IT_BEGIN_DEPARTURE,&plan)) return l1_BeginPassengerDeparture(r);
    int status=shell_BeginPassengerDeparture(r,&plan);
    if(plan.bad || plan.consumed!=plan.result.count) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_AnimatePassengerDeparture(Regs *r) {
    ItineraryPlan plan;
    if(!itinerary_prepare(r,IT_DEPARTURE,&plan)) return l1_AnimatePassengerDeparture(r);
    int status=shell_AnimatePassengerDeparture(r,&plan);
    if(plan.bad || plan.consumed!=plan.result.count) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_IgnoreActorState(Regs *r) {
    (void)r;ItineraryResult result=itinerary_apply(IT_IGNORE,0,0,0);return result.failed?UGH_BAD_CALLBACK:UGH_OK;
}
/* ITINERARY_EXPORTS_END */
