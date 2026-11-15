#ifndef PROJECTOR_TIMING_SERIALIZER_H
#define PROJECTOR_TIMING_SERIALIZER_H
#include "world_registry_generated.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
static inline const uint8_t *project_timing_observation(const uint8_t *machine){
 static uint8_t observation[UGH_MEM_SIZE];
 world_registry_require_seal(machine);memcpy(observation,machine,sizeof observation);
 world_registry_serialize(observation);
 if(world_registry_check(observation)!=UINT32_MAX){fputs("world registry: missed serialization\n",stderr);exit(88);}
 return observation;
}
#endif
