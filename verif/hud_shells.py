"""Seven exact retained HUD ABI bodies and explicit native stage cuts."""
import argparse
from closure_support import ROOT,function

OUT=ROOT/'build/workers/close-stones-11/hud'
BRIDGE=ROOT/'native/bridge/hud_bridge.c'
SUPPORT=ROOT/'native/bridge/hud_support.h'
NAMES=['DrawHudBorders','DrawHudDigit','DrawHudDigitAndAdvance','RedrawChangedTwoDigitNumber','RedrawChangedFourDigitNumber','RedrawChangedSixDigitNumber','RefreshHudAndTimerBar']
FILES=[ROOT/'native/hud.h',ROOT/'native/hud.c',SUPPORT,BRIDGE]
FIELDS=[('cursor_x','HudDigitCursorX',2),('cursor_y','HudDigitCursorY',2),('cached_lives','HudCachedLives',1),('score_low','ScoreLowWord',2),('score_high','ScoreHighWord',2),('cached_score_low','HudCachedScoreLow',2),('cached_score_high','HudCachedScoreHigh',2),('cached_journeys','HudCachedLevelCounter',1),('cached_icon_one','HudCachedPlayerOneIconState',2),('cached_icon_two','HudCachedPlayerTwoIconState',2),('cached_fare','HudCachedFare',2),('clear_fare','HudFareClearPending',1),('cached_multiplier','HudCachedMultiplier',1),('timer','LevelTimer',2),('fade_step','ScreenFadeStep',2),('fade_level','ScreenFadeLevel',2),('bar_width','CachedTimerBarWidth',2)]
BORROWED=[('lives','LivesRemaining',1),('journeys','RemainingPassengerJourneys',1),('icon_one','PlayerCarriedKinds',2),('icon_two','PlayerTwoPassengerIconState',2),('destination_one','PlayerDestinationIcons',2),('destination_two','PlayerTwoDestinationIconIndex',2),('players','PlayerCount',2),('fare_one','PlayerPassengerFares',2),('fare_two','PlayerPassengerFares',2),('multiplier','ScoreMultiplier',1),('divisor','TimerBarDivisor',2),('lives_x','HudLivesX',2),('score_x','HudScoreX',2),('journeys_x','HudLevelCounterX',2),('icon_one_x','HudPlayerOneIconX',2),('icon_two_x','HudPlayerTwoIconX',2),('destination_one_x','HudPlayerOneDestinationX',2),('destination_two_x','HudPlayerTwoDestinationX',2),('fare_x','HudFareX',2),('multiplier_x','HudMultiplierX',2)]

def replace(text,old,new):assert text.count(old)==1,(old,text.count(old));return text.replace(old,new)
def support():
    text='''#ifndef HUD_SUPPORT_H
#define HUD_SUPPORT_H
#include "platform.h"
#include "../hud.h"
#include <stdlib.h>
#include <string.h>
static void hd_require(int c){if(!c)abort();}
static uint16_t hd_word(uint16_t native_value,uint16_t old){hd_require(native_value==old);return native_value;}
static void hd_draw(Regs *r,RenderDrawRequest e){hd_require(e.draw);r->ax=hd_word(e.sprite,r->ax);r->bx=hd_word(e.x,r->bx);r->cx=hd_word(e.y,r->cx);}
static void hd_import(uint16_t data,HudValues *v){memset(v,0,sizeof(*v));
'''
    for member,label,width in [*FIELDS,*BORROWED]:
        address=f'(uint16_t)(D({label})+2u)' if member=='fare_two' else f'D({label})'
        text+=f'v->{member}=rd{width*8}(data,{address});\n'
    text+='''}
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
 static const uint16_t offsets[]={'''+','.join('D('+label+')' for _,label,_ in FIELDS)+'''};
 static const unsigned widths[]={'''+','.join(str(width) for _,_,width in FIELDS)+'''};
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
'''
    return text

def changed():
    b=function((ROOT/'c/render.c').read_text(),'changed_digits')
    b=replace(b,'cmp8(r,(uint8_t)r->ax,255); if((uint8_t)r->ax==255) return UGH_OK;','cmp8(r,(uint8_t)r->ax,255); if((uint8_t)r->ax==255) {HudDigitDecision end=hud_changed_digit((uint8_t)r->ax,0,R(HudDigitCursorX),r->si);hd_require(end.done && !end.draw);return UGH_OK;}')
    b=replace(b,'        cmp8(r,(uint8_t)r->ax,old);','        HudDigitDecision decision=hud_changed_digit((uint8_t)r->ax,old,R(HudDigitCursorX),r->si);hd_require(!decision.done);unsigned consumed=0;\n        cmp8(r,(uint8_t)r->ax,old);')
    b=replace(b,'{ CALL(DrawHudDigit','{ hd_require(decision.draw);consumed++;CALL(DrawHudDigit')
    b=replace(b,'W(HudDigitCursorX,add16(r,R(HudDigitCursorX),6,0));','hd_require(consumed==decision.draw);W(HudDigitCursorX,hd_word(decision.next_x,add16(r,R(HudDigitCursorX),6,0)));')
    b=replace(b,'flag(r,CF,cf);','flag(r,CF,cf);r->si=hd_word(decision.next_index,r->si);')
    return b

def body(name):
    b=function((ROOT/'c/render.c').read_text(),'c_'+name)
    if name=='DrawHudBorders':
        b=replace(b,'    sub16(r,R(PlayerCount),2,0);','    uint16_t players=R(PlayerCount);RenderDrawRequest first=hud_border(players,0),second=hud_border(players,1);\n    sub16(r,R(PlayerCount),2,0);')
        b=replace(b,'    CALL(DrawTransparentSprite','    hd_draw(r,first);\n    CALL(DrawTransparentSprite')
        b=replace(b,'    return ugh_dispatch','    hd_draw(r,second);return ugh_dispatch')
    if name=='DrawHudDigit':
        b=replace(b,'    push(r,r->ax);','    RenderDrawRequest request=hud_digit((uint8_t)r->ax,R(HudDigitCursorX),R(HudDigitCursorY));\n    push(r,r->ax);')
        b=replace(b,'    CALL(DrawTransparentSprite','    hd_draw(r,request);\n    CALL(DrawTransparentSprite')
    if name=='DrawHudDigitAndAdvance':b=replace(b,'W(HudDigitCursorX,add16(r,R(HudDigitCursorX),6,0));','W(HudDigitCursorX,hd_word(hud_advance(R(HudDigitCursorX)),add16(r,R(HudDigitCursorX),6,0)));')
    if name=='RefreshHudAndTimerBar':
        b=replace(b,'    W(HudDigitCursorY,194);','    HudPlan plan;hd_open(r,&plan,HUD_LIVES);\n    W(HudDigitCursorY,194);')
        cuts=[('    r->ax=R(ScoreLowWord);','HUD_SCORE'),('    set_al(r,B(RemainingPassengerJourneys));','HUD_JOURNEYS'),('    r->ax=R(PlayerCarriedKinds);','HUD_ICON_ONE'),('    sub16(r,R(PlayerCount),2,0);','HUD_ICON_TWO'),('    r->bp=R(HudFareX);','HUD_FARE')]
        # PlayerCount is tested several times; only its first whole statement is
        # the second-icon stage boundary.
        for needle,stage in cuts:
            at=b.index(needle);b=b[:at]+f'    hd_advance(r,&plan,{stage});\n'+b[at:]
        b=replace(b,'    WB(HudFareClearPending,0);','    WB(HudFareClearPending,0);\n    hd_finish(&plan,HUD_MULTIPLIER);')
        b=b.replace('goto multiplier;','{hd_finish(&plan,HUD_MULTIPLIER);goto multiplier;}')
        b=replace(b,'multiplier:\n','multiplier:\n    hd_open(r,&plan,HUD_MULTIPLIER);\n')
        b=b.replace('goto timer;','hd_finish(&plan,HUD_TIMER);goto timer;')
        b=replace(b,'timer:\n','    hd_finish(&plan,HUD_TIMER);\ntimer:\n    hd_open(r,&plan,HUD_TIMER);\n')
        b=replace(b,'        return UGH_OK;','        hd_finish(&plan,HUD_DONE);return UGH_OK;')
        b=replace(b,'if(!divisor) return UGH_UNSUPPORTED;','if(!divisor){hd_error(&plan);return UGH_UNSUPPORTED;}')
        b=replace(b,'    if((int16_t)r->ax<(int16_t)R(CachedTimerBarWidth)) {','    hd_bar_begin(&plan,r->ax,R(CachedTimerBarWidth));\n    if((int16_t)r->ax<(int16_t)R(CachedTimerBarWidth)) {')
        b=replace(b,'set_al(r,rd8(r->ds,(uint16_t)(D(VgaSinglePlaneMasks)+r->bx)));','set_al(r,hd_mask(&plan,0,r->bx,rd8(r->ds,(uint16_t)(D(VgaSinglePlaneMasks)+r->bx))));')
        b=replace(b,'set_al(r,rd8(r->ds,(uint16_t)(D(VgaCumulativePlaneMasks)+r->bx)));','set_al(r,hd_mask(&plan,1,r->bx,rd8(r->ds,(uint16_t)(D(VgaCumulativePlaneMasks)+r->bx))));')
        triple='wr8(r->ds,r->si,(uint8_t)r->ax); wr8(r->ds,(uint16_t)(r->si+96),(uint8_t)r->ax);\n        wr8(r->ds,(uint16_t)(r->si+192),(uint8_t)r->ax);'
        assert b.count(triple)==2;b=b.replace(triple,'hd_bar_pixels(r,&plan,(uint8_t)r->ax,0);')
        b=replace(b,'wr8(r->ds,r->si,(uint8_t)r->ax);\n                wr8(r->ds,(uint16_t)(r->si+96),(uint8_t)r->ax);\n                wr8(r->ds,(uint16_t)(r->si+192),(uint8_t)r->ax);','hd_bar_pixels(r,&plan,(uint8_t)r->ax,1);')
        b=replace(b,'r->bp=dec16(r,r->bp);','r->bp=dec16(r,r->bp);r->bp=hd_word(plan.bar.remaining,r->bp);')
        b=replace(b,'timer_done:\n','timer_done:\n    hd_bar_end(&plan);\n')
        b=replace(b,'W(CachedTimerBarWidth,r->ax); return UGH_OK;','W(CachedTimerBarWidth,r->ax);hd_finish(&plan,HUD_DONE);return UGH_OK;')
        b=b.replace('CALL(','HP_CALL(')
        b=b.replace('W(','HW(').replace('WB(','HWB(') # RI/rd/wr spelling unaffected
    return b

def generate():
    raw=(ROOT/'c/render.c').read_text();text='#include "hud_support.h"\n'
    for name in ['push','pop','cmp8','set_bl']:text+=function(raw,name)+'\n'
    text+='\n'.join(line for line in raw.splitlines() if line.startswith('#define '))+'\n'
    text+='''#define HW(n,v) hd_store(r,&plan,D(n),(uint16_t)(v),2)
#define HWB(n,v) hd_store(r,&plan,D(n),(uint8_t)(v),1)
#define HP_CALL(target,owner,delta) do{hd_service(r,&plan,G(target));int status=ugh_call_near(G(target),(uint16_t)(G(owner)+(delta)),r);if(status)return status;hd_returned(&plan);}while(0)
'''
    text+=changed()
    for name in NAMES:text+=body(name)+'\n'
    return text
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();s=generate();h=support()
    if a.write:BRIDGE.write_text(s);SUPPORT.write_text(h)
    assert BRIDGE.read_text()==s and SUPPORT.read_text()==h
    print('PASS seven full HUD ABI shells and shared digit scan')
if __name__=='__main__':main()
