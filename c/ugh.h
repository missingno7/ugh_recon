/* Portable C11 core. Game state lives only in ugh_mem at original addresses. */
#ifndef UGH_H
#define UGH_H
#include <stdint.h>
#include "ugh_sym.h"
#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif
#define UGH_MEM_SIZE 0x110000u
extern uint8_t ugh_mem[UGH_MEM_SIZE];
typedef struct Regs {
    uint16_t ax, bx, cx, dx, si, di, bp, sp, cs, ds, es, ss, ip, flags;
} Regs;
enum { CF=1, PF=4, AF=16, ZF=64, SF=128, IF=512, DF=1024, OF=2048 };
enum { UGH_OK=0, UGH_UNSUPPORTED=1, UGH_BUDGET=2, UGH_BAD_CALLBACK=3 };
#define G(n) UGH_O_GAME_##n
#define S(n) UGH_O_SOUND_##n
#define D(n) UGH_O_DGROUP_##n
#define T(n) UGH_O_TIMER_##n
#define GAME_SEG UGH_SEG_GAME
#define SOUND_SEG UGH_SEG_SOUND
#define DATA_SEG UGH_SEG_DGROUP
#define TIMER_SEG UGH_SEG_TIMER
static inline uint32_t lin(uint16_t s, uint16_t o) { return (uint32_t)s*16u + o; }
/* Platform aperture access is physical, so aliases such as 9FFF:0010 work too. */
EXPORT uint8_t ugh_read(uint32_t address);
EXPORT void ugh_write(uint32_t address, uint8_t value);
static inline uint8_t rd8(uint16_t s, uint16_t o) { return ugh_read(lin(s,o)); }
static inline uint16_t rd16(uint16_t s, uint16_t o) {
    return (uint16_t)(rd8(s,o) | (uint16_t)rd8(s,(uint16_t)(o+1))*256u);
}
static inline uint32_t rd32(uint16_t s, uint16_t o) {
    return rd16(s,o) | (uint32_t)rd16(s,(uint16_t)(o+2))*65536u;
}
static inline void wr8(uint16_t s, uint16_t o, uint8_t v) { ugh_write(lin(s,o),v); }
static inline void wr16(uint16_t s, uint16_t o, uint16_t v) {
    wr8(s,o,(uint8_t)v); wr8(s,(uint16_t)(o+1),(uint8_t)(v>>8));
}
static inline void wr32(uint16_t s, uint16_t o, uint32_t v) {
    wr16(s,o,(uint16_t)v); wr16(s,(uint16_t)(o+2),(uint16_t)(v>>16));
}
static inline void flag(Regs *r, uint16_t bit, int on) {
    r->flags = (uint16_t)((r->flags & ~bit) | (on ? bit : 0));
}
static inline void szp(Regs *r, uint16_t v, unsigned width) {
    uint8_t b=(uint8_t)v; b^=b>>4; b^=b>>2; b^=b>>1;
    flag(r,PF,!(b&1)); flag(r,ZF,!(v & (width==8 ? 255u : 65535u)));
    flag(r,SF,v & (width==8 ? 128u : 32768u));
}
static inline uint16_t logic(Regs *r, uint16_t v, unsigned width) {
    flag(r,CF,0); flag(r,OF,0); szp(r,v,width); return v;
}
static inline uint16_t sub16(Regs *r, uint16_t a, uint16_t b, unsigned borrow) {
    uint32_t rhs=(uint32_t)b+borrow; uint16_t v=(uint16_t)(a-rhs);
    flag(r,CF,(uint32_t)a<rhs); flag(r,OF,((a^b)&(a^v)&0x8000u)!=0);
    flag(r,AF,((a^b^v)&16u)!=0); szp(r,v,16); return v;
}
static inline uint16_t add16(Regs *r, uint16_t a, uint16_t b, unsigned carry) {
    uint32_t sum=(uint32_t)a+b+carry; uint16_t v=(uint16_t)sum;
    flag(r,CF,sum>65535u); flag(r,OF,((~(a^b))&(a^v)&0x8000u)!=0);
    flag(r,AF,((a^b^v)&16u)!=0); szp(r,v,16); return v;
}
static inline uint16_t dec16(Regs *r, uint16_t a) {
    uint16_t cf=r->flags&CF, v=sub16(r,a,1,0); flag(r,CF,cf); return v;
}
static inline int step(const Regs *r) { return r->flags&DF ? -1 : 1; }
static inline void set_al(Regs *r,uint8_t x) { r->ax=(uint16_t)((r->ax&0xff00u)|x); }
static inline void set_ah(Regs *r,uint8_t x) { r->ax=(uint16_t)((r->ax&255u)|(uint16_t)x*256u); }
/* Far cdecl argument byte offset, relative to the incoming SP after CALL FAR. */
static inline uint16_t arg16(const Regs *r, uint16_t n) { return rd16(r->ss,(uint16_t)(r->sp+4+n)); }
/* Every indirect target is resolved by its original far address; unknown is an error. */
int ugh_dispatch(uint16_t segment, uint16_t offset, Regs *r);
EXPORT int c_ClearSoundState(Regs *r);
#endif
