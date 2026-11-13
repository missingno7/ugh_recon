#include "ugh.h"
#include "../passenger_delivery.h"
#include "actor_projection.h"
typedef struct DeliveryPlan {
    PassengerStoneSlot slot;ActorType types[2];ActorRenderHistory render;
    PassengerDeliveryWorld world;LevelPlatform platforms[10];uint16_t frames[4][256];
    PassengerDeliveryResult result;size_t consumed;int bad,spawn_seen,sound_seen;
} DeliveryPlan;
static uint16_t delivery_word(Regs *r,uint16_t base,uint16_t index) {return rd16(r->ds,(uint16_t)(base+index));}
static uint16_t delivery_identity(unsigned id) {return id<6?(uint16_t)(D(Data_7720)+74u*id):0;}
static int delivery_id(uint16_t identity) {
    for(unsigned i=0;i<6;i++) if(identity==delivery_identity(i)) return (int)i;
    return -1;
}
static uint16_t delivery_phase(uint16_t phase) {
    switch(phase) {
    case ACTOR_PLATFORM_WAIT:return G(UpdatePassengerPlatformWait);
    case ACTOR_DESTINATION_REQUEST:return G(UpdatePassengerDestinationDisplay);
    case ACTOR_QUESTION:return G(UpdatePassengerQuestionDisplay);
    case ACTOR_APPROACH:return G(UpdatePassengerApproach);
    case ACTOR_CARRIED_PASSENGER:return G(UpdateCarriedPassenger);
    case ACTOR_WALK_TO_EXIT:return G(WalkPassengerToExit);
    case ACTOR_FLOATING_DESTINATION_REQUEST:return G(UpdateFloatingDestinationDisplay);
    case ACTOR_FLOATING_QUESTION:return G(UpdateFloatingQuestionDisplay);
    case ACTOR_FLOATING_APPROACH:return G(UpdateFloatingPassengerApproach);
    default:return 0;
    }
}
static uint16_t delivery_consume(DeliveryPlan *plan,Regs *r,uint16_t address,uint16_t expected,int byte) {
    if(plan->consumed>=plan->result.count) {plan->bad=1;return 0;}
    PassengerDeliveryWrite write=plan->result.writes[plan->consumed++];uint16_t base=0,index=r->bx,value=write.value;int width=0;
    switch(write.field) {
    case PD_PHASE:base=D(ActorUpdateOrScriptCursor);value=delivery_phase(value);break;
    case PD_TYPE:base=D(ActorDescriptors);value=delivery_identity(value);break;
    case PD_CURSOR:base=D(ActorAnimationByteOffsets);break;case PD_TICK:base=D(ActorAnimationCountdowns);break;
    case PD_POSE:case PD_REQUEST:base=D(ActorPhaseOrDemoLoopCursor);break;
    case PD_CARRIER:base=D(ActorPhaseOrDemoLoopCursor);value=(uint16_t)(value*2u);break;
    case PD_SPRITE:base=D(ActorSpriteIds);break;case PD_OVERLAY:base=D(ActorOverlayOrScriptCallbacks);break;
    case PD_X:base=D(ActorX32);break;case PD_Y:base=D(ActorY32);break;
    case PD_QUICK:base=D(PassengerQuickDeliveryCountdowns);break;
    case PD_OCCUPANT_CLEAR:base=D(PlatformActorOccupants);index=(uint16_t)(write.index*2u);break;
    case PD_FARE:base=D(PlayerPassengerFares);index=(uint16_t)(write.index*2u);break;
    case PD_FLOOR:base=D(PlayerMinimumFares);index=(uint16_t)(write.index*2u);break;
    case PD_KIND:base=D(PlayerCarriedKinds);index=(uint16_t)(write.index*2u);break;
    case PD_ICON:base=D(PlayerDestinationIcons);index=(uint16_t)(write.index*2u);break;
    case PD_SCORE_LOW:base=D(ScoreLowWord);index=0;break;
    case PD_SCORE_HIGH:base=D(ScoreHighWord);index=0;break;
    case PD_HUD_CLEAR:base=D(HudFareClearPending);index=0;width=1;break;
    }
    if(write.field!=PD_OCCUPANT_CLEAR && write.field!=PD_FARE && write.field!=PD_FLOOR && write.field!=PD_KIND && write.field!=PD_ICON && write.index) plan->bad=1;
    if((uint16_t)(base+index)!=address || value!=expected || byte!=width) plan->bad=1;
    return value;
}
static void delivery_write16(DeliveryPlan *plan,Regs *r,uint16_t address,uint16_t expected) {
    uint16_t value=delivery_consume(plan,r,address,expected,0);wr16(r->ds,address,value);
}
static void delivery_write8(DeliveryPlan *plan,Regs *r,uint16_t address,uint8_t expected) {
    uint16_t value=delivery_consume(plan,r,address,expected,1);wr8(r->ds,address,(uint8_t)value);
}
static int delivery_dispatch(Regs *r,DeliveryPlan *plan,uint16_t target) {
    uint16_t expected=0;
    switch(plan->result.next) {
    case PD_NEXT_WAIT:expected=G(BeginPassengerPlatformWait);break;
    case PD_NEXT_DESTINATION:expected=G(BeginPassengerDestinationDisplay);break;
    case PD_NEXT_QUESTION:expected=G(BeginPassengerQuestionDisplay);break;
    case PD_NEXT_APPROACH:expected=G(BeginPassengerApproach);break;
    case PD_NEXT_BOARD:expected=G(BoardPassenger);break;
    case PD_NEXT_DELIVER:expected=G(DeliverPassenger);break;
    case PD_NEXT_WATER:expected=G(BeginPassengerResurfacing);break;
    default:plan->bad=1;break;
    }
    if(plan->bad || plan->consumed!=plan->result.count || expected!=target) {plan->bad=1;return UGH_BAD_CALLBACK;}
    return ugh_dispatch(r->cs,target,r);
}
static int delivery_near(Regs *r,DeliveryPlan *plan,uint16_t target,uint16_t return_ip) {
    if(target==G(SpawnFallingItem)) {
        if(!plan->result.spawn_bonus || plan->spawn_seen || r->si!=D(FallingDescriptor_7A38) ||
            r->ax!=plan->result.launch.x32 || r->bp!=plan->result.launch.y32 || r->cx || r->dx) {plan->bad=1;return UGH_BAD_CALLBACK;}
        plan->spawn_seen=1;
        /* Real item bridge calls items_spawn and retains its full-pool transfer.
         * On that outcome no post-allocation passenger stores are consumed. */
    } else if(target!=G(FindPlayerTouchingActor)) {plan->bad=1;return UGH_BAD_CALLBACK;}
    return ugh_call_near(target,return_ip,r);
}
static int delivery_sound(Regs *r,DeliveryPlan *plan,uint16_t segment,uint16_t target) {
    if(!plan->result.bonus_sound || !plan->spawn_seen || plan->sound_seen || segment!=UGH_S_C_PlayAdlibEffect || target!=UGH_O_C_PlayAdlibEffect) {plan->bad=1;return UGH_BAD_CALLBACK;}
    plan->sound_seen=1;int status=ugh_dispatch(segment,target,r);
    if(!status) {
        PassengerDeliveryResult finish=passenger_delivery_finish(&plan->slot,&plan->world);
        if(!plan->result.finish_pending || finish.failed || plan->result.count+finish.count>32) {plan->bad=1;return UGH_BAD_CALLBACK;}
        for(size_t i=0;i<finish.count;i++) plan->result.writes[plan->result.count++]=finish.writes[i];
        plan->result.finish_pending=0;
    }
    return status;
}
static int delivery_vector(Regs *r,uint16_t pointer,uint16_t *words,ActorAnimation *animation) {
    size_t count=0;
    while(pointer>=D(Animation_0E20) && pointer<0x1020u && count<256) {
        uint16_t value=rd16(r->ds,pointer);if(value==65535u) {animation->sprites=words;animation->count=count;return count!=0;}
        words[count++]=value;pointer=(uint16_t)(pointer+2u);
    }
    return 0;
}
static int delivery_prepare(Regs *r,PassengerDeliveryEntry entry,DeliveryPlan *plan) {
    if(r->ds!=DATA_SEG || r->cs!=GAME_SEG || (r->bx&1u) || r->bx>=32u) return 0;
    uint16_t descriptor=delivery_word(r,D(ActorDescriptors),r->bx);int id=delivery_id(descriptor);if(id<0) return 0;
    int shared=entry==PD_BEGIN_DESTINATION || entry==PD_BEGIN_QUESTION || entry==PD_BEGIN_APPROACH;
    if(entry==PD_RESCUE ? !(id&1) : (!shared && (id&1))) return 0;
    if((entry==PD_BOARD || entry==PD_RESCUE || entry==PD_DELIVER) && (r->di>2u || (r->di&1u) || (r->di==2u && rd16(r->ds,D(PlayerCount))!=2))) return 0;
    *plan=(DeliveryPlan){0};
    for(unsigned i=0;i<2;i++) {
        unsigned selected=(unsigned)id^i;uint16_t base=delivery_identity(selected);ActorType *type=&plan->types[i];
        if(rd16(r->ds,(uint16_t)(base+72))!=delivery_identity(selected^1u)) return 0;
        type->id=(ActorTypeId)selected;type->paired_type=&plan->types[1-i];
        type->geometry=(ObjectGeometry){rd16(r->ds,base),rd16(r->ds,(uint16_t)(base+2)),rd16(r->ds,(uint16_t)(base+4)),rd16(r->ds,(uint16_t)(base+6))};
        type->animation_period=rd16(r->ds,(uint16_t)(base+62));type->initial_fare=rd16(r->ds,(uint16_t)(base+64));
        type->minimum_fare=rd16(r->ds,(uint16_t)(base+66));type->carried_kind=rd16(r->ds,(uint16_t)(base+70));
        if(selected&1u) {
            if(rd16(r->ds,(uint16_t)(base+8))!=G(BeginPassengerResurfacing) || rd16(r->ds,(uint16_t)(base+22))!=G(UpdateFloatingDestinationDisplay) ||
               rd16(r->ds,(uint16_t)(base+26))!=G(UpdateFloatingQuestionDisplay) || rd16(r->ds,(uint16_t)(base+30))!=G(UpdateFloatingPassengerApproach)) return 0;
        } else {
            const uint16_t targets[]={G(BeginPassengerPlatformWait),G(UpdatePassengerPlatformWait),G(BeginPassengerDestinationDisplay),G(UpdatePassengerDestinationDisplay),
                G(BeginPassengerQuestionDisplay),G(UpdatePassengerQuestionDisplay),G(BeginPassengerApproach),G(UpdatePassengerApproach),G(BoardPassenger),G(UpdateCarriedPassenger),G(DeliverPassenger),G(WalkPassengerToExit)};
            for(unsigned j=0;j<12;j++) if(rd16(r->ds,(uint16_t)(base+16+2*j))!=targets[j]) return 0;
        }
    }
    plan->slot.type=&plan->types[0];
    ActorPhase phase=entry==PD_WAIT?ACTOR_PLATFORM_WAIT:entry==PD_DESTINATION?ACTOR_DESTINATION_REQUEST:entry==PD_QUESTION?ACTOR_QUESTION:
        entry==PD_APPROACH?ACTOR_APPROACH:entry==PD_CARRIED || entry==PD_DELIVER?ACTOR_CARRIED_PASSENGER:ACTOR_READ_JOURNEY;
    if(!actor_bridge_alias_project(r->ds,r->bx/2u,phase,&plan->slot)) return 0;
    plan->slot.source_platform=delivery_word(r,D(ActorPlatformOrScriptDone),r->bx);plan->slot.destination_platform=delivery_word(r,D(ActorDestinationPlatforms),r->bx);
    int source=entry==PD_WAIT || entry==PD_DESTINATION || entry==PD_QUESTION || entry==PD_APPROACH || entry==PD_BOARD || entry==PD_RESCUE;
    /* Approach can board immediately, including between animation ticks. */
    int destination=entry==PD_APPROACH || entry==PD_BOARD || entry==PD_RESCUE || entry==PD_CARRIED || entry==PD_DELIVER;
    if(source && (plan->slot.source_platform>=10 || delivery_word(r,D(ActorSourcePlatformByteIndices),r->bx)!=2u*plan->slot.source_platform)) return 0;
    if(destination && (plan->slot.destination_platform>=10 || delivery_word(r,D(ActorDestinationPlatformByteIndices),r->bx)!=2u*plan->slot.destination_platform)) return 0;
    plan->slot.position=(ObjectPosition){delivery_word(r,D(ActorX32),r->bx),delivery_word(r,D(ActorY32),r->bx)};
    plan->slot.sprite=delivery_word(r,D(ActorSpriteIds),r->bx);plan->slot.overlay_sprite=delivery_word(r,D(ActorOverlayOrScriptCallbacks),r->bx);
    plan->slot.animation=(ActorAnimationState){delivery_word(r,D(ActorAnimationByteOffsets),r->bx),delivery_word(r,D(ActorAnimationCountdowns),r->bx)};
    plan->slot.quick_delivery_ticks=delivery_word(r,D(PassengerQuickDeliveryCountdowns),r->bx);
    plan->render.pixel_x=delivery_word(r,D(ActorPixelX),r->bx);plan->render.pixel_y=delivery_word(r,D(ActorPixelY),r->bx);
    plan->world.player_count=rd16(r->ds,D(PlayerCount));uint16_t bytes=rd16(r->ds,D(PlayerArrayBytes));
    if((plan->world.player_count!=1 && plan->world.player_count!=2) || bytes!=2u*plan->world.player_count) return 0;
    plan->world.player_slots=bytes/2u;
    plan->world.platform_count=10;plan->world.platforms=plan->platforms;plan->world.water_pixel_y=rd16(r->ds,D(WaterYPixels));
    plan->world.multiplier=rd16(r->ds,D(ScoreMultiplier));uint16_t difficulty=rd16(r->ds,D(SelectedDifficulty));
    if(entry==PD_DELIVER && difficulty>2) return 0;
    if(entry==PD_DELIVER) plan->world.multiplier_limit=delivery_word(r,D(MultiplierLimitsByDifficulty),(uint16_t)(2u*difficulty));
    plan->world.score=(uint32_t)rd16(r->ds,D(ScoreLowWord))|((uint32_t)rd16(r->ds,D(ScoreHighWord))<<16);
    plan->world.hud_clear=rd8(r->ds,D(HudFareClearPending));
    for(unsigned i=0;i<2;i++) {
        uint16_t index=(uint16_t)(2u*i);PassengerCraft *craft=&plan->world.craft[i];
        craft->position=(ObjectPosition){delivery_word(r,D(PlayerX32),index),delivery_word(r,D(PlayerY32),index)};
        craft->pixel_x=delivery_word(r,D(PlayerPixelX),index);craft->platform=delivery_word(r,D(PlayerPlatformIndices),index);
        craft->fare=delivery_word(r,D(PlayerPassengerFares),index);craft->minimum_fare=delivery_word(r,D(PlayerMinimumFares),index);
        craft->carried_kind=delivery_word(r,D(PlayerCarriedKinds),index);craft->destination_icon=delivery_word(r,D(PlayerDestinationIcons),index);
    }
    for(unsigned i=0;i<10;i++) {
        plan->platforms[i].waiting_x=delivery_word(r,D(PlatformWaitingPointsX),(uint16_t)(2u*i));
        plan->platforms[i].surface_y=delivery_word(r,D(PlatformHeights),(uint16_t)(2u*i));
        plan->platforms[i].destination_icon=delivery_word(r,D(PlatformDestinationIcons),(uint16_t)(2u*i));
    }
    int frames=entry==PD_WAIT || entry==PD_DESTINATION || entry==PD_QUESTION || entry==PD_APPROACH;
    if(frames) {
        const unsigned offsets[]={46,48,50,52};
        for(unsigned i=0;i<4;i++) if(!delivery_vector(r,rd16(r->ds,(uint16_t)(descriptor+offsets[i])),plan->frames[i],&plan->types[0].animations[i])) return 0;
    }
    size_t incoming=entry==PD_BOARD || entry==PD_RESCUE || entry==PD_DELIVER?r->di/2u:0;
    plan->result=passenger_delivery_apply(entry,&plan->slot,&plan->render,&plan->world,incoming);return !plan->result.failed;
}
/* DELIVERY_SHELLS_BEGIN */
/* Actual L1 expressions reconstruct the machine shell; native outputs supply every owned persistent store. */
#define READ(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define WRITE(n,i,v) delivery_write16(plan,r,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define A(n) READ(n,r->bx)
#define W(n,v) WRITE(n,r->bx,v)
#define DESC(n) rd16(r->ds,(uint16_t)(r->si+(n)))
static int pd_shell0_state_jump(Regs *r,DeliveryPlan *plan,uint16_t target);
static int pd_shell0_tail(Regs *r,DeliveryPlan *plan,unsigned field);
static int pd_shell0_less(const Regs *r) { return !!(r->flags&SF)!=!!(r->flags&OF); }

static int pd_shell0_greater(const Regs *r) { return !(r->flags&ZF) && !pd_shell0_less(r); }

static void pd_shell0_actor_init(Regs *r,DeliveryPlan *plan,unsigned field) {
    r->si=A(ActorDescriptors); r->ax=DESC(field);
    W(ActorUpdateOrScriptCursor,r->ax);
    W(ActorAnimationByteOffsets,0xfffe); W(ActorAnimationCountdowns,1);
}

static int pd_shell0_tail(Regs *r,DeliveryPlan *plan, unsigned field) { return pd_shell0_state_jump(r,plan,DESC(field)); }

static int pd_shell0_state_jump(Regs *r,DeliveryPlan *plan,uint16_t target) { return delivery_dispatch(r,plan,target); }

static int shell_BeginPassengerPlatformWait(Regs *r,DeliveryPlan *plan) {
    pd_shell0_actor_init(r,plan,0x12); r->ax=0xffff;
    W(ActorPhaseOrDemoLoopCursor,r->ax); W(ActorOverlayOrScriptCallbacks,r->ax); return UGH_OK;
}

static int shell_BeginPassengerDestinationDisplay(Regs *r,DeliveryPlan *plan) {
    pd_shell0_actor_init(r,plan,0x16); r->ax=add16(r,A(ActorDestinationPlatforms),0x10c,0);
    sub16(r,r->ax,0x112,0); if(!(r->flags&CF)) r->ax=0x111;
    W(ActorOverlayOrScriptCallbacks,r->ax); W(ActorPhaseOrDemoLoopCursor,140); return UGH_OK;
}

static int shell_BeginPassengerQuestionDisplay(Regs *r,DeliveryPlan *plan) {
    pd_shell0_actor_init(r,plan,0x1a); W(ActorOverlayOrScriptCallbacks,0x112); W(ActorPhaseOrDemoLoopCursor,140); return UGH_OK;
}

static int shell_BeginPassengerApproach(Regs *r,DeliveryPlan *plan) {
    pd_shell0_actor_init(r,plan,0x1e); W(ActorOverlayOrScriptCallbacks,0xffff); return UGH_OK;
}

static int shell_BoardPassenger(Regs *r,DeliveryPlan *plan) {
    r->si=A(ActorDescriptors); r->ax=DESC(0x40); WRITE(PlayerPassengerFares,r->di,r->ax);
    r->ax=DESC(0x42); WRITE(PlayerMinimumFares,r->di,r->ax);
    r->ax=DESC(0x22); W(ActorUpdateOrScriptCursor,r->ax);
    r->ax=DESC(0x46); WRITE(PlayerCarriedKinds,r->di,r->ax);
    r->si=A(ActorDestinationPlatformByteIndices); r->ax=READ(PlatformDestinationIcons,r->si);
    WRITE(PlayerDestinationIcons,r->di,r->ax); W(ActorPhaseOrDemoLoopCursor,r->di);
    W(ActorSpriteIds,0xffff); W(PassengerQuickDeliveryCountdowns,200);
    r->di=A(ActorSourcePlatformByteIndices); WRITE(PlatformActorOccupants,r->di,0xffff); return UGH_OK;
}

static int shell_UpdateCarriedPassenger(Regs *r,DeliveryPlan *plan) {
    r->di=A(ActorPhaseOrDemoLoopCursor); r->ax=READ(PlayerPassengerFares,r->di);
    sub16(r,r->ax,READ(PlayerMinimumFares,r->di),0);
    if(!(r->flags&(CF|ZF))) { r->ax=dec16(r,r->ax); WRITE(PlayerPassengerFares,r->di,r->ax); }
    r->ax=A(PassengerQuickDeliveryCountdowns); sub16(r,r->ax,0,0);
    if(pd_shell0_greater(r)) { r->ax=dec16(r,r->ax); W(PassengerQuickDeliveryCountdowns,r->ax); }
    r->ax=A(ActorDestinationPlatforms); sub16(r,r->ax,READ(PlayerPlatformIndices,r->di),0);
    if(!(r->flags&ZF)) return UGH_OK;
    r->si=A(ActorDescriptors); return pd_shell0_tail(r,plan,0x24);
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
#define W(n,i,v) delivery_write16(plan,r,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define A(n) R(n,r->bx)
#define B(n,v) W(n,r->bx,v)
#define F(n) rd16(r->ds,(uint16_t)(r->si+(n)))
static int pd_shell1_tail(Regs *r,DeliveryPlan *plan,unsigned field);
static int pd_shell1_lt(const Regs *r) { return !!(r->flags&SF)!=!!(r->flags&OF); }

static int pd_shell1_gt(const Regs *r) { return !(r->flags&ZF)&&!pd_shell1_lt(r); }

static uint16_t pd_shell1_shift(Regs *r,uint16_t v,unsigned n,int right) {
    for(unsigned i=0;i<n;i++) {
        flag(r,CF,right?(v&1):(v&0x8000));
        v=right?(uint16_t)((v>>1)|(v&0x8000)):(uint16_t)(v<<1);
    }
    szp(r,v,16); if(n==1) flag(r,OF,right?0:(!!(v&0x8000)^!!(r->flags&CF)));
    return v;
}

static uint16_t pd_shell1_inc(Regs *r,uint16_t v) {
    uint16_t cf=r->flags&CF; v=add16(r,v,1,0); flag(r,CF,cf); return v;
}

static void pd_shell1_push(Regs *r,uint16_t v) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v); }

static uint16_t pd_shell1_pop(Regs *r) { uint16_t v=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return v; }

static int pd_shell1_effect(Regs *r,DeliveryPlan *plan,uint16_t segment,uint16_t offset,uint16_t ret) {
    pd_shell1_push(r,1); pd_shell1_push(r,255); pd_shell1_push(r,segment); pd_shell1_push(r,offset);
    pd_shell1_push(r,r->cs); pd_shell1_push(r,ret);
    int status=delivery_sound(r,plan,UGH_S_C_PlayAdlibEffect,UGH_O_C_PlayAdlibEffect);
    if(status) return status;
    r->sp=(uint16_t)(r->sp+4); r->sp=add16(r,r->sp,8,0); return UGH_OK;
}

static int pd_shell1_frame(Regs *r,DeliveryPlan *plan,int enemy,unsigned field,int directional) {
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

static int pd_shell1_actor_tick(Regs *r,DeliveryPlan *plan) {
    uint16_t count=dec16(r,A(ActorAnimationCountdowns)); B(ActorAnimationCountdowns,count);
    if(count) return 0;
    r->ax=F(0x3e); B(ActorAnimationCountdowns,r->ax);
    B(ActorAnimationByteOffsets,add16(r,A(ActorAnimationByteOffsets),2,0)); return 1;
}

static int pd_shell1_submerged(Regs *r) {
    r->ax=pd_shell1_shift(r,F(2),1,1); r->ax=add16(r,r->ax,A(ActorPixelY),0);
    r->ax=sub16(r,r->ax,R(WaterYPixels,0),0); return !(r->flags&SF);
}

static int pd_shell1_water_swap(Regs *r,DeliveryPlan *plan,int place) {
    if(place) {
        r->ax=add16(r,R(WaterYPixels,0),F(2),0); r->ax=pd_shell1_shift(r,r->ax,5,0); B(ActorY32,r->ax);
        r->di=A(ActorSourcePlatformByteIndices); r->ax=0xffff;
        W(PlatformActorOccupants,r->di,r->ax); B(ActorOverlayOrScriptCallbacks,r->ax);
    }
    r->si=F(0x48); B(ActorDescriptors,r->si); return pd_shell1_tail(r,plan,8);
}

static int pd_shell1_platform_player(Regs *r,int empty) {
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

static int pd_shell1_display(Regs *r,DeliveryPlan *plan,int question) {
    r->si=A(ActorDescriptors); if(pd_shell1_submerged(r)) return pd_shell1_water_swap(r,plan,1);
    int status=delivery_near(r,plan,G(FindPlayerTouchingActor),(uint16_t)((question?G(UpdatePassengerQuestionDisplay)+0x3f:G(UpdatePassengerDestinationDisplay)+0x3f)));
    if(status) return status;
    if(!(r->flags&SF)) { sub16(r,r->ax,0xffff,0); if(r->flags&ZF) return pd_shell1_water_swap(r,plan,0); }
    if(!question) {
        int found=pd_shell1_platform_player(r,0); if(found<0) return UGH_BUDGET;
        if(!found) return pd_shell1_tail(r,plan,0x18);
        sub16(r,R(PlayerCarriedKinds,r->di),0,0); if(!(r->flags&ZF)) return pd_shell1_tail(r,plan,0x18);
    }
    if(pd_shell1_actor_tick(r,plan)) { status=pd_shell1_frame(r,plan,0,0x30,0); if(status) return status; }
    uint16_t count=dec16(r,A(ActorPhaseOrDemoLoopCursor)); B(ActorPhaseOrDemoLoopCursor,count); if(count) return UGH_OK;
    if(!question) return pd_shell1_tail(r,plan,0x1c);
    r->di=A(ActorSourcePlatformByteIndices);
    int found=pd_shell1_platform_player(r,1); if(found<0) return UGH_BUDGET; return pd_shell1_tail(r,plan,found?0x14:0x10);
}

static int pd_shell1_tail(Regs *r,DeliveryPlan *plan,unsigned field) { return delivery_dispatch(r,plan,F(field)); }

static int shell_UpdatePassengerPlatformWait(Regs *r,DeliveryPlan *plan) {
    r->di=A(ActorSourcePlatformByteIndices); r->si=A(ActorDescriptors);
    if(pd_shell1_submerged(r)) return pd_shell1_water_swap(r,plan,1);
    if(pd_shell1_actor_tick(r,plan)) {
        r->ax=add16(r,A(ActorPixelX),F(0),0); sub16(r,r->ax,R(PlatformWaitingPointsX,r->di),0);
        if(!(r->flags&ZF)) {
            B(ActorPhaseOrDemoLoopCursor,0); int left=!pd_shell1_lt(r), status=pd_shell1_frame(r,plan,0,left?0x32:0x34,0); if(status) return status;
            B(ActorX32,left?sub16(r,A(ActorX32),32,0):add16(r,A(ActorX32),32,0));
        } else {
            sub16(r,A(ActorPhaseOrDemoLoopCursor),1,0); if(!(r->flags&ZF)) B(ActorAnimationByteOffsets,0);
            int status=pd_shell1_frame(r,plan,0,0x2e,0); if(status) return status; B(ActorPhaseOrDemoLoopCursor,1);
        }
    }
    int status=delivery_near(r,plan,G(FindPlayerTouchingActor),(uint16_t)(G(UpdatePassengerPlatformWait)+0xe2)); if(status) return status;
    if(!(r->flags&SF)) { sub16(r,r->ax,0xffff,0); if(r->flags&ZF) return pd_shell1_water_swap(r,plan,0); }
    int found=pd_shell1_platform_player(r,1); if(found<0) return UGH_BUDGET; return found?pd_shell1_tail(r,plan,0x14):UGH_OK;
}

static int shell_UpdatePassengerDestinationDisplay(Regs *r,DeliveryPlan *plan) { return pd_shell1_display(r,plan,0); }

static int shell_UpdatePassengerQuestionDisplay(Regs *r,DeliveryPlan *plan) { return pd_shell1_display(r,plan,1); }

static int shell_UpdatePassengerApproach(Regs *r,DeliveryPlan *plan) {
    r->si=A(ActorDescriptors); if(pd_shell1_submerged(r)) return pd_shell1_water_swap(r,plan,1);
    int status=delivery_near(r,plan,G(FindPlayerTouchingActor),(uint16_t)(G(UpdatePassengerApproach)+0x3f)); if(status) return status;
    if(!(r->flags&SF)) { sub16(r,r->ax,0xffff,0); if(r->flags&ZF) return pd_shell1_water_swap(r,plan,0); }
    int found=pd_shell1_platform_player(r,0); if(found<0) return UGH_BUDGET; if(!found) return pd_shell1_tail(r,plan,0x18);
    r->cx=logic(r,0,16); if(pd_shell1_actor_tick(r,plan)) r->cx=pd_shell1_inc(r,r->cx);
    r->ax=add16(r,A(ActorPixelX),F(0),0); r->ax=sub16(r,r->ax,16,0); sub16(r,r->ax,R(PlayerPixelX,r->di),0);
    if(r->flags&ZF) return pd_shell1_tail(r,plan,0x20);
    int left=pd_shell1_gt(r); status=pd_shell1_frame(r,plan,0,left?0x32:0x34,0); if(status) return status;
    logic(r,r->cx,16); if(r->cx) B(ActorX32,left?sub16(r,A(ActorX32),32,0):add16(r,A(ActorX32),32,0));
    return UGH_OK;
}

static int shell_BoardWaterbornePassenger(Regs *r,DeliveryPlan *plan) {
    r->si=A(ActorDescriptors); r->ax=F(0x40); W(PlayerPassengerFares,r->di,r->ax);
    r->ax=F(0x42); W(PlayerMinimumFares,r->di,r->ax); r->si=F(0x48); B(ActorDescriptors,r->si);
    r->ax=F(0x22); B(ActorUpdateOrScriptCursor,r->ax); r->ax=F(0x46); W(PlayerCarriedKinds,r->di,r->ax);
    r->si=A(ActorDestinationPlatformByteIndices); r->ax=R(PlatformDestinationIcons,r->si); W(PlayerDestinationIcons,r->di,r->ax);
    B(ActorPhaseOrDemoLoopCursor,r->di); B(ActorSpriteIds,0xffff); B(PassengerQuickDeliveryCountdowns,200);
    r->di=A(ActorSourcePlatformByteIndices); W(PlatformActorOccupants,r->di,0xffff); return UGH_OK;
}

static int shell_DeliverPassenger(Regs *r,DeliveryPlan *plan) {
    r->si=A(ActorDescriptors); r->ax=F(0x26); B(ActorUpdateOrScriptCursor,r->ax);
    r->ax=logic(r,0,16); W(PlayerCarriedKinds,r->di,r->ax); W(PlayerDestinationIcons,r->di,r->ax);
    r->ax=sub16(r,16,F(0),0); r->ax=pd_shell1_shift(r,r->ax,5,0); r->di=A(ActorPhaseOrDemoLoopCursor);
    r->ax=add16(r,r->ax,R(PlayerX32,r->di),0); B(ActorX32,r->ax); r->ax=R(PlayerPassengerFares,r->di);
    uint32_t product=(uint32_t)r->ax*R(ScoreMultiplier,0); r->ax=(uint16_t)product; r->dx=(uint16_t)(product>>16);
    flag(r,CF,r->dx!=0); flag(r,OF,r->dx!=0);
    W(ScoreLowWord,0,add16(r,R(ScoreLowWord,0),r->ax,0));
    W(ScoreHighWord,0,add16(r,R(ScoreHighWord,0),r->dx,!!(r->flags&CF)));
    logic(r,A(PassengerQuickDeliveryCountdowns),16);
    if(!(r->flags&ZF)) {
        pd_shell1_push(r,r->si); r->ax=R(ScoreMultiplier,0); r->si=pd_shell1_shift(r,R(SelectedDifficulty,0),1,0);
        sub16(r,r->ax,R(MultiplierLimitsByDifficulty,r->si),0);
        if(r->flags&CF) {
            r->ax=add16(r,R(PlayerX32,r->di),0x200,0); r->bp=add16(r,R(PlayerY32,r->di),0x140,0);
            r->cx=logic(r,0,16); r->dx=logic(r,0,16); r->si=D(FallingDescriptor_7A38);
            int status=delivery_near(r,plan,F(4),(uint16_t)(G(DeliverPassenger)+0x70)); if(status) return status;
            pd_shell1_push(r,r->bx); status=pd_shell1_effect(r,plan,UGH_S_B3274_ext_3274,UGH_O_B3274_ext_3274,(uint16_t)(G(DeliverPassenger)+0x81));
            if(status) return status;
            r->bx=pd_shell1_pop(r);
        }
        r->si=pd_shell1_pop(r);
    }
    r->di=A(ActorDestinationPlatformByteIndices); r->ax=sub16(r,0,F(2),0);
    r->ax=add16(r,r->ax,R(PlatformHeights,r->di),0); r->ax=pd_shell1_shift(r,r->ax,5,0); B(ActorY32,r->ax);
    B(ActorAnimationByteOffsets,0xfffe); r->ax=1; B(ActorAnimationCountdowns,r->ax); delivery_write8(plan,r,D(HudFareClearPending),(uint8_t)r->ax); return UGH_OK;
}

#undef READ
#undef WRITE
#undef A
#undef W
#undef DESC
#undef R
#undef B
#undef F
/* DELIVERY_SHELLS_END */
/* DELIVERY_EXPORTS_BEGIN */
int l1_BeginPassengerPlatformWait(Regs *r);
int l1_UpdatePassengerPlatformWait(Regs *r);
int l1_BeginPassengerDestinationDisplay(Regs *r);
int l1_UpdatePassengerDestinationDisplay(Regs *r);
int l1_BeginPassengerQuestionDisplay(Regs *r);
int l1_UpdatePassengerQuestionDisplay(Regs *r);
int l1_BeginPassengerApproach(Regs *r);
int l1_UpdatePassengerApproach(Regs *r);
int l1_BoardWaterbornePassenger(Regs *r);
int l1_BoardPassenger(Regs *r);
int l1_UpdateCarriedPassenger(Regs *r);
int l1_DeliverPassenger(Regs *r);
EXPORT int c_BeginPassengerPlatformWait(Regs *r) {
    DeliveryPlan plan;
    if(!delivery_prepare(r,PD_BEGIN_WAIT,&plan)) return l1_BeginPassengerPlatformWait(r);
    int status=shell_BeginPassengerPlatformWait(r,&plan);
    if(plan.bad || (!status && (plan.consumed!=plan.result.count || plan.spawn_seen!=plan.result.spawn_bonus || plan.sound_seen!=plan.result.bonus_sound))) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_UpdatePassengerPlatformWait(Regs *r) {
    DeliveryPlan plan;
    if(!delivery_prepare(r,PD_WAIT,&plan)) return l1_UpdatePassengerPlatformWait(r);
    int status=shell_UpdatePassengerPlatformWait(r,&plan);
    if(plan.bad || (!status && (plan.consumed!=plan.result.count || plan.spawn_seen!=plan.result.spawn_bonus || plan.sound_seen!=plan.result.bonus_sound))) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_BeginPassengerDestinationDisplay(Regs *r) {
    DeliveryPlan plan;
    if(!delivery_prepare(r,PD_BEGIN_DESTINATION,&plan)) return l1_BeginPassengerDestinationDisplay(r);
    int status=shell_BeginPassengerDestinationDisplay(r,&plan);
    if(plan.bad || (!status && (plan.consumed!=plan.result.count || plan.spawn_seen!=plan.result.spawn_bonus || plan.sound_seen!=plan.result.bonus_sound))) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_UpdatePassengerDestinationDisplay(Regs *r) {
    DeliveryPlan plan;
    if(!delivery_prepare(r,PD_DESTINATION,&plan)) return l1_UpdatePassengerDestinationDisplay(r);
    int status=shell_UpdatePassengerDestinationDisplay(r,&plan);
    if(plan.bad || (!status && (plan.consumed!=plan.result.count || plan.spawn_seen!=plan.result.spawn_bonus || plan.sound_seen!=plan.result.bonus_sound))) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_BeginPassengerQuestionDisplay(Regs *r) {
    DeliveryPlan plan;
    if(!delivery_prepare(r,PD_BEGIN_QUESTION,&plan)) return l1_BeginPassengerQuestionDisplay(r);
    int status=shell_BeginPassengerQuestionDisplay(r,&plan);
    if(plan.bad || (!status && (plan.consumed!=plan.result.count || plan.spawn_seen!=plan.result.spawn_bonus || plan.sound_seen!=plan.result.bonus_sound))) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_UpdatePassengerQuestionDisplay(Regs *r) {
    DeliveryPlan plan;
    if(!delivery_prepare(r,PD_QUESTION,&plan)) return l1_UpdatePassengerQuestionDisplay(r);
    int status=shell_UpdatePassengerQuestionDisplay(r,&plan);
    if(plan.bad || (!status && (plan.consumed!=plan.result.count || plan.spawn_seen!=plan.result.spawn_bonus || plan.sound_seen!=plan.result.bonus_sound))) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_BeginPassengerApproach(Regs *r) {
    DeliveryPlan plan;
    if(!delivery_prepare(r,PD_BEGIN_APPROACH,&plan)) return l1_BeginPassengerApproach(r);
    int status=shell_BeginPassengerApproach(r,&plan);
    if(plan.bad || (!status && (plan.consumed!=plan.result.count || plan.spawn_seen!=plan.result.spawn_bonus || plan.sound_seen!=plan.result.bonus_sound))) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_UpdatePassengerApproach(Regs *r) {
    DeliveryPlan plan;
    if(!delivery_prepare(r,PD_APPROACH,&plan)) return l1_UpdatePassengerApproach(r);
    int status=shell_UpdatePassengerApproach(r,&plan);
    if(plan.bad || (!status && (plan.consumed!=plan.result.count || plan.spawn_seen!=plan.result.spawn_bonus || plan.sound_seen!=plan.result.bonus_sound))) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_BoardWaterbornePassenger(Regs *r) {
    DeliveryPlan plan;
    if(!delivery_prepare(r,PD_RESCUE,&plan)) return l1_BoardWaterbornePassenger(r);
    int status=shell_BoardWaterbornePassenger(r,&plan);
    if(plan.bad || (!status && (plan.consumed!=plan.result.count || plan.spawn_seen!=plan.result.spawn_bonus || plan.sound_seen!=plan.result.bonus_sound))) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_BoardPassenger(Regs *r) {
    DeliveryPlan plan;
    if(!delivery_prepare(r,PD_BOARD,&plan)) return l1_BoardPassenger(r);
    int status=shell_BoardPassenger(r,&plan);
    if(plan.bad || (!status && (plan.consumed!=plan.result.count || plan.spawn_seen!=plan.result.spawn_bonus || plan.sound_seen!=plan.result.bonus_sound))) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_UpdateCarriedPassenger(Regs *r) {
    DeliveryPlan plan;
    if(!delivery_prepare(r,PD_CARRIED,&plan)) return l1_UpdateCarriedPassenger(r);
    int status=shell_UpdateCarriedPassenger(r,&plan);
    if(plan.bad || (!status && (plan.consumed!=plan.result.count || plan.spawn_seen!=plan.result.spawn_bonus || plan.sound_seen!=plan.result.bonus_sound))) return UGH_BAD_CALLBACK;
    return status;
}
EXPORT int c_DeliverPassenger(Regs *r) {
    DeliveryPlan plan;
    if(!delivery_prepare(r,PD_DELIVER,&plan)) return l1_DeliverPassenger(r);
    int status=shell_DeliverPassenger(r,&plan);
    if(plan.bad || (!status && (plan.consumed!=plan.result.count || plan.spawn_seen!=plan.result.spawn_bonus || plan.sound_seen!=plan.result.bonus_sound))) return UGH_BAD_CALLBACK;
    return status;
}
/* DELIVERY_EXPORTS_END */
