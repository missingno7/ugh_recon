/* Shared actor vocabulary, adopted by the close-demo work order.
 * See docs/actor-storage.md for domains, projections and write-back rules.
 * This is a game-specific view, not the DOS storage layout or a new API mandate.
 */
#ifndef NATIVE_ACTORS_H
#define NATIVE_ACTORS_H
#include <stddef.h>
#include <stdint.h>
#include "geometry.h"

enum { ACTOR_CAPACITY = 16 };
enum { ACTOR_HIDDEN_SPRITE = UINT16_MAX, DEMO_HIDDEN_SPRITE = 0x7fff };

/* Resource identities matter: the primary stone alone participates in the
 * thrown-stone hazard query. The alternate stone is retained as a distinct
 * descriptor identity, although shipped level placements do not select it.
 */
typedef enum ActorTypeId {
    ACTOR_PASSENGER_ONE_LAND, ACTOR_PASSENGER_ONE_WATER,
    ACTOR_PASSENGER_TWO_LAND, ACTOR_PASSENGER_TWO_WATER,
    ACTOR_PASSENGER_THREE_LAND, ACTOR_PASSENGER_THREE_WATER,
    ACTOR_STONE, ACTOR_STONE_ALTERNATE
} ActorTypeId;
typedef enum ActorAnimationKind {
    ACTOR_IDLE_ANIMATION, ACTOR_REQUEST_ANIMATION,
    ACTOR_WALK_LEFT_ANIMATION, ACTOR_WALK_RIGHT_ANIMATION,
    ACTOR_ARRIVAL_ANIMATION, ACTOR_DEPARTURE_ANIMATION,
    ACTOR_ANIMATION_COUNT
} ActorAnimationKind;
typedef struct ActorAnimation {
    /* Resource adapter removes the terminal word, not any live sprite IDs. */
    const uint16_t *sprites;
    size_t count;
} ActorAnimation;
typedef struct ActorType {
    ActorTypeId id;
    ObjectGeometry geometry;
    ActorAnimation animations[ACTOR_ANIMATION_COUNT];
    uint16_t animation_period, initial_fare, minimum_fare, floating_lifetime;
    uint16_t carried_kind;
    const struct ActorType *paired_type;
} ActorType;

typedef struct PassengerJourneyLeg {
    uint16_t platform, wait; /* resource wait before three-halves scaling */
} PassengerJourneyLeg;
typedef struct PassengerJourney {
    const PassengerJourneyLeg *legs;
    size_t count; /* excludes the terminal platform marker */
} PassengerJourney;
typedef struct PassengerJourneyCursor {
    const PassengerJourney *journey;
    size_t leg; /* current leg; next leg gives the destination */
} PassengerJourneyCursor;

/* Persistent update phases; initializer/transition actions run immediately.
 * The stone initializer can also be stored by the original level loader.
 * There is no separate phase for an exhausted water descriptor's unused tail.
 */
typedef enum ActorPhase {
    ACTOR_READ_JOURNEY, ACTOR_WAIT_FOR_PLATFORM, ACTOR_ARRIVING,
    ACTOR_PLATFORM_WAIT, ACTOR_DESTINATION_REQUEST, ACTOR_QUESTION,
    ACTOR_APPROACH, ACTOR_CARRIED_PASSENGER, ACTOR_WALK_TO_EXIT,
    ACTOR_DEPARTING, ACTOR_RETIRED,
    ACTOR_BEGIN_STONE_WAIT, ACTOR_STONE_WAIT, ACTOR_CARRIED_STONE,
    ACTOR_THROWN_STONE, ACTOR_RESURFACING, ACTOR_SINKING,
    ACTOR_FLOATING, ACTOR_FLOATING_DESTINATION_REQUEST,
    ACTOR_FLOATING_QUESTION, ACTOR_FLOATING_APPROACH, ACTOR_PHASE_COUNT
} ActorPhase;
typedef struct ActorAnimationState {
    /* Retain the wrapping word offset and predecrement countdown, including
     * the offset seed and zero-period wrap. Do not normalize to a host timer.
     */
    uint16_t byte_offset, countdown;
} ActorAnimationState;
typedef struct PassengerStoneSlot {
    const ActorType *type;
    ActorPhase phase;
    PassengerJourneyCursor journey; /* unused for stone */
    uint16_t source_platform, destination_platform;
    ObjectPosition position;
    uint16_t sprite, overlay_sprite; /* simulation outputs, renderer inputs */
    ActorAnimationState animation;

    /* Semantic aliases of one retained cell. Read with actor_alias_value (or
     * the bridge's checked accessor); only the active phase's member
     * is an input. A transition writes its selected member explicitly.
     * The bridge publishes actual cell effects, never all aliases in order.
     */
    uint16_t waiting_pose; /* unset, walking, or standing; word patterns */
    uint16_t request_ticks;
    size_t carrier; /* player number, not a DOS byte index */
    /* Semantic aliases of another retained cell, with the same write rule. */
    uint16_t journey_wait, horizontal_step, floating_ticks;
    /* Direct step for a thrown stone, raw /64 motion term in water states. */
    uint16_t vertical_motion;
    uint16_t quick_delivery_ticks;
} PassengerStoneSlot;
typedef struct GameplayActors {
    size_t count;
    PassengerStoneSlot slots[ACTOR_CAPACITY];
} GameplayActors;

typedef enum DemoMotionEffect {
    DEMO_EFFECT_NONE, DEMO_EFFECT_FADE_ON_HIDDEN, DEMO_EFFECT_REVEAL_WIDTH
} DemoMotionEffect;
typedef struct DemoMotionScript {
    uint16_t initial_pixel_x, initial_pixel_y, period;
    DemoMotionEffect effect;
    const uint8_t *code;
    size_t code_size;
} DemoMotionScript;
typedef struct DemoMotionSlot {
    const DemoMotionScript *script;
    size_t cursor; /* byte offset in code; stop marker remains the cursor */
    size_t repeat_start; /* meaningful only when repeat_count is nonzero */
    uint16_t repeat_count, countdown; /* retain wrapping word operations */
    int finished; /* sticky completion; does not disable later countdowns */
    ObjectPosition position;
    uint16_t sprite;
} DemoMotionSlot;
typedef struct DemoMotionScene {
    size_t count;
    DemoMotionSlot slots[ACTOR_CAPACITY];
} DemoMotionScene;

/* One persistent instance for the physical slots across scene changes.
 * Pixel fields can be stale and are read by passenger logic; they are not
 * derived on projection. Scene/placement initialization has explicit writes.
 * Erase history is not reset just because a native view changes mode.
 */
typedef struct ActorRenderHistory {
    uint16_t pixel_x, pixel_y;
    uint16_t previous_x, previous_y;
    uint16_t erase_sprite, erase_overlay_sprite;
} ActorRenderHistory;
typedef struct ActorRenderStorage {
    ActorRenderHistory slots[ACTOR_CAPACITY];
} ActorRenderStorage;

/* Narrow interfaces live in actor_resources.h and demo_core.h.
 * A bridge accepts a valid active prefix with a separate in-range sentinel;
 * a full sixteen actors cannot be round-tripped to the DOS arrays that way.
 */
#endif
