"""Actual water append/consume/completion/selected-tail and no-op lemmas."""
import argparse,json
from pathlib import Path
from closure_support import ROOT,function
from water_build import OUT
from water_limits import cbmc,SMT
def main():
    p=argparse.ArgumentParser();p.add_argument('piece',choices=['emit','consume','complete','dispatch','ignore']);p.add_argument('mode',choices=['outputs','frame','dependencies']);p.add_argument('--timeout',type=int,default=600);a=p.parse_args()
    folder=OUT/'kernel'/(a.piece+'-'+a.mode);folder.mkdir(parents=True,exist_ok=True);bridge=ROOT/'native/bridge/passenger_water_bridge.c';native=ROOT/'native/passenger_water.c';resources=ROOT/'native/actor_resources.c';raw=bridge.read_text()
    code='#include "ugh.h"\n#include "'+(ROOT/'native/passenger_water.h').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert((c),(m))\n'
    code+=raw[raw.index('typedef struct WaterPlan'):raw.index('static uint16_t water_word')]
    code+='''static _Bool projected;static unsigned calls;static uint16_t called_target,called_craft;
static int water_projection(WaterPlan *p,Regs *r) {(void)p;(void)r;return projected;}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r) {CHECK(bank==GAME_SEG,"water tail bank");calls++;called_target=target;called_craft=r->di;return 17;}
'''
    code+=function(resources.read_text(),'actor_phase_aliases')
    for n in ['water_phase','water_target','water_consume','water_complete','water_dispatch']:code+=function(raw,n)
    if a.piece=='ignore':code+='#include "'+native.as_posix()+'"\n'+function(raw,'c_IgnoreWaterbornePassengerState')
    else:code+=function(native.read_text(),'pw_emit')
    code+='''int main(void) {
 WaterPlan plan;Regs r;r.cs=GAME_SEG;r.ds=DATA_SEG;unsigned actor;__CPROVER_assume(actor<16);r.bx=(uint16_t)(2u*actor);
 size_t players;__CPROVER_assume(players==1 || players==2);plan.world.player_count=players;plan.world.platform_count=10;
'''
    if a.piece=='emit':
        code+='''size_t start;__CPROVER_assume(start<32);plan.result.count=start;PassengerWaterField field;size_t index;uint16_t value;
'''
        if a.mode=='frame':code+='''unsigned byte;__CPROVER_assume(byte<sizeof(plan.result));uint8_t *cell=(uint8_t *)&plan.result+byte;uint8_t before=*cell;
'''
        if a.mode=='dependencies':code+='PassengerWaterResult other;other.count=start;\n'
        code+='pw_emit(&plan.result,field,index,value);\n'
        if a.mode=='outputs':code+='CHECK(plan.result.count==start+1 && plan.result.writes[start].field==field && plan.result.writes[start].index==index && plan.result.writes[start].value==value,"append exact arguments at arbitrary prefix");\n'
        elif a.mode=='frame':code+='if(!(cell>=(uint8_t *)&plan.result.count && cell<(uint8_t *)&plan.result.count+sizeof(plan.result.count)) && !(cell>=(uint8_t *)&plan.result.writes[start] && cell<(uint8_t *)&plan.result.writes[start]+sizeof(plan.result.writes[start]))) CHECK(*cell==before,"every other journal/control byte retained");\n'
        else:code+='pw_emit(&other,field,index,value);CHECK(plan.result.count==other.count && plan.result.writes[start].field==other.writes[start].field && plan.result.writes[start].index==other.writes[start].index && plan.result.writes[start].value==other.writes[start].value,"append independent of prefix payload and other control");\n'
    elif a.piece=='consume':
        code+='size_t count;__CPROVER_assume(count<=32);plan.result.count=count;size_t start=plan.consumed;uint16_t address,expected;\n'
        if a.mode=='frame':code+='unsigned byte;__CPROVER_assume(byte<sizeof(plan));uint8_t *cell=(uint8_t *)&plan+byte;uint8_t before=*cell;\n'
        if a.mode=='dependencies':code+='WaterPlan other=plan;PassengerStoneSlot unrelated;other.slot=unrelated;Regs second=r;\n'
        code+='uint16_t value=water_consume(&plan,&r,address,expected);\n'
        if a.mode=='outputs':code+='CHECK(plan.consumed==(start<count?start+1:start),"consume exactly one live entry");if(start>=count) CHECK(plan.bad,"empty journal rejected");if(!plan.bad) CHECK(value==expected,"accepted value matches actual expected store");\n'
        elif a.mode=='frame':
            terms=[f'(cell>=(uint8_t *)&plan.{n} && cell<(uint8_t *)&plan.{n}+sizeof(plan.{n}))' for n in ['consumed','bad','published_phase','phase_written']];code+='if(!('+' || '.join(terms)+')) CHECK(*cell==before,"decoder changes only protocol cursor/error/phase cells");\n'
        else:code+='uint16_t second_value=water_consume(&other,&second,address,expected);CHECK(value==second_value && plan.bad==other.bad && plan.consumed==other.consumed && plan.published_phase==other.published_phase && plan.phase_written==other.phase_written,"decoder independent of native working slot");\n'
    elif a.piece=='complete':
        if a.mode=='outputs':code+='CHECK(water_complete(&plan)==(!plan.bad && plan.consumed==plan.result.count && plan.tail_seen==(plan.result.next!=PW_NEXT_NONE)),"normal completion iff all journal and next requests consumed");\n'
        elif a.mode=='frame':code+='unsigned byte;__CPROVER_assume(byte<sizeof(plan));uint8_t *cell=(uint8_t *)&plan+byte;uint8_t before=*cell;water_complete(&plan);CHECK(*cell==before,"completion predicate writes no byte");\n'
        else:code+='WaterPlan other;other.bad=plan.bad;other.consumed=plan.consumed;other.result.count=plan.result.count;other.tail_seen=plan.tail_seen;other.result.next=plan.result.next;CHECK(water_complete(&plan)==water_complete(&other),"completion depends only on protocol fields");\n'
    elif a.piece=='dispatch':
        code+='''unsigned next;__CPROVER_assume(next<=PW_NEXT_BOARD);plan.result.next=(PassengerWaterNext)next;
 uint16_t target;_Bool projection;projected=projection;calls=0;
 const uint16_t targets[]={0,G(BeginPassengerFloating),G(BeginPassengerSinking),G(BeginPassengerDestinationDisplay),G(BeginPassengerQuestionDisplay),G(BeginPassengerApproach),G(BoardWaterbornePassenger)};
 int valid=next && !plan.bad && !plan.tail_seen && plan.consumed==plan.result.count && target==targets[next] && projected &&
  ((next!=PW_NEXT_BOARD && next!=PW_NEXT_DESTINATION) || (plan.result.selected>=0 && (size_t)plan.result.selected<players && r.di==2u*(unsigned)plan.result.selected));
'''
        if a.mode=='frame':code+='unsigned byte;__CPROVER_assume(byte<sizeof(plan));uint8_t *cell=(uint8_t *)&plan+byte;uint8_t before=*cell;Regs before_regs=r;\n'
        if a.mode=='dependencies':code+='WaterPlan other=plan;PassengerStoneSlot unrelated;other.slot=unrelated;Regs second=r;\n'
        code+='int status=water_dispatch(&r,&plan,target);\n'
        if a.mode=='outputs':code+='CHECK((status==17)==valid && calls==(unsigned)valid,"tail accepted iff target/journal/projection/selected contract holds");if(calls) CHECK(called_target==targets[next] && plan.tail_seen && ((next!=PW_NEXT_BOARD && next!=PW_NEXT_DESTINATION) || called_craft==2u*(unsigned)plan.result.selected),"selected native craft is consumed at actual scan/boarding tail");\n'
        elif a.mode=='frame':
            code+='if(!(cell>=(uint8_t *)&plan.bad && cell<(uint8_t *)&plan.bad+sizeof(plan.bad)) && !(cell>=(uint8_t *)&plan.tail_seen && cell<(uint8_t *)&plan.tail_seen+sizeof(plan.tail_seen))) CHECK(*cell==before,"dispatch changes only error and tail-consumption cells");\n'
            code+='CHECK('+' && '.join('r.'+f+'==before_regs.'+f for f in ['ax','bx','cx','dx','si','di','bp','sp','cs','ds','es','ss','ip','flags'])+',"dispatch preserves full pre-callee register state");\n'
        else:code+='int again=water_dispatch(&second,&other,target);CHECK(status==again && plan.bad==other.bad && plan.tail_seen==other.tail_seen,"dispatch independent of unrelated working slot");\n'
    else:
        code+='Regs any;r=any;Regs before=r;PassengerWaterResult out=passenger_water_apply(PW_IGNORE,0,0,0);int status=c_IgnoreWaterbornePassengerState(&r);\n'
        code+='CHECK(status==UGH_OK && !out.count && !out.failed && out.next==PW_NEXT_NONE && out.selected==-1,"actual null-safe no-op result");\n'
        code+='CHECK('+' && '.join('r.'+f+'==before.'+f for f in ['ax','bx','cx','dx','si','di','bp','sp','cs','ds','es','ss','ip','flags'])+',"no-op preserves every register and flag");\n'
    code+='return 0;}\n';source=folder/'harness.c';source.write_text(code)
    result=cbmc(source,folder,[Path(__file__),bridge,native,resources,ROOT/'native/passenger_water.h',ROOT/'native/actors.h',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=3,timeout=a.timeout,defines=['-DUINT16_MAX=65535u'],extra=[*SMT,'--no-array-field-sensitivity'])
    print(a.piece,a.mode,json.dumps({k:result[k] for k in ['result','seconds','peak_private_bytes','failures']}),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
