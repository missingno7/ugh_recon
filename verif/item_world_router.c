/* Independent literal address/member oracle, not the bridge table. */
#include "item_world_bridge.h"
#include <stdio.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
uint8_t enemies_borrowed_byte(const uint8_t*p,uint32_t i){return p[i];}
void enemies_borrowed_store(uint8_t*p,uint32_t i,uint8_t v){p[i]=v;}
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE],wanted[UGH_MEM_SIZE];
static struct {unsigned address;uint16_t*value;} words[144];static unsigned nw;
static void bind(unsigned at,uint16_t*p){unsigned a=lin(DATA_SEG,(uint16_t)at);words[nw].address=a;words[nw++].value=p;wanted[a]=wanted[a+1]=1;}
#define TEN(at,m) for(unsigned i=0;i<12;i++)bind(at+2*i,&w->slot[i].m)
int main(void){NativeItemWorld*w=native_item_world();

 TEN(0x2d6b,descriptor_word); TEN(0x2d83,callback_word); TEN(0x2d9b,sprite); TEN(0x2db3,erase_sprite); TEN(0x2dcb,x32); TEN(0x2de3,y32); TEN(0x2dfb,draw_x); TEN(0x2e13,previous_x); TEN(0x2e2b,draw_y); TEN(0x2e43,previous_y); TEN(0x2e5b,motion_or_lifetime); TEN(0x2e73,vertical_step);
 if(nw!=144)return 1;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(expected,ugh_mem,sizeof expected);itemstate_cold_import(ugh_mem);
 if(itemstate_owned_bytes()!=288)return 2;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(itemstate_is_owned(a)!=(int)wanted[a])return 3;
 memcpy(output,ugh_mem,sizeof output);itemstate_serialize(output);if(memcmp(output,expected,sizeof output))return 4;
 for(unsigned i=0;i<nw;i++){
  unsigned a=words[i].address;if(*words[i].value!=(unsigned)(expected[a]|expected[a+1]*256u))return 5;
  for(unsigned v=0;v<65536;v++){
   itemstate_borrow_write(ITEMSTATE_BORROW_SESSION,DATA_SEG,(uint16_t)(a-((uint32_t)DATA_SEG<<4)),2,v);expected[a]=(uint8_t)v;expected[a+1]=(uint8_t)(v>>8);
   if(*words[i].value!=v || itemstate_borrow_read(ITEMSTATE_BORROW_PHYSICS,DATA_SEG,(uint16_t)(a-((uint32_t)DATA_SEG<<4)),2)!=v)return 6;
  }
 }
 unsigned count=0;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(wanted[a])for(unsigned v=0;v<256;v++){
  itemstate_borrowed_store(ugh_mem,a,(uint8_t)v);expected[a]=(uint8_t)v;uint8_t now;
  if(!itemstate_shared_read(a,&now)||now!=v||itemstate_borrowed_byte(ugh_mem+(a&~15u),a&15u)!=v)return 7;
  itemstate_serialize(output);if(memcmp(output,expected,sizeof output)||itemstate_check_serialization(output)!=UINT32_MAX)return 8;count++;
 }
 for(unsigned role=0;role<ITEMSTATE_BORROW_COUNT;role++)for(unsigned width=1;width<=4;width*=2){
  unsigned at=0x2e89;itemstate_borrow_write((ItemstateBorrower)role,DATA_SEG,(uint16_t)at,width,0xfedcba98u);
  for(unsigned b=0;b<width;b++)expected[lin(DATA_SEG,(uint16_t)at)+b]=(uint8_t)(0xfedcba98u>>(8*b));
  memcpy(output,ugh_mem,sizeof output);itemstate_serialize(output);if(memcmp(output,expected,sizeof output))return 9;
 }
 for(unsigned d=0;d<3;d++){
  itemstate_borrow_write(ITEMSTATE_BORROW_ACTORS,(uint16_t)(DATA_SEG+d),(uint16_t)(0x2d6b -16*d+24),2,0xabcd);
  if(w->slot[0].callback_word!=0xabcd || w->slot[0].descriptor_word==0xabcd)return 10;
 }
 /* Raw resource/list storage stays live, mutable and outside this owner. */
 for(unsigned at=0x7200;at<0x7220;at++){
  if(itemstate_is_owned(lin(DATA_SEG,(uint16_t)at)))return 11;
  itemstate_borrow_write(ITEMSTATE_BORROW_RESOURCES,DATA_SEG,(uint16_t)at,1,at&255);
  if(itemstate_borrow_read(ITEMSTATE_BORROW_SESSION,DATA_SEG,(uint16_t)at,1)!=(at&255))return 12;
 }
 if(itemstate_is_owned(lin(DATA_SEG,0x2e8b)) || itemstate_is_owned(lin(DATA_SEG,0x2d6a)))return 13;
 itemstate_borrow_write(ITEMSTATE_BORROW_ACTORS,DATA_SEG,0x2d6b+24,2,0x78dc);if(w->slot[0].callback_word!=0x78dc)return 15;
 itemstate_borrow_write(ITEMSTATE_BORROW_DEMO,DATA_SEG,0x2d4d+2*15,2,0xffff);if(w->slot[0].descriptor_word!=0xffff)return 16;
 itemstate_require_seal(ugh_mem);itemstate_serialize(output);output[words[0].address]^=1;if(itemstate_check_serialization(output)!=words[0].address)return 14;
 printf("{\"bytes\":288,\"byte_values\":%u,\"word_roundtrips\":9437184,\"roles\":%u,\"slots\":12,\"raw_aliases\":true,\"mutable_resources\":true}\n",count,ITEMSTATE_BORROW_COUNT);return 0;
}
