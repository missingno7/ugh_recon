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
/* Effective offsets wrap before an operand; bytes within it are contiguous. */
static inline uint16_t rd16_linear(uint16_t s,uint16_t o) {
    uint32_t a=lin(s,o); uint16_t low=ugh_read(a);
    return (uint16_t)(low | (uint16_t)ugh_read(a+1)*256u);
}
static inline uint16_t rd16(uint16_t s,uint16_t o) { return rd16_linear(s,o); }
static inline uint32_t rd32(uint16_t s,uint16_t o) {
    uint32_t a=lin(s,o),v=0;
    for(unsigned i=0;i<4;i++) v|=(uint32_t)ugh_read(a+i)<<(8*i);
    return v;
}
static inline void wr8(uint16_t s,uint16_t o,uint8_t v) { ugh_write(lin(s,o),v); }
static inline void wr16(uint16_t s,uint16_t o,uint16_t v) {
    uint32_t a=lin(s,o); ugh_write(a,(uint8_t)v); ugh_write(a+1,(uint8_t)(v>>8));
}
static inline void wr32(uint16_t s,uint16_t o,uint32_t v) {
    uint32_t a=lin(s,o);
    for(unsigned i=0;i<4;i++) ugh_write(a+i,(uint8_t)(v>>(8*i)));
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
EXPORT int ugh_dispatch(uint16_t segment, uint16_t offset, Regs *r);
typedef int (*UghAdapter)(Regs *r);
UghAdapter ugh_resolve(uint16_t segment,uint16_t offset);
int ugh_call_near(uint16_t target,uint16_t return_ip,Regs *r);
EXPORT int ugh_dispatch_interrupt(uint16_t segment,uint16_t offset,Regs *r);
EXPORT uint16_t ugh_load16(uint16_t segment,uint16_t offset);
EXPORT uint32_t ugh_load32(uint16_t segment,uint16_t offset);
EXPORT void ugh_store16(uint16_t segment,uint16_t offset,uint16_t value);
EXPORT void ugh_store32(uint16_t segment,uint16_t offset,uint32_t value);
#include "ugh_adapters.h"
/* Compiler-owned switch positions measured within the rebuilt C function. */
#define UGH_O_C_DurationSwitchTable (UGH_O_C_GetMusicTrackDuration + 0x0107u)
#define UGH_O_C_DurationLongWait (UGH_O_C_GetMusicTrackDuration + 0x0092u)
#define UGH_O_C_DurationFrequency (UGH_O_C_GetMusicTrackDuration + 0x00AEu)
#define UGH_O_C_DurationKeyOff (UGH_O_C_GetMusicTrackDuration + 0x00B4u)
#define UGH_O_C_DurationVolume (UGH_O_C_GetMusicTrackDuration + 0x00B6u)
#define UGH_O_C_DurationInstrument (UGH_O_C_GetMusicTrackDuration + 0x00B8u)
#define UGH_O_C_DurationTimer (UGH_O_C_GetMusicTrackDuration + 0x00BEu)
#define UGH_O_C_DurationExtension (UGH_O_C_GetMusicTrackDuration + 0x00C0u)
#define UGH_O_C_DurationDefault (UGH_O_C_GetMusicTrackDuration + 0x00D0u)
#endif
