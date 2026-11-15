#ifndef UGH_PORT_RESOURCES_H
#define UGH_PORT_RESOURCES_H
#include "services.h"
typedef struct GSRequiredResource {GSResourceId id;uint32_t classification;uint64_t size,payload_offset;uint8_t sha256[32];} GSRequiredResource;
typedef struct GSResourcePack {uint8_t *storage;size_t size,payload;uint32_t count;} GSResourcePack;
/* All required objects must come from the compiled build-time admission manifest.
 * No partial pack is published on failure. Aliases share canonical payload bytes. */
GSStatus gs_resources_open(GSResourcePack *,const char *,const GSRequiredResource *,size_t,char *,size_t);
void gs_resources_close(GSResourcePack *);
GSResourceOps gs_resources_operations(void);
#endif
