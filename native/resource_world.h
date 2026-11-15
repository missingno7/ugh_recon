#ifndef NATIVE_RESOURCE_WORLD_H
#define NATIVE_RESOURCE_WORLD_H
#include <stdint.h>
#include <stddef.h>
#include "resource_world_layout.h"
/* Version-one provider identities. A view never owns a second copy. Encoded
 * descriptor/callback words remain compatibility data, never dispatch keys. */
typedef struct ResourceWorldToken {uint16_t index;} ResourceWorldToken;
typedef struct ResourceWorldView {uint16_t allocation;uint32_t offset,size;} ResourceWorldView;
typedef struct ResourceAllocation {uint32_t offset,size;} ResourceAllocation;
typedef enum ResourceBorrower {
 RESOURCE_BORROW_CODEC,RESOURCE_BORROW_RENDER,RESOURCE_BORROW_PLAYER,
 RESOURCE_BORROW_SESSION,RESOURCE_BORROW_ACTORS,RESOURCE_BORROW_FRONT_END,
 RESOURCE_BORROW_AUDIO,RESOURCE_BORROW_COPY_DECIMAL,RESOURCE_BORROW_COUNT
} ResourceBorrower;
const ResourceAllocation *resource_world_allocation(unsigned index);
int resource_world_view(ResourceWorldToken token,ResourceWorldView *view);
int resource_world_read(ResourceBorrower borrower,ResourceWorldToken token,uint32_t position,uint8_t *value);
int resource_world_store(ResourceBorrower borrower,ResourceWorldToken token,uint32_t position,uint8_t value);
/* Provider bootstrap and byte router share the same allocation, including
 * scratch and retained padding. No persistent full-window scratch copy exists. */
uint8_t *resource_world_bootstrap(unsigned allocation);
#endif
