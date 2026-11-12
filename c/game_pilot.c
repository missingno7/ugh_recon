#include "ugh.h"
#include "platform.h"

/* TRANSLATES GAME:ComplementHighScoreTable */
EXPORT int c_ComplementHighScoreTable(Regs *r) {
    r->si=106;
    do {
        uint16_t o=(uint16_t)(D(HighScoreRows)+r->si);
        wr8(r->ds,o,(uint8_t)logic(r,(uint8_t)(rd8(r->ds,o)^255u),8));
        r->si=dec16(r,r->si);
    } while((int16_t)r->si>=0);
    return UGH_OK;
}

/* TRANSLATES GAME:TestAllDemoScriptsFinished */
EXPORT int c_TestAllDemoScriptsFinished(Regs *r) {
    r->bx=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        uint16_t v=rd16(r->ds,(uint16_t)(D(ActorUpdateOrScriptCursor)+r->bx));
        sub16(r,v,65535,0);
        if(v==65535) { flag(r,CF,1); return UGH_OK; }
        r->bx=add16(r,r->bx,2,0);
        v=logic(r,rd16(r->ds,(uint16_t)(D(DemoCompletionScanBiasedBase)+r->bx)),16);
        if(!v) { flag(r,CF,0); return UGH_OK; }
    }
    return UGH_BUDGET;
}

/* TRANSLATES GAME:PollKeyboardScanChange */
EXPORT int c_PollKeyboardScanChange(Regs *r) {
    uint8_t old=rd8(r->ds,D(CurrentKeyboardScanCode));
    wr8(r->ds,D(PreviousPolledScanCode),old);
    uint8_t scan=rd8(GAME_SEG,G(LatestInterruptScanCode));
    wr8(r->ds,D(CurrentKeyboardScanCode),scan);
    set_al(r,scan); set_ah(r,(uint8_t)logic(r,(uint8_t)(scan^old),8));
    wr8(r->ds,D(KeyboardScanCodeChangeBits),(uint8_t)(r->ax>>8));
    return UGH_OK;
}

/* TRANSLATES GAME:CopyFarBytes */
EXPORT int c_CopyFarBytes(Regs *r) {
    uint16_t source=arg16(r,4), ds=arg16(r,6), dest=arg16(r,8), es=arg16(r,10);
    uint16_t count=arg16(r,0);
    for(unsigned n=0;n<count;n++) {
        wr8(es,dest,rd8(ds,source));
        source=(uint16_t)(source+step(r)); dest=(uint16_t)(dest+step(r));
    }
    r->cx=0; return UGH_OK; /* USES restores DS, ES, SI, DI; BP+8 ignored. */
}

/* TRANSLATES GAME:UploadChunkyImageToVgaPlanes */
EXPORT int c_UploadChunkyImageToVgaPlanes(Regs *r) {
    uint16_t ds=r->ds;
    r->di=rd16(GAME_SEG,G(DrawPagePointer)); r->es=rd16(GAME_SEG,G(DrawPagePointer)+2);
    r->cx=rd16(GAME_SEG,G(VgaPlaneCopyByteCount));
    r->si=rd16(ds,D(DecodedImagePointer)); r->ds=rd16(ds,D(DecodedImagePointer)+2);
    r->dx=0x3c4; set_al(r,2); platform_out(r->dx,1,2);
    /* INC DX flags survive all LODS/MOVS/LOOPs and the final MOV/OUT. */
    uint16_t cf=r->flags&CF;
    r->dx=add16(r,r->dx,1,0); flag(r,CF,cf);
    do {
        for(unsigned plane=0;plane<4;plane++) {
            set_al(r,(uint8_t)(1u<<plane)); platform_out(r->dx,1,(uint8_t)r->ax);
            uint8_t pixel=rd8(r->ds,r->si); r->si=(uint16_t)(r->si+step(r));
            if(plane<3) set_al(r,pixel); /* MOVSB does not change AL. */
            wr8(r->es,r->di,pixel);
        }
        r->di=(uint16_t)(r->di+step(r)); r->cx--;
    } while(r->cx); /* CX=0 means 65536 iterations, not zero. */
    set_al(r,15); platform_out(r->dx,1,15); r->ds=ds;
    return UGH_OK;
}
