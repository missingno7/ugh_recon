"""Actual C at branch/service cuts, with explicit captured-result seams."""
import argparse,json
from closure_support import ROOT
from demo_scene_build import OUT,pair
from demo_scene_pieces import pieces,modern,reference
from demo_scene_limits import cbmc,SMT

def make(key,folder):
    inputs=pair(folder);p=pieces()[key]
    code='#include "pair.inc"\n'+(ROOT/'verif/demo_scene_harness.c').read_text()
    code+='''
#undef W
#undef CALL
#define W(n,v) wr16(r->ds,D(n),(uint16_t)(v))
#define CALL(n,ret) do {int status=ugh_call_near(G(n),ret,r);if(status)return status;} while(0)
static int reference_piece(Regs *r) {'''+reference(p['fragment'])+'''return UGH_OK;}
#undef W
#undef CALL
#define W(n,v) dp_write(r,&plan,D(n),(uint16_t)(v))
#define CALL(n,ret) do {dp_before(r,&plan,G(n));int status=ugh_call_near(G(n),ret,r);dp_resume(r,&plan);if(status)return status;} while(0)
static int modern_piece(Regs *r) {DemoScenePlan plan={0};plan.active=1;plan.cursor=(DemoPresentationCursor){'''+p['kind']+','+p['phase']+'''};
'''+p['seam']+modern(p['fragment'])+'''
 if(!service_count) {
'''+('CHECK(plan.cursor.phase==DP_ERASE,"palette-result equality seam");' if key=='palette-result' else 'CHECK(plan.cursor.phase==DP_LOOP,"actual loopback equality seam");' if key in ['finished-result','joystick-result','keyboard-result','fade-check','fade-level'] else '')+'''
 }return UGH_OK;}
int main(void) {
 uint16_t words[38],post[4],offset;uint8_t byte;Regs initial,post_registers;unsigned watch;__CPROVER_assume(watch<PS_LOG_LIMIT);observe_index=watch;
 for(unsigned i=0;i<38;i++)ram[i]=words[i];for(unsigned i=0;i<4;i++)arbitrary_ram[i]=post[i];width_byte=byte;width_offset=offset;
 arbitrary_after=post_registers;actor_index=0;cut_services=1;int returned_status;__CPROVER_assume(returned_status!=0);cut_status=returned_status;
 initial.cs=GAME_SEG;initial.ds=DATA_SEG;initial.ss=0x9000;initial.sp=0x1000;Regs *r=&initial;
'''+p['seam'].replace('plan.observed.palette_work=r->cx;','').replace('plan.observed.finished=(r->flags&CF)!=0;','').replace('plan.observed.joystick_idle=(r->flags&ZF)!=0;','').replace('plan.observed.key_word=r->ax;','')+'''
 uint16_t before[38],after[38];for(unsigned i=0;i<38;i++)before[i]=ram[i];Regs a=initial,b=initial;
 modern=0;observations=service_count=0;int left=reference_piece(&a);expected_observations=observations;
 for(unsigned i=0;i<38;i++){after[i]=ram[i];ram[i]=before[i];}uint8_t old=width_byte;
 modern=1;observations=service_count=0;int right=modern_piece(&b);
 CHECK(left==right && equal_regs(a,b),"all registers/status at branch cut");CHECK(observations==expected_observations,"all cut events consumed");for(unsigned i=0;i<38;i++)CHECK(ram[i]==after[i],"full current RAM/stack frame");CHECK(width_byte==old,"unchanged width at service cut");return 0;
}
'''
    return code,[*inputs,ROOT/'verif/demo_scene_harness.c',ROOT/'verif/demo_scene_pieces.py',ROOT/'verif/demo_scene_proof.py']
def main():
    p=argparse.ArgumentParser();p.add_argument('piece',choices=pieces());p.add_argument('--timeout',type=int,default=600);p.add_argument('--sat',action='store_true');a=p.parse_args();folder=OUT/'proofs'/a.piece;folder.mkdir(parents=True,exist_ok=True);code,inputs=make(a.piece,folder);source=folder/'harness.c';source.write_text(code)
    result=cbmc(source,folder,inputs,unwind=42,timeout=a.timeout,defines=['-D__CPROVER__','-DACTOR_VERIFY'],extra=[*([] if a.sat else SMT),'--no-array-field-sensitivity'])
    print(json.dumps({k:result[k] for k in ['result','seconds','peak_private_bytes','failures']}),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
