#ifndef NATIVE_RUN_WORLD_BRIDGE_H
#define NATIVE_RUN_WORLD_BRIDGE_H
#include "ugh.h"
#include "../run_world.h"
typedef enum RunBorrower {
 RUN_BORROW_SESSION,RUN_BORROW_WATER,RUN_BORROW_MENUS,RUN_BORROW_SCORES,
 RUN_BORROW_INPUT,RUN_BORROW_HUD,RUN_BORROW_PHYSICS,RUN_BORROW_ACTORS,
 RUN_BORROW_ITEMS,RUN_BORROW_DEMO,RUN_BORROW_RENDER,RUN_BORROW_RESOURCES,
 RUN_BORROW_WINDOW,RUN_BORROW_COUNT
} RunBorrower;
void run_cold_import(uint8_t *memory);
void run_require_seal(const uint8_t *memory);
unsigned run_owned_bytes(void);
int run_is_owned(uint32_t address);
int run_shared_read(uint32_t address,uint8_t *value);
int run_shared_write(uint32_t address,uint8_t value);
void run_serialize(uint8_t *output);
uint32_t run_check_serialization(const uint8_t *output);
uint8_t run_borrowed_byte(const uint8_t *window,uint32_t index);
void run_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
uint32_t run_borrow_read(RunBorrower borrower,uint16_t bank,uint16_t position,unsigned width);
void run_borrow_write(RunBorrower borrower,uint16_t bank,uint16_t position,unsigned width,uint32_t value);
#endif
