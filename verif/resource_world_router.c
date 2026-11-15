#include "resource_world_bridge.h"
#include <stdio.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
#include "../native/bridge/resource_world_bindings.inc"
#include "../native/resource_world_layout.inc"
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE];
int main(void){
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(expected,ugh_mem,sizeof expected);resource_data_cold_import(ugh_mem);
 memcpy(output,ugh_mem,sizeof output);resource_data_serialize(output);
 if(memcmp(output,expected,sizeof output))return 1;
 unsigned total=0;
 for(unsigned n=0;n<RESOURCE_WORLD_REGIONS;n++){
  const ResourceAllocation *a=resource_world_allocation(n);total+=a->size;
  if(a->offset!=allocations[n].offset||a->size!=allocations[n].size)return 14;
  for(unsigned j=0;j<a->size;j++)for(unsigned v=0;v<256;v++){
   uint32_t address=addresses[n]+j;uint8_t before=resource_world_bootstrap(n)[(j+1)%a->size],now;
   if(!resource_data_shared_write(address,(uint8_t)v)||!resource_data_shared_read(address,&now)||now!=v)return 2;
   if(a->size>1&&resource_world_bootstrap(n)[(j+1)%a->size]!=before)return 3;
   expected[address]=(uint8_t)v;
  }
 }
 for(unsigned i=0;i<RESOURCE_WORLD_VIEWS;i++){
  ResourceWorldToken token={(uint16_t)i},back;ResourceWorldView view;uint16_t bank,offset;
  if(!resource_world_view(token,&view)||!resource_world_to_legacy(token,&bank,&offset)||!resource_world_from_legacy(bank,offset,view.size,&back))return 4;
  if(view.allocation!=views[i].allocation||view.offset!=views[i].offset||view.size!=views[i].size)return 15;
  ResourceWorldView alias;resource_world_view(back,&alias);
  if(alias.allocation!=view.allocation||alias.offset!=view.offset||alias.size!=view.size)return 5;
  for(unsigned role=0;role<RESOURCE_BORROW_COUNT;role++){
   uint8_t value=19;
   if(resource_world_read((ResourceBorrower)role,token,view.size,&value)||value!=19||resource_world_store((ResourceBorrower)role,token,view.size,0))return 6;
   if(resource_world_read((ResourceBorrower)role,token,UINT32_MAX,&value)||resource_world_store((ResourceBorrower)role,token,UINT32_MAX,0))return 16;
   if(!resource_world_store((ResourceBorrower)role,token,view.size-1,(uint8_t)i))return 7;
   if(!resource_data_shared_read(addresses[view.allocation]+view.offset+view.size-1,&value)||value!=(uint8_t)i)return 8;
   expected[addresses[view.allocation]+view.offset+view.size-1]=(uint8_t)i;
  }
 }
 for(unsigned i=RESOURCE_WORLD_VIEWS;i<65536;i++){
  ResourceWorldView v;uint8_t value=71;ResourceWorldToken invalid={(uint16_t)i};
  if(resource_world_view(invalid,&v)||resource_world_read(RESOURCE_BORROW_PLAYER,invalid,0,&value)||resource_world_store(RESOURCE_BORROW_PLAYER,invalid,0,0)||value!=71)return 17;
 }
 {uint8_t value=71;ResourceWorldToken t={0};if(resource_world_read(RESOURCE_BORROW_COUNT,t,0,&value)||resource_world_store(RESOURCE_BORROW_COUNT,t,0,0)||value!=71)return 18;}
 /* The two player views share 0CFC. A generic mutation must be live in both. */
 uint32_t shared=lin(DATA_SEG,D(PlayerAnimationCycleEnds));
 resource_data_shared_write(shared,37);expected[shared]=37;
 resource_data_shared_write(shared+1,89);expected[shared+1]=89;
 if(resource_data_borrow_read(RESOURCE_BORROW_PLAYER,DATA_SEG,D(PlayerAnimationCycleStarts)+2,2)!=(37u+89u*256u))return 9;
 /* Explicit alias endpoints cover the canonical 64KiB window without owning
  * the audio cells a second time or dropping the packed maps' retained tail. */
 uint32_t scratch=lin(UGH_S_ZERO_IceDecodeWorkspace,0);
 for(unsigned j=0;j<65536;j++){
  int own=resource_data_is_owned(scratch+j);
  if(own!=(j<64768||j>=64772))return 10;
 }
 resource_data_require_seal(ugh_mem);resource_data_serialize(output);
 if(resource_data_check_serialization(output)!=UINT32_MAX||memcmp(output,expected,sizeof output))return 11;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(!resource_data_is_owned(a)){uint8_t v=13;if(resource_data_shared_read(a,&v)||resource_data_shared_write(a,0)||v!=13)return 12;}
 if(total!=RESOURCE_WORLD_BYTES||total!=resource_data_owned_bytes())return 13;
 printf("{\"bytes\":%u,\"byte_values\":%llu,\"views\":%u,\"roles\":%u}\n",total,(unsigned long long)total*256,RESOURCE_WORLD_VIEWS,RESOURCE_BORROW_COUNT);return 0;
}
