#ifndef ACTOR_PROJECTION_H
#define ACTOR_PROJECTION_H
#include "level_projection.h"
#include "../actor_resources.h"
enum { ACTOR_TYPE_COUNT=8, ACTOR_RESOURCE_LIMIT=256, DEMO_SCRIPT_COUNT=28,
       DEMO_CODE_LIMIT=2048 };
typedef struct ActorResourceStorage {
    ActorType types[ACTOR_TYPE_COUNT];
    uint16_t animation_words[ACTOR_TYPE_COUNT][ACTOR_ANIMATION_COUNT][ACTOR_RESOURCE_LIMIT];
} ActorResourceStorage;
typedef struct ActorLevelEntry {
    const ActorType *type;
    uint16_t initial_platform;
    PassengerJourney journey; /* empty for stones; raw tail stays in level view */
} ActorLevelEntry;
typedef struct ActorLevelStorage {
    ActorLevelEntry entries[ACTOR_CAPACITY];
    PassengerJourneyLeg legs[ACTOR_CAPACITY][ACTOR_RESOURCE_LIMIT];
} ActorLevelStorage;
typedef struct DemoResourceStorage {
    DemoMotionScript scripts[DEMO_SCRIPT_COUNT];
    uint16_t headers[DEMO_SCRIPT_COUNT];
    uint8_t code[DEMO_SCRIPT_COUNT][DEMO_CODE_LIMIT];
    size_t count;
} DemoResourceStorage;
int actor_bridge_resources(uint16_t segment,ActorResourceStorage *storage);
const ActorType *actor_bridge_type(const ActorResourceStorage *storage,uint16_t identity);
int actor_bridge_level(uint16_t segment,uint16_t record,const LevelDescription *level,
    const ActorResourceStorage *resources,ActorLevelStorage *storage);
int actor_bridge_journey(uint16_t segment,uint16_t base,PassengerJourneyLeg *legs,PassengerJourney *journey);
int actor_bridge_scripts(uint16_t segment,DemoResourceStorage *storage);
int actor_bridge_script_cursor(const DemoResourceStorage *storage,uint16_t cursor,size_t *script,size_t *offset);
int actor_bridge_demo_project(uint16_t segment,const DemoResourceStorage *resources,DemoMotionScene *scene);
void actor_bridge_render_project(uint16_t segment,ActorRenderStorage *render);
/* Source phase determines the valid members. Invalid members are poisoned in
 * debug/verification builds. All reads through actor_alias_value reject an
 * inactive alias in every build, before accessing the member. */
int actor_bridge_alias_project(uint16_t segment,size_t index,ActorPhase phase,PassengerStoneSlot *slot);
int actor_bridge_alias_read(const PassengerStoneSlot *slot,ActorAlias member,uint16_t *value);
#endif
