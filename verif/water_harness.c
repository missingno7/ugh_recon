/* Word-normalized disjoint RAM. Other physical slots fail the footprint;
 * scalar frame profiles separately observe an arbitrary other RAM byte. */
#ifdef __CPROVER__
void __CPROVER_assert(_Bool,const char *);void __CPROVER_assume(_Bool);
#define CHECK(c,m) __CPROVER_assert((c),(m))
#else
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(c,m) do {if(!(c)) {fprintf(stderr,"%s line%d mode%u case%llu\n",m,__LINE__,operation,comparisons);exit(23);}} while(0)
#endif
typedef struct WaterRam {uint16_t actor[24],type[37],craft[4][2],occupants[10],frames[4][3],surface,players;} WaterRam;
typedef struct WaterStore {uint16_t address,value;} WaterStore;
static WaterRam ram;static WaterStore stores[32];static unsigned store_count,expected_count;
static uint16_t actor_index,type_base;static int modern_calls;static unsigned tail_calls;static uint16_t tail_target,tail_craft;
static unsigned operation;static unsigned long long comparisons;
static uint16_t watched_bank,watched_offset;static uint8_t watched_value;static int watching;
static const uint16_t craft_bases[]={D(PlayerPixelX),D(PlayerYPixels),D(PlayerVerticalVelocities),D(PlayerCarriedKinds)};
static const uint16_t vectors[]={0x0e20,0x0e28,0x0e30,0x0e38};
#ifdef GENERAL_FRAME
static uint16_t general_base;static size_t general_count;static uint16_t *general_words;
#endif
uint16_t wa_read(uint16_t bank,uint16_t address) {
 CHECK(bank==DATA_SEG,"water ordinary data bank");
 if(address>=D(ActorDescriptors) && address<D(ActorDescriptors)+768u) {
  unsigned delta=address-D(ActorDescriptors);CHECK(delta%32u==actor_index,"only selected actor read");return ram.actor[delta/32u];
 }
 if(address>=type_base && address<type_base+74u) {CHECK(!((address-type_base)&1u),"type alignment");return ram.type[(address-type_base)/2u];}
 for(unsigned i=0;i<4;i++) if(address>=craft_bases[i] && address<craft_bases[i]+4u) {CHECK(!((address-craft_bases[i])&1u),"craft alignment");return ram.craft[i][(address-craft_bases[i])/2u];}
 if(address>=D(PlatformActorOccupants) && address<D(PlatformActorOccupants)+20u) {CHECK(!((address-D(PlatformActorOccupants))&1u),"platform alignment");return ram.occupants[(address-D(PlatformActorOccupants))/2u];}
#ifdef GENERAL_FRAME
 if(general_words && address>=general_base && (uint32_t)address<=(uint32_t)general_base+2u*general_count) {CHECK(!((address-general_base)&1u),"general frame alignment");return general_words[(address-general_base)/2u];}
#endif
 for(unsigned i=0;i<4;i++) if(address>=vectors[i] && address<vectors[i]+6u) {CHECK(!((address-vectors[i])&1u),"frame alignment");return ram.frames[i][(address-vectors[i])/2u];}
 if(address==D(WaterYPixels)) return ram.surface;if(address==D(PlayerCount)) return ram.players;
 CHECK(0,"water read footprint");return 0;
}
void wa_write(uint16_t bank,uint16_t address,uint16_t value) {
 CHECK(bank==DATA_SEG,"water write bank");CHECK(store_count<32,"water finite journal");
 if(modern_calls) {CHECK(store_count<expected_count,"no extra store");CHECK(stores[store_count].address==address && stores[store_count].value==value,"all ordered water stores");}
 else stores[store_count]=(WaterStore){address,value};
 store_count++;
 if(watching && bank==watched_bank) {if(watched_offset==address) watched_value=(uint8_t)value;if(watched_offset==(uint16_t)(address+1u)) watched_value=(uint8_t)(value>>8);}
 if(address>=D(ActorDescriptors) && address<D(ActorDescriptors)+768u) {
  unsigned delta=address-D(ActorDescriptors);CHECK(delta%32u==actor_index,"only selected actor written");ram.actor[delta/32u]=value;return;
 }
 if(address>=D(PlatformActorOccupants) && address<D(PlatformActorOccupants)+20u) {CHECK(!((address-D(PlatformActorOccupants))&1u),"occupant alignment");ram.occupants[(address-D(PlatformActorOccupants))/2u]=value;return;}
 CHECK(0,"water write footprint");
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r) {
 CHECK(bank==GAME_SEG,"water immediate tail bank");
 CHECK(target==G(BeginPassengerFloating) || target==G(BeginPassengerSinking) || target==G(BeginPassengerDestinationDisplay) || target==G(BeginPassengerQuestionDisplay) || target==G(BeginPassengerApproach) || target==G(BoardWaterbornePassenger),"complete water immediate target set");
 tail_calls++;tail_target=target;tail_craft=r->di;return UGH_CONTROL_TRANSFER;
}
static int execute(unsigned mode,Regs *r,int native) {
 modern_calls=native;
 switch(mode) {
 case 0:return native?c_BeginPassengerResurfacing(r):l1_BeginPassengerResurfacing(r);
 case 1:return native?c_UpdatePassengerResurfacing(r):l1_UpdatePassengerResurfacing(r);
 case 2:return native?c_BeginPassengerSinking(r):l1_BeginPassengerSinking(r);
 case 3:return native?c_UpdatePassengerSinking(r):l1_UpdatePassengerSinking(r);
 case 4:return native?c_BeginPassengerFloating(r):l1_BeginPassengerFloating(r);
 case 5:return native?c_UpdatePassengerFloating(r):l1_UpdatePassengerFloating(r);
 case 6:return native?c_UpdateFloatingDestinationDisplay(r):l1_UpdateFloatingDestinationDisplay(r);
 case 7:return native?c_UpdateFloatingQuestionDisplay(r):l1_UpdateFloatingQuestionDisplay(r);
 case 8:return native?c_UpdateFloatingPassengerApproach(r):l1_UpdateFloatingPassengerApproach(r);
 default:return native?c_IgnoreWaterbornePassengerState(r):l1_IgnoreWaterbornePassengerState(r);
 }
}
static void configure(unsigned pair) {
 type_base=(uint16_t)(D(Data_7720)+74u*(2u*pair+1u));ram.actor[0]=type_base;
 const uint16_t callbacks[]={G(BeginPassengerResurfacing),G(UpdatePassengerResurfacing),G(BeginPassengerSinking),G(UpdatePassengerSinking),G(BeginPassengerFloating),G(UpdatePassengerFloating),G(BeginPassengerDestinationDisplay),G(UpdateFloatingDestinationDisplay),G(BeginPassengerQuestionDisplay),G(UpdateFloatingQuestionDisplay),G(BeginPassengerApproach),G(UpdateFloatingPassengerApproach),G(BoardWaterbornePassenger)};
 for(unsigned i=0;i<13;i++) ram.type[4+i]=callbacks[i];ram.type[22]=G(IgnoreActorState);ram.type[36]=(uint16_t)(type_base-74u);
 for(unsigned i=0;i<4;i++) {ram.type[23+i]=vectors[i];ram.frames[i][2]=65535u;}
}
static void seed_view(WaterPlan *plan,ActorPhase phase) {
 PassengerStoneSlot slot;ActorType type;ActorRenderHistory render;plan->slot=slot;plan->type=type;plan->render=render;
 CHECK(actor_bridge_alias_project(DATA_SEG,actor_index/2u,phase,&plan->slot),"input active-alias projection");
 plan->slot.type=&plan->type;plan->type.id=(ActorTypeId)((type_base-D(Data_7720))/74u);
 plan->type.geometry=(ObjectGeometry){ram.type[0],ram.type[1],ram.type[2],ram.type[3]};plan->type.animation_period=ram.type[31];plan->type.floating_lifetime=ram.type[34];
 for(unsigned i=0;i<4;i++) plan->type.animations[i]=(ActorAnimation){ram.frames[i],2};
 plan->slot.source_platform=ram.actor[5];plan->slot.destination_platform=ram.actor[6];plan->slot.position=(ObjectPosition){ram.actor[10],ram.actor[11]};
 plan->slot.sprite=ram.actor[18];plan->slot.overlay_sprite=ram.actor[20];plan->slot.animation=(ActorAnimationState){ram.actor[16],ram.actor[17]};
 plan->slot.vertical_motion=ram.actor[22];plan->slot.quick_delivery_ticks=ram.actor[23];plan->render.pixel_x=ram.actor[12];plan->render.pixel_y=ram.actor[14];
 plan->world.surface_y=ram.surface;plan->world.player_count=ram.players;plan->world.platform_count=10;
 for(unsigned i=0;i<2;i++) plan->world.craft[i]=(WaterCraft){ram.craft[0][i],ram.craft[1][i],ram.craft[2][i],ram.craft[3][i]};
 plan->result=(PassengerWaterResult){0};plan->result.selected=-1;plan->consumed=0;plan->bad=plan->tail_seen=plan->phase_written=0;plan->published_phase=phase;plan->actor_index=actor_index;
}
#ifndef PIECE
static void compare(unsigned mode,Regs r) {
 operation=mode;WaterRam initial=ram;Regs ref=r;store_count=tail_calls=0;int expected=execute(mode,&ref,0);WaterRam after=ram;
 unsigned stores_before=store_count,tails=tail_calls;uint16_t target=tail_target,craft=tail_craft;ram=initial;expected_count=stores_before;store_count=tail_calls=wa_fallback=0;
 int actual=execute(mode,&r,1);CHECK(!wa_fallback,"admitted water step has zero fallback");
 CHECK(actual==expected && store_count==stores_before && tail_calls==tails && (!tails || (tail_target==target && tail_craft==craft)),"complete tail/status/store observations");
 for(unsigned i=0;i<24;i++) CHECK(after.actor[i]==ram.actor[i],"all actor words and histories");
 for(unsigned i=0;i<10;i++) CHECK(after.occupants[i]==ram.occupants[i],"all occupants");
 CHECK(r.ax==ref.ax && r.bx==ref.bx && r.cx==ref.cx && r.dx==ref.dx && r.si==ref.si && r.di==ref.di && r.bp==ref.bp && r.sp==ref.sp && r.cs==ref.cs && r.ds==ref.ds && r.es==ref.es && r.ss==ref.ss && r.ip==ref.ip && r.flags==ref.flags,"all registers flags continuation");comparisons++;
}
static Regs seed(unsigned pair) {
 memset(&ram,0,sizeof(ram));actor_index=0;configure(pair);ram.players=2;ram.surface=96;ram.actor[5]=1;ram.actor[6]=2;ram.actor[7]=2;ram.actor[8]=4;
 ram.actor[10]=3000;ram.actor[11]=3000;ram.actor[12]=90;ram.actor[14]=100;ram.actor[16]=0;ram.actor[17]=1;ram.actor[9]=3;
 ram.type[0]=8;ram.type[1]=3;ram.type[31]=7;ram.type[34]=700;
 for(unsigned i=0;i<4;i++) for(unsigned j=0;j<2;j++) ram.frames[i][j]=(uint16_t)(100+4*i+j);
 ram.craft[0][0]=100;ram.craft[0][1]=200;ram.craft[1][0]=ram.craft[1][1]=0;
 Regs r={0};r.ds=DATA_SEG;r.cs=GAME_SEG;r.ss=1;r.sp=36864u;return r;
}
static uint32_t random_state=0x2e1905u;
static uint16_t random_word(void) {random_state=random_state*1664525u+1013904223u;return (uint16_t)(random_state>>8);}
int main(void) {
 for(unsigned slice=0;slice<8;slice++) for(unsigned value=0;value<65536;value++) {
  Regs r=seed(value%3u);unsigned mode=1;
  if(slice==0) ram.actor[22]=(uint16_t)value;
  if(slice==1) ram.actor[11]=(uint16_t)value;
  if(slice==2) ram.actor[14]=(uint16_t)value;
  if(slice==3) {mode=3;ram.actor[22]=(uint16_t)value;}
  if(slice==4) {mode=3;ram.actor[11]=(uint16_t)value;}
  if(slice==5) {mode=5;ram.actor[9]=(uint16_t)value;}
  if(slice==6) {mode=7;ram.actor[4]=(uint16_t)value;}
  if(slice==7) {mode=8;ram.actor[12]=(uint16_t)value;ram.craft[1][0]=78;}
  compare(mode,r);
 }
 for(unsigned test=0;test<12000;test++) for(unsigned mode=0;mode<10;mode++) {
  unsigned pair=test%3u;Regs r=seed(pair);actor_index=(uint16_t)(2u*(test%16u));r.bx=actor_index;
  for(unsigned i=0;i<24;i++) if(i!=0 && i!=5 && i!=6 && i!=7 && i!=8 && i!=16 && i!=17) ram.actor[i]=random_word();
  for(unsigned i=0;i<4;i++) for(unsigned j=0;j<2;j++) ram.craft[i][j]=random_word();
  for(unsigned i=0;i<4;i++) ram.type[i]=random_word();ram.type[31]=random_word();ram.type[34]=random_word();ram.surface=random_word();ram.players=(uint16_t)(1u+(test&1u));
  ram.actor[17]=test%4u==0?1:random_word();ram.actor[16]=(uint16_t)(2u*(test%3u));if(ram.actor[17]==1 && test%3u==2) ram.actor[16]=65534u;
  r.flags=random_word();r.ax=random_word();r.cx=random_word();r.dx=random_word();r.di=random_word();r.si=random_word();r.bp=random_word();r.es=random_word();r.ip=random_word();
  compare(mode,r);
 }
 printf("PASS %llu water comparisons: eight complete word slices and12000x10 arbitrary states/all16 slots/all3 pairs\n",comparisons);return 0;
}
#endif
