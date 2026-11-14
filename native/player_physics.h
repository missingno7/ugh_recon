#ifndef NATIVE_PLAYER_PHYSICS_H
#define NATIVE_PLAYER_PHYSICS_H
#include <stddef.h>
#include <stdint.h>
#include "geometry.h"
#include "level.h"

/* Borrowed working projection of the existing player arrays. This is not a
 * second persistent owner. Cache pixels are inputs, never rebuilt on entry. */
typedef struct PlayerPhysicsView {
    ObjectPosition position;
    uint16_t pixel_x,pixel_y,platform;
    uint16_t velocity_x,velocity_y,impact,thrust;
    uint16_t left,right,up,down;
} PlayerPhysicsView;
typedef struct PlayerPhysicsWorld {
    uint16_t timer,water_y,impact_limit,fade_rate,fade_level;
    uint8_t rain;
    const LevelPlatform *platforms;
    size_t platform_count;
} PlayerPhysicsWorld;

typedef enum PlayerPhysicsField {
    PF_TIMER,PF_IMPACT,PF_THRUST,PF_VX,PF_VY,PF_X,PF_PIXEL_X,
    PF_PLATFORM,PF_Y,PF_PIXEL_Y,PF_FADE_RATE,PF_FADE_LEVEL
} PlayerPhysicsField;
typedef enum PlayerPhysicsEventKind {
    PP_WRITE,PP_SELECT_PLANE_REGISTER,PP_READ_PLANE,PP_SAMPLE,PP_DONE
} PlayerPhysicsEventKind;
typedef struct PlayerCollisionProbe {
    uint16_t pixel_x,pixel_y;
    /* Relative four-pixel columns and legacy collision-image rows (96 cells).
     * Both wrap as words. Left/up intentionally retain their first probe. */
    uint16_t columns,rows;
} PlayerCollisionProbe;
typedef struct PlayerPhysicsEvent {
    PlayerPhysicsEventKind kind;
    PlayerPhysicsField field;
    uint16_t value;
    PlayerCollisionProbe probe;
} PlayerPhysicsEvent;
typedef enum PlayerPhysicsStage {
    PP_INITIAL,PP_HORIZONTAL,PP_HORIZONTAL_SCAN,PP_HORIZONTAL_HIT,
    PP_HORIZONTAL_END,PP_VERTICAL,PP_VERTICAL_SCAN,PP_VERTICAL_HIT,
    PP_VERTICAL_END,PP_FINISHED
} PlayerPhysicsStage;
typedef struct PlayerPhysicsProcess {
    PlayerPhysicsView *player;
    PlayerPhysicsWorld *world;
    PlayerPhysicsStage stage;
    PlayerPhysicsEvent journal[32];
    size_t count,consumed;
    uint16_t candidate,cursor,plane,columns,rows;
    int water_state,positive,awaiting_reply,failed;
    uint8_t sample;
} PlayerPhysicsProcess;

/* Primitive count is 1..15; the update uses fixed counts1,5,6. */
uint16_t player_physics_sar(uint16_t value,unsigned count);
uint16_t player_physics_limit(uint16_t value);
uint16_t player_physics_reflect(uint16_t *velocity);
uint8_t player_collision_sample(const uint8_t samples[10]);
void player_physics_begin(PlayerPhysicsProcess *process,PlayerPhysicsView *player,
    PlayerPhysicsWorld *world);
/* A sample must be replied to before polling again. Consume every request in
 * order. Each write has already changed the private working projection; publish
 * it before the next service. No allocation or asynchronous callbacks. */
PlayerPhysicsEvent player_physics_poll(PlayerPhysicsProcess *process);
void player_physics_reply(PlayerPhysicsProcess *process,uint8_t sample);
#endif
