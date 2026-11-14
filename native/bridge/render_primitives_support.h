#ifndef RENDER_PRIMITIVES_SUPPORT_H
#define RENDER_PRIMITIVES_SUPPORT_H
#include "platform.h"
#include "../render_primitives.h"
#include <stdlib.h>

static void rp_require(int condition){if(!condition)abort();}
static uint16_t rp_word(uint16_t native_value,uint16_t literal){rp_require(native_value==literal);return native_value;}
static uint8_t rp_byte(uint8_t native_value,uint8_t literal){rp_require(native_value==literal);return native_value;}
static void rp_draw(Regs *r,RenderDrawRequest e){
    rp_require(e.draw);r->ax=rp_word(e.sprite,r->ax);r->bx=rp_word(e.x,r->bx);r->cx=rp_word(e.y,r->cx);
}
static void rp_rectangle(Regs *r,RenderRectangleSpec e){
    r->ax=rp_word(e.x,r->ax);r->bx=rp_word(e.y,r->bx);r->cx=rp_word(e.width,r->cx);r->dx=rp_word(e.height,r->dx);
}
typedef struct RPAnimation {
    RenderAnimationResult result;
    uint16_t index;
    unsigned stores,draws;
    int active;
} RPAnimation;
static RPAnimation rp_animation_begin(Regs *r){
    RPAnimation p={0};p.index=r->bx;p.active=r->bx<4 && !(r->bx&1);
    if(p.active){
        RenderPlayerAnimation a;
        a.countdown=rd16(r->ds,(uint16_t)(D(PlayerAnimationCountdowns)+p.index));
        a.sprite=rd16(r->ds,(uint16_t)(D(PlayerSpriteIds)+p.index));
        a.cycle_start=rd16(r->ds,(uint16_t)(D(PlayerAnimationCycleStarts)+p.index));
        a.cycle_end=rd16(r->ds,(uint16_t)(D(PlayerAnimationCycleEnds)+p.index));
        a.rate=rd16(r->ds,(uint16_t)(D(PlayerThrustAnimationRate)+p.index));
        a.x=rd16(r->ds,(uint16_t)(D(PlayerPixelX)+p.index));
        a.y=rd16(r->ds,(uint16_t)(D(PlayerYPixels)+p.index));
        p.result=render_player_animation(a);
    }
    return p;
}
static void rp_animation_write(Regs *r,RPAnimation *p,uint16_t field,uint16_t index,uint16_t literal){
    uint16_t value=literal;
    if(p->active){
        rp_require(index==p->index);
        if(p->stores==0){rp_require(field==D(PlayerAnimationCountdowns));value=rp_word(p->result.countdown_first,literal);}
        else if(p->stores==1){rp_require(p->result.advance && field==D(PlayerAnimationCountdowns));value=rp_word(p->result.countdown,literal);}
        else {rp_require(p->stores==2 && p->result.advance && field==D(PlayerSpriteIds));value=rp_word(p->result.sprite,literal);}
        p->stores++;
    }
    wr16(r->ds,(uint16_t)(field+index),value);
    if(p->active)rp_require(rd16(r->ds,(uint16_t)(field+index))==value);
}
static void rp_animation_draw(Regs *r,RPAnimation *p){
    if(p->active){rp_require(p->stores==(p->result.advance?3u:1u) && !p->draws);rp_draw(r,p->result.request);p->draws++;}
}
static void rp_animation_complete(RPAnimation *p){
    if(p->active)rp_require(p->stores==(p->result.advance?3u:1u) && p->draws==p->result.request.draw);
}
typedef struct RPRestorePlayer {RenderDrawRequest request;unsigned consumed;int active;} RPRestorePlayer;
static RPRestorePlayer rp_restore_begin(Regs *r){
    RPRestorePlayer p={0};p.active=r->bx<4 && !(r->bx&1);
    if(p.active){RenderPlayerCache c;
        c.sprite=rd16(r->ds,(uint16_t)(D(PlayerCachedSpriteIds)+r->bx));
        c.x=rd16(r->ds,(uint16_t)(D(PlayerCachedPixelX)+r->bx));
        c.y=rd16(r->ds,(uint16_t)(D(PlayerCachedPixelY)+r->bx));p.request=render_player_restore(c);}
    return p;
}
static void rp_restore_request(Regs *r,RPRestorePlayer *p){
    if(p->active){rp_require(!p->consumed && p->request.draw);r->cx=rp_word(p->request.sprite,r->cx);
        r->ax=rp_word(p->request.x,r->ax);r->bx=rp_word(p->request.y,r->bx);p->consumed++;}
}
static void rp_restore_complete(RPRestorePlayer *p){if(p->active)rp_require(p->consumed==p->request.draw);}
static void rp_cache_write(Regs *r,RenderPlayerCache *cache,uint8_t field,uint16_t index,uint16_t value){
    render_cache_store(cache,field,value);
    uint16_t destination=field==0?D(PlayerCachedSpriteIds):field==1?D(PlayerCachedPixelX):D(PlayerCachedPixelY);
    uint16_t output=field==0?cache->sprite:field==1?cache->x:cache->y;
    rp_require(field<3);wr16(r->ds,(uint16_t)(destination+index),rp_word(output,value));
}
#endif
