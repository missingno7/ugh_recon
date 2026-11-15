#include "platform.h"
#include "lifecycle_world_bridge.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned active;
static uint32_t lifecycle_field(void){return lin(DATA_SEG,D(SavedBiosVideoMode));}
int lifecycle_is_owned(uint32_t address){return active && address==lifecycle_field();}
int lifecycle_shared_read(uint32_t address,uint8_t *value){
 if(!lifecycle_is_owned(address))return 0;
 *value=native_lifecycle_world()->saved_bios_video_mode;return 1;
}
int lifecycle_shared_write(uint32_t address,uint8_t value){
 if(!lifecycle_is_owned(address))return 0;
 native_lifecycle_world()->saved_bios_video_mode=value;return 1;
}
unsigned lifecycle_owned_bytes(void){return active?1:0;}
void lifecycle_cold_import(uint8_t *memory){
 active=0;memset(native_lifecycle_world(),0,sizeof *native_lifecycle_world());
 native_lifecycle_world()->saved_bios_video_mode=memory[lifecycle_field()];
 memory[lifecycle_field()]=0xa5;active=1;
}
void lifecycle_require_seal(const uint8_t *memory){
 if(active && memory[lifecycle_field()]!=0xa5){fputs("lifecycle: sealed RAM violation\n",stderr);exit(88);}
}
void lifecycle_serialize(uint8_t *output){
 if(!active)return;
#if LIFECYCLE_TEST_FAULT == 1
 (void)output;fputs("lifecycle: missed serialization\n",stderr);exit(88);
#else
 output[lifecycle_field()]=native_lifecycle_world()->saved_bios_video_mode;
#endif
}
uint32_t lifecycle_check_serialization(const uint8_t *output){
 if(active && output[lifecycle_field()]!=native_lifecycle_world()->saved_bios_video_mode)return lifecycle_field();
 return UINT32_MAX;
}
uint8_t lifecycle_borrowed_byte(const uint8_t *window,uint32_t index){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE){uint8_t value;if(lifecycle_shared_read((uint32_t)(p-base+index),&value))return value;}
 return window[index];
}
void lifecycle_borrowed_store(uint8_t *window,uint32_t index,uint8_t value){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE && lifecycle_shared_write((uint32_t)(p-base+index),value))return;
 window[index]=value;
}
uint8_t lifecycle_borrow_read(LifecycleBorrower borrower,uint16_t bank,uint16_t position){
 if(borrower>=LIFECYCLE_BORROW_COUNT)abort();
 uint8_t value;if(lifecycle_shared_read(lin(bank,position),&value))return value;
 return rd8(bank,position);
}
void lifecycle_borrow_write(LifecycleBorrower borrower,uint16_t bank,uint16_t position,uint8_t value){
 if(borrower>=LIFECYCLE_BORROW_COUNT)abort();
 if(!lifecycle_shared_write(lin(bank,position),value))wr8(bank,position,value);
}

/* Verification-only service binding. All machine status/frames stay here. */
typedef struct LifecycleAdapter {Regs *registers;int status;} LifecycleAdapter;
typedef int (*LifecyclePeer)(Regs *registers);
static void lifecycle_push(Regs *r,uint16_t value){r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,value);}
static uint16_t lifecycle_pop(Regs *r){uint16_t value=rd16(r->ss,r->sp);r->sp=(uint16_t)(r->sp+2);return value;}
static int lifecycle_near(Regs *r,LifecyclePeer peer,uint16_t ret){
 uint16_t saved_cs=r->cs;lifecycle_push(r,ret);int status=peer(r);
 if(status!=UGH_CONTROL_TRANSFER && status!=UGH_DOS_EXIT)r->cs=saved_cs;
 if(!status)r->sp=(uint16_t)(r->sp+2);
 return status;
}
static int lifecycle_far(Regs *r,LifecyclePeer peer,uint16_t ret){
 uint16_t saved_cs=r->cs;lifecycle_push(r,r->cs);lifecycle_push(r,ret);r->cs=UGH_SEG_C;int status=peer(r);
 if(status!=UGH_CONTROL_TRANSFER && status!=UGH_DOS_EXIT)r->cs=saved_cs;
 if(status!=UGH_CONTROL_TRANSFER)r->sp=(uint16_t)(r->sp+4);
 return status;
}
static LifecycleReply lifecycle_reply(LifecycleAdapter *adapter,int status){
 LifecycleReply reply={{GAME_CONTINUE,0},adapter->registers->ax};adapter->status=status;
 if(status)reply.result.kind=status==UGH_DOS_EXIT?GAME_EXITED:GAME_SERVICE_FAILED;
 reply.result.code=(uint8_t)reply.value;return reply;
}
static LifecycleReply lifecycle_service(void *context,LifecycleRequest request){
 LifecycleAdapter *adapter=context;Regs *r=adapter->registers;int status=0;
 switch(request.action){
 case LIFE_BIND_WORLD:r->dx=DATA_SEG;r->ds=r->dx;break;
 case LIFE_INITIALIZE_PLATFORM:status=lifecycle_near(r,c_InitializeDosVideoInputAndSound,G(RunDosGame)+8);break;
 case LIFE_STARTUP_PICTURES:status=lifecycle_near(r,c_ShowStartupPictures,G(RunDosGame)+11);break;
 case LIFE_GAMEPLAY_VIDEO:status=lifecycle_near(r,c_ConfigureVgaGameplayPages,G(RunDosGame)+14);break;
 case LIFE_MAIN_MENU:status=lifecycle_near(r,c_RunMainMenuAndAttractLoop,G(RunDosGame)+17);break;
 case LIFE_SHUTDOWN_PLATFORM:status=c_DosShutdownTail(r);break;
 case LIFE_QUERY_VIDEO:set_ah(r,15);status=platform_interrupt(0x10,r);break;
 case LIFE_SAVE_VIDEO:
  set_al(r,(uint8_t)logic(r,r->ax&0x7f,8));
  lifecycle_borrow_write(LIFECYCLE_BORROW_STARTUP,r->ds,D(SavedBiosVideoMode),(uint8_t)request.argument);break;
 case LIFE_CPU_PROBE:
  r->ax=logic(r,0,16);lifecycle_push(r,r->ax);r->flags=(uint16_t)(lifecycle_pop(r)|2);
  lifecycle_push(r,r->flags);r->ax=lifecycle_pop(r);r->ax=logic(r,r->ax&0xf000,16);sub16(r,r->ax,0xf000,0);break;
 case LIFE_INSTALL_ERROR_HANDLER:status=lifecycle_near(r,c_InstallDosCriticalErrorFailHandler,G(InitializeDosVideoInputAndSound)+0x20);break;
 case LIFE_LOAD_SCORES:status=lifecycle_near(r,c_LoadHighScores,G(InitializeDosVideoInputAndSound)+0x23);break;
 case LIFE_SEED_RANDOM:status=lifecycle_near(r,c_SeedRandomFromDosSeconds,G(InitializeDosVideoInputAndSound)+0x26);break;
 case LIFE_SET_VIDEO:flag(r,DF,0);r->ax=request.argument;status=platform_interrupt(0x10,r);break;
 case LIFE_PICTURE_VIDEO:status=lifecycle_near(r,c_ConfigureVgaPicturePages,G(InitializeDosVideoInputAndSound)+0x2f);break;
 case LIFE_INSTALL_KEYBOARD:status=lifecycle_near(r,c_InstallKeyboardSequenceInterrupt,G(InitializeDosVideoInputAndSound)+0x32);break;
 case LIFE_CALIBRATE_CONTROLS:status=lifecycle_near(r,c_DetectAndCalibrateJoysticks,G(InitializeDosVideoInputAndSound)+0x35);break;
 case LIFE_INITIALIZE_AUDIO:status=lifecycle_near(r,c_InitializeAdLibSound,G(InitializeDosVideoInputAndSound)+0x38);break;
 case LIFE_CLEAR_VIDEO:status=c_ClearAllVgaPlanes(r);break;
 case LIFE_SOUND_INITIALIZE_ADLIB:
  lifecycle_push(r,request.argument);status=lifecycle_far(r,c_InitializeSoundSystem,G(InitializeAdLibSound)+7);
  if(!status)r->sp=add16(r,r->sp,2,0);
  break;
 case LIFE_STOP_MUSIC:
  lifecycle_push(r,request.argument);status=lifecycle_far(r,c_StopMusicTrack,G(FadeAndShutdownSound)+7);
  if(!status)r->sp=add16(r,r->sp,2,0);
  break;
 case LIFE_SOUND_STOP:status=lifecycle_far(r,c_ShutdownSoundSystem,G(FadeAndShutdownSound)+15);break;
 default:status=UGH_UNSUPPORTED;break;
 }
 return lifecycle_reply(adapter,status);
}
static uint8_t lifecycle_live_mode(void *context){
 LifecycleAdapter *adapter=context;
 return lifecycle_borrow_read(LIFECYCLE_BORROW_TERMINAL,adapter->registers->ds,D(SavedBiosVideoMode));
}
static LifecycleReply lifecycle_terminal_service(void *context,TerminalAction action,uint8_t value){
 LifecycleAdapter *adapter=context;Regs *r=adapter->registers;int status=0;
 switch(action){
 case TERMINAL_STOP_SOUND:status=lifecycle_near(r,c_FadeAndShutdownSound,G(loc_4EE6)+3);break;
 case TERMINAL_RESTORE_VIDEO:set_ah(r,0);logic(r,0,8);set_al(r,value);status=platform_interrupt(0x10,r);break;
 case TERMINAL_RESTORE_INPUT:status=lifecycle_near(r,c_RestoreKeyboardInterrupt,G(loc_4EE6)+13);break;
 case TERMINAL_EXIT:set_al(r,value);set_ah(r,0x4c);status=platform_interrupt(0x21,r);if(!status)status=UGH_DOS_EXIT;break;
 default:status=UGH_UNSUPPORTED;break;
 }
 return lifecycle_reply(adapter,status);
}
int lifecycle_adapter_run(Regs *r,LifecycleTask task){
 LifecycleAdapter adapter={r,0};GameExit result=lifecycle_world_execute(native_lifecycle_world(),task,lifecycle_service,&adapter);
 return result.kind==GAME_CONTINUE?UGH_OK:(adapter.status?adapter.status:UGH_UNSUPPORTED);
}
int lifecycle_adapter_terminal(Regs *r){
 LifecycleAdapter adapter={r,0};GameExit result=lifecycle_world_terminate(native_lifecycle_world(),lifecycle_terminal_service,lifecycle_live_mode,&adapter);
 return result.kind==GAME_EXITED?UGH_DOS_EXIT:(adapter.status?adapter.status:UGH_UNSUPPORTED);
}
