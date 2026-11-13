#include "ugh.h"
#include "../passenger_water.h"
#include "actor_projection.h"
typedef struct WaterPlan {
 PassengerStoneSlot slot;ActorType type;ActorRenderHistory render;PassengerWaterWorld world;
 uint16_t frames[4][256];PassengerWaterResult result;size_t consumed;
 int bad,tail_seen,phase_written;ActorPhase published_phase;uint16_t actor_index;
} WaterPlan;
static uint16_t water_word(Regs *r,uint16_t base,uint16_t index) {return rd16(r->ds,(uint16_t)(base+index));}
static uint16_t water_identity(unsigned id) {return (uint16_t)(D(Data_7720)+74u*id);}
static uint16_t water_phase(ActorPhase phase) {
 switch(phase) {
 case ACTOR_RESURFACING:return G(UpdatePassengerResurfacing);case ACTOR_SINKING:return G(UpdatePassengerSinking);
 case ACTOR_FLOATING:return G(UpdatePassengerFloating);case ACTOR_FLOATING_DESTINATION_REQUEST:return G(UpdateFloatingDestinationDisplay);
 case ACTOR_FLOATING_QUESTION:return G(UpdateFloatingQuestionDisplay);case ACTOR_FLOATING_APPROACH:return G(UpdateFloatingPassengerApproach);
 case ACTOR_RETIRED:return G(IgnoreActorState);default:return 0;
 }
}
static uint16_t water_target(PassengerWaterNext next) {
 switch(next) {
 case PW_NEXT_FLOAT:return G(BeginPassengerFloating);case PW_NEXT_SINK:return G(BeginPassengerSinking);
 case PW_NEXT_DESTINATION:return G(BeginPassengerDestinationDisplay);case PW_NEXT_QUESTION:return G(BeginPassengerQuestionDisplay);
 case PW_NEXT_APPROACH:return G(BeginPassengerApproach);case PW_NEXT_BOARD:return G(BoardWaterbornePassenger);default:return 0;
 }
}
static uint16_t water_consume(WaterPlan *plan,Regs *r,uint16_t address,uint16_t expected) {
 if(plan->consumed>=plan->result.count) {plan->bad=1;return 0;}
 PassengerWaterWrite write=plan->result.writes[plan->consumed++];uint16_t base=0,index=r->bx,value=write.value;
 switch(write.field) {
 case PW_PHASE:base=D(ActorUpdateOrScriptCursor);plan->published_phase=(ActorPhase)value;plan->phase_written=1;value=water_phase((ActorPhase)value);break;
 case PW_CURSOR:base=D(ActorAnimationByteOffsets);break;case PW_TICK:base=D(ActorAnimationCountdowns);break;
 case PW_OVERLAY:base=D(ActorOverlayOrScriptCallbacks);break;case PW_VELOCITY:base=D(ActorVerticalOrDemoPeriod);break;
 case PW_Y:base=D(ActorY32);break;case PW_SPRITE:base=D(ActorSpriteIds);break;case PW_X:base=D(ActorX32);break;
 case PW_LIFETIME:
  if(!(actor_phase_aliases(plan->published_phase)&ACTOR_ALIAS_FLOATING_TICKS)) plan->bad=1;
  base=D(ActorMotionWaitOrDemoRepeats);break;
 case PW_REQUEST:
  if(!(actor_phase_aliases(plan->published_phase)&ACTOR_ALIAS_REQUEST_TICKS)) plan->bad=1;
  base=D(ActorPhaseOrDemoLoopCursor);break;
 case PW_OCCUPANT_CLEAR:
  if(write.index>=plan->world.platform_count) plan->bad=1;
  base=D(PlatformActorOccupants);index=(uint16_t)(2u*write.index);break;
 default:plan->bad=1;break;
 }
 if(write.field!=PW_OCCUPANT_CLEAR && write.index) plan->bad=1;
 if((uint16_t)(base+index)!=address || value!=expected) plan->bad=1;
 return value;
}
static void water_write(WaterPlan *plan,Regs *r,uint16_t address,uint16_t expected) {wr16(r->ds,address,water_consume(plan,r,address,expected));}
static int water_projection(WaterPlan *plan,Regs *r) {
#ifdef ACTOR_VERIFY
 PassengerStoneSlot *slot=&plan->slot;uint16_t at=plan->actor_index;
 if(plan->consumed!=plan->result.count || slot->type!=&plan->type || slot->phase!=plan->published_phase ||
    water_word(r,D(ActorDescriptors),at)!=water_identity(slot->type->id)) return 0;
 if(plan->phase_written && water_word(r,D(ActorUpdateOrScriptCursor),at)!=water_phase(slot->phase)) return 0;
 if(slot->source_platform!=water_word(r,D(ActorPlatformOrScriptDone),at) || slot->destination_platform!=water_word(r,D(ActorDestinationPlatforms),at) ||
    slot->position.x32!=water_word(r,D(ActorX32),at) || slot->position.y32!=water_word(r,D(ActorY32),at) ||
    slot->sprite!=water_word(r,D(ActorSpriteIds),at) || slot->overlay_sprite!=water_word(r,D(ActorOverlayOrScriptCallbacks),at) ||
    slot->animation.byte_offset!=water_word(r,D(ActorAnimationByteOffsets),at) || slot->animation.countdown!=water_word(r,D(ActorAnimationCountdowns),at) ||
    slot->vertical_motion!=water_word(r,D(ActorVerticalOrDemoPeriod),at) || slot->quick_delivery_ticks!=water_word(r,D(PassengerQuickDeliveryCountdowns),at)) return 0;
 unsigned aliases=actor_phase_aliases(slot->phase);PassengerStoneSlot observed={0};
 if(!actor_bridge_alias_project(r->ds,at/2u,slot->phase,&observed)) return 0;
 if((aliases&ACTOR_ALIAS_FLOATING_TICKS) && slot->floating_ticks!=observed.floating_ticks) return 0;
 if((aliases&ACTOR_ALIAS_REQUEST_TICKS) && slot->request_ticks!=observed.request_ticks) return 0;
 if(plan->render.pixel_x!=water_word(r,D(ActorPixelX),at) || plan->render.pixel_y!=water_word(r,D(ActorPixelY),at) ||
    plan->world.surface_y!=rd16(r->ds,D(WaterYPixels)) || plan->world.player_count!=rd16(r->ds,D(PlayerCount)) || plan->world.platform_count!=10) return 0;
 for(unsigned i=0;i<2;i++) {
  const WaterCraft *craft=&plan->world.craft[i];uint16_t index=(uint16_t)(2u*i);
  if(craft->pixel_x!=water_word(r,D(PlayerPixelX),index) || craft->pixel_y!=water_word(r,D(PlayerYPixels),index) ||
     craft->vertical_velocity!=water_word(r,D(PlayerVerticalVelocities),index) || craft->carried_kind!=water_word(r,D(PlayerCarriedKinds),index)) return 0;
 }
#else
 (void)plan;(void)r;
#endif
 return 1;
}
static int water_dispatch(Regs *r,WaterPlan *plan,uint16_t target) {
 if(plan->bad || plan->tail_seen || plan->consumed!=plan->result.count || !water_target(plan->result.next) || water_target(plan->result.next)!=target) {plan->bad=1;return UGH_BAD_CALLBACK;}
 if(plan->result.next==PW_NEXT_BOARD || plan->result.next==PW_NEXT_DESTINATION) {
  if(plan->result.selected<0 || (size_t)plan->result.selected>=plan->world.player_count || r->di!=2u*(unsigned)plan->result.selected) {plan->bad=1;return UGH_BAD_CALLBACK;}
  r->di=(uint16_t)(2u*(unsigned)plan->result.selected);
 }
 if(!water_projection(plan,r)) {plan->bad=1;return UGH_BAD_CALLBACK;}
 plan->tail_seen=1;return ugh_dispatch(r->cs,target,r);
}
static int water_complete(const WaterPlan *plan) {return !plan->bad && plan->consumed==plan->result.count && plan->tail_seen==(plan->result.next!=PW_NEXT_NONE);}
static int water_vector(Regs *r,uint16_t pointer,uint16_t words[256],ActorAnimation *animation) {
 size_t count=0;
 while(pointer>=D(Animation_0E20) && pointer<0x1020u && count<256) {
  uint16_t value=rd16(r->ds,pointer);if(value==65535u) {animation->sprites=words;animation->count=count;return count!=0;}
  words[count++]=value;pointer=(uint16_t)(pointer+2u);
 }
 return 0;
}
static int water_prepare(Regs *r,PassengerWaterEntry entry,WaterPlan *plan) {
 if(r->ds!=DATA_SEG || r->cs!=GAME_SEG || (r->bx&1u) || r->bx>=32u) return 0;
 uint16_t descriptor=water_word(r,D(ActorDescriptors),r->bx);unsigned id;
 for(id=1;id<6;id+=2) if(descriptor==water_identity(id)) break;
 if(id>=6) return 0;
 const uint16_t callbacks[]={G(BeginPassengerResurfacing),G(UpdatePassengerResurfacing),G(BeginPassengerSinking),G(UpdatePassengerSinking),
  G(BeginPassengerFloating),G(UpdatePassengerFloating),G(BeginPassengerDestinationDisplay),G(UpdateFloatingDestinationDisplay),
  G(BeginPassengerQuestionDisplay),G(UpdateFloatingQuestionDisplay),G(BeginPassengerApproach),G(UpdateFloatingPassengerApproach),G(BoardWaterbornePassenger)};
 for(unsigned i=0;i<13;i++) if(rd16(r->ds,(uint16_t)(descriptor+8+2u*i))!=callbacks[i]) return 0;
 if(rd16(r->ds,(uint16_t)(descriptor+44))!=G(IgnoreActorState) || rd16(r->ds,(uint16_t)(descriptor+72))!=water_identity(id^1u)) return 0;
 *plan=(WaterPlan){0};plan->actor_index=r->bx;
 ActorPhase phase=entry==PW_RESURFACE?ACTOR_RESURFACING:entry==PW_SINK?ACTOR_SINKING:entry==PW_FLOAT?ACTOR_FLOATING:
  entry==PW_DESTINATION?ACTOR_FLOATING_DESTINATION_REQUEST:entry==PW_QUESTION?ACTOR_FLOATING_QUESTION:entry==PW_APPROACH?ACTOR_FLOATING_APPROACH:ACTOR_READ_JOURNEY;
 if(!actor_bridge_alias_project(r->ds,r->bx/2u,phase,&plan->slot)) return 0;
 plan->published_phase=phase;plan->type.id=(ActorTypeId)id;plan->slot.type=&plan->type;
 plan->type.geometry=(ObjectGeometry){rd16(r->ds,descriptor),rd16(r->ds,(uint16_t)(descriptor+2)),rd16(r->ds,(uint16_t)(descriptor+4)),rd16(r->ds,(uint16_t)(descriptor+6))};
 plan->type.animation_period=rd16(r->ds,(uint16_t)(descriptor+62));plan->type.floating_lifetime=rd16(r->ds,(uint16_t)(descriptor+68));
 plan->slot.source_platform=water_word(r,D(ActorPlatformOrScriptDone),r->bx);plan->slot.destination_platform=water_word(r,D(ActorDestinationPlatforms),r->bx);
 if((entry==PW_BEGIN_RESURFACE || entry==PW_APPROACH) && (plan->slot.source_platform>=10 || water_word(r,D(ActorSourcePlatformByteIndices),r->bx)!=2u*plan->slot.source_platform)) return 0;
 if(entry==PW_APPROACH && (plan->slot.destination_platform>=10 || water_word(r,D(ActorDestinationPlatformByteIndices),r->bx)!=2u*plan->slot.destination_platform)) return 0;
 plan->slot.position=(ObjectPosition){water_word(r,D(ActorX32),r->bx),water_word(r,D(ActorY32),r->bx)};
 plan->slot.sprite=water_word(r,D(ActorSpriteIds),r->bx);plan->slot.overlay_sprite=water_word(r,D(ActorOverlayOrScriptCallbacks),r->bx);
 plan->slot.animation=(ActorAnimationState){water_word(r,D(ActorAnimationByteOffsets),r->bx),water_word(r,D(ActorAnimationCountdowns),r->bx)};
 plan->slot.vertical_motion=water_word(r,D(ActorVerticalOrDemoPeriod),r->bx);plan->slot.quick_delivery_ticks=water_word(r,D(PassengerQuickDeliveryCountdowns),r->bx);
 plan->render.pixel_x=water_word(r,D(ActorPixelX),r->bx);plan->render.pixel_y=water_word(r,D(ActorPixelY),r->bx);
 plan->world.player_count=rd16(r->ds,D(PlayerCount));if(plan->world.player_count!=1 && plan->world.player_count!=2) return 0;
 plan->world.surface_y=rd16(r->ds,D(WaterYPixels));plan->world.platform_count=10;
 for(unsigned i=0;i<2;i++) {
  uint16_t index=(uint16_t)(2u*i);plan->world.craft[i]=(WaterCraft){water_word(r,D(PlayerPixelX),index),water_word(r,D(PlayerYPixels),index),water_word(r,D(PlayerVerticalVelocities),index),water_word(r,D(PlayerCarriedKinds),index)};
 }
 if(entry==PW_RESURFACE || entry==PW_SINK || entry==PW_FLOAT || entry==PW_DESTINATION || entry==PW_QUESTION || entry==PW_APPROACH)
  for(unsigned i=0;i<4;i++) if(!water_vector(r,rd16(r->ds,(uint16_t)(descriptor+46+2u*i)),plan->frames[i],&plan->type.animations[i])) return 0;
 plan->result=passenger_water_apply(entry,&plan->slot,&plan->render,&plan->world);return !plan->result.failed;
}
/* WATER_SHELLS_BEGIN */
#define READ(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define WRITE(n,i,v) water_write(plan,r,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define A(n) READ(n,r->bx)
#define W(n,v) WRITE(n,r->bx,v)
#define DESC(n) rd16(r->ds,(uint16_t)(r->si+(n)))
static int water_shell_state_jump(Regs *r,WaterPlan *plan,uint16_t target);
static int water_shell_tail(Regs *r,WaterPlan *plan,unsigned field);

static uint16_t water_shell_shl(Regs *r,uint16_t v,unsigned n) {
    for(unsigned i=0;i<n;i++) { flag(r,CF,v&0x8000u); v=(uint16_t)(v<<1); }
    szp(r,v,16); if(n==1) flag(r,OF,!!(v&0x8000u)^!!(r->flags&CF));
    return v;
}

static uint16_t water_shell_sar(Regs *r,uint16_t v,unsigned n) {
    for(unsigned i=0;i<n;i++) { flag(r,CF,v&1); v=(uint16_t)((v>>1)|(v&0x8000u)); }
    szp(r,v,16); if(n==1) flag(r,OF,0); return v;
}

static uint16_t water_shell_inc(Regs *r,uint16_t v) {
    uint16_t cf=r->flags&CF; v=add16(r,v,1,0); flag(r,CF,cf); return v;
}

static int water_shell_less(const Regs *r) { return !!(r->flags&SF)!=!!(r->flags&OF); }

static int water_shell_greater(const Regs *r) { return !(r->flags&ZF) && !water_shell_less(r); }

static void water_shell_actor_init(Regs *r,WaterPlan *plan,unsigned field) {
    r->si=A(ActorDescriptors); r->ax=DESC(field);
    W(ActorUpdateOrScriptCursor,r->ax);
    W(ActorAnimationByteOffsets,0xfffe); W(ActorAnimationCountdowns,1);
}

static int water_shell_actor_frame(Regs *r,WaterPlan *plan,unsigned field) {
    for(unsigned budget=0;budget<32768;budget++) {
        r->di=DESC(field);
        r->di=add16(r,r->di,A(ActorAnimationByteOffsets),0);
        r->ax=rd16(r->ds,r->di); sub16(r,r->ax,0xffff,0);
        if(r->ax!=0xffff) { W(ActorSpriteIds,r->ax); return UGH_OK; }
        W(ActorAnimationByteOffsets,0);
    }
    return UGH_BUDGET;
}

static int water_shell_actor_tick(Regs *r,WaterPlan *plan) {
    uint16_t count=dec16(r,A(ActorAnimationCountdowns));
    W(ActorAnimationCountdowns,count);
    if(count) return 0;
    r->ax=DESC(0x3e); W(ActorAnimationCountdowns,r->ax);
    W(ActorAnimationByteOffsets,add16(r,A(ActorAnimationByteOffsets),2,0));
    return 1;
}

static void water_shell_surface_y(Regs *r,WaterPlan *plan) {
    r->ax=READ(WaterYPixels,0); sub16(r,r->ax,A(ActorPixelY),0);
    if(!(r->flags&ZF)) { r->ax=sub16(r,r->ax,DESC(2),0); r->ax=water_shell_shl(r,r->ax,5); W(ActorY32,r->ax); }
}

static int water_shell_state_jump(Regs *r,WaterPlan *plan,uint16_t target) { return water_dispatch(r,plan,target); }

static int water_shell_tail(Regs *r,WaterPlan *plan, unsigned field) { return water_shell_state_jump(r,plan,DESC(field)); }

static int shell_BeginPassengerResurfacing(Regs *r,WaterPlan *plan) {
    r->si=A(ActorDescriptors); r->ax=DESC(0x0a); W(ActorUpdateOrScriptCursor,r->ax);
    r->di=A(ActorSourcePlatformByteIndices); r->ax=0xffff;
    WRITE(PlatformActorOccupants,r->di,r->ax); W(ActorOverlayOrScriptCallbacks,r->ax);
    W(ActorAnimationByteOffsets,0xfffe); W(ActorAnimationCountdowns,1); W(ActorVerticalOrDemoPeriod,0); return UGH_OK;
}

static int shell_UpdatePassengerResurfacing(Regs *r,WaterPlan *plan) {
    r->si=A(ActorDescriptors); water_shell_actor_tick(r,plan);
    int status=water_shell_actor_frame(r,plan,0x2e); if(status) return status;
    r->cx=sub16(r,A(ActorPixelY),DESC(2),0); r->cx=sub16(r,r->cx,READ(WaterYPixels,0),0);
    if(!(r->flags&(SF|ZF))) r->cx=(uint16_t)((r->cx&255u)|0x100u);
    r->ax=A(ActorVerticalOrDemoPeriod); logic(r,r->cx>>8,8);
    if(r->flags&SF) r->ax=add16(r,r->ax,0x27,0);
    else { sub16(r,r->ax,0,0); r->ax=sub16(r,r->ax,water_shell_greater(r)?0x175:0x5c,0); }
    logic(r,r->ax,16);
    if(r->flags&SF) { sub16(r,r->ax,0xe800,0); if(water_shell_less(r)) r->ax=0xe800; }
    else { sub16(r,r->ax,0x1800,0); if(water_shell_greater(r)) r->ax=0x1800; }
    W(ActorVerticalOrDemoPeriod,r->ax); r->ax=water_shell_sar(r,r->ax,6); r->ax=add16(r,r->ax,A(ActorY32),0); W(ActorY32,r->ax);
    sub16(r,A(ActorVerticalOrDemoPeriod),0,0); if(!water_shell_less(r)) return UGH_OK;
    r->ax=water_shell_sar(r,r->ax,5); r->ax=sub16(r,r->ax,DESC(2),0);
    sub16(r,r->ax,READ(WaterYPixels,0),0); if(water_shell_greater(r)) return UGH_OK;
    r->ax=sub16(r,READ(WaterYPixels,0),DESC(2),0); r->ax=water_shell_shl(r,r->ax,5);
    W(ActorY32,r->ax); return water_shell_tail(r,plan,0x10);
}

static int shell_BeginPassengerSinking(Regs *r,WaterPlan *plan) {
    water_shell_actor_init(r,plan,0x0e); W(ActorOverlayOrScriptCallbacks,0xffff); W(ActorVerticalOrDemoPeriod,0); return UGH_OK;
}

static int shell_UpdatePassengerSinking(Regs *r,WaterPlan *plan) {
    r->si=A(ActorDescriptors); water_shell_actor_tick(r,plan); int status=water_shell_actor_frame(r,plan,0x2e); if(status) return status;
    r->ax=add16(r,A(ActorVerticalOrDemoPeriod),0x27,0); W(ActorVerticalOrDemoPeriod,r->ax);
    r->ax=water_shell_sar(r,r->ax,6); r->ax=add16(r,r->ax,A(ActorY32),0); sub16(r,r->ax,0x1800,0);
    if(r->flags&CF) W(ActorY32,r->ax);
    else { r->ax=DESC(0x2c); W(ActorUpdateOrScriptCursor,r->ax); W(ActorSpriteIds,0xffff); }
    return UGH_OK;
}

static int shell_BeginPassengerFloating(Regs *r,WaterPlan *plan) {
    water_shell_actor_init(r,plan,0x12); r->ax=DESC(0x44); W(ActorMotionWaitOrDemoRepeats,r->ax); return UGH_OK;
}

static int shell_UpdatePassengerFloating(Regs *r,WaterPlan *plan) {
    r->si=A(ActorDescriptors); water_shell_actor_tick(r,plan); int status=water_shell_actor_frame(r,plan,0x30); if(status) return status;
    water_shell_surface_y(r,plan); sub16(r,r->si,D(Data_77FE),0);
    if(!(r->flags&ZF)) {
        r->di=logic(r,0,16);
        for(;;) {
            sub16(r,READ(PlayerVerticalVelocities,r->di),0,0);
            if(!(r->flags&ZF)) goto next;
            sub16(r,READ(PlayerCarriedKinds,r->di),0,0); if(!(r->flags&ZF)) goto next;
            r->cx=sub16(r,READ(PlayerYPixels,r->di),READ(WaterYPixels,0),0);
            r->cx=add16(r,r->cx,18,0); if(r->flags&ZF) return water_shell_tail(r,plan,0x14);
next:       r->di=add16(r,r->di,2,0); sub16(r,r->di,4,0); if(!(r->flags&CF)) break;
            sub16(r,READ(PlayerCount,0),2,0); if(!(r->flags&ZF)) break;
        }
    }
    uint16_t count=dec16(r,A(ActorMotionWaitOrDemoRepeats)); W(ActorMotionWaitOrDemoRepeats,count);
    return count?UGH_OK:water_shell_tail(r,plan,0x0c);
}

static int shell_UpdateFloatingDestinationDisplay(Regs *r,WaterPlan *plan) {
    r->si=A(ActorDescriptors); water_shell_surface_y(r,plan);
    r->cx=sub16(r,READ(PlayerYPixels,0),READ(WaterYPixels,0),0); r->cx=add16(r,r->cx,18,0);
    if(!(r->flags&ZF)) {
        sub16(r,READ(PlayerCount,0),2,0); if(!(r->flags&ZF)) return water_shell_tail(r,plan,0x18);
        r->cx=sub16(r,READ(SecondPlayerYPixels,0),READ(WaterYPixels,0),0); r->cx=add16(r,r->cx,18,0);
        if(!(r->flags&ZF)) return water_shell_tail(r,plan,0x18);
    }
    if(water_shell_actor_tick(r,plan)) { int status=water_shell_actor_frame(r,plan,0x30); if(status) return status; }
    uint16_t count=dec16(r,A(ActorPhaseOrDemoLoopCursor)); W(ActorPhaseOrDemoLoopCursor,count); return count?UGH_OK:water_shell_tail(r,plan,0x1c);
}

static int shell_UpdateFloatingQuestionDisplay(Regs *r,WaterPlan *plan) {
    r->si=A(ActorDescriptors); water_shell_surface_y(r,plan);
    if(water_shell_actor_tick(r,plan)) { int status=water_shell_actor_frame(r,plan,0x30); if(status) return status; }
    uint16_t count=dec16(r,A(ActorPhaseOrDemoLoopCursor)); W(ActorPhaseOrDemoLoopCursor,count); return count?UGH_OK:water_shell_tail(r,plan,0x0c);
}

static int shell_UpdateFloatingPassengerApproach(Regs *r,WaterPlan *plan) {
    r->si=A(ActorDescriptors); water_shell_surface_y(r,plan); r->di=logic(r,0,16);
    for(;;) {
        sub16(r,READ(PlayerCarriedKinds,r->di),0,0);
        if(r->flags&ZF) {
            r->cx=sub16(r,READ(PlayerYPixels,r->di),READ(WaterYPixels,0),0); r->cx=add16(r,r->cx,18,0);
            if(r->flags&ZF) break;
        }
        r->di=add16(r,r->di,2,0); sub16(r,r->di,4,0); if(!(r->flags&CF)) return water_shell_tail(r,plan,0x18);
        sub16(r,READ(PlayerCount,0),2,0); if(!(r->flags&ZF)) return water_shell_tail(r,plan,0x18);
    }
    r->cx=logic(r,0,16); if(water_shell_actor_tick(r,plan)) r->cx=water_shell_inc(r,r->cx);
    r->ax=add16(r,A(ActorPixelX),DESC(0),0); r->ax=sub16(r,r->ax,16,0);
    sub16(r,r->ax,READ(PlayerPixelX,r->di),0);
    if(r->flags&ZF) return water_shell_tail(r,plan,0x20);
    int left=water_shell_greater(r), status=water_shell_actor_frame(r,plan,left?0x32:0x34); if(status) return status;
    logic(r,r->cx,16);
    if(r->cx) W(ActorX32,left?sub16(r,A(ActorX32),32,0):add16(r,A(ActorX32),32,0));
    return UGH_OK;
}

#undef READ
#undef WRITE
#undef A
#undef W
#undef DESC
/* WATER_SHELLS_END */
/* WATER_EXPORTS_BEGIN */
int l1_BeginPassengerResurfacing(Regs *r);
int l1_UpdatePassengerResurfacing(Regs *r);
int l1_BeginPassengerSinking(Regs *r);
int l1_UpdatePassengerSinking(Regs *r);
int l1_BeginPassengerFloating(Regs *r);
int l1_UpdatePassengerFloating(Regs *r);
int l1_UpdateFloatingDestinationDisplay(Regs *r);
int l1_UpdateFloatingQuestionDisplay(Regs *r);
int l1_UpdateFloatingPassengerApproach(Regs *r);
EXPORT int c_BeginPassengerResurfacing(Regs *r) {
 WaterPlan plan;if(!water_prepare(r,PW_BEGIN_RESURFACE,&plan)) return l1_BeginPassengerResurfacing(r);
 int status=shell_BeginPassengerResurfacing(r,&plan);
 if(plan.bad || (!status && !water_complete(&plan))) return UGH_BAD_CALLBACK;
 if(!status && !plan.tail_seen && !water_projection(&plan,r)) return UGH_BAD_CALLBACK;
 return status;
}
EXPORT int c_UpdatePassengerResurfacing(Regs *r) {
 WaterPlan plan;if(!water_prepare(r,PW_RESURFACE,&plan)) return l1_UpdatePassengerResurfacing(r);
 int status=shell_UpdatePassengerResurfacing(r,&plan);
 if(plan.bad || (!status && !water_complete(&plan))) return UGH_BAD_CALLBACK;
 if(!status && !plan.tail_seen && !water_projection(&plan,r)) return UGH_BAD_CALLBACK;
 return status;
}
EXPORT int c_BeginPassengerSinking(Regs *r) {
 WaterPlan plan;if(!water_prepare(r,PW_BEGIN_SINK,&plan)) return l1_BeginPassengerSinking(r);
 int status=shell_BeginPassengerSinking(r,&plan);
 if(plan.bad || (!status && !water_complete(&plan))) return UGH_BAD_CALLBACK;
 if(!status && !plan.tail_seen && !water_projection(&plan,r)) return UGH_BAD_CALLBACK;
 return status;
}
EXPORT int c_UpdatePassengerSinking(Regs *r) {
 WaterPlan plan;if(!water_prepare(r,PW_SINK,&plan)) return l1_UpdatePassengerSinking(r);
 int status=shell_UpdatePassengerSinking(r,&plan);
 if(plan.bad || (!status && !water_complete(&plan))) return UGH_BAD_CALLBACK;
 if(!status && !plan.tail_seen && !water_projection(&plan,r)) return UGH_BAD_CALLBACK;
 return status;
}
EXPORT int c_BeginPassengerFloating(Regs *r) {
 WaterPlan plan;if(!water_prepare(r,PW_BEGIN_FLOAT,&plan)) return l1_BeginPassengerFloating(r);
 int status=shell_BeginPassengerFloating(r,&plan);
 if(plan.bad || (!status && !water_complete(&plan))) return UGH_BAD_CALLBACK;
 if(!status && !plan.tail_seen && !water_projection(&plan,r)) return UGH_BAD_CALLBACK;
 return status;
}
EXPORT int c_UpdatePassengerFloating(Regs *r) {
 WaterPlan plan;if(!water_prepare(r,PW_FLOAT,&plan)) return l1_UpdatePassengerFloating(r);
 int status=shell_UpdatePassengerFloating(r,&plan);
 if(plan.bad || (!status && !water_complete(&plan))) return UGH_BAD_CALLBACK;
 if(!status && !plan.tail_seen && !water_projection(&plan,r)) return UGH_BAD_CALLBACK;
 return status;
}
EXPORT int c_UpdateFloatingDestinationDisplay(Regs *r) {
 WaterPlan plan;if(!water_prepare(r,PW_DESTINATION,&plan)) return l1_UpdateFloatingDestinationDisplay(r);
 int status=shell_UpdateFloatingDestinationDisplay(r,&plan);
 if(plan.bad || (!status && !water_complete(&plan))) return UGH_BAD_CALLBACK;
 if(!status && !plan.tail_seen && !water_projection(&plan,r)) return UGH_BAD_CALLBACK;
 return status;
}
EXPORT int c_UpdateFloatingQuestionDisplay(Regs *r) {
 WaterPlan plan;if(!water_prepare(r,PW_QUESTION,&plan)) return l1_UpdateFloatingQuestionDisplay(r);
 int status=shell_UpdateFloatingQuestionDisplay(r,&plan);
 if(plan.bad || (!status && !water_complete(&plan))) return UGH_BAD_CALLBACK;
 if(!status && !plan.tail_seen && !water_projection(&plan,r)) return UGH_BAD_CALLBACK;
 return status;
}
EXPORT int c_UpdateFloatingPassengerApproach(Regs *r) {
 WaterPlan plan;if(!water_prepare(r,PW_APPROACH,&plan)) return l1_UpdateFloatingPassengerApproach(r);
 int status=shell_UpdateFloatingPassengerApproach(r,&plan);
 if(plan.bad || (!status && !water_complete(&plan))) return UGH_BAD_CALLBACK;
 if(!status && !plan.tail_seen && !water_projection(&plan,r)) return UGH_BAD_CALLBACK;
 return status;
}
EXPORT int c_IgnoreWaterbornePassengerState(Regs *r) {(void)r;PassengerWaterResult result=passenger_water_apply(PW_IGNORE,0,0,0);return result.failed?UGH_BAD_CALLBACK:UGH_OK;}
/* WATER_EXPORTS_END */
