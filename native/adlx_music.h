#ifndef NATIVE_ADLX_MUSIC_H
#define NATIVE_ADLX_MUSIC_H
#include "adlx_sections.h"

typedef enum AudioMusicOperation {AUDIO_MUSIC_START,AUDIO_MUSIC_STOP} AudioMusicOperation;
typedef enum AudioMusicAction {
    AUDIO_MUSIC_DONE,AUDIO_MUSIC_CANCEL,AUDIO_MUSIC_LOAD,AUDIO_MUSIC_START_CHANNEL,
    AUDIO_MUSIC_SET_VOLUME,AUDIO_MUSIC_SCHEDULE,AUDIO_MUSIC_STOP_CHANNEL,
    AUDIO_MUSIC_TIMER_WAIT,AUDIO_MUSIC_SILENCE,AUDIO_MUSIC_WAIT_BOUND
} AudioMusicAction;
typedef struct AudioMusicRequest {
    AudioMusicAction action;AudioCursor resource;uint16_t channel,volume;
} AudioMusicRequest;
typedef struct AudioMusicWork {
    AudioMusicOperation operation;AudioCursor resource;
    uint16_t duration,volume,result,stage,channel;uint32_t wait_budget;
} AudioMusicWork;

/* Resume only after the requested peer succeeded. Reproject live state first;
 * ordinary negative API results are replies, distinct from service failures. */
AudioMusicWork audio_music_begin(AudioMusicOperation operation,AudioCursor resource,uint16_t duration,uint16_t volume,uint16_t devices);
AudioMusicRequest audio_music_next(AudioState *state,AudioMusicWork *work,uint16_t reply);

typedef enum AudioFadeAction {AUDIO_FADE_NONE,AUDIO_FADE_REGISTER,AUDIO_FADE_REMOVE,AUDIO_FADE_VOLUME,AUDIO_FADE_FAULT} AudioFadeAction;
typedef struct AudioFadeRequest {AudioFadeAction action;uint16_t handle,volume,remainder;uint32_t interval;} AudioFadeRequest;
AudioFadeRequest audio_music_schedule(const AudioState *state);
AudioFadeRequest audio_music_cancel(const AudioState *state);
void audio_music_registered(AudioState *state,uint16_t handle);
void audio_music_cancelled(AudioState *state);
AudioFadeRequest audio_music_fade_step(AudioState *state);
int audio_music_guard_begin(AudioState *state);
void audio_music_guard_end(AudioState *state);

/* The C loop indexes a WORD but the voice driver takes its low BYTE. Thus
 * even a corrupt count repeats voices 0..8 each 256 indices, without overflow
 * into other records. 256 groups * 9 voices * 2 writes bounds the journal. */
typedef struct AudioMusicVolume {AudioRegisterWrite writes[4608];uint16_t write_count,result;} AudioMusicVolume;
AudioMusicVolume audio_music_volume(AudioState *state,uint16_t devices,uint16_t volume);
void audio_music_silence(const AudioState *state,AudioRegisterWrite writes[20]);
#endif
