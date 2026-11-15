#include "random_world_bridge.h"
#include <stdio.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
uint8_t run_borrowed_byte(const uint8_t*p,uint32_t i){return p[i];}
void run_borrowed_store(uint8_t*p,uint32_t i,uint8_t v){p[i]=v;}
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE];
int main(void){
 const uint32_t base=lin(GAME_SEG,0x4ef7);RandomState *w=native_random_world();
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(expected,ugh_mem,sizeof expected);rng_cold_import(ugh_mem);
 if(rng_owned_bytes()!=8 || sizeof *w!=8)return 1;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(rng_is_owned(a)!=(a>=base && a<base+8))return 2;
 for(unsigned i=0;i<4;i++){
  if(w->word[i]!=(unsigned)(expected[base+i*2]|expected[base+i*2+1]*256u))return 3;
  for(unsigned v=0;v<65536;v++){
   rng_borrow_write(RNG_BORROW_GENERATOR,GAME_SEG,(uint16_t)(0x4ef7+i*2),2,v);
   expected[base+2*i]=(uint8_t)v;expected[base+2*i+1]=(uint8_t)(v>>8);
   if(w->word[i]!=v || rng_borrow_read(RNG_BORROW_GENERATOR,GAME_SEG,(uint16_t)(0x4ef7+i*2),2)!=v)return 4;
  }
 }
 for(unsigned i=0;i<8;i++)for(unsigned v=0;v<256;v++){
  rng_borrowed_store(ugh_mem+base,i,(uint8_t)v);expected[base+i]=(uint8_t)v;
  uint8_t got;if(!rng_shared_read(base+i,&got) || got!=v || rng_borrowed_byte(ugh_mem+base,i)!=v)return 5;
  memcpy(output,ugh_mem,sizeof output);rng_serialize(output);
  if(memcmp(output,expected,sizeof output) || rng_check_serialization(output)!=UINT32_MAX)return 6;
 }
 for(unsigned at=0;at<10;at++)for(unsigned width=1;width<=4;width*=2){
  rng_borrow_write(RNG_BORROW_GENERATOR,GAME_SEG,(uint16_t)(0x4ef6+at),width,0xfedcba98);
  for(unsigned i=0;i<width;i++)expected[base-1+at+i]=(uint8_t)(0xfedcba98u>>(8*i));
  memcpy(output,ugh_mem,sizeof output);rng_serialize(output);if(memcmp(output,expected,sizeof output))return 7;
 }
 for(unsigned delta=0;delta<3;delta++){
  rng_borrow_write(RNG_BORROW_GENERATOR,(uint16_t)(GAME_SEG+delta),(uint16_t)(0x4ef8-delta*16),1,delta+59);
  expected[base+1]=(uint8_t)(delta+59);if((w->word[0]>>8)!=delta+59)return 8;
 }
 rng_require_seal(ugh_mem);rng_serialize(output);output[base+1]^=1;if(rng_check_serialization(output)!=base+1)return 9;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(a<base || a>=base+8){uint8_t v=49;if(rng_shared_read(a,&v)||rng_shared_write(a,17)||v!=49)return 10;}
 puts("{\"owned_bytes\":8,\"byte_values\":2048,\"word_roundtrips\":262144,\"straddles\":30,\"paragraph_aliases\":3}");return 0;
}
