/* Independent full-memory and ordered-service comparisons of maintained loader
 * fragments, compiled verbatim for original and native. No hand model. */
#include "ugh.h"
#include "session.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
static uint8_t before[UGH_MEM_SIZE],expected[UGH_MEM_SIZE];
static unsigned phase,respawns,advances,calls,failed_at;static uint16_t order[1024];
#define REQUIRE(c) do{if(!(c)){fprintf(stderr,"loader line %u phase %u call %u\n",__LINE__,phase,calls);exit(3);}}while(0)
static uint16_t sq_word(uint16_t a,uint16_t b){REQUIRE(a==b);return a;}
static int sq_bool(int a,int b){REQUIRE(!!a==!!b);return !!a;}
static void cmp8(Regs*r,uint8_t a,uint8_t b){uint8_t v=(uint8_t)(a-b);flag(r,CF,a<b);flag(r,OF,((a^b)&(a^v)&128)!=0);flag(r,AF,((a^b^v)&16)!=0);szp(r,v,8);}
#define B(n) rd8(r->ds,D(n))
#define WI(n,i,v) wr16(r->ds,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define sessionstate_read16 rd16
static int request(Regs*r,unsigned target){
 order[calls]=(uint16_t)(target?0x8000u:r->bx);calls++;
 if(calls==failed_at)return 4;
 if(!target){REQUIRE(!advances);respawns++;}else advances++;
 return 0;
}
#define CALL(n,owner,delta) do{int status=request(r,G(n)==G(AdvanceRainParticles));if(status)return status;}while(0)
/* INSERT ACTUAL FRAGMENTS */
static void initial(void){for(unsigned i=0;i<UGH_MEM_SIZE;i++)before[i]=(uint8_t)(i*193u+(i>>8)*73u);}
int main(void){initial();unsigned copies=0,prefixes=0;
 for(unsigned shift=0;shift<80;shift++)for(unsigned df=0;df<2;df++){
  Regs a={0},b;a.ds=DATA_SEG;a.bx=(uint16_t)(D(CurrentLevelRecord)+shift-40u);a.flags=(uint16_t)(0x202u|(df?DF:0));b=a;
  memcpy(ugh_mem,before,sizeof before);phase=0;original_copy(&a);memcpy(expected,ugh_mem,sizeof expected);
  memcpy(ugh_mem,before,sizeof before);phase=1;modern_copy(&b);REQUIRE(!memcmp(&a,&b,sizeof a));REQUIRE(!memcmp(expected,ugh_mem,sizeof expected));copies++;
 }
 for(unsigned wet=0;wet<2;wet++)for(unsigned failure=0;failure<772;failure++){
  Regs a={0},b;a.ds=DATA_SEG;a.flags=0x202;b=a;uint16_t expected_order[1024];
  memcpy(ugh_mem,before,sizeof before);wr8(DATA_SEG,D(LevelRainDirection),(uint8_t)wet);phase=2;respawns=advances=calls=0;failed_at=failure;int left=original_rain(&a);unsigned count=calls;memcpy(expected_order,order,count*2);memcpy(expected,ugh_mem,sizeof expected);
  if(!failure && wet)REQUIRE(respawns==193 && advances==577 && count==770);
  memcpy(ugh_mem,before,sizeof before);wr8(DATA_SEG,D(LevelRainDirection),(uint8_t)wet);phase=3;respawns=advances=calls=0;int right=modern_rain(&b);
  REQUIRE(left==right && !memcmp(&a,&b,sizeof a));REQUIRE(count==calls && !memcmp(order,expected_order,count*2));REQUIRE(!memcmp(expected,ugh_mem,sizeof expected));prefixes++;
 }
 printf("{\"copy_alias_cases\":%u,\"rain_failure_prefixes\":%u,\"respawns\":193,\"advances\":577}\n",copies,prefixes);return 0;
}
