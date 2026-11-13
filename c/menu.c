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
static void push(Regs *r,uint16_t v) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v); }
static uint16_t pop(Regs *r) { uint16_t v=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return v; }
#define MCALL(n,ret) do { int st=ugh_call_near(G(n),ret,r); if(st) return st; } while(0)

/* Program entry. DOS startup/runtime remain outside this entry contract.
 * All subsystem state is initialized by the actual translated startup calls. */
/* TRANSLATES GAME:RunDosGame */
EXPORT int c_RunDosGame(Regs *r) {
    r->dx=DATA_SEG; r->ds=r->dx;
    MCALL(InitializeDosVideoInputAndSound,G(RunDosGame)+8);
    MCALL(ShowStartupPictures,G(RunDosGame)+11);
    MCALL(ConfigureVgaGameplayPages,G(RunDosGame)+14);
    MCALL(RunMainMenuAndAttractLoop,G(RunDosGame)+17);
    return ugh_dispatch(r->cs,G(loc_4EE6),r);
}

/* Restore the background, rewrite the two selected strings and draw the block.
 * CopyIndexedMenuString doubles BX and leaves ES=DS; all renderer outputs flow. */
/* TRANSLATES GAME:DrawMainMenu */
EXPORT int c_DrawMainMenu(Regs *r) {
    MCALL(RestorePlayfieldBackground,G(DrawMainMenu)+3);
    r->bx=rd16(r->ds,D(SelectedDifficulty)); r->si=D(DifficultyLabelPointers); r->di=D(Text_0AE4)+0x29;
    MCALL(CopyIndexedMenuString,G(DrawMainMenu)+0x10);
    r->bx=rd16(r->ds,D(PlayerCount)); r->bx=dec16(r,r->bx); r->si=D(PlayerCountLabelPointers); r->di=D(Text_0AE4)+0x35;
    MCALL(CopyIndexedMenuString,G(DrawMainMenu)+0x1e);
    r->si=D(Text_0AE4); r->cx=0x48; MCALL(DrawTextBlock,G(DrawMainMenu)+0x27);
    return ugh_dispatch(r->cs,G(SwapAndDisplayVgaPage),r);
}
/* Drawing preserves the editor's live BX/SI save words across all callees. */
/* TRANSLATES GAME:DrawHighScoreNameEntry */
EXPORT int c_DrawHighScoreNameEntry(Regs *r) {
    push(r,r->bx); push(r,r->si); r->ax=logic(r,0,16);
    r->bx=0xa0; r->cx=320; r->dx=16; MCALL(RestoreBackgroundRectangle,G(DrawHighScoreNameEntry)+0x10);
    r->si=D(HighScoreNameEntry); r->cx=0xa0; MCALL(DrawTextLine,G(DrawHighScoreNameEntry)+0x19);
    MCALL(SwapAndDisplayVgaPage,G(DrawHighScoreNameEntry)+0x1c);
    r->si=pop(r); r->bx=pop(r); return UGH_OK;
}
/* The selectors are signed -1/0/1; INC maps them into the three strings. */
/* TRANSLATES GAME:DrawControlOptions */
EXPORT int c_DrawControlOptions(Regs *r) {
    MCALL(RestorePlayfieldBackground,G(DrawControlOptions)+3);
    r->bx=increment_word(r,rd16(r->ds,D(PlayerOneControlMode))); r->si=D(ControlModeLabelPointers); r->di=D(Text_0B64)+15;
    MCALL(CopyIndexedMenuString,G(DrawControlOptions)+0x11);
    r->bx=increment_word(r,rd16(r->ds,D(PlayerTwoControlMode))); r->si=D(ControlModeLabelPointers); r->di=D(Text_0B64)+41;
    MCALL(CopyIndexedMenuString,G(DrawControlOptions)+0x1f);
    r->si=D(Text_0B64); r->cx=0x50; MCALL(DrawTextBlock,G(DrawControlOptions)+0x28);
    return ugh_dispatch(r->cs,G(SwapAndDisplayVgaPage),r);
}
/* File-independent high-score display. Input result is saved across fade-out;
 * Q returns -1, every other termination returns +1, flags from final AND. */
/* TRANSLATES GAME:ShowHighScores */
EXPORT int c_ShowHighScores(Regs *r) {
    wr16(r->ds,D(WaterYPixels),200); r->cx=40; MCALL(WaitRetraceCount,G(ShowHighScores)+0xc);
    MCALL(ClearAllVgaPlanes,G(ShowHighScores)+0xf); MCALL(DrawMenuHeaderSprites,G(ShowHighScores)+0x12);
    r->si=D(Text_0C7B); r->cx=0x50; MCALL(DrawTextBlock,G(ShowHighScores)+0x1b);
    MCALL(SwapAndDisplayVgaPage,G(ShowHighScores)+0x1e); MCALL(FadePaletteIn,G(ShowHighScores)+0x21);
    r->cx=0x578; MCALL(WaitForInputOrRetraceTimeout,G(ShowHighScores)+0x27);
    push(r,r->ax); MCALL(FadePaletteOut,G(ShowHighScores)+0x2b); r->ax=pop(r);
    set_al(r,(uint8_t)logic(r,r->ax&0x7f,8)); compare_byte(r,(uint8_t)r->ax,0x10);
    r->ax=(uint8_t)r->ax==0x10?0xffff:1; logic(r,r->ax,16); return UGH_OK;
}

/* Shared 072A body. The old DS and map offset are real stack words while
 * ICE changes segments; the final page flip is a tail, retaining entry frame. */
static int prepare_attract_map(Regs *r) {
    push(r,r->di); push(r,r->ds); push(r,r->si);
    MCALL(BlackenVgaPalette,G(PrepareAttractMap0)+0x10);
    MCALL(ClearAllVgaPlanes,G(PrepareAttractMap0)+0x13);
    MCALL(DuplicateSourcePaletteHalves,G(PrepareAttractMap0)+0x16);
    uint16_t o=rd16(r->ds,D(CompressedTileMapsPointer)); r->ds=rd16(r->ds,D(CompressedTileMapsPointer)+2); r->si=o;
    MCALL(UnpackIceToScratch,G(PrepareAttractMap0)+0x1d);
    push(r,r->es); r->ds=pop(r); r->si=pop(r); r->di=DATA_SEG; r->es=r->di;
    r->di=D(Data_264C); r->cx=160;
    do {
        uint16_t v=rd16(r->ds,r->si); r->si=(uint16_t)(r->si+2*step(r));
        wr16(r->es,r->di,v); r->di=(uint16_t)(r->di+2*step(r)); r->cx--;
    } while(r->cx);
    r->ds=pop(r); MCALL(DrawTileMap,G(PrepareAttractMap0)+0x31);
    r->di=pop(r); logic(r,r->di,16);
    if(r->di) { MCALL(DrawMenuHeaderSprites,G(PrepareAttractMap0)+0x3c); }
    MCALL(SaveDrawPageBackground,G(PrepareAttractMap0)+0x3f);
    MCALL(SwapAndDisplayVgaPage,G(PrepareAttractMap0)+0x42);
    MCALL(RestorePlayfieldBackground,G(PrepareAttractMap0)+0x45);
    uint16_t y=rd16(r->ds,D(WaterYPixels)); sub16(r,y,192,0);
    if((int16_t)y<192) { MCALL(DrawWaterSurface,G(PrepareAttractMap0)+0x53); }
    return ugh_dispatch(r->cs,G(SwapAndDisplayVgaPage),r);
}
/* Map 90's offset is 90*320; SI/DI survive on the shared stack until copied. */
/* TRANSLATES GAME:PrepareAttractMap90 */
EXPORT int c_PrepareAttractMap90(Regs *r) {
    wr16(r->ds,D(WaterYPixels),192); r->si=90*320; r->di=1; return prepare_attract_map(r);
}
/* TRANSLATES GAME:PrepareAttractMap0 */
EXPORT int c_PrepareAttractMap0(Regs *r) {
    wr16(r->ds,D(WaterYPixels),180); r->si=logic(r,0,16); r->di=logic(r,0,16);
    return prepare_attract_map(r);
}

/* Raw scan polling, signed selector cycling and negative presence flags are
 * retained. The 0834h timeout is restarted by every unrecognized changed key. */
/* TRANSLATES GAME:SelectPlayerControls */
EXPORT int c_SelectPlayerControls(Regs *r) {
    wr16(r->ds,D(WaterYPixels),200); r->cx=40;
    MCALL(WaitRetraceCount,G(SelectPlayerControls)+0xc);
    MCALL(DrawControlOptions,G(SelectPlayerControls)+0xf);
    MCALL(FadePaletteIn,G(SelectPlayerControls)+0x12);
restart:
    r->cx=0x834;
    for(unsigned budget=0;budget<100000;budget++) {
        MCALL(WaitNextVerticalRetrace,G(SelectPlayerControls)+0x1d);
        r->cx=dec16(r,r->cx);
        if(!r->cx) return ugh_dispatch(r->cs,G(FadePaletteOut),r);
        MCALL(PollKeyboardScanChange,G(SelectPlayerControls)+0x29);
        logic(r,r->ax>>8,8); if(!(r->ax>>8)) continue;
        compare_byte(r,(uint8_t)r->ax,1);
        if((uint8_t)r->ax==1) return ugh_dispatch(r->cs,G(FadePaletteOut),r);
        compare_byte(r,(uint8_t)r->ax,0x3b);
        if((uint8_t)r->ax==0x3b) r->bx=logic(r,0,16);
        else {
            compare_byte(r,(uint8_t)r->ax,0x3c);
            if((uint8_t)r->ax!=0x3c) goto restart;
            r->bx=2;
        }
        r->ax=rd16(r->ds,(uint16_t)(D(PlayerOneControlMode)+r->bx));
        do {
            r->ax=increment_word(r,r->ax); sub16(r,r->ax,2,0);
            if((int16_t)r->ax>=2) { r->ax=0xffff; break; }
            r->si=(uint16_t)(r->ax<<1);
            flag(r,CF,r->ax&0x8000); flag(r,OF,!!(r->ax&0x8000)^!!(r->si&0x8000)); szp(r,r->si,16);
            logic(r,rd16(r->ds,(uint16_t)(D(JoystickPresentFlags)+r->si)),16);
        } while(!(r->flags&SF));
        wr16(r->ds,(uint16_t)(D(PlayerOneControlMode)+r->bx),r->ax);
        MCALL(DrawControlOptions,G(SelectPlayerControls)+0x17); goto restart;
    }
    return UGH_BUDGET;
}
static uint8_t add_byte(Regs *r,uint8_t a,uint8_t b) {
    uint8_t v=(uint8_t)(a+b); flag(r,CF,(unsigned)a+b>255);
    flag(r,OF,((~(a^b))&(a^v)&128)!=0); flag(r,AF,((a^b^v)&16)!=0); szp(r,v,8); return v;
}
static uint8_t inc_byte(Regs *r,uint8_t a) {
    uint16_t cf=r->flags&CF; uint8_t v=add_byte(r,a,1); flag(r,CF,cf); return v;
}
/* Level title list is NUL-separated; decrement DL before scanning each title.
 * Saved water Y and all far-cdecl sound arguments occupy the original stack. */
/* TRANSLATES GAME:ShowLevelIntroduction */
EXPORT int c_ShowLevelIntroduction(Regs *r) {
    MCALL(ClearAllVgaPlanes,G(ShowLevelIntroduction)+3);
    r->ax=rd16(r->ds,D(WaterYPixels)); push(r,r->ax); wr16(r->ds,D(WaterYPixels),175);
    set_al(r,inc_byte(r,rd8(r->ds,D(CurrentLevelIndex)))); r->si=D(DecimalDigitBuffer);
    MCALL(EncodeTwoDecimalDigits,G(ShowLevelIntroduction)+0x18);
    set_al(r,add_byte(r,rd8(r->ds,D(DecimalDigitBuffer)),0x30)); wr8(r->ds,D(LevelNumberTensCharacter),(uint8_t)r->ax);
    set_al(r,add_byte(r,rd8(r->ds,D(DecimalDigit1)),0x30)); wr8(r->ds,D(LevelNumberUnitsCharacter),(uint8_t)r->ax);
    r->cx=32; r->si=D(Text_0BF6); MCALL(DrawTextLine,G(ShowLevelIntroduction)+0x31);
    r->cx=add16(r,r->cx,32,0); r->si=rd16(r->ds,D(LevelIntroTextPointer));
    MCALL(DrawTextBlock,G(ShowLevelIntroduction)+0x3b);
    r->cx=160; r->si=D(Text_0C00); MCALL(DrawTextLine,G(ShowLevelIntroduction)+0x44);
    uint8_t dl=inc_byte(r,rd8(r->ds,D(CurrentLevelIndex))); r->dx=(uint16_t)((r->dx&0xff00)|dl);
    r->bx=sub16(r,rd16(r->ds,D(PlayerArrayBytes)),2,0); r->si=rd16(r->ds,(uint16_t)(D(PasswordListPointers)+r->bx));
    for(unsigned budget=0;budget<65536;budget++) {
        dl=(uint8_t)r->dx; uint16_t cf=r->flags&CF; dl=compare_byte(r,dl,1); flag(r,CF,cf);
        r->dx=(uint16_t)((r->dx&0xff00)|dl); if(!dl) break;
        do { load_character(r); logic(r,(uint8_t)r->ax,8); } while((uint8_t)r->ax);
        if(budget==65535) return UGH_BUDGET;
    }
    MCALL(DrawTextLine,G(ShowLevelIntroduction)+0x66);
    MCALL(SwapAndDisplayVgaPage,G(ShowLevelIntroduction)+0x69);
    push(r,0x11); push(r,r->cs); push(r,G(ShowLevelIntroduction)+0x70);
    int st=ugh_dispatch(UGH_S_C_StopMusicTrack,UGH_O_C_StopMusicTrack,r); if(st) return st;
    r->sp=(uint16_t)(r->sp+4); r->sp=add16(r,r->sp,2,0);
    push(r,1); push(r,0xe1); push(r,UGH_S_B3629_ext_3629); push(r,0);
    push(r,r->cs); push(r,G(ShowLevelIntroduction)+0x83);
    st=ugh_dispatch(UGH_S_C_PlayAdlibEffect,UGH_O_C_PlayAdlibEffect,r); if(st) return st;
    r->sp=(uint16_t)(r->sp+4); r->sp=add16(r,r->sp,8,0);
    MCALL(FadePaletteIn,G(ShowLevelIntroduction)+0x89);
    MCALL(WaitForScanChangeOrJoystickButton,G(ShowLevelIntroduction)+0x8c);
    r->ax=pop(r); wr16(r->ds,D(WaterYPixels),r->ax); return ugh_dispatch(r->cs,G(FadePaletteOut),r);
}

/* BIOS character editor: accepts only letters/digits, uppercases lowercase,
 * blinks at the live index and keeps the original 20-byte capacity. The shared
 * reinstatement tail, rather than a synthetic result, defines outputs. */
/* TRANSLATES GAME:EditLevelPassword */
EXPORT int c_EditLevelPassword(Regs *r) {
    MCALL(RestoreKeyboardInterrupt,G(EditLevelPassword)+3);
    MCALL(RestorePlayfieldBackground,G(EditLevelPassword)+6);
    MCALL(DrawMainMenu,G(EditLevelPassword)+9);
    r->si=19; set_al(r,32);
    do { wr8(r->ds,(uint16_t)(D(PasswordEditBuffer)+r->si),(uint8_t)r->ax); r->si=dec16(r,r->si); } while(!(r->flags&SF));
    r->si=logic(r,0,16);
reset_blink:
    r->bx&=0xff00; logic(r,0,8);
    for(unsigned budget=0;budget<100000;budget++) {
        MCALL(WaitVerticalRetraceActive,G(EditLevelPassword)+0x1d);
        uint8_t b=(uint8_t)r->bx; uint16_t cf=r->flags&CF;
        b=compare_byte(r,b,1); flag(r,CF,cf); r->bx=(uint16_t)((r->bx&0xff00)|b);
        logic(r,b&16,8); set_al(r,(b&16)?'?':' '); sub16(r,r->si,20,0);
        if(r->si<20) wr8(r->ds,(uint16_t)(D(PasswordEditBuffer)+r->si),(uint8_t)r->ax);
        push(r,r->bx); push(r,r->si); r->ax=logic(r,0,16); r->bx=176; r->cx=320; r->dx=16;
        MCALL(RestoreBackgroundRectangle,G(EditLevelPassword)+0x4a);
        r->si=D(PasswordEditBuffer); r->cx=176; MCALL(DrawTextLine,G(EditLevelPassword)+0x53);
        MCALL(SwapAndDisplayVgaPage,G(EditLevelPassword)+0x56); r->si=pop(r); r->bx=pop(r);
        set_ah(r,1); int st=platform_interrupt(0x16,r); if(st) return st;
        if(r->flags&ZF) continue;
        set_ah(r,0); logic(r,0,8); st=platform_interrupt(0x16,r); if(st) return st;
        compare_byte(r,(uint8_t)r->ax,8);
        if((uint8_t)r->ax==8) {
            logic(r,r->si,16); if(!r->si) continue;
            set_al(r,32); sub16(r,r->si,20,0);
            if(r->si<20) wr8(r->ds,(uint16_t)(D(PasswordEditBuffer)+r->si),32);
            r->si=dec16(r,r->si); wr8(r->ds,(uint16_t)(D(PasswordEditBuffer)+r->si),32); goto reset_blink;
        }
        uint8_t ch=(uint8_t)r->ax; int accept=0;
        compare_byte(r,ch,'A');
        if(ch>='A') { compare_byte(r,ch,'Z'); if(ch<='Z') accept=1; }
        if(!accept) {
            compare_byte(r,ch,'a');
            if(ch>='a') {
                compare_byte(r,ch,'z');
                if(ch<='z') { ch=compare_byte(r,ch,32); set_al(r,ch); accept=1; }
            }
        }
        if(!accept) { compare_byte(r,ch,'0'); if(ch>='0') { compare_byte(r,ch,'9'); if(ch<='9') accept=1; } }
        if(accept) {
            sub16(r,r->si,20,0); if(r->si>=20) continue;
            wr8(r->ds,(uint16_t)(D(PasswordEditBuffer)+r->si),ch); r->si=increment_word(r,r->si); goto reset_blink;
        }
        compare_byte(r,ch,13); if(ch!=13) continue;
        sub16(r,r->si,20,0);
        if(r->si<20) {
            wr8(r->ds,(uint16_t)(D(PasswordEditBuffer)+r->si),32); logic(r,r->si,16);
            if(!r->si) { wr16(r->ds,D(PasswordEditBuffer),0x4f4e); wr16(r->ds,D(PasswordEditChars2To3),0x454e); }
        }
        return ugh_dispatch(r->cs,G(InstallKeyboardSequenceInterrupt),r);
    }
    return UGH_BUDGET;
}
static int menu_far(Regs *r,uint16_t seg,uint16_t off,uint16_t ret,unsigned bytes) {
    push(r,r->cs); push(r,ret); int st=ugh_dispatch(seg,off,r); if(st) return st;
    r->sp=(uint16_t)(r->sp+4); r->sp=add16(r,r->sp,(uint16_t)bytes,0); return UGH_OK;
}
#define MFAR(seg,off,ret,n) do { int st=menu_far(r,seg,off,ret,n); if(st) return st; } while(0)
/* The labels mirror distinct menu states, retaining the original fallthroughs
 * and tail calls. Input IRQ service is at the actual polling CALL, not a
 * fixture mutation of menu state. No host menu state shadows original RAM. */
/* TRANSLATES GAME:RunMainMenuAndAttractLoop */
EXPORT int c_RunMainMenuAndAttractLoop(Regs *r) {
restart_music:
    push(r,0x11); MFAR(UGH_S_C_StopMusicTrack,UGH_O_C_StopMusicTrack,G(RunMainMenuAndAttractLoop)+7,2);
    push(r,0xa5); push(r,0); push(r,UGH_S_B3637_ext_3637); push(r,0);
    MFAR(UGH_S_C_StartMusicTrack,UGH_O_C_StartMusicTrack,G(RunMainMenuAndAttractLoop)+0x1a,8);
attract:
    MCALL(PlaySpriteRevealDemo,G(RunMainMenuAndAttractLoop)+0x20); if(r->flags&SF) return UGH_OK;
    if(!(r->flags&ZF)) goto prepare;
    MCALL(ShowCreditsPages,G(RunMainMenuAndAttractLoop)+0x2d); if(r->flags&SF) return UGH_OK;
    if(!(r->flags&ZF)) goto prepare;
    MCALL(PlayAttractDemo,G(RunMainMenuAndAttractLoop)+0x3a); if(r->flags&SF) return UGH_OK;
    if(!(r->flags&ZF)) goto prepare;
    MCALL(ShowHighScores,G(RunMainMenuAndAttractLoop)+0x47); if(r->flags&SF) return UGH_OK;
prepare:
    MCALL(DuplicateSourcePaletteHalves,G(RunMainMenuAndAttractLoop)+0x4f);
draw_screen:
    wr16(r->ds,D(WaterYPixels),175); r->cx=40;
    MCALL(WaitRetraceCount,G(RunMainMenuAndAttractLoop)+0x5b);
    MCALL(ClearAllVgaPlanes,G(RunMainMenuAndAttractLoop)+0x5e);
    MCALL(DrawMenuHeaderSprites,G(RunMainMenuAndAttractLoop)+0x61);
    MCALL(SaveDrawPageBackground,G(RunMainMenuAndAttractLoop)+0x64);
    MCALL(SwapAndDisplayVgaPage,G(RunMainMenuAndAttractLoop)+0x67);
    MCALL(RestorePlayfieldBackground,G(RunMainMenuAndAttractLoop)+0x6a);
    MCALL(DrawMainMenu,G(RunMainMenuAndAttractLoop)+0x6d);
    MCALL(FadePaletteIn,G(RunMainMenuAndAttractLoop)+0x70); goto timeout;
redraw:
    MCALL(DrawMainMenu,G(RunMainMenuAndAttractLoop)+0x75);
timeout:
    r->cx=0x834;
    for(unsigned budget=0;budget<100000;budget++) {
        MCALL(WaitNextVerticalRetrace,G(RunMainMenuAndAttractLoop)+0x7b); r->cx=dec16(r,r->cx);
        if(!r->cx) goto restart_attract;
        int st=platform_service_point_at(SERVICE_IO,r->cs,G(loc_00E9),r); if(st) return st;
        MCALL(PollKeyboardScanChange,G(RunMainMenuAndAttractLoop)+0x89);
        logic(r,r->ax>>8,8); if(!(r->ax>>8)) continue;
        compare_byte(r,(uint8_t)r->ax,0x2e); if((uint8_t)r->ax==0x2e) goto restart_attract;
        compare_byte(r,(uint8_t)r->ax,0x10); if((uint8_t)r->ax==0x10) return ugh_dispatch(r->cs,G(FadePaletteOut),r);
        compare_byte(r,(uint8_t)r->ax,0x3f);
        if((uint8_t)r->ax==0x3f) {
            MCALL(FadePaletteOut,G(RunMainMenuAndAttractLoop)+0xa6);
            MCALL(SelectPlayerControls,G(RunMainMenuAndAttractLoop)+0xa9); goto draw_screen;
        }
        compare_byte(r,(uint8_t)r->ax,0x3e);
        if((uint8_t)r->ax==0x3e) {
            r->ax=logic(r,rd16(r->ds,D(PlayerCount))^3,16); wr16(r->ds,D(PlayerCount),r->ax);
            flag(r,CF,r->ax&0x8000); r->ax=(uint16_t)(r->ax<<1); szp(r,r->ax,16);
            wr16(r->ds,D(PlayerArrayBytes),r->ax); goto redraw;
        }
        compare_byte(r,(uint8_t)r->ax,0x3d);
        if((uint8_t)r->ax==0x3d) {
            r->ax=increment_word(r,rd16(r->ds,D(SelectedDifficulty))); sub16(r,r->ax,3,0);
            if(r->ax>=3) r->ax=logic(r,0,16);
            wr16(r->ds,D(SelectedDifficulty),r->ax); goto redraw;
        }
        compare_byte(r,(uint8_t)r->ax,0x3c);
        if((uint8_t)r->ax==0x3c) { MCALL(EditLevelPassword,G(RunMainMenuAndAttractLoop)+0xe6); goto redraw; }
        compare_byte(r,(uint8_t)r->ax,0x3b); if((uint8_t)r->ax!=0x3b) goto timeout;
        MCALL(FadePaletteOut,G(RunMainMenuAndAttractLoop)+0xef);
        MCALL(RunGameFromPassword,G(RunMainMenuAndAttractLoop)+0xf2);
        MCALL(ClearAllVgaPlanes,G(RunMainMenuAndAttractLoop)+0xf5);
        r->bx=sub16(r,rd16(r->ds,D(PlayerArrayBytes)),2,0); r->ax=rd16(r->ds,D(CurrentLevelIndex));
        sub16(r,r->ax,rd16(r->ds,(uint16_t)(D(LevelCountsByPlayerMode)+r->bx)),0);
        if(!(r->flags&CF)) { MCALL(PlayGameCompletionDemo,G(RunMainMenuAndAttractLoop)+0x14c); }
        else {
            wr16(r->ds,D(WaterYPixels),200); r->si=D(Text_0C0C); r->cx=72;
            MCALL(DrawTextBlock,G(RunMainMenuAndAttractLoop)+0x117); MCALL(SwapAndDisplayVgaPage,G(RunMainMenuAndAttractLoop)+0x11a);
            push(r,0x11); MFAR(UGH_S_C_StopMusicTrack,UGH_O_C_StopMusicTrack,G(RunMainMenuAndAttractLoop)+0x121,2);
            push(r,1); push(r,0xe1); push(r,UGH_S_B326B_ext_326B); push(r,0);
            MFAR(UGH_S_C_PlayAdlibEffect,UGH_O_C_PlayAdlibEffect,G(RunMainMenuAndAttractLoop)+0x134,8);
            MCALL(FadePaletteIn,G(RunMainMenuAndAttractLoop)+0x13a); r->cx=700;
            MCALL(WaitForInputOrRetraceTimeout,G(RunMainMenuAndAttractLoop)+0x140);
            MCALL(FadePaletteOut,G(RunMainMenuAndAttractLoop)+0x143);
        }
        MCALL(InsertHighScoreAndClearScore,G(RunMainMenuAndAttractLoop)+0x146); goto restart_music;
    }
    return UGH_BUDGET;
restart_attract:
    MCALL(FadePaletteOut,G(RunMainMenuAndAttractLoop)+0x84); goto attract;
}
/* BIOS editor shared control shape, but capacity twelve and space acceptance
 * belong only to the score name. BX/SI survive every redraw explicitly. */
static int edit_score_name(Regs *r) {
    r->si=logic(r,0,16);
reset:
    r->bx&=0xff00; logic(r,0,8);
    for(unsigned budget=0;budget<100000;budget++) {
        MCALL(WaitVerticalRetraceActive,G(InsertHighScoreAndClearScore)+0xcd);
        uint16_t cf=r->flags&CF; uint8_t b=compare_byte(r,(uint8_t)r->bx,1); flag(r,CF,cf);
        r->bx=(uint16_t)((r->bx&0xff00)|b); logic(r,b&16,8); set_al(r,b&16?'?':' ');
        sub16(r,r->si,12,0); if(r->si<12) wr8(r->ds,(uint16_t)(D(HighScoreNameEntry)+r->si),(uint8_t)r->ax);
        MCALL(DrawHighScoreNameEntry,G(InsertHighScoreAndClearScore)+0xed);
        set_ah(r,1); int st=platform_interrupt(0x16,r); if(st) return st;
        if(r->flags&ZF) continue;
        set_ah(r,0); logic(r,0,8); st=platform_interrupt(0x16,r); if(st) return st;
        uint8_t ch=(uint8_t)r->ax; compare_byte(r,ch,8);
        if(ch==8) {
            logic(r,r->si,16); if(!r->si) continue;
            set_al(r,32); sub16(r,r->si,12,0);
            if(r->si<12) wr8(r->ds,(uint16_t)(D(HighScoreNameEntry)+r->si),32);
            r->si=dec16(r,r->si); wr8(r->ds,(uint16_t)(D(HighScoreNameEntry)+r->si),32); goto reset;
        }
        int accept=0; compare_byte(r,ch,'A');
        if(ch>='A') { compare_byte(r,ch,'Z'); if(ch<='Z') accept=1; }
        if(!accept) {
            compare_byte(r,ch,'a');
            if(ch>='a') { compare_byte(r,ch,'z'); if(ch<='z') { ch=compare_byte(r,ch,32); set_al(r,ch); accept=1; } }
        }
        if(!accept) { compare_byte(r,ch,'0'); if(ch>='0') { compare_byte(r,ch,'9'); if(ch<='9') accept=1; } }
        if(!accept) { compare_byte(r,ch,32); if(ch==32) accept=1; }
        if(accept) {
            sub16(r,r->si,12,0); if(r->si>=12) continue;
            wr8(r->ds,(uint16_t)(D(HighScoreNameEntry)+r->si),ch); r->si=increment_word(r,r->si); goto reset;
        }
        compare_byte(r,ch,13); if(ch!=13) continue;
        sub16(r,r->si,12,0);
        if(r->si<12) {
            wr8(r->ds,(uint16_t)(D(HighScoreNameEntry)+r->si),32);
            MCALL(DrawHighScoreNameEntry,G(InsertHighScoreAndClearScore)+0x177);
            logic(r,r->si,16);
            if(!r->si) {
                wr16(r->ds,D(HighScoreNameEntry),0x4e49); wr16(r->ds,D(HighScoreNameChars2To3),0x4f43);
                wr16(r->ds,D(HighScoreNameChars4To5),0x4e47); wr16(r->ds,D(HighScoreNameChars6To7),0x5449);
                wr16(r->ds,D(HighScoreNameChars8To9),0x5355);
            }
        }
        return UGH_OK;
    }
    return UGH_BUDGET;
}
/* Qualification ties insert; rows copy only twenty bytes. The selected row
 * index remains on the original stack across music, BIOS editing and drawing.
 * Both reject and insertion paths tail into the same score-zeroing code. */
/* TRANSLATES GAME:InsertHighScoreAndClearScore */
EXPORT int c_InsertHighScoreAndClearScore(Regs *r) {
    r->si=D(DecimalDigitBuffer); r->ax=rd16(r->ds,D(ScoreLowWord)); r->dx=rd16(r->ds,D(ScoreHighWord));
    MCALL(EncodeSixDecimalDigits,G(InsertHighScoreAndClearScore)+13);
    set_ah(r,0); logic(r,0,8); r->si=logic(r,0,16);
    do {
        set_al(r,add_byte(r,rd8(r->ds,(uint16_t)(D(DecimalDigitBuffer)+r->si)),48));
        compare_byte(r,(uint8_t)r->ax,48);
        if((uint8_t)r->ax!=48) { uint16_t cf=r->flags&CF; set_ah(r,compare_byte(r,(uint8_t)(r->ax>>8),1)); flag(r,CF,cf); }
        logic(r,r->ax>>8,8);
        if(!(r->ax>>8)) { compare_byte(r,(uint8_t)r->ax,48); if((uint8_t)r->ax==48) set_al(r,32); }
        wr8(r->ds,(uint16_t)(D(DecimalDigitBuffer)+r->si),(uint8_t)r->ax);
        r->si=increment_word(r,r->si); sub16(r,r->si,6,0);
    } while(r->si!=6);
    r->cx&=0xff00; logic(r,0,8);
    for(;;) {
        MCALL(TestHighScoreQualification,G(InsertHighScoreAndClearScore)+0x40); if(r->flags&CF) break;
        r->cx=(uint16_t)((r->cx&0xff00)|inc_byte(r,(uint8_t)r->cx)); compare_byte(r,(uint8_t)r->cx,5);
        if((uint8_t)r->cx==5) goto clear_score;
    }
    r->cx&=255; logic(r,0,8); push(r,r->cx); r->bp=r->cx; r->cx=(uint16_t)((r->cx&0xff00)|3);
    do {
        MCALL(CopyHighScoreRowDown,G(InsertHighScoreAndClearScore)+0x5c); r->cx=dec16(r,r->cx); sub16(r,r->cx,r->bp,0);
    } while((int16_t)r->cx>=(int16_t)r->bp);
    r->cx=r->bp; MCALL(GetHighScoreDigits,G(InsertHighScoreAndClearScore)+0x66); r->si=5;
    do {
        set_al(r,rd8(r->ds,(uint16_t)(D(DecimalDigitBuffer)+r->si))); wr8(r->ds,(uint16_t)(r->bx+r->si),(uint8_t)r->ax);
        r->si=dec16(r,r->si);
    } while(!(r->flags&SF));
    push(r,0x11); MFAR(UGH_S_C_StopMusicTrack,UGH_O_C_StopMusicTrack,G(InsertHighScoreAndClearScore)+0x79,2);
    push(r,0xa5); push(r,0); push(r,UGH_S_B3279_ext_3279); push(r,0);
    MFAR(UGH_S_C_StartMusicTrack,UGH_O_C_StartMusicTrack,G(InsertHighScoreAndClearScore)+0x8c,8);
    MCALL(RestoreKeyboardInterrupt,G(InsertHighScoreAndClearScore)+0x92);
    r->si=11; set_al(r,32);
    do { wr8(r->ds,(uint16_t)(D(HighScoreNameEntry)+r->si),32); r->si=dec16(r,r->si); } while(!(r->flags&SF));
    wr16(r->ds,D(WaterYPixels),159); r->cx=40; MCALL(WaitRetraceCount,G(InsertHighScoreAndClearScore)+0xab);
    MCALL(ClearAllVgaPlanes,G(InsertHighScoreAndClearScore)+0xae); MCALL(DrawMenuHeaderSprites,G(InsertHighScoreAndClearScore)+0xb1);
    r->si=D(Text_0C23); r->cx=80; MCALL(DrawTextBlock,G(InsertHighScoreAndClearScore)+0xba);
    MCALL(SaveDrawPageBackground,G(InsertHighScoreAndClearScore)+0xbd);
    MCALL(SwapAndDisplayVgaPage,G(InsertHighScoreAndClearScore)+0xc0);
    MCALL(RestorePlayfieldBackground,G(InsertHighScoreAndClearScore)+0xc3); MCALL(FadePaletteIn,G(InsertHighScoreAndClearScore)+0xc6);
    { int st=edit_score_name(r); if(st) return st; }
    r->cx=pop(r); MCALL(GetHighScoreRow,G(InsertHighScoreAndClearScore)+0x1a0); r->si=11;
    do {
        set_al(r,rd8(r->ds,(uint16_t)(D(HighScoreNameEntry)+r->si))); wr8(r->ds,(uint16_t)(r->bx+r->si),(uint8_t)r->ax);
        r->si=dec16(r,r->si);
    } while(!(r->flags&SF));
    MCALL(InstallKeyboardSequenceInterrupt,G(InsertHighScoreAndClearScore)+0x1b0);
    MCALL(FadePaletteOut,G(InsertHighScoreAndClearScore)+0x1b3); MCALL(SaveHighScores,G(InsertHighScoreAndClearScore)+0x1b6);
    MCALL(ShowHighScores,G(InsertHighScoreAndClearScore)+0x1b9);
clear_score:
    r->ax=logic(r,0,16); wr16(r->ds,D(ScoreLowWord),r->ax); wr16(r->ds,D(ScoreHighWord),r->ax); return UGH_OK;
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
