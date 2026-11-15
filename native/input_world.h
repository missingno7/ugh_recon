#ifndef NATIVE_INPUT_WORLD_H
#define NATIVE_INPUT_WORLD_H
#include "input.h"
/* The saved vector is an opaque external binding, never callable game code. */
typedef struct InputKeyboardBinding {uint16_t first,second;} InputKeyboardBinding;
typedef struct NativeInputWorld {
    uint8_t latest,previous,change,index;
    /* Only the low byte is consumed by the ordinary scan/mask operations.
     * Preserve both allocated high bytes for raw aliases and observation. */
    uint16_t current_scan_storage,enabled_axis_storage,loop_limit;
    InputJoystick joysticks[2];
    uint16_t calibration_reset_words[4];
    uint8_t sequence[205]; /* 34 six-byte records AND their mutable FF sentinel */
    InputKeyboardBinding saved_keyboard;
} NativeInputWorld;
NativeInputWorld *native_input_world(void);

/* Set-1 bytes are delivered unchanged: E0 and break bytes are separate events.
 * No BIOS translation, coalescing or live joystick representation is chosen. */
typedef struct InputByteReply {uint8_t value;int status;} InputByteReply;
typedef struct InputButtonReply {uint16_t buttons;} InputButtonReply;
typedef struct InputCountsReply {
    /* counts use exactly the calibration unit, with uint16 wrap retained.
     * The remaining/latched witnesses preserve verification ABI/error prefixes;
     * they are not a direction classification or a live joystick policy. */
    uint16_t counts[4],latched[4],remaining;
    int status;
} InputCountsReply;
InputByteReply input_service_scan(void);
void input_service_acknowledge_scan(void);
void input_service_joystick_start(uint8_t trigger);
InputByteReply input_service_joystick_presence(void);
InputButtonReply input_service_joystick_buttons(unsigned joystick);
InputCountsReply input_service_joystick_counts(uint16_t limit,uint8_t enabled);
uint16_t input_rebase_count(uint16_t count,uint16_t sampled_limit,uint16_t live_limit);

typedef enum InputVectorOperation {INPUT_VECTOR_CAPTURE,INPUT_VECTOR_INSTALL_HANDLER,INPUT_VECTOR_RESTORE_SAVED} InputVectorOperation;
typedef enum InputQueueOperation {INPUT_QUEUE_TAKE,INPUT_QUEUE_PEEK} InputQueueOperation;
typedef struct InputQueueReply {uint16_t word;uint8_t present;int status;} InputQueueReply;
typedef enum InputPollCut {INPUT_POLL_SCAN,INPUT_POLL_WAIT} InputPollCut;
/* Optional, opaque verification continuation. Only the verification platform
 * adapter knows its ABI representation. Ordinary input state never contains it. */
typedef struct InputServiceContext InputServiceContext;
/* binding is consumed only after successful CAPTURE; setters publish status. */
typedef struct InputVectorReply {InputKeyboardBinding binding;int status;} InputVectorReply;
InputVectorReply input_service_vector(InputVectorOperation operation,InputKeyboardBinding binding,InputServiceContext *context);
uint16_t input_service_queue_flush(void);
InputQueueReply input_service_queue(InputQueueOperation operation,InputServiceContext *context);
int input_service_poll(InputPollCut cut,InputServiceContext *context);
#endif
