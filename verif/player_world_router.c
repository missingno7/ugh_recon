/* Independent literal-address/member oracle; no implementation table import. */
#include "player_world_bridge.h"
#include <stdio.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
uint8_t rng_borrowed_byte(const uint8_t*p,uint32_t i){return p[i];}
void rng_borrowed_store(uint8_t*p,uint32_t i,uint8_t v){p[i]=v;}
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE],wanted[UGH_MEM_SIZE];
static struct {unsigned address;uint16_t *word;} words[46];static unsigned nw;
static void word(unsigned at,uint16_t *p){unsigned a=lin(DATA_SEG,(uint16_t)at);words[nw].address=a;words[nw++].word=p;wanted[a]=wanted[a+1]=1;}
#define BOTH(at,m) for(unsigned p=0;p<2;p++)word(at+2*p,&w->player[p].m)
int main(void){NativePlayerWorld*w=native_player_world();
 BOTH(0x278c,up);BOTH(0x2790,down);BOTH(0x2794,left);BOTH(0x2798,right);BOTH(0x279c,action);
 BOTH(0x27d0,fixed_x);BOTH(0x27d4,fixed_y);BOTH(0x27d8,pixel_x);BOTH(0x27dc,pixel_y);
 BOTH(0x27e0,cached_x);BOTH(0x27e4,cached_y);BOTH(0x27e8,sprite);BOTH(0x27ec,cached_sprite);
 BOTH(0x27f0,animation);BOTH(0x27f4,thrust);BOTH(0x27f8,platform);BOTH(0x27fc,carried);
 BOTH(0x2804,destination);BOTH(0x2808,fare);BOTH(0x280c,minimum_fare);
 BOTH(0x2810,velocity_x);BOTH(0x2814,velocity_y);BOTH(0x2818,impact);
 if(nw!=46 || sizeof *w!=92)return 1;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(expected,ugh_mem,sizeof expected);player_cold_import(ugh_mem);if(player_owned_bytes()!=92)return 2;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(player_is_owned(a)!=(int)wanted[a])return 3;
 memcpy(output,ugh_mem,sizeof output);player_serialize(output);if(memcmp(output,expected,sizeof output))return 4;
 for(unsigned i=0;i<nw;i++){
  unsigned a=words[i].address;if(*words[i].word!=(unsigned)(expected[a]|expected[a+1]*256u))return 5;
  for(unsigned v=0;v<65536;v++){
   player_borrow_write(PLAYER_BORROW_SESSION,DATA_SEG,(uint16_t)(a-((uint32_t)DATA_SEG<<4)),2,v);expected[a]=(uint8_t)v;expected[a+1]=(uint8_t)(v>>8);
   if(*words[i].word!=v || player_borrow_read(PLAYER_BORROW_PHYSICS,DATA_SEG,(uint16_t)(a-((uint32_t)DATA_SEG<<4)),2)!=v)return 6;
  }
 }
 unsigned values=0;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(wanted[a])for(unsigned v=0;v<256;v++){
  player_borrowed_store(ugh_mem,a,(uint8_t)v);expected[a]=(uint8_t)v;uint8_t now;
  if(!player_shared_read(a,&now) || now!=v || player_borrowed_byte(ugh_mem+(a&~15u),a&15u)!=v)return 7;
  player_serialize(output);if(memcmp(output,expected,sizeof output) || player_check_serialization(output)!=UINT32_MAX)return 8;values++;
 }
 for(unsigned i=0;i<PLAYER_BORROW_COUNT;i++)for(unsigned width=1;width<=4;width*=2){
  unsigned at=0x27fe;player_borrow_write((PlayerBorrower)i,DATA_SEG,(uint16_t)at,width,0xfedcba98u);
  for(unsigned b=0;b<width;b++)expected[lin(DATA_SEG,(uint16_t)at)+b]=(uint8_t)(0xfedcba98u>>(8*b));
  memcpy(output,ugh_mem,sizeof output);player_serialize(output);if(memcmp(output,expected,sizeof output))return 9;
 }
 for(unsigned d=0;d<3;d++){
  player_borrow_write(PLAYER_BORROW_INPUT,(uint16_t)(DATA_SEG+d),(uint16_t)(0x279e - 16*d),2,0xabcd);
  if(w->player[1].action!=0xabcd || w->player[0].action==0xabcd)return 10;
 }
 /* Foreign immutable/shared resource view. 0CFC is one physical word, both
  * player0's end and player1's start; no native duplicate is invented. */
 if(player_is_owned(lin(DATA_SEG,0xcfa)) || player_is_owned(lin(DATA_SEG,0xcfc)) || player_is_owned(lin(DATA_SEG,0xcfe)))return 11;
 player_borrow_write(PLAYER_BORROW_RESOURCES,DATA_SEG,0xcfc,2,0x8bad);
 if(player_borrow_read(PLAYER_BORROW_RENDER,DATA_SEG,(uint16_t)(D(PlayerAnimationCycleEnds)+0),2)!=0x8bad || player_borrow_read(PLAYER_BORROW_RENDER,DATA_SEG,(uint16_t)(D(PlayerAnimationCycleStarts)+2),2)!=0x8bad)return 12;
 for(unsigned a=lin(DATA_SEG,0x2800);a<lin(DATA_SEG,0x2804);a++)if(player_is_owned(a))return 13;
 player_require_seal(ugh_mem);player_serialize(output);output[words[0].address]^=1;if(player_check_serialization(output)!=words[0].address)return 14;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(!wanted[a]){uint8_t v=49;if(player_shared_read(a,&v) || player_shared_write(a,17) || v!=49)return 15;}
 printf("{\"owned_bytes\":92,\"byte_values\":%u,\"word_roundtrips\":3014656,\"roles\":%u,\"shared_cycle_word\":true,\"both_players\":true}\n",values,PLAYER_BORROW_COUNT);return 0;
}
