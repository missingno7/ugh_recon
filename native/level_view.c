#include "level.h"
static uint16_t resource_word(const uint8_t *p) {
    return (uint16_t)(p[0]+(uint16_t)p[1]*256u);
}
ObjectGeometry level_object_geometry(const uint8_t raw[8]) {
    ObjectGeometry result={resource_word(raw),resource_word(raw+2),
        resource_word(raw+4),resource_word(raw+6)};
    return result;
}
ObjectGeometry level_item_geometry(const uint8_t raw[4]) {
    ObjectGeometry result={resource_word(raw),resource_word(raw+2),3,3};
    return result;
}
LevelPlatform level_platform(const uint8_t raw[16]) {
    uint16_t y=resource_word(raw+4);
    /* Retained arithmetic-right-shift rounding, including negative odd words. */
    uint16_t quarter=(uint16_t)((y>>2)|((y&32768u)?49152u:0u));
    LevelPlatform result={resource_word(raw),resource_word(raw+2),(uint16_t)(y-quarter),
        resource_word(raw+6),resource_word(raw+8),resource_word(raw+10),
        resource_word(raw+12),resource_word(raw+14)};
    return result;
}
LevelDescription level_description(const uint8_t raw[26], const uint8_t tiles[320],
    const LevelPlatform *platforms, size_t platform_count,
    const LevelActorPlacement *actors, size_t actor_count,
    const LevelEnemyPlacement *enemies, size_t enemy_count) {
    LevelDescription result;
    for(size_t i=0;i<26;i++) result.raw[i]=raw[i];
    result.objectives=raw[8]; result.weather=raw[12];
    result.player_starts[0]=(ObjectPosition){resource_word(raw+13),resource_word(raw+15)};
    result.player_starts[1]=(ObjectPosition){resource_word(raw+17),resource_word(raw+19)};
    result.water_y32=resource_word(raw+21); result.water_increment=resource_word(raw+23);
    result.tiles=tiles; result.platforms=platforms; result.platform_count=platform_count;
    result.actors=actors; result.actor_count=actor_count;
    result.enemies=enemies; result.enemy_count=enemy_count;
    return result;
}
