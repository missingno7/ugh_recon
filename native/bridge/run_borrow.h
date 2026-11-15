#ifndef NATIVE_RUN_BORROW_H
#define NATIVE_RUN_BORROW_H
#ifdef UGH_NATIVE_RUN
#include "run_world_bridge.h"
#ifndef RUN_BORROWER
#error Each run-state borrower must name its role
#endif
#define run_read8(bank,position) ((uint8_t)run_borrow_read(RUN_BORROWER,bank,position,1))
#define run_read16(bank,position) ((uint16_t)run_borrow_read(RUN_BORROWER,bank,position,2))
#define run_read32(bank,position) run_borrow_read(RUN_BORROWER,bank,position,4)
#define run_write8(bank,position,value) run_borrow_write(RUN_BORROWER,bank,position,1,(uint8_t)(value))
#define run_write16(bank,position,value) run_borrow_write(RUN_BORROWER,bank,position,2,(uint16_t)(value))
#define run_write32(bank,position,value) run_borrow_write(RUN_BORROWER,bank,position,4,(uint32_t)(value))
#else
#define run_read8 rd8
#define run_read16 rd16
#define run_read32 rd32
#define run_write8 wr8
#define run_write16 wr16
#define run_write32 wr32
#endif
#endif
