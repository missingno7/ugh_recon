#include "ugh.h"

/* The decoder helpers and shared 4D4B tail are inline here: they are not separate
 * completed translations in the ledger. Only UnpackIceStream is an exported entry. */
typedef struct Ice {
    uint16_t ds,es,si,di;
    uint8_t bits;
    unsigned budget;
} Ice;
static unsigned next_bit(Ice *c) {
    unsigned carry=c->bits>>7;
    c->bits=(uint8_t)(c->bits*2u);
    if(!c->bits) {
        uint8_t b=rd8(c->ds,c->si--);
        c->bits=(uint8_t)(b*2u+carry); carry=b>>7;
    }
    return carry;
}
static uint16_t read_bits(Ice *c,uint16_t count) {
    uint16_t value=0;
    do { value=(uint16_t)(value*2u+next_bit(c)); count--; } while((int16_t)count>=0);
    return value;
}

/* TRANSLATES GAME:UnpackIceStream */
EXPORT int c_UnpackIceStream(Regs *r) {
    uint16_t magic=rd16(r->ds,r->si); r->si+=2; flag(r,DF,0);
    if(magic!=0x4349) return UGH_OK;
    magic=rd16(r->ds,r->si); r->si+=2;
    if(magic!=0x2145) return UGH_OK;
    r->si+=2;
    uint16_t packed=rd16(r->ds,r->si); r->si+=4;
    uint16_t output=rd16(r->ds,r->si);
    packed=(uint16_t)((packed<<8)|(packed>>8));
    output=(uint16_t)((output<<8)|(output>>8));
    Ice c={r->ds,r->es,(uint16_t)(packed-1),(uint16_t)(output-1),0,2000000};
    c.bits=rd8(c.ds,c.si--);
    for(;;) {
        if(!c.budget--) return UGH_BUDGET;
        if(next_bit(&c)) {
            uint16_t dx=0;
            if(next_bit(&c)) {
                uint16_t bp=G(IceLiteralCodeTablePivot); int bh=4;
                do {
                    bp-=2; dx=read_bits(&c,rd16(GAME_SEG,bp));
                    if(dx!=rd16(GAME_SEG,(uint16_t)(bp+20))) break;
                } while(--bh>=0);
                dx=(uint16_t)(dx+rd16(GAME_SEG,(uint16_t)(bp+10)));
            }
            do { wr8(c.es,c.di--,rd8(c.ds,c.si--)); dx--; } while((int16_t)dx>=0);
        }
        if(c.di==65535) break;
        uint16_t bp=3;
        while(next_bit(&c)) { if((int16_t)--bp<0) break; }
        uint16_t dx=0;
        int16_t count=(int8_t)rd8(GAME_SEG,(uint16_t)(G(IceMatchLengthBitCountsMinusOne)+bp));
        if(count>=0) dx=read_bits(&c,(uint16_t)count);
        uint16_t bx=(uint16_t)(rd8(GAME_SEG,(uint16_t)(G(IceMatchLengthBiases)+bp))+dx);
        if(bx) {
            bp=1;
            while(next_bit(&c)) { if((int16_t)--bp<0) break; }
            uint16_t bits=(uint16_t)(int16_t)(int8_t)rd8(GAME_SEG,(uint16_t)(G(IceMatchOffsetBitCountsMinusOne)+bp));
            dx=read_bits(&c,bits); bp=(uint16_t)(bp*2);
            dx=(uint16_t)(dx+rd16(GAME_SEG,(uint16_t)(G(IceMatchOffsetBiases)+bp)));
            if((int16_t)dx<0) dx=(uint16_t)(dx-bx);
        } else {
            unsigned wide=next_bit(&c);
            dx=read_bits(&c,wide ? 8 : 5);
            dx=(uint16_t)(dx+(wide ? 63 : 65535));
        }
        uint16_t source=(uint16_t)(bx+c.di+2+dx);
        wr8(c.es,c.di--,rd8(c.es,source--));
        do { wr8(c.es,c.di--,rd8(c.es,source--)); bx--; } while((int16_t)bx>=0);
    }
    r->si=c.si; r->di=c.di; return UGH_OK;
}
