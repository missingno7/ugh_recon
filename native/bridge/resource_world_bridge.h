#ifndef RESOURCE_WORLD_BRIDGE_H
#define RESOURCE_WORLD_BRIDGE_H
#include "ugh.h"
#include "../resource_world.h"
void resource_data_cold_import(uint8_t*);
void resource_data_require_seal(const uint8_t*);
void resource_data_serialize(uint8_t*);
uint32_t resource_data_check_serialization(const uint8_t*);
unsigned resource_data_owned_bytes(void);
int resource_data_is_owned(uint32_t);
int resource_data_shared_read(uint32_t,uint8_t*);
int resource_data_shared_write(uint32_t,uint8_t);
uint8_t resource_data_borrowed_byte(const uint8_t*,uint32_t);
void resource_data_borrowed_store(uint8_t*,uint32_t,uint8_t);
int resource_world_from_legacy(uint16_t bank,uint16_t offset,uint32_t size,ResourceWorldToken*);
int resource_world_to_legacy(ResourceWorldToken,uint16_t*,uint16_t*);
uint32_t resource_data_borrow_read(ResourceBorrower,uint16_t,uint16_t,unsigned);
void resource_data_borrow_write(ResourceBorrower,uint16_t,uint16_t,unsigned,uint32_t);
#endif
