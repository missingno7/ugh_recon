#include "passenger_itinerary.h"
static int32_t itinerary_signed(uint16_t value) {return value<32768u?(int32_t)value:(int32_t)value-65536;}
static uint16_t itinerary_sar(uint16_t value) {return (uint16_t)((value>>5)|((value&32768u)?63488u:0));}
static void itinerary_emit(ItineraryResult *result,ItineraryField field,size_t index,uint16_t value) {
    ItineraryWrite *write=&result->writes[result->count++];write->field=field;write->index=index;write->value=value;
}
static void itinerary_phase(ItineraryResult *result,PassengerStoneSlot *slot,ActorPhase phase) {
    slot->phase=phase;itinerary_emit(result,IT_PHASE,0,(uint16_t)phase);
}
static void itinerary_begin(ItineraryResult *result,PassengerStoneSlot *slot,ActorPhase phase) {
    itinerary_phase(result,slot,phase);slot->animation.byte_offset=65534u;slot->animation.countdown=1;
    itinerary_emit(result,IT_CURSOR,0,65534u);itinerary_emit(result,IT_COUNTDOWN,0,1);
}
static int itinerary_tick(ItineraryResult *result,PassengerStoneSlot *slot) {
    slot->animation.countdown--;itinerary_emit(result,IT_COUNTDOWN,0,slot->animation.countdown);
    if(slot->animation.countdown) return 0;
    slot->animation.countdown=slot->type->animation_period;
    itinerary_emit(result,IT_COUNTDOWN,0,slot->animation.countdown);
    slot->animation.byte_offset=(uint16_t)(slot->animation.byte_offset+2u);
    itinerary_emit(result,IT_CURSOR,0,slot->animation.byte_offset);return 1;
}
static int itinerary_frame(ItineraryResult *result,PassengerStoneSlot *slot,ActorAnimationKind kind,int loop) {
    const ActorAnimation *animation=&slot->type->animations[kind];
    size_t index=slot->animation.byte_offset/2u;
    if((slot->animation.byte_offset&1u) || index>animation->count || (loop && !animation->count)) {result->failed=1;return 0;}
    if(index==animation->count) {
        if(!loop) return 0;
        slot->animation.byte_offset=0;itinerary_emit(result,IT_CURSOR,0,0);index=0;
    }
    slot->sprite=animation->sprites[index];itinerary_emit(result,IT_SPRITE,0,slot->sprite);return 1;
}
ItineraryResult itinerary_apply(ItineraryEntry entry,PassengerStoneSlot *slot,ActorRenderHistory *render,ItineraryWorld *world) {
    ItineraryResult result={0};
    switch(entry) {
    case IT_IGNORE:break;
    case IT_READ: {
        const PassengerJourney *journey=slot->journey.journey;size_t leg=slot->journey.leg;
        if(!journey || leg>=journey->count) {result.failed=1;break;}
        if(leg+1==journey->count) {
            /* Retained DEC8 sign gate, including 128 -> 127 and 0 -> FF.
             * Completion is byte FE, not a boolean or a cleared word. */
            uint8_t remaining=(uint8_t)(world->remaining-1u);
            if(remaining<128u) {
                world->remaining=remaining;itinerary_emit(&result,IT_REMAINING,0,remaining);
                if(!remaining) {
                    world->fade_rate=65534u;itinerary_emit(&result,IT_FADE_RATE,0,world->fade_rate);
                    world->fade_level=(uint16_t)(world->fade_level+65534u);itinerary_emit(&result,IT_FADE_LEVEL,0,world->fade_level);
                    world->completion=254;itinerary_emit(&result,IT_COMPLETION,0,world->completion);
                }
            }
            slot->sprite=ACTOR_HIDDEN_SPRITE;itinerary_emit(&result,IT_SPRITE,0,slot->sprite);
            itinerary_phase(&result,slot,ACTOR_RETIRED);result.next=IT_NEXT_IGNORE;break;
        }
        slot->destination_platform=journey->legs[leg+1].platform;
        itinerary_emit(&result,IT_DESTINATION,0,slot->destination_platform);
        itinerary_emit(&result,IT_DESTINATION_INDEX,0,slot->destination_platform);
        slot->source_platform=journey->legs[leg].platform;
        itinerary_emit(&result,IT_SOURCE,0,slot->source_platform);itinerary_emit(&result,IT_SOURCE_INDEX,0,slot->source_platform);
        uint16_t delay=scale_level_speed(journey->legs[leg].wait).value;
        slot->journey_wait=delay; /* output for the next phase, never an input alias here */
        itinerary_emit(&result,IT_DELAY,0,delay);itinerary_phase(&result,slot,ACTOR_WAIT_FOR_PLATFORM);break;
    }
    case IT_WAIT: {
        uint16_t delay;
        if(!actor_alias_value(slot,ACTOR_ALIAS_JOURNEY_WAIT,&delay) || slot->source_platform>=world->platform_count) {result.failed=1;break;}
        slot->sprite=ACTOR_HIDDEN_SPRITE;itinerary_emit(&result,IT_SPRITE,0,slot->sprite);
        if(delay) {
            slot->journey_wait=(uint16_t)(delay-1u);itinerary_emit(&result,IT_DELAY,0,slot->journey_wait);
            if(slot->journey_wait) break;
        }
        if(world->uses[slot->source_platform].available) result.next=IT_NEXT_PLACE;
        break;
    }
    case IT_PLACE: {
        size_t source=slot->source_platform;
        if(source>=world->platform_count) {result.failed=1;break;}
        const LevelPlatform *platform=&world->platforms[source];
        itinerary_phase(&result,slot,ACTOR_ARRIVING);
        world->uses[source].available=0;world->uses[source].actor=world->actor;
        itinerary_emit(&result,IT_OCCUPANT,source,(uint16_t)world->actor);
        render->pixel_y=(uint16_t)(platform->surface_y-slot->type->geometry.anchor_y);
        itinerary_emit(&result,IT_PIXEL_Y,0,render->pixel_y);
        slot->position.y32=(uint16_t)(render->pixel_y*32u);itinerary_emit(&result,IT_Y,0,slot->position.y32);
        render->pixel_x=(uint16_t)(platform->arrival_x-slot->type->geometry.anchor_x);
        itinerary_emit(&result,IT_PIXEL_X,0,render->pixel_x);
        slot->position.x32=(uint16_t)(render->pixel_x*32u);itinerary_emit(&result,IT_X,0,slot->position.x32);
        slot->animation.byte_offset=65534u;slot->animation.countdown=1;
        itinerary_emit(&result,IT_CURSOR,0,65534u);itinerary_emit(&result,IT_COUNTDOWN,0,1);break;
    }
    case IT_ARRIVAL:
        if(itinerary_tick(&result,slot) && !itinerary_frame(&result,slot,ACTOR_ARRIVAL_ANIMATION,0) && !result.failed) result.next=IT_NEXT_PLATFORM_WAIT;
        break;
    case IT_WALK: {
        size_t destination=slot->destination_platform;
        if(destination>=world->platform_count) {result.failed=1;break;}
        if(!itinerary_tick(&result,slot)) break;
        uint16_t target=world->platforms[destination].arrival_x;
        /* Retained renderer-lag input: first compare the cached pixel, then
         * compare current SAR5 position only after actually moving. */
        uint16_t center=(uint16_t)(render->pixel_x+slot->type->geometry.anchor_x);
        if(center==target) {result.next=IT_NEXT_DEPARTURE;break;}
        int left=itinerary_signed(center)>itinerary_signed(target);
        if(!itinerary_frame(&result,slot,left?ACTOR_WALK_LEFT_ANIMATION:ACTOR_WALK_RIGHT_ANIMATION,1)) break;
        slot->position.x32=(uint16_t)(slot->position.x32+(left?65504u:32u));itinerary_emit(&result,IT_X,0,slot->position.x32);
        center=(uint16_t)(itinerary_sar(slot->position.x32)+slot->type->geometry.anchor_x);
        if(center==target) result.next=IT_NEXT_DEPARTURE;
        break;
    }
    case IT_BEGIN_DEPARTURE:itinerary_begin(&result,slot,ACTOR_DEPARTING);break;
    case IT_DEPARTURE:
        if(itinerary_tick(&result,slot)) {
            const ActorAnimation *animation=&slot->type->animations[ACTOR_DEPARTURE_ANIMATION];
            size_t index=slot->animation.byte_offset/2u;
            if((slot->animation.byte_offset&1u) || index>=animation->count) {result.failed=1;break;}
            /* Store current frame BEFORE testing the following sentinel. */
            slot->sprite=animation->sprites[index];itinerary_emit(&result,IT_SPRITE,0,slot->sprite);
            if(index+1==animation->count) {
                slot->journey.leg++;itinerary_emit(&result,IT_JOURNEY,0,(uint16_t)slot->journey.leg);result.next=IT_NEXT_READ;
            }
        }
        break;
    }
    return result;
}
