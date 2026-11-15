#include "lifecycle_world_bridge.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#undef assert
#define assert(x) do {if(!(x)){fprintf(stderr,"check failed line %d: %s\n",__LINE__,#x);exit(3);}} while(0)
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t address){uint8_t value;if(lifecycle_shared_read(address,&value))return value;return ugh_mem[address];}
void ugh_write(uint32_t address,uint8_t value){if(!lifecycle_shared_write(address,value))ugh_mem[address]=value;}
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE];
int main(void){
 const uint32_t base=lin(DATA_SEG,0x92);
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(expected,ugh_mem,sizeof expected);lifecycle_cold_import(ugh_mem);
 assert(lifecycle_owned_bytes()==1 && native_lifecycle_world()->saved_bios_video_mode==expected[base]);
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)assert(lifecycle_is_owned(a)==(a==base));
 for(unsigned value=0;value<256;value++){
  lifecycle_borrowed_store(ugh_mem+base,0,(uint8_t)value);expected[base]=(uint8_t)value;
  assert(lifecycle_borrowed_byte(ugh_mem+base,0)==value);
  memcpy(output,ugh_mem,sizeof output);lifecycle_serialize(output);assert(!memcmp(expected,output,sizeof output));
  assert(lifecycle_check_serialization(output)==UINT32_MAX);output[base]^=1;assert(lifecycle_check_serialization(output)==base);
  for(unsigned delta=0;delta<3;delta++)assert(lifecycle_borrow_read(LIFECYCLE_BORROW_TERMINAL,(uint16_t)(DATA_SEG-delta),(uint16_t)(0x92+delta*16))==value);
 }
 for(unsigned word=0;word<65536;word++){
  wr16(DATA_SEG,0x91,(uint16_t)word);assert(native_lifecycle_world()->saved_bios_video_mode==word/256);
  wr16(DATA_SEG,0x92,(uint16_t)word);assert(native_lifecycle_world()->saved_bios_video_mode==(word&255));
 }
 lifecycle_require_seal(ugh_mem);
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(a!=base){uint8_t value=19;assert(!lifecycle_shared_read(a,&value) && value==19 && !lifecycle_shared_write(a,17));}
 puts("{\"owned_bytes\":1,\"byte_values\":256,\"word_straddles\":131072,\"paragraph_aliases\":768}");return 0;
}
