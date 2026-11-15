#ifndef NATIVE_PLAYER_WORLD_BRIDGE_H
#define NATIVE_PLAYER_WORLD_BRIDGE_H
#include "ugh.h"
#include "../player_world.h"
typedef enum PlayerBorrower {
 PLAYER_BORROW_SESSION,PLAYER_BORROW_WATER,PLAYER_BORROW_MENUS,PLAYER_BORROW_SCORES,
 PLAYER_BORROW_INPUT,PLAYER_BORROW_HUD,PLAYER_BORROW_PHYSICS,PLAYER_BORROW_ACTORS,
 PLAYER_BORROW_ITEMS,PLAYER_BORROW_DEMO,PLAYER_BORROW_RENDER,PLAYER_BORROW_RESOURCES,
 PLAYER_BORROW_WINDOW,PLAYER_BORROW_COUNT
} PlayerBorrower;
void player_cold_import(uint8_t *memory);
void player_require_seal(const uint8_t *memory);
unsigned player_owned_bytes(void);
int player_is_owned(uint32_t address);
int player_shared_read(uint32_t address,uint8_t *value);
int player_shared_write(uint32_t address,uint8_t value);
void player_serialize(uint8_t *output);
uint32_t player_check_serialization(const uint8_t *output);
uint8_t player_borrowed_byte(const uint8_t *window,uint32_t index);
void player_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
uint32_t player_borrow_read(PlayerBorrower borrower,uint16_t bank,uint16_t position,unsigned width);
void player_borrow_write(PlayerBorrower borrower,uint16_t bank,uint16_t position,unsigned width,uint32_t value);
#endif
