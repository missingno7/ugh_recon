"""Retain a mechanically checked L1 register shell in the owned bridge.

Actual L1 bodies, with only helper renames/context arguments and persistent
stores routed to the native output journal. No algorithm model substitutes for
either implementation. --write is for this unit's initial shell maintenance;
normal reproduction checks that the maintained shell still equals extraction.
"""
import argparse,re
from closure_support import ROOT,function
BRIDGE=ROOT/'native/bridge/passenger_itinerary_bridge.c'
NAMES=['ReadPassengerJourneyLeg','WaitForPassengerPlatform','PlacePassengerOnPlatform','AnimatePassengerArrival',
       'WalkPassengerToExit','BeginPassengerDeparture','AnimatePassengerDeparture','IgnoreActorState']
ENTRIES=['IT_READ','IT_WAIT','IT_PLACE','IT_ARRIVAL','IT_WALK','IT_BEGIN_DEPARTURE','IT_DEPARTURE','IT_IGNORE']
def shells():
    output='/* Derived machine shell: expected expressions are diagnostics; native journal values alone are published. */\n'
    groups=[('actors.c',['shl','sar','less','actor_init','actor_tick','actor_frame','tail','state_jump'],NAMES[1:-1]),
            ('actors_states.c',['shift','byte_sub','byte_dec'],NAMES[:1])]
    contextual={'actor_init','actor_tick','actor_frame','tail','state_jump'}
    for group,(module,helpers,names) in enumerate(groups):
        raw=(ROOT/'c'/module).read_text();parts=[]
        if group==0:
            parts += ['#define READ(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))',
                      '#define WRITE(n,i,v) itinerary_write16(plan,r,(uint16_t)(D(n)+(i)),(uint16_t)(v))',
                      '#define A(n) READ(n,r->bx)','#define W(n,v) WRITE(n,r->bx,v)',
                      '#define DESC(n) rd16(r->ds,(uint16_t)(r->si+(n)))',
                      'static int state_jump(Regs *r,ItineraryPlan *plan,uint16_t target);',
                      'static int tail(Regs *r,ItineraryPlan *plan,unsigned field);']
        else:
            parts += ['#define R(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))',
                      '#define W(n,i,v) itinerary_write16(plan,r,(uint16_t)(D(n)+(i)),(uint16_t)(v))',
                      '#define A(n) R(n,r->bx)','#define B(n,v) W(n,r->bx,v)',
                      '#define F(n) rd16(r->ds,(uint16_t)(r->si+(n)))']
        for name in helpers+['c_'+n for n in names]:
            body=function(raw,name)
            if name in contextual or name.startswith('c_'):
                body=body.replace('Regs *r,','Regs *r,ItineraryPlan *plan,').replace('Regs *r)','Regs *r,ItineraryPlan *plan)')
            if name in ['shl','sar','less','shift','byte_sub','byte_dec']:pass
            for callee in contextual:
                body=body.replace(callee+'(r,',callee+'(r,plan,').replace(callee+'(r)',callee+'(r,plan)')
            body=body.replace('ugh_dispatch(r->cs,target,r)','itinerary_dispatch(r,plan,target)')
            body=body.replace('ugh_dispatch(r->cs,r->ax,r)','itinerary_dispatch(r,plan,r->ax)')
            body=body.replace('wr8(r->ds,','itinerary_write8(plan,r,')
            parts.append(body)
        for helper in helpers:
            parts=[re.sub(r'\b'+helper+r'\b',f'it_shell{group}_{helper}',part) for part in parts]
        text='\n'.join(parts)
        for name in names:text=re.sub(r'\bEXPORT int c_'+name+r'\b','static int shell_'+name,text)
        text+='\n'+'\n'.join('#undef '+n for n in ['READ','WRITE','A','W','DESC','R','B','F'])+'\n'
        output+=text
    return output
def exports():
    text='\n'.join('int l1_'+name+'(Regs *r);' for name in NAMES[:-1])+'\n'
    for name,entry in zip(NAMES,ENTRIES):
        if entry=='IT_IGNORE':
            text+='EXPORT int c_IgnoreActorState(Regs *r) {\n    (void)r;ItineraryResult result=itinerary_apply(IT_IGNORE,0,0,0);return result.failed?UGH_BAD_CALLBACK:UGH_OK;\n}\n';continue
        text+=f'''EXPORT int c_{name}(Regs *r) {{
    ItineraryPlan plan;
    if(!itinerary_prepare(r,{entry},&plan)) return l1_{name}(r);
    int status=shell_{name}(r,&plan);
    if(plan.bad || plan.consumed!=plan.result.count) return UGH_BAD_CALLBACK;
    return status;
}}
'''
    return text
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    old=BRIDGE.read_text();new=old
    for tag,text in [('SHELLS',shells()),('EXPORTS',exports())]:
        begin=f'/* ITINERARY_{tag}_BEGIN */';end=f'/* ITINERARY_{tag}_END */'
        start=new.index(begin)+len(begin);finish=new.index(end,start);new=new[:start]+'\n'+text+new[finish:]
    if a.write:BRIDGE.write_text(new)
    else:assert new==old,'maintained machine shell differs from actual L1 extraction'
    print('PASS actual-L1 shell extraction')
if __name__=='__main__':main()
