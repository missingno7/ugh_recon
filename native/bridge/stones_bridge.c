#include "ugh.h"
#include "../stones.h"
#include "actor_projection.h"
int l1_BeginStonePickupWait(Regs *r);
int l1_UpdateStonePickupWait(Regs *r);
int l1_AttachStoneToPlayer(Regs *r);
int l1_WaitForStoneRelease(Regs *r);
int l1_ThrowCarriedStone(Regs *r);
int l1_UpdateThrownStone(Regs *r);
static uint16_t stone_word(Regs *r,uint16_t base,uint16_t index) {
    return rd16(r->ds,(uint16_t)(base+index));
}
static uint16_t stone_desc(Regs *r,unsigned field) { return rd16(r->ds,(uint16_t)(r->si+field)); }
static void stone_write(Regs *r,uint16_t base,uint16_t value) { wr16(r->ds,(uint16_t)(base+r->bx),value); }
static uint16_t stone_shift(Regs *r,uint16_t value,unsigned n,int right) {
    for(unsigned i=0;i<n;i++) {
        flag(r,CF,right?(value&1):(value&32768u));
        value=right?(uint16_t)((value>>1)|(value&32768u)):(uint16_t)(value<<1);
    }
    szp(r,value,16);if(n==1) flag(r,OF,right?0:(!!(value&32768u)^!!(r->flags&CF)));
    return value;
}
static int stone_project(Regs *r,ActorPhase phase,PassengerStoneSlot *slot,ActorType *type,StonePlayer players[2]) {
    if(r->ds!=DATA_SEG || r->cs!=GAME_SEG || (r->bx&1u) || r->bx>=32u) return 0;
    uint16_t descriptor=stone_word(r,D(ActorDescriptors),r->bx);
    if(descriptor!=D(Data_78DC) && descriptor!=D(Data_7926)) return 0;
    const unsigned fields[]={0x10,0x12,0x20,0x22,0x24,0x26,0x2c};
    const uint16_t handlers[]={G(BeginStonePickupWait),G(UpdateStonePickupWait),G(AttachStoneToPlayer),
        G(WaitForStoneRelease),G(ThrowCarriedStone),G(UpdateThrownStone),G(IgnoreActorState)};
    for(size_t i=0;i<7;i++) if(rd16(r->ds,(uint16_t)(descriptor+fields[i]))!=handlers[i]) return 0;
    *type=(ActorType){0};type->id=descriptor==D(Data_78DC)?ACTOR_STONE:ACTOR_STONE_ALTERNATE;
    type->geometry.anchor_x=rd16(r->ds,descriptor);type->geometry.anchor_y=rd16(r->ds,(uint16_t)(descriptor+2));
    type->geometry.extent_x=rd16(r->ds,(uint16_t)(descriptor+4));type->geometry.extent_y=rd16(r->ds,(uint16_t)(descriptor+6));
    type->carried_kind=rd16(r->ds,(uint16_t)(descriptor+0x46));
    *slot=(PassengerStoneSlot){0};slot->type=type;
    if(!actor_bridge_alias_project(r->ds,r->bx/2u,phase,slot)) return 0;
    slot->position.x32=stone_word(r,D(ActorX32),r->bx);slot->position.y32=stone_word(r,D(ActorY32),r->bx);
    slot->sprite=stone_word(r,D(ActorSpriteIds),r->bx);
    slot->animation.byte_offset=stone_word(r,D(ActorAnimationByteOffsets),r->bx);
    slot->animation.countdown=stone_word(r,D(ActorAnimationCountdowns),r->bx);
    slot->vertical_motion=stone_word(r,D(ActorVerticalOrDemoPeriod),r->bx);
    for(unsigned i=0;i<2;i++) {
        uint16_t index=(uint16_t)(2*i);
        players[i].position.x32=stone_word(r,D(PlayerX32),index);players[i].position.y32=stone_word(r,D(PlayerY32),index);
        players[i].horizontal_velocity=stone_word(r,D(PlayerHorizontalVelocities),index);
        players[i].vertical_velocity=stone_word(r,D(PlayerVerticalVelocities),index);
        players[i].carried_kind=stone_word(r,D(PlayerCarriedKinds),index);
        players[i].destination_icon=stone_word(r,D(PlayerDestinationIcons),index);
        players[i].action_word=stone_word(r,D(PlayerActionInput),index);
    }
    return 1;
}
static void stone_push(Regs *r,uint16_t value) { r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,value); }
static int stone_effect(Regs *r) {
    stone_push(r,r->bx);stone_push(r,1);stone_push(r,255);stone_push(r,UGH_S_B3632_ext_3632);stone_push(r,0);
    stone_push(r,r->cs);stone_push(r,G(ThrowCarriedStone)+0x68);
    int status=ugh_dispatch(UGH_S_C_PlayAdlibEffect,UGH_O_C_PlayAdlibEffect,r);
    if(status) return status;
    r->sp=(uint16_t)(r->sp+4);r->sp=add16(r,r->sp,8,0);
    r->bx=rd16(r->ss,r->sp);r->sp=(uint16_t)(r->sp+2);return UGH_OK;
}
EXPORT int c_BeginStonePickupWait(Regs *r) {
    PassengerStoneSlot slot;ActorType type;StonePlayer players[2];
    if(!stone_project(r,ACTOR_BEGIN_STONE_WAIT,&slot,&type,players)) return l1_BeginStonePickupWait(r);
    stone_begin_wait(&slot);r->si=stone_word(r,D(ActorDescriptors),r->bx);r->ax=stone_desc(r,0x12);
    stone_write(r,D(ActorUpdateOrScriptCursor),r->ax);
    stone_write(r,D(ActorAnimationByteOffsets),slot.animation.byte_offset);stone_write(r,D(ActorAnimationCountdowns),slot.animation.countdown);
    return UGH_OK;
}
EXPORT int c_UpdateStonePickupWait(Regs *r) {
    PassengerStoneSlot slot;ActorType type;StonePlayer players[2];
    if(!stone_project(r,ACTOR_STONE_WAIT,&slot,&type,players)) return l1_UpdateStonePickupWait(r);
    StoneResult result=stone_pickup_wait(&slot,players,rd16(r->ds,D(PlayerCount)));
    r->si=stone_word(r,D(ActorDescriptors),r->bx);
    int status=ugh_call_near(G(FindPlayerTouchingActor),G(UpdateStonePickupWait)+7,r);if(status) return status;
    if(result.contact.index>=0) logic(r,stone_word(r,D(PlayerCarriedKinds),r->di),16);
    if(result.exit==STONE_PICKUP) return ugh_dispatch(r->cs,stone_desc(r,0x20),r);
    stone_write(r,D(ActorSpriteIds),slot.sprite);return UGH_OK;
}
EXPORT int c_AttachStoneToPlayer(Regs *r) {
    PassengerStoneSlot slot;ActorType type;StonePlayer players[2];
    if(r->di>2u || (r->di&1u) || (r->di==2 && rd16(r->ds,D(PlayerCount))!=2) ||
       !stone_project(r,ACTOR_STONE_WAIT,&slot,&type,players)) return l1_AttachStoneToPlayer(r);
    stone_attach(&slot,players,r->di/2u);r->si=stone_word(r,D(ActorDescriptors),r->bx);r->ax=stone_desc(r,0x22);
    stone_write(r,D(ActorUpdateOrScriptCursor),r->ax);r->ax=type.carried_kind;
    wr16(r->ds,(uint16_t)(D(PlayerCarriedKinds)+r->di),players[r->di/2u].carried_kind);
    wr16(r->ds,(uint16_t)(D(PlayerDestinationIcons)+r->di),players[r->di/2u].destination_icon);
    stone_write(r,D(ActorPhaseOrDemoLoopCursor),(uint16_t)(slot.carrier*2u));stone_write(r,D(ActorSpriteIds),slot.sprite);
    return UGH_OK;
}
EXPORT int c_WaitForStoneRelease(Regs *r) {
    PassengerStoneSlot slot;ActorType type;StonePlayer players[2];uint16_t carrier;
    if(!stone_project(r,ACTOR_CARRIED_STONE,&slot,&type,players) || !actor_bridge_alias_read(&slot,ACTOR_ALIAS_CARRIER,&carrier)) return l1_WaitForStoneRelease(r);
    int release=stone_release_requested(&slot,players);r->di=(uint16_t)(2u*carrier);
    logic(r,(uint8_t)players[carrier].action_word,8);
    if(!release) return UGH_OK;
    r->si=stone_word(r,D(ActorDescriptors),r->bx);return ugh_dispatch(r->cs,stone_desc(r,0x24),r);
}
EXPORT int c_ThrowCarriedStone(Regs *r) {
    PassengerStoneSlot slot;ActorType type;StonePlayer players[2];
    if(r->di>2u || (r->di&1u) || (r->di==2 && rd16(r->ds,D(PlayerCount))!=2) ||
       !stone_project(r,ACTOR_CARRIED_STONE,&slot,&type,players)) return l1_ThrowCarriedStone(r);
    StonePlayer before=players[r->di/2u];stone_throw(&slot,players,r->di/2u);
    r->si=stone_word(r,D(ActorDescriptors),r->bx);r->ax=logic(r,0,16);
    wr16(r->ds,(uint16_t)(D(PlayerCarriedKinds)+r->di),players[r->di/2u].carried_kind);
    wr16(r->ds,(uint16_t)(D(PlayerDestinationIcons)+r->di),players[r->di/2u].destination_icon);
    r->ax=stone_shift(r,before.horizontal_velocity,5,1);stone_write(r,D(ActorMotionWaitOrDemoRepeats),slot.horizontal_step);
    r->ax=stone_shift(r,before.vertical_velocity,5,1);stone_write(r,D(ActorVerticalOrDemoPeriod),slot.vertical_motion);
    r->ax=before.position.x32;r->bp=before.position.y32;
    r->ax=add16(r,r->ax,512,0);r->bp=add16(r,r->bp,320,0);
    r->di=stone_shift(r,type.geometry.anchor_x,5,0);r->ax=sub16(r,r->ax,r->di,0);stone_write(r,D(ActorX32),slot.position.x32);
    r->di=stone_shift(r,type.geometry.anchor_y,4,0);r->bp=sub16(r,r->bp,r->di,0);stone_write(r,D(ActorY32),slot.position.y32);
    stone_write(r,D(ActorSpriteIds),slot.sprite);r->ax=stone_desc(r,0x26);stone_write(r,D(ActorUpdateOrScriptCursor),r->ax);
    return stone_effect(r);
}
EXPORT int c_UpdateThrownStone(Regs *r) {
    PassengerStoneSlot slot;ActorType type;StonePlayer players[2];uint16_t horizontal;
    if(!stone_project(r,ACTOR_THROWN_STONE,&slot,&type,players) || !actor_bridge_alias_read(&slot,ACTOR_ALIAS_HORIZONTAL_STEP,&horizontal)) return l1_UpdateThrownStone(r);
    LevelPlatform platforms[10];size_t count=0;
    for(;;) {
        uint16_t left=stone_word(r,D(PlatformLeftEdges),(uint16_t)(2u*count));
        if(left&32768u) break;
        if(count==10) return l1_UpdateThrownStone(r);
        platforms[count]=(LevelPlatform){0};platforms[count].left=left;
        platforms[count].right=stone_word(r,D(PlatformRightEdges),(uint16_t)(2u*count));
        platforms[count].surface_y=stone_word(r,D(PlatformHeights),(uint16_t)(2u*count));count++;
    }
    PassengerStoneSlot before=slot;StoneResult result=stone_flight(&slot,platforms,count);
    r->si=stone_word(r,D(ActorDescriptors),r->bx);r->ax=add16(r,horizontal,before.position.x32,0);
    sub16(r,r->ax,65024u,0);if(result.exit==STONE_OUT_LEFT) goto gone;
    sub16(r,r->ax,10240,0);if(result.exit==STONE_OUT_RIGHT) goto gone;
    stone_write(r,D(ActorX32),slot.position.x32);r->ax=add16(r,before.vertical_motion,2,0);
    stone_write(r,D(ActorVerticalOrDemoPeriod),slot.vertical_motion);logic(r,r->ax,16);
    if(result.exit==STONE_RISING) { add16(r,before.position.y32,r->ax,0);stone_write(r,D(ActorY32),slot.position.y32);return UGH_OK; }
    r->cx=before.position.y32;r->ax=add16(r,r->ax,r->cx,0);sub16(r,r->ax,6144,0);
    if(result.exit==STONE_OUT_BOTTOM) goto gone;
    stone_write(r,D(ActorY32),r->ax);r->ax=stone_shift(r,r->ax,5,1);r->cx=stone_shift(r,r->cx,5,1);
    r->ax=add16(r,r->ax,type.geometry.anchor_y,0);r->cx=add16(r,r->cx,type.geometry.anchor_y,0);r->di=logic(r,0,16);
    for(size_t i=0;i<=result.platform;i++) {
        uint16_t left=i==count?stone_word(r,D(PlatformLeftEdges),(uint16_t)(2u*i)):platforms[i].left;
        logic(r,left,16);if(i==count) return UGH_OK;
        uint16_t height=platforms[i].surface_y;sub16(r,r->cx,height,0);
        if((int16_t)r->cx<=(int16_t)height) {
            sub16(r,r->ax,height,0);
            if((int16_t)r->ax>=(int16_t)height) {
                r->dx=stone_shift(r,slot.position.x32,5,1);r->dx=add16(r,r->dx,type.geometry.anchor_x,0);
                sub16(r,r->dx,left,0);
                if((int16_t)r->dx>=(int16_t)left) sub16(r,r->dx,platforms[i].right,0);
            }
        }
        if(result.exit==STONE_LANDING && i==result.platform) {
            r->ax=sub16(r,height,type.geometry.anchor_y,0);r->ax=stone_shift(r,r->ax,5,0);
            stone_write(r,D(ActorY32),slot.position.y32);return ugh_dispatch(r->cs,stone_desc(r,0x10),r);
        }
        r->di=add16(r,r->di,2,0);
    }
    return UGH_OK;
gone:
    stone_write(r,D(ActorSpriteIds),slot.sprite);r->ax=stone_desc(r,0x2c);stone_write(r,D(ActorUpdateOrScriptCursor),r->ax);return UGH_OK;
}
