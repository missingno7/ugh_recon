#ifndef NATIVE_RANDOM_BORROW_H
#define NATIVE_RANDOM_BORROW_H
#ifdef UGH_NATIVE_RANDOM
#include "random_world_bridge.h"
#define rng_read16(bank,offset) ((uint16_t)rng_borrow_read(RNG_BORROW_GENERATOR,bank,offset,2))
#define rng_write16(bank,offset,value) rng_borrow_write(RNG_BORROW_GENERATOR,bank,offset,2,(uint16_t)(value))
#define rng_write8(bank,offset,value) rng_borrow_write(RNG_BORROW_GENERATOR,bank,offset,1,(uint8_t)(value))
#else
#define rng_read16 rd16
#define rng_write16 wr16
#define rng_write8 wr8
#endif
#endif
