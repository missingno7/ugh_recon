#ifndef NATIVE_STONES_H
#define NATIVE_STONES_H
#include "actor_resources.h"
#include "contacts.h"
#include "level.h"
typedef struct StonePlayer {
    ObjectPosition position;
    uint16_t horizontal_velocity, vertical_velocity;
    uint16_t carried_kind, destination_icon, action_word;
} StonePlayer;
typedef enum StoneExit {
    STONE_STILL, STONE_PICKUP, STONE_RELEASE, STONE_OUT_LEFT,
    STONE_OUT_RIGHT, STONE_RISING, STONE_OUT_BOTTOM, STONE_LANDING
} StoneExit;
typedef struct StoneResult {
    StoneExit exit;
    size_t platform;
    ContactSelection contact;
} StoneResult;
void stone_begin_wait(PassengerStoneSlot *slot);
StoneResult stone_pickup_wait(PassengerStoneSlot *slot, const StonePlayer players[2], uint16_t player_count);
void stone_attach(PassengerStoneSlot *slot, StonePlayer players[2], size_t carrier);
int stone_release_requested(const PassengerStoneSlot *slot, const StonePlayer players[2]);
void stone_throw(PassengerStoneSlot *slot, StonePlayer players[2], size_t carrier);
/* Landing requests the immediate begin-wait action. The adapter applies it
 * after publishing position, preserving the original transition order. */
StoneResult stone_flight(PassengerStoneSlot *slot, const LevelPlatform *platforms, size_t count);
/* Borrow immediately before each query, in ascending physical slot order.
 * Hazard bounce writes must be returned to that same slot before another step. */
StoneContactView stone_contact_view(const PassengerStoneSlot *slot);
#endif
