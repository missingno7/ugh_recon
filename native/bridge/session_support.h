#ifndef SESSION_SUPPORT_H
#define SESSION_SUPPORT_H
#include "platform.h"
#include "../session.h"
#include "session_actor_render.h"
#include <stdlib.h>

static void sq_require(int c){if(!c)abort();}
static uint16_t sq_word(uint16_t native_value,uint16_t literal){sq_require(native_value==literal);return native_value;}
static int sq_bool(int native_value,int literal){sq_require(!!native_value==!!literal);return !!native_value;}
static SessionWorld sq_world(Regs *r,SessionPhase phase){
    SessionWorld w;
    w.fade_level=rd16(r->ds,D(ScreenFadeLevel));w.fade_rate=rd16(r->ds,D(ScreenFadeStep));w.palette_reply=r->cx;
    w.player_bytes=rd16(r->ds,D(PlayerArrayBytes));w.player_count=rd16(r->ds,D(PlayerCount));
    w.level=rd16(r->ds,D(CurrentLevelIndex));w.level_limit=0;
    if(phase==SP_TEST_LEVEL_LIMIT)w.level_limit=rd16(r->ds,(uint16_t)(D(LevelCountsByPlayerMode)+(uint16_t)(w.player_bytes-2u)));
    w.password_reply=r->cx;w.lives=rd8(r->ds,D(LivesRemaining));w.completion=rd8(r->ds,D(LevelCompletionMarker));
    w.rain=rd8(r->ds,D(LevelRainDirection));w.scan=(uint8_t)r->ax;return w;
}
typedef struct SessionLayerPlan {SessionRenderResult result;uint16_t index;unsigned stores,requests;} SessionLayerPlan;
static SessionRenderView sq_layer_view(Regs *r,uint16_t index,int items){
    SessionRenderView v;
    v.sprite=rd16(r->ds,(uint16_t)((items?D(FallingItemSprites):D(EnemySpriteIds))+index));
    v.erase_sprite=rd16(r->ds,(uint16_t)((items?D(FallingItemEraseSprite):D(EnemyEraseSprite))+index));
    v.pixel_x=rd16(r->ds,(uint16_t)((items?D(FallingItemDrawX):D(EnemyDrawX))+index));
    v.pixel_y=rd16(r->ds,(uint16_t)((items?D(FallingItemDrawY):D(EnemyDrawY))+index));
    v.previous_x=rd16(r->ds,(uint16_t)((items?D(FallingItemPreviousDrawX):D(EnemyPreviousDrawX))+index));
    v.previous_y=rd16(r->ds,(uint16_t)((items?D(FallingItemPreviousDrawY):D(EnemyPreviousDrawY))+index));
    v.position.x32=rd16(r->ds,(uint16_t)((items?D(FallingItemX):D(EnemyX32))+index));
    v.position.y32=rd16(r->ds,(uint16_t)((items?D(FallingItemY):D(EnemyY32))+index));return v;
}
static SessionLayerPlan sq_layer_open(Regs *r,int items,int erase,int enabled){
    SessionLayerPlan p;p.index=r->si;p.stores=p.requests=0;SessionRenderView v=sq_layer_view(r,p.index,items);
    p.result=erase?session_erase_layer(v):session_draw_layer(v,(uint8_t)enabled);return p;
}
static void sq_layer_store(Regs *r,SessionLayerPlan *p,int items,unsigned field,uint16_t old){
    uint16_t value,base;
    if(field==0){sq_require(p->result.store_erase && !p->stores);value=p->result.erase_sprite;base=items?D(FallingItemEraseSprite):D(EnemyEraseSprite);}
    else {
        sq_require(p->result.store_position && p->stores==field-1u);
        if(field==1){value=p->result.previous_x;base=items?D(FallingItemPreviousDrawX):D(EnemyPreviousDrawX);}
        else if(field==2){value=p->result.previous_y;base=items?D(FallingItemPreviousDrawY):D(EnemyPreviousDrawY);}
        else if(field==3){value=p->result.pixel_x;base=items?D(FallingItemDrawX):D(EnemyDrawX);}
        else {sq_require(field==4);value=p->result.pixel_y;base=items?D(FallingItemDrawY):D(EnemyDrawY);}
    }
    sq_require(r->si==p->index);wr16(r->ds,(uint16_t)(base+p->index),sq_word(value,old));p->stores++;
}
static void sq_layer_request(Regs *r,SessionLayerPlan *p,int restore){
    sq_require(!p->requests && (restore?p->result.restore:p->result.draw));
    if(restore){r->cx=sq_word(p->result.sprite,r->cx);r->ax=sq_word(p->result.x,r->ax);r->bx=sq_word(p->result.y,r->bx);}
    else {r->ax=sq_word(p->result.sprite,r->ax);r->bx=sq_word(p->result.x,r->bx);r->cx=sq_word(p->result.y,r->cx);}
    p->requests++;
}
static void sq_layer_finish(SessionLayerPlan *p){sq_require(p->stores==(p->result.store_erase?1u:p->result.store_position?4u:0u) && p->requests==(unsigned)(p->result.draw || p->result.restore));}
#endif
