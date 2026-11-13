#ifndef NATIVE_RANDOM_H
#define NATIVE_RANDOM_H
#include <stdint.h>

/* Four independent word bit patterns, in their original update order. */
typedef struct RandomState { uint16_t word[4]; } RandomState;
typedef struct RandomDosTime {
    uint8_t hours, minutes, seconds, hundredths;
} RandomDosTime;

/* Replace only the high byte of word[0]; this is a partial reseed. */
void random_seed(RandomState *state, RandomDosTime time);
/* The bound participates in the recurrence, even when it is zero or one. */
uint16_t random_next_below(RandomState *state, uint16_t bound);
#endif
