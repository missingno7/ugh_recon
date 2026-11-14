#include "front_end_support.h"
#include "../high_scores.h"
#define MCALL(n,ret) do { int st=ugh_call_near(G(n),ret,r); if(st) return st; } while(0)
#define MFAR(seg,off,ret,n) do { int st=menu_far(r,seg,off,ret,n); if(st) return st; } while(0)
static int edit_score_name(Regs *r) {
    r->si=logic(r,0,16);
reset:
    r->bx&=0xff00; logic(r,0,8);
    for(unsigned budget=0;budget<100000;budget++) {
        MCALL(WaitVerticalRetraceActive,G(InsertHighScoreAndClearScore)+0xcd);
        FrontBlink blink=front_blink(r->si,12,(uint8_t)r->bx);uint16_t cf=r->flags&CF; uint8_t b=compare_byte(r,(uint8_t)r->bx,1); flag(r,CF,cf);
        r->bx=(uint16_t)((r->bx&0xff00)|b); logic(r,b&16,8); set_al(r,blink.character);
        sub16(r,r->si,12,0); if(blink.write) wr8(r->ds,(uint16_t)(D(HighScoreNameEntry)+r->si),(uint8_t)r->ax);
        MCALL(DrawHighScoreNameEntry,G(InsertHighScoreAndClearScore)+0xed);
        set_ah(r,1); int st=platform_interrupt(0x16,r); if(st) return st;
        if(r->flags&ZF) continue;
        set_ah(r,0); logic(r,0,8); st=platform_interrupt(0x16,r); if(st) return st;
        uint8_t ch=(uint8_t)r->ax;FrontEditCommand command=front_edit_command(r->si,12,ch,1); compare_byte(r,ch,8);
        if(ch==8) {
            logic(r,r->si,16); if(!r->si) continue;
            set_al(r,32); sub16(r,r->si,12,0);
            if(command.erase_count==2) wr8(r->ds,(uint16_t)(D(HighScoreNameEntry)+command.erase[0]),32);
            dec16(r,r->si);r->si=command.position;wr8(r->ds,(uint16_t)(D(HighScoreNameEntry)+command.position),32); goto reset;
        }
        editor_compare_trace(r,ch,1);
        if(command.accepted) {
            sub16(r,r->si,12,0); if(command.kind!=FRONT_EDIT_STORE) continue;
            wr8(r->ds,(uint16_t)(D(HighScoreNameEntry)+r->si),command.character); increment_word(r,r->si);r->si=command.position; goto reset;
        }
        compare_byte(r,ch,13); if(command.kind!=FRONT_EDIT_FINISH) continue;
        sub16(r,r->si,12,0);
        if(command.clear_current) {
            wr8(r->ds,(uint16_t)(D(HighScoreNameEntry)+r->si),32);
            MCALL(DrawHighScoreNameEntry,G(InsertHighScoreAndClearScore)+0x177);
            logic(r,r->si,16);
            FrontEditCommand after_draw=front_edit_command(r->si,12,13,1);if(after_draw.empty) {
                for(unsigned i=0;i<5;i++) wr16(r->ds,(uint16_t)(D(HighScoreNameEntry)+2u*i),high_default_name_word(i));
            }
        }
        return UGH_OK;
    }
    return UGH_BUDGET;
}
EXPORT int c_LoadHighScores(Regs *r) {
    HighFileFlow flow={0,0};
    for(;;) {
        HighFileAction action=high_file_next(&flow,!!(r->flags&CF));int status;
        switch(action) {
        case HIGH_FILE_COMPLEMENT:
            if(flow.saving && flow.phase==1) {status=ugh_call_near(G(ComplementHighScoreTable),G(SaveHighScores)+3,r);if(status) return status;break;}
            return ugh_dispatch(r->cs,G(ComplementHighScoreTable),r);
        case HIGH_FILE_CREATE:r->dx=D(Data_0CF1);r->cx=0;set_ah(r,0x3c);status=platform_interrupt(0x21,r);if(status) return status;break;
        case HIGH_FILE_OPEN:r->dx=D(Data_0CF1);r->ax=0x3d00;status=platform_interrupt(0x21,r);if(status) return status;break;
        case HIGH_FILE_READ:case HIGH_FILE_WRITE:
            wr16(r->ds,D(HighScoreFileHandle),r->ax);r->cx=high_file_size();r->dx=D(HighScoreRows);r->bx=rd16(r->ds,D(HighScoreFileHandle));set_ah(r,action==HIGH_FILE_READ ? 0x3f : 0x40);
            status=platform_interrupt(0x21,r);if(status) return status;break;
        case HIGH_FILE_CLOSE:r->bx=rd16(r->ds,D(HighScoreFileHandle));set_ah(r,0x3e);status=platform_interrupt(0x21,r);if(status) return status;break;
        default:return UGH_OK;
        }
    }
}
EXPORT int c_SaveHighScores(Regs *r) {
    HighFileFlow flow={1,0};
    for(;;) {
        HighFileAction action=high_file_next(&flow,!!(r->flags&CF));int status;
        switch(action) {
        case HIGH_FILE_COMPLEMENT:
            if(flow.saving && flow.phase==1) {status=ugh_call_near(G(ComplementHighScoreTable),G(SaveHighScores)+3,r);if(status) return status;break;}
            return ugh_dispatch(r->cs,G(ComplementHighScoreTable),r);
        case HIGH_FILE_CREATE:r->dx=D(Data_0CF1);r->cx=0;set_ah(r,0x3c);status=platform_interrupt(0x21,r);if(status) return status;break;
        case HIGH_FILE_OPEN:r->dx=D(Data_0CF1);r->ax=0x3d00;status=platform_interrupt(0x21,r);if(status) return status;break;
        case HIGH_FILE_READ:case HIGH_FILE_WRITE:
            wr16(r->ds,D(HighScoreFileHandle),r->ax);r->cx=high_file_size();r->dx=D(HighScoreRows);r->bx=rd16(r->ds,D(HighScoreFileHandle));set_ah(r,action==HIGH_FILE_READ ? 0x3f : 0x40);
            status=platform_interrupt(0x21,r);if(status) return status;break;
        case HIGH_FILE_CLOSE:r->bx=rd16(r->ds,D(HighScoreFileHandle));set_ah(r,0x3e);status=platform_interrupt(0x21,r);if(status) return status;break;
        default:return UGH_OK;
        }
    }
}
EXPORT int c_ComplementHighScoreTable(Regs *r) {
    HighDescending cursor=high_complement_begin();r->si=cursor.position;
    do {
        uint16_t o=(uint16_t)(D(HighScoreRows)+r->si);
        wr8(r->ds,o,(uint8_t)logic(r,(uint8_t)(high_complement_byte(rd8(r->ds,o))),8));
        dec16(r,r->si);high_descending_advance(&cursor);r->si=cursor.position;
    } while(cursor.remaining);
    return UGH_OK;
}
EXPORT int c_GetHighScoreRow(Regs *r) {
    uint8_t stride=rd8(r->ds,D(HighScoreRowStride));uint16_t product=(uint16_t)((uint8_t)r->cx * stride);
    r->ax=add16(r,product,D(HighScoreRows),0);
    r->bx=(uint16_t)(D(HighScoreRows)+high_row_offset((uint8_t)r->cx,stride,0));
    return UGH_OK;
}
EXPORT int c_GetHighScoreDigits(Regs *r) {
    uint8_t stride=rd8(r->ds,D(HighScoreRowStride));uint16_t product=(uint16_t)((uint8_t)r->cx * stride);
    r->ax=add16(r,product,(uint16_t)(D(HighScoreRows)+14),0);
    r->bx=(uint16_t)(D(HighScoreRows)+high_row_offset((uint8_t)r->cx,stride,1));
    return UGH_OK;
}
EXPORT int c_CopyHighScoreRowDown(Regs *r) {
    int status=ugh_call_near(G(GetHighScoreRow),
                            (uint16_t)(G(CopyHighScoreRowDown)+3),r);
    if(status) return status;
    HighCopy copy=high_copy_begin(r->bx);add16(r,r->bx,21,0);r->di=copy.destination;r->dx=(uint16_t)(copy.remaining-1u);
    do {
        set_al(r,rd8(r->ds,copy.source));wr8(r->ds,copy.destination,(uint8_t)r->ax);
        increment_word(r,r->bx);increment_word(r,r->di);
        r->dx=dec16(r,r->dx);high_copy_advance(&copy);r->bx=copy.source;r->di=copy.destination;
    } while(copy.remaining);
    return UGH_OK;
}
EXPORT int c_TestHighScoreQualification(Regs *r) {
    int status=ugh_call_near(G(GetHighScoreDigits),
                            (uint16_t)(G(TestHighScoreQualification)+3),r);
    if(status) return status;
    HighQualification test={0,0,0};for(;;) {unsigned i=test.position;
        uint8_t a=rd8(r->ds,(uint16_t)(D(DecimalDigitBuffer)+i));
        uint8_t b=rd8(r->ds,(uint16_t)(r->bx+i));
        set_al(r,a); compare_byte(r,a,b);
        high_compare_step(&test,a,b);if(test.done) {flag(r,CF,test.qualifies);return UGH_OK;}
    }
    return UGH_OK;
}
EXPORT int c_InsertHighScoreAndClearScore(Regs *r) {
    r->si=D(DecimalDigitBuffer); r->ax=rd16(r->ds,D(ScoreLowWord)); r->dx=rd16(r->ds,D(ScoreHighWord));
    MCALL(EncodeSixDecimalDigits,G(InsertHighScoreAndClearScore)+13);
    set_ah(r,0); logic(r,0,8); r->si=logic(r,0,16);
    do {
        uint8_t digit=rd8(r->ds,(uint16_t)(D(DecimalDigitBuffer)+r->si));HighFormatDigit formatted=high_format_digit(digit,(uint8_t)(r->ax>>8));
        set_al(r,add_byte(r,digit,48));
        compare_byte(r,(uint8_t)r->ax,48);
        if((uint8_t)r->ax!=48) { uint16_t cf=r->flags&CF; set_ah(r,compare_byte(r,(uint8_t)(r->ax>>8),1)); flag(r,CF,cf); }
        logic(r,r->ax>>8,8);
        if(!(r->ax>>8)) { compare_byte(r,(uint8_t)r->ax,48); if((uint8_t)r->ax==48) set_al(r,32); }
        set_al(r,formatted.character);set_ah(r,formatted.significant);wr8(r->ds,(uint16_t)(D(DecimalDigitBuffer)+r->si),(uint8_t)r->ax);
        r->si=increment_word(r,r->si); sub16(r,r->si,6,0);
    } while(r->si!=6);
    r->cx&=0xff00; logic(r,0,8);
    HighInsertion insertion={0,0,0,0};for(;;) {
        MCALL(TestHighScoreQualification,G(InsertHighScoreAndClearScore)+0x40); high_insertion_compare(&insertion,!!(r->flags&CF));if(insertion.accepted) break;
        r->cx=(uint16_t)((r->cx&0xff00)|inc_byte(r,(uint8_t)r->cx)); compare_byte(r,(uint8_t)r->cx,5);
        if(insertion.done) goto clear_score;
    }
    r->cx&=255; logic(r,0,8); push(r,r->cx); r->bp=r->cx; r->cx=(uint16_t)((r->cx&0xff00)|insertion.shift);
    do {
        MCALL(CopyHighScoreRowDown,G(InsertHighScoreAndClearScore)+0x5c); r->cx=dec16(r,r->cx); sub16(r,r->cx,r->bp,0);
    } while(high_shift_advance(&insertion));
    r->cx=r->bp; MCALL(GetHighScoreDigits,G(InsertHighScoreAndClearScore)+0x66); HighDescending digits=high_digits_begin();r->si=digits.position;
    do {
        set_al(r,rd8(r->ds,(uint16_t)(D(DecimalDigitBuffer)+r->si))); wr8(r->ds,(uint16_t)(r->bx+r->si),(uint8_t)r->ax);
        dec16(r,r->si);high_descending_advance(&digits);r->si=digits.position;
    } while(digits.remaining);
    push(r,0x11); MFAR(UGH_S_C_StopMusicTrack,UGH_O_C_StopMusicTrack,G(InsertHighScoreAndClearScore)+0x79,2);
    push(r,0xa5); push(r,0); push(r,UGH_S_B3279_ext_3279); push(r,0);
    MFAR(UGH_S_C_StartMusicTrack,UGH_O_C_StartMusicTrack,G(InsertHighScoreAndClearScore)+0x8c,8);
    MCALL(RestoreKeyboardInterrupt,G(InsertHighScoreAndClearScore)+0x92);
    HighDescending blank=high_name_begin();r->si=blank.position;set_al(r,32);
    do {wr8(r->ds,(uint16_t)(D(HighScoreNameEntry)+blank.position),32);dec16(r,r->si);high_descending_advance(&blank);r->si=blank.position;} while(blank.remaining);
    wr16(r->ds,D(WaterYPixels),159); r->cx=40; MCALL(WaitRetraceCount,G(InsertHighScoreAndClearScore)+0xab);
    MCALL(ClearAllVgaPlanes,G(InsertHighScoreAndClearScore)+0xae); MCALL(DrawMenuHeaderSprites,G(InsertHighScoreAndClearScore)+0xb1);
    r->si=D(Text_0C23); r->cx=80; MCALL(DrawTextBlock,G(InsertHighScoreAndClearScore)+0xba);
    MCALL(SaveDrawPageBackground,G(InsertHighScoreAndClearScore)+0xbd);
    MCALL(SwapAndDisplayVgaPage,G(InsertHighScoreAndClearScore)+0xc0);
    MCALL(RestorePlayfieldBackground,G(InsertHighScoreAndClearScore)+0xc3); MCALL(FadePaletteIn,G(InsertHighScoreAndClearScore)+0xc6);
    { int st=edit_score_name(r); if(st) return st; }
    r->cx=pop(r); MCALL(GetHighScoreRow,G(InsertHighScoreAndClearScore)+0x1a0); HighDescending name=high_name_begin();r->si=name.position;
    do {
        set_al(r,rd8(r->ds,(uint16_t)(D(HighScoreNameEntry)+r->si))); wr8(r->ds,(uint16_t)(r->bx+r->si),(uint8_t)r->ax);
        dec16(r,r->si);high_descending_advance(&name);r->si=name.position;
    } while(name.remaining);
    MCALL(InstallKeyboardSequenceInterrupt,G(InsertHighScoreAndClearScore)+0x1b0);
    MCALL(FadePaletteOut,G(InsertHighScoreAndClearScore)+0x1b3); MCALL(SaveHighScores,G(InsertHighScoreAndClearScore)+0x1b6);
    MCALL(ShowHighScores,G(InsertHighScoreAndClearScore)+0x1b9);
clear_score:
    r->ax=logic(r,0,16); wr16(r->ds,D(ScoreLowWord),r->ax); wr16(r->ds,D(ScoreHighWord),r->ax); return UGH_OK;
}
EXPORT int c_ShowHighScores(Regs *r) {
    wr16(r->ds,D(WaterYPixels),200); r->cx=40; MCALL(WaitRetraceCount,G(ShowHighScores)+0xc);
    MCALL(ClearAllVgaPlanes,G(ShowHighScores)+0xf); MCALL(DrawMenuHeaderSprites,G(ShowHighScores)+0x12);
    r->si=D(Text_0C7B); r->cx=0x50; MCALL(DrawTextBlock,G(ShowHighScores)+0x1b);
    MCALL(SwapAndDisplayVgaPage,G(ShowHighScores)+0x1e); MCALL(FadePaletteIn,G(ShowHighScores)+0x21);
    r->cx=0x578; MCALL(WaitForInputOrRetraceTimeout,G(ShowHighScores)+0x27);
    push(r,r->ax); MCALL(FadePaletteOut,G(ShowHighScores)+0x2b); r->ax=pop(r);
    set_al(r,(uint8_t)logic(r,r->ax&0x7f,8)); compare_byte(r,(uint8_t)r->ax,0x10);
    r->ax=(uint16_t)high_show_result((uint8_t)r->ax); logic(r,r->ax,16); return UGH_OK;
}
EXPORT int c_DrawHighScoreNameEntry(Regs *r) {
    push(r,r->bx); push(r,r->si); r->ax=logic(r,0,16);
    FrontRectangle rectangle=front_entry_rectangle(1);r->bx=rectangle.y;r->cx=rectangle.width;r->dx=rectangle.height; MCALL(RestoreBackgroundRectangle,G(DrawHighScoreNameEntry)+0x10);
    r->si=D(HighScoreNameEntry); r->cx=0xa0; MCALL(DrawTextLine,G(DrawHighScoreNameEntry)+0x19);
    MCALL(SwapAndDisplayVgaPage,G(DrawHighScoreNameEntry)+0x1c);
    r->si=pop(r); r->bx=pop(r); return UGH_OK;
}
