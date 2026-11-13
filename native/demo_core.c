#include "demo_core.h"
uint16_t demo_delta(uint8_t value) {
    int signed_value=value<128 ? (int)value : (int)value-256;
    return (uint16_t)(signed_value*4);
}
uint16_t demo_pixel_position(uint16_t pixel) { return (uint16_t)(pixel*32u); }
int demo_instruction(DemoMotionSlot *slot,DemoStep *effects) {
    const uint8_t *p=slot->script->code+slot->cursor;
    uint16_t op=(uint16_t)(p[0]+256u*p[1]);
    slot->cursor+=2;
    if(op<32768u) {
        slot->sprite=op;
        slot->position.x32=(uint16_t)(slot->position.x32+demo_delta(p[2]));
        effects->last_delta=demo_delta(p[3]);
        slot->position.y32=(uint16_t)(slot->position.y32+effects->last_delta);
        slot->cursor+=2; effects->motion=1;
        return 1;
    }
    if(op!=32768u) {
        slot->repeat_count=op; slot->repeat_start=slot->cursor;
        effects->repeat_written=effects->restart_written=1;
    } else if(slot->repeat_count) {
        /* Retained signed-repeat encoding: increment even positive/corrupt
         * values, wrapping to zero; completion waits for a later marker. */
        slot->repeat_count=(uint16_t)(slot->repeat_count+1u);
        effects->repeat_written=1;
        if(slot->repeat_count) slot->cursor=slot->repeat_start;
    } else {
        slot->cursor-=2; slot->finished=1; effects->stopped=1;
        return 2;
    }
    return 0;
}
int demo_advance_slot(DemoMotionSlot *slot,DemoStep *effects) {
    *effects=(DemoStep){0,0,0,0,0};
    slot->countdown=(uint16_t)(slot->countdown-1u);
    if(slot->countdown) return 1;
    slot->countdown=slot->script->period;
    /* Every admitted shipped control walk yields within this bound. Keep a
     * rejecting bound for malformed synthetic scripts instead of hanging. */
    for(size_t n=0;n<=slot->script->code_size;n++) {
        if(slot->cursor>slot->script->code_size || slot->script->code_size-slot->cursor<2) return 0;
        uint16_t op=(uint16_t)(slot->script->code[slot->cursor]+256u*slot->script->code[slot->cursor+1]);
        if(op<32768u && slot->script->code_size-slot->cursor<4) return 0;
        if(demo_instruction(slot,effects)) return 1;
    }
    return 0;
}
void demo_initialize(DemoMotionScene *scene,ActorRenderStorage *render,
    const DemoMotionScript *const *scripts,size_t count) {
    scene->count=count;
    for(size_t i=0;i<count;i++) {
        DemoMotionSlot *slot=&scene->slots[i]; const DemoMotionScript *script=scripts[i];
        slot->script=script; slot->cursor=0;
        /* repeat_start is deliberately untouched until its first directive. */
        slot->repeat_count=0; slot->countdown=1; slot->finished=0;
        slot->position.x32=demo_pixel_position(script->initial_pixel_x);
        slot->position.y32=demo_pixel_position(script->initial_pixel_y);
        render->slots[i].pixel_x=render->slots[i].previous_x=script->initial_pixel_x;
        render->slots[i].pixel_y=render->slots[i].previous_y=script->initial_pixel_y;
    }
    /* ResetSpriteEraseState's actor contribution touches all physical slots.
     * Overlay history, pixel caches and unused simulation slots stay stale. */
    for(size_t i=0;i<ACTOR_CAPACITY;i++) {
        scene->slots[i].sprite=ACTOR_HIDDEN_SPRITE;
        render->slots[i].erase_sprite=ACTOR_HIDDEN_SPRITE;
    }
}
int demo_all_finished(const DemoMotionScene *scene) {
    for(size_t i=0;i<scene->count;i++) if(!scene->slots[i].finished) return 0;
    return 1;
}
