#ifndef NATIVE_TIMER_H
#define NATIVE_TIMER_H
#include <stdint.h>

enum { TIMER_CAPACITY=16, TIMER_FREE=32768 };
typedef enum TimerCallback {
    TIMER_OPEN, TIMER_BIOS_CHAIN, TIMER_MUSIC_FADE, TIMER_ADLX_PLAYBACK,
    TIMER_FIXTURE_CLEAR, TIMER_FIXTURE_IRQ
} TimerCallback;
/* Symbolic callback fragments, never machine addresses. The bridge binds OPEN
 * fragments (32..63) to snapshot words. Keeping provenance is necessary because
 * the original removal bug can splice halves of DIFFERENT callbacks. */
typedef enum TimerFragment {
    TIMER_ZERO, TIMER_ENTRY_CHAIN, TIMER_ENTRY_FADE, TIMER_ENTRY_PLAYBACK,
    TIMER_ENTRY_CLEAR, TIMER_ENTRY_IRQ, TIMER_GROUP_TIMER, TIMER_GROUP_SOUND
} TimerFragment;
typedef struct TimerTarget { uint16_t first, second; } TimerTarget;
typedef struct TimerSlot {
    uint32_t interval, remaining;
    uint16_t due, handle;
    TimerTarget target;
} TimerSlot;
typedef struct TimerState {
    TimerSlot slots[TIMER_CAPACITY];
    /* Original byte-offset handle values are retained as public identities.
     * Broken mappings remain representable; this is deliberately not a bijection. */
    uint16_t by_handle[TIMER_CAPACITY];
    unsigned count;
    uint32_t quantum, earliest;
    uint16_t installed, programmed_divisor;
} TimerState;
typedef struct TimerTickScratch { uint16_t low, high; } TimerTickScratch;

TimerTarget timer_target(TimerCallback callback);
TimerCallback timer_callback(TimerTarget target);
int timer_handle_slot(const TimerState *state, uint16_t handle);
int timer_register(TimerState *state, TimerCallback callback, uint32_t interval);
/* Caller must check timer_handle_slot and count>=2. Returns the retained
 * removal result identity; it is not necessarily the identity removed. */
uint16_t timer_remove(TimerState *state, uint16_t handle);
void timer_remove_wrong_stride(TimerState *state, unsigned tail, unsigned destination);
void timer_set_interval(TimerState *state, uint16_t handle, uint32_t interval);
/* Tick has two phases: account all slots, then consume descending one at a
 * time. Callbacks can mutate state between consumes. Never snapshot a due list. */
TimerTickScratch timer_account_tick(TimerState *state);
int timer_take_due(TimerState *state, unsigned index, TimerCallback *callback);
#endif
