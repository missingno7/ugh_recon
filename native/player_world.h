#ifndef NATIVE_PLAYER_WORLD_H
#define NATIVE_PLAYER_WORLD_H
#include <stdint.h>
/* Raw 16-bit patterns retain signed arithmetic at the consuming operation.
 * Fixed positions are in 1/32 units. Simulation pixels and retained drawing
 * history are independent storage, never derived from fixed positions here. */
typedef struct NativePlayer {
 uint16_t up;
 uint16_t down;
 uint16_t left;
 uint16_t right;
 uint16_t action;
 uint16_t fixed_x;
 uint16_t fixed_y;
 uint16_t pixel_x;
 uint16_t pixel_y;
 uint16_t cached_x;
 uint16_t cached_y;
 uint16_t sprite;
 uint16_t cached_sprite;
 uint16_t animation;
 uint16_t thrust;
 uint16_t platform;
 uint16_t carried;
 uint16_t destination;
 uint16_t fare;
 uint16_t minimum_fare;
 uint16_t velocity_x;
 uint16_t velocity_y;
 uint16_t impact;
} NativePlayer;
typedef struct NativePlayerWorld {NativePlayer player[2];} NativePlayerWorld;
/* Both records exist even in one-player mode. */
NativePlayerWorld *native_player_world(void);
#endif
