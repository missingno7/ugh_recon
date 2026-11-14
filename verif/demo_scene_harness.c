/* Small disjoint word RAM and synchronous service cuts. No simulation hook is
 * used in whole-game evidence. These arbitrary service outputs are a relational
 * boundary, not an implementation/model of palette, input, audio or scripts. */
#ifdef __CPROVER__
void __CPROVER_assert(_Bool,const char *);void __CPROVER_assume(_Bool);
#define CHECK(c,m) __CPROVER_assert((c),(m))
#define PS_LOG_LIMIT 16
#else
#include <stdio.h>
#include <stdlib.h>
#define CHECK(c,m) do {if(!(c)) {fprintf(stderr,"%s line%d op%u case%llu\n",m,__LINE__,operation,comparisons);exit(23);}} while(0)
#define PS_LOG_LIMIT 256
#endif
static unsigned operation,modern,observations,expected_observations,service_count,frames;
static unsigned long long comparisons;
static uint16_t ram[38],actor_index,width_bank=0x6000,width_offset=0x100;
static uint8_t width_byte;
static uint16_t bases[6]={D(ScreenFadeLevel),D(ScreenFadeStep),D(DemoExitCode),D(WaterYPixels),D(ActorSpriteIds),D(ActorX32)};
static int cut_services,cut_status;
static Regs arbitrary_after,last_after;
static uint16_t arbitrary_ram[4];
static unsigned response_mode;
static uint16_t last_target,last_return,last_bank;
static DemoPresentationInput observed_before;
static DemoPresentationKind kind_before;
typedef struct SceneObservation {unsigned kind;uint16_t bank,address,value,ret;Regs registers;uint16_t globals[4];} SceneObservation;
#ifdef __CPROVER__
static unsigned observe_index;
static SceneObservation expected[1];
#else
static SceneObservation expected[PS_LOG_LIMIT];
#endif
static int equal_regs(Regs a,Regs b) {
 return a.ax==b.ax && a.bx==b.bx && a.cx==b.cx && a.dx==b.dx && a.si==b.si && a.di==b.di && a.bp==b.bp && a.sp==b.sp && a.cs==b.cs && a.ds==b.ds && a.es==b.es && a.ss==b.ss && a.ip==b.ip && a.flags==b.flags;
}
void ps_abort(void) {CHECK(0,"bridge rejection is a failed property");
#ifdef __CPROVER__
 __CPROVER_assume(0);
#else
 exit(23);
#endif
}
static void observe(unsigned kind,uint16_t bank,uint16_t address,uint16_t value,uint16_t ret,Regs *registers) {
 CHECK(observations<PS_LOG_LIMIT,"finite observation journal");SceneObservation event={0};event.kind=kind;event.bank=bank;event.address=address;event.value=value;event.ret=ret;
 if(registers)event.registers=*registers;for(unsigned i=0;i<4;i++)event.globals[i]=ram[i];
 #ifdef __CPROVER__
 if(observations!=observe_index){observations++;return;}unsigned index=0;
 #else
 unsigned index=observations;
 #endif
 if(modern) {
  CHECK(observations<expected_observations,"no extra event");SceneObservation old=expected[index];
  CHECK(event.kind==old.kind && event.bank==old.bank && event.address==old.address && event.value==old.value && event.ret==old.ret,"all ordered stores/service identities/frames");
  CHECK(equal_regs(event.registers,old.registers),"complete registers at every service cut");
  for(unsigned i=0;i<4;i++)CHECK(event.globals[i]==old.globals[i],"fresh RAM at each cut");
 } else expected[index]=event;
 observations++;
}
uint16_t ps_read(uint16_t bank,uint16_t address) {
 if(bank==DATA_SEG) {
  for(unsigned i=0;i<6;i++)if(address==(uint16_t)(bases[i]+(i>=4?actor_index:0)))return ram[i];
  if(address==D(ActorX32))return ram[5];
 }
 if(bank==GAME_SEG) {if(address==G(DemoRevealWidthPointer))return width_offset;if(address==(uint16_t)(G(DemoRevealWidthPointer)+2))return width_bank;}
 if(bank==0x9000 && address>=0xfc0 && address<0x1000 && !(address&1u))return ram[6+(address-0xfc0)/2u];
 CHECK(0,"declared word read footprint");return 0;
}
uint8_t ps_read8(uint16_t bank,uint16_t address) {CHECK(bank==width_bank && address==width_offset,"byte input footprint");return width_byte;}
void ps_write(uint16_t bank,uint16_t address,uint16_t value) {
 observe(0,bank,address,value,0,0);
 if(bank==DATA_SEG) {
  for(unsigned i=0;i<3;i++)if(address==bases[i]){ram[i]=value;return;}
  if(address==D(ActorX32)){ram[5]=value;return;}
 }
 if(bank==0x9000 && address>=0xfc0 && address<0x1000 && !(address&1u)){ram[6+(address-0xfc0)/2u]=value;return;}
 CHECK(0,"declared word store footprint");
}
void ps_write8(uint16_t bank,uint16_t address,uint8_t value) {
 observe(1,bank,address,value,0,0);CHECK(bank==width_bank && address==width_offset,"only the requested far byte");width_byte=value;
}
static int service(uint16_t bank,uint16_t target,uint16_t ret,Regs *r,unsigned transfer) {
 observe(2+transfer,bank,target,0,ret,r);last_bank=bank;last_target=target;last_return=ret;service_count++;
 if(cut_services) {
  Regs after=arbitrary_after;
  /* A nonlocal/error prefix can change even the caller bindings. Only normal
   * return seams require their ordinary CS/DS/SS:SP service contract. */
  if(!cut_status){after.cs=r->cs;after.ds=r->ds;after.ss=r->ss;after.sp=r->sp;}*r=after;
  for(unsigned i=0;i<4;i++)ram[i]=arbitrary_ram[i];last_after=*r;return cut_status;
 }
 /* Finite deterministic service schedules are C only. Every scalar at the
  * cut, including status and service-mutated RAM, is arbitrary in B profiles. */
 if(target==G(InitializeDemoScripts) && bank==GAME_SEG) {ram[0]=0x9abc;ram[1]=0x8000;ram[2]=0x5678;}
 if(target==G(ScaleAndUploadFadedPalette) && bank==GAME_SEG && (response_mode&8u))r->cx=(uint16_t)(r->cx+0x7fff);
 if(target==G(TestAllDemoScriptsFinished) && bank==GAME_SEG)flag(r,CF,response_mode&1u);
 if(target==G(SampleJoystickAxesAndButtons) && bank==GAME_SEG)flag(r,ZF,(response_mode&2u)!=0);
 if(target==G(PollKeyboardScanChange) && bank==GAME_SEG) {
  static const uint16_t keys[]={0,1,0x0110,0x0101,0x0111,0x01ff,0x8000,0xff80};r->ax=keys[(response_mode>>2)%8u];
 }
 if(target==G(SwapAndDisplayVgaPage) && bank==GAME_SEG) {frames++;if(frames>=2)ram[0]=65535u;if(response_mode&16u)ram[1]=65532u;}
 if(target==G(RunScriptedDemo) && bank==GAME_SEG) {r->flags=(uint16_t)(0x202u|(response_mode&0x8d5u));r->ax=(uint16_t)response_mode;ram[2]=(uint16_t)response_mode;}
 if(target==G(SetDemoRevealSpriteWidth) && bank==GAME_SEG)r->flags^=0x8d5;
 last_after=*r;return service_count>=64?UGH_CONTROL_TRANSFER:UGH_OK;
}
int ps_near(uint16_t target,uint16_t ret,Regs *r) {return service(r->cs,target,ret,r,0);}
int ps_dispatch(uint16_t bank,uint16_t target,Regs *r) {return service(bank,target,0,r,1);}
int ps_direct(Regs *r) {return service(r->cs,G(RunScriptedDemo),0,r,2);}
void ps_before(DemoScenePlan *plan) {observed_before=plan->observed;kind_before=plan->cursor.kind;}
void ps_parent_return(DemoScenePlan *plan,int status) {
 if(plan->active)CHECK(!plan->pending && plan->completed==!status && (status || plan->cursor.phase==DP_TERMINAL),"parent normal completion consumes the final next action");
}
static DemoPresentationPhase expected_phase(DemoScenePlan *plan) {
 if(last_bank!=GAME_SEG) {
  CHECK(last_bank==UGH_S_C_StopMusicTrack && last_target==UGH_O_C_StopMusicTrack || last_bank==UGH_S_C_StartMusicTrack && last_target==UGH_O_C_StartMusicTrack,"complete far music target set");
  return last_target==UGH_O_C_StopMusicTrack?DP_MUSIC_START:DP_VECTOR;
 }
 switch(last_target) {
 case G(InitializeDemoScripts):return DP_CLEAR_EXIT;
 case G(PollKeyboardScanChange):return last_return==G(RunScriptedDemo)+0x14?DP_LOOP:DP_KEYBOARD_AFTER;
 case G(ScaleAndUploadFadedPalette):return DP_PALETTE_AFTER;
 case G(WaitNextVerticalRetrace):return DP_ERASE;
 case G(EraseDemoSprites):return DP_WATER;
 case G(DrawWaterSurface):return DP_ADVANCE;
 case G(AdvanceDemoScripts):return DP_DRAW;
 case G(DrawDemoSprites):return DP_SWAP;
 case G(SwapAndDisplayVgaPage):return DP_TEST;
 case G(TestAllDemoScriptsFinished):return DP_TEST_AFTER;
 case G(SampleJoystickAxesAndButtons):return DP_JOYSTICK_AFTER;
 case G(PrepareAttractMap0):case G(PrepareAttractMap90):return plan->cursor.kind==DEMO_PRESENT_COMPLETION?DP_MUSIC_STOP:DP_VECTOR;
 case G(RunScriptedDemo):return plan->cursor.kind==DEMO_PRESENT_REVEAL?DP_REVEAL_X:DP_WRAPPER_DONE;
 case G(SetDemoRevealSpriteWidth):return DP_WRAPPER_DONE;
 }
 CHECK(0,"every service has a checked continuation cut");return DP_TERMINAL;
}
void ps_seam(DemoScenePlan *plan) {
 CHECK(plan->cursor.kind==kind_before && plan->cursor.phase==expected_phase(plan),"native next cut equals actual service continuation");
 DemoPresentationInput expected_input=observed_before;
 if(last_bank==GAME_SEG) {
  if(last_target==G(ScaleAndUploadFadedPalette))expected_input.palette_work=last_after.cx;
  if(last_target==G(PollKeyboardScanChange))expected_input.key_word=last_after.ax;
  if(last_target==G(TestAllDemoScriptsFinished))expected_input.finished=(last_after.flags&CF)!=0;
  if(last_target==G(SampleJoystickAxesAndButtons))expected_input.joystick_idle=(last_after.flags&ZF)!=0;
 }
 CHECK(plan->observed.fade_level==expected_input.fade_level && plan->observed.fade_step==expected_input.fade_step && plan->observed.exit_code==expected_input.exit_code && plan->observed.water_y==expected_input.water_y && plan->observed.palette_work==expected_input.palette_work && plan->observed.key_word==expected_input.key_word && plan->observed.finished==expected_input.finished && plan->observed.joystick_idle==expected_input.joystick_idle,"service-result equality and complete private snapshot frame");
}
static int execute(unsigned op,Regs *r,int native) {
 switch(op) {
 case 0:return native?c_StartDemoFadeWhenSpriteHidden(r):reference_StartDemoFadeWhenSpriteHidden(r);
 case 1:return native?c_SetDemoRevealSpriteWidth(r):reference_SetDemoRevealSpriteWidth(r);
 case 2:return native?c_RunScriptedDemo(r):reference_RunScriptedDemo(r);
 case 3:return native?c_PlaySpriteRevealDemo(r):reference_PlaySpriteRevealDemo(r);
 case 4:return native?c_PlayPreGameDemo(r):reference_PlayPreGameDemo(r);
 case 5:return native?c_PlayAttractDemo(r):reference_PlayAttractDemo(r);
 default:return native?c_PlayGameCompletionDemo(r):reference_PlayGameCompletionDemo(r);
 }
}
static void compare(unsigned op,Regs initial) {
 uint16_t before[38],after[38];for(unsigned i=0;i<38;i++)before[i]=ram[i];uint8_t byte_before=width_byte;
 operation=op;initial.cs=GAME_SEG;initial.ds=DATA_SEG;initial.ss=0x9000;initial.sp=0x1000;if(op<2)initial.bx=actor_index;
 Regs a=initial,b=initial;modern=0;observations=service_count=frames=0;int left=execute(op,&a,0);expected_observations=observations;
 for(unsigned i=0;i<38;i++){after[i]=ram[i];ram[i]=before[i];}uint8_t byte_after=width_byte;width_byte=byte_before;
 modern=1;observations=service_count=frames=0;int right=execute(op,&b,1);
 CHECK(left==right && equal_regs(a,b),"complete normal/abnormal register return");CHECK(observations==expected_observations,"complete event consumption");
 for(unsigned i=0;i<38;i++)CHECK(ram[i]==after[i],"all RAM and stack words");CHECK(width_byte==byte_after,"far width byte");comparisons++;
}
#ifndef __CPROVER__
static unsigned random_state=0x742ed391u;
static uint16_t word(void){random_state^=random_state<<13;random_state^=random_state>>17;random_state^=random_state<<5;return (uint16_t)random_state;}
static Regs seed(void) {
 Regs r={0};r.ax=word();r.bx=word();r.cx=word();r.dx=word();r.si=word();r.di=word();r.bp=word();r.es=word();r.flags=word();r.ip=word();
 for(unsigned i=0;i<38;i++)ram[i]=word();width_byte=(uint8_t)word();actor_index=(uint16_t)(2*(word()%16));width_offset=word();response_mode=word();cut_services=0;return r;
}
int main(void) {
 for(unsigned slice=0;slice<3;slice++)for(unsigned v=0;v<65536;v++) {
  random_state=0x742ed391u+slice;Regs r=seed();ram[4]=32767u;
  if(slice==0)ram[5]=(uint16_t)v;else if(slice==1)ram[4]=(uint16_t)v;else ram[0]=(uint16_t)v;
  compare(slice==0?1:0,r);
 }
 const uint16_t edges[]={0,1,127,128,191,192,193,255,256,257,0x7fff,0x8000,0xfffc,0xffff};
 for(unsigned op=2;op<7;op++)for(unsigned i=0;i<14;i++)for(unsigned j=0;j<14;j++)for(unsigned key=0;key<32;key++) {
  Regs r=seed();actor_index=0;ram[0]=edges[i];ram[1]=edges[j];ram[3]=edges[(i+j)%14];response_mode=key;compare(op,r);
 }
 for(unsigned n=0;n<3000;n++)for(unsigned op=0;op<7;op++) {Regs r=seed();if(op>=2)actor_index=0;compare(op,r);}
 printf("PASS %llu presentation comparisons\n",comparisons);return 0;
}
#endif
