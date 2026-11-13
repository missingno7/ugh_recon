#ifndef NATIVE_ADLX_MAIN_H
#define NATIVE_ADLX_MAIN_H
#include "audio.h"

typedef enum AudioMainOperation {
    AUDIO_LONG_WAIT, AUDIO_FREQUENCY, AUDIO_KEY_OFF, AUDIO_GAIN,
    AUDIO_INSTRUMENT, AUDIO_NO_OP, AUDIO_TIMER_PERIOD, AUDIO_CONTROL, AUDIO_SHORT_WAIT
} AudioMainOperation;
typedef enum AudioMainExit { AUDIO_CONTINUE, AUDIO_WAIT, AUDIO_END } AudioMainExit;
typedef struct AudioRegisterWrite { uint8_t reg, value; } AudioRegisterWrite;
enum { AUDIO_EVENT_WRITES=14 };
typedef struct AudioMainResult {
    AudioRegisterWrite writes[AUDIO_EVENT_WRITES];
    uint16_t write_count, advance, wait_delta, requested_period;
    uint8_t channel, displaced, timer_request, repeated;
    AudioMainExit exit;
} AudioMainResult;

AudioMainOperation audio_main_operation(uint8_t code);
/* One already-fetched event. operands holds twelve stable bytes (the extra
 * instrument working byte is intentional). cursor points to the payload.
 * Arbitrary channel/control/clock/voice words are admitted. Serialized ordinary
 * RAM, disjoint immutable operands: overlapping live source copying is outside
 * this API. Result writes are an ordered list, never a final register map. */
AudioMainResult audio_main_step(AudioState *state, AudioMainOperation operation,
                               uint8_t code, const uint8_t operands[12], AudioCursor *cursor);
#endif
