"""Checked coverage, exact ABI shells and static-plus-indirect caller set."""
import json,re,struct
from closure_support import ROOT,function,receipt,save
from demo_scene_build import OUT,FILES
from demo_scene_shells import main as check_shells,NAMES,BRIDGE
from demo_scene_pieces import pieces
def compact(s):return re.sub(r'\s+','',s)
def main():
    check_shells();p=pieces();source=(ROOT/'c/scene.c').read_text();body=function(source,'c_RunScriptedDemo');remaining=compact(body[body.index('{')+1:body.rfind('}')])
    inventory=['initialize','clear-before-poll','frame-header','erase','water-cut','draw','swap','completion-test','finished-result']
    for key in inventory:
        part=compact(p[key]['fragment']);assert remaining.count(part)==1,key;remaining=remaining.replace(part,'',1)
    assert remaining=='for(unsignedbudget=0;budget<100000;budget++){}returnUGH_BUDGET;',remaining
    for key,piece in p.items():assert piece['phase'].startswith('DP_') and piece['kind'].startswith('DEMO_PRESENT_')
    # All stored demo callback identities come from actual registered headers,
    # never from the otherwise unrelated unexplained RET at0B4E.
    import contacts_reference as ref
    ref.OUT=OUT/'reference';image=ref.expanded_image(local=True);data=image.read_bytes()[0xa00+0x5c09*16:]
    callbacks=[];vectors=[]
    symbols=(ROOT/'c/ugh_sym.h').read_text()
    def address(n):return int(re.search(r'#define UGH_O_GAME_'+n+r' (0x[0-9a-fA-F]+)u',symbols)[1],16)
    allowed={address(n):n for n in ['StartDemoFadeWhenSpriteHidden','SetDemoRevealSpriteWidth','IgnoreActorState']}
    for base in [0x1020,0x1792,0x1e40,0x24de]:
        cursor=base;headers=[]
        while struct.unpack_from('<H',data,cursor)[0]!=65535:
            header=struct.unpack_from('<H',data,cursor)[0];target=struct.unpack_from('<H',data,header+6)[0];assert target in allowed;headers.append(header);callbacks.append(dict(header=hex(header),target=allowed[target]));cursor+=2
        vectors.append(dict(vector=hex(base),headers=[hex(v) for v in headers]))
    assert len(callbacks)==28 and len({r['header'] for r in callbacks})==28
    direct=[]
    for path in (ROOT/'c').glob('*.c'):
        for number,line in enumerate(path.read_text().splitlines(),1):
            if re.search(r'\bc_loc_0B4E\s*\(',line) and not line.startswith('EXPORT int c_loc_0B4E'):direct.append(dict(file=path.relative_to(ROOT).as_posix(),line=number,text=line))
    assert not direct
    noop=function((ROOT/'c/demo_scripts.c').read_text(),'c_loc_0B4E');assert compact(noop[noop.index('{')+1:noop.rfind('}')])=='(void)r;returnUGH_OK;'
    coverage=[]
    for path in sorted((OUT/'whole').glob('*.ref.json')):
        j=json.loads(path.read_text());coverage.append(dict(scenario=path.name[:-9],routines=[n for n in j['coverage']['routines'] if n in ['GAME:'+x for x in [*NAMES,'DrawDemoSprites','EraseDemoSprites','loc_0B4E']]]))
    save(OUT/'coverage.json',receipt(['python','verif/demo_scene_coverage.py'],[*FILES,ROOT/'c/scene.c',ROOT/'c/demo_scripts.c',ROOT/'c/ugh_sym.h',image,ROOT/'verif/demo_scene_pieces.py',ROOT/'verif/demo_scene_proof.py',ROOT/'verif/demo_scene_harness.c',ROOT/'verif/demo_scene_coverage.py'],result='PASS',primary_runner_partition=inventory,retained_runner_remainder=remaining,stages=p,registered_vectors=vectors,stored_callbacks=callbacks,unexplained_ret=dict(address='GAME:0B4E',direct_call_sites=direct,indirect_header_targets=[],contract='Retained unexplained RET: UGH_OK and every register/flag/memory cell unchanged. It is not IgnoreActorState, not a demo effect and has no established caller.',witness='No input-only witness justified by the checked normal direct/indirect graph. Literal trivial property is proved; no invented native role/export.'),original_coverage=coverage,
      composition='Nine disjoint literal spans cover every common-runner statement except the unchanged diagnostic loop/budget return.27 branch/continuation profiles execute actual C and native event consumer at service/backedge/return cuts. Every service asserts next-phase and complete captured-result equality/frame; palette/input/flags/stack-return seams use arbitrary shared outputs. Independent actual native frame/dependence and two full effect properties cover remaining state. Four full wrappers are source-checked; after-prepare/music/cleanup/return profiles cover their continuations. Draw/erase delegate to accepted actor_render. No monolithic arbitrary-session termination or pixel/audio-service proof is claimed.',session_debt='No part of the accepted actor_render RunGameFromPassword copy can be removed by replacing only the called demo runner/wrappers. The native common runner is now a callee of that shell; removing it requires a session facade or caller rewrite outside this unit. No accepted renderer or whole-session code was changed.'))
    print('PASS complete runner inventory, continuation seams and28 stored callbacks; loc_0B4E unreached')
if __name__=='__main__':main()
