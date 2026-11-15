#ifndef NATIVE_ACTORS_WORLD_BRIDGE_H
#define NATIVE_ACTORS_WORLD_BRIDGE_H
#include "ugh.h"
#include "../actor_world.h"
typedef enum ActorsBorrower {
 ACTORS_BORROW_SESSION,ACTORS_BORROW_WATER,ACTORS_BORROW_MENUS,ACTORS_BORROW_SCORES,
 ACTORS_BORROW_INPUT,ACTORS_BORROW_HUD,ACTORS_BORROW_PHYSICS,ACTORS_BORROW_ACTORS,
 ACTORS_BORROW_ITEMS,ACTORS_BORROW_DEMO,ACTORS_BORROW_RENDER,ACTORS_BORROW_RESOURCES,
 ACTORS_BORROW_WINDOW,ACTORS_BORROW_COUNT
} ActorsBorrower;
void actors_cold_import(uint8_t *memory);
void actors_require_seal(const uint8_t *memory);
unsigned actors_owned_bytes(void);
int actors_is_owned(uint32_t address);
int actors_shared_read(uint32_t address,uint8_t *value);
int actors_shared_write(uint32_t address,uint8_t value);
void actors_serialize(uint8_t *output);
uint32_t actors_check_serialization(const uint8_t *output);
uint8_t actors_borrowed_byte(const uint8_t *window,uint32_t index);
void actors_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
uint32_t actors_borrow_read(ActorsBorrower borrower,uint16_t bank,uint16_t position,unsigned width);
void actors_borrow_write(ActorsBorrower borrower,uint16_t bank,uint16_t position,unsigned width,uint32_t value);
#endif
