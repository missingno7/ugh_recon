#ifndef NATIVE_ADLX_SAMPLES_H
#define NATIVE_ADLX_SAMPLES_H
#include "audio.h"
enum { AUDIO_SAMPLE_VOICES=8 };
/* A temporary borrowed view of the existing common owner. Voices point into
 * AudioState.channels; the remaining cells are rebound at each request. */
typedef struct AudioSampleView {
    AudioChannel *voices;
    uint16_t busy,count,mask,remaining,first_sum,second_sum;
} AudioSampleView;
typedef enum AudioSampleAction {AUDIO_SAMPLE_DONE,AUDIO_SAMPLE_READ,AUDIO_SAMPLE_WRITE,AUDIO_SAMPLE_FAULT,AUDIO_SAMPLE_BOUND} AudioSampleAction;
typedef struct AudioSampleRequest {AudioSampleAction action;AudioCursor source;uint16_t destination;uint8_t value;} AudioSampleRequest;
typedef struct AudioSampleMixWork {uint16_t requested,destination,voice,result;uint32_t iterations;uint8_t stage;} AudioSampleMixWork;
AudioSampleMixWork audio_sample_mix_begin(AudioSampleView *view,uint16_t requested,uint16_t destination);
AudioSampleRequest audio_sample_mix_next(AudioSampleView *view,AudioSampleMixWork *work,uint16_t sample);
int16_t audio_sample_scale(uint8_t sample,uint8_t volume);
typedef struct AudioSampleReset {uint16_t displacement;uint8_t overflow;} AudioSampleReset;
AudioSampleReset audio_sample_reset(uint16_t index);

typedef enum AudioSampleImportAction {AUDIO_SAMPLE_IMPORT_DONE,AUDIO_SAMPLE_IMPORT_READ,AUDIO_SAMPLE_IMPORT_STOP,AUDIO_SAMPLE_IMPORT_APPLY,AUDIO_SAMPLE_IMPORT_WAIT,AUDIO_SAMPLE_IMPORT_ACTIVATE,AUDIO_SAMPLE_IMPORT_BOUND} AudioSampleImportAction;
/* Indexed borrowed input ring: the bridge binds a 1 MiB cyclic byte window.
 * An initial unnormalised position may lie in its contiguous trailing margin.
 * No ordinary native object contains a segmented pointer or code identity. */
typedef struct AudioSampleImportRequest {AudioSampleImportAction action;uint32_t position,next;uint8_t publication,original_form;} AudioSampleImportRequest;
typedef struct AudioSampleImportWork {
    uint32_t origin,position,extent,length,budget;
    uint16_t slot,volume,repeats,rate,mode,scale,result;
    uint8_t stage,character,tag,first;
} AudioSampleImportWork;
AudioSampleImportWork audio_sample_import_begin(uint16_t devices,uint16_t slot,uint32_t position,uint16_t volume,uint16_t repeats,uint16_t scale);
AudioSampleImportRequest audio_sample_import_next(AudioSampleImportWork *work,uint16_t reply);
void audio_sample_import_apply(AudioChannel *voice,const AudioSampleImportWork *work,AudioCursor data);
void audio_sample_activate(AudioSampleView *view,uint16_t slot);
#endif
