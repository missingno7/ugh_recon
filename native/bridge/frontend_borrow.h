#ifndef NATIVE_FRONTEND_BORROW_H
#define NATIVE_FRONTEND_BORROW_H
#ifdef UGH_NATIVE_FRONT_END
#include "front_end_world_bridge.h"
#ifndef FRONTEND_BORROWER
#error Each frontend borrower must name its role
#endif
#define frontend_read8(b,o) ((uint8_t)frontend_borrow_read(FRONTEND_BORROWER,b,o,1))
#define frontend_read16(b,o) ((uint16_t)frontend_borrow_read(FRONTEND_BORROWER,b,o,2))
#define frontend_read32(b,o) frontend_borrow_read(FRONTEND_BORROWER,b,o,4)
#define frontend_write8(b,o,v) frontend_borrow_write(FRONTEND_BORROWER,b,o,1,(uint8_t)(v))
#define frontend_write16(b,o,v) frontend_borrow_write(FRONTEND_BORROWER,b,o,2,(uint16_t)(v))
#define frontend_write32(b,o,v) frontend_borrow_write(FRONTEND_BORROWER,b,o,4,(uint32_t)(v))
#else
#define frontend_read8 rd8
#define frontend_read16 rd16
#define frontend_read32 rd32
#define frontend_write8 wr8
#define frontend_write16 wr16
#define frontend_write32 wr32
#endif
#endif
