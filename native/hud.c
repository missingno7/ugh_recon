#include "hud.h"

static HudResult hud_empty(HudStage next){HudResult r;r.count=0;r.next=next;return r;}
static void hud_append(HudResult *r,HudEffectKind kind,HudField field,
    uint16_t a,uint16_t b,uint16_t c,uint16_t d,uint16_t e){
    HudEffect effect;effect.kind=kind;effect.field=field;
    effect.a=a;effect.b=b;effect.c=c;effect.d=d;effect.e=e;
    r->effects[r->count++]=effect;
}
static void hud_store(HudResult *r,HudField field,uint16_t value){hud_append(r,HUD_STORE,field,value,0,0,0,0);}
static void hud_number(HudResult *r,HudEffectKind kind,uint16_t current,uint16_t previous,uint16_t high,uint16_t old_high){
    hud_append(r,kind,HF_CURSOR_X,current,previous,high,old_high,0);
}
static void hud_sprite(HudResult *r,uint16_t id,uint16_t x){hud_append(r,HUD_SPRITE,HF_CURSOR_X,id,x,193,0,0);}
RenderDrawRequest hud_digit(uint8_t digit,uint16_t x,uint16_t y){
    RenderDrawRequest r;r.sprite=(uint16_t)(204u+digit);r.x=x;r.y=y;r.draw=1;return r;
}
RenderDrawRequest hud_border(uint16_t players,uint8_t second){
    RenderDrawRequest r;r.sprite=(uint16_t)((players==2?0xb0u:0xaeu)+(second?1u:0u));
    r.x=second?255:0;r.y=193;r.draw=1;return r;
}
uint16_t hud_advance(uint16_t x){return (uint16_t)(x+6u);}
HudDigitDecision hud_changed_digit(uint8_t current,uint8_t previous,uint16_t x,uint16_t index){
    HudDigitDecision r;r.done=(uint8_t)(current==255);r.draw=(uint8_t)(!r.done && current!=previous);
    r.next_x=r.done?x:hud_advance(x);r.next_index=r.done?index:(uint16_t)(index+1u);return r;
}
HudResult hud_lives(HudValues v){
    HudResult r=hud_empty(HUD_SCORE);hud_store(&r,HF_CURSOR_Y,194);
    if(v.lives!=v.cached_lives){hud_store(&r,HF_LIVES,v.lives);hud_store(&r,HF_CURSOR_X,v.lives_x);
        hud_number(&r,HUD_NUMBER_TWO,v.lives,v.cached_lives,0,0);}return r;
}
HudResult hud_score(HudValues v){
    HudResult r=hud_empty(HUD_JOURNEYS);
    if(v.score_high>15 || (v.score_high==15 && v.score_low>0x423fu)){
        v.score_low=0x423f;v.score_high=15;hud_store(&r,HF_SCORE_LOW,v.score_low);hud_store(&r,HF_SCORE_HIGH,v.score_high);}
    if(v.score_low!=v.cached_score_low || v.score_high!=v.cached_score_high){
        hud_store(&r,HF_CACHED_SCORE_LOW,v.score_low);hud_store(&r,HF_CACHED_SCORE_HIGH,v.score_high);
        hud_store(&r,HF_CURSOR_X,v.score_x);hud_number(&r,HUD_NUMBER_SIX,v.score_low,v.cached_score_low,v.score_high,v.cached_score_high);r.next=HUD_TIMER;}
    return r;
}
HudResult hud_journeys(HudValues v){
    HudResult r=hud_empty(HUD_ICON_ONE);
    if(v.journeys!=v.cached_journeys){hud_store(&r,HF_JOURNEYS,v.journeys);hud_store(&r,HF_CURSOR_X,v.journeys_x);
        hud_number(&r,HUD_NUMBER_TWO,v.journeys,v.cached_journeys,0,0);}return r;
}
HudResult hud_icon_one(HudValues v){
    HudResult r=hud_empty(HUD_ICON_TWO);
    if(v.icon_one!=v.cached_icon_one){hud_store(&r,HF_ICON_ONE,v.icon_one);
        hud_sprite(&r,(uint16_t)(v.icon_one+0xb2u),v.icon_one_x);
        hud_sprite(&r,(uint16_t)(v.destination_one+0xb7u),v.destination_one_x);r.next=HUD_TIMER;}return r;
}
HudResult hud_icon_two(HudValues v){
    HudResult r=hud_empty(HUD_FARE);
    if(v.players==2 && v.icon_two!=v.cached_icon_two){hud_store(&r,HF_ICON_TWO,v.icon_two);
        hud_sprite(&r,(uint16_t)(v.icon_two+0xbfu),v.icon_two_x);
        hud_sprite(&r,(uint16_t)(v.destination_two+0xc4u),v.destination_two_x);r.next=HUD_TIMER;}return r;
}
HudResult hud_fare(HudValues v){
    HudResult r=hud_empty(HUD_MULTIPLIER);uint16_t fare=0;hud_store(&r,HF_CURSOR_X,v.fare_x);
    if(v.icon_one)fare=v.fare_one;
    else if(v.players==2 && v.icon_two)fare=v.fare_two;
    else if(!v.clear_fare)return r;
    if(fare!=v.cached_fare){hud_store(&r,HF_FARE,fare);hud_number(&r,HUD_NUMBER_FOUR,fare,v.cached_fare,0,0);}
    hud_store(&r,HF_CLEAR_FARE,0);return r;
}
HudResult hud_multiplier(HudValues v){
    HudResult r=hud_empty(HUD_TIMER);
    if(v.multiplier!=v.cached_multiplier){hud_store(&r,HF_MULTIPLIER,v.multiplier);hud_store(&r,HF_CURSOR_X,v.multiplier_x);
        hud_number(&r,HUD_NUMBER_TWO,v.multiplier,v.cached_multiplier,0,0);}return r;
}
HudResult hud_timer(HudValues v){
    HudResult r=hud_empty(HUD_DONE);
    if((int16_t)v.timer<0){hud_store(&r,HF_TIMER,0xffff);
        if((int16_t)v.fade_step>=0){hud_store(&r,HF_FADE_STEP,0xfffe);hud_store(&r,HF_FADE_LEVEL,(uint16_t)(v.fade_level-2u));}
        return r;}
    if(!v.divisor){hud_append(&r,HUD_DIVISION_ERROR,HF_BAR_WIDTH,0,0,0,0,0);return r;}
    uint16_t width=(uint16_t)(v.timer/v.divisor);
    if(width!=v.bar_width)hud_append(&r,HUD_BAR,HF_BAR_WIDTH,width,v.bar_width,0,0,0);
    hud_store(&r,HF_BAR_WIDTH,width);return r;
}
void hud_project_store(HudValues *v,HudEffect e){
    if(e.kind!=HUD_STORE)return;
    switch(e.field){
    case HF_CURSOR_X:v->cursor_x=e.a;break;case HF_CURSOR_Y:v->cursor_y=e.a;break;
    case HF_LIVES:v->cached_lives=e.a;break;
    case HF_SCORE_LOW:v->score_low=e.a;break;case HF_SCORE_HIGH:v->score_high=e.a;break;
    case HF_CACHED_SCORE_LOW:v->cached_score_low=e.a;break;case HF_CACHED_SCORE_HIGH:v->cached_score_high=e.a;break;
    case HF_JOURNEYS:v->cached_journeys=e.a;break;case HF_ICON_ONE:v->cached_icon_one=e.a;break;case HF_ICON_TWO:v->cached_icon_two=e.a;break;
    case HF_FARE:v->cached_fare=e.a;break;case HF_CLEAR_FARE:v->clear_fare=e.a;break;
    case HF_MULTIPLIER:v->cached_multiplier=e.a;break;case HF_TIMER:v->timer=e.a;break;
    case HF_FADE_STEP:v->fade_step=e.a;break;case HF_FADE_LEVEL:v->fade_level=e.a;break;
    case HF_BAR_WIDTH:v->bar_width=e.a;break;
    }
}
HudBarSpec hud_bar(uint16_t width,uint16_t previous){
    HudBarSpec r;r.cumulative=(uint8_t)((int16_t)width>=(int16_t)previous);
    uint16_t last=r.cumulative?(uint16_t)(width-1u):width;
    r.cell=(uint16_t)(last>>2);r.mask_index=(uint8_t)(last&3u);r.value=r.cumulative?50:0;
    r.remaining=r.cumulative?(uint16_t)(r.cell-(previous>>2)):0;return r;
}
uint16_t hud_bar_next(HudBarSpec *bar){
    bar->cell=(uint16_t)(bar->cell-1u);bar->remaining=(uint16_t)(bar->remaining-1u);return bar->cell;
}
uint16_t hud_bar_row(uint16_t cell,uint8_t row){return (uint16_t)(cell+96u*row);}
