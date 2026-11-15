#include "backend.h"
#include <time.h>
static GSStatus read_seed(void *context,GSSeedReply *reply) {
    GSSdlSeed *seed=context;if(!reply)return GS_INVALID;
    if(seed->fixed){*reply=seed->replay;return GS_OK;}
    time_t now=time(NULL);struct tm *parts=localtime(&now);
    if(!parts)return GS_IO_ERROR;
    *reply=(GSSeedReply){(uint8_t)parts->tm_hour,(uint8_t)parts->tm_min,
        (uint8_t)parts->tm_sec,0};return GS_OK;
}
GSSeedOps gs_seed_operations(void){return (GSSeedOps){read_seed};}
