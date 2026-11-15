#ifndef NATIVE_ENEMIES_WORLD_BRIDGE_H
#define NATIVE_ENEMIES_WORLD_BRIDGE_H
#include "ugh.h"
#include "../enemy_world.h"
typedef enum EnemiesBorrower {
 ENEMIES_BORROW_SESSION,ENEMIES_BORROW_WATER,ENEMIES_BORROW_MENUS,ENEMIES_BORROW_SCORES,
 ENEMIES_BORROW_INPUT,ENEMIES_BORROW_HUD,ENEMIES_BORROW_PHYSICS,ENEMIES_BORROW_ACTORS,
 ENEMIES_BORROW_ITEMS,ENEMIES_BORROW_DEMO,ENEMIES_BORROW_RENDER,ENEMIES_BORROW_RESOURCES,
 ENEMIES_BORROW_WINDOW,ENEMIES_BORROW_COUNT
} EnemiesBorrower;
void enemies_cold_import(uint8_t *memory);
void enemies_require_seal(const uint8_t *memory);
unsigned enemies_owned_bytes(void);
int enemies_is_owned(uint32_t address);
int enemies_shared_read(uint32_t address,uint8_t *value);
int enemies_shared_write(uint32_t address,uint8_t value);
void enemies_serialize(uint8_t *output);
uint32_t enemies_check_serialization(const uint8_t *output);
uint8_t enemies_borrowed_byte(const uint8_t *window,uint32_t index);
void enemies_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
uint32_t enemies_borrow_read(EnemiesBorrower borrower,uint16_t bank,uint16_t position,unsigned width);
void enemies_borrow_write(EnemiesBorrower borrower,uint16_t bank,uint16_t position,unsigned width,uint32_t value);
#endif
