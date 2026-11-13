/* Actor history decisions are native; the measured machine shell and pixel
 * services remain here. Generated shells are checked against unchanged L1. */
#include "platform.h"
#include "../actor_render.h"
#include <stdlib.h>

#define R(n) rd16(r->ds,D(n))
#define W(n,v) wr16(r->ds,D(n),(uint16_t)(v))
#define RX(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define WX(n,i,v) wr16(r->ds,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define CALL(n,ret) do { int status=ugh_call_near(G(n),ret,r); if(status) return status; } while(0)
#define AR_CALL(n,ret) do { ar_request(r,&plan,G(n)); int status=ugh_call_near(G(n),ret,r); if(status) return status; } while(0)

typedef struct RenderPlan {
    ActorRenderStorage storage;
    ActorRenderInput input;
    ActorRenderHistory published;
    uint16_t published_sprite;
    ActorRenderResult result;
    size_t consumed;
    uint16_t index;
    int active;
} RenderPlan;
static void ar_require(int condition) { if(!condition) abort(); }
static uint16_t ar_address(ActorRenderField field) {
    switch(field) {
    case ACTOR_RENDER_PIXEL_X:return D(ActorPixelX);
    case ACTOR_RENDER_PIXEL_Y:return D(ActorPixelY);
    case ACTOR_RENDER_PREVIOUS_X:return D(ActorPreviousDrawX);
    case ACTOR_RENDER_PREVIOUS_Y:return D(ActorPreviousDrawY);
    case ACTOR_RENDER_ERASE_SPRITE:return D(ActorEraseSprite);
    case ACTOR_RENDER_ERASE_OVERLAY:return D(ActorEraseOverlaySprite);
    case ACTOR_RENDER_CURRENT_SPRITE:return D(ActorSpriteIds);
    }
    ar_require(0);return 0;
}
static ActorRenderHistory ar_history(Regs *r,uint16_t index) {
    ActorRenderHistory value;
    value.pixel_x=RX(ActorPixelX,index);value.pixel_y=RX(ActorPixelY,index);
    value.previous_x=RX(ActorPreviousDrawX,index);value.previous_y=RX(ActorPreviousDrawY,index);
    value.erase_sprite=RX(ActorEraseSprite,index);value.erase_overlay_sprite=RX(ActorEraseOverlaySprite,index);
    return value;
}
static void ar_open(Regs *r,RenderPlan *plan,ActorRenderOperation operation) {
    *plan=(RenderPlan){0};plan->index=r->si;
    /* Invalid/corrupt or dynamic segment fixtures retain the actual L1 shell.
     * No partial native publication occurs on this compatibility path. */
    plan->active=r->ds==DATA_SEG && r->cs==GAME_SEG && !(r->si&1u) && r->si<32;
    if(!plan->active) return;
    plan->published=ar_history(r,r->si);plan->storage.slots[r->si/2]=plan->published;
    plan->input.position.x32=RX(ActorX32,r->si);plan->input.position.y32=RX(ActorY32,r->si);
    plan->input.sprite=RX(ActorSpriteIds,r->si);plan->input.overlay_sprite=RX(ActorOverlayOrScriptCallbacks,r->si);
    plan->published_sprite=plan->input.sprite;
    plan->result=actor_render_apply(operation,&plan->storage,r->si/2,&plan->input);
}
static ActorRenderEvent ar_next(RenderPlan *plan,ActorRenderEventKind kind) {
    ar_require(plan->consumed<plan->result.count && plan->result.count<=5);
    ActorRenderEvent event=plan->result.events[plan->consumed++];
    ar_require(event.kind==kind);return event;
}
static int ar_equal(ActorRenderHistory a,ActorRenderHistory b) {
    return a.pixel_x==b.pixel_x && a.pixel_y==b.pixel_y &&
        a.previous_x==b.previous_x && a.previous_y==b.previous_y &&
        a.erase_sprite==b.erase_sprite && a.erase_overlay_sprite==b.erase_overlay_sprite;
}
static void ar_projection(Regs *r,RenderPlan *plan) {
#ifdef ACTOR_VERIFY
    ar_require(ar_equal(ar_history(r,plan->index),plan->published));
    ar_require(RX(ActorSpriteIds,plan->index)==plan->published_sprite);
#else
    (void)r;(void)plan;
#endif
}
static void ar_write(Regs *r,RenderPlan *plan,uint16_t address,uint16_t expected) {
    if(!plan->active) {wr16(r->ds,address,expected);return;}
    ActorRenderEvent event=ar_next(plan,ACTOR_RENDER_STORE);
    ar_require(address==(uint16_t)(ar_address(event.field)+plan->index) && event.value==expected);
    switch(event.field) {
    case ACTOR_RENDER_PIXEL_X:plan->published.pixel_x=event.value;break;
    case ACTOR_RENDER_PIXEL_Y:plan->published.pixel_y=event.value;break;
    case ACTOR_RENDER_PREVIOUS_X:plan->published.previous_x=event.value;break;
    case ACTOR_RENDER_PREVIOUS_Y:plan->published.previous_y=event.value;break;
    case ACTOR_RENDER_ERASE_SPRITE:plan->published.erase_sprite=event.value;break;
    case ACTOR_RENDER_ERASE_OVERLAY:plan->published.erase_overlay_sprite=event.value;break;
    case ACTOR_RENDER_CURRENT_SPRITE:plan->published_sprite=event.value;break;
    }
    wr16(r->ds,address,event.value);
    ar_projection(r,plan);
}
static void ar_request(Regs *r,RenderPlan *plan,uint16_t target) {
    if(!plan->active) return;
    int restore=target==G(RestoreSpriteBackground);
    ar_require(restore || target==G(DrawTransparentSprite));
    ActorRenderEvent event=ar_next(plan,restore?ACTOR_RENDER_RESTORE:ACTOR_RENDER_DRAW);
    ar_require(event.sprite==(restore?r->cx:r->ax));
    ar_require(event.x==(restore?r->ax:r->bx) && event.y==(restore?r->bx:r->cx));
    ar_projection(r,plan);
    /* The platform receives the native request's actual values. */
    if(restore) {r->ax=event.x;r->bx=event.y;r->cx=event.sprite;}
    else {r->ax=event.sprite;r->bx=event.x;r->cx=event.y;}
}
static void ar_finish(Regs *r,RenderPlan *plan) {
    if(!plan->active) return;
    ar_require(plan->consumed==plan->result.count);
    ar_require(ar_equal(plan->published,plan->storage.slots[plan->index/2]));
    ar_projection(r,plan);
}

/* BEGIN CHECKED L1 SHELLS */
static uint16_t sar(uint16_t v,unsigned n) {
    return (uint16_t)((v>>n)|((v&0x8000u) ? (0xffffu<<(16-n)) : 0));
}

static void push(Regs *r,uint16_t v) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v); }

static int scene_far_call(Regs *r,uint16_t seg,uint16_t off,uint16_t ret) {
    push(r,r->cs); push(r,ret); int st=ugh_dispatch(seg,off,r);
    r->sp=(uint16_t)(r->sp+4); return st;
}

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
        { RenderPlan plan; ar_open(r,&plan,ACTOR_RENDER_GAME_ERASE);

            r->ax=RX(ActorSpriteIds,r->si); r->cx=RX(ActorEraseSprite,r->si); ar_write(r,&plan,(uint16_t)(D(ActorEraseSprite)+r->si),r->ax);
            sub16(r,r->cx,0xffff,0);
            if(r->cx!=0xffff) {
                r->ax=RX(ActorPreviousDrawX,r->si); r->bx=RX(ActorPreviousDrawY,r->si); sub16(r,r->bx,192,0);
                if((int16_t)r->bx<192) {
                    AR_CALL(RestoreSpriteBackground,G(RunGameFromPassword)+0xe3);
                    r->ax=RX(ActorOverlayOrScriptCallbacks,r->si); r->cx=RX(ActorEraseOverlaySprite,r->si);
                    ar_write(r,&plan,(uint16_t)(D(ActorEraseOverlaySprite)+r->si),r->ax); sub16(r,r->cx,0xffff,0);
                    if(r->cx!=0xffff) {
                        r->ax=add16(r,RX(ActorPreviousDrawX,r->si),11,0); r->bx=add16(r,RX(ActorPreviousDrawY,r->si),(uint16_t)-13,0);
                        AR_CALL(RestoreSpriteBackground,G(RunGameFromPassword)+0x108);
                    }
                }
            }
          ar_finish(r,&plan); }

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
        { RenderPlan plan; ar_open(r,&plan,ACTOR_RENDER_GAME_DRAW);

            r->ax=RX(ActorSpriteIds,r->si); sub16(r,r->ax,0xffff,0);
            if(r->ax!=0xffff) {
                r->bx=RX(ActorPixelX,r->si); r->cx=RX(ActorPixelY,r->si); ar_write(r,&plan,(uint16_t)(D(ActorPreviousDrawX)+r->si),r->bx); ar_write(r,&plan,(uint16_t)(D(ActorPreviousDrawY)+r->si),r->cx);
                r->bx=sar(RX(ActorX32,r->si),5); ar_write(r,&plan,(uint16_t)(D(ActorPixelX)+r->si),r->bx); r->cx=sar(RX(ActorY32,r->si),5); ar_write(r,&plan,(uint16_t)(D(ActorPixelY)+r->si),r->cx);
                sub16(r,r->cx,192,0);
                if((int16_t)r->cx<192) { sub16(r,r->cx,(uint16_t)-11,0); if((int16_t)r->cx>-11) { AR_CALL(DrawTransparentSprite,G(RunGameFromPassword)+0x232); } }
            }
          ar_finish(r,&plan); }

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
        { RenderPlan plan; ar_open(r,&plan,ACTOR_RENDER_GAME_OVERLAY);

            r->ax=RX(ActorSpriteIds,r->si); sub16(r,r->ax,0xffff,0);
            if(r->ax!=0xffff) {
                r->ax=RX(ActorOverlayOrScriptCallbacks,r->si); sub16(r,r->ax,0xffff,0);
                if(r->ax!=0xffff) {
                    r->bx=add16(r,RX(ActorPixelX,r->si),11,0); r->cx=add16(r,RX(ActorPixelY,r->si),(uint16_t)-13,0);
                    AR_CALL(DrawTransparentSprite,G(RunGameFromPassword)+0x382);
                }
            }
          ar_finish(r,&plan); }

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

EXPORT int c_EraseDemoSprites(Regs *r) {
    r->si=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        sub16(r,RX(ActorUpdateOrScriptCursor,r->si),0xffff,0);
        if(r->flags&ZF) return UGH_OK;

        { RenderPlan plan; ar_open(r,&plan,ACTOR_RENDER_DEMO_ERASE);
        r->ax=RX(ActorSpriteIds,r->si); r->cx=RX(ActorEraseSprite,r->si); ar_write(r,&plan,(uint16_t)(D(ActorEraseSprite)+r->si),r->ax);
        sub16(r,r->cx,0xffff,0);
        if(!(r->flags&ZF)) {
            sub16(r,r->cx,0x7fff,0);
            if(!(r->flags&ZF)) {
                r->ax=RX(ActorPreviousDrawX,r->si); r->bx=RX(ActorPreviousDrawY,r->si);
                AR_CALL(RestoreSpriteBackground,G(EraseDemoSprites)+0x34);
            }
        }

          ar_finish(r,&plan); }
        r->si=add16(r,r->si,2,0);
    }
    return UGH_BUDGET;
}

EXPORT int c_DrawDemoSprites(Regs *r) {
    r->si=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        uint16_t cursor=RX(ActorUpdateOrScriptCursor,r->si);
        sub16(r,cursor,0xffff,0); if(cursor==0xffff) return UGH_OK;

        { RenderPlan plan; ar_open(r,&plan,ACTOR_RENDER_DEMO_DRAW);
        r->ax=RX(ActorSpriteIds,r->si); sub16(r,r->ax,0x7fff,0);
        if(r->ax!=0x7fff) {
            r->bx=RX(ActorPixelX,r->si); r->cx=RX(ActorPixelY,r->si);
            ar_write(r,&plan,(uint16_t)(D(ActorPreviousDrawX)+r->si),r->bx); ar_write(r,&plan,(uint16_t)(D(ActorPreviousDrawY)+r->si),r->cx);
            r->bx=sar(RX(ActorX32,r->si),5); ar_write(r,&plan,(uint16_t)(D(ActorPixelX)+r->si),r->bx);
            r->cx=sar(RX(ActorY32,r->si),5); ar_write(r,&plan,(uint16_t)(D(ActorPixelY)+r->si),r->cx);
            sub16(r,r->bx,320,0);
            if((int16_t)r->bx<320) {
                sub16(r,r->cx,192,0);
                if((int16_t)r->cx<192) { AR_CALL(DrawTransparentSprite,(uint16_t)(G(DrawDemoSprites)+0x53)); }
            }
        }

          ar_finish(r,&plan); }
        r->si=add16(r,r->si,2,0);
    }
    return UGH_BUDGET;
}

EXPORT int c_ResetSpriteEraseState(Regs *r) {
    r->ax=0xffff;
    r->si=8;
    do {
        wr16(r->ds,(uint16_t)(D(EnemySpriteIds)+r->si),r->ax);
        wr16(r->ds,(uint16_t)(D(EnemyEraseSprite)+r->si),r->ax);
        r->si=sub16(r,r->si,2,0);
    } while((int16_t)r->si>=0);
    r->si=30;
    do {

        { RenderPlan plan; ar_open(r,&plan,ACTOR_RENDER_RESET);
        ar_write(r,&plan,(uint16_t)(D(ActorSpriteIds)+r->si),r->ax);
        ar_write(r,&plan,(uint16_t)(D(ActorEraseSprite)+r->si),r->ax);

          ar_finish(r,&plan); }
        r->si=sub16(r,r->si,2,0);
    } while((int16_t)r->si>=0);
    r->si=22;
    do {
        wr16(r->ds,(uint16_t)(D(FallingItemSprites)+r->si),r->ax);
        wr16(r->ds,(uint16_t)(D(FallingItemEraseSprite)+r->si),r->ax);
        r->si=sub16(r,r->si,2,0);
    } while((int16_t)r->si>=0);
    return UGH_OK;
}

