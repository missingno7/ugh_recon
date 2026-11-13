#ifndef NATIVE_ADLX_VOICE_H
#define NATIVE_ADLX_VOICE_H
#include "adlx_main.h"

typedef enum AudioVoiceOperation {
    AUDIO_VOICE_VOLUME,AUDIO_VOICE_GAIN,AUDIO_VOICE_KEY_OFF,
    AUDIO_VOICE_FREQUENCY,AUDIO_VOICE_INSTRUMENT
} AudioVoiceOperation;

/* Twelve wrapping source-byte reads. An alias identifies an instrument byte
 * in this channel's live (0..11) or saved (12..23) view; -1 is a stable external
 * byte. This describes overlap without putting machine addresses in L2.
 * The description itself is immutable and disjoint from AudioState. */
typedef struct AudioInstrumentSource {uint8_t bytes[12];int8_t alias[12];} AudioInstrumentSource;
typedef struct AudioVoiceResult {
    AudioRegisterWrite writes[14];uint16_t write_count;
    /* displaced describes the primary store/copy, not a later volume refresh. */
    uint8_t channel,displaced,reservation_checked,first_reserved;
} AudioVoiceResult;

/* Channel/value use their low bytes except frequency's full value word.
 * INSTRUMENT requires all aliases in -1..23. Invalid channels read no source.
 * Ordinary serialized RAM; MMIO sources stay in the bridge's explicit boundary. */
AudioVoiceResult audio_voice_step(AudioState *state,AudioVoiceOperation operation,
                                 uint16_t channel,uint16_t value,const AudioInstrumentSource *source);
typedef struct AudioIoDelay {uint32_t iterations;uint8_t overflow;} AudioIoDelay;
AudioIoDelay audio_voice_delay(uint8_t factor,uint8_t calibration);
AudioRegisterWrite audio_voice_register(uint16_t packed);
#endif
