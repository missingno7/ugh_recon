/* Disjoint word-normalized selected player and resources, not byte RAM.
 * Full word scalars; two physical indices exercised by compiled cases. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define CHECK(c,m) do {if(!(c)){fprintf(stderr,"FAIL %s line %d test %u\n",m,__LINE__,test_number);exit(1);}}while(0)
#include "pair.inc"
typedef struct PhysicsRam {
 uint16_t player[13],timer,water,fade_rate,fade_level,stride,difficulty,limits[3],rain;
 uint16_t platform[10][3],page,segment,stack[4];
} PhysicsRam;
static PhysicsRam ram;
static uint16_t actor_index;
static unsigned test_number,modern,observations,pattern,read_number;
typedef struct Observation {uint32_t kind,address,value;} Observation;
static Observation expected[50000];
static const uint16_t player_base[]={D(PlayerX32),D(PlayerY32),D(PlayerPixelX),D(PlayerYPixels),D(PlayerPlatformIndices),
 D(PlayerHorizontalVelocities),D(PlayerVerticalVelocities),D(PlayerImpactMagnitude),D(PlayerThrustAnimationRate),
 D(PlayerLeftInput),D(PlayerRightInput),D(PlayerUpInput),D(PlayerDownInput)};
static void observe(unsigned kind,uint32_t address,uint32_t value) {
 CHECK(observations<50000,"observation capacity");Observation event={kind,address,value};
 if(modern)CHECK(!memcmp(&expected[observations],&event,sizeof(event)),"ordered observation equality");
 else expected[observations]=event;
 observations++;
}
void px_abort(void){CHECK(0,"bridge consumption/projection");}
uint16_t px_read(uint16_t bank,uint16_t address) {
 if(bank==DATA_SEG) {
  for(unsigned i=0;i<13;i++)if(address==(uint16_t)(player_base[i]+actor_index))return ram.player[i];
  const uint16_t globals[]={D(LevelTimer),D(WaterYPixels),D(ScreenFadeStep),D(ScreenFadeLevel),D(VgaRowStrideBytes),D(SelectedDifficulty)};
  uint16_t *values[]={&ram.timer,&ram.water,&ram.fade_rate,&ram.fade_level,&ram.stride,&ram.difficulty};
  for(unsigned i=0;i<6;i++)if(address==globals[i])return *values[i];
  for(unsigned i=0;i<3;i++)if(address==D(PlayerImpactLimits)+2u*i)return ram.limits[i];
  for(unsigned i=0;i<10;i++)for(unsigned j=0;j<3;j++) {
   const uint16_t bases[]={D(PlatformLeftEdges),D(PlatformRightEdges),D(PlatformHeights)};
   if(address==bases[j]+2u*i)return ram.platform[i][j];
  }
 }
 if(bank==GAME_SEG) {
  if(address==G(BackgroundPagePointer))return ram.page;
  if(address==G(BackgroundPagePointer)+2u)return ram.segment;
 }
 if(bank==0x9000 && address>=0x7ff8 && address<0x8000 && !(address&1u))return ram.stack[(address-0x7ff8)/2u];
 CHECK(0,"read footprint");return 0;
}
uint8_t px_read8(uint16_t bank,uint16_t address) {
 if(bank==DATA_SEG && address==D(LevelRainDirection))return (uint8_t)ram.rain;
 unsigned bit=read_number++%10u;
 uint32_t hash=(uint32_t)address*2654435761u+(uint32_t)bank*1103515245u+pattern*1664525u;
 uint8_t value=(uint8_t)((hash>>24)&127u);
 /* The first 1024 schedules cover every ten-sample collision mask. Later
  * schedules depend on location, so a wrong scan direction/address matters. */
 if(pattern<1024u)value|=(uint8_t)(((pattern>>bit)&1u)*128u);
 else value|=(uint8_t)((hash>>15)&128u);
 observe(2,((uint32_t)bank<<16)|address,value);return value;
}
void px_write(uint16_t bank,uint16_t address,uint16_t value) {
 observe(0,((uint32_t)bank<<16)|address,value);
 if(bank==DATA_SEG) {
  for(unsigned i=0;i<13;i++)if(address==(uint16_t)(player_base[i]+actor_index)){ram.player[i]=value;return;}
  if(address==D(LevelTimer)){ram.timer=value;return;}if(address==D(ScreenFadeStep)){ram.fade_rate=value;return;}
  if(address==D(ScreenFadeLevel)){ram.fade_level=value;return;}
 }
 if(bank==0x9000 && address>=0x7ff8 && address<0x8000 && !(address&1u)){ram.stack[(address-0x7ff8)/2u]=value;return;}
 CHECK(0,"write footprint");
}
void px_out(uint16_t port,unsigned width,uint32_t value) {observe(1,port,value|((uint32_t)width<<16));}
int px_near(uint16_t target,uint16_t return_word,Regs *r) {
 CHECK(target==G(SamplePlayerCollisionPixels),"single callee");
 r->sp=(uint16_t)(r->sp-2u);px_write(r->ss,r->sp,return_word);
 int status=modern?c_SamplePlayerCollisionPixels(r):reference_c_SamplePlayerCollisionPixels(r);
 r->ip=px_read(r->ss,r->sp);r->sp=(uint16_t)(r->sp+2u);return status;
}
static uint32_t random_state=0x84627931u;
static uint16_t word(void){random_state=random_state*1664525u+1013904223u;return (uint16_t)(random_state>>13);}
static Regs seed(void){Regs r;uint16_t *at=(uint16_t *)&r;for(unsigned i=0;i<14;i++)at[i]=word();r.cs=GAME_SEG;r.ds=DATA_SEG;r.ss=0x9000;r.sp=0x8000;r.bx=actor_index;return r;}
static void compare(Regs initial,int sampler) {
 PhysicsRam before=ram;Regs a=initial,b=initial;modern=0;observations=read_number=0;
 int left=sampler?reference_c_SamplePlayerCollisionPixels(&a):reference_c_MovePlayerWithVgaCollisions(&a);
 PhysicsRam after=ram;unsigned count=observations;ram=before;modern=1;observations=read_number=0;
 int right=sampler?c_SamplePlayerCollisionPixels(&b):c_MovePlayerWithVgaCollisions(&b);
 CHECK(left==right && !memcmp(&a,&b,sizeof(a)),"status and complete register/flag equality");
 CHECK(observations==count && !memcmp(&ram,&after,sizeof(ram)),"complete normalized RAM and event count");test_number++;
}
static void initialize(void) {
 memset(&ram,0,sizeof(ram));ram.water=192;ram.stride=96;ram.segment=0xa000;ram.limits[0]=1380;ram.limits[1]=2300;ram.limits[2]=3100;
 ram.player[0]=3200;ram.player[1]=1600;ram.player[2]=100;ram.player[3]=50;ram.player[4]=65535;
 ram.platform[0][0]=65535;ram.fade_rate=0;ram.fade_level=64;ram.timer=140;
}
#ifndef PLAYER_PHYSICS_NO_MAIN
int main(void) {
 const uint16_t edges[]={0,1,2,31,32,63,64,127,128,191,192,193,255,256,257,608,6111,6112,6113,6143,6144,6145,9727,9728,9729,32767,32768,65503,65504,65534,65535,0xe7ff,0xe800,0xe801,0xfda0,0xfe00};
 for(unsigned i=0;i<65536u;i++) {
  CHECK(player_physics_limit((uint16_t)i)==reference_limit_velocity((uint16_t)i),"full word clamp");
  for(unsigned n=1;n<=15;n++)CHECK(player_physics_sar((uint16_t)i,n)==reference_sar((uint16_t)i,n),"full word SAR");
  uint16_t speed=(uint16_t)i;uint16_t magnitude=player_physics_reflect(&speed);initialize();ram.player[5]=(uint16_t)i;Regs r=seed();reference_reflect_velocity(&r,D(PlayerHorizontalVelocities));
  CHECK(speed==ram.player[5] && magnitude==r.ax,"full word reflection and magnitude");observations=0;
 }
 for(unsigned mask=0;mask<1024;mask++)for(unsigned axis=0;axis<4;axis++) {
  initialize();actor_index=(uint16_t)(2u*(mask&1u));pattern=mask;
  ram.player[axis&1u?6:5]=(axis&2u)?(uint16_t)-6144:6144;compare(seed(),0);
 }
 /* Whole-handler word slices, holding the remaining input at declared seeds. */
 for(unsigned field=0;field<7;field++)for(unsigned i=0;i<65536u;i++) {
  initialize();actor_index=(uint16_t)(2u*(i&1u));pattern=1024u+(i%997u);
  switch(field){case 0:ram.player[5]=(uint16_t)i;break;case 1:ram.player[6]=(uint16_t)i;break;
   case 2:ram.timer=(uint16_t)i;break;case 3:ram.water=(uint16_t)i;break;
   case 4:ram.fade_rate=(uint16_t)i;ram.limits[0]=0;break;case 5:ram.limits[0]=(uint16_t)i;break;
   case 6:ram.player[4]=(uint16_t)i;break;}
  compare(seed(),0);
 }
 for(unsigned t=0;t<8000;t++) {
  initialize();actor_index=(uint16_t)(2u*(t&1u));pattern=1024u+t;
  for(unsigned i=0;i<13;i++)ram.player[i]=word();ram.timer=word();ram.water=word();ram.rain=word()&255u;
  ram.fade_rate=word();ram.fade_level=word();ram.stride=word();ram.page=word();ram.segment=word();ram.difficulty=word()%3u;
  for(unsigned i=0;i<3;i++)ram.limits[i]=word();
  for(unsigned i=0;i<9;i++){ram.platform[i][0]=word()&32767u;ram.platform[i][1]=word();ram.platform[i][2]=word();}
  ram.platform[9][0]=65535;compare(seed(),0);
 }
 for(unsigned i=0;i<sizeof(edges)/sizeof(edges[0]);i++)for(unsigned j=0;j<sizeof(edges)/sizeof(edges[0]);j++) {
  initialize();actor_index=0;pattern=1024u+i*36u+j;
  ram.player[0]=edges[i];ram.player[2]=edges[j];ram.player[1]=edges[j];ram.player[3]=edges[i];
  ram.player[5]=edges[j];ram.player[6]=edges[i];ram.player[11]=ram.player[12]=65535;compare(seed(),0);
  Regs r=seed();r.es=edges[i];r.si=edges[j];compare(r,1);
 }
 printf("PASS %u complete C comparisons; 7 full word whole-handler slices; all 1024 collision masks in four directions; 65536 clamp/reflection and 15 SAR slices\n",test_number);
 return 0;
}
#endif
