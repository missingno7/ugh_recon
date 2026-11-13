#include "random.h"

void random_seed(RandomState *state, RandomDosTime time) {
    state->word[0]=(uint16_t)((state->word[0]&255u)+(uint16_t)time.seconds*256u);
}

uint16_t random_next_below(RandomState *state, uint16_t bound) {
    uint32_t sum=(uint32_t)bound+state->word[0];
    uint16_t first=(uint16_t)sum;
    /* Retained: each word wraps, but its carry feeds the next addition.
     * The first partial sum survives until the final feedback addition. */
    sum=(uint32_t)state->word[1]+first+(sum>>16);
    state->word[1]=(uint16_t)sum;
    sum=(uint32_t)state->word[2]+state->word[1]+(sum>>16);
    state->word[2]=(uint16_t)sum;
    sum=(uint32_t)state->word[3]+state->word[2]+(sum>>16);
    state->word[3]=(uint16_t)sum;
    state->word[0]=(uint16_t)((uint32_t)first+state->word[3]+(sum>>16));
    /* Retained multiply-high scaling, without rejection or modulo reduction. */
    return (uint16_t)(((uint32_t)state->word[0]*bound)>>16);
}
