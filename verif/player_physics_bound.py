"""An under-unwound actual native zero-journal/backedge walk must fail."""
from closure_support import ROOT
from player_physics_build import OUT,FILES
from player_physics_limits import cbmc
def main():
    folder=OUT/'negative-bound';folder.mkdir(parents=True,exist_ok=True);source=folder/'harness.c'
    source.write_text('#include "'+(ROOT/'native/player_physics.c').as_posix()+'''"
int main(void) {
 PlayerPhysicsView v={0};PlayerPhysicsWorld w={0};PlayerPhysicsProcess p;
 player_physics_begin(&p,&v,&w);p.stage=PP_HORIZONTAL_HIT;p.positive=1;p.cursor=0;p.candidate=64;p.sample=0;
 PlayerPhysicsEvent event=player_physics_poll(&p);__CPROVER_assert(event.kind==PP_READ_PLANE,"next real scan event");return 0;
}
''')
    result=cbmc(source,folder,[*FILES,ROOT/'verif/player_physics_bound.py'],unwind=1,timeout=60,extra=['--no-array-field-sensitivity'])
    print(result['result'],result['failures'],flush=True)
    assert result['result']=='FAIL' and any('player_physics_poll' in n and 'unwind' in n for n,_ in result['failures'])
if __name__=='__main__':main()
