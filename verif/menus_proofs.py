"""Actual-C menu/text/editor decision and transaction properties."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from menus_build import OUT
from menus_spans import sources,password_editor_span,selector_span
from front_end_limits import cbmc
from adlx_lifetime_proofs import SOLVER

def main():
 p=argparse.ArgumentParser();p.add_argument('entry',choices=['text','centering','copy-index','copy-step','control','mutators','selector','attract','editor','header']);p.add_argument('--negative',action='store_true');a=p.parse_args();folder=OUT/f'menus-proof-{a.entry}{"-negative" if a.negative else ""}';folder.mkdir(parents=True,exist_ok=True)
 menu,helpers,scene=sources();bridge=(ROOT/'native/bridge/menus_bridge.c').read_text();native=(ROOT/'native/menus.c').read_text();shared=(ROOT/'native/high_scores.c').read_text()
 if a.negative:
  if a.entry=='editor':shared=shared.replace('character-32u','character-31u')
  else:
   old,new={'text':('character=91','character=90'),'centering':('320u-','318u-'),'copy-index':('index*2u','index*3u'),'copy-step':('!character','character==255'),'control':('(int16_t)candidate.mode>=2','candidate.mode>=2'),'mutators':('players^=3','players^=1'),'selector':('case 62:','case 64:'),'attract':('if(reply.negative)','if(!reply.negative)'),'header':('ordinal==0 ? 215','ordinal==0 ? 216')}[a.entry];assert old in native;native=native.replace(old,new)
 code='#include "platform.h"\n#include "menus.h"\n#include "high_scores.h"\n#include "'+(ROOT/'native/bridge/front_end_support.h').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert(c,m)\nuint8_t nondet_u8(void);uint16_t nondet_u16(void);Regs nondet_regs(void);\n'+shared+native
 code+='''static void equal(Regs r,Regs s) {CHECK(r.ax==s.ax && r.bx==s.bx && r.cx==s.cx && r.dx==s.dx && r.si==s.si && r.di==s.di && r.bp==s.bp && r.sp==s.sp && r.cs==s.cs && r.ds==s.ds && r.es==s.es && r.ss==s.ss && r.ip==s.ip && r.flags==s.flags,"complete output/frame");}
'''
 unwind=17;extra=[]
 if a.entry=='centering':
  ref=function(menu,'c_DrawTextLine');ref=ref[ref.index('        r->bp=(uint16_t)(r->bp<<4)'):ref.index('        r->si=r->di;')]
  actual=function(bridge,'c_DrawTextLine');actual=actual[actual.index('        r->bx=menus_text_center_x'):actual.index('        r->si=r->di;')]
  code+='static void ref_line(Regs *r) {'+ref+'}\nstatic void actual_line(Regs *r) {'+actual+'}\n'
  ref=function(scene,'c_ShowCreditsPages');ref=ref[ref.index('        r->bp=(uint16_t)((r->bp+1)<<4)'):ref.index('        CALL(DrawTextBlock')]
  actual=function(bridge,'c_ShowCreditsPages');actual=actual[actual.index('        uint16_t center='):actual.index('        MCALL(DrawTextBlock')]
  code+='static void ref_credits(Regs *r) {'+ref+'}\nstatic void actual_credits(Regs *r) {'+actual+'}\nint main(void) {Regs r=nondet_regs(),s=r;if(nondet_u8()&1) {ref_line(&r);actual_line(&s);}else {ref_credits(&r);actual_credits(&s);}equal(r,s);return 0;}'
 elif a.entry=='selector':
  code+='static MenusMainAction reference(Regs *r) {'+selector_span()+'}\n'+function(bridge,'main_key_trace')
  code+='int main(void) {Regs r=nondet_regs(),s=r;MenusMainAction expected=reference(&r);logic(&s,s.ax>>8,8);if(s.ax>>8) main_key_trace(&s,(uint8_t)s.ax);MenusMain state={MENUS_MAIN_POLL,1,1};MenusMainReply reply={0,0,(uint8_t)!!(s.ax>>8),(uint8_t)s.ax,0,0};MenusMainAction actual=menus_main_next(&state,reply);CHECK(expected==actual,"every raw scan and change byte selects its original first action");equal(r,s);return 0;}'
 elif a.entry=='attract':
  body=function(menu,'c_RunMainMenuAndAttractLoop')
  pairs=[('PlaySpriteRevealDemo','ShowCreditsPages','MENUS_MAIN_CREDITS'),('ShowCreditsPages','PlayAttractDemo','MENUS_MAIN_ATTRACT'),('PlayAttractDemo','ShowHighScores','MENUS_MAIN_SCORES'),('ShowHighScores',None,'MENUS_MAIN_PREPARE_PALETTE')]
  for i,(name,next_name,next_action) in enumerate(pairs):
   start=body.index('MCALL('+name);start=body.index(';',start)+1;end=body.index('    MCALL('+next_name,start) if next_name else body.index('prepare:',start)
   part=body[start:end].replace('return UGH_OK;','return MENUS_MAIN_DONE;').replace('goto prepare;','return MENUS_MAIN_PREPARE_PALETTE;')
   code+=f'static MenusMainAction reference_{i}(Regs *r) {{'+part+'return '+next_action+';}\n'
  code+='int main(void) {Regs r=nondet_regs();unsigned stage=nondet_u8();__CPROVER_assume(stage<4);MenusMainAction phases[]={MENUS_MAIN_REVEAL,MENUS_MAIN_CREDITS,MENUS_MAIN_ATTRACT,MENUS_MAIN_SCORES};MenusMainAction expected=stage==0 ? reference_0(&r) : stage==1 ? reference_1(&r) : stage==2 ? reference_2(&r) : reference_3(&r);MenusMain state={phases[stage],1,1};MenusMainReply reply={(uint8_t)!!(r.flags&SF),(uint8_t)!!(r.flags&ZF),0,0,0,0};CHECK(expected==menus_main_next(&state,reply),"original service-result flags drive the attract dispatch, including contradictory flags");return 0;}'
 elif a.entry in ['text','copy-index','copy-step','control','editor']:
  code+='''typedef struct Event {uint32_t address;uint8_t value;} Event;static unsigned side,nr[2],nw[2];static Event reads[2][2],writes[2][16];static uint16_t delivered;
uint8_t ugh_read(uint32_t address) {CHECK(nr[side]<2,"read footprint");uint8_t value=(uint8_t)(delivered>>(8u*nr[side]));reads[side][nr[side]].address=address;reads[side][nr[side]++].value=value;return value;}
void ugh_write(uint32_t address,uint8_t value) {CHECK(nw[side]<16,"write footprint");writes[side][nw[side]].address=address;writes[side][nw[side]++].value=value;}
static void accesses(void) {CHECK(nr[0]==nr[1] && nw[0]==nw[1],"read/write counts");for(unsigned i=0;i<nr[0];i++) CHECK(reads[0][i].address==reads[1][i].address && reads[0][i].value==reads[1][i].value,"ordered reads");for(unsigned i=0;i<nw[0];i++) CHECK(writes[0][i].address==writes[1][i].address && writes[0][i].value==writes[1][i].value,"ordered physical byte writes");}
'''
  if a.entry=='text':
   ref=function(menu,'c_DrawTextLine');ref=ref[ref.index('        if(ch==13 ||'):ref.rindex('    }')]
   actual=function(bridge,'c_DrawTextLine');actual=actual[actual.index('        MenusTextStep item='):actual.rindex('    }')]
   code+='''static Regs response,arguments[2];static uint16_t targets[2],returns[2];static uint8_t calls[2],failure;
int ugh_call_near(uint16_t target,uint16_t ret,Regs *r) {calls[side]++;arguments[side]=*r;targets[side]=target;returns[side]=ret;*r=response;return failure;}
'''
   code+='static int reference(Regs *r,uint8_t *character) {uint8_t ch=*character;'+ref+'*character=ch;return 3;}\nstatic int actual(Regs *r,uint8_t *character) {uint8_t ch=*character;'+actual+'*character=ch;return 3;}\n'
   code+='int main(void) {Regs r=nondet_regs(),s=r;response=nondet_regs();delivered=nondet_u8();failure=nondet_u8()&1;uint8_t ch=nondet_u8(),other=ch;side=0;int first=reference(&r,&ch);side=1;int second=actual(&s,&other);CHECK(first==second && ch==other,"delimiter,failed-service or next-glyph outcome");equal(r,s);accesses();CHECK(calls[0]==calls[1],"glyph request count");if(calls[0]) {equal(arguments[0],arguments[1]);CHECK(targets[0]==targets[1] && returns[0]==returns[1],"glyph service/frame identity");}return 0;}'
  elif a.entry=='copy-index':
   ref=function(helpers,'c_CopyIndexedMenuString');ref=ref[ref.index('    r->es=r->ds;'):ref.index('    for(;;)')]
   actual=function(bridge,'c_CopyIndexedMenuString');actual=actual[actual.index('    r->es=r->ds;'):actual.index('    MenusStringCopy')]
   code+='static void reference(Regs *r) {'+ref+'}\nstatic void actual(Regs *r) {'+actual+'}\nint main(void) {Regs r=nondet_regs(),s=r;delivered=nondet_u16();side=0;reference(&r);side=1;actual(&s);equal(r,s);accesses();return 0;}'
  elif a.entry=='copy-step':
   ref=function(helpers,'c_CopyIndexedMenuString');ref=ref[ref.index('        uint8_t ch='):ref.rindex('    }')]
   actual=function(bridge,'c_CopyIndexedMenuString');actual=actual[actual.index('        uint8_t ch='):actual.rindex('    }')]
   code+='static int reference(Regs *r) {'+ref+'return 3;}\nstatic int actual(Regs *r) {MenusStringCopy copy=menus_string_begin(r->si,r->di,!!(r->flags&DF));'+actual+'return 3;}\nint main(void) {Regs r=nondet_regs(),s=r;delivered=nondet_u8();side=0;int first=reference(&r);side=1;int second=actual(&s);CHECK(first==second,"consumeNUL without a store or continue after store");equal(r,s);accesses();return 0;}'
  elif a.entry=='control':
   ref=function(menu,'c_SelectPlayerControls');ref=ref[ref.index('            r->ax=increment_word'):ref.index('        } while(!(r->flags&SF));')].replace('break;','return 1;')
   actual=function(bridge,'c_SelectPlayerControls');actual=actual[actual.index('            MenusControlCandidate'):actual.index('        } while(!menus_control_present')].replace('break;','return 1;')
   code+='static int reference(Regs *r) {'+ref+'return !!(r->flags&SF);}\nstatic int actual(Regs *r) {uint16_t presence;'+actual+'return menus_control_present(presence);}\nint main(void) {Regs r=nondet_regs(),s=r;delivered=nondet_u16();side=0;int first=reference(&r);side=1;int second=actual(&s);CHECK(first==second,"signed mode wrap and signed presence acceptance");equal(r,s);accesses();return 0;}'
  else:
   code+='static int reference(Regs *r) {'+password_editor_span()+'}\nstatic int actual(Regs *r) {'+password_editor_span(True)+'}\nint main(void) {Regs r=nondet_regs(),s=r;side=0;int first=reference(&r);side=1;int second=actual(&s);CHECK(first==second,"password editor outcome for every index/character");equal(r,s);accesses();return 0;}'
 elif a.entry=='mutators':
  code+='''typedef struct Memory {uint16_t players,bytes,difficulty;} Memory;static Memory memory[2];static unsigned side;
uint8_t ugh_read(uint32_t at) {CHECK(at==D(PlayerCount) || at==D(PlayerCount)+1 || at==D(SelectedDifficulty) || at==D(SelectedDifficulty)+1,"borrowed count/difficulty read");uint16_t value=at<D(SelectedDifficulty) ? memory[side].players : memory[side].difficulty;unsigned shift=(at==D(PlayerCount)+1 || at==D(SelectedDifficulty)+1) ? 8 : 0;return (uint8_t)(value>>shift);}
void ugh_write(uint32_t at,uint8_t value) {uint16_t *field;unsigned shift;if(at==D(PlayerCount) || at==D(PlayerCount)+1) {field=&memory[side].players;shift=8u*(at-D(PlayerCount));}else if(at==D(PlayerArrayBytes) || at==D(PlayerArrayBytes)+1) {field=&memory[side].bytes;shift=8u*(at-D(PlayerArrayBytes));}else {CHECK(at==D(SelectedDifficulty) || at==D(SelectedDifficulty)+1,"difficulty write");field=&memory[side].difficulty;shift=8u*(at-D(SelectedDifficulty));}*field=(uint16_t)((*field&~(255u<<shift))|((uint16_t)value<<shift));}
'''
  body=function(menu,'c_RunMainMenuAndAttractLoop')
  for scan,label in [('0x3e','players'),('0x3d','difficulty')]:
   start=body.index('if((uint8_t)r->ax=='+scan+') {');start=body.index('{',start)+1;end=body.index('goto redraw;',start);part=body[start:end];code+='static void ref_'+label+'(Regs *r) {'+part+'}\n'
  for tag,label in [('MENUS_MAIN_PLAYERS','players'),('MENUS_MAIN_DIFFICULTY','difficulty')]:
   body=function(bridge,'c_RunMainMenuAndAttractLoop');start=body.index('case '+tag+': {');start=body.index('{',start)+1;end=body.index('break;',start);code+='static void native_'+label+'(Regs *r) {'+body[start:end]+'}\n'
  code+='int main(void) {memory[0].players=nondet_u16();memory[0].bytes=nondet_u16();memory[0].difficulty=nondet_u16();memory[1]=memory[0];Regs r=nondet_regs(),s=r;r.ds=s.ds=0;int selected=nondet_u8()&1;side=0;if(selected) ref_players(&r);else ref_difficulty(&r);side=1;if(selected) native_players(&s);else native_difficulty(&s);equal(r,s);CHECK(memory[0].players==memory[1].players && memory[0].bytes==memory[1].bytes && memory[0].difficulty==memory[1].difficulty,"all raw word configurations and retained fields");return 0;}'
 else:
  code+='''static unsigned side,count[2];static Regs calls[2][3],responses[2];static uint16_t targets[2][3],returns[2][3];static uint8_t failure[2];
int ugh_call_near(uint16_t target,uint16_t ret,Regs *r) {unsigned at=count[side]++;CHECK(at<2,"two non-tail header draws");calls[side][at]=*r;targets[side][at]=target;returns[side][at]=ret;*r=responses[at];return failure[at];}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r) {unsigned at=count[side]++;CHECK(at==2,"third header draw is tail");calls[side][at]=*r;targets[side][at]=target;returns[side][at]=bank;return 0;}
'''
  code+=function(menu,'c_DrawMenuHeaderSprites').replace('c_DrawMenuHeaderSprites(','reference(')+function(bridge,'c_DrawMenuHeaderSprites').replace('c_DrawMenuHeaderSprites(','actual(')
  code+='int main(void) {for(unsigned i=0;i<2;i++) {responses[i]=nondet_regs();failure[i]=nondet_u8()&1;}Regs r=nondet_regs(),s=r;side=0;int first=reference(&r);side=1;int second=actual(&s);CHECK(first==second && count[0]==count[1],"header error prefix and draw count");equal(r,s);for(unsigned i=0;i<count[0];i++) {equal(calls[0][i],calls[1][i]);CHECK(targets[0][i]==targets[1][i] && returns[0][i]==returns[1][i],"ordered three sprite calls and frames");}return 0;}'
 harness=folder/'harness.c';harness.write_text(code);result=cbmc(harness,folder,[Path(__file__),ROOT/'verif/menus_spans.py',ROOT/'native/menus.c',ROOT/'native/menus.h',ROOT/'native/high_scores.c',ROOT/'native/high_scores.h',ROOT/'native/front_end.h',ROOT/'native/bridge/menus_bridge.c',ROOT/'native/bridge/front_end_support.h',ROOT/'c/menu.c',ROOT/'c/menu_helpers.c',ROOT/'c/scene.c'],unwind=unwind,timeout=60,extra=[*SOLVER,*extra]);print(a.entry,result['result'],result['seconds'],result['failures'][:3],flush=True);assert result['result']==('FAIL' if a.negative else 'PASS'),result['result']
if __name__=='__main__':main()
