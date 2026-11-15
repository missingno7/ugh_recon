#ifndef S7_SHADOW_H
#define S7_SHADOW_H
#include "platform.h"
#include "test/backend.h"
extern GSTestBackend s7_backend;
extern GameServices s7_services;
void s7_begin(void);
void s7_check(void);
void s7_finish(void);
void s7_irq(unsigned,uint32_t,int);
void s7_cut(unsigned);
void s7_flush(uint16_t);
void s7_effects(unsigned);
uint8_t s7_model_read(uint32_t);
void s7_model_write(uint32_t,uint8_t);
void s7_model_out(uint16_t,unsigned,uint32_t);
uint32_t s7_model_in(uint16_t,unsigned);
int s7_model_interrupt(uint8_t,Regs *);
#endif
