"""Maintain an actual-L1 machine shell consuming only native journal values."""
import argparse,re
from closure_support import ROOT,function
BRIDGE=ROOT/'native/bridge/passenger_delivery_bridge.c'
NAMES=['BeginPassengerPlatformWait','UpdatePassengerPlatformWait','BeginPassengerDestinationDisplay','UpdatePassengerDestinationDisplay',
       'BeginPassengerQuestionDisplay','UpdatePassengerQuestionDisplay','BeginPassengerApproach','UpdatePassengerApproach',
       'BoardWaterbornePassenger','BoardPassenger','UpdateCarriedPassenger','DeliverPassenger']
ENTRIES=['PD_BEGIN_WAIT','PD_WAIT','PD_BEGIN_DESTINATION','PD_DESTINATION','PD_BEGIN_QUESTION','PD_QUESTION','PD_BEGIN_APPROACH','PD_APPROACH','PD_RESCUE','PD_BOARD','PD_CARRIED','PD_DELIVER']
def shells():
    output='/* Actual L1 expressions reconstruct the machine shell; native outputs supply every owned persistent store. */\n'
    groups=[('actors.c',['less','greater','actor_init','tail','state_jump'],[NAMES[i] for i in [0,2,4,6,9,10]]),
        ('actors_states.c',['lt','gt','shift','inc','push','pop','effect','frame','actor_tick','submerged','water_swap','platform_player','display','tail'],[NAMES[i] for i in [1,3,5,7,8,11]])]
    contextual={'actor_init','tail','state_jump','effect','frame','actor_tick','water_swap','display'}
    for group,(module,helpers,names) in enumerate(groups):
        raw=(ROOT/'c'/module).read_text()
        if group==0:
            parts=['#define READ(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))',
                '#define WRITE(n,i,v) delivery_write16(plan,r,(uint16_t)(D(n)+(i)),(uint16_t)(v))',
                '#define A(n) READ(n,r->bx)','#define W(n,v) WRITE(n,r->bx,v)','#define DESC(n) rd16(r->ds,(uint16_t)(r->si+(n)))',
                'static int state_jump(Regs *r,DeliveryPlan *plan,uint16_t target);','static int tail(Regs *r,DeliveryPlan *plan,unsigned field);']
        else:
            parts=['#define R(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))',
                '#define W(n,i,v) delivery_write16(plan,r,(uint16_t)(D(n)+(i)),(uint16_t)(v))',
                '#define A(n) R(n,r->bx)','#define B(n,v) W(n,r->bx,v)','#define F(n) rd16(r->ds,(uint16_t)(r->si+(n)))',
                'static int tail(Regs *r,DeliveryPlan *plan,unsigned field);']
        for name in helpers+['c_'+n for n in names]:
            body=function(raw,name)
            if name in contextual or name.startswith('c_'):
                body=body.replace('Regs *r,','Regs *r,DeliveryPlan *plan,').replace('Regs *r)','Regs *r,DeliveryPlan *plan)')
            for callee in contextual:body=body.replace(callee+'(r,',callee+'(r,plan,').replace(callee+'(r)',callee+'(r,plan)')
            body=body.replace('ugh_dispatch(r->cs,target,r)','delivery_dispatch(r,plan,target)').replace('ugh_dispatch(r->cs,F(field),r)','delivery_dispatch(r,plan,F(field))')
            body=body.replace('ugh_dispatch(UGH_S_C_PlayAdlibEffect,UGH_O_C_PlayAdlibEffect,r)','delivery_sound(r,plan,UGH_S_C_PlayAdlibEffect,UGH_O_C_PlayAdlibEffect)')
            body=body.replace('ugh_call_near(','delivery_near(r,plan,').replace(',r);',');') if 'ugh_call_near(' in body else body
            body=body.replace('wr8(r->ds,','delivery_write8(plan,r,')
            parts.append(body)
        for helper in helpers:parts=[re.sub(r'\b'+helper+r'\b',f'pd_shell{group}_{helper}',part) for part in parts]
        text='\n'.join(parts)
        for name in names:text=re.sub(r'\bEXPORT int c_'+name+r'\b','static int shell_'+name,text)
        output+=text+'\n'+'\n'.join('#undef '+n for n in ['READ','WRITE','A','W','DESC','R','B','F'])+'\n'
    return output
def exports():
    text='\n'.join('int l1_'+name+'(Regs *r);' for name in NAMES)+'\n'
    for name,entry in zip(NAMES,ENTRIES):
        text+=f'''EXPORT int c_{name}(Regs *r) {{
    DeliveryPlan plan;
    if(!delivery_prepare(r,{entry},&plan)) return l1_{name}(r);
    int status=shell_{name}(r,&plan);
    if(plan.bad || (!status && (plan.consumed!=plan.result.count || plan.spawn_seen!=plan.result.spawn_bonus || plan.sound_seen!=plan.result.bonus_sound))) return UGH_BAD_CALLBACK;
    return status;
}}
'''
    return text
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args();old=BRIDGE.read_text();new=old
    for tag,text in [('SHELLS',shells()),('EXPORTS',exports())]:
        begin=f'/* DELIVERY_{tag}_BEGIN */';end=f'/* DELIVERY_{tag}_END */';start=new.index(begin)+len(begin);finish=new.index(end,start)
        new=new[:start]+'\n'+text+new[finish:]
    if a.write:BRIDGE.write_text(new)
    else:assert new==old,'machine shell drift'
    print('PASS actual-L1 delivery shell')
if __name__=='__main__':main()
