#ifndef NATIVE_GAME_DEMO_H
#define NATIVE_GAME_DEMO_H
#include "object_identities.h"
#include "enemy_world.h"
#include "item_world.h"
#include "presentation_world.h"
/* Production actors retain one physical history across gameplay/demo modes.
 * Cursor cells are offsets inside their typed data resource, never code words. */
typedef struct GameActorSlot {
    ObjectResourceIdentity descriptor,journey,script,loop_script;
    ObjectCallbackIdentity callback;
    uint16_t cursor,loop_cursor,initial_platform,source_or_done,destination_platform;
    uint16_t source_byte_index,destination_byte_index,delay_or_repeat_word;
    ObjectPosition position;
    ActorRenderHistory history;
    ActorAnimationState animation;
    uint16_t sprite,overlay_sprite,motion_or_period_word,quick_delivery_ticks;
    uint8_t demo;
} GameActorSlot;
typedef struct GameActorWorld {GameActorSlot slot[ACTOR_CAPACITY];} GameActorWorld;
enum { GAME_DEMO_SCRIPTS=28,GAME_DEMO_RESOURCE_BYTES=8192 };
typedef struct GameDemoResource {
    ObjectResourceIdentity identity;
    ObjectCallbackIdentity callback;
    size_t offset,size;
} GameDemoResource;
typedef struct GameDemoResources {
    GameDemoResource scripts[GAME_DEMO_SCRIPTS];
    uint8_t bytes[GAME_DEMO_RESOURCE_BYTES];
    uint8_t row_stride,ready;
} GameDemoResources;
#endif
