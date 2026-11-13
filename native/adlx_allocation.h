#ifndef NATIVE_ADLX_ALLOCATION_H
#define NATIVE_ADLX_ALLOCATION_H
#include "adlx_main.h"

typedef enum AudioAllocationOperation {
    AUDIO_ALLOCATION_STOP, AUDIO_ALLOCATION_RESTORE, AUDIO_ALLOCATION_START
} AudioAllocationOperation;
typedef enum AudioAllocationActionKind {
    AUDIO_ALLOCATION_COPY, AUDIO_ALLOCATION_KEY_OFF, AUDIO_ALLOCATION_INSTRUMENT,
    AUDIO_ALLOCATION_FREQUENCY, AUDIO_ALLOCATION_VOLUME,
    AUDIO_ALLOCATION_MUSIC_RESULT, AUDIO_ALLOCATION_EMPTY_RESULT
} AudioAllocationActionKind;
enum { AUDIO_ALLOCATION_ACTIONS=80, AUDIO_ALLOCATION_WRITES=384 };
/* Ordered subordinate voice calls, with their native writes. The bridge uses
 * the call journal only to reconstruct the temporary compiler scratch ABI. */
typedef struct AudioAllocationAction {
    AudioAllocationActionKind kind;
    uint16_t channel, current_channel, first_reserved, write_count;
    uint8_t displaced;
} AudioAllocationAction;
typedef struct AudioAllocationResult {
    AudioAllocationAction actions[AUDIO_ALLOCATION_ACTIONS];
    AudioRegisterWrite writes[AUDIO_ALLOCATION_WRITES];
    uint16_t action_count, write_count, value, volume, old_guard, first_voice;
    uint8_t performed, capacity_failure, clamped;
} AudioAllocationResult;
typedef struct AudioEffectSelection { uint16_t channel; uint8_t replace; } AudioEffectSelection;

/* Forward, disjoint ordinary record copies; all iterated voice records are
 * 0..8. Unsupported physical aliases/backward copies belong to the bridge's
 * explicit literal boundary. Device bits are an input, not audio-owned state. */
int audio_allocation_supported(const AudioState *state, AudioAllocationOperation operation,
    uint16_t channel, uint16_t device_bits);
AudioAllocationResult audio_allocation_run(AudioState *state, AudioAllocationOperation operation,
    uint16_t channel, uint16_t volume, uint16_t device_bits);
AudioEffectSelection audio_effect_select(const AudioState *state);
#endif
