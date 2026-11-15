#ifndef NATIVE_ITEMSTATE_WORLD_BRIDGE_H
#define NATIVE_ITEMSTATE_WORLD_BRIDGE_H
#include "ugh.h"
#include "../item_world.h"
typedef enum ItemstateBorrower {
 ITEMSTATE_BORROW_SESSION,ITEMSTATE_BORROW_WATER,ITEMSTATE_BORROW_MENUS,ITEMSTATE_BORROW_SCORES,
 ITEMSTATE_BORROW_INPUT,ITEMSTATE_BORROW_HUD,ITEMSTATE_BORROW_PHYSICS,ITEMSTATE_BORROW_ACTORS,
 ITEMSTATE_BORROW_ITEMS,ITEMSTATE_BORROW_DEMO,ITEMSTATE_BORROW_RENDER,ITEMSTATE_BORROW_RESOURCES,
 ITEMSTATE_BORROW_WINDOW,ITEMSTATE_BORROW_COUNT
} ItemstateBorrower;
void itemstate_cold_import(uint8_t *memory);
void itemstate_require_seal(const uint8_t *memory);
unsigned itemstate_owned_bytes(void);
int itemstate_is_owned(uint32_t address);
int itemstate_shared_read(uint32_t address,uint8_t *value);
int itemstate_shared_write(uint32_t address,uint8_t value);
void itemstate_serialize(uint8_t *output);
uint32_t itemstate_check_serialization(const uint8_t *output);
uint8_t itemstate_borrowed_byte(const uint8_t *window,uint32_t index);
void itemstate_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
uint32_t itemstate_borrow_read(ItemstateBorrower borrower,uint16_t bank,uint16_t position,unsigned width);
void itemstate_borrow_write(ItemstateBorrower borrower,uint16_t bank,uint16_t position,unsigned width,uint32_t value);
#endif
