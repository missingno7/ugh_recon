#include "platform.h"
#include "lifecycle_world_bridge.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#undef assert
#define assert(x) do {if(!(x)){fprintf(stderr,"check failed line %d: %s\n",__LINE__,#x);exit(3);}} while(0)
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){uint8_t value;if(lifecycle_shared_read(a,&value))return value;return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t value){if(!lifecycle_shared_write(a,value))ugh_mem[a]=value;}
static unsigned count,fail_at,fail_status,foreign,mode_value,exit_value;
static unsigned stream[8];
static int event(unsigned kind){assert(count<8);stream[count++]=kind;return count==fail_at?(int)fail_status:0;}
int c_FadeAndShutdownSound(Regs *r){
 r->ds=foreign?0x7500:DATA_SEG;wr8(r->ds,D(SavedBiosVideoMode),(uint8_t)mode_value);set_al(r,0x75);return event(0);
}
int c_RestoreKeyboardInterrupt(Regs *r){r->ax=(uint16_t)(0xbe00|exit_value);return event(2);}
int platform_interrupt(uint8_t number,Regs *r){
 if(number==0x10){assert((r->ax&255)==mode_value);return event(1);}
 assert(number==0x21 && (r->ax>>8)==0x4c && (r->ax&255)==exit_value);return event(3);
}
static int fixture_near(Regs *r,uint16_t target,uint16_t ret){
 r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,ret);
 int status=target==G(FadeAndShutdownSound)?c_FadeAndShutdownSound(r):c_RestoreKeyboardInterrupt(r);
 if(!status)r->sp=(uint16_t)(r->sp+2);return status;
}
/* PEER STUBS */
/* LITERAL TERMINAL */
static uint8_t observed[UGH_MEM_SIZE],reference[UGH_MEM_SIZE];
int main(void){
 unsigned cases=0;
 for(foreign=0;foreign<2;foreign++)for(mode_value=0;mode_value<256;mode_value++)for(exit_value=0;exit_value<256;exit_value+=17)
 for(fail_at=0;fail_at<=4;fail_at++)for(fail_status=1;fail_status<=5;fail_status++){
  Regs before={0},literal,native;before.ds=DATA_SEG;before.cs=GAME_SEG;before.ss=0x9000;before.sp=0x100;before.flags=(uint16_t)(0xed7^((mode_value&1)*DF));
  memset(ugh_mem,0x39,sizeof ugh_mem);lifecycle_cold_import(ugh_mem);count=0;literal=before;int expected=literal_terminal(&literal);unsigned expected_count=count,expected_stream[8];memcpy(expected_stream,stream,sizeof stream);
  memcpy(reference,ugh_mem,sizeof reference);lifecycle_serialize(reference);
  memset(ugh_mem,0x39,sizeof ugh_mem);lifecycle_cold_import(ugh_mem);count=0;native=before;int actual=lifecycle_adapter_terminal(&native);
  memcpy(observed,ugh_mem,sizeof observed);lifecycle_serialize(observed);lifecycle_require_seal(ugh_mem);
  assert(actual==expected && !memcmp(&literal,&native,sizeof literal));assert(!memcmp(reference,observed,sizeof reference));
  assert(count==expected_count && count>0 && !memcmp(expected_stream,stream,count*sizeof *stream));cases++;
 }
 printf("{\"literal_adapter_cases\":%u,\"services_nonempty\":true}\n",cases);return 0;
}
