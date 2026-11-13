#ifndef MUSIC_CLOCK_H
#define MUSIC_CLOCK_H
#include <stdint.h>

typedef enum MusicClockStatus {
    MUSIC_CLOCK_OK,
    MUSIC_CLOCK_DIVIDE_BY_ZERO
} MusicClockStatus;

typedef struct MusicClockResult {
    MusicClockStatus status;
    uint32_t units; /* Meaningful only on MUSIC_CLOCK_OK. */
} MusicClockResult;

uint32_t music_clock_swap_bytes(uint32_t value);
uint16_t music_clock_disable_section_loop(uint16_t playing, uint16_t enabled);
MusicClockResult music_clock_elapsed(uint32_t ticks, uint32_t origin, uint16_t rate);
#endif
