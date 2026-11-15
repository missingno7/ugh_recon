#ifndef NATIVE_PLATFORM_WORLD_H
#define NATIVE_PLATFORM_WORLD_H
#include <stdint.h>
/* Ten admitted slots. Raw word patterns retain signed/inclusive policies in
 * their existing consumers. Longer lists remain separate live resource views. */
typedef struct NativePlatform {uint16_t left,right,height,arrival,wait,spawn,icon,occupant;} NativePlatform;
typedef struct NativePlatformsWorld {NativePlatform slot[10];} NativePlatformsWorld;
NativePlatformsWorld *native_platforms_world(void);
#endif
