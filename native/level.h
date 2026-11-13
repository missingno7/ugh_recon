#ifndef NATIVE_LEVEL_H
#define NATIVE_LEVEL_H
#include <stddef.h>
#include <stdint.h>
#include "geometry.h"
typedef struct LevelPlatform {
    /* Input +0/+2 signed pixel bounds; negative +0 terminates (G:3A6D..3A7B). */
    uint16_t left, right;
    /* Input +4 after y-SAR(y,2), G:3A80/3A83; landing surface in pixels. */
    uint16_t surface_y;
    /* Input +6/+8/+A, copied to arrival/wait/spawn arrays, G:3A88/3A8D/3A92. */
    uint16_t arrival_x, waiting_x, spawn_x;
    /* Input +C: HUD destination icon/type, G:3A97, not a terrain/material enum. */
    uint16_t destination_icon;
    /* Input +E is skipped, G:3A9B. No meaning assigned. */
    uint16_t reserved_raw;
} LevelPlatform;
typedef struct LevelActorPlacement {
    ObjectGeometry geometry; /* referenced descriptor +0..6 */
    uint16_t initial_platform; /* placement +2, G:3ABF */
    uint8_t tail_raw[2]; /* +4 itinerary reference or stone-specific word, unprojected */
} LevelActorPlacement;
typedef enum LevelEnemyKind { LEVEL_BIRD, LEVEL_TRIOPTERUS, LEVEL_DINO, LEVEL_TREE } LevelEnemyKind;
typedef struct LevelEnemyPlacement {
    LevelEnemyKind kind; /* descriptor identity, classified only by bridge */
    ObjectGeometry geometry; /* referenced descriptor +0..6 */
    /* Entire original placement, including skipped +2 bird/+4 Triopterus/
     * +6,+8 Dino words. No native pointers or invented skipped-field meanings. */
    uint8_t raw[10];
    size_t raw_size;
} LevelEnemyPlacement;
typedef struct LevelDescription {
    /* Exact 26-byte input retained, including reserved +09/+19 and unresolved
     * reference encodings. It is evidence, never dereferenced by native code. */
    uint8_t raw[26];
    uint8_t objectives; /* +08, copied at G:3976; completion mutates another copy */
    uint8_t weather; /* +0C, G:3C16/3C50 */
    ObjectPosition player_starts[2]; /* +0D/+0F,+11/+13, before loader corrections */
    uint16_t water_y32, water_increment; /* +15/+17, before aspect conversion */
    const uint8_t *tiles; /* resolved immutable map, 20 columns x16 rows, G:4172 */
    const LevelPlatform *platforms;
    size_t platform_count;
    const LevelActorPlacement *actors;
    size_t actor_count;
    const LevelEnemyPlacement *enemies;
    size_t enemy_count;
} LevelDescription;
/* Ordinary little-endian resource decoding; accessible initialized inputs,
 * separate output storage. No machine state, allocation, callbacks or writes
 * to input data. Pointers in the description borrow caller-owned storage. */
ObjectGeometry level_object_geometry(const uint8_t raw[8]);
ObjectGeometry level_item_geometry(const uint8_t raw[4]);
LevelPlatform level_platform(const uint8_t raw[16]);
LevelDescription level_description(const uint8_t raw[26], const uint8_t tiles[320],
    const LevelPlatform *platforms, size_t platform_count,
    const LevelActorPlacement *actors, size_t actor_count,
    const LevelEnemyPlacement *enemies, size_t enemy_count);
#endif
