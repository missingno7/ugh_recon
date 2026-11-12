#include "ugh.h"
#include "platform.h"

/* All entries are near-return adapters, retain SS/SP, and use the incoming DS.
 * No cdecl arguments or calls outside this package. Arithmetic helpers below
 * are inline implementation details, not independently translated entries. */
static uint16_t sar_word(uint16_t v, unsigned n) {
    /* Explicit sign fill: negative odd coordinates round toward minus infinity. */
    return (uint16_t)((v >> n) | ((v & 0x8000u) ? (0xffffu << (16-n)) : 0));
}
static uint8_t dec_byte(Regs *r, uint8_t v) {
    uint8_t out=(uint8_t)(v-1);
    flag(r,OF,v==0x80); flag(r,AF,((v^1u^out)&16u)!=0);
    szp(r,out,8); return out; /* DEC preserves CF. */
}

/* AX signed input/result; all other registers and IF/DF preserved. Writes the
 * removed quarter through DS; all six arithmetic flags are those of SUB. */
/* TRANSLATES GAME:ScaleLevelYToThreeQuarters */
EXPORT int c_ScaleLevelYToThreeQuarters(Regs *r) {
    wr16(r->ds,D(CoordinateScaleScratch),sar_word(r->ax,2));
    r->ax=sub16(r,r->ax,rd16(r->ds,D(CoordinateScaleScratch)),0);
    return UGH_OK;
}

/* AX signed input/result; writes the floor-rounded half through DS. Other
 * registers and IF/DF preserved; arithmetic flags are those of wrapped ADD. */
/* TRANSLATES GAME:ScaleLevelSpeedToThreeHalves */
EXPORT int c_ScaleLevelSpeedToThreeHalves(Regs *r) {
    wr16(r->ds,D(CoordinateScaleScratch),sar_word(r->ax,1));
    r->ax=add16(r,r->ax,rd16(r->ds,D(CoordinateScaleScratch)),0);
    return UGH_OK;
}

/* AL input (AH ignored); DS:SI destination, DS divisor byte. AX destroyed,
 * SI advances twice to the FF sentinel. All other registers, IF/DF preserved.
 * DIV arithmetic flags are not a contract. Zero divisors require INT 0, which
 * the platform cannot service: reject rather than manufacture a game result. */
/* TRANSLATES GAME:EncodeTwoDecimalDigits */
EXPORT int c_EncodeTwoDecimalDigits(Regs *r) {
    uint8_t divisor=rd8(r->ds,D(DecimalTenDivisor));
    set_ah(r,0);
    if(!divisor) return UGH_UNSUPPORTED;
    uint8_t q=(uint8_t)r->ax/divisor, rem=(uint8_t)r->ax%divisor;
    r->ax=(uint16_t)(q+(uint16_t)rem*256u);
    wr8(r->ds,r->si,(uint8_t)r->ax); r->si=(uint16_t)(r->si+1);
    set_al(r,(uint8_t)(r->ax>>8));
    wr8(r->ds,r->si,(uint8_t)r->ax); r->si=(uint16_t)(r->si+1);
    wr8(r->ds,r->si,255);
    return UGH_OK;
}

/* AX unsigned word; DS:SI destination and live divisors. DX becomes remainder
 * of division by the thousand divisor; AX destroyed, SI advances four. Other
 * registers, IF/DF preserved. Falls into the single shared two-digit body. */
/* TRANSLATES GAME:EncodeFourDecimalDigits */
EXPORT int c_EncodeFourDecimalDigits(Regs *r) {
    uint16_t divisor=rd16(r->ds,D(DecimalThousandDivisor));
    r->dx=0;
    if(!divisor) return UGH_UNSUPPORTED;
    uint16_t rem=(uint16_t)(r->ax%divisor);
    r->ax=(uint16_t)(r->ax/divisor); r->dx=rem;
    wr8(r->ds,r->si,(uint8_t)r->ax); r->si=(uint16_t)(r->si+1);
    r->ax=r->dx;
    uint8_t hundred=rd8(r->ds,D(DecimalHundredDivisor));
    if(!hundred || r->ax/hundred>255u) return UGH_UNSUPPORTED;
    rem=(uint16_t)(r->ax%hundred);
    r->ax=(uint16_t)(r->ax/hundred+rem*256u);
    wr8(r->ds,r->si,(uint8_t)r->ax); r->si=(uint16_t)(r->si+1);
    set_al(r,(uint8_t)(r->ax>>8));
    return c_EncodeTwoDecimalDigits(r);
}

/* DX:AX input (normally <=999999), DS:SI output and live divisors; CX saved,
 * SI advances six, AX/DX destroyed; other registers and IF/DF preserved.
 * @3F17 tests the signed high word, NOT 32-bit unsigned borrow. INC CL wraps.
 * Subtraction is retained even for values outside the usual six-digit range. */
/* TRANSLATES GAME:EncodeSixDecimalDigits */
EXPORT int c_EncodeSixDecimalDigits(Regs *r) {
    uint16_t cx=r->cx;
    uint8_t digit=255;
    do {
        digit=(uint8_t)(digit+1);
        uint16_t old=r->ax;
        r->ax=(uint16_t)(old-0x86a0u);
        r->dx=(uint16_t)(r->dx-1u-(old<0x86a0u));
    } while(!(r->dx&0x8000u));
    uint32_t low=(uint32_t)r->ax+0x86a0u;
    r->ax=(uint16_t)low; r->dx=(uint16_t)(r->dx+1u+(low>65535u));
    wr8(r->ds,r->si,digit); r->si=(uint16_t)(r->si+1);
    uint16_t divisor=rd16(r->ds,D(DecimalTenThousandDivisor));
    uint32_t numerator=(uint32_t)r->dx*65536u+r->ax;
    if(!divisor || numerator/divisor>65535u) return UGH_UNSUPPORTED;
    r->ax=(uint16_t)(numerator/divisor); r->dx=(uint16_t)(numerator%divisor);
    wr8(r->ds,r->si,(uint8_t)r->ax); r->si=(uint16_t)(r->si+1);
    r->ax=r->dx; r->cx=cx;
    return c_EncodeFourDecimalDigits(r);
}

/* DS fields indexed by wrapped BX (usually 0/2). Three ordered reads/writes,
 * preserving every register and flag, including in deliberately aliased state. */
/* TRANSLATES GAME:CachePlayerDrawState */
EXPORT int c_CachePlayerDrawState(Regs *r) {
    wr16(r->ds,(uint16_t)(D(PlayerCachedSpriteIds)+r->bx),
         rd16(r->ds,(uint16_t)(D(PlayerSpriteIds)+r->bx)));
    wr16(r->ds,(uint16_t)(D(PlayerCachedPixelX)+r->bx),
         rd16(r->ds,(uint16_t)(D(PlayerPixelX)+r->bx)));
    wr16(r->ds,(uint16_t)(D(PlayerCachedPixelY)+r->bx),
         rd16(r->ds,(uint16_t)(D(PlayerYPixels)+r->bx)));
    return UGH_OK;
}

/* DS water Y and particle tables; CS draw-page offset. One iteration occurs
 * even for a negative doubled count; SUB/JNS, not a bounded array loop.
 * ES=A000, AX=5B0F, BX/CX/DX/DI/BP destroyed, SI preserved. Final SUB defines
 * arithmetic flags; IF/DF preserved. Sequencer selection=2, map mask forced F.
 * @3D38 uses the 286 masked shift count, not a normalized plane number. */
/* TRANSLATES GAME:DrawRainParticles */
EXPORT int c_DrawRainParticles(Regs *r) {
    r->bx=(uint16_t)(rd16(r->ds,D(WaterYPixels))*2u);
    r->dx=0x3c4; set_al(r,2); platform_out(r->dx,1,2); r->dx++;
    r->es=0xa000; r->bp=rd16(r->cs,G(DrawPagePointer)); set_ah(r,0x5b);
    do {
        r->cx=rd16(r->ds,(uint16_t)(D(RainParticleXModuloFour)+r->bx));
        unsigned shift=r->cx&31u;
        set_al(r,shift<8 ? (uint8_t)(1u<<shift) : 0);
        platform_out(r->dx,1,(uint8_t)r->ax);
        r->di=rd16(r->ds,(uint16_t)(D(RainParticleOffsets)+r->bx));
        r->di=(uint16_t)(r->di+r->bp);
        wr8(r->es,r->di,(uint8_t)(r->ax>>8));
        r->bx=sub16(r,r->bx,2,0);
    } while(!(r->bx&0x8000u));
    set_al(r,15); platform_out(r->dx,1,15);
    return UGH_OK;
}

/* AX ID, signed BX X/CX Y, DS water Y; CS original far directory/pixel banks.
 * Preserves AX/BX/CX/DX/SI/DI/DS/ES; BP is the water threshold, decremented per
 * row only in the crossing-water path. IF/DF preserved (LODS obeys DF).
 * Writes CS scratch and VGA pixels, leaves sequencer index 2/map mask F.
 * No clipping: word address arithmetic wraps; zero byte dimensions mean 256.
 * Water threshold==height takes the unshaded path; threshold==0 shades only
 * rows AFTER the first. HUD page selection compares signed Y, then subtracts
 * 192, not PlayfieldHeight. Final arithmetic flags come from DEC CL. */
/* TRANSLATES GAME:DrawTransparentSprite */
EXPORT int c_DrawTransparentSprite(Regs *r) {
    uint16_t id=r->ax, y=r->cx;
    uint16_t dest=rd16(r->cs,G(DrawPagePointer));
    if((int16_t)y >= (int16_t)rd16(r->cs,G(PlayfieldHeight))) {
        dest=rd16(r->cs,G(FixedVgaPagePointer)); y=(uint16_t)(y-192u);
    }
    uint16_t water=(uint16_t)(rd16(r->ds,D(WaterYPixels))-y);
    wr16(r->cs,G(RendererScratchWord),water);
    dest=(uint16_t)(dest+sar_word(r->bx,2)+(uint16_t)(y*96u));
    platform_out(0x3c4,1,2);
    uint8_t plane=(uint8_t)(1u<<(r->bx&3u));
    wr16(r->cs,G(SpritePlaneStateScratch),(uint16_t)((uint16_t)plane*256u+2));
    uint16_t directory=rd16(r->cs,G(SpriteDirectoryPointer));
    uint16_t dirseg=rd16(r->cs,G(SpriteDirectoryPointer)+2);
    directory=(uint16_t)(directory+(uint16_t)(id*4u));
    uint16_t offset=rd16(dirseg,directory), dimensions=rd16(dirseg,(uint16_t)(directory+2));
    uint16_t bank=G(SpritePixels0To216Pointer);
    if(id>=217) bank=G(SpritePixels217To297Pointer);
    if(id>=298) bank=G(SpritePixels298To546Pointer);
    if(id>=547) bank=G(SpritePixels547AndUpPointer);
    uint16_t source=(uint16_t)(rd16(r->cs,bank)+offset), source_seg=rd16(r->cs,(uint16_t)(bank+2));
    uint8_t columns=(uint8_t)dimensions, height=(uint8_t)(dimensions>>8);
    r->bp=water;
    int crossing=(int16_t)water>=0 && (int16_t)water<height;
    int submerged=(int16_t)water<0;
    do {
        platform_out(0x3c5,1,plane);
        uint16_t row_dest=dest;
        uint8_t rows=height;
        if(crossing) r->bp=rd16(r->cs,G(RendererScratchWord));
        do {
            uint8_t pixel=rd8(source_seg,source); source=(uint16_t)(source+step(r));
            if(pixel) {
                if(submerged || (crossing && (r->bp&0x8000u))) pixel|=0x40;
                wr8(0xa000,row_dest,pixel);
            }
            row_dest=(uint16_t)(row_dest+96u);
            if(crossing) r->bp=(uint16_t)(r->bp-1);
            rows=(uint8_t)(rows-1);
        } while(rows);
        plane=(uint8_t)((plane<<1)&15u);
        flag(r,CF,0); /* AND AH,0Fh; later INC instructions preserve this. */
        if(!plane) { plane=1; dest=(uint16_t)(dest+1); }
        columns=dec_byte(r,columns);
    } while(columns);
    platform_out(0x3c5,1,15);
    return UGH_OK;
}
