#include "ugh.h"
#include "platform.h"

/* All seven adapters have near returns, no arguments, and retain SS/SP/CS,
 * DS/ES and IF/DF. Memory operands use the incoming DS. Calls below construct
 * the original near frame, including when the callee is an existing pilot.
 * Inline flag helpers are implementation details, not translated entries. */
static uint8_t compare_byte(Regs *r,uint8_t a,uint8_t b) {
    uint8_t v=(uint8_t)(a-b);
    flag(r,CF,a<b); flag(r,OF,((a^b)&(a^v)&128u)!=0);
    flag(r,AF,((a^b^v)&16u)!=0); szp(r,v,8); return v;
}
static uint16_t increment_word(Regs *r,uint16_t v) {
    uint16_t carry=r->flags&CF;
    v=add16(r,v,1,0); flag(r,CF,carry); return v;
}
static uint8_t load_character(Regs *r) {
    uint8_t v=rd8(r->ds,r->si);
    r->si=(uint16_t)(r->si+step(r)); set_al(r,v); return v;
}

/* DS:HighScoreRows[107] is complemented before create/write and restored on
 * every return, including errors. AX/BX/CX/DX/SI and arithmetic flags are
 * outputs; DI/BP survive. A successful create stores DS:HighScoreFileHandle.
 * INT21 3C/40 are ordered platform transactions. The created handle leaks;
 * short writes are accepted; the complement tail destroys DOS carry errors. */
/* TRANSLATES GAME:SaveHighScores */
EXPORT int c_SaveHighScores(Regs *r) {
    int status=ugh_call_near(G(ComplementHighScoreTable),
                            (uint16_t)(G(SaveHighScores)+3),r);
    if(status) return status;
    r->dx=D(Data_0CF1); r->cx=0; set_ah(r,0x3c);
    status=platform_interrupt(0x21,r); if(status) return status;
    if(!(r->flags&CF)) {
        wr16(r->ds,D(HighScoreFileHandle),r->ax);
        r->cx=107; r->dx=D(HighScoreRows);
        r->bx=rd16(r->ds,D(HighScoreFileHandle)); set_ah(r,0x40);
        status=platform_interrupt(0x21,r); if(status) return status;
    }
    return ugh_dispatch(r->cs,G(ComplementHighScoreTable),r);
}

/* INT21 3D/3F/3E open/read/close. AX/BX/CX/DX/SI/flags are outputs; DI/BP
 * survive. Open errors leave the handle word/table untouched; read errors
 * leak the new handle; close errors skip complementing. Successful short
 * reads complement stale bytes too. No rollback, validation or host files. */
/* TRANSLATES GAME:LoadHighScores */
EXPORT int c_LoadHighScores(Regs *r) {
    r->dx=D(Data_0CF1); r->ax=0x3d00;
    int status=platform_interrupt(0x21,r); if(status) return status;
    if(r->flags&CF) return UGH_OK;
    wr16(r->ds,D(HighScoreFileHandle),r->ax);
    r->cx=107; r->dx=D(HighScoreRows); set_ah(r,0x3f);
    r->bx=rd16(r->ds,D(HighScoreFileHandle));
    status=platform_interrupt(0x21,r); if(status) return status;
    if(r->flags&CF) return UGH_OK;
    r->bx=rd16(r->ds,D(HighScoreFileHandle)); set_ah(r,0x3e);
    status=platform_interrupt(0x21,r); if(status) return status;
    if(r->flags&CF) return UGH_OK;
    return ugh_dispatch(r->cs,G(ComplementHighScoreTable),r);
}

/* CL is the unsigned row index; DS supplies stride, candidate and stored
 * characters. AX/BX and all arithmetic flags are outputs; other registers
 * survive. Unsigned byte lexicographic comparison, with ties qualifying.
 * CF is deliberately inverted relative to CMP; ZF describes the last CMP. */
/* TRANSLATES GAME:TestHighScoreQualification */
EXPORT int c_TestHighScoreQualification(Regs *r) {
    int status=ugh_call_near(G(GetHighScoreDigits),
                            (uint16_t)(G(TestHighScoreQualification)+3),r);
    if(status) return status;
    for(unsigned i=0;i<6;i++) {
        uint8_t a=rd8(r->ds,(uint16_t)(D(DecimalDigitBuffer)+i));
        uint8_t b=rd8(r->ds,(uint16_t)(r->bx+i));
        set_al(r,a); compare_byte(r,a,b);
        if(a!=b || i==5) { flag(r,CF,a>=b); return UGH_OK; }
    }
    return UGH_OK;
}

/* CL unsigned row, byte stride from DS. AX/BX/DX/DI and arithmetic flags
 * change; CX/SI/BP survive. Exactly twenty ordered byte copies to source+21,
 * independent of the configured stride. Destination byte 20 is stale. The
 * loop ignores DF, wraps each effective offset, and is not an overlap move. */
/* TRANSLATES GAME:CopyHighScoreRowDown */
EXPORT int c_CopyHighScoreRowDown(Regs *r) {
    int status=ugh_call_near(G(GetHighScoreRow),
                            (uint16_t)(G(CopyHighScoreRowDown)+3),r);
    if(status) return status;
    r->di=add16(r,r->bx,21,0); r->dx=19;
    do {
        set_al(r,rd8(r->ds,r->bx)); wr8(r->ds,r->di,(uint8_t)r->ax);
        r->bx=increment_word(r,r->bx); r->di=increment_word(r,r->di);
        r->dx=dec16(r,r->dx);
    } while((int16_t)r->dx>=0);
    return UGH_OK;
}

/* DS water threshold and original CS sprite pointers feed the pilot renderer.
 * Three draws at (16,0), (227,0), (97,0), IDs 215/216/214. AX=214,BX=97,CX=0;
 * BP and arithmetic flags flow from the final renderer. DX/SI/DI survive.
 * Effects: renderer scratch in CS, physical VGA and ordered sequencer writes. */
/* TRANSLATES GAME:DrawMenuHeaderSprites */
EXPORT int c_DrawMenuHeaderSprites(Regs *r) {
    r->ax=215; r->bx=16; r->cx=logic(r,0,16);
    int status=ugh_call_near(G(DrawTransparentSprite),
                            (uint16_t)(G(DrawMenuHeaderSprites)+11),r);
    if(status) return status;
    r->ax=increment_word(r,r->ax); r->bx=227;
    status=ugh_call_near(G(DrawTransparentSprite),
                         (uint16_t)(G(DrawMenuHeaderSprites)+18),r);
    if(status) return status;
    r->ax=214; r->bx=97;
    return ugh_dispatch(r->cs,G(DrawTransparentSprite),r);
}

/* DS:SI encoded line, CX Y; incoming DF controls every LODSB. AX/BX/CX/SI/
 * DI/BP change, DX survives. DI retains SI after the first byte. Initial FE
 * scans until NUL/CR/FD and centers with wrapped word arithmetic and logical
 * SHR. No clipping: overlong lines underflow and high bytes are glyphs.
 * Sprite ID=byte+0x237; 8E/99/9A map to 5B/5C/5D. CR adds 16, FD adds 8
 * to Y. AL is delimiter, final AND defines CF/PF/ZF/SF/OF; AF undefined.
 * VGA, CS scratch and sequencer effects belong to the existing renderer. */
/* TRANSLATES GAME:DrawTextLine */
EXPORT int c_DrawTextLine(Regs *r) {
    r->bx=logic(r,0,16);
    uint8_t ch=load_character(r); r->di=r->si;
    compare_byte(r,ch,0xfe);
    if(ch==0xfe) {
        r->bp=65535;
        do {
            ch=load_character(r); r->bp=increment_word(r,r->bp);
        } while(ch!=0 && ch!=13 && ch!=0xfd);
        r->bp=(uint16_t)(r->bp<<4);
        r->bx=(uint16_t)((uint16_t)(320-r->bp)>>1);
        r->si=r->di; ch=load_character(r);
    }
    for(;;) {
        if(ch==13 || ch==0xfd || ch==0) {
            if(ch==13) r->cx=add16(r,r->cx,8,0);
            if(ch) r->cx=add16(r,r->cx,8,0);
            set_al(r,(uint8_t)logic(r,ch,8)); return UGH_OK;
        }
        if(ch==0x8e) ch=0x5b;
        else if(ch==0x99) ch=0x5c;
        else if(ch==0x9a) ch=0x5d;
        set_al(r,ch); set_ah(r,0); logic(r,0,8); /* XOR AH,AH */
        r->ax=add16(r,r->ax,0x237,0);
        int status=ugh_call_near(G(DrawTransparentSprite),
                                (uint16_t)(G(DrawTextLine)+0x6c),r);
        if(status) return status;
        r->bx=add16(r,r->bx,16,0); ch=load_character(r);
    }
}

/* Same register/memory/device contract as DrawTextLine; repeatedly consumes
 * lines while returned ZF is clear. FF has no special meaning here. */
/* TRANSLATES GAME:DrawTextBlock */
EXPORT int c_DrawTextBlock(Regs *r) {
    do {
        int status=ugh_call_near(G(DrawTextLine),
                                (uint16_t)(G(DrawTextBlock)+3),r);
        if(status) return status;
    } while(!(r->flags&ZF));
    return UGH_OK;
}
