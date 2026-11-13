#ifndef NATIVE_PASSENGER_WATER_H
#define NATIVE_PASSENGER_WATER_H
#include "actor_resources.h"

typedef struct WaterCraft {
    uint16_t pixel_x,pixel_y,vertical_velocity,carried_kind;
} WaterCraft;
typedef struct PassengerWaterWorld {
    WaterCraft craft[2];size_t player_count,platform_count;
    uint16_t surface_y;
} PassengerWaterWorld;
typedef enum PassengerWaterEntry {
    PW_BEGIN_RESURFACE,PW_RESURFACE,PW_BEGIN_SINK,PW_SINK,
    PW_BEGIN_FLOAT,PW_FLOAT,PW_DESTINATION,PW_QUESTION,PW_APPROACH,PW_IGNORE
} PassengerWaterEntry;
typedef enum PassengerWaterNext {
    PW_NEXT_NONE,PW_NEXT_FLOAT,PW_NEXT_SINK,PW_NEXT_DESTINATION,
    PW_NEXT_QUESTION,PW_NEXT_APPROACH,PW_NEXT_BOARD
} PassengerWaterNext;
typedef enum PassengerWaterField {
    PW_PHASE,PW_CURSOR,PW_TICK,PW_OVERLAY,PW_VELOCITY,PW_Y,PW_SPRITE,
    PW_LIFETIME,PW_REQUEST,PW_X,PW_OCCUPANT_CLEAR
} PassengerWaterField;
typedef struct PassengerWaterWrite {
    PassengerWaterField field;size_t index;uint16_t value;
} PassengerWaterWrite;
typedef struct PassengerWaterResult {
    PassengerWaterWrite writes[32];size_t count;
    PassengerWaterNext next;int selected,failed;
} PassengerWaterResult;
/* Ordinary typed one-step view. Only the current phase's aliases are inputs.
 * The raw motion word and cached renderer pixels are deliberately retained.
 * Consume the journal before the requested immediate initializer/boarding tail. */
PassengerWaterResult passenger_water_apply(PassengerWaterEntry entry,
    PassengerStoneSlot *slot,const ActorRenderHistory *render,const PassengerWaterWorld *world);
#endif
