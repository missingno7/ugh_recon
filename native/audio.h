#ifndef NATIVE_AUDIO_H
#define NATIVE_AUDIO_H
#include <stdint.h>

enum { AUDIO_CHANNEL_COUNT=13, AUDIO_MAIN_CHANNEL=12, AUDIO_VOICE_COUNT=9 };
/* Allocation remains at the C boundary; interpreters borrow these records. */
enum { AUDIO_FIRST_EFFECT_CHANNEL=8, AUDIO_EFFECT_CHANNEL_COUNT=4 };

/* A borrowed event window and its wrapping byte index. The bridge alone binds
 * windows to DOS resources. No native field contains a machine address. */
typedef struct AudioCursor {
    const uint8_t *window;
    uint16_t index;
} AudioCursor;

/* One shared record, including the main descriptor at index twelve. Absolute
 * main-track aliases are views of channels[12], never independent copies.
 * The six uninterpreted words are preserved storage, not a PCM implementation. */
typedef struct AudioChannel {
    uint32_t age;
    uint16_t repeats;
    AudioCursor start;
    uint16_t length;
    uint16_t sample_mode, sample_rate;
    AudioCursor cursor;
    uint16_t sample_half_length, reserved_word, sample_selector, sample_accumulator;
    uint16_t volume;
    uint32_t deadline;
    uint16_t voice_count, first_voice, step_q8, control;
} AudioChannel;

typedef struct AudioVoice {
    uint8_t instrument[12];
    uint16_t volume, gain, owner, frequency;
} AudioVoice;

typedef struct AudioFade {
    uint16_t step_count, duration, start_volume, target_volume, scheduled, timer_handle;
} AudioFade;

typedef struct AudioState {
    AudioChannel channels[AUDIO_CHANNEL_COUNT];
    AudioVoice live[AUDIO_VOICE_COUNT], displaced[AUDIO_VOICE_COUNT], scanned[AUDIO_VOICE_COUNT];
    uint8_t operator_index[AUDIO_VOICE_COUNT];
    uint16_t playback_guard, ticks_per_unit, playing, section_loop_enabled;
    uint32_t ticks, time_origin, scanned_ticks;
    AudioCursor section_start, section_end;
    AudioFade fade;
    uint16_t timer_period, playback_timer_handle, reserved_voices, current_channel, track_volume;
} AudioState;
#endif
