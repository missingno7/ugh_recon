#ifndef NATIVE_ADLX_EFFECTS_H
#define NATIVE_ADLX_EFFECTS_H
#include "adlx_main.h"

typedef enum AudioEffectsExit {
    AUDIO_EFFECTS_CONTINUE, AUDIO_EFFECTS_WAIT, AUDIO_EFFECTS_END, AUDIO_EFFECTS_DIVIDE_FAULT
} AudioEffectsExit;
typedef struct AudioEffectsResult {
    AudioRegisterWrite writes[AUDIO_EVENT_WRITES];
    uint16_t write_count, advance, requested_period;
    uint32_t wait_delta;
    uint8_t channel, displaced, timer_request, stop_request, repeated;
    AudioEffectsExit exit;
} AudioEffectsResult;

/* track borrows one effect record independently of current_channel (the
 * allocation/stop identity). The bridge binds one of the four effect records. Operands are
 * twelve stable ordinary bytes, disjoint from live/displaced destinations.
 * A stop request occurs after repeat decrement; its C owner must run before
 * another event. The caller must reproject after that external operation. */
AudioEffectsResult audio_effects_step(AudioState *state, AudioChannel *track,
    AudioMainOperation operation, uint8_t code, const uint8_t operands[12], AudioCursor *cursor);
#endif
