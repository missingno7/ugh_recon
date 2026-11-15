#ifndef NATIVE_AUDIO_WORLD_H
#define NATIVE_AUDIO_WORLD_H
#include "adlx_lifetime.h"

/* The resident audio owner. AudioState remains the algorithms' temporary
 * borrowed view: its clock fields are supplied by the existing timing owner.
 * No second persistent copy of those fields is kept here. */
typedef enum AudioExternalRole {AUDIO_EXTERNAL_OTHER,AUDIO_EXTERNAL_BIOS} AudioExternalRole;
typedef struct AudioExternalBinding {AudioExternalRole role;uint16_t identity;} AudioExternalBinding;
typedef struct AudioDriverCells {
    uint16_t initialized,shutdown;
    AudioExternalBinding calibration_binding,dsp_binding;
    uint16_t current_record;
    uint16_t pairs_remaining,first_sum,second_sum,delay_multiplier,calibration_remainder;
    uint8_t attempted,interrupt_busy,probe_seen,selection,interrupt_mask;
} AudioDriverCells;

/* The two queued DMA descriptors and their sample reservations. Retained
 * lanes have no invented interpretation. */
typedef struct AudioDmaStorage {
    uint16_t count;
    uint8_t page,retained_high;
    uint16_t address,offset;
    uint8_t samples[1024],retained[2];
} AudioDmaStorage;

typedef struct NativeAudioStorage {
    AudioChannel channels[AUDIO_CHANNEL_COUNT];
    AudioVoice live[AUDIO_VOICE_COUNT],displaced[AUDIO_VOICE_COUNT],scanned[AUDIO_VOICE_COUNT];
    uint8_t operator_index[AUDIO_VOICE_COUNT];
    uint16_t playback_guard;
    uint32_t scanned_ticks;
    AudioCursor section_start,section_end;
    AudioFade fade;
    uint16_t timer_period,playback_timer_handle,reserved_voices,current_channel,track_volume;
    AudioResetCells reset;
    AudioDriverCells driver;
    AudioDmaStorage dma[2];
    /* The page-crossing fallback is raw reserved storage. Its first eight
     * bytes are not interpreted as a third queue descriptor. */
    uint8_t fallback_reservation[sizeof(AudioDmaStorage)];
    uint8_t retained_dma_tail[2];
} NativeAudioStorage;

typedef enum AudioPeerRole {
 AUDIO_PEER_UNSUPPORTED,
 AUDIO_PEER_AdvanceGuardedSoundClock,
 AUDIO_PEER_AdvanceMusicFade,
 AUDIO_PEER_ApplyScannedMusicEvents,
 AUDIO_PEER_BeginSoundDelayMeasurement,
 AUDIO_PEER_CalibrateSoundDelay,
 AUDIO_PEER_CancelMusicFade,
 AUDIO_PEER_ChainSavedTimerInterrupt,
 AUDIO_PEER_ClearSoundState,
 AUDIO_PEER_DelaySoundIo,
 AUDIO_PEER_DisableMusicSectionLoop,
 AUDIO_PEER_FinishSoundDelayMeasurement,
 AUDIO_PEER_GetElapsedMusicTime,
 AUDIO_PEER_GetMusicTrackDuration,
 AUDIO_PEER_HandleDspProbeInterrupt,
 AUDIO_PEER_HandleEffectAdlxControl,
 AUDIO_PEER_HandleEffectAdlxFrequency,
 AUDIO_PEER_HandleEffectAdlxGain,
 AUDIO_PEER_HandleEffectAdlxInstrument,
 AUDIO_PEER_HandleEffectAdlxKeyOff,
 AUDIO_PEER_HandleEffectAdlxLongWait,
 AUDIO_PEER_HandleEffectAdlxNoOp,
 AUDIO_PEER_HandleEffectAdlxShortWait,
 AUDIO_PEER_HandleEffectAdlxTimerPeriod,
 AUDIO_PEER_HandleMainAdlxControl,
 AUDIO_PEER_HandleMainAdlxFrequency,
 AUDIO_PEER_HandleMainAdlxGain,
 AUDIO_PEER_HandleMainAdlxInstrument,
 AUDIO_PEER_HandleMainAdlxKeyOff,
 AUDIO_PEER_HandleMainAdlxLongWait,
 AUDIO_PEER_HandleMainAdlxNoOp,
 AUDIO_PEER_HandleMainAdlxShortWait,
 AUDIO_PEER_HandleMainAdlxTimerPeriod,
 AUDIO_PEER_HandleSampleDmaInterrupt,
 AUDIO_PEER_HandleTimerInterrupt,
 AUDIO_PEER_InitializeAdlibPlayback,
 AUDIO_PEER_InitializeDspPlayback,
 AUDIO_PEER_InitializeSoundSystem,
 AUDIO_PEER_InstallTimerInterrupt,
 AUDIO_PEER_KeyOffAdlibChannel,
 AUDIO_PEER_LoadAdlibChannel,
 AUDIO_PEER_LoadAdlibInstrument,
 AUDIO_PEER_LoadAdlibTrackData,
 AUDIO_PEER_LoadBankSoundByIndex,
 AUDIO_PEER_LoadIffSample,
 AUDIO_PEER_LoadSoundBankResource,
 AUDIO_PEER_LocateDmaMixBuffers,
 AUDIO_PEER_MixSampleVoicePairs,
 AUDIO_PEER_PlayAdlibEffect,
 AUDIO_PEER_PrimeSampleDmaPlayback,
 AUDIO_PEER_ProbeSoundBlasterDmaIrq,
 AUDIO_PEER_RegisterTimerCallback,
 AUDIO_PEER_RegisterTimerCallbackFromStack,
 AUDIO_PEER_RemoveTimerCallback,
 AUDIO_PEER_RemoveTimerCallbackFromStack,
 AUDIO_PEER_ResetAdlibTrackChannelCursor,
 AUDIO_PEER_ResetSampleVoiceCursor,
 AUDIO_PEER_ResetSoundBlasterDsp,
 AUDIO_PEER_RestoreAdlibVoiceAllocation,
 AUDIO_PEER_RestoreTimerInterrupt,
 AUDIO_PEER_RunEffectAdlxEvents,
 AUDIO_PEER_RunMainAdlxEvents,
 AUDIO_PEER_ScanMusicEvents,
 AUDIO_PEER_ScheduleMusicFade,
 AUDIO_PEER_SetAdlibChannelGain,
 AUDIO_PEER_SetAdlibChannelVolume,
 AUDIO_PEER_SetAdlibFrequency,
 AUDIO_PEER_SetDspSampleRate,
 AUDIO_PEER_SetMusicTrackVolume,
 AUDIO_PEER_SetTimerCallbackInterval,
 AUDIO_PEER_ShutdownAdlibPlayback,
 AUDIO_PEER_ShutdownDspPlayback,
 AUDIO_PEER_ShutdownSoundSystem,
 AUDIO_PEER_SilenceAdlibOperators,
 AUDIO_PEER_StartAdlibTrackChannel,
 AUDIO_PEER_StartDmaSampleBlock,
 AUDIO_PEER_StartMusicTrack,
 AUDIO_PEER_StartSoundOutputs,
 AUDIO_PEER_StopAdlibTrackChannel,
 AUDIO_PEER_StopMusicTrack,
 AUDIO_PEER_StopSoundChannel,
 AUDIO_PEER_SwapDwordByteOrder,
 AUDIO_PEER_TickAdlxPlayback,
 AUDIO_PEER_WriteAdlibRegister,
 AUDIO_PEER_WriteSoundBlasterDsp,
 AUDIO_PEER_loc_032F,
} AudioPeerRole;

void audio_world_borrow(const NativeAudioStorage *owner,AudioState *view,
                        uint32_t ticks,uint32_t origin,uint16_t rate,
                        uint16_t playing,uint16_t section_loop);
#endif
