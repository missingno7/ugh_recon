#ifndef NATIVE_ITEMSTATE_BORROW_H
#define NATIVE_ITEMSTATE_BORROW_H
#ifdef UGH_NATIVE_ITEMS
#include "item_world_bridge.h"
#ifndef ITEMSTATE_BORROWER
#error Each itemstate borrower must name its role
#endif
#define itemstate_read8(b,o) ((uint8_t)itemstate_borrow_read(ITEMSTATE_BORROWER,b,o,1))
#define itemstate_read16(b,o) ((uint16_t)itemstate_borrow_read(ITEMSTATE_BORROWER,b,o,2))
#define itemstate_read32(b,o) itemstate_borrow_read(ITEMSTATE_BORROWER,b,o,4)
#define itemstate_write8(b,o,v) itemstate_borrow_write(ITEMSTATE_BORROWER,b,o,1,(uint8_t)(v))
#define itemstate_write16(b,o,v) itemstate_borrow_write(ITEMSTATE_BORROWER,b,o,2,(uint16_t)(v))
#define itemstate_write32(b,o,v) itemstate_borrow_write(ITEMSTATE_BORROWER,b,o,4,(uint32_t)(v))
#else
#define itemstate_read8 rd8
#define itemstate_read16 rd16
#define itemstate_read32 rd32
#define itemstate_write8 wr8
#define itemstate_write16 wr16
#define itemstate_write32 wr32
#endif
#endif
