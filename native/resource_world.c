#include "resource_world.h"
#include "resource_world_layout.inc"
static uint8_t storage[RESOURCE_WORLD_BYTES];
const ResourceAllocation *resource_world_allocation(unsigned index){return index<RESOURCE_WORLD_REGIONS?allocations+index:0;}
uint8_t *resource_world_bootstrap(unsigned allocation){const ResourceAllocation *a=resource_world_allocation(allocation);return a?storage+a->offset:0;}
int resource_world_view(ResourceWorldToken token,ResourceWorldView *view){
 if(token.index>=RESOURCE_WORLD_VIEWS || !view)return 0;
#if RESOURCE_DATA_TEST_FAULT == 4
 if(token.index<2)token.index^=1;
#endif
 *view=views[token.index];return 1;
}
static int resource_world_position(ResourceBorrower borrower,ResourceWorldToken token,uint32_t position,uint32_t *index){
 ResourceWorldView view;
 if(borrower>=RESOURCE_BORROW_COUNT || !resource_world_view(token,&view) || position>=view.size)return 0;
 *index=allocations[view.allocation].offset+view.offset+position;return 1;
}
int resource_world_read(ResourceBorrower borrower,ResourceWorldToken token,uint32_t position,uint8_t *value){
 uint32_t index;if(!value || !resource_world_position(borrower,token,position,&index))return 0;
 *value=storage[index];return 1;
}
int resource_world_store(ResourceBorrower borrower,ResourceWorldToken token,uint32_t position,uint8_t value){
 uint32_t index;if(!resource_world_position(borrower,token,position,&index))return 0;
 storage[index]=value;return 1;
}
