#ifndef NATIVE_ENEMY_WORLD_H
#define NATIVE_ENEMY_WORLD_H
#include <stdint.h>
/* Exactly five physical slots. Descriptor, callback, list and sound-handle
 * words are retained compatibility data, not registry tokens. Signed arithmetic
 * and the direction/target alias are interpreted only by their live consumers.
 * Long raw indexed views retain their physical aliases; there is no sixth slot. */
typedef struct NativeEnemySlot {
 uint16_t descriptor_word;
 uint16_t platform;
 uint16_t x32;
 uint16_t y32;
 uint16_t animation_or_drop_word;
 uint16_t initial_delay;
 uint16_t speed;
 uint16_t callback_word;
 uint16_t counter;
 uint16_t draw_x;
 uint16_t previous_x;
 uint16_t draw_y;
 uint16_t previous_y;
 uint16_t animation_offset;
 uint16_t countdown;
 uint16_t sprite;
 uint16_t erase_sprite;
 uint16_t direction_or_target_word;
 uint16_t sound_handle_word;
} NativeEnemySlot;
typedef struct NativeEnemyWorld {NativeEnemySlot slot[5];} NativeEnemyWorld;
NativeEnemyWorld *native_enemy_world(void);
#endif
