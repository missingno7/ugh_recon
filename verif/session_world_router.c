/* Independent physical/member oracle. No bridge binding table is reused. */
#include "session_world_bridge.h"
#include <stdio.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
uint8_t frontend_borrowed_byte(const uint8_t*p,uint32_t i){return p[i];}
void frontend_borrowed_store(uint8_t*p,uint32_t i,uint8_t v){p[i]=v;}
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE],wanted[UGH_MEM_SIZE];
static uint8_t *members[4];static unsigned addresses[4],count;
static void bind(unsigned at,uint8_t*p,unsigned n){for(unsigned i=0;i<n;i++){unsigned a=lin(DATA_SEG,(uint16_t)(at+i));members[count]=p+i;addresses[count++]=a;wanted[a]=1;}}
int main(void){NativeSessionWorld*w=native_session_world();
 bind(0x2648,(uint8_t*)&w->coordinate_scale_scratch,2);bind(0x264a,(uint8_t*)&w->demo_exit_code,2);
 if(count!=4||sizeof *w!=4)return 1;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(expected,ugh_mem,sizeof expected);sessionstate_cold_import(ugh_mem);
 if(sessionstate_owned_bytes()!=4)return 2;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(sessionstate_is_owned(a)!=(int)wanted[a])return 3;
 memcpy(output,ugh_mem,sizeof output);sessionstate_serialize(output);if(memcmp(output,expected,sizeof output))return 4;
 for(unsigned i=0;i<count;i++)for(unsigned v=0;v<256;v++){
  unsigned a=addresses[i];sessionstate_borrowed_store(ugh_mem,a,(uint8_t)v);expected[a]=(uint8_t)v;
  if(*members[i]!=v||sessionstate_borrowed_byte(ugh_mem+(a&~15u),a&15u)!=v)return 5;
  sessionstate_serialize(output);if(memcmp(output,expected,sizeof output)||sessionstate_check_serialization(output)!=UINT32_MAX)return 6;
 }
 for(unsigned i=0;i<2;i++)for(unsigned v=0;v<65536;v++){
  sessionstate_borrow_write(SESSIONSTATE_BORROW_SESSION,DATA_SEG,(uint16_t)(0x2648+i*2),2,v);
  if((i?w->demo_exit_code:w->coordinate_scale_scratch)!=v)return 7;
 }
 sessionstate_serialize(expected);
 for(unsigned i=0;i<count;i++)for(unsigned role=0;role<SESSIONSTATE_BORROW_COUNT;role++)for(unsigned width=1;width<=4;width*=2){
  unsigned a=addresses[i];uint16_t pos=(uint16_t)(a-((uint32_t)DATA_SEG<<4));
  sessionstate_borrow_write((SessionstateBorrower)role,DATA_SEG,pos,width,0x89abcdefu);
  for(unsigned j=0;j<width;j++)expected[a+j]=(uint8_t)(0x89abcdefu>>(8*j));
  memcpy(output,ugh_mem,sizeof output);sessionstate_serialize(output);if(memcmp(output,expected,sizeof output))return 8;
  uint32_t mask=width==4?UINT32_MAX:((1u<<(8*width))-1u);
  if(sessionstate_borrow_read((SessionstateBorrower)role,(uint16_t)(DATA_SEG-1),(uint16_t)(pos+16),width)!=(0x89abcdefu&mask))return 9;
 }
 /* The encompassing loader clear begins here and must cross to the map owner. */
 sessionstate_borrow_write(SESSIONSTATE_BORROW_WINDOW,DATA_SEG,0x2647,4,0x76543210);
 if(w->coordinate_scale_scratch!=0x5432||(w->demo_exit_code&255)!=0x76)return 10;
 sessionstate_require_seal(ugh_mem);sessionstate_serialize(output);output[addresses[0]]^=1;
 if(sessionstate_check_serialization(output)!=addresses[0])return 11;
 printf("{\"bytes\":4,\"byte_values\":1024,\"word_values\":131072,\"straddles\":156,\"roles\":13}\n");return 0;
}
