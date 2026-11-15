#ifndef NATIVE_SESSIONSTATE_BORROW_H
#define NATIVE_SESSIONSTATE_BORROW_H
#ifdef UGH_NATIVE_SESSION
#include "session_world_bridge.h"
#ifndef SESSIONSTATE_BORROWER
#error Each sessionstate borrower must name its role
#endif
#define sessionstate_read8(b,o) ((uint8_t)sessionstate_borrow_read(SESSIONSTATE_BORROWER,b,o,1))
#define sessionstate_read16(b,o) ((uint16_t)sessionstate_borrow_read(SESSIONSTATE_BORROWER,b,o,2))
#define sessionstate_read32(b,o) sessionstate_borrow_read(SESSIONSTATE_BORROWER,b,o,4)
#define sessionstate_write8(b,o,v) sessionstate_borrow_write(SESSIONSTATE_BORROWER,b,o,1,(uint8_t)(v))
#define sessionstate_write16(b,o,v) sessionstate_borrow_write(SESSIONSTATE_BORROWER,b,o,2,(uint16_t)(v))
#define sessionstate_write32(b,o,v) sessionstate_borrow_write(SESSIONSTATE_BORROWER,b,o,4,(uint32_t)(v))
#else
#define sessionstate_read8 rd8
#define sessionstate_read16 rd16
#define sessionstate_read32 rd32
#define sessionstate_write8 wr8
#define sessionstate_write16 wr16
#define sessionstate_write32 wr32
#endif
#endif
