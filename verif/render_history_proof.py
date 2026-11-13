"""Per-slot actual-C outputs, arbitrary-byte frames and dependence."""
import argparse,json
from closure_support import ROOT,save
from render_history_build import OUT,pair
from render_history_shells import OPS
from render_history_limits import cbmc,SMT
HISTORY=['pixel_x','pixel_y','previous_x','previous_y','erase_sprite','erase_overlay_sprite']
OWNED=[[4,5],[0,1,2,3],[],[4],[0,1,2,3],[4]]
READ_HISTORY=[[2,3,4,5],[0,1],[0,1],[2,3,4],[0,1],[]]
READ_INPUT=[['sprite','overlay_sprite'],['position.x32','position.y32','sprite'],['sprite','overlay_sprite'],['sprite'],['position.x32','position.y32','sprite'],[]]
def make(op,mode,folder):
    inputs=pair(folder);code='#include "pair.inc"\n'+(ROOT/'verif/render_history_harness.c').read_text()+'\nint main(void) {\n'
    if mode=='outputs':
        code+='uint16_t words[10];for(unsigned i=0;i<10;i++) ram[i]=words[i];\n'
        code+='Regs r,a,b;service_after[0]=a;service_after[1]=b;int s,t;__CPROVER_assume(s>=0 && s<=5 && t>=0 && t<=5);service_status[0]=s;service_status[1]=t;actor_index=0;\n'
        code+=f'compare({op},r);\n'
    elif mode=='native-frame':
        code+='ActorRenderStorage storage={0};ActorRenderHistory here,other;ActorRenderInput input;storage.slots[0]=here;unsigned slot;__CPROVER_assume(slot>0 && slot<16);storage.slots[slot]=other;\n'
        code+='unsigned object,byte;__CPROVER_assume(object<3);uint8_t *cell=object==0?(uint8_t *)&storage.slots[0]:object==1?(uint8_t *)&storage.slots[slot]:(uint8_t *)&input;size_t size=object==2?sizeof(input):sizeof(here);__CPROVER_assume(byte<size);cell+=byte;uint8_t before=*cell;\n'
        code+=f'(void)actor_render_apply((ActorRenderOperation){op},&storage,0,&input);\n'
        allowed=['(object==0 && cell>=(uint8_t *)&storage.slots[0].'+HISTORY[n]+' && cell<(uint8_t *)&storage.slots[0].'+HISTORY[n]+'+sizeof(uint16_t))' for n in OWNED[op]]
        code+='if(!('+(' || '.join(allowed) or '0')+')) CHECK(*cell==before,"every unowned history/input/other-slot byte");\n'
    elif mode=='dependencies':
        code+='ActorRenderStorage left={0},right={0};ActorRenderHistory a,b;ActorRenderInput x,y;left.slots[0]=a;right.slots[0]=b;\n'
        for n in READ_HISTORY[op]:code+=f'right.slots[0].{HISTORY[n]}=left.slots[0].{HISTORY[n]};\n'
        for n in READ_INPUT[op]:code+=f'y.{n}=x.{n};\n'
        code+=f'ActorRenderResult l=actor_render_apply((ActorRenderOperation){op},&left,0,&x),r=actor_render_apply((ActorRenderOperation){op},&right,0,&y);CHECK(l.count==r.count,"complete result count dependence");\n'
        code+='for(unsigned i=0;i<l.count;i++) {ActorRenderEvent a=l.events[i],b=r.events[i];CHECK(a.kind==b.kind && a.field==b.field && a.value==b.value && a.x==b.x && a.y==b.y && a.sprite==b.sprite,"all published values independent of other inputs");}\n'
        # Hidden draws publish nothing. Unwritten prior values are covered by
        # the frame relation, not asserted equal between different histories.
        for n in OWNED[op]:code+=f'if(l.count) CHECK(left.slots[0].{HISTORY[n]}==right.slots[0].{HISTORY[n]},"published history output dependence");\n'
    code+='return 0;}\n'
    return code,[*inputs,ROOT/'verif/render_history_harness.c',ROOT/'verif/render_history_proof.py']
def main():
    p=argparse.ArgumentParser();p.add_argument('operation',choices=OPS);p.add_argument('mode',choices=['outputs','native-frame','dependencies']);p.add_argument('--timeout',type=int,default=600);a=p.parse_args()
    folder=OUT/'proofs'/(a.operation+'-'+a.mode);folder.mkdir(parents=True,exist_ok=True);code,inputs=make(OPS.index(a.operation),a.mode,folder);source=folder/'harness.c';source.write_text(code)
    result=cbmc(source,folder,inputs,unwind=18,timeout=a.timeout,defines=['-D__CPROVER__','-DACTOR_VERIFY','-DUINT16_MAX=65535u'],extra=SMT)
    print(json.dumps({k:result[k] for k in ['result','seconds','peak_private_bytes','failures']}),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
