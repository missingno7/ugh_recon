"""Small actual-code effect, frame, dependence and retained-caller properties."""
import argparse,json
from closure_support import ROOT,function
from demo_scene_build import OUT,pair,FILES
from demo_scene_limits import cbmc
def make(mode,folder):
    inputs=pair(folder);code='#include "pair.inc"\n'+(ROOT/'verif/demo_scene_harness.c').read_text()
    if mode in ['fade','width']:
        code+='''int main(void) {uint16_t input[38],offset;uint8_t byte;Regs r;
 for(unsigned i=0;i<38;i++)ram[i]=input[i];width_byte=byte;width_offset=offset;actor_index=0;unsigned watch;__CPROVER_assume(watch<PS_LOG_LIMIT);observe_index=watch;
'''+f'compare({0 if mode=="fade" else 1},r);return 0;}}\n'
    elif mode=='noop':
        code+=function((ROOT/'c/demo_scripts.c').read_text(),'c_loc_0B4E')+'int main(void) {Regs r,before;r=before;CHECK(c_loc_0B4E(&r)==UGH_OK && equal_regs(r,before),"retained unexplained RET only preserves state");return 0;}\n'
    elif mode=='constructor':
        code+='int main(void) {unsigned k;__CPROVER_assume(k<5);DemoPresentationCursor c=demo_presentation_begin((DemoPresentationKind)k);CHECK(c.kind==(DemoPresentationKind)k && c.phase==(k==DEMO_PRESENT_RUN?DP_INITIALIZE:DP_PREPARE),"all five entry cursors");return 0;}\n'
    elif mode=='terminal':
        code+='''int main(void) {DemoScenePlan plan={0};unsigned kind;__CPROVER_assume(kind>0 && kind<5);plan.active=1;plan.cursor=(DemoPresentationCursor){(DemoPresentationKind)kind,DP_WRAPPER_DONE};DemoPresentationInput observed;plan.observed=observed;
 uint16_t words[38];for(unsigned i=0;i<38;i++)ram[i]=words[i];Regs r,before;r=before;r.cs=GAME_SEG;r.ds=DATA_SEG;before=r;
 dp_finish(&r,&plan);CHECK(plan.completed && !plan.pending && plan.cursor.phase==DP_TERMINAL && plan.cursor.kind==(DemoPresentationKind)kind,"normal wrapper completion consumes exact terminal action");CHECK(equal_regs(r,before),"terminal consumption preserves all ABI state");for(unsigned i=0;i<38;i++)CHECK(ram[i]==words[i],"terminal consumption writes no RAM");return 0;}
'''
    elif mode=='frame':
        code+='''int main(void) {DemoPresentationCursor cursor;DemoPresentationInput input;unsigned phase,kind;__CPROVER_assume(phase<DEMO_PRESENT_PHASE_COUNT && kind<5);cursor.phase=(DemoPresentationPhase)phase;cursor.kind=(DemoPresentationKind)kind;
 unsigned object,byte;__CPROVER_assume(object<2);uint8_t *cell=object?(uint8_t *)&input:(uint8_t *)&cursor.kind;unsigned size=object?sizeof(input):sizeof(cursor.kind);__CPROVER_assume(byte<size);cell+=byte;uint8_t before=*cell;
 (void)demo_presentation_next(&cursor,&input);CHECK(*cell==before,"every native input and immutable cursor-kind byte retained");return 0;}
'''
    elif mode=='dependence':
        code+='''int main(void) {unsigned phase,kind;__CPROVER_assume(phase<DEMO_PRESENT_PHASE_COUNT && kind<5);DemoPresentationCursor a={(DemoPresentationKind)kind,(DemoPresentationPhase)phase},b=a;DemoPresentationInput x,y;
 switch(phase) {
 case DP_LOOP:y.fade_level=x.fade_level;y.exit_code=x.exit_code;break;
 case DP_PALETTE_AFTER:y.palette_work=x.palette_work;y.fade_step=x.fade_step;break;
 case DP_WATER:y.water_y=x.water_y;break;
 case DP_TEST_AFTER:y.finished=x.finished;y.fade_step=x.fade_step;break;
 case DP_JOYSTICK_AFTER:y.joystick_idle=x.joystick_idle;break;
 case DP_KEYBOARD_AFTER:y.key_word=x.key_word;break;
 case DP_FADE_CHECK:y.fade_step=x.fade_step;break;
 case DP_FADE_LEVEL:y.fade_level=x.fade_level;break;
 default:break;
 }
 DemoPresentationAction l=demo_presentation_next(&a,&x),r=demo_presentation_next(&b,&y);
 CHECK(l.kind==r.kind && l.service==r.service && l.value==r.value && a.kind==b.kind && a.phase==b.phase,"every event and next cut independent of every other input");return 0;}
'''
    else:
        scene=(ROOT/'c/scene.c').read_text();body=function(scene,'c_RunGameFromPassword');a=body.index('    push(r,0x11); int st=scene_far_call',body.index('CALL(PlayPreGameDemo'));b=body.index('    CALL(BlackenVgaPalette',a);fragment=body[a:b]
        assert fragment in function((ROOT/'native/bridge/actor_render_bridge.c').read_text(),'c_RunGameFromPassword')
        fragment=fragment.replace('scene_far_call','reference_scene_far_call').replace('push(','reference_push(')
        code+='''#undef CALL
#define CALL(n,ret) do {int status=ugh_call_near(G(n),ret,r);if(status)return status;} while(0)
static int caller(Regs *r) {'''+fragment+'''return UGH_OK;}
int main(void) {Regs r,post;uint16_t words[38],after[4];for(unsigned i=0;i<38;i++)ram[i]=words[i];for(unsigned i=0;i<4;i++)arbitrary_ram[i]=after[i];arbitrary_after=post;
 r.cs=GAME_SEG;r.ds=DATA_SEG;r.ss=0x9000;r.sp=0x1000;cut_services=1;cut_status=0;modern=0;observe_index=0;CHECK(caller(&r)==0,"normal pregame caller continues");CHECK(service_count==2 && last_target==G(ResetScoreLivesAndMultiplier),"arbitrary pregame AX/flags never gate reset-score continuation");return 0;}
'''
    return code,[*inputs,ROOT/'verif/demo_scene_harness.c',ROOT/'verif/demo_scene_kernel.py']+([ROOT/'native/bridge/actor_render_bridge.c'] if mode=='ignored-pregame' else [])
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['fade','width','noop','constructor','terminal','frame','dependence','ignored-pregame']);p.add_argument('--timeout',type=int,default=600);a=p.parse_args();folder=OUT/'kernel'/a.mode;folder.mkdir(parents=True,exist_ok=True);code,inputs=make(a.mode,folder);source=folder/'harness.c';source.write_text(code)
    result=cbmc(source,folder,inputs,unwind=42,timeout=a.timeout,defines=['-D__CPROVER__','-DACTOR_VERIFY'],extra=['--no-array-field-sensitivity'])
    print(json.dumps({k:result[k] for k in ['result','seconds','peak_private_bytes','failures']}),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
