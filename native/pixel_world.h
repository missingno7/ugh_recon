#ifndef NATIVE_PIXEL_WORLD_H
#define NATIVE_PIXEL_WORLD_H
#include "video_pages.h"
/* Exclusive renderer working words. Persistent player/actor histories and
 * water/world coordinates keep their existing canonical owners. */
typedef struct NativePixelWorld {uint16_t plane_state,water_distance;} NativePixelWorld;
NativePixelWorld *native_pixel_world(void);
uint16_t pixel_collision_position(uint16_t origin,unsigned ordinal);
typedef enum PixelControlRoute {
 PIXEL_SEQ_INDEX,PIXEL_SEQ_DATA,PIXEL_GC_INDEX,PIXEL_GC_DATA,PIXEL_INVALID_CONTROL
} PixelControlRoute;
typedef enum PixelReadRole {PIXEL_SOURCE,PIXEL_COLLISION} PixelReadRole;
void pixel_service_control_write(PixelControlRoute route,uint8_t value);
VideoByteReply pixel_service_control_read(PixelControlRoute route);
uint8_t pixel_service_read(VideoCellAddress address,PixelReadRole role);
void pixel_service_store(VideoCellAddress address,uint8_t value);
/* Each copy reads now, loading all four latches, then writes now. The reply is
 * the full CPU read byte; the inherited write controls still decide the lanes. */
uint8_t pixel_service_copy(VideoCellAddress source,VideoCellAddress destination);
/* Read first; write CPU 40h under the caller's inherited GC recipe. This is
 * deliberately not a software OR over a flat image. Reply preserves AH. */
uint8_t pixel_service_water_mark(VideoCellAddress address);
/* Opaque compatibility role retained for the accepted noncanonical bindings
 * and unknown frame tails. Only the verification provider decodes its payload.
 * Production admission/retirement belongs to the later fail-closed cut. */
typedef struct PixelExternalBinding {uint16_t first,second;} PixelExternalBinding;
typedef struct PixelServiceContext PixelServiceContext;
typedef enum PixelContinuationKind {PIXEL_EXTERNAL_NEAR,PIXEL_EXTERNAL_TAIL} PixelContinuationKind;
int pixel_service_continuation(PixelContinuationKind kind,PixelExternalBinding binding,
 uint16_t return_identity,PixelServiceContext *context);
/* A direct frame ABI can inherit a non-pixel control binding as well. Keep
 * that compatibility payload opaque, separate from the indexed pixel roles. */
typedef struct PixelExternalControlBinding {uint16_t identity;} PixelExternalControlBinding;
void pixel_service_compatibility_write(PixelExternalControlBinding binding,unsigned width,uint32_t value);
#endif
