#include "random_world.h"
static RandomState world;
RandomState *native_random_world(void){return &world;}
