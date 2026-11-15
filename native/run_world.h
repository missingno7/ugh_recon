#ifndef NATIVE_RUN_WORLD_H
#define NATIVE_RUN_WORLD_H
#include <stdint.h>

/* Resource identities are retained data words until the resource-registry cut.
 * They are never executable pointers or a second copy of their resources. */
typedef struct RunResourceIdentity {uint16_t value;} RunResourceIdentity;
typedef struct RunConfiguration {
 uint16_t players,player_bytes,control_mode[2],difficulty;
} RunConfiguration;
typedef struct LevelRuntimeRecord {
 RunResourceIdentity map,platforms,actors,enemies,introduction;
 uint8_t journeys,reserved_before_text,rain,reserved_tail;
 uint16_t player_start[2][2],water_fixed,water_step;
} LevelRuntimeRecord;
typedef struct NativeRunWorld {
 RunConfiguration configuration;
 LevelRuntimeRecord record;
 uint32_t score;
 uint16_t level,timer,fade_level,fade_step,water_y;
 uint8_t lives,multiplier,completion;
 uint8_t tiles[320];
} NativeRunWorld;
/* Exactly one resident store. Working subsystem views only borrow its values. */
NativeRunWorld *native_run_world(void);
#endif
