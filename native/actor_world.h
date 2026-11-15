#ifndef NATIVE_ACTOR_WORLD_H
#define NATIVE_ACTOR_WORLD_H
#include "actors.h"
/* One physical lifetime, including inactive aliases. These retained identity
 * words are compatibility data, never native dispatch targets. Existing checked
 * adapters decode gameplay phases and demo roles. A later identity/continuation
 * cut replaces their transport; it must not add phase aliases or reset history. */
typedef struct NativeActorSlot {
 uint16_t descriptor_word,initial_platform,journey_word,update_or_script_word;
 uint16_t phase_or_loop_word,source_or_done,destination_platform;
 uint16_t source_byte_index,destination_byte_index,delay_or_repeat_word;
 ObjectPosition position;
 ActorRenderHistory history;
 ActorAnimationState animation;
 uint16_t sprite,overlay_or_effect_word,motion_or_period_word,quick_delivery_ticks;
} NativeActorSlot;
typedef struct NativeActorWorld {NativeActorSlot slot[ACTOR_CAPACITY];} NativeActorWorld;
NativeActorWorld *native_actor_world(void);
#endif
