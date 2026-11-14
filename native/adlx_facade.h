#ifndef NATIVE_ADLX_FACADE_H
#define NATIVE_ADLX_FACADE_H
#include "audio.h"
typedef enum AudioFacadeOperation {AUDIO_FACADE_INIT,AUDIO_FACADE_SHUTDOWN,AUDIO_FACADE_START} AudioFacadeOperation;
typedef enum AudioFacadeAction {
    AUDIO_FACADE_DONE,AUDIO_FACADE_CLEAR,AUDIO_FACADE_STOP_SYSTEM,AUDIO_FACADE_INIT_DSP,
    AUDIO_FACADE_INIT_ADLIB,AUDIO_FACADE_CANCEL,AUDIO_FACADE_STOP_DSP,AUDIO_FACADE_STOP_ADLIB,
    AUDIO_FACADE_PRIME,AUDIO_FACADE_START_CHANNEL,AUDIO_FACADE_BROKEN_HOOK,
    AUDIO_FACADE_INITIALIZED,AUDIO_FACADE_SHUTDOWN_LATCH
} AudioFacadeAction;
typedef struct AudioFacadeView {AudioState *audio;uint16_t devices,initialized,shutdown_latch,sample_count;} AudioFacadeView;
typedef struct AudioFacadeWork {AudioFacadeOperation operation;uint16_t stage,collected,channel;} AudioFacadeWork;
typedef struct AudioFacadeRequest {AudioFacadeAction action;uint16_t channel,volume;} AudioFacadeRequest;
AudioFacadeWork audio_facade_begin(AudioFacadeOperation operation);
/* Rebind all borrowed cells, the caller's requested mask and reply after every
 * service. A broken-hook request has no ordinary successful continuation. */
AudioFacadeRequest audio_facade_next(AudioFacadeView *view,AudioFacadeWork *work,uint16_t requested,uint16_t reply);

typedef struct AudioDurationWork {uint16_t position,end;uint32_t total,budget;uint8_t enabled;} AudioDurationWork;
typedef struct AudioDurationResult {uint16_t value;uint8_t fault;} AudioDurationResult;
AudioDurationWork audio_duration_begin(uint16_t devices,uint16_t playing,uint16_t rate,uint16_t start,uint16_t length);
int audio_duration_fetch(AudioDurationWork *work);
int audio_duration_step(AudioDurationWork *work,uint8_t code,int arm,uint8_t payload);
AudioDurationResult audio_duration_result(const AudioDurationWork *work,uint16_t live_rate);
#endif
