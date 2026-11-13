#ifndef NATIVE_HAZARDS_H
#define NATIVE_HAZARDS_H
#include "contacts.h"
#include "level.h"

enum { HAZARD_CAPACITY = 5, HAZARD_WRITE_CAPACITY = 16 };
/* Entries include initializers and the nominal, normally bypassed impact
 * handler. ZERO and IGNORE remain distinct, explicit descriptor targets. */
typedef enum HazardEntry {
    H_ZERO, H_IGNORE, H_BIRD_DELAY, H_BIRD_WAIT, H_BIRD_WARNING,
    H_BIRD_WARN_WAIT, H_BIRD_LAUNCH, H_BIRD_FLIGHT, H_BIRD_STUN,
    H_BIRD_FALL, H_BIRD_STOP,
    H_TRIO_PATROL_BEGIN, H_TRIO_PATROL, H_TRIO_ALERT_BEGIN, H_TRIO_ALERT,
    H_TRIO_CHARGE_BEGIN, H_TRIO_CHARGE, H_TRIO_RECOVER_BEGIN, H_TRIO_RECOVER,
    H_TRIO_IMPACT_BEGIN, H_TRIO_IMPACT, H_TRIO_STUN, H_TRIO_STUNNED,
    H_DINO_BEGIN, H_DINO_FORCE, H_DINO_STUN, H_DINO_STUNNED,
    H_TREE_BEGIN, H_TREE_ANIMATE, H_TREE_RELEASE, H_TREE_COOLDOWN, H_TREE_EMPTY
} HazardEntry;

/* A borrowed animation window at the incoming cursor. Sampling immutable
 * resources belongs to the projection; stepping/resetting the cursor belongs
 * to hazards. This admits every cursor word, including odd/wrapped cursors. */
typedef struct HazardAnimation { uint16_t first, next; } HazardAnimation;
typedef struct HazardType {
    ObjectGeometry geometry;
    HazardEntry handlers[13];
    HazardAnimation animations[12];
    HazardAnimation flight;
    uint16_t score;
    int rewards_exhausted;
} HazardType;
typedef enum HazardFlightSide { H_FLIGHT_LEFT, H_FLIGHT_RIGHT, H_FLIGHT_UNSELECTED } HazardFlightSide;

/* Defined once for all four species. Rendering owns the cache words; hazards
 * only writes draw_x/draw_y in the tree initializer (retained DOS SHL bug). */
typedef struct HazardSlot {
    HazardEntry state;
    ObjectPosition position;
    uint16_t platform, initial_delay, speed, counter, animation_cursor;
    uint16_t animation_countdown, sprite, direction, flight_sound;
    uint16_t draw_x, draw_y;
    /* Phase-specific resource identity. The resource provider samples the flight
     * vector selected by flight_side, or the reward at reward_cursor. */
    HazardFlightSide flight_side;
    uint16_t reward_cursor;
} HazardSlot;
typedef struct HazardPlayer {
    ObjectPosition position;
    uint16_t platform, horizontal_velocity, vertical_velocity;
} HazardPlayer;
typedef struct HazardStone {
    StoneContactView contact;
    uint16_t horizontal_step, sprite;
} HazardStone;
typedef struct HazardWorld {
    HazardPlayer players[2];
    HazardStone stones[16];
    size_t stone_count;
    uint16_t player_count, player_slots, water_y32, fade_step, fade_level;
    uint32_t score;
    const LevelPlatform *platforms;
    size_t platform_count;
} HazardWorld;

/* Ordered semantic stores let the temporary bridge reconstruct the complete
 * deterministic register/flag shell without making machine arithmetic the
 * authority for persistent state. No code/data addresses occur in this log. */
typedef enum HazardField {
    HW_STATE, HW_X, HW_Y, HW_SPEED, HW_COUNTER, HW_CURSOR, HW_TICK, HW_SPRITE,
    HW_DIRECTION, HW_DRAW_X, HW_DRAW_Y, HW_LIST, HW_SCORE_LOW, HW_SCORE_HIGH,
    HW_FADE_STEP, HW_FADE_LEVEL, HW_STONE_VERTICAL, HW_STONE_SPRITE,
    HW_PLAYER_Y, HW_PLAYER_HORIZONTAL, HW_PLAYER_VERTICAL, HW_PLAYER_PLATFORM
} HazardField;
typedef struct HazardWrite { HazardField field; uint16_t index, value; } HazardWrite;
typedef enum HazardAudio { HA_NONE, HA_WARNING, HA_FLIGHT, HA_DINO, HA_REWARD, HA_STOP } HazardAudio;
typedef struct HazardResult {
    HazardWrite writes[16];
    size_t count;
    HazardEntry tail;
    int has_tail;
    HazardAudio audio;
    uint16_t audio_handle; /* stop request; flight start supplies a handle later */
    int spawn_item;
    uint16_t spawn_reward; /* reward-list ordinal before advancement */
    ObjectPosition launch;
    uint16_t launch_horizontal, launch_term;
} HazardResult;

HazardResult hazard_step(HazardEntry entry, HazardSlot *slot,
    const HazardType *type, HazardWorld *world, int incoming_stone);
/* Count is the descriptor-sentinel projection, independent of hidden sprites.
 * Callers inspect the live state after each callback, in ascending order. */
int hazards_next(size_t count, size_t *cursor);
#endif
