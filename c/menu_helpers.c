#include "ugh.h"

/* GAME:001C..001F are each one near RET, despite their far declarations in
 * module.c and SOUND. These adapters preserve all registers, flags and memory;
 * the harness/caller owns the two-byte near return. They assign no game result.
 * In particular, they must not be used as working far resource callbacks. */
/* TRANSLATES GAME:loc_001C */
EXPORT int c_loc_001C(Regs *r) { (void)r; return UGH_OK; }
/* TRANSLATES GAME:loc_001D */
EXPORT int c_loc_001D(Regs *r) { (void)r; return UGH_OK; }
/* TRANSLATES GAME:loc_001E */
EXPORT int c_loc_001E(Regs *r) { (void)r; return UGH_OK; }
/* TRANSLATES GAME:loc_001F */
EXPORT int c_loc_001F(Regs *r) { (void)r; return UGH_OK; }

/* Both score entries: near return, CL unsigned index, DS supplies the byte
 * stride. AX/BX are the wrapped address, and arithmetic flags come from ADD
 * (overwriting MUL's flags). CX/DX/SI/DI/BP, segments, IF/DF are preserved.
 * No memory writes, calls, stack arguments or device effects. The digits are
 * 14 bytes into the same row, as established by the two original immediates. */
/* TRANSLATES GAME:GetHighScoreRow */
EXPORT int c_GetHighScoreRow(Regs *r) {
    uint16_t product=(uint16_t)((uint8_t)r->cx * rd8(r->ds,D(HighScoreRowStride)));
    r->ax=add16(r,product,D(HighScoreRows),0);
    r->bx=r->ax;
    return UGH_OK;
}

/* TRANSLATES GAME:GetHighScoreDigits */
EXPORT int c_GetHighScoreDigits(Regs *r) {
    uint16_t product=(uint16_t)((uint8_t)r->cx * rd8(r->ds,D(HighScoreRowStride)));
    r->ax=add16(r,product,(uint16_t)(D(HighScoreRows)+14),0);
    r->bx=r->ax;
    return UGH_OK;
}

/* Near return. DS:SI is a near-pointer table, BX its unsigned word index,
 * DS:DI the mutable destination. ES becomes DS. BX doubles modulo 65536;
 * SI/DI wrap independently and follow incoming DF (there is no CLD at 0652).
 * AH/CX/DX/BP, DS and IF/DF survive; AL=0 and CF=OF=SF=0, PF=ZF=1 on exit.
 * AF is undefined by AND. The NUL is consumed but never stored, and stale
 * destination bytes survive. Read each byte immediately before writing it:
 * overlap can change later reads, including the location of the terminator.
 * No callees/devices; an unterminated/corrupt stream need not return. */
/* TRANSLATES GAME:CopyIndexedMenuString */
EXPORT int c_CopyIndexedMenuString(Regs *r) {
    r->es=r->ds;
    r->bx=(uint16_t)(r->bx*2u);
    r->si=rd16_linear(r->ds,(uint16_t)(r->bx+r->si));
    for(;;) {
        uint8_t ch=rd8(r->ds,r->si);
        r->si=(uint16_t)(r->si+step(r));
        set_al(r,(uint8_t)logic(r,ch,8));
        if(!ch) return UGH_OK;
        wr8(r->es,r->di,ch);
        r->di=(uint16_t)(r->di+step(r));
    }
}
