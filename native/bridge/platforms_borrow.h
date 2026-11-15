#ifndef NATIVE_PLATFORMS_BORROW_H
#define NATIVE_PLATFORMS_BORROW_H
#ifdef UGH_NATIVE_PLAYER
#include "platform_world_bridge.h"
#ifndef PLATFORMS_BORROWER
#error Each platforms borrower must name its role
#endif
#define platforms_read8(b,o) ((uint8_t)platforms_borrow_read(PLATFORMS_BORROWER,b,o,1))
#define platforms_read16(b,o) ((uint16_t)platforms_borrow_read(PLATFORMS_BORROWER,b,o,2))
#define platforms_read32(b,o) platforms_borrow_read(PLATFORMS_BORROWER,b,o,4)
#define platforms_write8(b,o,v) platforms_borrow_write(PLATFORMS_BORROWER,b,o,1,(uint8_t)(v))
#define platforms_write16(b,o,v) platforms_borrow_write(PLATFORMS_BORROWER,b,o,2,(uint16_t)(v))
#define platforms_write32(b,o,v) platforms_borrow_write(PLATFORMS_BORROWER,b,o,4,(uint32_t)(v))
#else
#define platforms_read8 rd8
#define platforms_read16 rd16
#define platforms_read32 rd32
#define platforms_write8 wr8
#define platforms_write16 wr16
#define platforms_write32 wr32
#endif
#endif
