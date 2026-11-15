#ifndef NATIVE_TIMING_WORLD_H
#define NATIVE_TIMING_WORLD_H
#include "timer_lifetime.h"
#include "audio_world.h"
/* First composition cut: the scheduler and logical music clock. Channel,
 * voice, fade and PCM storage remain with the existing audio owner. */
typedef struct NativeMusicClock {
    uint32_t ticks,origin;
    uint16_t rate,playing,section_loop;
} NativeMusicClock;
typedef struct NativeTimingWorld {
    TimerState timer;
    TimerLifetime lifetime;
    NativeMusicClock music;
    uint16_t last_offset;
    NativeAudioStorage audio;
} NativeTimingWorld;
NativeTimingWorld *native_timing_world(void);
void native_timing_reset(void);
#endif
