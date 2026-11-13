#include "actor_render.h"

static int render_signed(uint16_t value) {
    return value < 32768u ? (int)value : (int)value - 65536;
}
static uint16_t render_pixel(uint16_t value) {
    /* SAR rounds negative positions down; retain the raw word pattern. */
    return (uint16_t)((value >> 5) | ((value & 32768u) ? 63488u : 0));
}
static void render_store(ActorRenderResult *result, ActorRenderField field,
                         uint16_t value) {
    ActorRenderEvent event = {ACTOR_RENDER_STORE,field,value,0,0,0};
    result->events[result->count++] = event;
}
static void render_request(ActorRenderResult *result, ActorRenderEventKind kind,
                           uint16_t x, uint16_t y, uint16_t sprite) {
    ActorRenderEvent event = {kind,ACTOR_RENDER_PIXEL_X,0,x,y,sprite};
    result->events[result->count++] = event;
}
static void render_rotate(ActorRenderResult *result, ActorRenderHistory *history,
                          const ActorRenderInput *input) {
    history->previous_x = history->pixel_x;
    render_store(result,ACTOR_RENDER_PREVIOUS_X,history->previous_x);
    history->previous_y = history->pixel_y;
    render_store(result,ACTOR_RENDER_PREVIOUS_Y,history->previous_y);
    history->pixel_x = render_pixel(input->position.x32);
    render_store(result,ACTOR_RENDER_PIXEL_X,history->pixel_x);
    history->pixel_y = render_pixel(input->position.y32);
    render_store(result,ACTOR_RENDER_PIXEL_Y,history->pixel_y);
}
ActorRenderResult actor_render_apply(ActorRenderOperation operation,
    ActorRenderStorage *storage, size_t slot, const ActorRenderInput *input) {
    ActorRenderResult result = {0};
    ActorRenderHistory *history = &storage->slots[slot];
    uint16_t old = history->erase_sprite;
    switch(operation) {
    case ACTOR_RENDER_GAME_ERASE:
    case ACTOR_RENDER_DEMO_ERASE:
        history->erase_sprite = input->sprite;
        render_store(&result,ACTOR_RENDER_ERASE_SPRITE,input->sprite);
        if(old == ACTOR_HIDDEN_SPRITE) break;
        if(operation == ACTOR_RENDER_DEMO_ERASE) {
            if(old != DEMO_HIDDEN_SPRITE)
                render_request(&result,ACTOR_RENDER_RESTORE,history->previous_x,history->previous_y,old);
        } else if(render_signed(history->previous_y) < 192) {
            render_request(&result,ACTOR_RENDER_RESTORE,history->previous_x,history->previous_y,old);
            old = history->erase_overlay_sprite;
            /* This swap is guarded by the old main sprite and its Y clip. */
            history->erase_overlay_sprite = input->overlay_sprite;
            render_store(&result,ACTOR_RENDER_ERASE_OVERLAY,input->overlay_sprite);
            if(old != ACTOR_HIDDEN_SPRITE)
                render_request(&result,ACTOR_RENDER_RESTORE,
                    (uint16_t)(history->previous_x+11u),(uint16_t)(history->previous_y-13u),old);
        }
        break;
    case ACTOR_RENDER_GAME_DRAW:
    case ACTOR_RENDER_DEMO_DRAW:
        if(input->sprite == (operation == ACTOR_RENDER_GAME_DRAW ? ACTOR_HIDDEN_SPRITE : DEMO_HIDDEN_SPRITE)) break;
        render_rotate(&result,history,input);
        /* Cache rotation precedes clipping. Demo has no lower bounds; gameplay
         * has no X test and excludes Y == -11 as well as Y == 192. */
        if(render_signed(history->pixel_y) >= 192) break;
        if(operation == ACTOR_RENDER_GAME_DRAW) {
            if(render_signed(history->pixel_y) <= -11) break;
        } else if(render_signed(history->pixel_x) >= 320) break;
        render_request(&result,ACTOR_RENDER_DRAW,history->pixel_x,history->pixel_y,input->sprite);
        break;
    case ACTOR_RENDER_GAME_OVERLAY:
        /* No clipping here: the main sprite's visibility, not its draw result,
         * guards overlays. Coordinates use the current persistent cache. */
        if(input->sprite != ACTOR_HIDDEN_SPRITE && input->overlay_sprite != ACTOR_HIDDEN_SPRITE)
            render_request(&result,ACTOR_RENDER_DRAW,
                (uint16_t)(history->pixel_x+11u),(uint16_t)(history->pixel_y-13u),input->overlay_sprite);
        break;
    case ACTOR_RENDER_RESET:
        render_store(&result,ACTOR_RENDER_CURRENT_SPRITE,ACTOR_HIDDEN_SPRITE);
        history->erase_sprite = ACTOR_HIDDEN_SPRITE;
        render_store(&result,ACTOR_RENDER_ERASE_SPRITE,ACTOR_HIDDEN_SPRITE);
        break;
    }
    return result;
}
