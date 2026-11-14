#ifndef PROJECTOR_TIMING_SERIALIZER_H
#define PROJECTOR_TIMING_SERIALIZER_H
#include "timing_world_bridge.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
static inline const uint8_t *project_timing_observation(const uint8_t *machine) {
    static uint8_t observation[UGH_MEM_SIZE];
    timing_require_seal(machine);
    memcpy(observation,machine,sizeof observation);
    timing_serialize(observation);
    if(timing_check_serialization(observation)!=UINT32_MAX){
        fputs("timing: missed owned serialization\n",stderr);exit(88);
    }
    return observation;
}
#endif
