#ifndef ICE_CBMC_UGH_H
#define ICE_CBMC_UGH_H
#include <stdint.h>
void __CPROVER_assume(_Bool);
void __CPROVER_assert(_Bool,const char *);
#if COVER_RUN
#define REACHABLE(condition,description) __CPROVER_assert(!(condition),description)
#else
#define REACHABLE(condition,description) ((void)0)
#endif
typedef struct Regs {
    uint16_t ax,bx,cx,dx,si,di,bp,sp,cs,ds,es,ss,ip,flags;
} Regs;
#define EXPORT
enum { DF=1024, UGH_OK=0, UGH_BUDGET=2 };
#define GAME_SEG 3
#define G(name) ICE_O_##name
static void flag(Regs *r,uint16_t bit,int on) {
    r->flags=(uint16_t)((r->flags & ~bit) | (on ? bit : 0));
}
static uint8_t rd8(uint16_t segment,uint16_t offset);
static uint16_t rd16(uint16_t segment,uint16_t offset);
static void wr8(uint16_t segment,uint16_t offset,uint8_t value);
#endif
