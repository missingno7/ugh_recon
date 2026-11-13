#include "actor_resources.h"
unsigned actor_phase_aliases(ActorPhase phase) {
    static const unsigned valid[ACTOR_PHASE_COUNT]={
        0, ACTOR_ALIAS_JOURNEY_WAIT, 0, ACTOR_ALIAS_WAITING_POSE,
        ACTOR_ALIAS_REQUEST_TICKS, ACTOR_ALIAS_REQUEST_TICKS, 0,
        ACTOR_ALIAS_CARRIER, 0, 0, 0, 0, 0, ACTOR_ALIAS_CARRIER,
        ACTOR_ALIAS_HORIZONTAL_STEP, 0, 0, ACTOR_ALIAS_FLOATING_TICKS,
        ACTOR_ALIAS_REQUEST_TICKS, ACTOR_ALIAS_REQUEST_TICKS, 0
    };
    return (unsigned)phase<ACTOR_PHASE_COUNT ? valid[phase] : 0;
}
int actor_alias_value(const PassengerStoneSlot *slot, ActorAlias member, uint16_t *value) {
    if(!(actor_phase_aliases(slot->phase)&(unsigned)member)) return 0;
    switch(member) {
    case ACTOR_ALIAS_WAITING_POSE: *value=slot->waiting_pose; break;
    case ACTOR_ALIAS_REQUEST_TICKS: *value=slot->request_ticks; break;
    case ACTOR_ALIAS_CARRIER: *value=(uint16_t)slot->carrier; break;
    case ACTOR_ALIAS_JOURNEY_WAIT: *value=slot->journey_wait; break;
    case ACTOR_ALIAS_HORIZONTAL_STEP: *value=slot->horizontal_step; break;
    case ACTOR_ALIAS_FLOATING_TICKS: *value=slot->floating_ticks; break;
    default: return 0;
    }
    return 1;
}
static uint16_t actor_resource_word(const uint8_t *p) {
    return (uint16_t)(p[0]+256u*p[1]);
}
ActorType actor_type_resource(ActorTypeId id,const uint8_t raw[74],
    const ActorAnimation animations[ACTOR_ANIMATION_COUNT],const ActorType *pair) {
    ActorType type;
    type.id=id; type.geometry=level_object_geometry(raw);
    for(size_t i=0;i<ACTOR_ANIMATION_COUNT;i++) type.animations[i]=animations[i];
    /* The two intervening scalar words have no established actor consumer. */
    type.animation_period=actor_resource_word(raw+62);
    type.initial_fare=actor_resource_word(raw+64);
    type.minimum_fare=actor_resource_word(raw+66);
    type.floating_lifetime=actor_resource_word(raw+68);
    type.carried_kind=actor_resource_word(raw+70); type.paired_type=pair;
    return type;
}
int demo_script_boundary(const DemoMotionScript *script,size_t offset) {
    size_t p=0;
    while(p<script->code_size && script->code_size-p>=2) {
        if(p==offset) return 1;
        uint16_t op=actor_resource_word(script->code+p);
        p+=op<32768u ? 4 : 2;
    }
    return 0;
}
