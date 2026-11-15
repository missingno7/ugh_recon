/* Independent historical address/named-member oracle for the 5A binding. */
#include "run_world_bridge.h"
#include <stdio.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
uint8_t presentation_borrowed_byte(const uint8_t*p,uint32_t i){return p[i];}
void presentation_borrowed_store(uint8_t*p,uint32_t i,uint8_t v){p[i]=v;}
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE],wanted[UGH_MEM_SIZE];
static struct {unsigned address;uint16_t *word;} words[21];static unsigned nw;
static struct {unsigned address;uint8_t *byte;} bytes[327];static unsigned nb;
static void word(unsigned at,uint16_t *p){words[nw].address=lin(DATA_SEG,(uint16_t)at);words[nw++].word=p;wanted[lin(DATA_SEG,(uint16_t)at)]=wanted[lin(DATA_SEG,(uint16_t)(at+1))]=1;}
static void byte(unsigned at,uint8_t *p){bytes[nb].address=lin(DATA_SEG,(uint16_t)at);bytes[nb++].byte=p;wanted[lin(DATA_SEG,(uint16_t)at)]=1;}
int main(void){NativeRunWorld*w=native_run_world();
 word(0x2634,&w->configuration.players);word(0x2636,&w->configuration.player_bytes);
 word(0x263f,&w->configuration.control_mode[0]);word(0x2641,&w->configuration.control_mode[1]);word(0x2638,&w->configuration.difficulty);
 word(0x261c,&w->level);word(0x2622,&w->timer);word(0x27a8,&w->fade_level);word(0x27aa,&w->fade_step);word(0x2903,&w->water_y);
 word(0x28e9,&w->record.map.value);word(0x28eb,&w->record.platforms.value);word(0x28ed,&w->record.actors.value);word(0x28ef,&w->record.enemies.value);word(0x28f3,&w->record.introduction.value);
 word(0x28f6,&w->record.player_start[0][0]);word(0x28f8,&w->record.player_start[0][1]);word(0x28fa,&w->record.player_start[1][0]);word(0x28fc,&w->record.player_start[1][1]);word(0x28fe,&w->record.water_fixed);word(0x2900,&w->record.water_step);
 byte(0x263c,&w->lives);byte(0x263d,&w->multiplier);byte(0x27cf,&w->completion);
 byte(0x28f1,&w->record.journeys);byte(0x28f2,&w->record.reserved_before_text);byte(0x28f5,&w->record.rain);byte(0x2902,&w->record.reserved_tail);
 for(unsigned i=0;i<320;i++)byte(0x264c+i,&w->tiles[i]);
 unsigned score=lin(DATA_SEG,0x261e);for(unsigned i=0;i<4;i++)wanted[score+i]=1;
 if(nw!=21 || nb!=327)return 1;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(expected,ugh_mem,sizeof expected);run_cold_import(ugh_mem);if(run_owned_bytes()!=373)return 2;
 memcpy(output,ugh_mem,sizeof output);run_serialize(output);
 if(memcmp(output,expected,sizeof output))return 18;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(run_is_owned(a)!=(int)wanted[a])return 3;
 for(unsigned i=0;i<nw;i++){
  unsigned a=words[i].address;if(*words[i].word!=(unsigned)(expected[a]|expected[a+1]*256u))return 4;
  for(unsigned v=0;v<65536;v++){
   run_shared_write(a,(uint8_t)v);run_borrowed_store(ugh_mem,a+1,(uint8_t)(v>>8));expected[a]=(uint8_t)v;expected[a+1]=(uint8_t)(v>>8);
   if(*words[i].word!=v || run_borrow_read(RUN_BORROW_SESSION,DATA_SEG,(uint16_t)(a-((uint32_t)DATA_SEG<<4)),2)!=v)return 5;
  }
 }
 for(unsigned h=0;h<2;h++)for(unsigned v=0;v<65536;v++){
  unsigned a=score+h*2;run_borrow_write(RUN_BORROW_HUD,DATA_SEG,(uint16_t)(a-((uint32_t)DATA_SEG<<4)),2,v);expected[a]=(uint8_t)v;expected[a+1]=(uint8_t)(v>>8);
  if(((w->score>>(h*16))&65535u)!=v)return 6;
 }
 for(unsigned i=0;i<nb;i++){unsigned a=bytes[i].address;if(*bytes[i].byte!=expected[a])return 7;}
 memcpy(output,ugh_mem,sizeof output);run_serialize(output);if(memcmp(output,expected,sizeof output))return 8;
 unsigned values=0;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(wanted[a])for(unsigned v=0;v<256;v++){
  run_borrowed_store(ugh_mem,a,(uint8_t)v);expected[a]=(uint8_t)v;uint8_t now;
  if(!run_shared_read(a,&now) || now!=v || run_borrowed_byte(ugh_mem+(a&~15u),a&15u)!=v)return 9;
  run_serialize(output);if(memcmp(output,expected,sizeof output) || run_check_serialization(output)!=UINT32_MAX)return 10;values++;
 }
 for(unsigned i=0;i<26;i++)for(unsigned width=1;width<=4;width*=2){
  unsigned at=0x28e9+i;run_borrow_write(RUN_BORROW_SESSION,DATA_SEG,(uint16_t)at,width,0xfedcba98u);
  for(unsigned b=0;b<width;b++)expected[lin(DATA_SEG,(uint16_t)at)+b]=(uint8_t)(0xfedcba98u>>(8*b));
  memcpy(output,ugh_mem,sizeof output);run_serialize(output);if(memcmp(output,expected,sizeof output))return 11;
 }
 for(unsigned i=0;i<RUN_BORROW_COUNT;i++)for(unsigned width=1;width<=4;width*=2){
  unsigned at=0x264c+317;uint32_t v=run_borrow_read((RunBorrower)i,DATA_SEG,(uint16_t)at,width);
  uint32_t want=0;for(unsigned b=0;b<width;b++)want|=(uint32_t)expected[lin(DATA_SEG,(uint16_t)at)+b]<<(8*b);
  if(v!=want)return 12;
 }
 for(unsigned i=0;i<2;i++)if(run_borrow_read(RUN_BORROW_INPUT,DATA_SEG,(uint16_t)(0x263f+2*i),2)!=w->configuration.control_mode[i])return 17;
 for(unsigned delta=0;delta<3;delta++){
  uint16_t bank=(uint16_t)(DATA_SEG+delta),offset=(uint16_t)(0x2903-delta*16);
  run_borrow_write(RUN_BORROW_MENUS,bank,offset,2,0xabcd);if(w->water_y!=0xabcd)return 13;
 }
 if(run_is_owned(lin(DATA_SEG,0x2905)) || run_is_owned(lin(DATA_SEG,0x27c8)) || run_is_owned(lin(DATA_SEG,0x2800)))return 14;
 run_require_seal(ugh_mem);run_serialize(output);output[score]^=1;if(run_check_serialization(output)!=score)return 15;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(!wanted[a]){uint8_t v=49;if(run_shared_read(a,&v) || run_shared_write(a,17) || v!=49)return 16;}
 printf("{\"owned_bytes\":373,\"byte_values\":%u,\"word_roundtrips\":1507328,\"borrower_roles\":%u,\"record_straddle_cases\":78,\"private_bytes\":%u}\n",values,RUN_BORROW_COUNT,(unsigned)sizeof *w);return 0;
}
