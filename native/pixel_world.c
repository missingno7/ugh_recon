#include "pixel_world.h"
static NativePixelWorld world;
NativePixelWorld *native_pixel_world(void){return &world;}
uint16_t pixel_collision_position(uint16_t origin,unsigned ordinal){
 static const uint16_t delta[]={0,3,5,19u*96u,19u*96u+3u,19u*96u+5u,
  6u*96u,6u*96u+5u,12u*96u,12u*96u+5u};
 /* Ten ordered reads; each effective position reduces independently. */
 return (uint16_t)(origin+delta[ordinal]);
}
