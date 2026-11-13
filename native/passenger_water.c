#include "passenger_water.h"
static int32_t pw_signed(uint16_t v) {return v<32768u?(int32_t)v:(int32_t)v-65536;}
static uint16_t pw_sar(uint16_t v,unsigned bits) {
    return (uint16_t)((v>>bits)|((v&32768u)?(65535u<<(16u-bits)):0u));
}
static void pw_emit(PassengerWaterResult *out,PassengerWaterField field,size_t index,uint16_t value) {
    PassengerWaterWrite *write=&out->writes[out->count++];write->field=field;write->index=index;write->value=value;
}
static void pw_begin(PassengerWaterResult *out,PassengerStoneSlot *slot,ActorPhase phase) {
    slot->phase=phase;pw_emit(out,PW_PHASE,0,(uint16_t)phase);
    slot->animation.byte_offset=65534u;pw_emit(out,PW_CURSOR,0,65534u);
    slot->animation.countdown=1;pw_emit(out,PW_TICK,0,1);
}
static int pw_tick(PassengerWaterResult *out,PassengerStoneSlot *slot) {
    slot->animation.countdown--;pw_emit(out,PW_TICK,0,slot->animation.countdown);
    if(slot->animation.countdown) return 0;
    slot->animation.countdown=slot->type->animation_period;pw_emit(out,PW_TICK,0,slot->animation.countdown);
    slot->animation.byte_offset=(uint16_t)(slot->animation.byte_offset+2u);pw_emit(out,PW_CURSOR,0,slot->animation.byte_offset);return 1;
}
static int pw_frame(PassengerWaterResult *out,PassengerStoneSlot *slot,ActorAnimationKind kind) {
    const ActorAnimation *animation=&slot->type->animations[kind];size_t index=slot->animation.byte_offset/2u;
    if((slot->animation.byte_offset&1u) || index>animation->count || !animation->count) {out->failed=1;return 0;}
    if(index==animation->count) {slot->animation.byte_offset=0;pw_emit(out,PW_CURSOR,0,0);index=0;}
    slot->sprite=animation->sprites[index];pw_emit(out,PW_SPRITE,0,slot->sprite);return 1;
}
static int pw_animate(PassengerWaterResult *out,PassengerStoneSlot *slot,ActorAnimationKind kind,int conditional) {
    int due=pw_tick(out,slot);
    return (conditional && !due) || pw_frame(out,slot,kind);
}
static void pw_surface(PassengerWaterResult *out,PassengerStoneSlot *slot,const ActorRenderHistory *render,const PassengerWaterWorld *world) {
    /* Equality uses the stale cached Y itself, without subtracting the anchor. */
    if(render->pixel_y==world->surface_y) return;
    slot->position.y32=(uint16_t)((world->surface_y-slot->type->geometry.anchor_y)*32u);pw_emit(out,PW_Y,0,slot->position.y32);
}
static void pw_resurface_motion(PassengerWaterResult *out,PassengerStoneSlot *slot,const ActorRenderHistory *render,const PassengerWaterWorld *world) {
    uint16_t delta=(uint16_t)(render->pixel_y-slot->type->geometry.anchor_y-world->surface_y);
    uint16_t velocity=slot->vertical_motion;
    /* JS of a wrapped difference, not a signed comparison of its operands.
     * The machine shell also retains the positive-difference CH=1 stamp. */
    velocity=(uint16_t)(velocity+((delta&32768u)?39u:(pw_signed(velocity)>0?65163u:65444u)));
    if(pw_signed(velocity)<0) {if(pw_signed(velocity)<-6144) velocity=59392u;}
    else if(pw_signed(velocity)>6144) velocity=6144;
    slot->vertical_motion=velocity;pw_emit(out,PW_VELOCITY,0,velocity);
    slot->position.y32=(uint16_t)(slot->position.y32+pw_sar(velocity,6));pw_emit(out,PW_Y,0,slot->position.y32);
}
static void pw_resurface_cross(PassengerWaterResult *out,PassengerStoneSlot *slot,const PassengerWaterWorld *world) {
    if(pw_signed(slot->vertical_motion)>=0) return;
    uint16_t top=(uint16_t)(pw_sar(slot->position.y32,5)-slot->type->geometry.anchor_y);
    if(pw_signed(top)>pw_signed(world->surface_y)) return;
    slot->position.y32=(uint16_t)((world->surface_y-slot->type->geometry.anchor_y)*32u);pw_emit(out,PW_Y,0,slot->position.y32);out->next=PW_NEXT_FLOAT;
}
static void pw_sink_motion(PassengerWaterResult *out,PassengerStoneSlot *slot) {
    slot->vertical_motion=(uint16_t)(slot->vertical_motion+39u);pw_emit(out,PW_VELOCITY,0,slot->vertical_motion);
    uint16_t y=(uint16_t)(slot->position.y32+pw_sar(slot->vertical_motion,6));
    /* The retirement threshold is unsigned; the raw accumulator is not clamped. */
    if(y<6144u) {slot->position.y32=y;pw_emit(out,PW_Y,0,y);}
    else {slot->phase=ACTOR_RETIRED;pw_emit(out,PW_PHASE,0,ACTOR_RETIRED);slot->sprite=65535u;pw_emit(out,PW_SPRITE,0,65535u);}
}
static int pw_at_surface(const WaterCraft *craft,const PassengerWaterWorld *world) {
    return (uint16_t)(craft->pixel_y-world->surface_y+18u)==0;
}
static void pw_float_select(PassengerWaterResult *out,const PassengerStoneSlot *slot,const PassengerWaterWorld *world) {
    /* The second passenger's water identity deliberately never searches. */
    if(slot->type->id==ACTOR_PASSENGER_TWO_WATER) return;
    for(size_t i=0;i<world->player_count;i++) if(!world->craft[i].vertical_velocity && !world->craft[i].carried_kind && pw_at_surface(&world->craft[i],world)) {
        out->selected=(int)i;out->next=PW_NEXT_DESTINATION;return;
    }
}
static void pw_float_expire(PassengerWaterResult *out,PassengerStoneSlot *slot) {
    uint16_t value;if(!actor_alias_value(slot,ACTOR_ALIAS_FLOATING_TICKS,&value)) {out->failed=1;return;}
    slot->floating_ticks=(uint16_t)(value-1u);pw_emit(out,PW_LIFETIME,0,slot->floating_ticks);
    if(!slot->floating_ticks) out->next=PW_NEXT_SINK;
}
static int pw_destination_gate(PassengerWaterResult *out,const PassengerWaterWorld *world) {
    for(size_t i=0;i<world->player_count;i++) if(pw_at_surface(&world->craft[i],world)) return 0;
    out->next=PW_NEXT_QUESTION;return 1;
}
static void pw_request_clock(PassengerWaterResult *out,PassengerStoneSlot *slot,PassengerWaterEntry entry) {
    uint16_t value;if(!actor_alias_value(slot,ACTOR_ALIAS_REQUEST_TICKS,&value)) {out->failed=1;return;}
    slot->request_ticks=(uint16_t)(value-1u);pw_emit(out,PW_REQUEST,0,slot->request_ticks);
    if(!slot->request_ticks) out->next=entry==PW_DESTINATION?PW_NEXT_APPROACH:PW_NEXT_SINK;
}
static int pw_approach_select(PassengerWaterResult *out,const PassengerWaterWorld *world) {
    for(size_t i=0;i<world->player_count;i++) if(!world->craft[i].carried_kind && pw_at_surface(&world->craft[i],world)) {out->selected=(int)i;return 0;}
    out->next=PW_NEXT_QUESTION;return 1;
}
static void pw_approach_motion(PassengerWaterResult *out,PassengerStoneSlot *slot,const ActorRenderHistory *render,const PassengerWaterWorld *world) {
    int due=pw_tick(out,slot);
    uint16_t center=(uint16_t)(render->pixel_x+slot->type->geometry.anchor_x-16u),target=world->craft[out->selected].pixel_x;
    if(center==target) {out->next=PW_NEXT_BOARD;return;}
    int left=pw_signed(center)>pw_signed(target);
    if(!pw_frame(out,slot,left?ACTOR_WALK_LEFT_ANIMATION:ACTOR_WALK_RIGHT_ANIMATION)) return;
    if(due) {slot->position.x32=(uint16_t)(slot->position.x32+(left?65504u:32u));pw_emit(out,PW_X,0,slot->position.x32);}
}
PassengerWaterResult passenger_water_apply(PassengerWaterEntry entry,PassengerStoneSlot *slot,const ActorRenderHistory *render,const PassengerWaterWorld *world) {
    PassengerWaterResult out={0};out.selected=-1;
    switch(entry) {
    case PW_BEGIN_RESURFACE:
        slot->phase=ACTOR_RESURFACING;pw_emit(&out,PW_PHASE,0,ACTOR_RESURFACING);
        pw_emit(&out,PW_OCCUPANT_CLEAR,slot->source_platform,65535u);
        slot->overlay_sprite=65535u;pw_emit(&out,PW_OVERLAY,0,65535u);
        slot->animation.byte_offset=65534u;pw_emit(&out,PW_CURSOR,0,65534u);
        slot->animation.countdown=1;pw_emit(&out,PW_TICK,0,1);
        slot->vertical_motion=0;pw_emit(&out,PW_VELOCITY,0,0);break;
    case PW_BEGIN_SINK:
        pw_begin(&out,slot,ACTOR_SINKING);slot->overlay_sprite=65535u;pw_emit(&out,PW_OVERLAY,0,65535u);
        slot->vertical_motion=0;pw_emit(&out,PW_VELOCITY,0,0);break;
    case PW_BEGIN_FLOAT:
        pw_begin(&out,slot,ACTOR_FLOATING);slot->floating_ticks=slot->type->floating_lifetime;pw_emit(&out,PW_LIFETIME,0,slot->floating_ticks);break;
    case PW_RESURFACE:
        if(!pw_animate(&out,slot,ACTOR_IDLE_ANIMATION,0)) break;
        pw_resurface_motion(&out,slot,render,world);pw_resurface_cross(&out,slot,world);break;
    case PW_SINK:
        if(pw_animate(&out,slot,ACTOR_IDLE_ANIMATION,0)) pw_sink_motion(&out,slot);
        break;
    case PW_FLOAT:
        if(!pw_animate(&out,slot,ACTOR_REQUEST_ANIMATION,0)) break;
        pw_surface(&out,slot,render,world);pw_float_select(&out,slot,world);
        if(out.next==PW_NEXT_NONE) pw_float_expire(&out,slot);
        break;
    case PW_DESTINATION:case PW_QUESTION:
        pw_surface(&out,slot,render,world);
        if(entry==PW_DESTINATION && pw_destination_gate(&out,world)) break;
        if(!pw_animate(&out,slot,ACTOR_REQUEST_ANIMATION,1)) break;
        pw_request_clock(&out,slot,entry);break;
    case PW_APPROACH:
        pw_surface(&out,slot,render,world);if(!pw_approach_select(&out,world)) pw_approach_motion(&out,slot,render,world);break;
    case PW_IGNORE:break;
    }
    return out;
}
