/* Independent literal address/member oracle, not the bridge table. */
#include "platform_world_bridge.h"
#include <stdio.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
uint8_t resources_borrowed_byte(const uint8_t*p,uint32_t i){return p[i];}
void resources_borrowed_store(uint8_t*p,uint32_t i,uint8_t v){p[i]=v;}
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE],wanted[UGH_MEM_SIZE];
static struct {unsigned address;uint16_t*value;} words[80];static unsigned nw;
static void bind(unsigned at,uint16_t*p){unsigned a=lin(DATA_SEG,(uint16_t)at);words[nw].address=a;words[nw++].value=p;wanted[a]=wanted[a+1]=1;}
#define TEN(at,m) for(unsigned i=0;i<10;i++)bind(at+2*i,&w->slot[i].m)
int main(void){NativePlatformsWorld*w=native_platforms_world();
 TEN(0x290d,left);TEN(0x2921,right);TEN(0x2935,height);TEN(0x2949,arrival);
 TEN(0x295d,wait);TEN(0x2971,spawn);TEN(0x2985,icon);TEN(0x2999,occupant);
 if(nw!=80)return 1;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(expected,ugh_mem,sizeof expected);platforms_cold_import(ugh_mem);
 if(platforms_owned_bytes()!=160)return 2;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(platforms_is_owned(a)!=(int)wanted[a])return 3;
 memcpy(output,ugh_mem,sizeof output);platforms_serialize(output);if(memcmp(output,expected,sizeof output))return 4;
 for(unsigned i=0;i<nw;i++){
  unsigned a=words[i].address;if(*words[i].value!=(unsigned)(expected[a]|expected[a+1]*256u))return 5;
  for(unsigned v=0;v<65536;v++){
   platforms_borrow_write(PLATFORMS_BORROW_SESSION,DATA_SEG,(uint16_t)(a-((uint32_t)DATA_SEG<<4)),2,v);expected[a]=(uint8_t)v;expected[a+1]=(uint8_t)(v>>8);
   if(*words[i].value!=v || platforms_borrow_read(PLATFORMS_BORROW_PHYSICS,DATA_SEG,(uint16_t)(a-((uint32_t)DATA_SEG<<4)),2)!=v)return 6;
  }
 }
 unsigned count=0;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(wanted[a])for(unsigned v=0;v<256;v++){
  platforms_borrowed_store(ugh_mem,a,(uint8_t)v);expected[a]=(uint8_t)v;uint8_t now;
  if(!platforms_shared_read(a,&now)||now!=v||platforms_borrowed_byte(ugh_mem+(a&~15u),a&15u)!=v)return 7;
  platforms_serialize(output);if(memcmp(output,expected,sizeof output)||platforms_check_serialization(output)!=UINT32_MAX)return 8;count++;
 }
 for(unsigned role=0;role<PLATFORMS_BORROW_COUNT;role++)for(unsigned width=1;width<=4;width*=2){
  unsigned at=0x29ab;platforms_borrow_write((PlatformsBorrower)role,DATA_SEG,(uint16_t)at,width,0xfedcba98u);
  for(unsigned b=0;b<width;b++)expected[lin(DATA_SEG,(uint16_t)at)+b]=(uint8_t)(0xfedcba98u>>(8*b));
  memcpy(output,ugh_mem,sizeof output);platforms_serialize(output);if(memcmp(output,expected,sizeof output))return 9;
 }
 for(unsigned d=0;d<3;d++){
  platforms_borrow_write(PLATFORMS_BORROW_ACTORS,(uint16_t)(DATA_SEG+d),(uint16_t)(0x290d -16*d+20),2,0xabcd);
  if(w->slot[0].right!=0xabcd || w->slot[0].left==0xabcd)return 10;
 }
 /* Raw resource/list storage stays live, mutable and outside this owner. */
 for(unsigned at=0x7200;at<0x7220;at++){
  if(platforms_is_owned(lin(DATA_SEG,(uint16_t)at)))return 11;
  platforms_borrow_write(PLATFORMS_BORROW_RESOURCES,DATA_SEG,(uint16_t)at,1,at&255);
  if(platforms_borrow_read(PLATFORMS_BORROW_SESSION,DATA_SEG,(uint16_t)at,1)!=(at&255))return 12;
 }
 if(platforms_is_owned(lin(DATA_SEG,0x29ad)) || platforms_is_owned(lin(DATA_SEG,0x290c)))return 13;
 platforms_require_seal(ugh_mem);platforms_serialize(output);output[words[0].address]^=1;if(platforms_check_serialization(output)!=words[0].address)return 14;
 printf("{\"bytes\":160,\"byte_values\":%u,\"word_roundtrips\":5242880,\"roles\":%u,\"slots\":10,\"raw_aliases\":true,\"mutable_resources\":true}\n",count,PLATFORMS_BORROW_COUNT);return 0;
}
