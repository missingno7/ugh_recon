#ifndef LEVEL_PROJECTION_H
#define LEVEL_PROJECTION_H
#include "ugh.h"
#include "../level.h"
typedef struct LevelProjectionStorage {
    uint8_t tiles[320];
    LevelPlatform platforms[10];
    LevelActorPlacement actors[16];
    LevelEnemyPlacement enemies[5];
} LevelProjectionStorage;
ObjectGeometry level_bridge_geometry(uint16_t segment, uint16_t descriptor, int item);
/* Project a source level record, with already decompressed map bank. Source
 * bytes stay untouched. Returns zero on malformed/capacity/unknown-type input;
 * storage may be partial then, and output view is not published. */
int level_bridge_project(uint16_t segment, uint16_t record,
    const uint8_t *map_bank, size_t map_size, LevelProjectionStorage *storage, LevelDescription *view);
#endif
