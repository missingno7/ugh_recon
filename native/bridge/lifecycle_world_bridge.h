#ifndef NATIVE_LIFECYCLE_WORLD_BRIDGE_H
#define NATIVE_LIFECYCLE_WORLD_BRIDGE_H
#include "ugh.h"
#include "../lifecycle_world.h"
typedef enum LifecycleBorrower { LIFECYCLE_BORROW_STARTUP, LIFECYCLE_BORROW_TERMINAL,
    LIFECYCLE_BORROW_WINDOW, LIFECYCLE_BORROW_COUNT } LifecycleBorrower;
int lifecycle_is_owned(uint32_t address);
int lifecycle_shared_read(uint32_t address,uint8_t *value);
int lifecycle_shared_write(uint32_t address,uint8_t value);
unsigned lifecycle_owned_bytes(void);
void lifecycle_cold_import(uint8_t *memory);
void lifecycle_require_seal(const uint8_t *memory);
void lifecycle_serialize(uint8_t *output);
uint32_t lifecycle_check_serialization(const uint8_t *output);
uint8_t lifecycle_borrowed_byte(const uint8_t *window,uint32_t index);
void lifecycle_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
uint8_t lifecycle_borrow_read(LifecycleBorrower borrower,uint16_t bank,uint16_t position);
void lifecycle_borrow_write(LifecycleBorrower borrower,uint16_t bank,uint16_t position,uint8_t value);
int lifecycle_adapter_run(Regs *registers,LifecycleTask task);
int lifecycle_adapter_terminal(Regs *registers);
#endif
