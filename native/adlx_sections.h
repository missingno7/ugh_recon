#ifndef NATIVE_ADLX_SECTIONS_H
#define NATIVE_ADLX_SECTIONS_H
#include "adlx_main.h"

typedef enum AudioScanAction {
    AUDIO_SCAN_LONG, AUDIO_SCAN_FREQUENCY, AUDIO_SCAN_KEY_OFF, AUDIO_SCAN_GAIN,
    AUDIO_SCAN_INSTRUMENT, AUDIO_SCAN_TIMER, AUDIO_SCAN_EXTENSION,
    AUDIO_SCAN_DEFAULT, AUDIO_SCAN_BAD
} AudioScanAction;
typedef struct AudioScanDispatch {uint16_t value;AudioScanAction action;} AudioScanDispatch;
typedef enum AudioScanExit {AUDIO_SCAN_MORE,AUDIO_SCAN_DONE,AUDIO_SCAN_END,AUDIO_SCAN_BUDGET,AUDIO_SCAN_CALLBACK,AUDIO_SCAN_BOUNDARY} AudioScanExit;
typedef struct AudioScanWork {
    AudioCursor cursor;
    uint32_t total,threshold,budget;
    uint16_t next_units;
    uint8_t pass,entered,copied;
    AudioScanExit exit;
} AudioScanWork;

/* Stable ordinary resource window65537 bytes, disjoint from shared state.
 * This is the C seek decoder, deliberately independent of both interpreters.
 * BOUNDARY means discard the unpublished snapshot and use compatibility. */
AudioScanAction audio_section_classify(const AudioScanDispatch table[7],uint8_t code);
AudioScanWork audio_section_scan_begin(AudioState *state,uint16_t first,uint16_t second,uint16_t devices);
AudioScanExit audio_section_scan_step(AudioState *state,AudioScanWork *work,const AudioScanDispatch table[7]);
AudioScanWork audio_section_scan(AudioState *state,uint16_t first,uint16_t second,uint16_t devices,const AudioScanDispatch table[7]);

typedef enum AudioSectionActionKind {AUDIO_SECTION_COPY,AUDIO_SECTION_INSTRUMENT,AUDIO_SECTION_FREQUENCY,AUDIO_SECTION_VOLUME} AudioSectionActionKind;
typedef struct AudioSectionAction {
    AudioSectionActionKind kind;uint16_t channel,current_channel,first_reserved,write_count;uint8_t displaced;
} AudioSectionAction;
typedef struct AudioSectionApply {
    AudioSectionAction actions[36];AudioRegisterWrite writes[162];
    uint16_t action_count,write_count;
} AudioSectionApply;
/* Native physical voices0..8, forward record copies. The bridge retains
 * backwards copies and unchecked physical aliases explicitly. */
AudioSectionApply audio_section_apply(AudioState *state,uint16_t devices);
int audio_section_tick_begin(AudioState *state);
int audio_section_main_due(const AudioState *state);
int audio_section_apply_due(const AudioState *state);
int audio_section_effect_due(const AudioState *state,unsigned index);
void audio_section_main_context(AudioState *state);
void audio_section_effects_begin(AudioState *state);
void audio_section_effect_next(AudioState *state);
void audio_section_tick_end(AudioState *state);
#endif
