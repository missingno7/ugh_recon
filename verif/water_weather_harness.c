#include <stddef.h>
#include <stdint.h>
#ifdef SYMBOLIC
#define CHECK(c,m) __CPROVER_assert((c),(m))
#else
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(c,m) do{if(!(c)){fprintf(stderr,"FAIL %s at%d case%u\n",m,__LINE__,test_number);exit(1);}}while(0)
#endif
#include "pair.inc"
typedef struct WeatherRam {
 uint16_t fixed_y,surface,previous,position,frame,phase,bytes,increment,stride,direction;
 uint16_t particle,particle_previous,modulo;
 uint16_t background,background_segment,draw,draw_segment,table[3],stack[4];
} WeatherRam;
static WeatherRam ram;
static uint16_t slot;
static unsigned test_number,epoch,observations,watch;
static uint16_t random_reply,service_flags,service_di;
static int service_status,modern;
typedef struct WeatherObservation {uint32_t kind,bank,position,value;} WeatherObservation;
#ifdef SYMBOLIC
static WeatherObservation log[2];static int seen[2];
#else
static WeatherObservation log[90000];
#endif
static void observe(unsigned kind,uint16_t bank,uint16_t position,uint16_t value){
 WeatherObservation event={kind,bank,position,value};
#ifdef SYMBOLIC
 if(observations==watch){log[epoch]=event;seen[epoch]=1;}
#else
 CHECK(observations<90000,"observation capacity");
 if(modern)CHECK(!memcmp(&log[observations],&event,sizeof(event)),"ordered stores/ports/reads/services");else log[observations]=event;
#endif
 observations++;
}
void wt_abort(void){CHECK(0,"native bridge consumption/projection");}
static uint16_t *word_at(uint16_t bank,uint16_t address){
 if(bank==DATA_SEG){
  const uint16_t bases[]={D(WaterY32),D(WaterYPixels),D(PreviousWaterSurfaceY),D(WaterSurfaceByteOffset),D(WaterSurfaceFrame),D(WaterStepPhase),D(WaterRestorePending),D(WaterSurfaceStep),D(VgaRowStrideBytes),D(LevelRainDirection)};
  uint16_t *values[]={&ram.fixed_y,&ram.surface,&ram.previous,&ram.position,&ram.frame,&ram.phase,&ram.bytes,&ram.increment,&ram.stride,&ram.direction};
  for(unsigned i=0;i<10;i++)if(address==bases[i])return values[i];
  if(address==(uint16_t)(D(RainParticleOffsets)+slot))return &ram.particle;
  if(address==(uint16_t)(D(RainPreviousOffsets)+slot))return &ram.particle_previous;
  if(address==(uint16_t)(D(RainParticleXModuloFour)+slot))return &ram.modulo;
 }
 if(bank==GAME_SEG){
  if(address==G(BackgroundPagePointer))return &ram.background;if(address==G(BackgroundPagePointer)+2)return &ram.background_segment;
  if(address==G(DrawPagePointer))return &ram.draw;if(address==G(DrawPagePointer)+2)return &ram.draw_segment;
  if(address>=G(WaterSurfaceDispatch) && address<G(WaterSurfaceDispatch)+6 && !((address-G(WaterSurfaceDispatch))&1u))return &ram.table[(address-G(WaterSurfaceDispatch))/2u];
 }
 if(bank==0x9000 && address>=0x7ff8 && address<0x8000 && !(address&1u))return &ram.stack[(address-0x7ff8)/2u];
 CHECK(0,"complete ordinary read/write footprint");return &ram.fixed_y;
}
uint16_t wt_read(uint16_t bank,uint16_t address){return *word_at(bank,address);}
void wt_write(uint16_t bank,uint16_t address,uint16_t value){observe(0,bank,address,value);*word_at(bank,address)=value;}
uint8_t wt_read8(uint16_t bank,uint16_t address){
 if(bank==DATA_SEG){
  if(address==D(WaterRestorePending))return (uint8_t)ram.bytes;
  if(address==D(WaterSurfaceFrameCountdown))return (uint8_t)(ram.bytes>>8);
  if(address==D(WaterStepPhase))return (uint8_t)ram.phase;
  if(address==D(VgaRowStrideBytes))return (uint8_t)ram.stride;
  if(address==D(LevelRainDirection))return (uint8_t)ram.direction;
 }
 uint8_t value=(uint8_t)((address*17u+bank*31u+random_reply)&255u);observe(2,bank,address,value);return value;
}
void wt_write8(uint16_t bank,uint16_t address,uint8_t value){
 observe(1,bank,address,value);
 if(bank==DATA_SEG){
  if(address==D(WaterRestorePending)){ram.bytes=(uint16_t)((ram.bytes&0xff00u)|value);return;}
  if(address==D(WaterSurfaceFrameCountdown)){ram.bytes=(uint16_t)((ram.bytes&255u)|((uint16_t)value<<8));return;}
  if(address==D(WaterStepPhase)){ram.phase=(uint16_t)((ram.phase&0xff00u)|value);return;}
 }
}
void wt_out(uint16_t port,unsigned width,uint32_t value){observe(3,port,(uint16_t)width,(uint16_t)value);}
void wt_mark(Regs *r){
 observe(4,0,(uint16_t)((uint8_t)ram.previous*(uint8_t)ram.stride),80);
 r->ax=random_reply;r->bx=65535;r->dx=0x3cf;r->si=ram.background;r->flags=service_flags;
}
int wt_dispatch(uint16_t bank,uint16_t target,Regs *r){
 observe(5,bank,target,r->ax);observe(6,r->bx,r->cx,r->dx);observe(7,r->ds,r->di,r->si);
 if(target==G(RestoreBackgroundRectangle)){r->di=service_di;r->flags=service_flags;return service_status;}
 CHECK(target==G(DrawWaterSurfaceFrame0) || target==G(DrawWaterSurfaceFrame1) || target==G(DrawWaterSurfaceFrame2),"registered frame target");
#ifdef SYMBOLIC
 set_al(r,15);r->flags=service_flags;r->ds=wt_read(r->ss,r->sp);r->sp=(uint16_t)(r->sp+2);return service_status;
#else
 if(target==G(DrawWaterSurfaceFrame0))return modern?c_DrawWaterSurfaceFrame0(r):reference_c_DrawWaterSurfaceFrame0(r);
 if(target==G(DrawWaterSurfaceFrame1))return modern?c_DrawWaterSurfaceFrame1(r):reference_c_DrawWaterSurfaceFrame1(r);
 return modern?c_DrawWaterSurfaceFrame2(r):reference_c_DrawWaterSurfaceFrame2(r);
#endif
}
int wt_near(uint16_t target,uint16_t ret,Regs *r){
 r->sp=(uint16_t)(r->sp-2);wt_write(r->ss,r->sp,ret);observe(8,r->cs,target,r->ax);int status;
 if(target==G(NextRandomBelowAx)){r->ax=random_reply;r->flags=service_flags;status=service_status;}
 else{CHECK(target==G(RespawnRainParticle),"only rain child");status=modern?c_RespawnRainParticle(r):reference_c_RespawnRainParticle(r);}
 r->ip=wt_read(r->ss,r->sp);r->sp=(uint16_t)(r->sp+2);return status;
}
static int execute(unsigned key,Regs *r){
 switch(key){case 0:return modern?c_AdvanceWaterSurface(r):reference_c_AdvanceWaterSurface(r);case 1:return modern?c_DrawWaterSurface(r):reference_c_DrawWaterSurface(r);
 case 2:return modern?c_DrawWaterSurfaceFrame0(r):reference_c_DrawWaterSurfaceFrame0(r);case 3:return modern?c_DrawWaterSurfaceFrame1(r):reference_c_DrawWaterSurfaceFrame1(r);case 4:return modern?c_DrawWaterSurfaceFrame2(r):reference_c_DrawWaterSurfaceFrame2(r);
 case 5:return modern?c_AdvanceRainParticles(r):reference_c_AdvanceRainParticles(r);case 6:return modern?c_RespawnRainParticle(r):reference_c_RespawnRainParticle(r);case 7:return modern?c_DrawRainParticles(r):reference_c_DrawRainParticles(r);default:return modern?c_RestoreRainBackground(r):reference_c_RestoreRainBackground(r);}
}
#ifndef SYMBOLIC
static uint32_t random_seed=0xc9247193u;
static uint16_t word(void){random_seed=random_seed*1664525u+1013904223u;return (uint16_t)(random_seed>>11);}
static Regs seed(void){Regs r;uint16_t *p=(uint16_t *)&r;for(unsigned i=0;i<14;i++)p[i]=word();r.ds=DATA_SEG;r.cs=GAME_SEG;r.ss=0x9000;r.sp=0x8000;r.bx=slot;r.dx=0x3c5;return r;}
static void initialize(void){uint16_t *p=(uint16_t *)&ram;for(unsigned i=0;i<sizeof(ram)/2;i++)p[i]=word();ram.surface=0;ram.frame=word()%3;ram.table[0]=G(DrawWaterSurfaceFrame0);ram.table[1]=G(DrawWaterSurfaceFrame1);ram.table[2]=G(DrawWaterSurfaceFrame2);ram.draw_segment=0xa000;ram.background_segment=0xa000;service_status=0;random_reply=word();service_flags=word();service_di=word();}
static void compare(unsigned key,Regs r){
 WeatherRam before=ram;Regs a=r,b=r;modern=observations=0;int left=execute(key,&a);WeatherRam after=ram;unsigned count=observations;
 ram=before;modern=1;observations=0;int right=execute(key,&b);
 CHECK(left==right && !memcmp(&a,&b,sizeof(a)),"full register/flags/status");CHECK(observations==count && !memcmp(&after,&ram,sizeof(ram)),"all normalized RAM and transaction length");test_number++;
}
int main(void){
 slot=0;
 for(unsigned value=0;value<65536;value++){
  initialize();ram.fixed_y=(uint16_t)value;ram.bytes&=0xff00u;ram.phase=(uint16_t)((ram.phase&0xff00u)|1u);compare(0,seed());
  initialize();ram.surface=(uint16_t)value;ram.frame=word()%3;ram.bytes=0x0600;compare(1,seed());
  initialize();random_reply=(uint16_t)value;compare(6,seed());
  initialize();ram.modulo=(uint16_t)value;compare(7,seed());
  initialize();ram.surface=65535;ram.particle=(uint16_t)value;compare(5,seed());
 }
 for(unsigned i=0;i<20000;i++){
  initialize();ram.bytes=(uint16_t)(word()&0xff00u);ram.fixed_y=word();ram.surface=word();ram.increment=word();ram.phase=word();compare(0,seed());
  initialize();ram.bytes=word();compare(1,seed());
  initialize();ram.surface=65535;ram.modulo=word();ram.particle=word();compare(5,seed());
  initialize();Regs r=seed();r.sp=0x7ffe;r.bx=word();compare(2+i%3,r);
  initialize();ram.surface=65535;compare(8,seed());
 }
 printf("PASS %u complete C comparisons; five full-word slices and full frame/service transactions\n",test_number);return 0;
}
#endif
