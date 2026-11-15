#ifndef NATIVE_ENEMIES_BORROW_H
#define NATIVE_ENEMIES_BORROW_H
#ifdef UGH_NATIVE_ENEMIES
#include "enemy_world_bridge.h"
#ifndef ENEMIES_BORROWER
#error Each enemies borrower must name its role
#endif
#define enemies_read8(b,o) ((uint8_t)enemies_borrow_read(ENEMIES_BORROWER,b,o,1))
#define enemies_read16(b,o) ((uint16_t)enemies_borrow_read(ENEMIES_BORROWER,b,o,2))
#define enemies_read32(b,o) enemies_borrow_read(ENEMIES_BORROWER,b,o,4)
#define enemies_write8(b,o,v) enemies_borrow_write(ENEMIES_BORROWER,b,o,1,(uint8_t)(v))
#define enemies_write16(b,o,v) enemies_borrow_write(ENEMIES_BORROWER,b,o,2,(uint16_t)(v))
#define enemies_write32(b,o,v) enemies_borrow_write(ENEMIES_BORROWER,b,o,4,(uint32_t)(v))
#else
#define enemies_read8 rd8
#define enemies_read16 rd16
#define enemies_read32 rd32
#define enemies_write8 wr8
#define enemies_write16 wr16
#define enemies_write32 wr32
#endif
#endif
