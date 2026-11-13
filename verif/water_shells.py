"""Checked literal machine shell for the water passenger continuation."""
import argparse,re
from closure_support import ROOT,function
BRIDGE=ROOT/'native/bridge/passenger_water_bridge.c'
NAMES=['BeginPassengerResurfacing','UpdatePassengerResurfacing','BeginPassengerSinking','UpdatePassengerSinking',
       'BeginPassengerFloating','UpdatePassengerFloating','UpdateFloatingDestinationDisplay','UpdateFloatingQuestionDisplay',
       'UpdateFloatingPassengerApproach','IgnoreWaterbornePassengerState']
ENTRIES=['PW_BEGIN_RESURFACE','PW_RESURFACE','PW_BEGIN_SINK','PW_SINK','PW_BEGIN_FLOAT','PW_FLOAT','PW_DESTINATION','PW_QUESTION','PW_APPROACH','PW_IGNORE']
HELPERS=['shl','sar','inc','less','greater','actor_init','actor_frame','actor_tick','surface_y','state_jump','tail']
CONTEXT={'actor_init','actor_frame','actor_tick','surface_y','state_jump','tail'}

def adapt(body):
    for callee in CONTEXT:body=body.replace(callee+'(r,',callee+'(r,plan,').replace(callee+'(r)',callee+'(r,plan)')
    body=body.replace('ugh_dispatch(r->cs,target,r)','water_dispatch(r,plan,target)')
    for helper in HELPERS:body=re.sub(r'\b'+helper+r'\b','water_shell_'+helper,body)
    return body

def shells():
    raw=(ROOT/'c/actors.c').read_text()
    parts=['''#define READ(n,i) rd16(r->ds,(uint16_t)(D(n)+(i)))
#define WRITE(n,i,v) water_write(plan,r,(uint16_t)(D(n)+(i)),(uint16_t)(v))
#define A(n) READ(n,r->bx)
#define W(n,v) WRITE(n,r->bx,v)
#define DESC(n) rd16(r->ds,(uint16_t)(r->si+(n)))
static int water_shell_state_jump(Regs *r,WaterPlan *plan,uint16_t target);
static int water_shell_tail(Regs *r,WaterPlan *plan,unsigned field);
''']
    for name in HELPERS+['c_'+n for n in NAMES[:-1]]:
        body=function(raw,name)
        if name in CONTEXT or name.startswith('c_'):body=body.replace('Regs *r,','Regs *r,WaterPlan *plan,').replace('Regs *r)','Regs *r,WaterPlan *plan)')
        body=adapt(body)
        for n in NAMES:body=body.replace('EXPORT int c_'+n+'(','static int shell_'+n+'(')
        parts.append(body)
    parts+=['#undef '+n for n in ['READ','WRITE','A','W','DESC']]
    return '\n'.join(parts)+'\n'

def exports():
    text='\n'.join('int l1_'+n+'(Regs *r);' for n in NAMES[:-1])+'\n'
    for name,entry in zip(NAMES[:-1],ENTRIES[:-1]):
        text+=f'''EXPORT int c_{name}(Regs *r) {{
 WaterPlan plan;if(!water_prepare(r,{entry},&plan)) return l1_{name}(r);
 int status=shell_{name}(r,&plan);
 if(plan.bad || (!status && !water_complete(&plan))) return UGH_BAD_CALLBACK;
 if(!status && !plan.tail_seen && !water_projection(&plan,r)) return UGH_BAD_CALLBACK;
 return status;
}}
'''
    text+='EXPORT int c_IgnoreWaterbornePassengerState(Regs *r) {(void)r;PassengerWaterResult result=passenger_water_apply(PW_IGNORE,0,0,0);return result.failed?UGH_BAD_CALLBACK:UGH_OK;}\n'
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();old=BRIDGE.read_text();new=old
    for tag,text in [('SHELLS',shells()),('EXPORTS',exports())]:
        begin='/* WATER_'+tag+'_BEGIN */';end='/* WATER_'+tag+'_END */';i=new.index(begin)+len(begin);j=new.index(end,i);new=new[:i]+'\n'+text+new[j:]
    if a.write:BRIDGE.write_text(new)
    else:assert old==new,'water machine shell drift'
    print('PASS actual-L1 water shell')
if __name__=='__main__':main()
