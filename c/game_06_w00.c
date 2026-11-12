#include "platform.h"

/* SHARED-REQUEST: declare this accepted pilot adapter in c/ugh.h. */
EXPORT int c_UnpackIceStream(Regs *r);

/* SHARED-REQUEST: rd16/wr16 wrap their second byte at FFFFh, but an x86 word
 * operand spans consecutive physical bytes (the rebuilt oracle confirms this).
 * Offset calculations still wrap before each operand. Keep this workaround local
 * until the supervisor fixes the shared helpers and reruns the pilot suites. */
static uint16_t palette_read_word(uint16_t s,uint16_t o) {
    uint32_t a=lin(s,o);
    return (uint16_t)(ugh_read(a)|(uint16_t)ugh_read(a+1)*256u);
}
static void palette_write_word(uint16_t s,uint16_t o,uint16_t value) {
    uint32_t a=lin(s,o);
    ugh_write(a,(uint8_t)value);
    ugh_write(a+1,(uint8_t)(value>>8));
}

/* Near entry, no stack arguments. DS locates the two far-pointer cells; it is
 * restored. ES becomes the destination segment. AX is the final loaded word,
 * CX=0, SI/DI move by +/-384; BX/DX/BP and all flags are preserved.
 * Each iteration reads first, writes DI+180h, then writes DI. This order matters
 * for aliased palettes. DF is consumed, never cleared; all offsets wrap at 16 bits.
 * No callees or hardware effects. The second source half is never read. */
/* TRANSLATES GAME:DuplicateSourcePaletteHalves */
EXPORT int c_DuplicateSourcePaletteHalves(Regs *r) {
    uint16_t saved_ds=r->ds;
    r->di=rd16(r->ds,D(BasePalettePointer));
    r->es=rd16(r->ds,(uint16_t)(D(BasePalettePointer)+2));
    r->si=rd16(r->ds,D(PaletteSourcePointer));
    r->ds=rd16(r->ds,(uint16_t)(D(PaletteSourcePointer)+2));
    r->cx=0xc0;
    do {
        r->ax=palette_read_word(r->ds,r->si);
        r->si=(uint16_t)(r->si+2*step(r));
        palette_write_word(r->es,(uint16_t)(r->di+0x180),r->ax);
        palette_write_word(r->es,r->di,r->ax);
        r->di=(uint16_t)(r->di+2*step(r));
        r->cx=(uint16_t)(r->cx-1);
    } while(r->cx);
    r->ds=saved_ds;
    return UGH_OK;
}

/* Near entry, no stack arguments. DS:SI is the packed stream; ES is replaced
 * by the original zero-workspace segment, DI by zero, then control falls through
 * to the accepted ICE pilot. AX/BX/CX/DX/BP/DS remain unchanged, SI/DI are decoder
 * outputs, DF=0. Bad first/second magic advances SI by 2/4 and leaves DI=0.
 * Other arithmetic flags are scratch; no platform calls. */
/* TRANSLATES GAME:UnpackIceToScratch */
EXPORT int c_UnpackIceToScratch(Regs *r) {
    r->es=UGH_S_ZERO_IceDecodeWorkspace;
    r->di=logic(r,0,16); /* XOR DI,DI precedes the decoder's saved registers. */
    return c_UnpackIceStream(r);
}

/* INT 24h entry / IRET, no arguments: AL=3, all other registers preserved.
 * STI sets live IF; the harness performs IRET and restores the saved FLAGS.
 * No DOS service is called by this handler itself. */
/* TRANSLATES GAME:FailDosCriticalError */
EXPORT int c_FailDosCriticalError(Regs *r) {
    flag(r,IF,1);
    set_al(r,3);
    return UGH_OK;
}

/* Near entry, no arguments. AX is an unsigned exclusive bound, including zero.
 * Four state words are read/written through incoming CS, never DS. The carry
 * from each ADD/ADC feeds the next, including the final update of state0.
 * AX=high word of new state0*bound; BX/CX/DX/SI/DI/BP and segments preserved.
 * MUL defines CF/OF iff its high word is nonzero; other arithmetic flags are
 * undefined. No callees or device effects. Bound zero still advances the state. */
/* TRANSLATES GAME:NextRandomBelowAx */
EXPORT int c_NextRandomBelowAx(Regs *r) {
    uint16_t bound=r->ax;
    uint16_t a=add16(r,bound,rd16(r->cs,G(RandomStateWord0)),0);
    uint16_t b=add16(r,rd16(r->cs,G(RandomStateWord1)),a,r->flags&CF);
    wr16(r->cs,G(RandomStateWord1),b);
    uint16_t c=add16(r,rd16(r->cs,G(RandomStateWord2)),b,r->flags&CF);
    wr16(r->cs,G(RandomStateWord2),c);
    uint16_t d=add16(r,rd16(r->cs,G(RandomStateWord3)),c,r->flags&CF);
    wr16(r->cs,G(RandomStateWord3),d);
    a=add16(r,a,d,r->flags&CF);
    wr16(r->cs,G(RandomStateWord0),a);
    uint32_t product=(uint32_t)a*bound;
    r->ax=(uint16_t)(product>>16);
    flag(r,CF,r->ax!=0);
    flag(r,OF,r->ax!=0);
    return UGH_OK;
}

/* Near entry, no arguments: write SEQ index 2 then map mask 0Fh, in that order.
 * AL=0Fh (AH preserved), DX=03C5h. Other registers and CF/IF/DF preserved;
 * PF/AF/ZF/SF/OF come from INC 03C4h. No RAM writes or callees. */
/* TRANSLATES GAME:EnableAllVgaWritePlanes */
EXPORT int c_EnableAllVgaWritePlanes(Regs *r) {
    r->dx=0x3c4;
    set_al(r,2);
    platform_out(r->dx,1,(uint8_t)r->ax);
    uint16_t cf=r->flags&CF;
    r->dx=add16(r,r->dx,1,0);
    flag(r,CF,cf);
    set_al(r,15);
    platform_out(r->dx,1,(uint8_t)r->ax);
    return UGH_OK;
}
