#ifndef HUD_SUPPORT_H
#define HUD_SUPPORT_H
#include "platform.h"
#include "../hud.h"
#include <stdlib.h>
#include <string.h>
static void hd_require(int c){if(!c)abort();}
static uint16_t hd_word(uint16_t native_value,uint16_t old){hd_require(native_value==old);return native_value;}
static void hd_draw(Regs *r,RenderDrawRequest e){hd_require(e.draw);r->ax=hd_word(e.sprite,r->ax);r->bx=hd_word(e.x,r->bx);r->cx=hd_word(e.y,r->cx);}
static void hd_import(uint16_t data,HudValues *v){memset(v,0,sizeof(*v));
v->cursor_x=rd16(data,D(HudDigitCursorX));
v->cursor_y=rd16(data,D(HudDigitCursorY));
v->cached_lives=rd8(data,D(HudCachedLives));
v->score_low=rd16(data,D(ScoreLowWord));
v->score_high=rd16(data,D(ScoreHighWord));
v->cached_score_low=rd16(data,D(HudCachedScoreLow));
v->cached_score_high=rd16(data,D(HudCachedScoreHigh));
v->cached_journeys=rd8(data,D(HudCachedLevelCounter));
v->cached_icon_one=rd16(data,D(HudCachedPlayerOneIconState));
v->cached_icon_two=rd16(data,D(HudCachedPlayerTwoIconState));
v->cached_fare=rd16(data,D(HudCachedFare));
v->clear_fare=rd8(data,D(HudFareClearPending));
v->cached_multiplier=rd8(data,D(HudCachedMultiplier));
v->timer=rd16(data,D(LevelTimer));
v->fade_step=rd16(data,D(ScreenFadeStep));
v->fade_level=rd16(data,D(ScreenFadeLevel));
v->bar_width=rd16(data,D(CachedTimerBarWidth));
v->lives=rd8(data,D(LivesRemaining));
v->journeys=rd8(data,D(RemainingPassengerJourneys));
v->icon_one=rd16(data,D(PlayerCarriedKinds));
v->icon_two=rd16(data,D(PlayerTwoPassengerIconState));
v->destination_one=rd16(data,D(PlayerDestinationIcons));
v->destination_two=rd16(data,D(PlayerTwoDestinationIconIndex));
v->players=rd16(data,D(PlayerCount));
v->fare_one=rd16(data,D(PlayerPassengerFares));
v->fare_two=rd16(data,(uint16_t)(D(PlayerPassengerFares)+2u));
v->multiplier=rd8(data,D(ScoreMultiplier));
v->divisor=rd16(data,D(TimerBarDivisor));
v->lives_x=rd16(data,D(HudLivesX));
v->score_x=rd16(data,D(HudScoreX));
v->journeys_x=rd16(data,D(HudLevelCounterX));
v->icon_one_x=rd16(data,D(HudPlayerOneIconX));
v->icon_two_x=rd16(data,D(HudPlayerTwoIconX));
v->destination_one_x=rd16(data,D(HudPlayerOneDestinationX));
v->destination_two_x=rd16(data,D(HudPlayerTwoDestinationX));
v->fare_x=rd16(data,D(HudFareX));
v->multiplier_x=rd16(data,D(HudMultiplierX));
}
typedef struct HudPlan {HudValues values;HudResult result;unsigned consumed;uint16_t data;HudBarSpec bar;uint16_t bar_base,bar_segment;int bar_active,partial;} HudPlan;
static void hd_projection(HudPlan *p){HudValues live;hd_import(p->data,&live);hd_require(!memcmp(&p->values,&live,sizeof(live)));}
static void hd_open(Regs *r,HudPlan *p,HudStage stage){
 p->data=r->ds;p->consumed=0;p->bar_active=p->partial=0;hd_import(p->data,&p->values);
 switch(stage){
 case HUD_LIVES:p->result=hud_lives(p->values);break;case HUD_SCORE:p->result=hud_score(p->values);break;
 case HUD_JOURNEYS:p->result=hud_journeys(p->values);break;case HUD_ICON_ONE:p->result=hud_icon_one(p->values);break;
 case HUD_ICON_TWO:p->result=hud_icon_two(p->values);break;case HUD_FARE:p->result=hud_fare(p->values);break;
 case HUD_MULTIPLIER:p->result=hud_multiplier(p->values);break;case HUD_TIMER:p->result=hud_timer(p->values);break;
 default:abort();}
 hd_require(p->result.count<=8);
}
static HudEffect hd_next(HudPlan *p){hd_require(p->consumed<p->result.count);return p->result.effects[p->consumed++];}
static void hd_finish(HudPlan *p,HudStage next){hd_require(p->consumed==p->result.count && p->result.next==next && !p->bar_active);hd_projection(p);}
static void hd_advance(Regs *r,HudPlan *p,HudStage next){hd_finish(p,next);hd_open(r,p,next);}
static void hd_store(Regs *r,HudPlan *p,uint16_t field,uint16_t old,unsigned width){
 static const uint16_t offsets[]={D(HudDigitCursorX),D(HudDigitCursorY),D(HudCachedLives),D(ScoreLowWord),D(ScoreHighWord),D(HudCachedScoreLow),D(HudCachedScoreHigh),D(HudCachedLevelCounter),D(HudCachedPlayerOneIconState),D(HudCachedPlayerTwoIconState),D(HudCachedFare),D(HudFareClearPending),D(HudCachedMultiplier),D(LevelTimer),D(ScreenFadeStep),D(ScreenFadeLevel),D(CachedTimerBarWidth)};
 static const unsigned widths[]={2,2,1,2,2,2,2,1,2,2,2,1,1,2,2,2,2};
 HudEffect e=hd_next(p);hd_require(e.kind==HUD_STORE && (unsigned)e.field<17 && offsets[e.field]==field && widths[e.field]==width);
 uint16_t value=hd_word(e.a,old);hd_require(r->ds==p->data);hud_project_store(&p->values,e);
 if(width==1)wr8(r->ds,field,(uint8_t)value);else wr16(r->ds,field,value);hd_projection(p);
}
static void hd_service(Regs *r,HudPlan *p,uint16_t target){
 hd_projection(p);HudEffect e=hd_next(p);
 if(e.kind==HUD_SPRITE){hd_require(target==G(DrawTransparentSprite));RenderDrawRequest q={e.a,e.b,e.c,1};hd_draw(r,q);}
 else if(e.kind==HUD_NUMBER_TWO){hd_require(target==G(RedrawChangedTwoDigitNumber));set_al(r,(uint8_t)hd_word(e.a,(uint8_t)r->ax));r->bx=(uint16_t)((r->bx&0xff00u)|hd_word(e.b,(uint8_t)r->bx));}
 else if(e.kind==HUD_NUMBER_FOUR){hd_require(target==G(RedrawChangedFourDigitNumber));r->ax=hd_word(e.a,r->ax);r->bx=hd_word(e.b,r->bx);}
 else {hd_require(e.kind==HUD_NUMBER_SIX && target==G(RedrawChangedSixDigitNumber));r->ax=hd_word(e.a,r->ax);r->bx=hd_word(e.b,r->bx);r->dx=hd_word(e.c,r->dx);r->cx=hd_word(e.d,r->cx);}
}
static void hd_returned(HudPlan *p){p->values.cursor_x=rd16(p->data,D(HudDigitCursorX));hd_projection(p);}
static void hd_error(HudPlan *p){HudEffect e=hd_next(p);hd_require(e.kind==HUD_DIVISION_ERROR);hd_finish(p,HUD_DONE);}
static void hd_bar_begin(HudPlan *p,uint16_t width,uint16_t previous){
 hd_projection(p);HudEffect e=hd_next(p);hd_require(e.kind==HUD_BAR);hd_word(e.a,width);hd_word(e.b,previous);
 p->bar=hud_bar(e.a,e.b);p->bar_active=1;p->partial=0;
 p->bar_base=rd16(p->data,D(TimerBarPointer));p->bar_segment=rd16(p->data,D(TimerBarPointer)+2);
}
static uint8_t hd_mask(HudPlan *p,uint8_t cumulative,uint16_t index,uint8_t old){
 hd_require(p->bar_active && p->bar.cumulative==cumulative && p->bar.mask_index==index);
 uint16_t base=p->bar.cumulative?D(VgaCumulativePlaneMasks):D(VgaSinglePlaneMasks);
 return (uint8_t)hd_word(rd8(p->data,(uint16_t)(base+p->bar.mask_index)),old);
}
static void hd_bar_pixels(Regs *r,HudPlan *p,uint8_t value,int full){
 hd_require(p->bar_active && r->ds==p->bar_segment);
 uint16_t cell;
 if(full){hd_require(p->partial && p->bar.remaining);cell=hud_bar_next(&p->bar);}
 else {hd_require(!p->partial);cell=p->bar.cell;p->partial=1;}
 uint16_t position=(uint16_t)(p->bar_base+cell);hd_word(position,r->si);hd_word(p->bar.value,value);
 for(uint8_t row=0;row<3;row++)wr8(r->ds,(uint16_t)(p->bar_base+hud_bar_row(cell,row)),p->bar.value);
}
static void hd_bar_end(HudPlan *p){if(p->bar_active){hd_require(p->partial && !p->bar.remaining);p->bar_active=0;}}
#endif
