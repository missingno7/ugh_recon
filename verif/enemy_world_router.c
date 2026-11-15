/* Independent literal address/member oracle, not the bridge table. */
#include "enemy_world_bridge.h"
#include <stdio.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
uint8_t actors_borrowed_byte(const uint8_t*p,uint32_t i){return p[i];}
void actors_borrowed_store(uint8_t*p,uint32_t i,uint8_t v){p[i]=v;}
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE],wanted[UGH_MEM_SIZE];
static struct {unsigned address;uint16_t*value;} words[95];static unsigned nw;
static void bind(unsigned at,uint16_t*p){unsigned a=lin(DATA_SEG,(uint16_t)at);words[nw].address=a;words[nw++].value=p;wanted[a]=wanted[a+1]=1;}
#define TEN(at,m) for(unsigned i=0;i<5;i++)bind(at+2*i,&w->slot[i].m)
int main(void){NativeEnemyWorld*w=native_enemy_world();

 TEN(0x2cad,descriptor_word); TEN(0x2cb7,platform); TEN(0x2cc1,x32); TEN(0x2ccb,y32); TEN(0x2cd5,animation_or_drop_word); TEN(0x2cdf,initial_delay); TEN(0x2ce9,speed); TEN(0x2cf3,callback_word); TEN(0x2cfd,counter); TEN(0x2d07,draw_x); TEN(0x2d11,previous_x); TEN(0x2d1b,draw_y); TEN(0x2d25,previous_y); TEN(0x2d2f,animation_offset); TEN(0x2d39,countdown); TEN(0x2d43,sprite); TEN(0x2d4d,erase_sprite); TEN(0x2d57,direction_or_target_word); TEN(0x2d61,sound_handle_word); 
 if(nw!=95)return 1;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(expected,ugh_mem,sizeof expected);enemies_cold_import(ugh_mem);
 if(enemies_owned_bytes()!=190)return 2;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(enemies_is_owned(a)!=(int)wanted[a])return 3;
 memcpy(output,ugh_mem,sizeof output);enemies_serialize(output);if(memcmp(output,expected,sizeof output))return 4;
 for(unsigned i=0;i<nw;i++){
  unsigned a=words[i].address;if(*words[i].value!=(unsigned)(expected[a]|expected[a+1]*256u))return 5;
  for(unsigned v=0;v<65536;v++){
   enemies_borrow_write(ENEMIES_BORROW_SESSION,DATA_SEG,(uint16_t)(a-((uint32_t)DATA_SEG<<4)),2,v);expected[a]=(uint8_t)v;expected[a+1]=(uint8_t)(v>>8);
   if(*words[i].value!=v || enemies_borrow_read(ENEMIES_BORROW_PHYSICS,DATA_SEG,(uint16_t)(a-((uint32_t)DATA_SEG<<4)),2)!=v)return 6;
  }
 }
 unsigned count=0;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(wanted[a])for(unsigned v=0;v<256;v++){
  enemies_borrowed_store(ugh_mem,a,(uint8_t)v);expected[a]=(uint8_t)v;uint8_t now;
  if(!enemies_shared_read(a,&now)||now!=v||enemies_borrowed_byte(ugh_mem+(a&~15u),a&15u)!=v)return 7;
  enemies_serialize(output);if(memcmp(output,expected,sizeof output)||enemies_check_serialization(output)!=UINT32_MAX)return 8;count++;
 }
 for(unsigned role=0;role<ENEMIES_BORROW_COUNT;role++)for(unsigned width=1;width<=4;width*=2){
  unsigned at=0x2d69;enemies_borrow_write((EnemiesBorrower)role,DATA_SEG,(uint16_t)at,width,0xfedcba98u);
  for(unsigned b=0;b<width;b++)expected[lin(DATA_SEG,(uint16_t)at)+b]=(uint8_t)(0xfedcba98u>>(8*b));
  memcpy(output,ugh_mem,sizeof output);enemies_serialize(output);if(memcmp(output,expected,sizeof output))return 9;
 }
 for(unsigned d=0;d<3;d++){
  enemies_borrow_write(ENEMIES_BORROW_ACTORS,(uint16_t)(DATA_SEG+d),(uint16_t)(0x2cad -16*d+10),2,0xabcd);
  if(w->slot[0].platform!=0xabcd || w->slot[0].descriptor_word==0xabcd)return 10;
 }
 /* Raw resource/list storage stays live, mutable and outside this owner. */
 for(unsigned at=0x7200;at<0x7220;at++){
  if(enemies_is_owned(lin(DATA_SEG,(uint16_t)at)))return 11;
  enemies_borrow_write(ENEMIES_BORROW_RESOURCES,DATA_SEG,(uint16_t)at,1,at&255);
  if(enemies_borrow_read(ENEMIES_BORROW_SESSION,DATA_SEG,(uint16_t)at,1)!=(at&255))return 12;
 }
 if(enemies_is_owned(lin(DATA_SEG,0x2d6b)) || enemies_is_owned(lin(DATA_SEG,0x2cac)))return 13;
 enemies_borrow_write(ENEMIES_BORROW_ACTORS,DATA_SEG,0x2cad+10,2,0x78dc);if(w->slot[0].platform!=0x78dc)return 15;
 enemies_require_seal(ugh_mem);enemies_serialize(output);output[words[0].address]^=1;if(enemies_check_serialization(output)!=words[0].address)return 14;
 printf("{\"bytes\":190,\"byte_values\":%u,\"word_roundtrips\":6225920,\"roles\":%u,\"slots\":5,\"raw_aliases\":true,\"mutable_resources\":true}\n",count,ENEMIES_BORROW_COUNT);return 0;
}
