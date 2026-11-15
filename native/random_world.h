#ifndef NATIVE_RANDOM_WORLD_H
#define NATIVE_RANDOM_WORLD_H
#include "random.h"
/* One resident allocation; the seconds seed is word[0]'s high-byte view. */
RandomState *native_random_world(void);
#endif
