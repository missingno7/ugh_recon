#ifndef NATIVE_ITEM_WORLD_H
#define NATIVE_ITEM_WORLD_H
#include <stdint.h>
/* Twelve physical item slots. Descriptor/callback identities remain raw
 * compatibility words; resource bytes are live views outside this owner.
 * Current simulation coordinates, current draw coordinates and previous erase
 * history are independent. Retirement retains all stale payload and history.
 * Motion and lifetime share exactly one word, overwritten only at landing. */
typedef struct NativeItemSlot {
 uint16_t descriptor_word;
 uint16_t callback_word;
 uint16_t sprite;
 uint16_t erase_sprite;
 uint16_t x32;
 uint16_t y32;
 uint16_t draw_x;
 uint16_t previous_x;
 uint16_t draw_y;
 uint16_t previous_y;
 uint16_t motion_or_lifetime;
 uint16_t vertical_step;
} NativeItemSlot;
typedef struct NativeItemWorld {NativeItemSlot slot[12];} NativeItemWorld;
NativeItemWorld *native_item_world(void);
#endif
