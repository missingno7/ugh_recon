#include "platform.h"

/* All entries are near, without arguments. DS owns the parallel state arrays;
 * CS owns page pointers. SS:SP and IF/DF survive. Arithmetic is word-sized.
 * Calls retain the measured original return words, including the tail transfer
 * from initialization into the already translated script interpreter. */
#define R(n) rd16(r->ds,D(n))
#define W(n,v) wr16(r->ds,D(n),(uint16_t)(v))
#define RX(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define WX(n,i,v) wr16(r->ds,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define CALL(n,ret) do { int status=ugh_call_near(G(n),ret,r); if(status) return status; } while(0)
static uint16_t sar(uint16_t v,unsigned n) {
    return (uint16_t)((v>>n)|((v&0x8000u) ? (0xffffu<<(16-n)) : 0));
}
static void push(Regs *r,uint16_t v) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v); }
static uint16_t pop(Regs *r) { uint16_t v=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return v; }

/* Erase caches are updated even for hidden/FFFF sprites; the current cursor
 * vector's equality-only FFFF sentinel bounds the scan. Restore clears DF. */
/* TRANSLATES GAME:EraseDemoSprites */
EXPORT int c_EraseDemoSprites(Regs *r) {
    r->si=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        sub16(r,RX(ActorUpdateOrScriptCursor,r->si),0xffff,0);
        if(r->flags&ZF) return UGH_OK;
        r->ax=RX(ActorSpriteIds,r->si); r->cx=RX(ActorEraseSprite,r->si); WX(ActorEraseSprite,r->si,r->ax);
        sub16(r,r->cx,0xffff,0);
        if(!(r->flags&ZF)) {
            sub16(r,r->cx,0x7fff,0);
            if(!(r->flags&ZF)) {
                r->ax=RX(ActorPreviousDrawX,r->si); r->bx=RX(ActorPreviousDrawY,r->si);
                CALL(RestoreSpriteBackground,G(EraseDemoSprites)+0x34);
            }
        }
        r->si=add16(r,r->si,2,0);
    }
    return UGH_BUDGET;
}
/* Whole demo loop: fade advances in live RAM, scripts/callbacks and both
 * rendering paths run normally. Input never changes state via a fixture hook.
 * SF/ZF are memory TEST outputs; AX is deliberately not the exit-code result. */
/* TRANSLATES GAME:RunScriptedDemo */
EXPORT int c_RunScriptedDemo(Regs *r) {
    CALL(InitializeDemoScripts,G(RunScriptedDemo)+3);
    r->ax=logic(r,0,16); W(DemoExitCode,r->ax); W(ScreenFadeLevel,r->ax); W(ScreenFadeStep,4);
    CALL(PollKeyboardScanChange,G(RunScriptedDemo)+0x14);
    for(unsigned budget=0;budget<100000;budget++) {
        r->cx=R(ScreenFadeLevel); sub16(r,r->cx,0,0);
        if((int16_t)r->cx<0) { logic(r,R(DemoExitCode),16); return UGH_OK; }
        sub16(r,r->cx,256,0);
        if((int16_t)r->cx<=256) {
            CALL(ScaleAndUploadFadedPalette,G(RunScriptedDemo)+0x2f);
            r->cx=add16(r,r->cx,R(ScreenFadeStep),0); W(ScreenFadeLevel,r->cx);
        } else { CALL(WaitNextVerticalRetrace,G(RunScriptedDemo)+0x3c); }
        CALL(EraseDemoSprites,G(RunScriptedDemo)+0x3f);
        sub16(r,R(WaterYPixels),192,0);
        if((int16_t)R(WaterYPixels)<192) { CALL(DrawWaterSurface,G(RunScriptedDemo)+0x4d); }
        CALL(AdvanceDemoScripts,G(RunScriptedDemo)+0x50);
        CALL(DrawDemoSprites,G(RunScriptedDemo)+0x53);
        CALL(SwapAndDisplayVgaPage,G(RunScriptedDemo)+0x56);
        CALL(TestAllDemoScriptsFinished,G(RunScriptedDemo)+0x59);
        if(!(r->flags&CF)) {
            CALL(SampleJoystickAxesAndButtons,G(RunScriptedDemo)+0x61);
            if(r->flags&ZF) {
                CALL(PollKeyboardScanChange,G(RunScriptedDemo)+0x69);
                logic(r,r->ax>>8,8); if(!(r->ax>>8)) continue;
                set_al(r,(uint8_t)logic(r,r->ax&0x7f,8));
                sub16(r,(uint8_t)r->ax,0x10,0);
                if((uint8_t)r->ax==0x10) W(DemoExitCode,0xffff);
                else {
                    sub16(r,(uint8_t)r->ax,1,0);
                    W(DemoExitCode,(uint8_t)r->ax==1?1:0);
                }
            } else W(DemoExitCode,0);
        }
        sub16(r,R(ScreenFadeStep),0,0);
        if((int16_t)R(ScreenFadeStep)<0) continue;
        r->ax=0xfffc; W(ScreenFadeStep,r->ax); W(ScreenFadeLevel,add16(r,R(ScreenFadeLevel),r->ax,0));
    }
    return UGH_BUDGET;
}
/* Picture display owns its saved timeout and input result across both fades. */
/* TRANSLATES GAME:ShowPackedPictureAndWait */
EXPORT int c_ShowPackedPictureAndWait(Regs *r) {
    push(r,r->cx); CALL(UnpackPictureAndCopyPalette,G(ShowPackedPictureAndWait)+4);
    CALL(UploadChunkyImageToVgaPlanes,G(ShowPackedPictureAndWait)+7);
    CALL(SwapAndDisplayVgaPage,G(ShowPackedPictureAndWait)+10);
    CALL(FadePaletteIn,G(ShowPackedPictureAndWait)+13); r->cx=pop(r);
    CALL(WaitForInputOrRetraceTimeout,G(ShowPackedPictureAndWait)+17);
    push(r,r->ax); CALL(FadePaletteOut,G(ShowPackedPictureAndWait)+21); r->ax=pop(r);
    set_al(r,(uint8_t)logic(r,r->ax&0x7f,8));
    /* These are byte CMPs; only the final word AND survives as an output. */
    if((uint8_t)r->ax==1) r->ax=1;
    else if((uint8_t)r->ax==0x10) r->ax=0xffff;
    else r->ax=logic(r,0,16);
    logic(r,r->ax,16); return UGH_OK;
}

/* Local far calls construct the original return words; argument cleanup is
 * the following ADD SP and therefore supplies its actual arithmetic flags. */
static int scene_far_call(Regs *r,uint16_t seg,uint16_t off,uint16_t ret) {
    push(r,r->cs); push(r,ret); int st=ugh_dispatch(seg,off,r);
    r->sp=(uint16_t)(r->sp+4); return st;
}
/* Reveal must restore the demo's returned flags after resetting width. */
/* TRANSLATES GAME:PlaySpriteRevealDemo */
EXPORT int c_PlaySpriteRevealDemo(Regs *r) {
    CALL(PrepareAttractMap0,G(PlaySpriteRevealDemo)+3); r->si=D(DemoTable_24DE);
    CALL(RunScriptedDemo,G(PlaySpriteRevealDemo)+9); push(r,r->flags);
    r->bx=logic(r,0,16); W(ActorX32,r->bx);
    CALL(SetDemoRevealSpriteWidth,G(PlaySpriteRevealDemo)+0x13); r->flags=pop(r); return UGH_OK;
}
/* TRANSLATES GAME:PlayPreGameDemo */
EXPORT int c_PlayPreGameDemo(Regs *r) {
    CALL(PrepareAttractMap0,G(PlayPreGameDemo)+3); r->si=D(DemoTable_1792);
    return ugh_dispatch(r->cs,G(RunScriptedDemo),r);
}
/* TRANSLATES GAME:PlayAttractDemo */
EXPORT int c_PlayAttractDemo(Regs *r) {
    CALL(PrepareAttractMap90,G(PlayAttractDemo)+3); r->si=D(DemoTable_1E40);
    return c_RunScriptedDemo(r);
}
/* Completion switches music before entering the actual shared demo tail. */
/* TRANSLATES GAME:PlayGameCompletionDemo */
EXPORT int c_PlayGameCompletionDemo(Regs *r) {
    CALL(PrepareAttractMap0,G(PlayGameCompletionDemo)+3); push(r,0x11);
    int st=scene_far_call(r,UGH_S_C_StopMusicTrack,UGH_O_C_StopMusicTrack,G(PlayGameCompletionDemo)+10);
    if(st) return st;
    r->sp=add16(r,r->sp,2,0); push(r,0xa5); push(r,0); push(r,UGH_S_B3279_ext_3279); push(r,0);
    st=scene_far_call(r,UGH_S_C_StartMusicTrack,UGH_O_C_StartMusicTrack,G(PlayGameCompletionDemo)+0x1d);
    if(st) return st;
    r->sp=add16(r,r->sp,8,0); r->si=D(DemoTable_1020); return ugh_dispatch(r->cs,G(RunScriptedDemo),r);
}
/* Credits count CR/FD as lines, but center every line at a 16-pixel pitch.
 * Timeout flags are saved across fade-out; page sentinel FF returns zero. */
/* TRANSLATES GAME:ShowCreditsPages */
EXPORT int c_ShowCreditsPages(Regs *r) {
    W(WaterYPixels,200); CALL(DuplicateSourcePaletteHalves,G(ShowCreditsPages)+9); r->si=D(Text_091F);
    for(unsigned pages=0;pages<32768;pages++) {
        push(r,r->si); r->cx=40; CALL(WaitRetraceCount,G(ShowCreditsPages)+0x13);
        CALL(ClearAllVgaPlanes,G(ShowCreditsPages)+0x16); CALL(DrawMenuHeaderSprites,G(ShowCreditsPages)+0x19);
        CALL(SaveDrawPageBackground,G(ShowCreditsPages)+0x1c); CALL(SwapAndDisplayVgaPage,G(ShowCreditsPages)+0x1f);
        CALL(RestorePlayfieldBackground,G(ShowCreditsPages)+0x22); r->si=pop(r); r->di=r->si; r->bp=logic(r,0,16);
        if(rd8(r->ds,r->si)==255) { r->ax=logic(r,0,16); return UGH_OK; }
        for(unsigned chars=0;chars<65536;chars++) {
            set_al(r,rd8(r->ds,r->si)); r->si=(uint16_t)(r->si+step(r));
            if((uint8_t)r->ax==0xfd || (uint8_t)r->ax==13) { uint16_t cf=r->flags&CF; r->bp=add16(r,r->bp,1,0); flag(r,CF,cf); continue; }
            if(!(uint8_t)r->ax) break;
            if(chars==65535) return UGH_BUDGET;
        }
        r->bp=(uint16_t)((r->bp+1)<<4); r->cx=sub16(r,144,r->bp,0);
        flag(r,CF,r->cx&1); r->cx>>=1; flag(r,OF,0); szp(r,r->cx,16);
        r->cx=add16(r,r->cx,56,0); r->si=r->di;
        CALL(DrawTextBlock,G(ShowCreditsPages)+0x58); push(r,r->si);
        CALL(SwapAndDisplayVgaPage,G(ShowCreditsPages)+0x5c); CALL(FadePaletteIn,G(ShowCreditsPages)+0x5f);
        r->cx=350; CALL(WaitForInputOrRetraceTimeout,G(ShowCreditsPages)+0x65);
        push(r,r->flags); push(r,r->ax); CALL(FadePaletteOut,G(ShowCreditsPages)+0x6a);
        r->ax=pop(r); r->flags=pop(r); r->si=pop(r);
        if(r->flags&ZF) continue;
        set_al(r,(uint8_t)logic(r,r->ax&0x7f,8));
        if((uint8_t)r->ax==0x10) r->ax=0xffff;
        else if((uint8_t)r->ax==1) r->ax=1;
        else r->ax=0;
        logic(r,r->ax,16); return UGH_OK;
    }
    return UGH_BUDGET;
}
/* Every picture goes through the same actual decompression/drawing/input body.
 * A Q exit transfers to the shared shutdown tail with no fabricated RET. */
/* TRANSLATES GAME:ShowStartupPictures */
EXPORT int c_ShowStartupPictures(Regs *r) {
    r->si=UGH_S_B2D9A_ext_2D9A; r->cx=280; CALL(ShowPackedPictureAndWait,G(ShowStartupPictures)+10);
    if(r->flags&SF) return ugh_dispatch(r->cs,G(loc_4EE6),r);
    if(!(r->flags&ZF)) return UGH_OK;
    r->si=UGH_S_B2BF6_ext_2BF6; r->cx=280; CALL(ShowPackedPictureAndWait,G(ShowStartupPictures)+30);
    if(r->flags&SF) return ugh_dispatch(r->cs,G(loc_4EE6),r);
    if(!(r->flags&ZF)) return UGH_OK;
    r->si=UGH_S_B2F9E_ext_2F9E; r->cx=140; CALL(ShowPackedPictureAndWait,G(ShowStartupPictures)+50);
    if(r->flags&SF) return ugh_dispatch(r->cs,G(loc_4EE6),r);
    if(!(r->flags&ZF)) return UGH_OK;
    r->si=UGH_S_B2FB7_ext_2FB7; r->cx=420; CALL(ShowPackedPictureAndWait,G(ShowStartupPictures)+70);
    if(r->flags&SF) return ugh_dispatch(r->cs,G(loc_4EE6),r);
    return UGH_OK;
}
/* The two enemy layers share their literal drawing body, selected by the
 * original descriptor identity. SI and all live caches remain in original RAM. */
static int draw_enemy_layer(Regs *r,int front) {
    r->si=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        r->ax=RX(EnemyDescriptors,r->si); sub16(r,r->ax,0xffff,0); if(r->ax==0xffff) return UGH_OK;
        sub16(r,r->ax,D(Data_76E4),0); int special=r->ax==D(Data_76E4);
        if(!special) { sub16(r,r->ax,D(Data_76A8),0); special=r->ax==D(Data_76A8); }
        if(special!=front) {
            r->ax=RX(EnemySpriteIds,r->si); sub16(r,r->ax,0xffff,0);
            if(r->ax!=0xffff) {
                r->bx=RX(EnemyDrawX,r->si); r->cx=RX(EnemyDrawY,r->si);
                WX(EnemyPreviousDrawX,r->si,r->bx); WX(EnemyPreviousDrawY,r->si,r->cx);
                r->bx=sar(RX(EnemyX32,r->si),5); WX(EnemyDrawX,r->si,r->bx);
                r->cx=sar(RX(EnemyY32,r->si),5); WX(EnemyDrawY,r->si,r->cx);
                sub16(r,r->cx,192,0);
                if((int16_t)r->cx<192) { CALL(DrawTransparentSprite,G(RunGameFromPassword)+(front?0x302:0x293)); }
            }
        }
        r->si=add16(r,r->si,2,0);
    }
    return UGH_BUDGET;
}
/* Password selection, then the complete erase/input/update/draw loop. The
 * original equality-only player loops and split actor/overlay cache updates
 * are retained. A finite diagnostic guard rejects nonreturning corrupt lists;
 * it supplies no substitute game result. */
/* TRANSLATES GAME:RunGameFromPassword */
EXPORT int c_RunGameFromPassword(Regs *r) {
    r->cx=logic(r,0,16); r->bx=R(PlayerArrayBytes);
    r->si=rd16(r->ds,(uint16_t)(D(PasswordListPointers)-2+r->bx));
next_password:
    r->bx=logic(r,0,16); r->bp=logic(r,0,16);
    for(unsigned chars=0;chars<65536;chars++) {
        set_al(r,rd8(r->ds,r->si)); r->si=(uint16_t)(r->si+step(r)); logic(r,(uint8_t)r->ax,8);
        if(!(uint8_t)r->ax) break;
        if((uint8_t)r->ax==255) { r->cx=logic(r,0,16); goto selected; }
        uint16_t cf=r->flags&CF; r->bx=add16(r,r->bx,1,0); flag(r,CF,cf);
        if((uint8_t)r->ax!=rd8(r->ds,(uint16_t)(D(PasswordCompareBiasedBase)+r->bx))) r->bp=dec16(r,r->bp);
        if(chars==65535) return UGH_BUDGET;
    }
    logic(r,r->bp,16);
    if(!r->bp) {
        for(;;) {
            sub16(r,r->bx,20,0); if(r->bx>=20) goto selected;
            set_al(r,32);
            if(rd8(r->ds,(uint16_t)(D(PasswordEditBuffer)+r->bx))!=32) break;
            uint16_t cf=r->flags&CF; r->bx=add16(r,r->bx,1,0); flag(r,CF,cf);
        }
    }
    { uint16_t cf=r->flags&CF; r->cx=add16(r,r->cx,1,0); flag(r,CF,cf); } goto next_password;
selected:
    W(CurrentLevelIndex,r->cx); CALL(PlayPreGameDemo,G(RunGameFromPassword)+0x50);
    push(r,0x11); int st=scene_far_call(r,UGH_S_C_StopMusicTrack,UGH_O_C_StopMusicTrack,G(RunGameFromPassword)+0x57);
    if(st) return st;
    r->sp=add16(r,r->sp,2,0); CALL(ResetScoreLivesAndMultiplier,G(RunGameFromPassword)+0x5d);
    CALL(BlackenVgaPalette,G(RunGameFromPassword)+0x60);
level:
    CALL(InitializeLevelDisplay,G(RunGameFromPassword)+0x63);
    push(r,0xa5); push(r,0); push(r,UGH_S_B3444_ext_3444); push(r,0);
    st=scene_far_call(r,UGH_S_C_StartMusicTrack,UGH_O_C_StartMusicTrack,G(RunGameFromPassword)+0x73); if(st) return st;
    r->sp=add16(r,r->sp,8,0);
    for(unsigned frames=0;frames<100000;frames++) {
        r->cx=R(ScreenFadeLevel); sub16(r,r->cx,0,0); if((int16_t)r->cx<0) goto faded;
        sub16(r,r->cx,256,0);
        if((int16_t)r->cx<=256) {
            CALL(ScaleAndUploadFadedPalette,G(RunGameFromPassword)+0x91);
            r->cx=add16(r,r->cx,R(ScreenFadeStep),0); W(ScreenFadeLevel,r->cx);
        } else { CALL(WaitNextVerticalRetrace,G(RunGameFromPassword)+0x9e); }
        CALL(RefreshHudAndTimerBar,G(RunGameFromPassword)+0xa1); r->bx=logic(r,0,16);
        do {
            CALL(RestorePlayerBackground,G(RunGameFromPassword)+0xa6);
            r->bx=add16(r,r->bx,2,0); sub16(r,r->bx,R(PlayerArrayBytes),0);
        } while(r->bx!=R(PlayerArrayBytes));
        r->si=logic(r,0,16);
        for(unsigned slots=0;slots<32768;slots++) {
            sub16(r,RX(ActorDescriptors,r->si),0xffff,0); if(r->flags&ZF) break;
            r->ax=RX(ActorSpriteIds,r->si); r->cx=RX(ActorEraseSprite,r->si); WX(ActorEraseSprite,r->si,r->ax);
            sub16(r,r->cx,0xffff,0);
            if(r->cx!=0xffff) {
                r->ax=RX(ActorPreviousDrawX,r->si); r->bx=RX(ActorPreviousDrawY,r->si); sub16(r,r->bx,192,0);
                if((int16_t)r->bx<192) {
                    CALL(RestoreSpriteBackground,G(RunGameFromPassword)+0xe3);
                    r->ax=RX(ActorOverlayOrScriptCallbacks,r->si); r->cx=RX(ActorEraseOverlaySprite,r->si);
                    WX(ActorEraseOverlaySprite,r->si,r->ax); sub16(r,r->cx,0xffff,0);
                    if(r->cx!=0xffff) {
                        r->ax=add16(r,RX(ActorPreviousDrawX,r->si),11,0); r->bx=add16(r,RX(ActorPreviousDrawY,r->si),(uint16_t)-13,0);
                        CALL(RestoreSpriteBackground,G(RunGameFromPassword)+0x108);
                    }
                }
            }
            r->si=add16(r,r->si,2,0); if(slots==32767) return UGH_BUDGET;
        }
        r->si=logic(r,0,16);
        for(unsigned slots=0;slots<32768;slots++) {
            sub16(r,RX(EnemyDescriptors,r->si),0xffff,0); if(r->flags&ZF) break;
            r->ax=RX(EnemySpriteIds,r->si); r->cx=RX(EnemyEraseSprite,r->si); WX(EnemyEraseSprite,r->si,r->ax);
            sub16(r,r->cx,0xffff,0);
            if(r->cx!=0xffff) {
                r->ax=RX(EnemyPreviousDrawX,r->si); r->bx=RX(EnemyPreviousDrawY,r->si);
                CALL(RestoreSpriteBackground,G(RunGameFromPassword)+0x138);
            }
            r->si=add16(r,r->si,2,0); if(slots==32767) return UGH_BUDGET;
        }
        r->si=22;
        do {
            r->ax=RX(FallingItemSprites,r->si); r->cx=RX(FallingItemEraseSprite,r->si); WX(FallingItemEraseSprite,r->si,r->ax);
            sub16(r,r->cx,0xffff,0);
            if(r->cx!=0xffff) {
                r->ax=RX(FallingItemPreviousDrawX,r->si); r->bx=RX(FallingItemPreviousDrawY,r->si);
                CALL(RestoreSpriteBackground,G(RunGameFromPassword)+0x15f);
            }
            r->si=sub16(r,r->si,2,0);
        } while(!(r->flags&SF));
        if(rd8(r->ds,D(LevelRainDirection))) { CALL(RestoreRainBackground,G(RunGameFromPassword)+0x171); }
        CALL(AdvanceWaterSurface,G(RunGameFromPassword)+0x174);
        st=platform_service_point_at(SERVICE_IO,r->cs,G(RunGameFromPassword)+0x174,r); if(st) return st;
        CALL(PollPlayerControls,G(RunGameFromPassword)+0x177);
        if((uint8_t)r->ax==0x19) {
            do { CALL(PollKeyboardScanChange,G(RunGameFromPassword)+0x181); } while((uint8_t)r->ax!=0x99);
            do { CALL(PollKeyboardScanChange,G(RunGameFromPassword)+0x188); } while((uint8_t)r->ax&128);
            do { CALL(PollKeyboardScanChange,G(RunGameFromPassword)+0x18f); } while(!((uint8_t)r->ax&128));
        }
        if((uint8_t)r->ax==1) {
            wr8(r->ds,D(LivesRemaining),0); sub16(r,R(ScreenFadeStep),0,0);
            if((int16_t)R(ScreenFadeStep)>=0) { r->ax=0xfffe; W(ScreenFadeStep,r->ax); W(ScreenFadeLevel,add16(r,R(ScreenFadeLevel),r->ax,0)); }
        }
        sub16(r,R(ScreenFadeLevel),192,0); int move=(int16_t)R(ScreenFadeLevel)>192;
        if(!move) { sub16(r,R(ScreenFadeStep),0,0); move=(int16_t)R(ScreenFadeStep)<=0; }
        if(move) {
            r->bx=logic(r,0,16);
            do { CALL(MovePlayerWithVgaCollisions,G(RunGameFromPassword)+0x1ce); r->bx=add16(r,r->bx,2,0); sub16(r,r->bx,R(PlayerCount),0); } while(r->bx==R(PlayerCount));
        }
        CALL(DispatchActorUpdates,G(RunGameFromPassword)+0x1da); CALL(DispatchEnemyStates,G(RunGameFromPassword)+0x1dd);
        CALL(DispatchFallingItems,G(RunGameFromPassword)+0x1e0); r->si=logic(r,0,16);
        for(unsigned slots=0;slots<32768;slots++) {
            sub16(r,RX(ActorDescriptors,r->si),0xffff,0); if(r->flags&ZF) break;
            r->ax=RX(ActorSpriteIds,r->si); sub16(r,r->ax,0xffff,0);
            if(r->ax!=0xffff) {
                r->bx=RX(ActorPixelX,r->si); r->cx=RX(ActorPixelY,r->si); WX(ActorPreviousDrawX,r->si,r->bx); WX(ActorPreviousDrawY,r->si,r->cx);
                r->bx=sar(RX(ActorX32,r->si),5); WX(ActorPixelX,r->si,r->bx); r->cx=sar(RX(ActorY32,r->si),5); WX(ActorPixelY,r->si,r->cx);
                sub16(r,r->cx,192,0);
                if((int16_t)r->cx<192) { sub16(r,r->cx,(uint16_t)-11,0); if((int16_t)r->cx>-11) { CALL(DrawTransparentSprite,G(RunGameFromPassword)+0x232); } }
            }
            r->si=add16(r,r->si,2,0); if(slots==32767) return UGH_BUDGET;
        }
        st=draw_enemy_layer(r,0); if(st) return st;
        r->bx=logic(r,0,16);
        do { CALL(AnimateAndDrawPlayer,G(RunGameFromPassword)+0x29d); r->bx=add16(r,r->bx,2,0); sub16(r,r->bx,R(PlayerArrayBytes),0); } while(r->bx!=R(PlayerArrayBytes));
        st=draw_enemy_layer(r,1); if(st) return st;
        r->si=22;
        do {
            r->ax=RX(FallingItemSprites,r->si); sub16(r,r->ax,0xffff,0);
            if(r->ax!=0xffff) {
                r->bx=RX(FallingItemDrawX,r->si); r->cx=RX(FallingItemDrawY,r->si); WX(FallingItemPreviousDrawX,r->si,r->bx); WX(FallingItemPreviousDrawY,r->si,r->cx);
                r->bx=sar(RX(FallingItemX,r->si),5); WX(FallingItemDrawX,r->si,r->bx); r->cx=sar(RX(FallingItemY,r->si),5); WX(FallingItemDrawY,r->si,r->cx);
                sub16(r,r->cx,192,0); if((int16_t)r->cx<192) { CALL(DrawTransparentSprite,G(RunGameFromPassword)+0x348); }
            }
            r->si=sub16(r,r->si,2,0);
        } while(!(r->flags&SF));
        r->si=logic(r,0,16);
        for(unsigned slots=0;slots<32768;slots++) {
            sub16(r,RX(ActorDescriptors,r->si),0xffff,0); if(r->flags&ZF) break;
            r->ax=RX(ActorSpriteIds,r->si); sub16(r,r->ax,0xffff,0);
            if(r->ax!=0xffff) {
                r->ax=RX(ActorOverlayOrScriptCallbacks,r->si); sub16(r,r->ax,0xffff,0);
                if(r->ax!=0xffff) {
                    r->bx=add16(r,RX(ActorPixelX,r->si),11,0); r->cx=add16(r,RX(ActorPixelY,r->si),(uint16_t)-13,0);
                    CALL(DrawTransparentSprite,G(RunGameFromPassword)+0x382);
                }
            }
            r->si=add16(r,r->si,2,0); if(slots==32767) return UGH_BUDGET;
        }
        if(rd8(r->ds,D(LevelRainDirection))) { CALL(AdvanceRainParticles,G(RunGameFromPassword)+0x394); CALL(DrawRainParticles,G(RunGameFromPassword)+0x397); }
        CALL(DrawWaterSurface,G(RunGameFromPassword)+0x39a); CALL(SwapAndDisplayVgaPage,G(RunGameFromPassword)+0x39d);
    }
    return UGH_BUDGET;
faded:
    push(r,0x11); st=scene_far_call(r,UGH_S_C_StopMusicTrack,UGH_O_C_StopMusicTrack,G(RunGameFromPassword)+0x3a7); if(st) return st;
    r->sp=add16(r,r->sp,2,0); logic(r,rd8(r->ds,D(LevelCompletionMarker)),8);
    if(!(r->flags&SF)) {
        uint8_t old=rd8(r->ds,D(LivesRemaining)),v=(uint8_t)(old-1); uint16_t cf=r->flags&CF;
        flag(r,OF,old==128); flag(r,AF,((old^v^1)&16)!=0); szp(r,v,8); flag(r,CF,cf); wr8(r->ds,D(LivesRemaining),v);
        if(!v || (r->flags&SF)) return UGH_OK;
        wr8(r->ds,D(ScoreMultiplier),1); goto level;
    }
    r->ax=R(CurrentLevelIndex); { uint16_t cf=r->flags&CF; r->ax=add16(r,r->ax,1,0); flag(r,CF,cf); }
    W(CurrentLevelIndex,r->ax); r->bx=sub16(r,R(PlayerArrayBytes),2,0); sub16(r,r->ax,RX(LevelCountsByPlayerMode,r->bx),0);
    if(r->flags&CF) goto level;
    return UGH_OK;
}

/* DS:SI vector; each header is pixel X,Y,period,near callback. Shifts wrap,
 * and the whole vector is read before ResetSpriteEraseState destroys SI.
 * No array bound or malformed-vector normalization. Out follows AdvanceDemoScripts:
 * BX=sentinel index, SI=FFFF; AX and callback effects flow through. */
/* TRANSLATES GAME:InitializeDemoScripts */
EXPORT int c_InitializeDemoScripts(Regs *r) {
    r->bx=logic(r,0,16);
    for(unsigned budget=0;;budget++) {
        if(budget==32768) return UGH_BUDGET;
        r->di=rd16(r->ds,(uint16_t)(r->bx+r->si));
        sub16(r,r->di,0xffff,0);
        if(r->di==0xffff) break;
        r->ax=rd16(r->ds,r->di);
        WX(ActorPixelX,r->bx,r->ax); WX(ActorPreviousDrawX,r->bx,r->ax);
        r->ax=(uint16_t)(r->ax<<5); WX(ActorX32,r->bx,r->ax);
        r->ax=rd16(r->ds,(uint16_t)(r->di+2));
        WX(ActorPixelY,r->bx,r->ax); WX(ActorPreviousDrawY,r->bx,r->ax);
        r->ax=(uint16_t)(r->ax<<5); WX(ActorY32,r->bx,r->ax);
        r->ax=rd16(r->ds,(uint16_t)(r->di+4)); WX(ActorVerticalOrDemoPeriod,r->bx,r->ax);
        r->ax=rd16(r->ds,(uint16_t)(r->di+6)); WX(ActorOverlayOrScriptCallbacks,r->bx,r->ax);
        r->di=add16(r,r->di,8,0); WX(ActorUpdateOrScriptCursor,r->bx,r->di);
        WX(ActorAnimationCountdowns,r->bx,1);
        r->ax=logic(r,0,16); WX(ActorMotionWaitOrDemoRepeats,r->bx,r->ax); WX(ActorPlatformOrScriptDone,r->bx,r->ax);
        r->bx=add16(r,r->bx,2,0);
    }
    WX(ActorUpdateOrScriptCursor,r->bx,r->di);
    CALL(ResetSpriteEraseState,(uint16_t)(G(InitializeDemoScripts)+0x60));
    return ugh_dispatch(r->cs,G(AdvanceDemoScripts),r);
}

/* DS arrays; visible sprites update both cache generations BEFORE clipping.
 * Only upper signed bounds are checked. AX/BX/CX are the final slot's work
 * values, SI=sentinel index, BP may be changed by the real sprite renderer.
 * DX/DI/DS/ES survive; final CMP sentinel supplies arithmetic flags. */
/* TRANSLATES GAME:DrawDemoSprites */
EXPORT int c_DrawDemoSprites(Regs *r) {
    r->si=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        uint16_t cursor=RX(ActorUpdateOrScriptCursor,r->si);
        sub16(r,cursor,0xffff,0); if(cursor==0xffff) return UGH_OK;
        r->ax=RX(ActorSpriteIds,r->si); sub16(r,r->ax,0x7fff,0);
        if(r->ax!=0x7fff) {
            r->bx=RX(ActorPixelX,r->si); r->cx=RX(ActorPixelY,r->si);
            WX(ActorPreviousDrawX,r->si,r->bx); WX(ActorPreviousDrawY,r->si,r->cx);
            r->bx=sar(RX(ActorX32,r->si),5); WX(ActorPixelX,r->si,r->bx);
            r->cx=sar(RX(ActorY32,r->si),5); WX(ActorPixelY,r->si,r->cx);
            sub16(r,r->bx,320,0);
            if((int16_t)r->bx<320) {
                sub16(r,r->cx,192,0);
                if((int16_t)r->cx<192) { CALL(DrawTransparentSprite,(uint16_t)(G(DrawDemoSprites)+0x53)); }
            }
        }
        r->si=add16(r,r->si,2,0);
    }
    return UGH_BUDGET;
}

/* Keyboard-mode action words retain their stale high bytes. Joystick words
 * are cleared then decremented to FFFF; signed inclusive thresholds apply.
 * The original JE at 108B visits slot 1 only when PlayerCount==2.
 * Out AL scan/AH XOR change; BX/SI and joystick scratch outputs flow through;
 * final flags are CMP BX,PlayerCount, DX/DI/BP survive without sampling. */
/* TRANSLATES GAME:PollPlayerControls */
EXPORT int c_PollPlayerControls(Regs *r) {
    CALL(PollKeyboardScanChange,(uint16_t)(G(PollPlayerControls)+3));
    logic(r,R(PlayerOneControlMode),16);
    if((int16_t)R(PlayerOneControlMode)>=0) { CALL(SampleJoystickAxesAndButtons,(uint16_t)(G(PollPlayerControls)+0x26)); }
    else {
        logic(r,R(PlayerTwoControlMode),16);
        if((int16_t)R(PlayerTwoControlMode)>=0) {
            sub16(r,R(PlayerCount),2,0);
            if(R(PlayerCount)==2) { CALL(SampleJoystickAxesAndButtons,(uint16_t)(G(PollPlayerControls)+0x26)); }
        }
    }
    r->bx=logic(r,0,16);
    do {
        r->si=(uint16_t)(RX(PlayerOneControlMode,r->bx)<<1);
        logic(r,r->si,16);
        if((int16_t)r->si>=0) {
            r->ax=logic(r,0,16);
            WX(PlayerUpInput,r->bx,0); WX(PlayerDownInput,r->bx,0);
            WX(PlayerLeftInput,r->bx,0); WX(PlayerRightInput,r->bx,0); WX(PlayerActionInput,r->bx,0);
            r->ax=RX(FirstJoystickXCount,r->si);
            if((int16_t)r->ax<=(int16_t)RX(JoystickLeftThresholds,r->si)) WX(PlayerLeftInput,r->bx,0xffff);
            else if((int16_t)r->ax>=(int16_t)RX(JoystickRightThresholds,r->si)) WX(PlayerRightInput,r->bx,0xffff);
            r->ax=RX(FirstJoystickYCount,r->si);
            if((int16_t)r->ax<=(int16_t)RX(JoystickUpThresholds,r->si)) WX(PlayerUpInput,r->bx,0xffff);
            else if((int16_t)r->ax>=(int16_t)RX(JoystickDownThresholds,r->si)) WX(PlayerDownInput,r->bx,0xffff);
            if(RX(JoystickButtonBits,r->si)) WX(PlayerActionInput,r->bx,0xffff);
        }
        r->bx=add16(r,r->bx,2,0); sub16(r,r->bx,R(PlayerCount),0);
    } while(r->bx==R(PlayerCount));
    set_al(r,rd8(r->ds,D(CurrentKeyboardScanCode)));
    set_ah(r,rd8(r->ds,D(KeyboardScanCodeChangeBits)));
    return UGH_OK;
}

/* Compute the same signed IMUL low/high words and the wrapped plane address.
 * The second invocation leaves DX=IMUL high word, AFTER the port selection. */
static void collision_address(Regs *r) {
    r->ax=RX(PlayerYPixels,r->bx);
    int32_t product=(int32_t)(int16_t)r->ax*(int16_t)R(VgaRowStrideBytes);
    r->ax=(uint16_t)product; r->dx=(uint16_t)((uint32_t)product>>16);
    r->si=RX(PlayerPixelX,r->bx); r->si=(uint16_t)(r->si+5); r->si=sar(r->si,2);
    r->ax=(uint16_t)(r->ax+r->si);
    r->si=rd16(r->cs,G(BackgroundPagePointer));
    r->es=rd16(r->cs,(uint16_t)(G(BackgroundPagePointer)+2));
    r->si=(uint16_t)(r->si+r->ax);
}
static void select_collision_plane(Regs *r) {
    r->dx=0x3ce; set_al(r,4); platform_out(r->dx,1,(uint8_t)r->ax);
    r->dx=(uint16_t)(r->dx+1);
    r->ax=(uint16_t)(RX(PlayerPixelX,r->bx)+0x25); r->ax=logic(r,r->ax&3,16);
}
static uint16_t limit_velocity(uint16_t v) {
    if((int16_t)v < -6144) return 0xe800;
    if((int16_t)v > 6144) return 0x1800;
    return v;
}
static void reflect_velocity(Regs *r,uint16_t offset) {
    r->ax=(uint16_t)(0-rd16(r->ds,offset)); r->ax=sar(r->ax,1);
    wr16(r->ds,offset,r->ax); r->ax=(uint16_t)(r->ax<<1);
    if((int16_t)r->ax<0) r->ax=(uint16_t)(0-r->ax);
}

/* Player BX is preserved. Out AX/CX/DX/SI/DI/BP/ES and arithmetic flags
 * follow the original instruction ordering. VGA read-map selection/latches
 * and ordered ports are observable. No host pixel cache exists.
 * Left/up scans intentionally re-read one address; right/down scans advance.
 * Impact comparisons, clamps and SAR rounding are signed with word wrapping.
 * There is no timer saturation, velocity friction or lower-level clipping. */
/* TRANSLATES GAME:MovePlayerWithVgaCollisions */
EXPORT int c_MovePlayerWithVgaCollisions(Regs *r) {
    W(LevelTimer,dec16(r,R(LevelTimer)));
    r->ax=logic(r,0,16); WX(PlayerImpactMagnitude,r->bx,0); WX(PlayerThrustAnimationRate,r->bx,0);
    r->cx=(uint16_t)(RX(PlayerYPixels,r->bx)-R(WaterYPixels)+18);
    if((int16_t)r->cx>0) r->cx=(uint16_t)((r->cx&255)|0x100);
    if((int16_t)RX(PlayerPlatformIndices,r->bx)<0) {
        if((int8_t)(r->cx>>8)<0) {
            set_al(r,rd8(r->ds,D(LevelRainDirection)));
            if((uint8_t)r->ax) {
                set_ah(r,0); r->ax=(uint16_t)((((r->ax-1)*2)-1)*32);
                WX(PlayerHorizontalVelocities,r->bx,RX(PlayerHorizontalVelocities,r->bx)+r->ax);
                r->ax=sar(r->ax,1); if((int16_t)r->ax<0) r->ax=(uint16_t)(0-r->ax);
                WX(PlayerVerticalVelocities,r->bx,RX(PlayerVerticalVelocities,r->bx)+r->ax);
            }
        }
        r->ax=RX(PlayerHorizontalVelocities,r->bx);
        if(RX(PlayerLeftInput,r->bx)) {
            r->ax=(uint16_t)(r->ax-63); WX(PlayerThrustAnimationRate,r->bx,RX(PlayerThrustAnimationRate,r->bx)+63);
        } else if(RX(PlayerRightInput,r->bx)) {
            r->ax=(uint16_t)(r->ax+63); WX(PlayerThrustAnimationRate,r->bx,RX(PlayerThrustAnimationRate,r->bx)+63);
        }
        r->ax=limit_velocity(r->ax); WX(PlayerHorizontalVelocities,r->bx,r->ax);
        r->ax=(uint16_t)(sar(r->ax,6)+RX(PlayerX32,r->bx));
        if((int16_t)r->ax<-512) { r->ax=0xfe00; WX(PlayerHorizontalVelocities,r->bx,0); }
        else if((int16_t)r->ax>9728) { r->ax=0x2600; WX(PlayerHorizontalVelocities,r->bx,0); }
        r->di=r->ax; push(r,r->cx);
        collision_address(r); select_collision_plane(r);
        r->cx=(uint16_t)((r->cx&0xff00)|(uint8_t)r->ax); platform_out(r->dx,1,(uint8_t)r->ax);
        r->bp=r->di; r->ax=sar(r->di,5);
        if(r->ax!=RX(PlayerPixelX,r->bx)) {
            r->bp=RX(PlayerX32,r->bx);
            int hit=0;
            if((int16_t)r->di<=(int16_t)r->bp) {
                uint8_t cl=(uint8_t)((uint8_t)r->cx-1);
                if((int8_t)cl<0) { cl&=3; r->si=(uint16_t)(r->si-1); }
                r->cx=(uint16_t)((r->cx&0xff00)|cl); set_al(r,cl); platform_out(r->dx,1,cl);
                do {
                    CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x12f));
                    if(r->flags&SF) { r->bp=(uint16_t)((r->bp&0xffe0)+32); hit=1; break; }
                    r->bp=(uint16_t)(r->bp-32);
                } while((int16_t)r->bp>(int16_t)r->di);
            } else {
                do {
                    uint8_t cl=(uint8_t)((uint8_t)r->cx+1);
                    if(cl>=4) { cl&=3; r->si=(uint16_t)(r->si+1); }
                    r->cx=(uint16_t)((r->cx&0xff00)|cl); set_al(r,cl); platform_out(r->dx,1,cl);
                    CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x159));
                    if(r->flags&SF) { r->bp&=0xffe0; hit=1; break; }
                    r->bp=(uint16_t)(r->bp+32);
                } while((int16_t)r->bp<(int16_t)r->di);
            }
            if(hit) {
                reflect_velocity(r,(uint16_t)(D(PlayerHorizontalVelocities)+r->bx));
                WX(PlayerImpactMagnitude,r->bx,r->ax);
            } else r->bp=r->di;
        }
        WX(PlayerX32,r->bx,r->bp); r->bp=sar(r->bp,5); WX(PlayerPixelX,r->bx,r->bp);
        r->cx=pop(r);
    }
    r->ax=RX(PlayerVerticalVelocities,r->bx);
    int8_t water_state=(int8_t)(r->cx>>8);
    if(water_state>0) {
        W(LevelTimer,R(LevelTimer)-2);
        if((int16_t)r->ax>0) r->ax=(uint16_t)(r->ax-193);
        else { r->ax=(uint16_t)(r->ax-21); WX(PlayerPlatformIndices,r->bx,0xffff); }
    } else {
        if(water_state<0 && (int16_t)RX(PlayerPlatformIndices,r->bx)<0) {
            r->ax=(uint16_t)(r->ax+27); W(LevelTimer,R(LevelTimer)-2);
            if(RX(PlayerDownInput,r->bx)) {
                r->ax=(uint16_t)(r->ax+70); WX(PlayerThrustAnimationRate,r->bx,RX(PlayerThrustAnimationRate,r->bx)+90);
                goto vertical_limit;
            }
        }
        if(RX(PlayerUpInput,r->bx)) {
            W(LevelTimer,R(LevelTimer)-3); r->ax=(uint16_t)(r->ax-70);
            WX(PlayerThrustAnimationRate,r->bx,RX(PlayerThrustAnimationRate,r->bx)+90);
            WX(PlayerPlatformIndices,r->bx,0xffff);
        }
    }
vertical_limit:
    r->ax=limit_velocity(r->ax); WX(PlayerVerticalVelocities,r->bx,r->ax);
    r->ax=(uint16_t)(sar(r->ax,6)+RX(PlayerY32,r->bx));
    if((int16_t)r->ax<-608) { r->ax=0xfda0; WX(PlayerVerticalVelocities,r->bx,0); }
    else if((int16_t)r->ax>6112) { r->ax=0x17e0; WX(PlayerVerticalVelocities,r->bx,0); }
    if(water_state>0) {
        r->dx=(uint16_t)(sar(r->ax,5)-R(WaterYPixels)+18);
        if((int16_t)r->dx<=0) {
            WX(PlayerVerticalVelocities,r->bx,0); r->ax=(uint16_t)((R(WaterYPixels)<<5)-0x240);
        }
    }
    r->di=r->ax; select_collision_plane(r); platform_out(r->dx,1,(uint8_t)r->ax);
    collision_address(r); r->bp=r->di; r->ax=sar(r->di,5);
    if(r->ax!=RX(PlayerYPixels,r->bx)) {
        r->bp=RX(PlayerY32,r->bx); int hit=0;
        if((int16_t)r->di<=(int16_t)r->bp) {
            r->si=(uint16_t)(r->si-0x60);
            do {
                CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x2d4));
                if(r->flags&SF) { r->bp=(uint16_t)((r->bp&0xffe0)+32); hit=1; break; }
                r->bp=(uint16_t)(r->bp-32);
            } while((int16_t)r->bp>(int16_t)r->di);
        } else {
            do {
                r->si=(uint16_t)(r->si+0x60);
                CALL(SamplePlayerCollisionPixels,(uint16_t)(G(MovePlayerWithVgaCollisions)+0x2f1));
                if(r->flags&SF) { r->bp&=0xffe0; hit=1; break; }
                r->bp=(uint16_t)(r->bp+32);
            } while((int16_t)r->bp<(int16_t)r->di);
        }
        if(hit) {
            reflect_velocity(r,(uint16_t)(D(PlayerVerticalVelocities)+r->bx));
            if((int16_t)r->ax>(int16_t)RX(PlayerImpactMagnitude,r->bx)) WX(PlayerImpactMagnitude,r->bx,r->ax);
            if((int16_t)RX(PlayerVerticalVelocities,r->bx)<0) {
                r->ax=RX(PlayerImpactMagnitude,r->bx); r->si=(uint16_t)(R(SelectedDifficulty)<<1);
                if((int16_t)r->ax<(int16_t)RX(PlayerImpactLimits,r->si)) {
                    r->si=0; r->ax=(uint16_t)(sar(r->bp,5)+20);
                    for(unsigned budget=0;;budget++) {
                        if(budget==32768) return UGH_BUDGET;
                        if((int16_t)RX(PlatformLeftEdges,r->si)<0) break;
                        if(RX(PlatformHeights,r->si)==r->ax) {
                            r->cx=(uint16_t)(RX(PlayerPixelX,r->bx)+16);
                            if((int16_t)r->cx>=(int16_t)RX(PlatformLeftEdges,r->si) &&
                               (int16_t)r->cx<=(int16_t)RX(PlatformRightEdges,r->si)) {
                                r->si>>=1; WX(PlayerPlatformIndices,r->bx,r->si); r->ax=logic(r,0,16);
                                WX(PlayerHorizontalVelocities,r->bx,0); WX(PlayerVerticalVelocities,r->bx,0); break;
                            }
                        }
                        r->si=(uint16_t)(r->si+2);
                    }
                }
            }
        } else r->bp=r->di;
    }
    WX(PlayerY32,r->bx,r->bp); r->bp=sar(r->bp,5); WX(PlayerYPixels,r->bx,r->bp);
    r->ax=RX(PlayerImpactMagnitude,r->bx); r->si=(uint16_t)(R(SelectedDifficulty)<<1);
    sub16(r,r->ax,RX(PlayerImpactLimits,r->si),0);
    if((int16_t)r->ax>=(int16_t)RX(PlayerImpactLimits,r->si)) {
        sub16(r,R(ScreenFadeStep),0,0);
        if((int16_t)R(ScreenFadeStep)>=0) {
            r->ax=0xfffe; W(ScreenFadeStep,r->ax); W(ScreenFadeLevel,add16(r,R(ScreenFadeLevel),r->ax,0));
        }
    }
    return UGH_OK;
}
