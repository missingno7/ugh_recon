"""Check literal operation coverage, loop cuts and native stage orchestration."""
import re
from collections import Counter
from pycparser import c_ast,c_parser,c_generator
from closure_support import ROOT,function,receipt,save
from player_physics_build import OUT,FILES
from player_physics_pieces import pieces
from player_physics_proof import STAGES
from player_physics_children import platform_span
from player_physics_shells import main as shells
def operations(body):
    text=re.sub(r'/\*.*?\*/|//[^\n]*','',body,flags=re.S)
    pre='typedef unsigned short uint16_t;typedef short int16_t;typedef unsigned char uint8_t;typedef signed char int8_t;typedef struct Regs Regs;'
    tree=c_parser.CParser().parse(pre+'int piece(Regs *r){'+text+'}')
    result=Counter();generator=c_generator.CGenerator()
    class Visit(c_ast.NodeVisitor):
        def generic_visit(self,node):
            if isinstance(node,(c_ast.Assignment,c_ast.FuncCall,c_ast.BinaryOp,c_ast.UnaryOp)):
                result[re.sub(r'\s+','',generator.visit(node))]+=1
            super().generic_visit(node)
    Visit().visit(tree);return result
def main():
    OUT.mkdir(parents=True,exist_ok=True);shells()
    scene=(ROOT/'c/scene.c').read_text();body=function(scene,'c_MovePlayerWithVgaCollisions');body=body[body.index('{')+1:body.rfind('}')]
    actual=operations(body);covered=Counter()
    for key,piece in pieces().items():covered.update(operations(piece))
    missing={op:n-covered[op] for op,n in actual.items() if n>covered[op]}
    assert not missing,missing
    native=(ROOT/'native/player_physics.c').read_text();poll=function(native,'player_physics_poll')
    mappings=['PP_INITIAL','PP_HORIZONTAL','PP_HORIZONTAL_SCAN','PP_HORIZONTAL_HIT','PP_HORIZONTAL_END','PP_VERTICAL','PP_VERTICAL_SCAN','PP_VERTICAL_HIT','PP_VERTICAL_END']
    for stage,helper in zip(mappings,STAGES.values()):assert 'case '+stage+':'+helper+'(p);break;' in poll,(stage,helper)
    compact=lambda text:re.sub(r'\s+','',text)
    search=function(native,'pp_find_platform');search=search[search.index('{')+1:search.rfind('}')]
    expected='''uint16_t height=(uint16_t)(player_physics_sar(cursor,5)+20u);
 uint16_t center=(uint16_t)(pixel_x+16u);
 for(size_t i=0;i<w->platform_count;i++) {
  const LevelPlatform *platform=&w->platforms[i];
  int decision=pp_platform_decision(platform,height,center);
  if(decision<0)break;
  if(decision)return (int)i;
 }
 return -1;'''
    assert compact(search)==compact(expected),'platform composition/order drift'
    stripped=native.replace(function(native,'pp_append'),'').replace(poll,'')
    assert '->journal' not in stripped,'stage helpers may not depend on prior journal payload'
    body_poll=poll[poll.index('{')+1:poll.rfind('}')];a=body_poll.index('switch(p->stage)');b=body_poll.index('{',a)+1;depth=1
    while depth:depth+=int(body_poll[b]=='{')-int(body_poll[b]=='}');b+=1
    shape=body_poll[:a]+'STAGES;'+body_poll[b:]
    expected='''if(p->awaiting_reply){p->failed=1;return (PlayerPhysicsEvent){.kind=PP_DONE};}
 while(p->consumed==p->count && p->stage!=PP_FINISHED && !p->failed) {
  p->count=p->consumed=0;STAGES;
 }
 if(p->consumed==p->count)return (PlayerPhysicsEvent){.kind=PP_DONE};
 PlayerPhysicsEvent event=p->journal[p->consumed++];
 if(event.kind==PP_SAMPLE)p->awaiting_reply=1;
 return event;'''
    assert compact(shape)==compact(expected),'native stage/journal orchestration drift'
    assert platform_span() in pieces()['vertical-hit']
    scope=dict(initial='water high byte and attachment gate',horizontal='wind, thrust, clamp, integration, cached equality and initial plane/left probe',
      horizontal_scan='one right-plane/cell advance or unchanged left probe, ordered sample and shared byte reply',
      horizontal_hit='one collision/reflection or signed cursor/backedge decision',horizontal_end='position/cache publication and saved water state',
      vertical='water/air/input priority, timer, clamp, surface equality and initial up probe',vertical_scan='one down-row advance or unchanged up probe and sample',
      vertical_hit='reflection, signed greater component, impact threshold and platform child',vertical_end='position/cache publication and crash fade')
    source_inputs=[*FILES,ROOT/'c/scene.c',ROOT/'c/demo_scripts.c',ROOT/'verif/player_physics_coverage.py',ROOT/'verif/player_physics_pieces.py',ROOT/'verif/player_physics_children.py',ROOT/'verif/player_physics_stage.py',ROOT/'verif/player_physics_proof.py',ROOT/'verif/player_physics_shells.py']
    save(OUT/'coverage.json',receipt(['python','verif/player_physics_coverage.py'],source_inputs,result='PASS',literal_operations=sum(actual.values()),partitions=scope,
      composition='All assignments, calls, arithmetic/comparison and unary operations in the actual handler occur with at least their original multiplicity in checked literal pieces. Loop break/backedge edges become explicit continuation values; per-iteration proofs assert equality of cursor/candidate/direction and plane/displacement seams. Address construction and first-platform lookup are separate actual-C children with arbitrary shared outputs and equality assertions in parents. Per-stage outputs, arbitrary native/resource byte frames and inactive-input dependence cover all typed outputs, retained words, ordered writes/ports/sample requests and replies, and control state. The complete retained ABI shell is regenerated from actual C; no register/flag deadness claim is used. Ordinary disjoint RAM/resources/stack, valid selected physical slot and a negative platform-left sentinel within ten borrowed entries are explicit B assumptions; all scalar words and cached histories are arbitrary.'))
    print('PASS complete literal operation inventory and nine native stages; '+str(sum(actual.values()))+' operations')
if __name__=='__main__':main()
