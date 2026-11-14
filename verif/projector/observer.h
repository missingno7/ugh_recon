#ifndef VERIF_PROJECTOR_OBSERVER_H
#define VERIF_PROJECTOR_OBSERVER_H
#include <stdint.h>
struct Regs;
void pr_import(void);
void pr_verify_baseline(void);
void pr_write(uint32_t address,uint8_t value);
void pr_pointer_write(const uint8_t *destination,uint8_t value);
void pr_publish(const uint8_t *destination,unsigned count);
void pr_vga_read(uint32_t address);
void pr_services(unsigned groups);
void pr_event(unsigned kind,uint16_t port,unsigned width,uint32_t value);
void pr_boundary(struct Regs *regs,const char *terminal);
#endif
