#ifndef NATIVE_ACTOR_RENDER_H
#define NATIVE_ACTOR_RENDER_H
#include "actors.h"

typedef enum ActorRenderOperation {
    ACTOR_RENDER_GAME_ERASE, ACTOR_RENDER_GAME_DRAW,
    ACTOR_RENDER_GAME_OVERLAY, ACTOR_RENDER_DEMO_ERASE,
    ACTOR_RENDER_DEMO_DRAW, ACTOR_RENDER_RESET
} ActorRenderOperation;
typedef struct ActorRenderInput {
    ObjectPosition position;
    uint16_t sprite, overlay_sprite;
} ActorRenderInput;
typedef enum ActorRenderField {
    ACTOR_RENDER_PIXEL_X, ACTOR_RENDER_PIXEL_Y,
    ACTOR_RENDER_PREVIOUS_X, ACTOR_RENDER_PREVIOUS_Y,
    ACTOR_RENDER_ERASE_SPRITE, ACTOR_RENDER_ERASE_OVERLAY,
    ACTOR_RENDER_CURRENT_SPRITE
} ActorRenderField;
typedef enum ActorRenderEventKind {
    ACTOR_RENDER_STORE, ACTOR_RENDER_RESTORE, ACTOR_RENDER_DRAW
} ActorRenderEventKind;
typedef struct ActorRenderEvent {
    ActorRenderEventKind kind;
    ActorRenderField field;
    uint16_t value, x, y, sprite;
} ActorRenderEvent;
typedef struct ActorRenderResult {
    ActorRenderEvent events[5];
    size_t count;
} ActorRenderResult;
/* One operation on a physical slot. Storage persists across both modes.
 * Preconditions: slot < ACTOR_CAPACITY; ordinary disjoint input/storage.
 * Events are consumed in order, including stores between pixel services.
 * Reset also publishes a current-sprite write, owned by simulation otherwise.
 */
ActorRenderResult actor_render_apply(ActorRenderOperation operation,
    ActorRenderStorage *storage, size_t slot, const ActorRenderInput *input);
#endif
