#include "lifecycle_world.h"
void __CPROVER_assert(int,const char *);
#define assert(x) __CPROVER_assert((x),#x)
static NativeLifecycleWorld owner;
static unsigned count,fail_at,reads,terminal_ack;
static uint8_t live_mode,ack_code;
static uint16_t input_reply;
unsigned nondet_uint(void);uint8_t nondet_byte(void);uint16_t nondet_word(void);
void __CPROVER_assume(int);
static uint8_t mode(void *context){assert(context==&owner);assert(count==1);reads++;return owner.saved_bios_video_mode;}
static LifecycleReply terminal(void *context,TerminalAction action,uint8_t value){
 assert(context==&owner);assert((unsigned)action==count);
 LifecycleReply reply={{GAME_CONTINUE,0},input_reply};
 if(action==TERMINAL_STOP_SOUND)owner.saved_bios_video_mode=live_mode;
 if(action==TERMINAL_RESTORE_VIDEO){assert(value==live_mode);assert(reads==1);}
 if(action==TERMINAL_EXIT)assert(value==(uint8_t)input_reply);
 if(++count==fail_at)reply.result.kind=GAME_SERVICE_FAILED;
 else if(action==TERMINAL_EXIT && terminal_ack){reply.result.kind=GAME_EXITED;reply.result.code=ack_code;}
 return reply;
}
int main(void){
 owner.saved_bios_video_mode=nondet_byte();live_mode=nondet_byte();input_reply=nondet_word();fail_at=nondet_uint();__CPROVER_assume(fail_at<=4);
 terminal_ack=nondet_uint();ack_code=nondet_byte();
 GameExit result=lifecycle_world_terminate(&owner,terminal,mode,&owner);
 assert(count==(fail_at?fail_at:4));assert(reads==(fail_at==1?0u:1u));
 assert(result.kind==(fail_at?GAME_SERVICE_FAILED:GAME_EXITED));
 if(!fail_at)assert(result.code==(uint8_t)input_reply);
 return 0;
}
