"""Actual water C: outputs, native/RAM frame, full-slot frame and dependence."""
import argparse,json,re
from pathlib import Path
from closure_support import ROOT,function
from water_build import OUT,pair
from water_shells import HELPERS,adapt
from water_pieces import pieces,INPUTS,OUTPUTS,MEMBERS,RAM,CONTRACTED
from water_limits import cbmc,SMT

def wrappers(body):
    ref=body
    for name in HELPERS:ref=re.sub(r'\b'+name+r'\b','wa_ref_'+name,ref)
    common=''
    if re.search(r'\bstatus\s*=',body) and not re.search(r'\bint\b[^;\n]*\bstatus\s*=',body):common='int status=0;\n'
    macros='''#define READ(n,i) wa_read(r->ds,(uint16_t)(D(n)+(i)))
#define A(n) READ(n,r->bx)
#define DESC(n) wa_read(r->ds,(uint16_t)(r->si+(n)))
'''
    undef='\n'.join('#undef '+s for s in ['READ','WRITE','A','W','DESC'])+'\n'
    return macros+'''#define WRITE(n,i,v) wa_write(r->ds,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define W(n,v) WRITE(n,r->bx,v)
static int reference_piece(Regs *r) {
'''+common+ref+'\nreturn UGH_OK;}\n'+undef+macros+'''#define WRITE(n,i,v) water_write(plan,r,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define W(n,v) WRITE(n,r->bx,v)
static int bridge_piece(Regs *r,WaterPlan *plan) {(void)plan;
'''+common+adapt(body)+'\nreturn UGH_OK;}\n'+undef

def invoke(call,relation,name='nret'):
    return f'int {name}=0;'+call+';\n' if relation in ('void','apply','motion') else f'int {name}='+call+';\n'

def frame_allowed(key):
    names=[]
    for field in OUTPUTS[key]:names+=RAM[field]
    addresses=['D('+n+')' for n in names]
    if key=='begin-resurface':addresses.append('(uint16_t)(D(PlatformActorOccupants)+2u*ram.actor[5])')
    return ' || '.join('(watched_bank==DATA_SEG && (watched_offset=='+a+' || watched_offset==(uint16_t)('+a+'+1u)))' for a in addresses) or '0'

def make(key,mode,folder):
    call,body,phase,relation=pieces()[key];inputs=pair(folder);inc=folder/'pair.inc';text=inc.read_text();native=ROOT/'native/passenger_water.c'
    text=text.replace('#include "'+native.as_posix()+'"',native.read_text())
    contracted=key in CONTRACTED
    if mode=='outputs' and contracted:
        # The actual complete predicate is discharged independently. Output
        # plus native/RAM byte frames establish its conjunction at this cut.
        checks=['plan->consumed==plan->result.count']
        for member in OUTPUTS[key]:
            if member=='animation':checks+=['plan->slot.animation.byte_offset==wa_read(r->ds,D(ActorAnimationByteOffsets))','plan->slot.animation.countdown==wa_read(r->ds,D(ActorAnimationCountdowns))']
            else:checks.append('plan->slot.'+member+'==wa_read(r->ds,D('+RAM[member][0]+'))')
        text=text.replace(function(text,'water_projection'),'static int water_projection(WaterPlan *plan,Regs *r) {return '+' && '.join(checks)+';}\n')
    if contracted:
        for name in ['pw_tick','pw_frame','actor_tick','actor_frame','water_shell_actor_tick','water_shell_actor_frame']:
            old=function(text,name);sig=old[:old.index('{')].strip();actual=re.sub(r'\b'+name+r'(?=\s*\()', 'actual_'+name,old,count=1)
            text=text.replace(old,sig+';\n'+actual,1)
    if mode in ('native-frame','full-frame','dependencies'):
        actual=function(text,'pw_emit')
        replacement='''static void pw_emit(PassengerWaterResult *out,PassengerWaterField field,size_t index,uint16_t value) {
 CHECK(out->count<32,"actual append lemma prefix bound");
'''
        if mode=='dependencies':replacement+='if(out->count==observe_index) {observe_seen[epoch]=1;observed[epoch]=(PassengerWaterWrite){field,index,value};}\n'
        else:replacement+='(void)field;(void)index;(void)value;\n'
        text=text.replace(actual,replacement+'out->count++;}\n',1)
    inc.write_text(text)
    header='#define PIECE\n#include "ugh.h"\n#include "'+(ROOT/'native/passenger_water.h').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert((c),(m))\n'
    header+='static unsigned piece_kind;static size_t observe_index;static unsigned epoch;static _Bool observe_seen[2];static PassengerWaterWrite observed[2];\n'
    support=(ROOT/'verif/water_harness.c').read_text().split('#ifndef PIECE')[0]
    code=header+'#include "pair.inc"\n'+support
    if contracted:
        contract=(ROOT/'verif/water_contracts.c').read_text()
        if mode=='ram-frame':contract='\n'.join(l for l in contract.splitlines() if not l.lstrip().startswith(('CHECK(nt==1 &&','CHECK(nf==1 &&')))+'\n'
        code+=contract
    code+=wrappers(body)
    code+='''int main(void) {
 WaterRam arbitrary;ram=arbitrary;unsigned pair;__CPROVER_assume(pair<3);
 actor_index=0;configure(pair);__CPROVER_assume(ram.players==1 || ram.players==2);
 for(unsigned i=0;i<4;i++) for(unsigned j=0;j<2;j++) __CPROVER_assume(ram.frames[i][j]!=65535u);
'''
    if key=='begin-resurface':code+='__CPROVER_assume(ram.actor[5]<10);ram.actor[7]=(uint16_t)(2u*ram.actor[5]);\n'
    code+=f'WaterPlan plan;seed_view(&plan,{phase});\n'
    code+='''PassengerStoneSlot slot=plan.slot;ActorRenderHistory render=plan.render;PassengerWaterWorld world=plan.world;
 PassengerWaterResult out=plan.result;
 size_t selected;__CPROVER_assume(selected<ram.players);
'''
    if key=='approach-motion':code+='out.selected=(int)selected;\n'
    if key=='frame':
        code+='''unsigned kind;__CPROVER_assume(kind<4);piece_kind=kind;
 uint16_t bank[256];size_t count;uint16_t base;__CPROVER_assume(count>0 && count<256);
 __CPROVER_assume(base>=0x0e20u && (uint32_t)base+2u*count<0x1020u);
 general_words=bank;general_base=base;general_count=count;ram.type[23+kind]=base;
 __CPROVER_assume(!(ram.actor[16]&1u) && ram.actor[16]/2u<=count);
 __CPROVER_assume(bank[0]!=65535u);if(ram.actor[16]/2u<count) __CPROVER_assume(bank[ram.actor[16]/2u]!=65535u);
 bank[count]=65535u;plan.type.animations[kind]=(ActorAnimation){bank,count};
'''
    if contracted:code+='WaterContract any;contract=any;nt=nf=rt=rf=bt=bf=0;\n'
    if mode=='outputs':
        code+='''WaterRam initial=ram;Regs r;r.ds=DATA_SEG;r.cs=GAME_SEG;r.ss=1;r.sp=36864u;r.bx=0;r.si=ram.actor[0];r.di=(uint16_t)(2u*selected);
'''
        if key=='resurface-cross':code+='r.ax=ram.actor[11];CHECK(r.ax==slot.position.y32,"integration Y equality at crossing seam");\n'
        code+='Regs bridge=r;\n'+invoke(call,relation)
        code+='''CHECK(!out.failed,"admitted native branch");plan.slot=slot;plan.result=out;
 store_count=tail_calls=0;modern_calls=0;int expected=reference_piece(&r);
 unsigned ref_count=store_count,ref_tails=tail_calls;uint16_t target=tail_target,craft=tail_craft;
 ram=initial;expected_count=ref_count;store_count=tail_calls=0;modern_calls=1;
 int actual=bridge_piece(&bridge,&plan);
 CHECK(actual==expected && store_count==ref_count && tail_calls==ref_tails && (!ref_tails || (target==tail_target && craft==tail_craft)),"all ordered stores, status and immediate tail observations");
 CHECK(!plan.bad && plan.consumed==plan.result.count && water_projection(&plan,&bridge),"full active native working-state projection at matching cut");
 CHECK(water_target(out.next)==(ref_tails?target:0),"all native next requests consumed");
 CHECK(!actual?water_complete(&plan):1,"normal completion consumes every request");
 CHECK(r.ax==bridge.ax && r.bx==bridge.bx && r.cx==bridge.cx && r.dx==bridge.dx && r.si==bridge.si && r.di==bridge.di && r.bp==bridge.bp && r.sp==bridge.sp && r.cs==bridge.cs && r.ds==bridge.ds && r.es==bridge.es && r.ss==bridge.ss && r.ip==bridge.ip && r.flags==bridge.flags,"complete registers flags continuation");
'''
        if relation=='tick':code+='CHECK(nret==expected,"tick gate equality");\n'
        if relation=='success':code+='CHECK(nret==1,"successful animation branch");\n'
        if relation=='gate':code+='CHECK((nret!=0)==(ref_tails!=0),"early branch equality");\n'
        if key=='resurface-motion':code+='CHECK(slot.position.y32==r.ax,"published integration Y equals crossing input AX");\n'
        if key in ('float-select','approach-select'):code+='CHECK(out.selected==(ref_tails && target==G(BeginPassengerQuestionDisplay)?-1:(key_unused)),"selected placeholder");\n'
        # Selection is independently checked, not inferred from final DI after
        # an animation helper has overwritten it.
        if key=='float-select':code=code.replace('(ref_tails && target==G(BeginPassengerQuestionDisplay)?-1:(key_unused))','(ref_tails?(int)(r.di/2u):-1)')
        if key=='approach-select':code=code.replace('(ref_tails && target==G(BeginPassengerQuestionDisplay)?-1:(key_unused))','(ref_tails?-1:(int)(r.di/2u))')
        if key=='approach-motion':code+='CHECK(out.selected==(int)selected,"selected craft survives animation and binds boarding");\n'
        if key not in ('float-select','approach-select','approach-motion'):code+='CHECK(out.selected==-1,"no spurious selected craft");\n'
        if key=='float-select':code+='if(plan.type.id==ACTOR_PASSENGER_TWO_WATER) CHECK(out.next==PW_NEXT_NONE && out.selected==-1,"second water identity cannot request rescue");\n'
        if contracted:code+='CHECK(nt==rt && nt==bt && nf==rf && nf==bf,"all tick/frame seam outputs consumed exactly once");\n'
    elif mode=='dependencies':
        code+='PassengerStoneSlot independent;independent.type=slot.type;ActorRenderHistory other_render;other_render.pixel_x=render.pixel_x;other_render.pixel_y=render.pixel_y;\n'
        for member in INPUTS[key]:code+=f'independent.{member}=slot.{member};\n'
        code+='PassengerWaterResult other=out;size_t probe;__CPROVER_assume(probe<32);observe_index=probe;epoch=0;observe_seen[0]=observe_seen[1]=0;\n'+invoke(call,relation)
        if contracted:code+='unsigned old_nt=nt,old_nf=nf;uint16_t c=count_in,u=cursor_in,p=period_in,f=frame_cursor,k=frame_kind;nt=nf=0;\n'
        second=call.replace('&out','&other').replace('&slot','&independent').replace('&render','&other_render').replace('out=','other=')
        code+='epoch=1;\n'+invoke(second,relation,'second')+'CHECK(nret==second,"no other slot input changes branch control");\n'
        for member in OUTPUTS[key]:
            if member=='animation':code+='CHECK(slot.animation.byte_offset==independent.animation.byte_offset && slot.animation.countdown==independent.animation.countdown,"animation dependence");\n'
            else:code+=f'CHECK(slot.{member}==independent.{member},"owned output dependence");\n'
        code+='''CHECK(out.count==other.count && out.next==other.next && out.selected==other.selected && out.failed==other.failed,"all semantic result dependence");
 CHECK(observe_seen[0]==observe_seen[1],"same arbitrary append position exists");
 if(observe_seen[0]) CHECK(observed[0].field==observed[1].field && observed[0].index==observed[1].index && observed[0].value==observed[1].value,"all append argument dependence through actual append lemma");
'''
        if contracted:code+='CHECK(nt==old_nt && nf==old_nf && (!nt || (c==count_in && u==cursor_in && p==period_in)) && (!nf || (f==frame_cursor && k==frame_kind)),"helper input dependence at seams");\n'
    elif mode in ('native-frame','full-frame'):
        if mode=='full-frame':
            code+='PassengerStoneSlot arbitrary_other;\n'
            for member in MEMBERS:
                if member not in INPUTS[key]:code+=f'slot.{member}=arbitrary_other.{member};\n'
        code+='''unsigned object,byte;__CPROVER_assume(object<OBJECTS);
 uint8_t *cell=object==0?(uint8_t *)&slot:object==1?(uint8_t *)&render:object==2?(uint8_t *)&world:object==3?(uint8_t *)&plan.type:RESULT_CELL;
 size_t length=object==0?sizeof(slot):object==1?sizeof(render):object==2?sizeof(world):object==3?sizeof(plan.type):RESULT_LENGTH;
 __CPROVER_assume(byte<length);cell+=byte;uint8_t before=*cell;
'''+invoke(call,relation)
        allowed=[f'(object==0 && cell>=(uint8_t *)&slot.{n} && cell<(uint8_t *)&slot.{n}+sizeof(slot.{n}))' for n in OUTPUTS[key]]
        allowed += [f'(object==4 && cell>=(uint8_t *)&out.{n} && cell<(uint8_t *)&out.{n}+sizeof(out.{n}))' for n in ['count','next','selected','failed']]
        allowed.append('(object==4 && cell>=(uint8_t *)out.writes && cell<(uint8_t *)out.writes+out.count*sizeof(out.writes[0]))')
        code+='if(!('+' ||\n'.join(allowed)+')) CHECK(*cell==before,"every other native slot/history/world/resource/result byte retained");\n(void)nret;\n'
    else:
        code+='''Regs r;r.ds=DATA_SEG;r.cs=GAME_SEG;r.ss=1;r.sp=36864u;r.bx=0;r.si=ram.actor[0];r.di=(uint16_t)(2u*selected);
'''
        if key=='resurface-cross':code+='r.ax=ram.actor[11];\n'
        code+='''uint16_t probe_bank,offset;uint8_t byte;watched_bank=probe_bank;watched_offset=offset;watched_value=byte;watching=1;
 store_count=tail_calls=0;modern_calls=0;reference_piece(&r);
'''+f'if(!({frame_allowed(key)})) CHECK(watched_value==byte,"every other RAM byte including every other slot retained");\n'
    if key=='frame':code=code.replace('OBJECTS','6').replace('RESULT_CELL','object==4?(uint8_t *)&out:(uint8_t *)bank').replace('RESULT_LENGTH','object==4?sizeof(out):sizeof(bank)')
    else:code=code.replace('OBJECTS','5').replace('RESULT_CELL','(uint8_t *)&out').replace('RESULT_LENGTH','sizeof(out)')
    code+='return 0;}\n'
    return code,[*inputs,ROOT/'verif/water_harness.c',ROOT/'verif/water_pieces.py',ROOT/'verif/water_contracts.c',Path(__file__)]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('piece',choices=pieces());p.add_argument('mode',choices=['outputs','native-frame','ram-frame','full-frame','dependencies']);p.add_argument('--timeout',type=int,default=600);a=p.parse_args()
    folder=OUT/'scalar'/(a.piece+'-'+a.mode);folder.mkdir(parents=True,exist_ok=True);code,inputs=make(a.piece,a.mode,folder);source=folder/'harness.c';source.write_text(code)
    defines=['-D__CPROVER__','-DACTOR_VERIFY','-DUINT16_MAX=65535u']+(['-DGENERAL_FRAME'] if a.piece=='frame' else [])
    result=cbmc(source,folder,inputs,unwind=40,timeout=a.timeout,defines=defines,extra=[*SMT,'--no-array-field-sensitivity','--unwindset','wa_ref_actor_frame.0:3,water_shell_actor_frame.0:3,pw_float_select.0:3,pw_destination_gate.0:3,pw_approach_select.0:3,reference_piece.0:3,bridge_piece.0:3'])
    print(json.dumps({k:result[k] for k in ['result','seconds','peak_private_bytes','failures']}),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
