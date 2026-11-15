#ifndef NATIVE_PLAYER_BORROW_H
#define NATIVE_PLAYER_BORROW_H
#ifdef UGH_NATIVE_PLAYER
#include "player_world_bridge.h"
#ifndef PLAYER_BORROWER
#error Each player borrower must name its role
#endif
#define player_read8(b,o) ((uint8_t)player_borrow_read(PLAYER_BORROWER,b,o,1))
#define player_read16(b,o) ((uint16_t)player_borrow_read(PLAYER_BORROWER,b,o,2))
#define player_read32(b,o) player_borrow_read(PLAYER_BORROWER,b,o,4)
#define player_write8(b,o,v) player_borrow_write(PLAYER_BORROWER,b,o,1,(uint8_t)(v))
#define player_write16(b,o,v) player_borrow_write(PLAYER_BORROWER,b,o,2,(uint16_t)(v))
#define player_write32(b,o,v) player_borrow_write(PLAYER_BORROWER,b,o,4,(uint32_t)(v))
#else
#define player_read8 rd8
#define player_read16 rd16
#define player_read32 rd32
#define player_write8 wr8
#define player_write16 wr16
#define player_write32 wr32
#endif
#endif
