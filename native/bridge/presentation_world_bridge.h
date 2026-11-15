#ifndef PRESENTATION_WORLD_BRIDGE_H
#define PRESENTATION_WORLD_BRIDGE_H
#include "ugh.h"
#include "../presentation_world.h"
int presentation_is_owned(uint32_t address);
int presentation_shared_read(uint32_t address,uint8_t *value);
int presentation_shared_write(uint32_t address,uint8_t value);
void presentation_cold_import(uint8_t *memory);
void presentation_require_seal(const uint8_t *memory);
void presentation_serialize(uint8_t *output);
uint32_t presentation_check_serialization(const uint8_t *output);
unsigned presentation_owned_bytes(void);
uint8_t presentation_borrowed_byte(const uint8_t *window,uint32_t index);
void presentation_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
#endif
