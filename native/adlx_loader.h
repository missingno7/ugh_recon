#ifndef NATIVE_ADLX_LOADER_H
#define NATIVE_ADLX_LOADER_H
#include "audio.h"

typedef enum AudioAdlxLoadStage {
    AUDIO_ADLX_GATE, AUDIO_ADLX_ROOT_TAG, AUDIO_ADLX_HEADER_TAG,
    AUDIO_ADLX_MAP_TAG, AUDIO_ADLX_TRACK_TAG, AUDIO_ADLX_CAPACITY, AUDIO_ADLX_LOADED
} AudioAdlxLoadStage;
typedef struct AudioAdlxLoadResult {
    AudioCursor instrument_map;
    AudioAdlxLoadStage stage;
    uint16_t value, swap_high, swaps;
    uint8_t main_map;
} AudioAdlxLoadResult;

/* A stable ordinary resource window of 65537 bytes: indexes wrap before each
 * operand, while the second byte of a word at FFFF is contiguous. Input is
 * disjoint from state, result and cursor. The parser deliberately has no file
 * length check. Its index records every consumed/skipped header even on error.
 * Instrument-map setup is a typed output; no independent shadow map is stored
 * in AudioState. Existing shared layout remains unchanged. */
AudioAdlxLoadResult audio_adlx_load(AudioState *state,uint16_t channel,
    AudioCursor *input,uint16_t repeats,uint16_t device_bits);
uint16_t audio_adlx_reset(AudioChannel *track);
/* Retained wrapper bug: parser FFFF is true. The bridge can borrow even a raw
 * aliased record's volume field without manufacturing an array index. */
uint16_t audio_adlx_loaded_volume(AudioChannel *track,uint16_t volume,uint16_t parser_value);
#endif
