#ifndef NATIVE_ACTOR_RESOURCES_H
#define NATIVE_ACTOR_RESOURCES_H
#include "actors.h"
#include "level.h"
/* Semantic aliases are inputs only in the phases named by this table. */
typedef enum ActorAlias {
    ACTOR_ALIAS_WAITING_POSE=1, ACTOR_ALIAS_REQUEST_TICKS=2,
    ACTOR_ALIAS_CARRIER=4, ACTOR_ALIAS_JOURNEY_WAIT=8,
    ACTOR_ALIAS_HORIZONTAL_STEP=16, ACTOR_ALIAS_FLOATING_TICKS=32
} ActorAlias;
unsigned actor_phase_aliases(ActorPhase phase);
int actor_alias_value(const PassengerStoneSlot *slot, ActorAlias member, uint16_t *value);
ActorType actor_type_resource(ActorTypeId id, const uint8_t raw[74],
    const ActorAnimation animations[ACTOR_ANIMATION_COUNT], const ActorType *pair);
/* Instruction boundaries include the retained stop marker, never its end. */
int demo_script_boundary(const DemoMotionScript *script, size_t offset);
#endif
