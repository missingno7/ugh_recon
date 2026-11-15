#ifndef NATIVE_PLATFORMS_WORLD_BRIDGE_H
#define NATIVE_PLATFORMS_WORLD_BRIDGE_H
#include "ugh.h"
#include "../platform_world.h"
typedef enum PlatformsBorrower {
 PLATFORMS_BORROW_SESSION,PLATFORMS_BORROW_WATER,PLATFORMS_BORROW_MENUS,PLATFORMS_BORROW_SCORES,
 PLATFORMS_BORROW_INPUT,PLATFORMS_BORROW_HUD,PLATFORMS_BORROW_PHYSICS,PLATFORMS_BORROW_ACTORS,
 PLATFORMS_BORROW_ITEMS,PLATFORMS_BORROW_DEMO,PLATFORMS_BORROW_RENDER,PLATFORMS_BORROW_RESOURCES,
 PLATFORMS_BORROW_WINDOW,PLATFORMS_BORROW_COUNT
} PlatformsBorrower;
void platforms_cold_import(uint8_t *memory);
void platforms_require_seal(const uint8_t *memory);
unsigned platforms_owned_bytes(void);
int platforms_is_owned(uint32_t address);
int platforms_shared_read(uint32_t address,uint8_t *value);
int platforms_shared_write(uint32_t address,uint8_t value);
void platforms_serialize(uint8_t *output);
uint32_t platforms_check_serialization(const uint8_t *output);
uint8_t platforms_borrowed_byte(const uint8_t *window,uint32_t index);
void platforms_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
uint32_t platforms_borrow_read(PlatformsBorrower borrower,uint16_t bank,uint16_t position,unsigned width);
void platforms_borrow_write(PlatformsBorrower borrower,uint16_t bank,uint16_t position,unsigned width,uint32_t value);
#endif
