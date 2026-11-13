"""Actual journal append/consume, request completion and tail-binding lemmas."""
import argparse,json
from pathlib import Path
from closure_support import ROOT,function
from delivery_build import OUT
from delivery_limits import cbmc,SMT

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('piece',choices=['emit','consume','complete','dispatch']);p.add_argument('mode',choices=['outputs','frame','dependencies']);p.add_argument('--timeout',type=int,default=120);a=p.parse_args()
    folder=OUT/'kernel'/(a.piece+'-'+a.mode);folder.mkdir(parents=True,exist_ok=True)
    core=ROOT/'native/passenger_delivery.c';bridge=ROOT/'native/bridge/passenger_delivery_bridge.c';resources=ROOT/'native/actor_resources.c';raw=bridge.read_text()
    declaration=raw[raw.index('typedef struct DeliveryPlan'):raw.index('static uint16_t delivery_word')]
    code='#include "ugh.h"\n#define UINT16_MAX 65535u\n#include "'+(ROOT/'native/passenger_delivery.h').as_posix()+'"\n'+declaration
    code+='''#define CHECK(c,m) __CPROVER_assert((c),(m))
static _Bool projected;static unsigned calls;static uint16_t observed_target,observed_craft;
static int delivery_projection(DeliveryPlan *p,Regs *r) {(void)p;(void)r;return projected;}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r) {CHECK(bank==GAME_SEG,"tail bank");calls++;observed_target=target;observed_craft=r->di;return 17;}
'''
    for n in ['actor_phase_aliases']:code+=function(resources.read_text(),n)
    for n in ['delivery_phase','delivery_identity','delivery_consume','delivery_complete','delivery_dispatch']:code+=function(raw,n)
    code+=function(core.read_text(),'pd_emit')
    code+='''int main(void) {
 DeliveryPlan p;Regs r;r.cs=GAME_SEG;r.ds=DATA_SEG;
 unsigned actor;__CPROVER_assume(actor<16);r.bx=(uint16_t)(2u*actor);
 p.world.player_slots=2;p.world.platform_count=10;
'''
    if a.piece=='emit':
        code+='''size_t base;__CPROVER_assume(base<32);p.result.count=base;
 PassengerDeliveryField field;size_t index;uint16_t value;
'''
        if a.mode=='outputs':code+='''pd_emit(&p.result,field,index,value);
 CHECK(p.result.count==base+1 && p.result.writes[base].field==field && p.result.writes[base].index==index && p.result.writes[base].value==value,"append value/order at arbitrary prefix length");
'''
        elif a.mode=='frame':code+='''unsigned probe;__CPROVER_assume(probe<sizeof(p.result));uint8_t *cell=(uint8_t *)&p.result+probe;uint8_t before=*cell;
 pd_emit(&p.result,field,index,value);
 if(!(cell>=(uint8_t *)&p.result.count && cell<(uint8_t *)&p.result.count+sizeof(p.result.count)) &&
    !(cell>=(uint8_t *)&p.result.writes[base] && cell<(uint8_t *)&p.result.writes[base]+sizeof(p.result.writes[base]))) CHECK(*cell==before,"every other journal/control byte retained");
'''
        else:code+='''PassengerDeliveryResult other;other.count=base;pd_emit(&p.result,field,index,value);pd_emit(&other,field,index,value);
 CHECK(p.result.count==other.count && p.result.writes[base].field==other.writes[base].field && p.result.writes[base].index==other.writes[base].index && p.result.writes[base].value==other.writes[base].value,"no prefix/suffix/control dependence of append");
'''
    elif a.piece=='complete':
        if a.mode=='outputs':code+='''int actual=delivery_complete(&p);
 CHECK(actual==(!p.bad && p.consumed==p.result.count && p.spawn_seen==p.result.spawn_bonus && p.sound_seen==p.result.bonus_sound && p.tail_seen==(p.result.next!=PD_NEXT_NONE) && !p.result.finish_pending),"normal completion iff all journal/services/tail/pending consumed");
'''
        elif a.mode=='frame':code+='''unsigned probe;__CPROVER_assume(probe<sizeof(p));uint8_t *cell=(uint8_t *)&p+probe;uint8_t before=*cell;delivery_complete(&p);CHECK(*cell==before,"completion predicate writes no byte");
'''
        else:code+='''DeliveryPlan other;
 other.bad=p.bad;other.consumed=p.consumed;other.result.count=p.result.count;other.spawn_seen=p.spawn_seen;other.result.spawn_bonus=p.result.spawn_bonus;other.sound_seen=p.sound_seen;other.result.bonus_sound=p.result.bonus_sound;other.tail_seen=p.tail_seen;other.result.next=p.result.next;other.result.finish_pending=p.result.finish_pending;
 CHECK(delivery_complete(&p)==delivery_complete(&other),"completion depends only on its declared protocol cells");
'''
    elif a.piece=='consume':
        code+='''size_t count;__CPROVER_assume(count<=32);p.result.count=count;
 uint16_t address,expected;_Bool byte;size_t old=p.consumed;int valid=old<count;
 uint16_t value;
'''
        if a.mode=='frame':code+='''unsigned probe;__CPROVER_assume(probe<sizeof(p));uint8_t *cell=(uint8_t *)&p+probe;uint8_t before=*cell;
'''
        if a.mode=='dependencies':code+='''DeliveryPlan other=p;PassengerStoneSlot unrelated;other.slot=unrelated;Regs second=r;
'''
        code+='value=delivery_consume(&p,&r,address,expected,byte);\n'
        if a.mode=='outputs':code+='''CHECK(p.consumed==(valid?old+1:old),"consume exactly one live entry");
 if(!valid) CHECK(p.bad,"empty journal rejected");
 if(!p.bad) CHECK(value==expected,"accepted publication returns the actual expected value");
'''
        elif a.mode=='frame':
            terms=[f'(cell>=(uint8_t *)&p.{n} && cell<(uint8_t *)&p.{n}+sizeof(p.{n}))' for n in ['consumed','bad','published_phase','phase_written']]
            code+='if(!('+' || '.join(terms)+')) CHECK(*cell==before,"consume changes only cursor/error/published-phase bookkeeping");\n'
        else:code+='''uint16_t other_value=delivery_consume(&other,&second,address,expected,byte);
 CHECK(value==other_value && p.bad==other.bad && p.consumed==other.consumed && p.published_phase==other.published_phase && p.phase_written==other.phase_written,"unborrowed native slot does not affect journal decoding");
'''
    else:
        code+='''unsigned next;__CPROVER_assume(next<=PD_NEXT_WATER);p.result.next=(PassengerDeliveryNext)next;
 const uint16_t targets[]={0,G(BeginPassengerPlatformWait),G(BeginPassengerDestinationDisplay),G(BeginPassengerQuestionDisplay),G(BeginPassengerApproach),G(BoardPassenger),G(DeliverPassenger),G(BeginPassengerResurfacing)};
 uint16_t target;_Bool projection;projected=projection;calls=0;
 int critical=next==PD_NEXT_BOARD || next==PD_NEXT_DELIVER;
 int allowed=next!=PD_NEXT_NONE && !p.bad && !p.tail_seen && p.consumed==p.result.count && target==targets[next] && projected && (!critical || (p.result.selected>=0 && p.result.selected<2 && r.di==2u*(unsigned)p.result.selected));
'''
        if a.mode=='frame':code+='''unsigned probe;__CPROVER_assume(probe<sizeof(p));uint8_t *cell=(uint8_t *)&p+probe;uint8_t before=*cell;Regs before_regs=r;
'''
        if a.mode=='dependencies':code+='''DeliveryPlan other=p;PassengerStoneSlot unrelated;other.slot=unrelated;Regs second=r;
'''
        code+='int status=delivery_dispatch(&r,&p,target);\n'
        if a.mode=='outputs':code+='''CHECK((status==17)==allowed && calls==(unsigned)allowed,"tail acceptance exactly matches request/count/target/projection/selected contract");
 if(calls) CHECK(observed_target==targets[next] && p.tail_seen && (!critical || observed_craft==2u*(unsigned)p.result.selected),"native selected craft is passed to the actual tail");
'''
        elif a.mode=='frame':code+='''if(!(cell>=(uint8_t *)&p.bad && cell<(uint8_t *)&p.bad+sizeof(p.bad)) && !(cell>=(uint8_t *)&p.tail_seen && cell<(uint8_t *)&p.tail_seen+sizeof(p.tail_seen))) CHECK(*cell==before,"tail helper changes only error/consumed-tail cells");
 CHECK(r.ax==before_regs.ax && r.bx==before_regs.bx && r.cx==before_regs.cx && r.dx==before_regs.dx && r.si==before_regs.si && r.di==before_regs.di && r.bp==before_regs.bp && r.sp==before_regs.sp && r.cs==before_regs.cs && r.ds==before_regs.ds && r.es==before_regs.es && r.ss==before_regs.ss && r.ip==before_regs.ip && r.flags==before_regs.flags,"binding preserves the complete pre-callee machine shell");
'''
        else:code+='''calls=0;int second_status=delivery_dispatch(&second,&other,target);
 CHECK(status==second_status && p.bad==other.bad && p.tail_seen==other.tail_seen,"tail protocol independent of unrelated slot fields");
'''
    code+='return 0;}\n';source=folder/'harness.c';source.write_text(code)
    result=cbmc(source,folder,[Path(__file__),core,bridge,resources,ROOT/'native/passenger_delivery.h',ROOT/'native/actors.h',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=3,timeout=a.timeout,extra=[*SMT,'--no-array-field-sensitivity'])
    print(a.piece,a.mode,json.dumps({k:result[k] for k in ['result','seconds','peak_private_bytes','failures']}),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
