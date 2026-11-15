#include "platform.h"
#include "presentation_world_bridge.h"
#include "pixel_world_bridge.h"
#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
typedef struct PresentationField {uint32_t address;size_t member;unsigned width,count,stride;} PresentationField;
#define A(n) (((uint32_t)DATA_SEG<<4)+D(n))
#define MEMBER(m) ((size_t)&((NativePresentationWorld*)0)->m)
#define WORD(n,m) {A(n),MEMBER(m),2,1,2}
#define BYTE(n,m) {A(n),MEMBER(m),1,1,1}
static const PresentationField fields[]={
 {A(DecimalDigitBuffer),MEMBER(hud.digits),1,14,1},
 WORD(CachedTimerBarWidth,hud.timer_width),WORD(HudDigitCursorX,hud.cursor_x),WORD(HudDigitCursorY,hud.cursor_y),
 {A(HudLivesX),MEMBER(hud.layout_x),2,9,2},
 {A(HudCachedScoreLow),MEMBER(hud.score_words),2,2,2},
 WORD(HudCachedFare,hud.fare),WORD(ds_27C8,hud.retained_seed),
 BYTE(HudCachedMultiplier,hud.multiplier),BYTE(HudCachedLives,hud.lives),
 BYTE(HudCachedLevelCounter,hud.counter),BYTE(HudFareClearPending,hud.fare_pending),
 {A(HudCachedPlayerOneIconState),MEMBER(hud.icons),2,2,2},
 BYTE(WaterRestorePending,weather.pending),BYTE(WaterSurfaceFrameCountdown,weather.countdown),
 WORD(WaterSurfaceFrame,weather.frame),BYTE(WaterStepPhase,weather.phase),
 WORD(PreviousWaterSurfaceY,weather.previous_y),WORD(WaterSurfaceByteOffset,weather.byte_offset),
 {A(RainParticleOffsets),MEMBER(weather.rain[0].position),2,193,sizeof(NativeRainRecord)},
 {A(RainPreviousOffsets),MEMBER(weather.rain[0].previous),2,193,sizeof(NativeRainRecord)},
 {A(RainParticleXModuloFour),MEMBER(weather.rain[0].modulo),2,193,sizeof(NativeRainRecord)}
};
static unsigned active;
static int presentation_field(uint32_t address,unsigned *slot,unsigned *lane){
 uint32_t base=(uint32_t)DATA_SEG<<4;
 if(address<base)return 0;
 uint32_t offset=address-base;
 if(!((offset>=0xc8 && offset<0xd6) || (offset>=0x27a2 && offset<0x27d0) ||
      (offset>=0x2800 && offset<0x2804) || (offset>=0x2905 && offset<0x2909) ||
      (offset>=0x2e8b && offset<0x3311)))return 0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)if(address>=fields[i].address && address-fields[i].address<fields[i].width*fields[i].count){*slot=i;*lane=(unsigned)(address-fields[i].address);return 1;}
 return 0;
}
static uint8_t presentation_field_get(const PresentationField *field,unsigned lane){
 uint8_t *p=(uint8_t*)native_presentation_world()+field->member+(lane/field->width)*field->stride;
 if(field->width==1)return *p;
 uint16_t value;memcpy(&value,p,2);return (uint8_t)(value>>((lane&1)*8));
}
static void presentation_field_put(const PresentationField *field,unsigned lane,uint8_t value){
 uint8_t *p=(uint8_t*)native_presentation_world()+field->member+(lane/field->width)*field->stride;
 if(field->width==1){*p=value;return;}
 uint16_t word;memcpy(&word,p,2);unsigned shift=(lane&1)*8;
 word=(uint16_t)((word&~(255u<<shift))|((unsigned)value<<shift));memcpy(p,&word,2);
}
int presentation_is_owned(uint32_t address){unsigned slot,lane;return active && presentation_field(address,&slot,&lane);}
int presentation_shared_read(uint32_t address,uint8_t *value){unsigned slot,lane;if(!active || !presentation_field(address,&slot,&lane))return 0;*value=presentation_field_get(fields+slot,lane);return 1;}
int presentation_shared_write(uint32_t address,uint8_t value){
 unsigned slot,lane;if(!active || !presentation_field(address,&slot,&lane))return 0;
#if PRESENTATION_TEST_FAULT == 1
 if(address==A(HudCachedLives))return 1;
#endif
#if PRESENTATION_TEST_FAULT == 3
 if(fields[slot].address==A(RainParticleXModuloFour) && !(lane&1))value=(uint8_t)((value+1)&3);
#endif
 presentation_field_put(fields+slot,lane,value);return 1;
}
unsigned presentation_owned_bytes(void){return active?1221:0;}
void presentation_cold_import(uint8_t *memory){
 active=0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)presentation_field_put(fields+i,lane,memory[fields[i].address+lane]);
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)memset(memory+fields[i].address,0xa5,fields[i].width*fields[i].count);
 active=1;
}
void presentation_require_seal(const uint8_t *memory){
 if(!active)return;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)if(memory[fields[i].address+lane]!=0xa5){fputs("presentation: sealed RAM violation\n",stderr);abort();}
}
void presentation_serialize(uint8_t *output){
 if(!active)return;
 unsigned emitted=0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++){
#if PRESENTATION_TEST_FAULT == 4
  if(!i && !lane)continue;
#endif
  output[fields[i].address+lane]=presentation_field_get(fields+i,lane);emitted++;
 }
 if(emitted!=presentation_owned_bytes()){fputs("presentation: missed serialization\n",stderr);exit(88);}
}
uint32_t presentation_check_serialization(const uint8_t *output){
 if(active)for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)if(output[fields[i].address+lane]!=presentation_field_get(fields+i,lane))return fields[i].address+lane;
 return UINT32_MAX;
}
uint8_t presentation_borrowed_byte(const uint8_t *window,uint32_t index){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE){uint8_t value;if(presentation_shared_read((uint32_t)(p-base+index),&value))return value;}
 return pixel_borrowed_byte(window,index);
}
void presentation_borrowed_store(uint8_t *window,uint32_t index,uint8_t value){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE && presentation_shared_write((uint32_t)(p-base+index),value))return;
 pixel_borrowed_store(window,index,value);
}
