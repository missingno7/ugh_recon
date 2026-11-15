#ifndef PROJECTOR_TIMING_SERIALIZER_H
#define PROJECTOR_TIMING_SERIALIZER_H
#include "timing_world_bridge.h"
#ifdef UGH_NATIVE_PALETTE
#include "palette_world_bridge.h"
#endif
#ifdef UGH_NATIVE_INPUT
#include "input_world_bridge.h"
#endif
#ifdef UGH_NATIVE_VIDEO_PAGES
#include "video_pages_bridge.h"
#endif
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
static inline const uint8_t *project_timing_observation(const uint8_t *machine) {
    static uint8_t observation[UGH_MEM_SIZE];
    timing_require_seal(machine);
#ifdef UGH_NATIVE_PALETTE
    palette_require_seal(machine);
#endif
#ifdef UGH_NATIVE_INPUT
    input_require_seal(machine);
#endif
#ifdef UGH_NATIVE_VIDEO_PAGES
    video_pages_require_seal(machine);
#endif
    memcpy(observation,machine,sizeof observation);
    timing_serialize(observation);
#ifdef UGH_NATIVE_PALETTE
    palette_serialize(observation);
    if(palette_check_serialization(observation)!=UINT32_MAX){fputs("palette: missed serialization\n",stderr);exit(88);}
#endif
#ifdef UGH_NATIVE_INPUT
    input_serialize(observation);
    if(input_check_serialization(observation)!=UINT32_MAX){fputs("input: missed serialization\n",stderr);exit(88);}
#endif
    #ifdef UGH_NATIVE_VIDEO_PAGES
    video_pages_serialize(observation);
    if(video_pages_check_serialization(observation)!=UINT32_MAX){fputs("pages: missed serialization\n",stderr);exit(88);}
    #endif
    if(timing_check_serialization(observation)!=UINT32_MAX){
        fputs("timing: missed owned serialization\n",stderr);exit(88);
    }
    return observation;
}
#endif
