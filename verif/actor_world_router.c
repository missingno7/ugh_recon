/* Independent literal address/member oracle, not the bridge table. */
#include "actor_world_bridge.h"
#include <stdio.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
uint8_t platforms_borrowed_byte(const uint8_t*p,uint32_t i){return p[i];}
void platforms_borrowed_store(uint8_t*p,uint32_t i,uint8_t v){p[i]=v;}
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE],wanted[UGH_MEM_SIZE];
static struct {unsigned address;uint16_t*value;} words[384];static unsigned nw;
static void bind(unsigned at,uint16_t*p){unsigned a=lin(DATA_SEG,(uint16_t)at);words[nw].address=a;words[nw++].value=p;wanted[a]=wanted[a+1]=1;}
#define TEN(at,m) for(unsigned i=0;i<16;i++)bind(at+2*i,&w->slot[i].m)
int main(void){NativeActorWorld*w=native_actor_world();

 TEN(0x29ad,descriptor_word); TEN(0x29cd,initial_platform); TEN(0x29ed,journey_word); TEN(0x2a0d,update_or_script_word); TEN(0x2a2d,phase_or_loop_word); TEN(0x2a4d,source_or_done); TEN(0x2a6d,destination_platform); TEN(0x2a8d,source_byte_index); TEN(0x2aad,destination_byte_index); TEN(0x2acd,delay_or_repeat_word); TEN(0x2aed,position.x32); TEN(0x2b0d,position.y32); TEN(0x2b2d,history.pixel_x); TEN(0x2b4d,history.previous_x); TEN(0x2b6d,history.pixel_y); TEN(0x2b8d,history.previous_y); TEN(0x2bad,animation.byte_offset); TEN(0x2bcd,animation.countdown); TEN(0x2bed,sprite); TEN(0x2c0d,history.erase_sprite); TEN(0x2c2d,overlay_or_effect_word); TEN(0x2c4d,history.erase_overlay_sprite); TEN(0x2c6d,motion_or_period_word); TEN(0x2c8d,quick_delivery_ticks);
 if(nw!=384)return 1;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(expected,ugh_mem,sizeof expected);actors_cold_import(ugh_mem);
 if(actors_owned_bytes()!=768)return 2;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(actors_is_owned(a)!=(int)wanted[a])return 3;
 memcpy(output,ugh_mem,sizeof output);actors_serialize(output);if(memcmp(output,expected,sizeof output))return 4;
 for(unsigned i=0;i<nw;i++){
  unsigned a=words[i].address;if(*words[i].value!=(unsigned)(expected[a]|expected[a+1]*256u))return 5;
  for(unsigned v=0;v<65536;v++){
   actors_borrow_write(ACTORS_BORROW_SESSION,DATA_SEG,(uint16_t)(a-((uint32_t)DATA_SEG<<4)),2,v);expected[a]=(uint8_t)v;expected[a+1]=(uint8_t)(v>>8);
   if(*words[i].value!=v || actors_borrow_read(ACTORS_BORROW_PHYSICS,DATA_SEG,(uint16_t)(a-((uint32_t)DATA_SEG<<4)),2)!=v)return 6;
  }
 }
 unsigned count=0;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(wanted[a])for(unsigned v=0;v<256;v++){
  actors_borrowed_store(ugh_mem,a,(uint8_t)v);expected[a]=(uint8_t)v;uint8_t now;
  if(!actors_shared_read(a,&now)||now!=v||actors_borrowed_byte(ugh_mem+(a&~15u),a&15u)!=v)return 7;
  actors_serialize(output);if(memcmp(output,expected,sizeof output)||actors_check_serialization(output)!=UINT32_MAX)return 8;count++;
 }
 for(unsigned role=0;role<ACTORS_BORROW_COUNT;role++)for(unsigned width=1;width<=4;width*=2){
  unsigned at=0x2cab;actors_borrow_write((ActorsBorrower)role,DATA_SEG,(uint16_t)at,width,0xfedcba98u);
  for(unsigned b=0;b<width;b++)expected[lin(DATA_SEG,(uint16_t)at)+b]=(uint8_t)(0xfedcba98u>>(8*b));
  memcpy(output,ugh_mem,sizeof output);actors_serialize(output);if(memcmp(output,expected,sizeof output))return 9;
 }
 for(unsigned d=0;d<3;d++){
  actors_borrow_write(ACTORS_BORROW_ACTORS,(uint16_t)(DATA_SEG+d),(uint16_t)(0x29ad -16*d+32),2,0xabcd);
  if(w->slot[0].initial_platform!=0xabcd || w->slot[0].descriptor_word==0xabcd)return 10;
 }
 /* Raw resource/list storage stays live, mutable and outside this owner. */
 for(unsigned at=0x7200;at<0x7220;at++){
  if(actors_is_owned(lin(DATA_SEG,(uint16_t)at)))return 11;
  actors_borrow_write(ACTORS_BORROW_RESOURCES,DATA_SEG,(uint16_t)at,1,at&255);
  if(actors_borrow_read(ACTORS_BORROW_SESSION,DATA_SEG,(uint16_t)at,1)!=(at&255))return 12;
 }
 if(actors_is_owned(lin(DATA_SEG,0x2cad)) || actors_is_owned(lin(DATA_SEG,0x29ac)))return 13;
 actors_borrow_write(ACTORS_BORROW_ACTORS,DATA_SEG,0x2999+20,2,0x78dc);if(w->slot[0].descriptor_word!=0x78dc)return 15;
 actors_require_seal(ugh_mem);actors_serialize(output);output[words[0].address]^=1;if(actors_check_serialization(output)!=words[0].address)return 14;
 printf("{\"bytes\":768,\"byte_values\":%u,\"word_roundtrips\":25165824,\"roles\":%u,\"slots\":16,\"raw_aliases\":true,\"mutable_resources\":true}\n",count,ACTORS_BORROW_COUNT);return 0;
}
