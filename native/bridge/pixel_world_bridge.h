#ifndef PIXEL_WORLD_BRIDGE_H
#define PIXEL_WORLD_BRIDGE_H
#include "ugh.h"
#include "../pixel_world.h"
int pixel_is_owned(uint32_t address);
int pixel_shared_read(uint32_t address,uint8_t *value);
int pixel_shared_write(uint32_t address,uint8_t value);
void pixel_cold_import(uint8_t *memory);
void pixel_require_seal(const uint8_t *memory);
void pixel_serialize(uint8_t *output);
uint32_t pixel_check_serialization(const uint8_t *output);
unsigned pixel_owned_bytes(void);
uint8_t pixel_borrowed_byte(const uint8_t *window,uint32_t index);
void pixel_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
typedef enum PixelPeerRole {
 PIXEL_PEER_DrawTransparentSprite,
 PIXEL_PEER_DrawMapTile,
 PIXEL_PEER_RestoreBackgroundRectangle,
 PIXEL_PEER_RestoreSpriteBackground,
 PIXEL_PEER_CachePlayerDrawState,
 PIXEL_PEER_DrawHudDigit,
 PIXEL_PEER_EncodeTwoDecimalDigits,
 PIXEL_PEER_EncodeFourDecimalDigits,
 PIXEL_PEER_EncodeSixDecimalDigits,
 PIXEL_PEER_RedrawChangedTwoDigitNumber,
 PIXEL_PEER_RedrawChangedFourDigitNumber,
 PIXEL_PEER_RedrawChangedSixDigitNumber,
 PIXEL_PEER_SamplePlayerCollisionPixels,
 PIXEL_PEER_NextRandomBelowAx,
 PIXEL_PEER_RespawnRainParticle,
 PIXEL_PEER_DrawWaterSurfaceFrame0,
 PIXEL_PEER_DrawWaterSurfaceFrame1,
 PIXEL_PEER_DrawWaterSurfaceFrame2
} PixelPeerRole;
int pixel_peer(PixelPeerRole role,uint16_t return_identity,Regs *r);
int pixel_tail(uint16_t target,Regs *r);
#endif
