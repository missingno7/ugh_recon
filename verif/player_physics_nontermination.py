"""Retained wrapping-water/up-scan divergence: induction and bounded witnesses."""
import argparse,subprocess,sys
from closure_support import ROOT,function,compile_c,receipt,save
from player_physics_build import OUT,FILES
from player_physics_pair import pair
from player_physics_limits import cbmc
def proof(timeout):
    folder=OUT/'proofs/nontermination';folder.mkdir(parents=True,exist_ok=True);source=folder/'harness.c'
    source.write_text('#include "'+(ROOT/'native/player_physics.c').as_posix()+'''"
int main(void) {
 PlayerPhysicsView v={0};PlayerPhysicsWorld w={0};PlayerPhysicsProcess p;
 player_physics_begin(&p,&v,&w);uint16_t cursor;__CPROVER_assume((cursor&31u)!=0);
 p.cursor=cursor;p.candidate=32768;p.positive=0;p.sample=0;p.rows=65535;p.columns=0;
 pp_vertical_hit(&p);
 __CPROVER_assert(p.stage==PP_VERTICAL_SCAN && p.count==0,"actual no-hit backedge repeats without publishing position");
 __CPROVER_assert((p.cursor&31u)==(cursor&31u) && p.cursor!=32768,"inductive residue excludes the target at every wrap");
 uint16_t after=p.cursor;pp_vertical_scan(&p);PlayerPhysicsEvent event=p.journal[0];
 __CPROVER_assert(p.count==1 && event.kind==PP_SAMPLE && event.probe.columns==0 && event.probe.rows==65535 && event.probe.pixel_x==v.pixel_x && event.probe.pixel_y==v.pixel_y && p.cursor==after,"actual up scan reuses the same immutable sample and cursor");
 return 0;
}
''')
    result=cbmc(source,folder,[*FILES,ROOT/'verif/player_physics_nontermination.py'],unwind=5,timeout=timeout,extra=['--no-array-field-sensitivity'])
    print('nontermination invariant',result['result'],flush=True);assert result['result']=='PASS'
def witnesses():
    folder=OUT/'nontermination';inputs=pair(folder);raw=(ROOT/'verif/player_physics_harness.c').read_text()
    old=function(raw,'px_near');new=old.replace('return status;','if(read_number>=320u)status=UGH_BUDGET;return status;');assert new!=old
    raw=raw.replace(old,new)
    raw='#define PLAYER_PHYSICS_NO_MAIN\n'+raw+'''
int main(void) {
 initialize();actor_index=0;pattern=0;ram.player[1]=1;ram.player[3]=1042;ram.player[4]=0;ram.water=1042;
 compare(seed(),0);CHECK(read_number==320 && ram.player[1]==1 && ram.player[3]==1042 && ram.player[6]==0 && ram.player[4]==65535,"32-probe original/native diagnostic prefix");
 uint32_t first[10];unsigned n=0;
 for(unsigned i=0;i<observations;i++)if(expected[i].kind==2){if(n<10)first[n]=expected[i].address;else CHECK(expected[i].address==first[n%10u],"unchanged ten-address footprint across all32 up probes");n++;}
 CHECK(n==320,"complete diagnostic read prefix");printf("PASS32-probe L1/native prefix; diagnostic service cut only, no production budget added\\n");return 0;
}
'''
    source=folder/'harness.c';source.write_text(raw);exe=folder/'witness.exe'
    built=compile_c([source],exe,[ROOT/'c',ROOT/'native'],['-DACTOR_VERIFY','-Wno-misleading-indentation','-Wno-unused-function'])
    run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=60);assert not run.returncode,run.stdout+run.stderr
    import contacts_reference as ref
    ref.OUT=OUT/'reference';plain=ref.prepare_reference(local=True)
    sys.path.insert(0,str(ROOT/'tools'));import difftest
    scene=difftest.load_suite('scene');case=scene.move_case('retained wrap/up-scan divergence',y=1,pixel=(100,1042),water=1042,platform=0)
    m=difftest.Machine();m.reset();case.setup(m);m.prepare(case.routine,case.regs,case.kind,case.args,case.flags)
    error=None
    try:m.run(50000)
    except RuntimeError as exc:error=str(exc)
    assert error and error.startswith('budget 50000 exhausted'),error
    registers={n:m.reg(n) for n in ['CS','IP','BP','DI']}
    assert registers['DI']==32768 and registers['BP']&31==1
    assert scene.get(m,scene.DATA_SEG,'PlayerY32')==1 and scene.get(m,scene.DATA_SEG,'PlayerYPixels')==1042
    save(folder/'result.json',receipt(built['command'],[*inputs,ROOT/'verif/player_physics_harness.c',ROOT/'verif/player_physics_nontermination.py',ROOT/'tools/emu.py',ROOT/'tools/difftest.py',ROOT/'tests/scene.py',plain],result='PASS',compiled_prefix=run.stdout.strip(),l0_budget=50000,l0_result=error,l0_registers=registers,
      input=dict(y32=1,cached_pixel_y=1042,water_y=1042,platform=0,vertical_velocity=0,clear_collision_image=True),
      claim='Expected lack of return, not a terminating game scenario. Actual-C induction plus matching per-iteration output theorem establishes the retained cycle; the L0 instruction budget and injected C service stop record finite prefixes only.'))
    print(run.stdout.strip());print('PASS L0 retained cycle prefix',registers,flush=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--proof-only',action='store_true');ap.add_argument('--witness-only',action='store_true');ap.add_argument('--timeout',type=int,default=120);a=ap.parse_args()
    if not a.witness_only:proof(a.timeout)
    if not a.proof_only:witnesses()
if __name__=='__main__':main()
