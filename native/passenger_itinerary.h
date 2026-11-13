#ifndef NATIVE_PASSENGER_ITINERARY_H
#define NATIVE_PASSENGER_ITINERARY_H
#include "actor_resources.h"
#include "coordinate_scale.h"
#include "level.h"
typedef enum ItineraryEntry {
    IT_READ, IT_WAIT, IT_PLACE, IT_ARRIVAL, IT_WALK,
    IT_BEGIN_DEPARTURE, IT_DEPARTURE, IT_IGNORE
} ItineraryEntry;
typedef enum ItineraryNext {
    IT_NEXT_NONE, IT_NEXT_PLACE, IT_NEXT_PLATFORM_WAIT,
    IT_NEXT_DEPARTURE, IT_NEXT_READ, IT_NEXT_IGNORE
} ItineraryNext;
/* Only availability is an input. Actor identity is an output of a claim;
 * this narrow borrow does not decode arbitrary occupied-owner words. */
typedef struct ItineraryPlatformUse { int available; size_t actor; } ItineraryPlatformUse;
typedef struct ItineraryWorld {
    const LevelPlatform *platforms;
    ItineraryPlatformUse *uses;
    size_t platform_count, actor;
    uint8_t remaining, completion;
    uint16_t fade_rate, fade_level;
} ItineraryWorld;
/* Ordered outputs retain intermediate countdown/sprite writes before a tail.
 * Field identities and indices are semantic, never addresses or byte indices. */
typedef enum ItineraryField {
    IT_PHASE, IT_SOURCE, IT_DESTINATION, IT_SOURCE_INDEX, IT_DESTINATION_INDEX,
    IT_DELAY, IT_X, IT_Y, IT_PIXEL_X, IT_PIXEL_Y, IT_CURSOR, IT_COUNTDOWN,
    IT_SPRITE, IT_JOURNEY, IT_OCCUPANT, IT_REMAINING, IT_COMPLETION,
    IT_FADE_RATE, IT_FADE_LEVEL
} ItineraryField;
typedef struct ItineraryWrite { ItineraryField field; size_t index; uint16_t value; } ItineraryWrite;
typedef struct ItineraryResult {
    ItineraryWrite writes[16];size_t count;
    ItineraryNext next;
    int failed;
} ItineraryResult;
/* Contract resources have at most 256 entries and actor identity is below 16.
 * Valid finite resource cursors and platform indices; arbitrary scalar words,
 * including zero timers. Failure is private partial output, not publication.
 * A completing departure has a following journey leg to advance into.
 * Immediate tails are applied by the caller after consuming these outputs. */
ItineraryResult itinerary_apply(ItineraryEntry entry,PassengerStoneSlot *slot,
    ActorRenderHistory *render,ItineraryWorld *world);
#endif
