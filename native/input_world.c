#include "input_world.h"
static NativeInputWorld world;
NativeInputWorld *native_input_world(void){return &world;}
uint16_t input_rebase_count(uint16_t count,uint16_t sampled_limit,uint16_t live_limit){return (uint16_t)(count+(uint16_t)(live_limit-sampled_limit));}
