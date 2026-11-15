#include "lifecycle_world.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#undef assert
#define assert(x) do {if(!(x)){fprintf(stderr,"check failed line %d: %s\n",__LINE__,#x);exit(3);}} while(0)
static NativeLifecycleWorld owner;
static unsigned count,fail_at,mode_reads,terminal_ack;
static uint16_t input_reply,video_reply;
static const LifecycleAction program[]={LIFE_BIND_WORLD,LIFE_INITIALIZE_PLATFORM,LIFE_STARTUP_PICTURES,LIFE_GAMEPLAY_VIDEO,LIFE_MAIN_MENU,LIFE_SHUTDOWN_PLATFORM};
static const LifecycleAction init[]={LIFE_QUERY_VIDEO,LIFE_SAVE_VIDEO,LIFE_CPU_PROBE,LIFE_INSTALL_ERROR_HANDLER,LIFE_LOAD_SCORES,LIFE_SEED_RANDOM,LIFE_SET_VIDEO,LIFE_PICTURE_VIDEO,LIFE_INSTALL_KEYBOARD,LIFE_CALIBRATE_CONTROLS,LIFE_INITIALIZE_AUDIO,LIFE_CLEAR_VIDEO};
static const LifecycleAction audio[]={LIFE_SOUND_INITIALIZE_ADLIB};
static const LifecycleAction shutdown[]={LIFE_STOP_MUSIC,LIFE_SOUND_STOP};
static const LifecycleAction *expected;
static LifecycleReply service(void *context,LifecycleRequest request){
 assert(context==&owner);assert(request.action==expected[count]);
 if(request.action==LIFE_SAVE_VIDEO){assert(request.argument==(video_reply&127));owner.saved_bios_video_mode=(uint8_t)request.argument;}
 if(request.action==LIFE_SET_VIDEO)assert(request.argument==19);
 if(request.action==LIFE_SOUND_INITIALIZE_ADLIB)assert(request.argument==1);
 if(request.action==LIFE_STOP_MUSIC)assert(request.argument==17);
 LifecycleReply reply={{GAME_CONTINUE,0},video_reply};
 if(++count==fail_at)reply.result.kind=GAME_SERVICE_FAILED;
 return reply;
}
static uint8_t mode(void *context){assert(context==&owner);assert(count==1);mode_reads++;return owner.saved_bios_video_mode;}
static LifecycleReply terminal(void *context,TerminalAction action,uint8_t value){
 assert(context==&owner);assert((unsigned)action==count);
 LifecycleReply reply={{GAME_CONTINUE,0},input_reply};
 if(action==TERMINAL_STOP_SOUND)owner.saved_bios_video_mode=(uint8_t)video_reply;
 if(action==TERMINAL_RESTORE_VIDEO){assert(mode_reads==1);assert(value==(uint8_t)video_reply);}
 if(action==TERMINAL_EXIT)assert(value==(uint8_t)input_reply);
 if(++count==fail_at)reply.result.kind=GAME_SERVICE_FAILED;
 else if(action==TERMINAL_EXIT && terminal_ack)reply.result.kind=GAME_EXITED;
 return reply;
}
int main(void){
 unsigned starts=0,terminals=0;
 const LifecycleAction *orders[]={program,init,audio,shutdown};const unsigned lengths[]={6,12,1,2};
 for(unsigned task=0;task<4;task++)for(unsigned failure=0;failure<=lengths[task];failure++)for(unsigned v=0;v<256;v++){
  memset(&owner,0,sizeof owner);expected=orders[task];count=0;fail_at=failure;video_reply=(uint16_t)(0xfe00|v);
  GameExit result=lifecycle_world_execute(&owner,(LifecycleTask)task,service,&owner);
  assert(count==(failure?failure:lengths[task]));assert(result.kind==(failure?GAME_SERVICE_FAILED:GAME_CONTINUE));starts++;
 }
 for(terminal_ack=0;terminal_ack<2;terminal_ack++)for(unsigned failure=0;failure<=4;failure++)for(unsigned v=0;v<256;v++)for(unsigned exit_byte=0;exit_byte<256;exit_byte++){
  memset(&owner,0,sizeof owner);owner.saved_bios_video_mode=(uint8_t)~v;
  count=mode_reads=0;fail_at=failure;video_reply=(uint16_t)v;input_reply=(uint16_t)(0xbe00|exit_byte);
  GameExit result=lifecycle_world_terminate(&owner,terminal,mode,&owner);
  assert(count==(failure?failure:4));assert(mode_reads==(failure==1?0u:1u));
  assert(result.kind==(failure?GAME_SERVICE_FAILED:GAME_EXITED));if(!failure)assert(result.code==exit_byte);terminals++;
 }
 printf("{\"startup_prefixes\":%u,\"terminal_prefixes\":%u}\n",starts,terminals);return 0;
}
