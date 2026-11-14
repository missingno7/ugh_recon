"""Actual-C HUD branch pieces, independent effect recording and native frames."""
import argparse,re
from closure_support import ROOT,function
from hud_shells import OUT,FILES,FIELDS,BORROWED
from render_primitives_limits import cbmc as limited

STAGES={'lives':('hud_lives','HUD_SCORE'),'score':('hud_score','HUD_JOURNEYS'),
 'journeys':('hud_journeys','HUD_ICON_ONE'),'icon-one':('hud_icon_one','HUD_ICON_TWO'),
 'icon-two':('hud_icon_two','HUD_FARE'),'fare':('hud_fare','HUD_MULTIPLIER'),
 'multiplier':('hud_multiplier','HUD_TIMER'),'timer':('hud_timer','HUD_DONE')}
READS={
 'lives':['lives','cached_lives','lives_x'],
 'score':['score_low','score_high','cached_score_low','cached_score_high','score_x'],
 'journeys':['journeys','cached_journeys','journeys_x'],
 'icon-one':['icon_one','cached_icon_one','destination_one','icon_one_x','destination_one_x'],
 'icon-two':['players','icon_two','cached_icon_two','destination_two','icon_two_x','destination_two_x'],
 'fare':['fare_x','icon_one','icon_two','players','fare_one','fare_two','cached_fare','clear_fare'],
 'multiplier':['multiplier','cached_multiplier','multiplier_x'],
 'timer':['timer','fade_step','fade_level','divisor','bar_width']}
BYTE_MEMBERS=[m for m,_,w in [*FIELDS,*BORROWED] if w==1]

def actual(name):return function((ROOT/'c/render.c').read_text(),name)
def cut(body,start,end):return body[body.index(start):body.index(end,body.index(start))]
def fragment(key):
    b=actual('c_RefreshHudAndTimerBar')
    starts={'lives':'    W(HudDigitCursorY,194);','score':'    r->ax=R(ScoreLowWord);','journeys':'    set_al(r,B(RemainingPassengerJourneys));','icon-one':'    r->ax=R(PlayerCarriedKinds);','icon-two':'    sub16(r,R(PlayerCount),2,0);','fare':'    r->bp=R(HudFareX);','multiplier':'    set_al(r,B(ScoreMultiplier));','timer':'    r->ax=R(LevelTimer);'}
    ends={'lives':starts['score'],'score':starts['journeys'],'journeys':starts['icon-one'],'icon-one':starts['icon-two'],'icon-two':starts['fare'],'fare':'multiplier:','multiplier':'timer:','timer':'    sub16(r,r->ax,R(CachedTimerBarWidth),0);'}
    return cut(b,starts[key],ends[key])

def common():
    s='#include "ugh.h"\n#include "'+(ROOT/'native/hud.c').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert((c),(m))\n'
    s+='static HudValues memory;static HudResult recorded;static unsigned read_mask;static uint16_t sampled_dimensions;static uint16_t stack_words[4];static unsigned depth;\n'
    s+='static void record(HudEffectKind kind,HudField field,uint16_t a,uint16_t b,uint16_t c,uint16_t d){CHECK(recorded.count<8,"independent recorder bound");HudEffect e={kind,field,a,b,c,d,0};recorded.effects[recorded.count++]=e;}\n'
    s+='static uint16_t sample16(uint16_t segment,uint16_t at){(void)segment;\n'
    for member,label,width in [*FIELDS,*BORROWED]:
        address=f'(uint16_t)(D({label})+2u)' if member=='fare_two' else f'D({label})'
        s+=f'if(at=={address})return memory.{member};\n'
    s+='CHECK(0,"complete word-field binding");return 0;}\n'
    s+='static uint8_t sample8(uint16_t segment,uint16_t at){if(at>=D(VgaSinglePlaneMasks) && at<(uint16_t)(D(VgaSinglePlaneMasks)+4)){read_mask=at;return 0;}if(at>=D(VgaCumulativePlaneMasks) && at<(uint16_t)(D(VgaCumulativePlaneMasks)+4)){read_mask=at;return 0;}return (uint8_t)sample16(segment,at);}\n'
    s+='static void store(uint16_t segment,uint16_t at,uint16_t value,unsigned width){(void)segment;\n'
    for i,(member,label,width) in enumerate(FIELDS):s+=f'if(at==D({label})){{CHECK(width=={width},"exact store width");record(HUD_STORE,(HudField){i},value,0,0,0);memory.{member}=value;return;}}\n'
    s+='CHECK(0,"declared writes only; every other normalized field is framed");}\n'
    s+='static void ref_call(uint16_t target,Regs *r){if(target==G(DrawTransparentSprite))record(HUD_SPRITE,HF_CURSOR_X,r->ax,r->bx,r->cx,0);else if(target==G(RedrawChangedTwoDigitNumber))record(HUD_NUMBER_TWO,HF_CURSOR_X,(uint8_t)r->ax,(uint8_t)r->bx,0,0);else if(target==G(RedrawChangedFourDigitNumber))record(HUD_NUMBER_FOUR,HF_CURSOR_X,r->ax,r->bx,0,0);else if(target==G(RedrawChangedSixDigitNumber))record(HUD_NUMBER_SIX,HF_CURSOR_X,r->ax,r->bx,r->dx,r->cx);else CHECK(0,"complete service target set");}\n'
    s+='static void ref_push(Regs *r,uint16_t v){(void)r;CHECK(depth<4,"ordinary disjoint stack");stack_words[depth++]=v;}\nstatic uint16_t ref_pop(Regs *r){(void)r;CHECK(depth>0,"paired original stack");return stack_words[--depth];}\n'
    s+='''#define R(n) sample16(r->ds,D(n))
#define B(n) sample8(r->ds,D(n))
#define RI(n,i) sample16(r->ds,(uint16_t)(D(n)+(i)))
#define W(n,v) store(r->ds,D(n),(uint16_t)(v),2)
#define WB(n,v) store(r->ds,D(n),(uint8_t)(v),1)
#define rd16 sample16
#define rd8 sample8
#define push ref_push
#define pop ref_pop
#define CALL(n,o,d) ref_call(G(n),r)
'''
    s+=actual('cmp8')+actual('set_bl')
    return s

def byte_constraints(obj):return ''.join(f'__CPROVER_assume({obj}.{m}<256);' for m in BYTE_MEMBERS)
def effect_equal(a,b):return ' && '.join(f'{a}.{f}=={b}.{f}' for f in ['kind','field','a','b','c','d','e'])

def output(key):
    s=common()
    if key in STAGES:
        native,next_stage=STAGES[key];body=fragment(key)
        if key=='timer':
            b=actual('c_RefreshHudAndTimerBar')
            body=body.replace('return UGH_OK;','goto done;').replace('if(!divisor) return UGH_UNSUPPORTED;','if(!divisor){record(HUD_DIVISION_ERROR,HF_BAR_WIDTH,0,0,0,0);goto done;}')
            body+=cut(b,'    sub16(r,r->ax,R(CachedTimerBarWidth),0);','    if((int16_t)r->ax<(int16_t)R(CachedTimerBarWidth)) {')
            body+='record(HUD_BAR,HF_BAR_WIDTH,r->ax,R(CachedTimerBarWidth),0,0);\n'
            body+='timer_done:\n'+cut(b,'    r->ax=pop(r); r->ds=pop(r);',' return UGH_OK;')
        s+=f'static void reference(Regs *r){{recorded.count=0;recorded.next={next_stage};'+body
        s+='goto done;\ntimer:recorded.next=HUD_TIMER;goto done;\n' if key!='timer' else 'goto done;\n'
        if key=='fare':s+='multiplier:;\n'
        s+='done:return;}\nint main(void){HudValues v;'+byte_constraints('v')+'Regs r;r.ds=0x8000;memory=v;depth=0;reference(&r);HudResult modern='+native+'(v);CHECK(modern.count==recorded.count && modern.next==recorded.next,"count and exact branch continuation");unsigned watch;__CPROVER_assume(watch<8);if(watch<modern.count)CHECK('+effect_equal('modern.effects[watch]','recorded.effects[watch]')+',"arbitrary ordered published store/service");return 0;}'
    elif key=='advance':
        b=actual('c_DrawHudDigitAndAdvance');statement=cut(b,'    W(HudDigitCursorX',' return UGH_OK;')
        s+='int main(void){HudValues any;memory=any;Regs arbitrary;Regs *r=&arbitrary;recorded.count=0;uint16_t before=memory.cursor_x;'+statement+'CHECK(memory.cursor_x==hud_advance(before),"actual post-service live cursor word wraps");return 0;}'
    elif key=='digit':
        b=actual('c_DrawHudDigit');s+='int main(void){HudValues any;memory=any;Regs arbitrary;Regs *r=&arbitrary;depth=0;RenderDrawRequest e=hud_digit((uint8_t)r->ax,memory.cursor_x,memory.cursor_y);'+cut(b,'    push(r,r->ax);','    CALL(')+'CHECK(e.sprite==r->ax && e.x==r->bx && e.y==r->cx && e.draw,"raw AL glyph and live cursor seam");return 0;}'
    elif key=='border':
        b=actual('c_DrawHudBorders');s+='int main(void){HudValues any;memory=any;Regs arbitrary;Regs *r=&arbitrary;depth=0;RenderDrawRequest first=hud_border(memory.players,0),second=hud_border(memory.players,1);'+cut(b,'    sub16(r,R(PlayerCount),2,0);','    CALL(')+'CHECK(first.sprite==r->ax && first.x==r->bx && first.y==r->cx && first.draw,"first border request");'+cut(b,'    r->ax=pop(r);','    return ugh_dispatch')+'CHECK(second.sprite==r->ax && second.x==r->bx && second.y==r->cx && second.draw,"second border tail request");return 0;}'
    elif key in ['bar-shrink','bar-grow']:
        b=actual('c_RefreshHudAndTimerBar');growing=key=='bar-grow'
        a='        r->di=(uint16_t)(R(CachedTimerBarWidth)>>2);' if growing else '        r->bp=r->ax;'
        end='        wr8(r->ds,r->si,'
        piece=cut(b,a,end)
        # Port and pixel bindings remain services; preserve all scalar statements.
        s+='static void ignored_out(uint16_t port,unsigned width,uint32_t v){(void)port;(void)width;(void)v;}\n#define platform_out ignored_out\n'
        s+='int main(void){HudValues any;memory=any;Regs arbitrary;Regs *r=&arbitrary;uint16_t width=r->ax,previous=memory.bar_width;__CPROVER_assume(width!=previous && ((int16_t)width'+('>=' if growing else '<')+'(int16_t)previous));HudBarSpec e=hud_bar(width,previous);\n'
        # Resource pointer reads are arbitrary service outputs at this cut.
        s+='#undef R\n#define R(n) (D(n)==D(TimerBarPointer)?0:sample16(r->ds,D(n)))\n#undef rd16\n#define rd16(seg,at) ((uint16_t)0)\n'
        s+=piece
        if growing:s+=cut(b,'        r->bp=sub16(r,r->bp,r->di,0);','        if(r->bp)')
        s+='CHECK(e.cumulative=='+('1' if growing else '0')+' && e.mask_index==(read_mask-'+('D(VgaCumulativePlaneMasks)' if growing else 'D(VgaSinglePlaneMasks)')+') && e.cell==r->si && e.value==(uint8_t)r->ax,"mask family/index, relative partial cell and paint value");'
        s+='CHECK(e.remaining==r->bp,"wrapping complete-cell span");' if growing else 'CHECK(!e.remaining,"shrink clears only one partial cell");'
        s+='return 0;}'
    elif key=='bar-next':
        b=actual('c_RefreshHudAndTimerBar');piece=cut(b,'                r->si=dec16(r,r->si);','            } while(r->bp);')
        s+='static uint16_t positions[3];static uint8_t values[3];static unsigned count;static void pixel(uint16_t segment,uint16_t at,uint8_t v){(void)segment;CHECK(count<3,"exact three-row service");positions[count]=at;values[count++]=v;}\n#define wr8 pixel\nint main(void){Regs arbitrary;Regs *r=&arbitrary;HudBarSpec e;uint16_t base;uint16_t oldcell=e.cell;r->si=(uint16_t)(base+e.cell);r->bp=e.remaining;uint8_t paint=(uint8_t)r->ax;count=0;uint16_t cell=hud_bar_next(&e);'+piece+'CHECK(count==3 && e.cell==cell && cell==(uint16_t)(oldcell-1u) && e.remaining==r->bp,"actual full-cell successor and countdown wrap");uint8_t row;__CPROVER_assume(row<3);CHECK(positions[row]==(uint16_t)(base+hud_bar_row(cell,row)) && values[row]==paint,"arbitrary ordered row position/value");return 0;}'
    elif key=='changed':
        b=actual('changed_digits');piece=cut(b,'        set_al(r,rd8','    }\n}')
        s+='static uint8_t current_digit,previous_digit;static uint16_t scan_index;static unsigned calls;static uint8_t digit_read(uint16_t segment,uint16_t at){(void)segment;if(at==(uint16_t)(D(DecimalDigitBuffer)+scan_index))return current_digit;CHECK(at==(uint16_t)(D(DecimalDigitBuffer)+7+scan_index),"old digit read only at matching index");return previous_digit;}\n#undef rd8\n#define rd8 digit_read\n#undef CALL\n#define CALL(n,o,d) calls++\n'
        s+='int main(void){HudValues any;memory=any;Regs arbitrary;Regs *r=&arbitrary;uint8_t a,b;current_digit=a;previous_digit=b;scan_index=r->si;calls=recorded.count=0;HudDigitDecision e=hud_changed_digit(a,b,memory.cursor_x,r->si);'+piece.replace('return UGH_OK;','goto done;')+'done:CHECK(e.done==(a==255) && e.draw==calls && e.next_x==memory.cursor_x && e.next_index==r->si,"sentinel, draw/skip, cursor and wrapping scanner seam");return 0;}'
    elif key=='projection':
        s+='int main(void){HudValues v,before;v=before;HudEffect e;__CPROVER_assume(e.kind==HUD_STORE && (unsigned)e.field<17);hud_project_store(&v,e);unsigned selected=0;\n'
        for i,(member,_,_) in enumerate(FIELDS):s+=f'if(e.field=={i}){{CHECK(v.{member}==e.a,"selected working field");selected=1;}}else CHECK(v.{member}==before.{member},"every other owned field frame");\n'
        for member,_,_ in BORROWED:s+=f'CHECK(v.{member}==before.{member},"every borrowed input field frame");\n'
        s+='CHECK(selected,"complete projection field domain");return 0;}'
    elif key=='append':
        s+='int main(void){HudResult r,before;r=before;__CPROVER_assume(r.count<8);HudEffectKind kind;HudField field;uint16_t a,b,c,d,e;unsigned prefix=r.count;hud_append(&r,kind,field,a,b,c,d,e);CHECK(r.count==prefix+1 && r.next==before.next,"arbitrary prefix append count and continuation frame");unsigned watch;__CPROVER_assume(watch<8);if(watch==prefix)CHECK(r.effects[watch].kind==kind && r.effects[watch].field==field && r.effects[watch].a==a && r.effects[watch].b==b && r.effects[watch].c==c && r.effects[watch].d==d && r.effects[watch].e==e,"arbitrary appended payload");else CHECK('+effect_equal('r.effects[watch]','before.effects[watch]')+',"every other event frame");return 0;}'
    else:raise ValueError(key)
    return s

def dependence(key):
    if key=='bar-next':
        return '#include "'+(ROOT/'native/hud.c').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert((c),(m))\nint main(void){HudBarSpec a,b;b.cell=a.cell;b.remaining=a.remaining;uint16_t x=hud_bar_next(&a),y=hud_bar_next(&b);CHECK(x==y && a.cell==b.cell && a.remaining==b.remaining,"bar successor dependence on cursor/count only");return 0;}'
    fn,_=STAGES[key];s='#include "'+(ROOT/'native/hud.c').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert((c),(m))\nint main(void){HudValues first,second;'+byte_constraints('first')+byte_constraints('second')
    for f in READS[key]:s+=f'second.{f}=first.{f};'
    s+='HudResult a='+fn+'(first),b='+fn+'(second);CHECK(a.count==b.count && a.next==b.next,"only declared inputs determine branch/count");unsigned watch;__CPROVER_assume(watch<8);if(watch<a.count)CHECK('+effect_equal('a.effects[watch]','b.effects[watch]')+',"arbitrary published effect dependence");return 0;}'
    return s

def frame(key):
    s='#include <stddef.h>\n#include "'+(ROOT/'native/hud.c').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert((c),(m))\nint main(void){'
    if key=='bar-next':s+='HudBarSpec a,b;a=b;hud_bar_next(&a);CHECK(a.cumulative==b.cumulative && a.mask_index==b.mask_index && a.value==b.value,"all other bar request fields framed");'
    else:
        fn,_=STAGES[key];s+='HudValues a,b;a=b;'+byte_constraints('a')+'HudResult out='+fn+'(a);CHECK(out.count<=8,"complete journal bound");size_t at;__CPROVER_assume(at<sizeof(a));CHECK(((unsigned char *)&a)[at]==((unsigned char *)&b)[at],"every original owned/borrowed input byte unchanged by pure stage");'
    return s+'return 0;}'

KEYS=[*STAGES,'digit','advance','border','changed','bar-shrink','bar-grow','bar-next','projection','append']
def main():
    ap=argparse.ArgumentParser();ap.add_argument('key',choices=KEYS);ap.add_argument('mode',choices=['output','frame','dependence'],default='output',nargs='?');ap.add_argument('--timeout',type=int,default=600);ap.add_argument('--reachability',action='store_true');a=ap.parse_args()
    folder=OUT/('reachability' if a.reachability else 'proofs')/(a.key+'-'+a.mode);folder.mkdir(parents=True,exist_ok=True)
    code=output(a.key) if a.mode=='output' else frame(a.key) if a.mode=='frame' else dependence(a.key)
    if a.reachability:
        at=code.rindex('return 0;');code=code[:at]+'CHECK(0,"REACHED_FINAL_COMPARISON");'+code[at:]
    harness=folder/'harness.c';harness.write_text(code)
    # The primitive worker wrapper archives under its parent worker directory;
    # these HUD subdirectories remain within that same owned tree.
    result=limited(harness,folder,[*FILES,ROOT/'native/render_primitives.h',ROOT/'c/render.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',ROOT/'verif/hud_proof.py'],unwind=16,timeout=a.timeout)
    print(result['result'],a.key,a.mode,result['seconds'],flush=True)
    if a.reachability:assert result['result']=='FAIL' and result['failures'] and all('REACHED_FINAL_COMPARISON' in str(f) for f in result['failures'])
    else:assert result['result']=='PASS',result.get('failures')
if __name__=='__main__':main()
