#ifndef NATIVE_RESOURCE_CATALOG_BRIDGE_H
#define NATIVE_RESOURCE_CATALOG_BRIDGE_H
#include "ugh.h"
#include "../resource_catalog.h"
int resources_is_owned(uint32_t address);
int resources_shared_read(uint32_t address,uint8_t *value);
int resources_shared_write(uint32_t address,uint8_t value);
unsigned resources_owned_bytes(void);
void resources_cold_import(uint8_t *memory);
void resources_require_seal(const uint8_t *memory);
void resources_serialize(uint8_t *output);
uint32_t resources_check_serialization(const uint8_t *output);
uint8_t resources_borrowed_byte(const uint8_t *window,uint32_t index);
void resources_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
int resource_sprite_from_legacy(uint16_t ordinal,ResourceToken *token);
int resource_table_from_legacy(uint16_t word,ResourceToken *token);
int resource_effect_from_legacy(uint16_t word,ResourceToken *token);
int resource_token_to_legacy(ResourceToken token,uint16_t *word);
#endif
