"""Actual bridge import, working projection, consumption and return-cut properties."""
import argparse
from closure_support import ROOT
from hud_shells import OUT,FILES,FIELDS,BORROWED
from hud_proof import common,byte_constraints,effect_equal
from render_primitives_limits import cbmc

KEYS=['import','store','finish','service-two','service-four','service-six','service-sprite','returned']
def source(key):
    s=common()+'''static void normalized8(uint16_t segment,uint16_t at,uint8_t value){store(segment,at,value,1);}
static void normalized16(uint16_t segment,uint16_t at,uint16_t value){store(segment,at,value,2);}
void bridge_abort(void){CHECK(0,"BRIDGE_REJECTED");__CPROVER_assume(0);}
#define wr8 normalized8
#define wr16 normalized16
#define abort bridge_abort
'''
    header=(ROOT/'native/bridge/hud_support.h').read_text().replace('#include <stdlib.h>','').replace('#include <string.h>','''#include <stddef.h>
static void *normalized_memset(void *p,int value,size_t n){unsigned char *a=p;for(size_t i=0;i<n;i++)a[i]=(unsigned char)value;return p;}
static int normalized_memcmp(const void *p,const void *q,size_t n){const unsigned char *a=p,*b=q;for(size_t i=0;i<n;i++)if(a[i]!=b[i])return a[i]<b[i]?-1:1;return 0;}
#define memset normalized_memset
#define memcmp normalized_memcmp
''').replace('#include "../hud.h"','#include "'+(ROOT/'native/hud.h').as_posix()+'"')
    s+=header+'\nint main(void){HudValues arbitrary;memory=arbitrary;'+byte_constraints('memory')+'recorded.count=0;\n'
    if key=='import':
        s+='HudValues view;uint16_t data;hd_import(data,&view);'
        for m,_,_ in [*FIELDS,*BORROWED]:s+=f'CHECK(view.{m}==memory.{m},"complete actual import field");'
    else:
        s+='HudPlan p;p.values=memory;Regs r;r.ds=p.data;unsigned prefix;__CPROVER_assume(prefix<8);p.consumed=prefix;p.result.count=prefix+1;\n'
        if key=='store':
            s+='unsigned selected;__CPROVER_assume(selected<17);uint16_t value;\n'
            for i,(_,_,width) in enumerate(FIELDS):
                if width==1:s+=f'if(selected=={i})__CPROVER_assume(value<256);\n'
            s+='HudEffect e={HUD_STORE,(HudField)selected,value,0,0,0,0};p.result.effects[prefix]=e;\n'
            s+='const uint16_t offsets[]={'+','.join('D('+n+')' for _,n,_ in FIELDS)+'};const unsigned widths[]={'+','.join(str(w) for _,_,w in FIELDS)+'};\n'
            s+='hd_store(&r,&p,offsets[selected],value,widths[selected]);CHECK(p.consumed==prefix+1 && recorded.count==1 && '+effect_equal('recorded.effects[0]','e')+',"selected exact-width store consumed and published");'
        elif key=='finish':
            s+='p.consumed=p.result.count;p.bar_active=0;HudStage next;p.result.next=next;hd_finish(&p,next);CHECK(p.consumed==p.result.count && !p.bar_active,"normal finish requires full consumption and no pending bar");'
        elif key=='returned':
            s+='uint16_t previous;p.values.cursor_x=previous;hd_returned(&p);CHECK(p.values.cursor_x==memory.cursor_x,"child cursor continuation imported before projection");'
        else:
            kind={'service-two':'HUD_NUMBER_TWO','service-four':'HUD_NUMBER_FOUR','service-six':'HUD_NUMBER_SIX','service-sprite':'HUD_SPRITE'}[key]
            target={'service-two':'RedrawChangedTwoDigitNumber','service-four':'RedrawChangedFourDigitNumber','service-six':'RedrawChangedSixDigitNumber','service-sprite':'DrawTransparentSprite'}[key]
            s+='HudEffect e;e.kind='+kind+';uint16_t ah,bh;'
            if key=='service-two':s+='__CPROVER_assume(e.a<256 && e.b<256);r.ax=(uint16_t)((ah&0xff00u)|e.a);r.bx=(uint16_t)((bh&0xff00u)|e.b);'
            else:s+='r.ax=e.a;r.bx=e.b;r.cx=e.c;r.dx=e.c;'
            if key=='service-six':s+='r.cx=e.d;'
            s+='p.result.effects[prefix]=e;Regs before=r;hd_service(&r,&p,G('+target+'));CHECK(p.consumed==prefix+1,"selected native service consumed exactly once");CHECK(r.ax==before.ax && r.bx==before.bx && r.cx==before.cx && r.dx==before.dx,"actual binding preserves the matching ABI operands");'
        for m,_,_ in [*FIELDS,*BORROWED]:s+=f'CHECK(p.values.{m}==memory.{m},"every working input/output field agrees at cut");'
    return s+'return 0;}'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('key',choices=KEYS);ap.add_argument('--timeout',type=int,default=600);ap.add_argument('--reachability',action='store_true');a=ap.parse_args()
    folder=OUT/('kernel-reachability' if a.reachability else 'kernel')/a.key;folder.mkdir(parents=True,exist_ok=True);code=source(a.key)
    if a.reachability:
        at=code.rindex('return 0;}');code=code[:at]+'CHECK(0,"REACHED_FINAL_COMPARISON");'+code[at:]
    h=folder/'harness.c';h.write_text(code)
    r=cbmc(h,folder,[*FILES,ROOT/'native/render_primitives.h',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',ROOT/'verif/hud_proof.py',ROOT/'verif/hud_kernel.py'],unwind=96,timeout=a.timeout)
    print(r['result'],a.key,r['seconds'],flush=True)
    if a.reachability:assert r['result']=='FAIL' and r['failures'] and all('REACHED_FINAL_COMPARISON' in str(f) for f in r['failures'])
    else:assert r['result']=='PASS',r.get('failures')
if __name__=='__main__':main()
