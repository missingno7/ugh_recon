#include "timing_world.h"
/* One verification-host instance. No historical RAM, frame or platform state. */
static NativeTimingWorld owner;
NativeTimingWorld *native_timing_world(void) { return &owner; }
void native_timing_reset(void) { owner=(NativeTimingWorld){0}; }
