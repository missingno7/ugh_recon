#ifndef NATIVE_ACTORS_BORROW_H
#define NATIVE_ACTORS_BORROW_H
#ifdef UGH_NATIVE_ACTORS
#include "actor_world_bridge.h"
#ifndef ACTORS_BORROWER
#error Each actors borrower must name its role
#endif
#define actors_read8(b,o) ((uint8_t)actors_borrow_read(ACTORS_BORROWER,b,o,1))
#define actors_read16(b,o) ((uint16_t)actors_borrow_read(ACTORS_BORROWER,b,o,2))
#define actors_read32(b,o) actors_borrow_read(ACTORS_BORROWER,b,o,4)
#define actors_write8(b,o,v) actors_borrow_write(ACTORS_BORROWER,b,o,1,(uint8_t)(v))
#define actors_write16(b,o,v) actors_borrow_write(ACTORS_BORROWER,b,o,2,(uint16_t)(v))
#define actors_write32(b,o,v) actors_borrow_write(ACTORS_BORROWER,b,o,4,(uint32_t)(v))
#else
#define actors_read8 rd8
#define actors_read16 rd16
#define actors_read32 rd32
#define actors_write8 wr8
#define actors_write16 wr16
#define actors_write32 wr32
#endif
#endif
