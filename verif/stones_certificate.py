"""Prepare a review certificate; only the supervisor promotes status."""
import argparse,json,hashlib,sys
from pathlib import Path
from closure_support import ROOT,save
from stones_build import OUT,NAMES,SOURCES
sys.path.insert(0,str(ROOT/'tools'))
import closure
def evidence(prop,level,command,result,method):
    return dict(property=prop,level=level,command=command,result=result,method=method,date='2026-11-13')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--draft',action='store_true');a=p.parse_args()
    files=['native/stones.h','native/stones.c','native/bridge/stones_bridge.c']
    cert=dict(component='stones',status='unanalyzed',proposed_status='boundary-established' if a.draft else 'migrated',
        original=[dict(identity='GAME:'+name,address='013B:'+offset,l1='c_'+name) for name,offset in zip(NAMES,['1C0F','1C27','1C48','1C6B','1C81','1CEE'])],
        native=dict(files=files,header='native/stones.h',functions=['stone_begin_wait','stone_pickup_wait','stone_attach','stone_release_requested','stone_throw','stone_flight','stone_contact_view'],build='python verif/stones_build.py'),
        purpose='Stone lifecycle: waiting, first touching empty craft pickup, carrying, action-byte release, throw, flight, ordered platform landing and retirement. Borrow the same physical slots for hazard contact without resetting renderer history.',
        interface=dict(inputs=['Known primary or alternate stone descriptor; any word-valued slot state for the entry phase, any geometry/carried kind words, two craft records and player count.','Carry alias is player 0, or player 1 with count two. Direct attach/throw carrier is independently valid. Flight borrows up to ten platforms in original order; signed-negative left edge terminates.'],
            outputs=['Typed slot/craft mutations, contact and platform selections, transition requests. The bridge preserves the deterministic full L1 machine shell and the real synchronous throw sound ABI.'],
            effects=['No renderer-history writes. Positions/velocities and presentation sprite are committed before immediate landing initialization or sound callback.','The bridge projects fresh RAM per entry, publishes only actual stores, and uses existing phase-checked alias accessors.'],
            preconditions=['Serialized ordinary nonaliasing RAM/stack and immutable descriptor/platform inputs during one call. DS=DGROUP, CS=GAME, aligned physical slot 0..15.','Descriptor callback words must be the known stone targets. Malformed indices/identities/targets, invalid carrier aliases and unterminated platform lists use explicit L1 compatibility. No native evidence is claimed for fallback.','Native carrier arguments must be below two. Hazard views must be borrowed immediately before query in physical slot order, and hazard bounce writes returned before the next actor step.']),
        callers=['DispatchActorUpdates in ascending active-prefix order; loader bootstrap, stone descriptor tails; hazards run after actor updates and before drawing.','Routine direct-entry tests retain their live input/output register shell.'],
        callees=dict(native=['actor_alias_value','contact_players'],bridge=['actor_bridge_alias_project','actor_bridge_alias_read','FindPlayerTouchingActor','PlayAdlibEffect','closed stone descriptor tails']),
        indirect=dict(targets=['BeginStonePickupWait','UpdateStonePickupWait','AttachStoneToPlayer','WaitForStoneRelease','ThrowCarriedStone','UpdateThrownStone','IgnoreActorState'],classification='Known descriptor targets checked before projection; the original dispatcher retains explicit error/fallback behavior outside the contract.'),
        memory=dict(owned=['Actor update phase, animation offset/countdown, sprite, X32/Y32; carried alias, thrown horizontal and vertical motion; selected craft carried kind and destination icon.'],
            borrowed=['Descriptor geometry, callbacks and carried kind; platform bounds/heights; craft position/raw velocity/action low byte.'],
            aliases='Only carrier in carried phase and horizontal_step in thrown phase are read through checked alias accessors. No table widening. All six renderer-history words remain persistent and untouched, including history seeded by the pre-game demo.',
            hazards='Primary identity only, phase thrown, nonnegative vertical step; ascending first match. Current bridge RAM is the shared synchronization boundary, not a second cached native slot array.'),
        assumptions=['One step from any admitted scalar slot state, not a proof only from initializer-reachable states.','The full bridge formal profiles abstract a successful read-only sound callback; real sound, registers and device effects are differential/integration evidence.','L0 unchanged; L0 -> L1 remains C/D. Native A/B evidence never becomes an exact ASM/C byte-match contribution.'],
        eliminated=['Ordinary native functions use typed slots, player numbers and borrowed resources; no machine addresses/registers/dispatch in native/stones.c.','Renderer history is neither reset nor derived from current position on entry.'],
        retained=['16-bit wrapping addition/subtraction, explicit signed word comparisons and arithmetic right shift of raw craft velocities by five.','Only action low-byte bit seven releases; high byte and all action bits survive unchanged.','Inclusive X retirement at -512, right retirement at 10240, descending bottom retirement at 6144; rising Y has no bottom retirement.','Gravity adds two before sign test; inclusive old/new platform crossing and both horizontal edges, first platform wins.','Primary and alternate identities remain distinct; only primary thrown stones can hit hazards. Initializing wait leaves sprite, velocities and render history stale; retired slots keep their descriptor/order.'],
        evidence=[evidence('Pending final review','C','python verif/stones_integration.py --whole --local-reference','Pending: draft certificate','Actual C and independent L0 differential runner')],
        amiga=dict(classification='similar purpose with different implementation',finding='The shared carry/throw role supplies meaning only; DOS hazard scan placement, signed geometry and arithmetic prevail. No Amiga byte or behaviour equivalence claimed.'),
        uncertainty=['Only the supervisor sets administrative status.','Malformed resource/alias and device cases routed to L1 are compatibility evidence. Full bridge-shell profiles that time out are not proofs.'],
        dependencies={name:closure.actual_dependencies(ROOT/name) for name in files})
    if not a.draft:
        host=json.loads((OUT/'host.json').read_text());assert host['result']=='PASS' and host['check']['passed']
        scratch=ROOT/host['scratch']
        for name in files:
            if name.endswith('.c'):assert host['build']['inputs'][str(scratch/name)]==hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),'stale host source: '+name
        integration=json.loads((OUT/'integration.json').read_text());assert not integration['whole_status'] and not any(row['problems'] for row in integration['cases']) and integration['cross_mode']==1
        enum=json.loads((OUT/'evidence/enumerate_1/result.json').read_text());assert enum['result']=='PASS'
        cert['evidence']=[evidence('Finite complete scalar domains','A','python verif/stones_evidence.py enumerate',enum['stdout'].strip(),
            'Complete 65536 action-word, joint velocity diagonal (horizontal=vertical=value), X-retirement and vertical-gravity slices with other inputs fixed. The velocity Cartesian product is not enumerated; arbitrary independent axes have separate B evidence. Generated states remain C, not A.'),
            evidence('Bridge shell, phase projection and frame integration','C','python verif/stones_integration.py --whole --local-reference',f'PASS {len(integration["cases"])} routine cases, zero scenario fallbacks, cross-mode history regression', 'Actual bridged L1 versus independently rebuilt L0, normal and poisoned register inputs; exact RAM/register/flag and device observations.'),
            evidence('Whole-game observations','D','python verif/stones_integration.py --whole --local-reference','PASS all seventeen maintained scenarios','Page-boundary state/frame/device/log digests from independent L0 references.'),
            evidence('Native host scratch promotion','D','python verif/stones_host.py -> python tools/hostbuild.py; python host/check.py --variant native','PASS seventeen scenarios and 256-frame smoke','Unchanged CLI commands on a real copied checkout with only scratch stone status promoted, including accepted native hazards/contacts/demo.')]
        sync=json.loads((OUT/'sync/result.json').read_text());assert sync['result']=='PASS'
        mutants=json.loads((OUT/'mutants.json').read_text());assert all(row['result']=='DETECTED' for row in mutants)
        negative=json.loads((OUT/'evidence/BeginStonePickupWait_0_negative/result.json').read_text());assert negative['result']=='FAIL' and any(row[0]=='stone_project.unwind.0' for row in negative['failures'])
        cert['evidence'] += [evidence('Live stone/hazard borrowing','C','python verif/stones_sync.py',sync['stdout'].strip(),
            'Actual maintained native stone, hazard and contact implementations: alternate/primary identity, ascending selection, two hazards in one frame, bounce publication and following actor step.'),
            evidence('Defect and unwind controls','C','python verif/stones_mutants.py; python verif/stones_evidence.py BeginStonePickupWait --platforms 0 --negative --timeout 30',
            'PASS: four scratch defects detected; insufficient production stone_project loop unwind fails, never truncates silently.',
            'High-byte action test, gravity +3, strict old-surface crossing and broadened alternate identity are each rejected by compiled actual-C cases.')]
        for name in NAMES:
            candidates=[OUT/'evidence'/f'{name}_1/result.json',OUT/'evidence'/f'{name}_1_semantic/result.json']
            passed=[]
            for path in candidates:
                if path.exists() and json.loads(path.read_text())['result']=='PASS':passed.append(path)
            assert passed,'no actual-C CBMC proof for '+name
            path=passed[0];proof=json.loads(path.read_text());semantic='_semantic' in str(path)
            for name_input in ['native/stones.c','native/bridge/stones_bridge.c','verif/stones_harness.c','verif/stones_build.py','verif/stones_evidence.py']:
                assert proof['inputs'][name_input]==hashlib.sha256((ROOT/name_input).read_bytes()).hexdigest(),'stale proof: '+str(path)+' '+name_input
            cert['evidence'].append(evidence(name+' actual-C one-step','B',f'python verif/stones_evidence.py {name} '+('--semantic ' if semantic else '')+'--timeout 180',
                f'PASS {proof["seconds"]:.3f}s, unwind assertions and bounds/pointer/signed-overflow checks',
                ('Semantic state and sound requests only; bridge shell/order remains C. ' if semantic else 'Full bridge state/register/flag/ordered-store relation. ')+
                'One arbitrary physical slot 0..15, arbitrary admitted scalar words and geometry, primary/alternate identity, exact targets; flight has one arbitrary platform (explicit B bound), successful observing sound callback.'))
        cert['uncertainty'] += ['Full bridge-shell pickup and flight profiles timed out at 60 and 180 seconds. Semantic-only pickup timed out at 60 before passing at 180. No timeout is evidence of equivalence. The ten-platform semantic flight attempt is separately recorded and does not replace the one-platform B profile.',
            'Unit 4 passenger itinerary is stopped at the static contract boundary, with its complete transition/effect checklist and continuation commands in build/workers/close-stones/REPORT.md. None of its handlers is replaced.']
        cert['proposed_status_reason']='Actual-C per-entry evidence, finite exhaustive domains and C/D bridge integration plus actual native-host scratch promotion. Full up-to-ten-platform bridge contract retains C where formal profiles time out; propose migrated only.'
        inputs=[ROOT/name for name in files]+[p for p in SOURCES if p!=ROOT/'native/bridge/stones_bridge.c']+list((ROOT/'verif').glob('stones*'))+[
            ROOT/'native/actors.h',ROOT/'native/actor_resources.h',ROOT/'native/contacts.h',ROOT/'native/level.h',ROOT/'native/geometry.h',
            ROOT/'native/bridge/actor_projection.h',ROOT/'c/actors.c',ROOT/'c/actors_states.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',
            ROOT/'verif/closure_support.py',ROOT/'verif/windows_job.py',ROOT/'tools/closure.py',ROOT/'tools/hostbuild.py',ROOT/'host/check.py',ROOT/'metadata/verif-tools.json']
        cert['verification_input_hashing']='sha256-lf-text';cert['verification_inputs']={path.relative_to(ROOT).as_posix():hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest() for path in inputs}
    save(ROOT/'metadata/closure/stones.json',cert)
if __name__=='__main__':main()
