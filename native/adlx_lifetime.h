#ifndef NATIVE_ADLX_LIFETIME_H
#define NATIVE_ADLX_LIFETIME_H
#include "audio.h"

/* Borrowed expansion of the common owner's reset view, not a persistent PCM
 * owner. The bridge binds these cells for one reset only. Resident DMA buffers,
 * operator indices, timer handles and calibration cells are outside this view. */
typedef struct AudioResetCells {
    uint16_t mixer_busy, dsp_port, interrupt_vector;
    AudioCursor bank, instrument_map;
    uint32_t bank_length;
    uint16_t devices, sample_count, sample_mask, spare[2];
} AudioResetCells;
void audio_lifetime_reset(AudioState *state,AudioResetCells *cells);

typedef enum AudioLifetimeAction {
    AUDIO_LIFETIME_DONE,AUDIO_LIFETIME_CALIBRATE,AUDIO_LIFETIME_WRITE,
    AUDIO_LIFETIME_DELAY,AUDIO_LIFETIME_READ,AUDIO_LIFETIME_SILENCE,
    AUDIO_LIFETIME_INSTALL,AUDIO_LIFETIME_REGISTER,AUDIO_LIFETIME_REMOVE,
    AUDIO_LIFETIME_RESTORE
} AudioLifetimeAction;
typedef struct AudioLifetimeRequest {AudioLifetimeAction action;uint16_t value;} AudioLifetimeRequest;
typedef struct AudioLifetimeWork {uint16_t stage,result;uint8_t stopping;} AudioLifetimeWork;
AudioLifetimeWork audio_lifetime_begin(int stopping);
/* attempted and handle are fresh borrowed cells at each service boundary.
 * A request is resumed only on successful delivery, never after an error. */
AudioLifetimeRequest audio_lifetime_next(AudioLifetimeWork *work,uint8_t *attempted,uint16_t handle,uint16_t reply);

typedef enum AudioCalibrationAction {
    AUDIO_CALIBRATION_WAIT_BEGIN,AUDIO_CALIBRATION_WAIT_LOOP,
    AUDIO_CALIBRATION_DONE,AUDIO_CALIBRATION_BOUND
} AudioCalibrationAction;
typedef struct AudioCalibrationWork {
    uint16_t marker,remaining,progress;
    uint32_t budget;
    AudioCalibrationAction action;
} AudioCalibrationWork;
typedef struct AudioMeasurement {uint16_t remainder,multiplier;} AudioMeasurement;
AudioCalibrationWork audio_calibration_begin(uint16_t progress_bias);
/* One original polling instruction after the external service has optionally
 * delivered an interrupt. The service supplies the live marker/counter/progress
 * values. All words wrap; no division or CPU-frequency conversion occurs. */
AudioCalibrationAction audio_calibration_resume(AudioCalibrationWork *work);
uint16_t audio_calibration_started(void);
AudioMeasurement audio_calibration_finished(uint16_t remaining,uint16_t progress);
#endif
