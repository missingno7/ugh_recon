#include "platform.h"
#include "random_world_bridge.h"
#include "run_world_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned active;
static uint8_t rng_get(unsigned lane){return (uint8_t)(native_random_world()->word[lane/2]>>((lane&1)*8));}
static void rng_put(unsigned lane,uint8_t value){
 uint16_t *word=&native_random_world()->word[lane/2];unsigned shift=(lane&1)*8;
 *word=(uint16_t)((*word&~(255u<<shift))|((unsigned)value<<shift));
}
static int rng_lane(uint32_t address,unsigned *lane){
 uint32_t base=lin(GAME_SEG,G(RandomStateWord0));
 if(address<base || address-base>=8)return 0;
 *lane=(unsigned)(address-base);return 1;
}
int rng_is_owned(uint32_t address){unsigned lane;return active && rng_lane(address,&lane);}
int rng_shared_read(uint32_t address,uint8_t *value){unsigned lane;if(!active || !rng_lane(address,&lane))return 0;*value=rng_get(lane);return 1;}
int rng_shared_write(uint32_t address,uint8_t value){unsigned lane;if(!active || !rng_lane(address,&lane))return 0;rng_put(lane,value);return 1;}
unsigned rng_owned_bytes(void){return active?8:0;}
void rng_cold_import(uint8_t *memory){
 active=0;uint32_t base=lin(GAME_SEG,G(RandomStateWord0));
 for(unsigned i=0;i<8;i++)rng_put(i,memory[base+i]);
 for(unsigned i=0;i<8;i++)memory[base+i]=0xa5;
 active=1;
}
void rng_require_seal(const uint8_t *memory){
 if(!active)return;
 uint32_t base=lin(GAME_SEG,G(RandomStateWord0));
 for(unsigned i=0;i<8;i++)if(memory[base+i]!=0xa5){fputs("random: sealed RAM violation\n",stderr);exit(88);}
}
void rng_serialize(uint8_t *output){
 if(!active)return;
 unsigned emitted=0;uint32_t base=lin(GAME_SEG,G(RandomStateWord0));
 for(unsigned i=0;i<8;i++){
#if RNG_TEST_FAULT == 1
  if(i==1)continue;
#endif
  output[base+i]=rng_get(i);emitted++;
 }
 if(emitted!=8){fputs("random: missed serialization\n",stderr);exit(88);}
}
uint32_t rng_check_serialization(const uint8_t *output){
 if(active){uint32_t base=lin(GAME_SEG,G(RandomStateWord0));for(unsigned i=0;i<8;i++)if(output[base+i]!=rng_get(i))return base+i;}
 return UINT32_MAX;
}
uint8_t rng_borrowed_byte(const uint8_t *window,uint32_t index){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE){uint8_t value;if(rng_shared_read((uint32_t)(p-base+index),&value))return value;}
 return run_borrowed_byte(window,index);
}
void rng_borrowed_store(uint8_t *window,uint32_t index,uint8_t value){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE && rng_shared_write((uint32_t)(p-base+index),value))return;
 run_borrowed_store(window,index,value);
}
uint32_t rng_borrow_read(RandomBorrower who,uint16_t bank,uint16_t offset,unsigned width){
 if(who>=RNG_BORROW_COUNT || (width!=1 && width!=2 && width!=4)){fputs("random: invalid borrower\n",stderr);exit(88);}
 uint32_t result=0,address=lin(bank,offset);
 for(unsigned i=0;i<width;i++){uint8_t byte;if(!rng_shared_read(address+i,&byte))byte=ugh_read(address+i);result|=(uint32_t)byte<<(8*i);}
 return result;
}
void rng_borrow_write(RandomBorrower who,uint16_t bank,uint16_t offset,unsigned width,uint32_t value){
 if(who>=RNG_BORROW_COUNT || (width!=1 && width!=2 && width!=4)){fputs("random: invalid borrower\n",stderr);exit(88);}
 uint32_t address=lin(bank,offset);
 for(unsigned i=0;i<width;i++)if(!rng_shared_write(address+i,(uint8_t)(value>>(8*i))))ugh_write(address+i,(uint8_t)(value>>(8*i)));
}
