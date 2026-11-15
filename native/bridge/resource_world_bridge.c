#include "platform.h"
#include "resource_world_bridge.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "resource_world_bindings.inc"
static unsigned active;
static int resource_data_field(uint32_t address,unsigned *slot,unsigned *lane){
 unsigned lo=0,hi=RESOURCE_WORLD_REGIONS;
 while(lo<hi){unsigned mid=lo+(hi-lo)/2;if(address<addresses[mid])hi=mid;else lo=mid+1;}
 if(!lo)return 0;
 unsigned n=lo-1;const ResourceAllocation *a=resource_world_allocation(n);
 if(address-addresses[n]>=a->size)return 0;
 *slot=n;*lane=address-addresses[n];return 1;
}
int resource_data_is_owned(uint32_t address){unsigned slot,lane;return active&&resource_data_field(address,&slot,&lane);}
int resource_data_shared_read(uint32_t address,uint8_t *value){
 unsigned slot,lane;if(!active||!resource_data_field(address,&slot,&lane))return 0;
#if RESOURCE_DATA_TEST_FAULT == 3
 if(address>=lin(UGH_S_ZERO_IceDecodeWorkspace,32000)&&address<lin(UGH_S_ZERO_IceDecodeWorkspace,64768)){*value=0;return 1;}
#endif
 *value=resource_world_bootstrap(slot)[lane];return 1;
}
int resource_data_shared_write(uint32_t address,uint8_t value){
 unsigned slot,lane;if(!active||!resource_data_field(address,&slot,&lane))return 0;
#if RESOURCE_DATA_TEST_FAULT == 1
 if(address==lin(DATA_SEG,D(PlayerAnimationCycleEnds)))return 1;
#endif
 resource_world_bootstrap(slot)[lane]=value;return 1;
}
unsigned resource_data_owned_bytes(void){return active?RESOURCE_WORLD_BYTES:0;}
void resource_data_cold_import(uint8_t *memory){
 active=0;
 for(unsigned i=0;i<RESOURCE_WORLD_REGIONS;i++){
  unsigned size=resource_world_allocation(i)->size;
  memcpy(resource_world_bootstrap(i),memory+addresses[i],size);
  memset(memory+addresses[i],0xa5,size);
 }
 active=1;
}
void resource_data_require_seal(const uint8_t *memory){
 if(!active)return;
 for(unsigned i=0;i<RESOURCE_WORLD_REGIONS;i++)for(unsigned j=0;j<resource_world_allocation(i)->size;j++)if(memory[addresses[i]+j]!=0xa5){fputs("resource data: sealed RAM violation\n",stderr);exit(88);}
}
void resource_data_serialize(uint8_t *output){
 if(!active)return;
 unsigned count=0;
 for(unsigned i=0;i<RESOURCE_WORLD_REGIONS;i++){
  unsigned size=resource_world_allocation(i)->size;
#if RESOURCE_DATA_TEST_FAULT == 2
  if(!i){size--;}
#endif
  memcpy(output+addresses[i],resource_world_bootstrap(i),size);count+=size;
 }
 if(count!=resource_data_owned_bytes()){fputs("resource data: missed serialization\n",stderr);exit(88);}
}
uint32_t resource_data_check_serialization(const uint8_t *output){
 if(active)for(unsigned i=0;i<RESOURCE_WORLD_REGIONS;i++)for(unsigned j=0;j<resource_world_allocation(i)->size;j++)if(output[addresses[i]+j]!=resource_world_bootstrap(i)[j])return addresses[i]+j;
 return UINT32_MAX;
}
uint8_t resource_data_borrowed_byte(const uint8_t *window,uint32_t index){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base&&p-base+index<UGH_MEM_SIZE){uint8_t v;if(resource_data_shared_read((uint32_t)(p-base+index),&v))return v;}
 return window[index];
}
void resource_data_borrowed_store(uint8_t *window,uint32_t index,uint8_t value){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base&&p-base+index<UGH_MEM_SIZE&&resource_data_shared_write((uint32_t)(p-base+index),value))return;
 window[index]=value;
}
int resource_world_to_legacy(ResourceWorldToken token,uint16_t *bank,uint16_t *offset){
 ResourceWorldView view;if(!resource_world_view(token,&view))return 0;
 uint32_t a=addresses[view.allocation]+view.offset;*bank=(uint16_t)(a/16);*offset=(uint16_t)(a%16);return 1;
}
int resource_world_from_legacy(uint16_t bank,uint16_t offset,uint32_t size,ResourceWorldToken *token){
 uint32_t address=lin(bank,offset);
 for(unsigned i=0;i<RESOURCE_WORLD_VIEWS;i++){
  ResourceWorldView v;resource_world_view((ResourceWorldToken){(uint16_t)i},&v);
  if(addresses[v.allocation]+v.offset==address&&v.size==size){*token=(ResourceWorldToken){(uint16_t)i};return 1;}
 }
 return 0;
}
uint32_t resource_data_borrow_read(ResourceBorrower role,uint16_t bank,uint16_t position,unsigned width){
 if(role>=RESOURCE_BORROW_COUNT||(width!=1&&width!=2&&width!=4))exit(88);
 uint32_t result=0,address=lin(bank,position);
 for(unsigned i=0;i<width;i++){uint8_t v;if(!resource_data_shared_read(address+i,&v))v=ugh_read(address+i);result|=(uint32_t)v<<(8*i);}
 return result;
}
void resource_data_borrow_write(ResourceBorrower role,uint16_t bank,uint16_t position,unsigned width,uint32_t value){
 if(role>=RESOURCE_BORROW_COUNT||(width!=1&&width!=2&&width!=4))exit(88);
 uint32_t address=lin(bank,position);
 for(unsigned i=0;i<width;i++)if(!resource_data_shared_write(address+i,(uint8_t)(value>>(8*i))))ugh_write(address+i,(uint8_t)(value>>(8*i)));
}
