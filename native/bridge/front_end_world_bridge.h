#ifndef NATIVE_FRONTEND_WORLD_BRIDGE_H
#define NATIVE_FRONTEND_WORLD_BRIDGE_H
#include "ugh.h"
#include "../front_end_world.h"
typedef enum FrontEndBorrower {
 FRONTEND_BORROW_MENUS,FRONTEND_BORROW_SCORES,FRONTEND_BORROW_SESSION,
 FRONTEND_BORROW_TEXT,FRONTEND_BORROW_FILES,FRONTEND_BORROW_WINDOW,FRONTEND_BORROW_COUNT
} FrontEndBorrower;
void frontend_cold_import(uint8_t *memory);
void frontend_require_seal(const uint8_t *memory);
unsigned frontend_owned_bytes(void);
int frontend_is_owned(uint32_t address);
int frontend_shared_read(uint32_t address,uint8_t *value);
int frontend_shared_write(uint32_t address,uint8_t value);
void frontend_serialize(uint8_t *output);
uint32_t frontend_check_serialization(const uint8_t *output);
uint8_t frontend_borrowed_byte(const uint8_t *window,uint32_t index);
void frontend_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
uint32_t frontend_borrow_read(FrontEndBorrower borrower,uint16_t bank,uint16_t position,unsigned width);
void frontend_borrow_write(FrontEndBorrower borrower,uint16_t bank,uint16_t position,unsigned width,uint32_t value);
#endif
