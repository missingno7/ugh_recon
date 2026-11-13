#ifndef NATIVE_DEMO_CORE_H
#define NATIVE_DEMO_CORE_H
#include "actors.h"
typedef struct DemoStep {
    int motion, stopped, repeat_written, restart_written;
    uint16_t last_delta;
} DemoStep;
uint16_t demo_delta(uint8_t value);
uint16_t demo_pixel_position(uint16_t pixel);
/* One bytecode instruction; result 0 continues, 1 yields motion, 2 stops.
 * Accessible instruction and (on motion) two delta bytes are preconditions.
 * Slot cursor is a byte offset. No positivity or reachability assumption is
 * made about the wrapping repeat word, position or sticky finished value. */
int demo_instruction(DemoMotionSlot *slot, DemoStep *effects);
/* Bounded immutable script with valid cursor/restart and a terminating control
 * walk. Errors reject the extended malformed-stream domain; no partial state
 * is published by the bridge on rejection. */
int demo_advance_slot(DemoMotionSlot *slot, DemoStep *effects);
void demo_initialize(DemoMotionScene *scene, ActorRenderStorage *render,
    const DemoMotionScript *const *scripts, size_t count);
/* initialize requires count<=ACTOR_CAPACITY and separate initialized storage
 * with immutable accessible scripts. The bridge further reserves a sentinel. */
int demo_all_finished(const DemoMotionScene *scene);
#endif
