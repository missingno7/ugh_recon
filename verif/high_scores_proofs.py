"""Split actual-C high-score properties under the accepted process envelope."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from high_scores_build import OUT
from high_scores_spans import sources,format_span,high_editor_span
from front_end_limits import cbmc
from adlx_lifetime_proofs import SOLVER

def main():
 p=argparse.ArgumentParser();p.add_argument('entry',choices=['row','qualification','format','complement','copy','insertion','file','editor']);p.add_argument('--negative',action='store_true');a=p.parse_args();folder=OUT/f'high-proof-{a.entry}{"-negative" if a.negative else ""}';folder.mkdir(parents=True,exist_ok=True)
 menu,helpers,services=sources();bridge=(ROOT/'native/bridge/high_scores_bridge.c').read_text();native=(ROOT/'native/high_scores.c').read_text();front=''
 if a.negative:
  if a.entry=='editor':native=native.replace("character-32u","character-31u")
  else:
   old,new={'row':('digits ? 14u','digits ? 13u'),'qualification':('candidate>=stored','candidate>stored'),'format':('digit+48u','digit+49u'),'complement':('byte^255u','byte^254u'),'copy':('source+21u','source+20u'),'insertion':('insertion->shift=3','insertion->shift=4'),'file':('return 107','return 106')}[a.entry];assert old in native;native=native.replace(old,new)
 code='#include "platform.h"\n#include "high_scores.h"\n#include "'+(ROOT/'native/bridge/front_end_support.h').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert(c,m)\nuint8_t nondet_u8(void);uint16_t nondet_u16(void);Regs nondet_regs(void);\n'+native+front
 code+='''static void equal(Regs r,Regs s) {CHECK(r.ax==s.ax && r.bx==s.bx && r.cx==s.cx && r.dx==s.dx && r.si==s.si && r.di==s.di && r.bp==s.bp && r.sp==s.sp && r.cs==s.cs && r.ds==s.ds && r.es==s.es && r.ss==s.ss && r.ip==s.ip && r.flags==s.flags,"complete output/frame");}
'''
 unwind=12;extra=[]
 if a.entry=='row':
  code+='''static uint8_t stride;static uint16_t bank;static unsigned reads;
uint8_t ugh_read(uint32_t address) {CHECK(address==(uint32_t)bank*16u+D(HighScoreRowStride),"one stride-byte field");reads++;return stride;}
'''
  for n in ['GetHighScoreRow','GetHighScoreDigits']:
   code+=function(helpers,'c_'+n).replace('c_'+n+'(','ref_'+n+'(')+function(bridge,'c_'+n).replace('c_'+n+'(','native_'+n+'(')
  code+='int main(void) {Regs r=nondet_regs();Regs s=r;bank=r.ds;stride=nondet_u8();int digits=nondet_u8()&1;if(digits) {ref_GetHighScoreDigits(&r);native_GetHighScoreDigits(&s);}else {ref_GetHighScoreRow(&r);native_GetHighScoreRow(&s);}equal(r,s);CHECK(reads==2,"exact one byte read per implementation");return 0;}'
 elif a.entry=='format':
  code+='''static uint8_t digit,written;
uint8_t ugh_read(uint32_t address) {CHECK(address==D(DecimalDigitBuffer),"one work byte read");return digit;}
void ugh_write(uint32_t address,uint8_t value) {CHECK(address==D(DecimalDigitBuffer),"one work byte written");written=value;}
static void reference(Regs *r) {'''+format_span()+'''}
int main(void) {Regs r=nondet_regs();r.ds=0;r.si=0;uint8_t significant=(uint8_t)(r.ax>>8);digit=nondet_u8();reference(&r);HighFormatDigit result=high_format_digit(digit,significant);CHECK(result.character==written && result.significant==(uint8_t)(r.ax>>8),"all16 digit/counter input bits, including wrapping ASCII");return 0;}
'''
 elif a.entry=='qualification':
  code+='''static uint8_t candidate[6],stored[6];
uint8_t ugh_read(uint32_t address) {if(address>=D(DecimalDigitBuffer) && address<D(DecimalDigitBuffer)+6) return candidate[address-D(DecimalDigitBuffer)];CHECK(address>=D(HighScoreRows)+14 && address<D(HighScoreRows)+20,"six stored characters");return stored[address-D(HighScoreRows)-14];}
int ugh_call_near(uint16_t target,uint16_t ret,Regs *r) {CHECK(target==G(GetHighScoreDigits) && ret==G(TestHighScoreQualification)+3,"actual row service frame");r->bx=D(HighScoreRows)+14;return 0;}
'''
  code+=function(menu,'c_TestHighScoreQualification').replace('c_TestHighScoreQualification(','reference(')+function(bridge,'c_TestHighScoreQualification').replace('c_TestHighScoreQualification(','actual(')
  code+='int main(void) {for(unsigned i=0;i<6;i++) {candidate[i]=nondet_u8();stored[i]=nondet_u8();}Regs r=nondet_regs();r.ds=0;Regs s=r;int first=reference(&r),second=actual(&s);CHECK(first==second,"return status");equal(r,s);return 0;}'
  extra=['--unwindset','reference.0:7,actual.0:7']
 elif a.entry in ['complement','copy','editor']:
  code+='''typedef struct Event {uint32_t address;uint8_t value;} Event;static Event writes[2][16];static unsigned side,nw[2],nr[2];static uint8_t delivered;
uint8_t ugh_read(uint32_t address) {(void)address;nr[side]++;return delivered;}
void ugh_write(uint32_t address,uint8_t value) {CHECK(nw[side]<16,"ordered write log bound");writes[side][nw[side]].address=address;writes[side][nw[side]++].value=value;}
static void compare_writes(void) {CHECK(nr[0]==nr[1] && nw[0]==nw[1],"access counts");for(unsigned i=0;i<nw[0];i++) CHECK(writes[0][i].address==writes[1][i].address && writes[0][i].value==writes[1][i].value,"ordered physical byte writes");}
'''
  if a.entry=='complement':
   ref=function(services,'c_ComplementHighScoreTable');ref=ref[ref.index('        uint16_t o='):ref.index('    } while')]
   actual=function(bridge,'c_ComplementHighScoreTable');actual=actual[actual.index('        uint16_t o='):actual.index('    } while')]
   code+='static void reference(Regs *r) {'+ref+'}\nstatic void actual(Regs *r) {HighDescending cursor={r->si,(uint16_t)(r->si+1u)};'+actual+'}\nint main(void) {Regs r=nondet_regs();__CPROVER_assume(r.si<107);Regs s=r;delivered=nondet_u8();side=0;reference(&r);side=1;actual(&s);equal(r,s);compare_writes();return 0;}'
  elif a.entry=='copy':
   ref=function(menu,'c_CopyHighScoreRowDown');ref=ref[ref.index('        set_al'):ref.index('    } while')]
   actual=function(bridge,'c_CopyHighScoreRowDown');actual=actual[actual.index('        set_al'):actual.index('    } while')]
   code+='static void reference(Regs *r) {'+ref+'}\nstatic void actual(Regs *r) {HighCopy copy={r->bx,r->di,(uint16_t)(r->dx+1u)};'+actual+'}\nint main(void) {Regs r=nondet_regs();__CPROVER_assume(r.dx<20);r.di=(uint16_t)(r.bx+21u);Regs s=r;delivered=nondet_u8();side=0;reference(&r);side=1;actual(&s);equal(r,s);compare_writes();HighCopy start=high_copy_begin(s.bx);CHECK(start.destination==(uint16_t)(s.bx+21u) && start.remaining==20,"fixed destination spacing and20-byte extent independent of stride");return 0;}'
  else:
   code+='#define MCALL(n,ret) do {(void)(ret);} while(0)\nstatic int reference(Regs *r) {'+high_editor_span()+'}\nstatic int actual(Regs *r) {'+high_editor_span(True)+'}\nint main(void) {Regs r=nondet_regs();Regs s=r;side=0;int first=reference(&r);side=1;int second=actual(&s);CHECK(first==second,"continue,reset,finish editor outcomes");equal(r,s);compare_writes();return 0;}'
 elif a.entry=='insertion':
  code+='''static uint8_t qualified[5],memory[2][32];static unsigned side,count[2];static uint16_t rows[2][12],targets[2][12];
uint8_t ugh_read(uint32_t at) {CHECK(at<32,"canonical active frame");return memory[side][at];}
void ugh_write(uint32_t at,uint8_t value) {CHECK(at<32,"canonical active frame");memory[side][at]=value;}
int ugh_call_near(uint16_t target,uint16_t ret,Regs *r) {(void)ret;CHECK(count[side]<12,"rank/shift call bound");rows[side][count[side]]=r->cx;targets[side][count[side]++]=target;if(target==G(TestHighScoreQualification)) {CHECK((uint8_t)r->cx<5,"five qualification rows");flag(r,CF,qualified[(uint8_t)r->cx]);}return 0;}
#define MCALL(n,ret) do {int st=ugh_call_near(G(n),ret,r);if(st) return st;} while(0)
'''
  for text,name in [(menu,'reference'),(bridge,'actual')]:
   body=function(text,'c_InsertHighScoreAndClearScore');part=body[body.index('    r->cx&=0xff00'):body.index('    r->cx=r->bp;')].replace('goto clear_score;','return 1;')
   code+='static int '+name+'(Regs *r) {'+part+'return 0;}\n'
  code+='int main(void) {for(unsigned i=0;i<5;i++) qualified[i]=nondet_u8()&1;Regs r=nondet_regs();r.ss=0;r.sp=24;Regs s=r;side=0;int first=reference(&r);side=1;int second=actual(&s);CHECK(first==second,"reject or insert");equal(r,s);CHECK(count[0]==count[1],"service count");for(unsigned i=0;i<count[0];i++) CHECK(rows[0][i]==rows[1][i] && targets[0][i]==targets[1][i],"qualification rank and descending shift order including rank4 copy");for(unsigned i=0;i<32;i++) CHECK(memory[0][i]==memory[1][i],"saved rank word");return 0;}'
  unwind=33;extra=['--unwindset','reference.0:6,reference.1:5,actual.0:6,actual.1:5']
 else:
  code+='''typedef struct Event {uint16_t kind,first,second,b,c,d,bank;} Event;static Event events[2][6];static unsigned side,n[2],dos[2];static uint16_t handle[2],reply[3];static uint8_t carry[3],status[3];
uint8_t ugh_read(uint32_t at) {CHECK(at==D(HighScoreFileHandle) || at==D(HighScoreFileHandle)+1,"handle read");return (uint8_t)(handle[side]>>(8u*(at-D(HighScoreFileHandle))));}
void ugh_write(uint32_t at,uint8_t value) {CHECK(at==D(HighScoreFileHandle) || at==D(HighScoreFileHandle)+1,"handle write");unsigned shift=8u*(at-D(HighScoreFileHandle));handle[side]=(uint16_t)((handle[side]&~(255u<<shift))|((uint16_t)value<<shift));}
static void event(uint16_t kind,uint16_t first,uint16_t second,Regs *r) {CHECK(n[side]<6,"file event bound");Event e={kind,first,second,r->bx,r->cx,r->dx,r->ds};events[side][n[side]++]=e;}
int ugh_call_near(uint16_t target,uint16_t ret,Regs *r) {event(0,target,ret,r);return 0;}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r) {event(1,bank,target,r);return 0;}
int platform_interrupt(uint8_t number,Regs *r) {CHECK(number==0x21,"DOS only");event(2,r->ax,0,r);unsigned at=dos[side]++;CHECK(at<3,"three DOS services maximum");r->ax=reply[at];flag(r,CF,carry[at]);return status[at];}
'''
  for label in ['SaveHighScores','LoadHighScores']:
   code+=function(menu,'c_'+label).replace('c_'+label+'(','ref_'+label+'(')+function(bridge,'c_'+label).replace('c_'+label+'(','native_'+label+'(')
  code+='int main(void) {for(unsigned i=0;i<3;i++) {reply[i]=nondet_u16();carry[i]=nondet_u8()&1;status[i]=nondet_u8()&1;}Regs r=nondet_regs();r.ds=0;Regs s=r;handle[0]=handle[1]=nondet_u16();int saving=nondet_u8()&1;side=0;int first=saving ? ref_SaveHighScores(&r) : ref_LoadHighScores(&r);side=1;int second=saving ? native_SaveHighScores(&s) : native_LoadHighScores(&s);CHECK(first==second && n[0]==n[1] && dos[0]==dos[1] && handle[0]==handle[1],"DOS errors, transport errors,handle and complement prefix");equal(r,s);for(unsigned i=0;i<n[0];i++) CHECK(events[0][i].kind==events[1][i].kind && events[0][i].first==events[1][i].first && events[0][i].second==events[1][i].second && events[0][i].b==events[1][i].b && events[0][i].c==events[1][i].c && events[0][i].d==events[1][i].d && events[0][i].bank==events[1][i].bank,"ordered protocol and arguments");return 0;}'
  unwind=12;extra=['--unwindset','native_SaveHighScores.0:5,native_LoadHighScores.0:5']
 harness=folder/'harness.c';harness.write_text(code);result=cbmc(harness,folder,[Path(__file__),ROOT/'verif/high_scores_spans.py',ROOT/'native/high_scores.c',ROOT/'native/high_scores.h',ROOT/'native/front_end.h',ROOT/'native/bridge/high_scores_bridge.c',ROOT/'native/bridge/front_end_support.h',ROOT/'c/menu.c',ROOT/'c/menu_helpers.c',ROOT/'c/game_services.c'],unwind=unwind,timeout=60,extra=[*SOLVER,*extra]);print(a.entry,result['result'],result['seconds'],result['failures'][:3],flush=True);assert result['result']==('FAIL' if a.negative else 'PASS'),result['result']
if __name__=='__main__':main()
