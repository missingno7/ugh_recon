#ifndef NATIVE_RANDOM_WORLD_BRIDGE_H
#define NATIVE_RANDOM_WORLD_BRIDGE_H
#include "ugh.h"
#include "../random_world.h"
#include <stdint.h>
typedef enum RandomBorrower {RNG_BORROW_GENERATOR,RNG_BORROW_COUNT} RandomBorrower;
int rng_is_owned(uint32_t address);
int rng_shared_read(uint32_t address,uint8_t *value);
int rng_shared_write(uint32_t address,uint8_t value);
unsigned rng_owned_bytes(void);
void rng_cold_import(uint8_t *memory);
void rng_require_seal(const uint8_t *memory);
void rng_serialize(uint8_t *output);
uint32_t rng_check_serialization(const uint8_t *output);
uint8_t rng_borrowed_byte(const uint8_t *window,uint32_t index);
void rng_borrowed_store(uint8_t *window,uint32_t index,uint8_t value);
uint32_t rng_borrow_read(RandomBorrower who,uint16_t bank,uint16_t offset,unsigned width);
void rng_borrow_write(RandomBorrower who,uint16_t bank,uint16_t offset,unsigned width,uint32_t value);
#endif
