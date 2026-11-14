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

EXPORT int actor_render_session_GAME_ERASE(Regs *r) {r->si=logic(r,0,16);for(unsigned slots=0;slots<32768;slots++) {
            sub16(r,RX(ActorDescriptors,r->si),0xffff,0); if(r->flags&ZF) break;
{RenderPlan plan;ar_open(r,&plan,ACTOR_RENDER_GAME_ERASE);

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
ar_finish(r,&plan);}

            r->si=add16(r,r->si,2,0); if(slots==32767) return UGH_BUDGET;
        }return UGH_OK;}
EXPORT int actor_render_session_GAME_DRAW(Regs *r) {r->si=logic(r,0,16);for(unsigned slots=0;slots<32768;slots++) {
            sub16(r,RX(ActorDescriptors,r->si),0xffff,0); if(r->flags&ZF) break;
{RenderPlan plan;ar_open(r,&plan,ACTOR_RENDER_GAME_DRAW);

            r->ax=RX(ActorSpriteIds,r->si); sub16(r,r->ax,0xffff,0);
            if(r->ax!=0xffff) {
                r->bx=RX(ActorPixelX,r->si); r->cx=RX(ActorPixelY,r->si); ar_write(r,&plan,(uint16_t)(D(ActorPreviousDrawX)+r->si),r->bx); ar_write(r,&plan,(uint16_t)(D(ActorPreviousDrawY)+r->si),r->cx);
                r->bx=sar(RX(ActorX32,r->si),5); ar_write(r,&plan,(uint16_t)(D(ActorPixelX)+r->si),r->bx); r->cx=sar(RX(ActorY32,r->si),5); ar_write(r,&plan,(uint16_t)(D(ActorPixelY)+r->si),r->cx);
                sub16(r,r->cx,192,0);
                if((int16_t)r->cx<192) { sub16(r,r->cx,(uint16_t)-11,0); if((int16_t)r->cx>-11) { AR_CALL(DrawTransparentSprite,G(RunGameFromPassword)+0x232); } }
            }
ar_finish(r,&plan);}

            r->si=add16(r,r->si,2,0); if(slots==32767) return UGH_BUDGET;
        }return UGH_OK;}
EXPORT int actor_render_session_GAME_OVERLAY(Regs *r) {r->si=logic(r,0,16);for(unsigned slots=0;slots<32768;slots++) {
            sub16(r,RX(ActorDescriptors,r->si),0xffff,0); if(r->flags&ZF) break;
{RenderPlan plan;ar_open(r,&plan,ACTOR_RENDER_GAME_OVERLAY);

            r->ax=RX(ActorSpriteIds,r->si); sub16(r,r->ax,0xffff,0);
            if(r->ax!=0xffff) {
                r->ax=RX(ActorOverlayOrScriptCallbacks,r->si); sub16(r,r->ax,0xffff,0);
                if(r->ax!=0xffff) {
                    r->bx=add16(r,RX(ActorPixelX,r->si),11,0); r->cx=add16(r,RX(ActorPixelY,r->si),(uint16_t)-13,0);
                    AR_CALL(DrawTransparentSprite,G(RunGameFromPassword)+0x382);
                }
            }
ar_finish(r,&plan);}

            r->si=add16(r,r->si,2,0); if(slots==32767) return UGH_BUDGET;
        }return UGH_OK;}
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

