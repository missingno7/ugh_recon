#include "music_clock.h"

uint32_t music_clock_swap_bytes(uint32_t value)
{
    return (value >> 24) | ((value >> 8) & 0xff00u)
        | ((value << 8) & 0xff0000u) | (value << 24);
}

uint16_t music_clock_disable_section_loop(uint16_t playing, uint16_t enabled)
{
    /* Original C tests the entire word, unlike the driver's bit-zero tests. */
    return playing ? 0 : enabled;
}

MusicClockResult music_clock_elapsed(uint32_t ticks, uint32_t origin, uint16_t rate)
{
    MusicClockResult result = { MUSIC_CLOCK_DIVIDE_BY_ZERO, 0 };
    /* Retain the fault outcome; zero rate must never become elapsed time zero. */
    if (rate) {
        result.status = MUSIC_CLOCK_OK;
        /* Retained: subtraction wraps at 32 bits BEFORE unsigned division.
         * These are ADLX timing units, not seconds or video frames. */
        result.units = (uint32_t)(ticks - origin) / rate;
    }
    return result;
}
