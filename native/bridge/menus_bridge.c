#include "front_end_support.h"
#include "../menus.h"
#define MCALL(n,ret) do { int st=ugh_call_near(G(n),ret,r); if(st) return st; } while(0)
#define MFAR(seg,off,ret,n) do { int st=menu_far(r,seg,off,ret,n); if(st) return st; } while(0)
static int prepare_attract_map(Regs *r) {
    push(r,r->di); push(r,r->ds); push(r,r->si);
    MCALL(BlackenVgaPalette,G(PrepareAttractMap0)+0x10);
    MCALL(ClearAllVgaPlanes,G(PrepareAttractMap0)+0x13);
    MCALL(DuplicateSourcePaletteHalves,G(PrepareAttractMap0)+0x16);
    uint16_t o=rd16(r->ds,D(CompressedTileMapsPointer)); r->ds=rd16(r->ds,D(CompressedTileMapsPointer)+2); r->si=o;
    MCALL(UnpackIceToScratch,G(PrepareAttractMap0)+0x1d);
    push(r,r->es); r->ds=pop(r); r->si=pop(r); r->di=DATA_SEG; r->es=r->di;
    r->di=D(Data_264C);MenusMapCopy copy=menus_map_begin(r->si,r->di,!!(r->flags&DF));r->cx=copy.remaining;
    do {
        uint16_t v=rd16(r->ds,r->si); r->si=(uint16_t)(copy.source+2*copy.direction);
        wr16(r->es,r->di,v); menus_map_advance(&copy);r->di=copy.destination;r->cx=copy.remaining;
    } while(r->cx);
    r->ds=pop(r); MCALL(DrawTileMap,G(PrepareAttractMap0)+0x31);
    r->di=pop(r); logic(r,r->di,16);
    if(r->di) { MCALL(DrawMenuHeaderSprites,G(PrepareAttractMap0)+0x3c); }
    MCALL(SaveDrawPageBackground,G(PrepareAttractMap0)+0x3f);
    MCALL(SwapAndDisplayVgaPage,G(PrepareAttractMap0)+0x42);
    MCALL(RestorePlayfieldBackground,G(PrepareAttractMap0)+0x45);
    uint16_t y=rd16(r->ds,D(WaterYPixels)); sub16(r,y,192,0);
    if(menus_draw_water(y)) { MCALL(DrawWaterSurface,G(PrepareAttractMap0)+0x53); }
    return ugh_dispatch(r->cs,G(SwapAndDisplayVgaPage),r);
}
static void main_key_trace(Regs *r,uint8_t scan) {
    static const uint8_t keys[]={0x2e,0x10,0x3f,0x3e,0x3d,0x3c,0x3b};
    for(unsigned i=0;i<7;i++) {compare_byte(r,scan,keys[i]);if(scan==keys[i]) break;}
}
EXPORT int c_RunMainMenuAndAttractLoop(Regs *r) {
    MenusMain menu={0,0,0};uint8_t completed=0;
    for(;;) {
        MenusMainReply reply={(uint8_t)!!(r->flags&SF),(uint8_t)!!(r->flags&ZF),(uint8_t)!!(r->ax>>8),(uint8_t)r->ax,completed,r->cx};
        MenusMainAction action=menus_main_next(&menu,reply);
        switch(action) {
        case MENUS_MAIN_STOP_MUSIC:
            push(r,0x11);MFAR(UGH_S_C_StopMusicTrack,UGH_O_C_StopMusicTrack,G(RunMainMenuAndAttractLoop)+7,2);break;
        case MENUS_MAIN_START_MUSIC:
            push(r,0xa5);push(r,0);push(r,UGH_S_B3637_ext_3637);push(r,0);
            MFAR(UGH_S_C_StartMusicTrack,UGH_O_C_StartMusicTrack,G(RunMainMenuAndAttractLoop)+0x1a,8);break;
        case MENUS_MAIN_REVEAL:MCALL(PlaySpriteRevealDemo,G(RunMainMenuAndAttractLoop)+0x20);break;
        case MENUS_MAIN_CREDITS:MCALL(ShowCreditsPages,G(RunMainMenuAndAttractLoop)+0x2d);break;
        case MENUS_MAIN_ATTRACT:MCALL(PlayAttractDemo,G(RunMainMenuAndAttractLoop)+0x3a);break;
        case MENUS_MAIN_SCORES:MCALL(ShowHighScores,G(RunMainMenuAndAttractLoop)+0x47);break;
        case MENUS_MAIN_PREPARE_PALETTE:MCALL(DuplicateSourcePaletteHalves,G(RunMainMenuAndAttractLoop)+0x4f);break;
        case MENUS_MAIN_PREPARE_SCREEN:
            wr16(r->ds,D(WaterYPixels),menus_water(2));r->cx=40;
            MCALL(WaitRetraceCount,G(RunMainMenuAndAttractLoop)+0x5b);
            MCALL(ClearAllVgaPlanes,G(RunMainMenuAndAttractLoop)+0x5e);
            MCALL(DrawMenuHeaderSprites,G(RunMainMenuAndAttractLoop)+0x61);
            MCALL(SaveDrawPageBackground,G(RunMainMenuAndAttractLoop)+0x64);
            MCALL(SwapAndDisplayVgaPage,G(RunMainMenuAndAttractLoop)+0x67);
            MCALL(RestorePlayfieldBackground,G(RunMainMenuAndAttractLoop)+0x6a);
            MCALL(DrawMainMenu,G(RunMainMenuAndAttractLoop)+0x6d);
            MCALL(FadePaletteIn,G(RunMainMenuAndAttractLoop)+0x70);break;
        case MENUS_MAIN_REDRAW:MCALL(DrawMainMenu,G(RunMainMenuAndAttractLoop)+0x75);break;
        case MENUS_MAIN_RESET_TIMEOUT:r->cx=0x834;break;
        case MENUS_MAIN_WAIT:MCALL(WaitNextVerticalRetrace,G(RunMainMenuAndAttractLoop)+0x7b);r->cx=dec16(r,r->cx);break;
        case MENUS_MAIN_POLL: {
            int status=platform_service_point_at(SERVICE_IO,r->cs,G(loc_00E9),r);if(status) return status;
            MCALL(PollKeyboardScanChange,G(RunMainMenuAndAttractLoop)+0x89);logic(r,r->ax>>8,8);if(r->ax>>8) main_key_trace(r,(uint8_t)r->ax);break;
        }
        case MENUS_MAIN_RESTART_ATTRACT:MCALL(FadePaletteOut,G(RunMainMenuAndAttractLoop)+0x84);break;
        case MENUS_MAIN_EXIT_FADE:return ugh_dispatch(r->cs,G(FadePaletteOut),r);
        case MENUS_MAIN_CONTROLS_FADE:MCALL(FadePaletteOut,G(RunMainMenuAndAttractLoop)+0xa6);break;
        case MENUS_MAIN_CONTROLS:MCALL(SelectPlayerControls,G(RunMainMenuAndAttractLoop)+0xa9);break;
        case MENUS_MAIN_PLAYERS: {
            FrontConfiguration configuration={0};configuration.players=rd16(r->ds,D(PlayerCount));menus_toggle_players(&configuration);
            r->ax=logic(r,configuration.players,16);wr16(r->ds,D(PlayerCount),configuration.players);
            flag(r,CF,r->ax&0x8000);r->ax=configuration.player_bytes;szp(r,r->ax,16);wr16(r->ds,D(PlayerArrayBytes),configuration.player_bytes);break;
        }
        case MENUS_MAIN_DIFFICULTY: {
            uint16_t difficulty=rd16(r->ds,D(SelectedDifficulty));r->ax=increment_word(r,difficulty);sub16(r,r->ax,3,0);if(r->ax>=3) logic(r,0,16);
            r->ax=menus_difficulty_next(difficulty);wr16(r->ds,D(SelectedDifficulty),r->ax);break;
        }
        case MENUS_MAIN_PASSWORD:MCALL(EditLevelPassword,G(RunMainMenuAndAttractLoop)+0xe6);break;
        case MENUS_MAIN_PLAY_FADE:MCALL(FadePaletteOut,G(RunMainMenuAndAttractLoop)+0xef);break;
        case MENUS_MAIN_SESSION:MCALL(RunGameFromPassword,G(RunMainMenuAndAttractLoop)+0xf2);break;
        case MENUS_MAIN_CLEAR_SESSION:MCALL(ClearAllVgaPlanes,G(RunMainMenuAndAttractLoop)+0xf5);break;
        case MENUS_MAIN_CHECK_SESSION: {
            r->bx=sub16(r,rd16(r->ds,D(PlayerArrayBytes)),2,0);r->ax=rd16(r->ds,D(CurrentLevelIndex));
            uint16_t limit=rd16(r->ds,(uint16_t)(D(LevelCountsByPlayerMode)+r->bx));sub16(r,r->ax,limit,0);completed=(uint8_t)menus_session_complete(r->ax,limit);break;
        }
        case MENUS_MAIN_COMPLETION:MCALL(PlayGameCompletionDemo,G(RunMainMenuAndAttractLoop)+0x14c);break;
        case MENUS_MAIN_GAME_OVER:
            wr16(r->ds,D(WaterYPixels),menus_water(3));r->si=D(Text_0C0C);r->cx=72;
            MCALL(DrawTextBlock,G(RunMainMenuAndAttractLoop)+0x117);MCALL(SwapAndDisplayVgaPage,G(RunMainMenuAndAttractLoop)+0x11a);
            push(r,0x11);MFAR(UGH_S_C_StopMusicTrack,UGH_O_C_StopMusicTrack,G(RunMainMenuAndAttractLoop)+0x121,2);
            push(r,1);push(r,0xe1);push(r,UGH_S_B326B_ext_326B);push(r,0);
            MFAR(UGH_S_C_PlayAdlibEffect,UGH_O_C_PlayAdlibEffect,G(RunMainMenuAndAttractLoop)+0x134,8);
            MCALL(FadePaletteIn,G(RunMainMenuAndAttractLoop)+0x13a);r->cx=700;
            MCALL(WaitForInputOrRetraceTimeout,G(RunMainMenuAndAttractLoop)+0x140);
            MCALL(FadePaletteOut,G(RunMainMenuAndAttractLoop)+0x143);break;
        case MENUS_MAIN_INSERT_SCORES:MCALL(InsertHighScoreAndClearScore,G(RunMainMenuAndAttractLoop)+0x146);break;
        case MENUS_MAIN_BOUND:return UGH_BUDGET;
        default:return UGH_OK;
        }
    }
}
EXPORT int c_DrawMainMenu(Regs *r) {
    MCALL(RestorePlayfieldBackground,G(DrawMainMenu)+3);
    MenusLabel difficulty=menus_label(0,rd16(r->ds,D(SelectedDifficulty)));r->bx=difficulty.index; r->si=D(DifficultyLabelPointers); r->di=(uint16_t)(D(Text_0AE4)+difficulty.destination);
    MCALL(CopyIndexedMenuString,G(DrawMainMenu)+0x10);
    uint16_t count=rd16(r->ds,D(PlayerCount));MenusLabel players=menus_label(1,count);r->bx=count;dec16(r,r->bx);r->bx=players.index;r->si=D(PlayerCountLabelPointers);r->di=(uint16_t)(D(Text_0AE4)+players.destination);
    MCALL(CopyIndexedMenuString,G(DrawMainMenu)+0x1e);
    r->si=D(Text_0AE4); r->cx=0x48; MCALL(DrawTextBlock,G(DrawMainMenu)+0x27);
    return ugh_dispatch(r->cs,G(SwapAndDisplayVgaPage),r);
}
EXPORT int c_DrawMenuHeaderSprites(Regs *r) {
    MenusHeaderItem first=menus_header_item(0,r->ax);r->ax=first.sprite;r->bx=first.x;r->cx=logic(r,0,16);
    int status=ugh_call_near(G(DrawTransparentSprite),
                            (uint16_t)(G(DrawMenuHeaderSprites)+11),r);
    if(status) return status;
    MenusHeaderItem second=menus_header_item(1,r->ax);increment_word(r,r->ax);r->ax=second.sprite;r->bx=second.x;
    status=ugh_call_near(G(DrawTransparentSprite),
                         (uint16_t)(G(DrawMenuHeaderSprites)+18),r);
    if(status) return status;
    MenusHeaderItem third=menus_header_item(2,r->ax);r->ax=third.sprite;r->bx=third.x;
    return ugh_dispatch(r->cs,G(DrawTransparentSprite),r);
}
EXPORT int c_SelectPlayerControls(Regs *r) {
    wr16(r->ds,D(WaterYPixels),menus_water(3)); r->cx=40;
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
        MenusControlKey key=menus_control_key((uint8_t)r->ax);compare_byte(r,(uint8_t)r->ax,1);
        if(key==MENUS_CONTROL_QUIT) return ugh_dispatch(r->cs,G(FadePaletteOut),r);
        compare_byte(r,(uint8_t)r->ax,0x3b);
        if(key==MENUS_CONTROL_PLAYER0) r->bx=logic(r,0,16);
        else {
            compare_byte(r,(uint8_t)r->ax,0x3c);
            if(key!=MENUS_CONTROL_PLAYER1) goto restart;
            r->bx=2;
        }
        r->ax=rd16(r->ds,(uint16_t)(D(PlayerOneControlMode)+r->bx));
        uint16_t presence=0;do {
            MenusControlCandidate candidate=menus_control_next(r->ax);r->ax=increment_word(r,r->ax); sub16(r,r->ax,2,0);
            if(candidate.keyboard) {r->ax=candidate.mode;break;}
            r->si=candidate.index;
            flag(r,CF,r->ax&0x8000); flag(r,OF,!!(r->ax&0x8000)^!!(r->si&0x8000)); szp(r,r->si,16);
            presence=rd16(r->ds,(uint16_t)(D(JoystickPresentFlags)+r->si));logic(r,presence,16);
        } while(!menus_control_present(presence));
        wr16(r->ds,(uint16_t)(D(PlayerOneControlMode)+r->bx),r->ax);
        MCALL(DrawControlOptions,G(SelectPlayerControls)+0x17); goto restart;
    }
    return UGH_BUDGET;
}
EXPORT int c_DrawControlOptions(Regs *r) {
    MCALL(RestorePlayfieldBackground,G(DrawControlOptions)+3);
    uint16_t mode0=rd16(r->ds,D(PlayerOneControlMode));MenusLabel first=menus_label(2,mode0);increment_word(r,mode0);r->bx=first.index; r->si=D(ControlModeLabelPointers); r->di=(uint16_t)(D(Text_0B64)+first.destination);
    MCALL(CopyIndexedMenuString,G(DrawControlOptions)+0x11);
    uint16_t mode1=rd16(r->ds,D(PlayerTwoControlMode));MenusLabel second=menus_label(3,mode1);increment_word(r,mode1);r->bx=second.index; r->si=D(ControlModeLabelPointers); r->di=(uint16_t)(D(Text_0B64)+second.destination);
    MCALL(CopyIndexedMenuString,G(DrawControlOptions)+0x1f);
    r->si=D(Text_0B64); r->cx=0x50; MCALL(DrawTextBlock,G(DrawControlOptions)+0x28);
    return ugh_dispatch(r->cs,G(SwapAndDisplayVgaPage),r);
}
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
        FrontBlink blink=front_blink(r->si,20,(uint8_t)r->bx);uint8_t b=(uint8_t)r->bx; uint16_t cf=r->flags&CF;
        b=compare_byte(r,b,1); flag(r,CF,cf); r->bx=(uint16_t)((r->bx&0xff00)|b);
        logic(r,b&16,8); set_al(r,blink.character); sub16(r,r->si,20,0);
        if(blink.write) wr8(r->ds,(uint16_t)(D(PasswordEditBuffer)+r->si),(uint8_t)r->ax);
        push(r,r->bx); push(r,r->si); r->ax=logic(r,0,16); r->bx=176; r->cx=320; r->dx=16;
        MCALL(RestoreBackgroundRectangle,G(EditLevelPassword)+0x4a);
        r->si=D(PasswordEditBuffer); r->cx=176; MCALL(DrawTextLine,G(EditLevelPassword)+0x53);
        MCALL(SwapAndDisplayVgaPage,G(EditLevelPassword)+0x56); r->si=pop(r); r->bx=pop(r);
        set_ah(r,1); int st=platform_interrupt(0x16,r); if(st) return st;
        if(r->flags&ZF) continue;
        set_ah(r,0); logic(r,0,8); st=platform_interrupt(0x16,r); if(st) return st;
        FrontEditCommand command=front_edit_command(r->si,20,(uint8_t)r->ax,0);compare_byte(r,(uint8_t)r->ax,8);
        if((uint8_t)r->ax==8) {
            logic(r,r->si,16); if(!r->si) continue;
            set_al(r,32); sub16(r,r->si,20,0);
            if(command.erase_count==2) wr8(r->ds,(uint16_t)(D(PasswordEditBuffer)+command.erase[0]),32);
            dec16(r,r->si);r->si=command.position;wr8(r->ds,(uint16_t)(D(PasswordEditBuffer)+r->si),32); goto reset_blink;
        }
        uint8_t ch=(uint8_t)r->ax;editor_compare_trace(r,ch,0);
        if(command.accepted) {
            sub16(r,r->si,20,0); if(command.kind!=FRONT_EDIT_STORE) continue;
            wr8(r->ds,(uint16_t)(D(PasswordEditBuffer)+r->si),command.character);increment_word(r,r->si);r->si=command.position; goto reset_blink;
        }
        compare_byte(r,ch,13); if(command.kind!=FRONT_EDIT_FINISH) continue;
        sub16(r,r->si,20,0);
        if(command.clear_current) {
            wr8(r->ds,(uint16_t)(D(PasswordEditBuffer)+r->si),32); logic(r,r->si,16);
            if(!r->si) { wr16(r->ds,D(PasswordEditBuffer),0x4f4e); wr16(r->ds,D(PasswordEditChars2To3),0x454e); }
        }
        return ugh_dispatch(r->cs,G(InstallKeyboardSequenceInterrupt),r);
    }
    return UGH_BUDGET;
}
EXPORT int c_CopyIndexedMenuString(Regs *r) {
    r->es=r->ds;
    r->bx=menus_double_index(r->bx);
    r->si=rd16_linear(r->ds,(uint16_t)(r->bx+r->si));
    MenusStringCopy copy=menus_string_begin(r->si,r->di,!!(r->flags&DF));for(;;) {
        uint8_t ch=rd8(r->ds,r->si);
        menus_string_read(&copy,ch);r->si=copy.source;
        set_al(r,(uint8_t)logic(r,ch,8));
        if(copy.done) return UGH_OK;
        wr8(r->es,r->di,ch);
        menus_string_written(&copy);r->di=copy.destination;
    }
}
EXPORT int c_DrawTextLine(Regs *r) {
    r->bx=logic(r,0,16);
    uint8_t ch=load_character(r); r->di=r->si;
    compare_byte(r,ch,0xfe);
    if(menus_text_centered(ch)) {
        r->bp=65535;
        do {
            ch=load_character(r); r->bp=increment_word(r,r->bp);
        } while(ch!=0 && ch!=13 && ch!=0xfd);
        r->bx=menus_text_center_x(r->bp);r->bp=(uint16_t)(r->bp<<4);
        r->si=r->di; ch=load_character(r);
    }
    for(;;) {
        MenusTextStep item=menus_text_step(ch);if(item.kind!=MENUS_TEXT_GLYPH) {
            uint16_t next_y=menus_text_next_y(r->cx,ch);
            if(ch==13) r->cx=add16(r,r->cx,8,0);
            if(ch) r->cx=add16(r,r->cx,8,0);
            r->cx=next_y;set_al(r,(uint8_t)logic(r,ch,8)); return UGH_OK;
        }
        ch=item.character;set_al(r,ch);set_ah(r,0);logic(r,0,8);
        add16(r,r->ax,0x237,0);r->ax=item.glyph;
        int status=ugh_call_near(G(DrawTransparentSprite),
                                (uint16_t)(G(DrawTextLine)+0x6c),r);
        if(status) return status;
        add16(r,r->bx,16,0);r->bx=menus_text_next_x(r->bx);ch=load_character(r);
    }
}
EXPORT int c_DrawTextBlock(Regs *r) {
    do {
        int status=ugh_call_near(G(DrawTextLine),
                                (uint16_t)(G(DrawTextBlock)+3),r);
        if(status) return status;
    } while(menus_text_step((uint8_t)r->ax).kind!=MENUS_TEXT_END);
    return UGH_OK;
}
EXPORT int c_PrepareAttractMap0(Regs *r) {
    wr16(r->ds,D(WaterYPixels),menus_water(0)); r->si=logic(r,0,16); r->di=logic(r,0,16);
    return prepare_attract_map(r);
}
EXPORT int c_PrepareAttractMap90(Regs *r) {
    wr16(r->ds,D(WaterYPixels),menus_water(1)); r->si=menus_attract_map_offset(1); r->di=1; return prepare_attract_map(r);
}
EXPORT int c_ShowLevelIntroduction(Regs *r) {
    MCALL(ClearAllVgaPlanes,G(ShowLevelIntroduction)+3);
    r->ax=rd16(r->ds,D(WaterYPixels)); push(r,r->ax); wr16(r->ds,D(WaterYPixels),menus_water(2));
    uint8_t level=rd8(r->ds,D(CurrentLevelIndex));inc_byte(r,level);set_al(r,menus_level_ordinal(level)); r->si=D(DecimalDigitBuffer);
    MCALL(EncodeTwoDecimalDigits,G(ShowLevelIntroduction)+0x18);
    {uint8_t digit=rd8(r->ds,D(DecimalDigitBuffer));add_byte(r,digit,0x30);set_al(r,menus_ascii_digit(digit));} wr8(r->ds,D(LevelNumberTensCharacter),(uint8_t)r->ax);
    {uint8_t digit=rd8(r->ds,D(DecimalDigit1));add_byte(r,digit,0x30);set_al(r,menus_ascii_digit(digit));} wr8(r->ds,D(LevelNumberUnitsCharacter),(uint8_t)r->ax);
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
EXPORT int c_ShowCreditsPages(Regs *r) {
    wr16(r->ds,D(WaterYPixels),menus_water(3)); MCALL(DuplicateSourcePaletteHalves,G(ShowCreditsPages)+9); r->si=D(Text_091F);
    for(unsigned pages=0;pages<32768;pages++) {
        push(r,r->si); r->cx=40; MCALL(WaitRetraceCount,G(ShowCreditsPages)+0x13);
        MCALL(ClearAllVgaPlanes,G(ShowCreditsPages)+0x16); MCALL(DrawMenuHeaderSprites,G(ShowCreditsPages)+0x19);
        MCALL(SaveDrawPageBackground,G(ShowCreditsPages)+0x1c); MCALL(SwapAndDisplayVgaPage,G(ShowCreditsPages)+0x1f);
        MCALL(RestorePlayfieldBackground,G(ShowCreditsPages)+0x22); r->si=pop(r); r->di=r->si; r->bp=logic(r,0,16);
        if(rd8(r->ds,r->si)==255) { r->ax=logic(r,0,16); return UGH_OK; }
        for(unsigned chars=0;chars<65536;chars++) {
            set_al(r,rd8(r->ds,r->si)); r->si=(uint16_t)(r->si+step(r));
            if((uint8_t)r->ax==0xfd || (uint8_t)r->ax==13) { uint16_t cf=r->flags&CF; r->bp=add16(r,r->bp,1,0); flag(r,CF,cf); continue; }
            if(!(uint8_t)r->ax) break;
            if(chars==65535) return UGH_BUDGET;
        }
        uint16_t center=menus_center_credits(r->bp);r->bp=(uint16_t)((r->bp+1)<<4); r->cx=sub16(r,144,r->bp,0);
        flag(r,CF,r->cx&1); r->cx>>=1; flag(r,OF,0); szp(r,r->cx,16);
        add16(r,r->cx,56,0);r->cx=center;r->si=r->di;
        MCALL(DrawTextBlock,G(ShowCreditsPages)+0x58); push(r,r->si);
        MCALL(SwapAndDisplayVgaPage,G(ShowCreditsPages)+0x5c); MCALL(FadePaletteIn,G(ShowCreditsPages)+0x5f);
        r->cx=350; MCALL(WaitForInputOrRetraceTimeout,G(ShowCreditsPages)+0x65);
        push(r,r->flags); push(r,r->ax); MCALL(FadePaletteOut,G(ShowCreditsPages)+0x6a);
        r->ax=pop(r); r->flags=pop(r); r->si=pop(r);
        if(r->flags&ZF) continue;
        set_al(r,(uint8_t)logic(r,r->ax&0x7f,8));
        r->ax=(uint16_t)menus_credits_result((uint8_t)r->ax);
        logic(r,r->ax,16); return UGH_OK;
    }
    return UGH_BUDGET;
}
