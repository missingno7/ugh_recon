#ifndef NATIVE_DEMO_PRESENTATION_H
#define NATIVE_DEMO_PRESENTATION_H
#include <stdint.h>

typedef enum DemoPresentationKind {
    DEMO_PRESENT_RUN, DEMO_PRESENT_REVEAL, DEMO_PRESENT_PREGAME,
    DEMO_PRESENT_ATTRACT, DEMO_PRESENT_COMPLETION
} DemoPresentationKind;
typedef enum DemoPresentationPhase {
    DP_INITIALIZE, DP_CLEAR_EXIT, DP_CLEAR_LEVEL, DP_CLEAR_STEP,
    DP_INITIAL_POLL, DP_LOOP, DP_PALETTE_AFTER, DP_ERASE, DP_WATER,
    DP_ADVANCE, DP_DRAW, DP_SWAP, DP_TEST, DP_TEST_AFTER,
    DP_JOYSTICK_AFTER, DP_KEYBOARD_AFTER, DP_FADE_CHECK, DP_FADE_LEVEL, DP_REPEAT,
    DP_PREPARE, DP_MUSIC_STOP, DP_MUSIC_START, DP_VECTOR, DP_RUN,
    DP_REVEAL_X, DP_REVEAL_WIDTH, DP_WRAPPER_DONE, DP_TERMINAL,
    DEMO_PRESENT_PHASE_COUNT
} DemoPresentationPhase;
typedef struct DemoPresentationCursor {
    DemoPresentationKind kind;
    DemoPresentationPhase phase;
} DemoPresentationCursor;
typedef struct DemoPresentationInput {
    uint16_t fade_level, fade_step, exit_code, water_y;
    uint16_t palette_work, key_word;
    int finished, joystick_idle;
} DemoPresentationInput;
typedef enum DemoPresentationService {
    DP_SERVICE_INITIALIZE, DP_SERVICE_POLL_KEYBOARD,
    DP_SERVICE_PALETTE, DP_SERVICE_RETRACE, DP_SERVICE_ERASE,
    DP_SERVICE_WATER, DP_SERVICE_ADVANCE, DP_SERVICE_DRAW,
    DP_SERVICE_SWAP, DP_SERVICE_TEST, DP_SERVICE_JOYSTICK,
    DP_SERVICE_PREPARE_ZERO, DP_SERVICE_PREPARE_NINETY,
    DP_SERVICE_MUSIC_STOP, DP_SERVICE_MUSIC_START,
    DP_SERVICE_RUN, DP_SERVICE_REVEAL_WIDTH
} DemoPresentationService;
typedef enum DemoPresentationActionKind {
    DP_ACTION_SERVICE, DP_ACTION_EXIT, DP_ACTION_LEVEL, DP_ACTION_STEP,
    DP_ACTION_VECTOR, DP_ACTION_REVEAL_X, DP_ACTION_DONE, DP_ACTION_REPEAT, DP_ACTION_INVALID
} DemoPresentationActionKind;
typedef struct DemoPresentationAction {
    DemoPresentationActionKind kind;
    DemoPresentationService service;
    uint16_t value;
} DemoPresentationAction;
typedef struct DemoFadeEffect { int triggered; uint16_t fade_step,level; } DemoFadeEffect;
typedef struct DemoRevealWidth { uint16_t pixel_x,width_word; uint8_t width; } DemoRevealWidth;

DemoPresentationCursor demo_presentation_begin(DemoPresentationKind kind);
/* Consume one event, execute it synchronously, then supply fresh service/RAM
 * results to next. No callback, timer or page operation is precomputed away.
 * kind/phase must describe an admitted cut of this sequence. */
DemoPresentationAction demo_presentation_next(DemoPresentationCursor *cursor,
    const DemoPresentationInput *input);
DemoFadeEffect demo_presentation_fade(uint16_t sprite,uint16_t level);
DemoRevealWidth demo_presentation_width(uint16_t position_x32);
#endif
