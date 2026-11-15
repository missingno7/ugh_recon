#ifndef NATIVE_SESSIONSTATE_WORLD_BRIDGE_H
#define NATIVE_SESSIONSTATE_WORLD_BRIDGE_H
#include "ugh.h"
#include "../session_world.h"
typedef enum SessionstateBorrower {
 SESSIONSTATE_BORROW_SESSION,SESSIONSTATE_BORROW_WATER,SESSIONSTATE_BORROW_MENUS,SESSIONSTATE_BORROW_SCORES,
 SESSIONSTATE_BORROW_INPUT,SESSIONSTATE_BORROW_HUD,SESSIONSTATE_BORROW_PHYSICS,SESSIONSTATE_BORROW_ACTORS,
 SESSIONSTATE_BORROW_ITEMS,SESSIONSTATE_BORROW_DEMO,SESSIONSTATE_BORROW_RENDER,SESSIONSTATE_BORROW_RESOURCES,
 SESSIONSTATE_BORROW_WINDOW,SESSIONSTATE_BORROW_COUNT
} SessionstateBorrower;
void sessionstate_cold_import(uint8_t *memory);
void sessionstate_require_seal(const uint8_t *memory);
unsigned sessionstate_owned_bytes(void);
int sessionstate_is_owned(uint32_t address);
int sessionstate_shared_read(uint32_t address,uint8_t *value);
int sessionstate_shared_write(uint32_t address,uint8_t value);
void sessionstate_serialize(uint8_t *output);
uint32_t sessionstate_check_serialization(const uint8_t *output);
uint8_t sessionstate_borrowed_byte(const uint8_t *window,uint32_t index);
void sessionstate_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
uint32_t sessionstate_borrow_read(SessionstateBorrower borrower,uint16_t bank,uint16_t position,unsigned width);
void sessionstate_borrow_write(SessionstateBorrower borrower,uint16_t bank,uint16_t position,unsigned width,uint32_t value);
#endif
