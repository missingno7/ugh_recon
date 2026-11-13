#include "passenger_delivery.h"
static int32_t pd_signed(uint16_t value) {return value<32768u?(int32_t)value:(int32_t)value-65536;}
static void pd_emit(PassengerDeliveryResult *result,PassengerDeliveryField field,size_t index,uint16_t value) {
    PassengerDeliveryWrite *write=&result->writes[result->count++];write->field=field;write->index=index;write->value=value;
}
static void pd_begin(PassengerDeliveryResult *result,PassengerStoneSlot *slot,ActorPhase phase) {
    slot->phase=phase;pd_emit(result,PD_PHASE,0,(uint16_t)phase);
    slot->animation.byte_offset=65534u;pd_emit(result,PD_CURSOR,0,65534u);
    slot->animation.countdown=1;pd_emit(result,PD_TICK,0,1);
}
static int pd_tick(PassengerDeliveryResult *result,PassengerStoneSlot *slot) {
    slot->animation.countdown--;pd_emit(result,PD_TICK,0,slot->animation.countdown);
    if(slot->animation.countdown) return 0;
    slot->animation.countdown=slot->type->animation_period;pd_emit(result,PD_TICK,0,slot->animation.countdown);
    slot->animation.byte_offset=(uint16_t)(slot->animation.byte_offset+2u);pd_emit(result,PD_CURSOR,0,slot->animation.byte_offset);return 1;
}
static int pd_frame(PassengerDeliveryResult *result,PassengerStoneSlot *slot,ActorAnimationKind kind) {
    const ActorAnimation *animation=&slot->type->animations[kind];size_t index=slot->animation.byte_offset/2u;
    if((slot->animation.byte_offset&1u) || index>animation->count || !animation->count) {result->failed=1;return 0;}
    if(index==animation->count) {slot->animation.byte_offset=0;pd_emit(result,PD_CURSOR,0,0);index=0;}
    slot->sprite=animation->sprites[index];pd_emit(result,PD_SPRITE,0,slot->sprite);return 1;
}
static int pd_platform(const PassengerStoneSlot *slot,const PassengerDeliveryWorld *world,int empty) {
    for(size_t i=0;i<world->player_slots;i++)
        if(world->craft[i].platform==slot->source_platform && (!empty || !world->craft[i].carried_kind)) return (int)i;
    return -1;
}
static int pd_contact(const PassengerStoneSlot *slot,const PassengerDeliveryWorld *world) {
    ObjectPosition positions[2]={world->craft[0].position,world->craft[1].position};
    return contact_players(slot->position,slot->type->geometry,positions,world->player_count).index;
}
static int pd_submerged(const PassengerStoneSlot *slot,const ActorRenderHistory *render,const PassengerDeliveryWorld *world) {
    uint16_t height=slot->type->geometry.anchor_y;
    uint16_t half=(uint16_t)((height>>1)|(height&32768u));
    /* Retained JS of the WRAPPED subtraction, not a signed operand compare. */
    return !((uint16_t)(half+render->pixel_y-world->water_pixel_y)&32768u);
}
static void pd_water(PassengerDeliveryResult *result,PassengerStoneSlot *slot,const PassengerDeliveryWorld *world,int place) {
    if(!slot->type->paired_type) {result->failed=1;return;}
    if(place) {
        slot->position.y32=(uint16_t)((world->water_pixel_y+slot->type->geometry.anchor_y)*32u);pd_emit(result,PD_Y,0,slot->position.y32);
        pd_emit(result,PD_OCCUPANT_CLEAR,slot->source_platform,65535u);
        slot->overlay_sprite=65535u;pd_emit(result,PD_OVERLAY,0,65535u);
    }
    slot->type=slot->type->paired_type;pd_emit(result,PD_TYPE,0,(uint16_t)slot->type->id);result->next=PD_NEXT_WATER;
}
static void pd_board(PassengerDeliveryResult *result,PassengerStoneSlot *slot,const PassengerDeliveryWorld *world,size_t carrier) {
    slot->phase=ACTOR_CARRIED_PASSENGER;pd_emit(result,PD_PHASE,0,ACTOR_CARRIED_PASSENGER);
    pd_emit(result,PD_KIND,carrier,slot->type->carried_kind);
    pd_emit(result,PD_ICON,carrier,world->platforms[slot->destination_platform].destination_icon);
    slot->carrier=carrier;pd_emit(result,PD_CARRIER,0,(uint16_t)carrier);
    slot->sprite=65535u;pd_emit(result,PD_SPRITE,0,65535u);
    slot->quick_delivery_ticks=200;pd_emit(result,PD_QUICK,0,200);
    pd_emit(result,PD_OCCUPANT_CLEAR,slot->source_platform,65535u);
}
static void pd_finish(PassengerDeliveryResult *result,PassengerStoneSlot *slot,PassengerDeliveryWorld *world) {
    slot->position.y32=(uint16_t)((world->platforms[slot->destination_platform].surface_y-slot->type->geometry.anchor_y)*32u);pd_emit(result,PD_Y,0,slot->position.y32);
    slot->animation.byte_offset=65534u;pd_emit(result,PD_CURSOR,0,65534u);
    slot->animation.countdown=1;pd_emit(result,PD_TICK,0,1);
    world->hud_clear=1;pd_emit(result,PD_HUD_CLEAR,0,1);
}
PassengerDeliveryResult passenger_delivery_finish(PassengerStoneSlot *slot,PassengerDeliveryWorld *world) {
    PassengerDeliveryResult result={0};result.selected=-1;pd_finish(&result,slot,world);return result;
}
PassengerDeliveryResult passenger_delivery_apply(PassengerDeliveryEntry entry,PassengerStoneSlot *slot,
    const ActorRenderHistory *render,PassengerDeliveryWorld *world,size_t incoming_craft) {
    PassengerDeliveryResult result={0};result.selected=-1;int water=slot->type->id%2u!=0;
    switch(entry) {
    case PD_BEGIN_WAIT:
        pd_begin(&result,slot,ACTOR_PLATFORM_WAIT);slot->waiting_pose=65535u;pd_emit(&result,PD_POSE,0,65535u);
        slot->overlay_sprite=65535u;pd_emit(&result,PD_OVERLAY,0,65535u);break;
    case PD_BEGIN_DESTINATION: {
        pd_begin(&result,slot,water?ACTOR_FLOATING_DESTINATION_REQUEST:ACTOR_DESTINATION_REQUEST);
        uint16_t icon=(uint16_t)(slot->destination_platform+268u);if(icon>=274u) icon=273;
        slot->overlay_sprite=icon;pd_emit(&result,PD_OVERLAY,0,icon);
        slot->request_ticks=140;pd_emit(&result,PD_REQUEST,0,140);break;
    }
    case PD_BEGIN_QUESTION:
        pd_begin(&result,slot,water?ACTOR_FLOATING_QUESTION:ACTOR_QUESTION);
        slot->overlay_sprite=274;pd_emit(&result,PD_OVERLAY,0,274);
        slot->request_ticks=140;pd_emit(&result,PD_REQUEST,0,140);break;
    case PD_BEGIN_APPROACH:
        pd_begin(&result,slot,water?ACTOR_FLOATING_APPROACH:ACTOR_APPROACH);
        slot->overlay_sprite=65535u;pd_emit(&result,PD_OVERLAY,0,65535u);break;
    case PD_WAIT: {
        if(pd_submerged(slot,render,world)) {pd_water(&result,slot,world,1);break;}
        if(pd_tick(&result,slot)) {
            uint16_t center=(uint16_t)(render->pixel_x+slot->type->geometry.anchor_x);
            uint16_t target=world->platforms[slot->source_platform].waiting_x;
            if(center!=target) {
                slot->waiting_pose=0;pd_emit(&result,PD_POSE,0,0);
                int left=pd_signed(center)>pd_signed(target);
                if(!pd_frame(&result,slot,left?ACTOR_WALK_LEFT_ANIMATION:ACTOR_WALK_RIGHT_ANIMATION)) break;
                slot->position.x32=(uint16_t)(slot->position.x32+(left?65504u:32u));pd_emit(&result,PD_X,0,slot->position.x32);
            } else {
                uint16_t pose;if(!actor_alias_value(slot,ACTOR_ALIAS_WAITING_POSE,&pose)) {result.failed=1;break;}
                if(pose!=1) {slot->animation.byte_offset=0;pd_emit(&result,PD_CURSOR,0,0);}
                if(!pd_frame(&result,slot,ACTOR_IDLE_ANIMATION)) break;
                slot->waiting_pose=1;pd_emit(&result,PD_POSE,0,1);
            }
        }
        int contact=pd_contact(slot,world);
        if(contact>=0 && world->craft[contact].platform==65535u) {pd_water(&result,slot,world,0);break;}
        result.selected=pd_platform(slot,world,1);if(result.selected>=0) result.next=PD_NEXT_DESTINATION;break;
    }
    case PD_DESTINATION:case PD_QUESTION: {
        if(pd_submerged(slot,render,world)) {pd_water(&result,slot,world,1);break;}
        int contact=pd_contact(slot,world);
        if(contact>=0 && world->craft[contact].platform==65535u) {pd_water(&result,slot,world,0);break;}
        if(entry==PD_DESTINATION) {
            result.selected=pd_platform(slot,world,0);
            if(result.selected<0 || world->craft[result.selected].carried_kind) {result.next=PD_NEXT_QUESTION;break;}
        }
        if(pd_tick(&result,slot) && !pd_frame(&result,slot,ACTOR_REQUEST_ANIMATION)) break;
        uint16_t count;if(!actor_alias_value(slot,ACTOR_ALIAS_REQUEST_TICKS,&count)) {result.failed=1;break;}
        count=(uint16_t)(count-1u);slot->request_ticks=count;pd_emit(&result,PD_REQUEST,0,count);if(count) break;
        if(entry==PD_DESTINATION) result.next=PD_NEXT_APPROACH;
        else {result.selected=pd_platform(slot,world,1);result.next=result.selected>=0?PD_NEXT_DESTINATION:PD_NEXT_WAIT;}
        break;
    }
    case PD_APPROACH: {
        if(pd_submerged(slot,render,world)) {pd_water(&result,slot,world,1);break;}
        int contact=pd_contact(slot,world);
        if(contact>=0 && world->craft[contact].platform==65535u) {pd_water(&result,slot,world,0);break;}
        result.selected=pd_platform(slot,world,0);if(result.selected<0) {result.next=PD_NEXT_QUESTION;break;}
        int due=pd_tick(&result,slot);
        uint16_t center=(uint16_t)(render->pixel_x+slot->type->geometry.anchor_x-16u);
        uint16_t target=world->craft[result.selected].pixel_x;
        if(center==target) {result.next=PD_NEXT_BOARD;break;}
        int left=pd_signed(center)>pd_signed(target);
        if(!pd_frame(&result,slot,left?ACTOR_WALK_LEFT_ANIMATION:ACTOR_WALK_RIGHT_ANIMATION)) break;
        if(due) {slot->position.x32=(uint16_t)(slot->position.x32+(left?65504u:32u));pd_emit(&result,PD_X,0,slot->position.x32);}
        break;
    }
    case PD_RESCUE:case PD_BOARD: {
        /* DOS rescue reads fare/floor BEFORE changing to the land pair. */
        pd_emit(&result,PD_FARE,incoming_craft,slot->type->initial_fare);world->craft[incoming_craft].fare=slot->type->initial_fare;
        pd_emit(&result,PD_FLOOR,incoming_craft,slot->type->minimum_fare);world->craft[incoming_craft].minimum_fare=slot->type->minimum_fare;
        if(entry==PD_RESCUE) {
            if(!slot->type->paired_type) {result.failed=1;break;}
            slot->type=slot->type->paired_type;pd_emit(&result,PD_TYPE,0,(uint16_t)slot->type->id);
        }
        pd_board(&result,slot,world,incoming_craft);world->craft[incoming_craft].carried_kind=slot->type->carried_kind;
        world->craft[incoming_craft].destination_icon=world->platforms[slot->destination_platform].destination_icon;break;
    }
    case PD_CARRIED: {
        uint16_t carrier;if(!actor_alias_value(slot,ACTOR_ALIAS_CARRIER,&carrier)) {result.failed=1;break;}
        PassengerCraft *craft=&world->craft[carrier];
        if(craft->fare>craft->minimum_fare) {craft->fare--;pd_emit(&result,PD_FARE,carrier,craft->fare);}
        if(pd_signed(slot->quick_delivery_ticks)>0) {slot->quick_delivery_ticks--;pd_emit(&result,PD_QUICK,0,slot->quick_delivery_ticks);}
        if(slot->destination_platform==craft->platform) {result.selected=carrier;result.next=PD_NEXT_DELIVER;}
        break;
    }
    case PD_DELIVER: {
        uint16_t carrier;if(!actor_alias_value(slot,ACTOR_ALIAS_CARRIER,&carrier)) {result.failed=1;break;}
        slot->phase=ACTOR_WALK_TO_EXIT;pd_emit(&result,PD_PHASE,0,ACTOR_WALK_TO_EXIT);
        world->craft[incoming_craft].carried_kind=0;pd_emit(&result,PD_KIND,incoming_craft,0);
        world->craft[incoming_craft].destination_icon=0;pd_emit(&result,PD_ICON,incoming_craft,0);
        PassengerCraft *craft=&world->craft[carrier];
        slot->position.x32=(uint16_t)(craft->position.x32+(16u-slot->type->geometry.anchor_x)*32u);pd_emit(&result,PD_X,0,slot->position.x32);
        world->score+=(uint32_t)craft->fare*world->multiplier;
        pd_emit(&result,PD_SCORE_LOW,0,(uint16_t)world->score);pd_emit(&result,PD_SCORE_HIGH,0,(uint16_t)(world->score>>16));
        /* Signed-positive countdown updates, but ANY nonzero value qualifies
         * here. Negative stale quick words therefore still request a bonus. */
        if(slot->quick_delivery_ticks && world->multiplier<world->multiplier_limit) {
            result.spawn_bonus=result.bonus_sound=result.finish_pending=1;
            result.launch=(ObjectPosition){(uint16_t)(craft->position.x32+512u),(uint16_t)(craft->position.y32+320u)};
            break;
        }
        pd_finish(&result,slot,world);break;
    }
    }
    return result;
}
