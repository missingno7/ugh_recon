#include "platform.h"
#include "pixel_world_bridge.h"
#include "video_pages_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned active;
static int pixel_index(uint32_t address,unsigned *index){
 uint32_t base=lin(GAME_SEG,G(SpritePlaneStateScratch));
 if(address<base || address-base>=4)return 0;
 *index=(unsigned)(address-base);return 1;
}
static uint16_t pixel_get_word(unsigned index){NativePixelWorld *p=native_pixel_world();return index?p->water_distance:p->plane_state;}
static void pixel_put_word(unsigned index,uint16_t value){NativePixelWorld *p=native_pixel_world();if(index)p->water_distance=value;else p->plane_state=value;}
int pixel_is_owned(uint32_t address){unsigned i;return active && pixel_index(address,&i);}
int pixel_shared_read(uint32_t address,uint8_t *value){unsigned i;if(!active || !pixel_index(address,&i))return 0;*value=(uint8_t)(pixel_get_word(i/2)>>((i&1)*8));return 1;}
int pixel_shared_write(uint32_t address,uint8_t value){
 unsigned i;if(!active || !pixel_index(address,&i))return 0;
 unsigned shift=(i&1)*8;uint16_t word=pixel_get_word(i/2);
 pixel_put_word(i/2,(uint16_t)((word&~(255u<<shift))|((unsigned)value<<shift)));return 1;
}
unsigned pixel_owned_bytes(void){return active?4:0;}
void pixel_cold_import(uint8_t *memory){
 active=0;uint32_t base=lin(GAME_SEG,G(SpritePlaneStateScratch));
 for(unsigned i=0;i<2;i++)pixel_put_word(i,(uint16_t)(memory[base+i*2]|memory[base+i*2+1]*256u));
 for(unsigned i=0;i<4;i++)memory[base+i]=0xa5;
 active=1;
}
void pixel_require_seal(const uint8_t *memory){
 if(!active)return;
 uint32_t base=lin(GAME_SEG,G(SpritePlaneStateScratch));
 for(unsigned i=0;i<4;i++)if(memory[base+i]!=0xa5){fputs("pixels: sealed RAM violation\n",stderr);abort();}
}
void pixel_serialize(uint8_t *output){
 if(!active)return;
 uint32_t base=lin(GAME_SEG,G(SpritePlaneStateScratch));unsigned emitted=0;
 for(unsigned i=0;i<4;i++){
#if PIXEL_TEST_FAULT == 5
  if(!i)continue;
#endif
  output[base+i]=(uint8_t)(pixel_get_word(i/2)>>((i&1)*8));emitted++;
 }
 if(emitted!=pixel_owned_bytes()){fputs("pixels: missed serialization\n",stderr);exit(88);}
}
uint32_t pixel_check_serialization(const uint8_t *output){
 if(active){uint32_t base=lin(GAME_SEG,G(SpritePlaneStateScratch));for(unsigned i=0;i<4;i++)if(output[base+i]!=(uint8_t)(pixel_get_word(i/2)>>((i&1)*8)))return base+i;}
 return UINT32_MAX;
}
uint8_t pixel_borrowed_byte(const uint8_t *window,uint32_t index){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE){uint8_t value;if(pixel_shared_read((uint32_t)(p-base+index),&value))return value;}
 return video_pages_borrowed_byte(window,index);
}
void pixel_borrowed_store(uint8_t *window,uint32_t index,uint8_t value){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE && pixel_shared_write((uint32_t)(p-base+index),value))return;
 video_pages_borrowed_store(window,index,value);
}
int pixel_peer(PixelPeerRole role,uint16_t return_identity,Regs *r){
 if(r->cs!=GAME_SEG){uint16_t target;
  switch(role){
  case PIXEL_PEER_DrawTransparentSprite:target=G(DrawTransparentSprite);break;
  case PIXEL_PEER_DrawMapTile:target=G(DrawMapTile);break;
  case PIXEL_PEER_RestoreBackgroundRectangle:target=G(RestoreBackgroundRectangle);break;
  case PIXEL_PEER_RestoreSpriteBackground:target=G(RestoreSpriteBackground);break;
  case PIXEL_PEER_CachePlayerDrawState:target=G(CachePlayerDrawState);break;
  case PIXEL_PEER_DrawHudDigit:target=G(DrawHudDigit);break;
  case PIXEL_PEER_EncodeTwoDecimalDigits:target=G(EncodeTwoDecimalDigits);break;
  case PIXEL_PEER_EncodeFourDecimalDigits:target=G(EncodeFourDecimalDigits);break;
  case PIXEL_PEER_EncodeSixDecimalDigits:target=G(EncodeSixDecimalDigits);break;
  case PIXEL_PEER_RedrawChangedTwoDigitNumber:target=G(RedrawChangedTwoDigitNumber);break;
  case PIXEL_PEER_RedrawChangedFourDigitNumber:target=G(RedrawChangedFourDigitNumber);break;
  case PIXEL_PEER_RedrawChangedSixDigitNumber:target=G(RedrawChangedSixDigitNumber);break;
  case PIXEL_PEER_SamplePlayerCollisionPixels:target=G(SamplePlayerCollisionPixels);break;
  case PIXEL_PEER_NextRandomBelowAx:target=G(NextRandomBelowAx);break;
  case PIXEL_PEER_RespawnRainParticle:target=G(RespawnRainParticle);break;
  case PIXEL_PEER_DrawWaterSurfaceFrame0:target=G(DrawWaterSurfaceFrame0);break;
  case PIXEL_PEER_DrawWaterSurfaceFrame1:target=G(DrawWaterSurfaceFrame1);break;
  case PIXEL_PEER_DrawWaterSurfaceFrame2:target=G(DrawWaterSurfaceFrame2);break;
  default:return UGH_BAD_CALLBACK;
  }
  return pixel_service_continuation(PIXEL_EXTERNAL_NEAR,(PixelExternalBinding){r->cs,target},return_identity,(PixelServiceContext*)r);
 }
 r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,return_identity);int status;
 switch(role){
 case PIXEL_PEER_DrawTransparentSprite:status=c_DrawTransparentSprite(r);break;
 case PIXEL_PEER_DrawMapTile:status=c_DrawMapTile(r);break;
 case PIXEL_PEER_RestoreBackgroundRectangle:status=c_RestoreBackgroundRectangle(r);break;
 case PIXEL_PEER_RestoreSpriteBackground:status=c_RestoreSpriteBackground(r);break;
 case PIXEL_PEER_CachePlayerDrawState:status=c_CachePlayerDrawState(r);break;
 case PIXEL_PEER_DrawHudDigit:status=c_DrawHudDigit(r);break;
 case PIXEL_PEER_EncodeTwoDecimalDigits:status=c_EncodeTwoDecimalDigits(r);break;
 case PIXEL_PEER_EncodeFourDecimalDigits:status=c_EncodeFourDecimalDigits(r);break;
 case PIXEL_PEER_EncodeSixDecimalDigits:status=c_EncodeSixDecimalDigits(r);break;
 case PIXEL_PEER_RedrawChangedTwoDigitNumber:status=c_RedrawChangedTwoDigitNumber(r);break;
 case PIXEL_PEER_RedrawChangedFourDigitNumber:status=c_RedrawChangedFourDigitNumber(r);break;
 case PIXEL_PEER_RedrawChangedSixDigitNumber:status=c_RedrawChangedSixDigitNumber(r);break;
 case PIXEL_PEER_SamplePlayerCollisionPixels:status=c_SamplePlayerCollisionPixels(r);break;
 case PIXEL_PEER_NextRandomBelowAx:status=c_NextRandomBelowAx(r);break;
 case PIXEL_PEER_RespawnRainParticle:status=c_RespawnRainParticle(r);break;
 case PIXEL_PEER_DrawWaterSurfaceFrame0:status=c_DrawWaterSurfaceFrame0(r);break;
 case PIXEL_PEER_DrawWaterSurfaceFrame1:status=c_DrawWaterSurfaceFrame1(r);break;
 case PIXEL_PEER_DrawWaterSurfaceFrame2:status=c_DrawWaterSurfaceFrame2(r);break;
 default:return UGH_BAD_CALLBACK;
 }
 if(status)return status;
 r->sp=(uint16_t)(r->sp+2);return UGH_OK;
}
int pixel_tail(uint16_t target,Regs *r){
 if(r->cs!=GAME_SEG)return pixel_service_continuation(PIXEL_EXTERNAL_TAIL,(PixelExternalBinding){r->cs,target},0,(PixelServiceContext*)r);
 switch(target){
 case G(DrawTransparentSprite):return c_DrawTransparentSprite(r);
 case G(RestoreBackgroundRectangle):return c_RestoreBackgroundRectangle(r);
 case G(DrawWaterSurfaceFrame0):return c_DrawWaterSurfaceFrame0(r);
 case G(DrawWaterSurfaceFrame1):return c_DrawWaterSurfaceFrame1(r);
 case G(DrawWaterSurfaceFrame2):return c_DrawWaterSurfaceFrame2(r);
 default:return pixel_service_continuation(PIXEL_EXTERNAL_TAIL,(PixelExternalBinding){r->cs,target},0,(PixelServiceContext*)r);
 }
}
