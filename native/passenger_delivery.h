#ifndef NATIVE_PASSENGER_DELIVERY_H
#define NATIVE_PASSENGER_DELIVERY_H
#include "actor_resources.h"
#include "contacts.h"
#include "level.h"
typedef enum PassengerDeliveryEntry {
    PD_BEGIN_WAIT,PD_WAIT,PD_BEGIN_DESTINATION,PD_DESTINATION,
    PD_BEGIN_QUESTION,PD_QUESTION,PD_BEGIN_APPROACH,PD_APPROACH,
    PD_RESCUE,PD_BOARD,PD_CARRIED,PD_DELIVER
} PassengerDeliveryEntry;
typedef struct PassengerCraft {
    ObjectPosition position;
    uint16_t pixel_x,platform,carried_kind,destination_icon,fare,minimum_fare;
} PassengerCraft;
typedef struct PassengerDeliveryWorld {
    PassengerCraft craft[2];uint16_t player_count;
    size_t player_slots; /* one or two, independent contact retry rule retained */
    const LevelPlatform *platforms;size_t platform_count;
    uint16_t water_pixel_y,multiplier,multiplier_limit;
    uint32_t score;uint8_t hud_clear;
} PassengerDeliveryWorld;
typedef enum PassengerDeliveryNext {
    PD_NEXT_NONE,PD_NEXT_WAIT,PD_NEXT_DESTINATION,PD_NEXT_QUESTION,
    PD_NEXT_APPROACH,PD_NEXT_BOARD,PD_NEXT_DELIVER,PD_NEXT_WATER
} PassengerDeliveryNext;
typedef enum PassengerDeliveryField {
    PD_PHASE,PD_TYPE,PD_CURSOR,PD_TICK,PD_POSE,PD_REQUEST,PD_CARRIER,
    PD_SPRITE,PD_OVERLAY,PD_X,PD_Y,PD_QUICK,PD_OCCUPANT_CLEAR,
    PD_FARE,PD_FLOOR,PD_KIND,PD_ICON,PD_SCORE_LOW,PD_SCORE_HIGH,PD_HUD_CLEAR
} PassengerDeliveryField;
typedef struct PassengerDeliveryWrite {
    PassengerDeliveryField field;size_t index;uint16_t value;
} PassengerDeliveryWrite;
typedef struct PassengerDeliveryResult {
    PassengerDeliveryWrite writes[32];size_t count;
    PassengerDeliveryNext next;int selected,failed;
    int spawn_bonus,bonus_sound,finish_pending;ObjectPosition launch;
} PassengerDeliveryResult;
/* Immutable, nonempty live animation resources with explicit terminal count;
 * caller applies immediate tails after consuming outputs. Only the active
 * phase's aliases are inputs. Incoming craft is separately live at boarding
 * and delivery; delivery also uses the stored carrier, deliberately. */
PassengerDeliveryResult passenger_delivery_apply(PassengerDeliveryEntry entry,
    PassengerStoneSlot *slot,const ActorRenderHistory *render,
    PassengerDeliveryWorld *world,size_t incoming_craft);
/* Bonus delivery stops after score publication. Apply item allocation and audio
 * through their existing APIs, then continue ONLY on normal completion. A full
 * pool leaves Y/animation/HUD unchanged even in the native working state. */
PassengerDeliveryResult passenger_delivery_finish(PassengerStoneSlot *slot,PassengerDeliveryWorld *world);
#endif
