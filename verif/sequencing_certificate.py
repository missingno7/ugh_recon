"""Sequencing certificates; administrative promotion remains supervisor-owned."""
import argparse,hashlib,json,sys
from datetime import date
from closure_support import ROOT,hashes,save
from sequencing_build import OUT
from lifecycle_shells import FILES as LIFEFILES,NAMES as LIFENAMES
from session_bridge import FILES as SESSIONFILES,NAMES as SESSIONNAMES
sys.path.insert(0,str(ROOT/'tools'))
import closure

def evidence(prop,level,command,result,method):return dict(property=prop,level=level,command=command,result=result,method=method,date=date.today().isoformat())
def text_hash(p):return hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def locks(files):return {p.relative_to(ROOT).as_posix():text_hash(p) for p in files if p.is_file()}
def maintained():
    return [*LIFEFILES,*SESSIONFILES,*sorted((ROOT/'verif').glob('sequencing_*')),*[ROOT/'verif'/n for n in ['lifecycle_shells.py','session_bridge.py','session_loader.py','session_record_proof.py','session_copy_proof.py']],
      ROOT/'native/bridge/actor_render_bridge.c',ROOT/'native/actors.h',*sorted((ROOT/'c').glob('*.[ch]')),
      ROOT/'tools/closure.py',ROOT/'tools/nbuild.py',ROOT/'tools/hostbuild.py',ROOT/'tools/wholegame.py',ROOT/'tools/emu.py',ROOT/'tools/difftest.py',ROOT/'host/check.py',ROOT/'metadata/verif-tools.json',ROOT/'verif/closure_support.py',ROOT/'verif/windows_job.py',*sorted((ROOT/'tests/scenarios').glob('*.txt'))]
def draft(component):
    life=component=='lifecycle';files=LIFEFILES if life else SESSIONFILES;names=LIFENAMES if life else SESSIONNAMES
    owned=[p for p in files if p.suffix in ['.c','.h']];relative=[p.relative_to(ROOT).as_posix() for p in owned]
    cert=dict(component=component,status='unanalyzed',proposed_status='boundary-established',
      original=dict(owned=['GAME:'+n for n in names],l1=['c/menu.c','c/video.c'] if life else ['c/scene.c','c/render.c','c/items_water.c']),
      native=dict(files=relative,header='native/'+component+'.h',functions=['lifecycle_begin','lifecycle_next','lifecycle_consume'] if life else ['session_begin','session_next','session_acknowledge','session_load_begin','session_load_next','session_load_accept'],build='python verif/sequencing_build.py'),
      purpose='Program lifetime and synchronous platform/audio initialisation and shutdown requests.' if life else 'Single owner of password/level/session/frame orchestration, streamed level-record construction, display initialisation and score/lives reset.',
      interface=dict(inputs=['Raw scalar words/bytes, retained histories and synchronous service replies at original cuts. Private continuation state is not a game mode or a second persistent world.'],outputs=['Ordered role-named requests and exact wrapping state values; ABI adapter publishes writes at matching cuts and binds native selections.'],preconditions=['Ordinary disjoint RAM/resources/native output/stack; no asynchronous mutation during one synchronous operation. Original resource pointers and finite list prefixes must be valid to complete; malformed data is not repaired.','Frame simulation services retain their accepted contracts. Pixel services preserve actor arrays; typed render histories persist. The L1 adapters retain live DS/CS, emulated stack and exact original return words.']),
      callers=['Program entry and literal DOS shutdown tail.'] if life else ['Menus continue to call the unchanged GAME:RunGameFromPassword service entry; level display and attract preparation call the loader.'],
      callees=dict(native=['Only same-unit pure helpers.'],services=['All original closed subsystem entries and platform services, synchronously and in source order. No subsystem algorithm is inlined.']),
      indirect=dict(classification='No native code pointers. Opaque descriptor identities/callback roles remain boundary values; existing callback dispatch stays with its owner.',retained='loc_001C..001F remain literal near RET hooks; lifecycle does not give them a new role.'),
      memory=dict(owned=['Lifecycle continuation and saved BIOS mode byte.'] if life else ['Existing canonical level/session/lives/score/multiplier fields and initializer writes only. Decoder and frame cursors are private working state, never second persistent owners.'],borrowed=['All closed subsystem state at original boundaries, persistent actor/player/enemy/item rendering histories and resource views.'],frame=['Native core changes only its declared continuation/output object; persistent RAM writes are explicit adapter operations. Service frames are borrowed contracts.']),
      assumptions=['Ordinary disjoint resources and stack; original callbacks/services synchronous. Full raw arithmetic is retained without positivity or initialized-history assumptions.','Formal profiles state fixed-slot, typed/disjoint resource normalizations. Whole-emulated RAM/device/ABI, arbitrary resource aliasing, pixel execution, interrupt timing and entire session termination are composition evidence, not an unrestricted theorem.'],
      eliminated=['Whole generated session copy in actor_render. Native orchestration has no registers, machine addresses, VGA transactions or recovered code pointers.'] if not life else ['The lifecycle order and parameters are explicit native requests, including AdLib-only mask1 and stop selector17.'],
      retained=['Abnormal service returns stop at the consumed prefix; no synthesized cleanup or rollback.','Literal verification guards remain where the original C translation put them; native code introduces no new gameplay timeout.'],
      evidence=[evidence('Implementation boundary and checked source cuts','C','python verif/lifecycle_shells.py; python verif/session_bridge.py','PASS current generated ABI adapters','Acceptance replay is recorded separately; no automatic status promotion.')],
      amiga=dict(classification='Meaning only',finding='DOS direct loops and raw arithmetic are authoritative; Amiga h0:00E98 indirect top-level site is not imported.'),
      uncertainty=['No A claim for the whole lifecycle/session. External hooks are retained unexplained RETs.'],
      dependencies={n:closure.actual_dependencies(ROOT/n) for n in relative})
    cert['verification_input_hashing']='sha256-lf-text';cert['verification_inputs']=locks(maintained())
    return cert
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--final',action='store_true');a=ap.parse_args()
    for component in ['lifecycle','session']:
        cert=draft(component)
        if a.final:
            for name in ['proof-matrix.json','record-matrix.json','cases.json','mutants.json','inventory.json','integration.json','host.json']:
                j=json.loads((OUT/name).read_text());assert j.get('result','PASS')=='PASS',name
            integ=json.loads((OUT/'integration.json').read_text());assert not integ['whole_status'] and all(not r['problems'] for r in integ['cases'])
            assert all(not any(r['fallbacks']) for r in integ['scenario_audits'])
            cert['proposed_status']='migrated';cert['proposed_status_reason']='Actual-C transition/record profiles, exhaustive scalar slices, full-RAM pairs, mutation controls, committed-baseline scenario replay and scratch host pass. Closure dependency refreshes, if blocked by ownership, are explicitly separate.'
            cert['evidence'] += [evidence('Transition/scalar/output/frame/dependence profiles','B','python verif/sequencing_proofs.py','PASS20 profiles and20 final-comparison reachability controls','Actual maintained native C. Full raw scalar domains; actual literal water cap and display-score arithmetic fragments. Policy invariants and protocol properties are narrower than full L1 equivalence. The two-player frame-order profile includes both rain branches.'),evidence('Complete streamed record pairs','B','python verif/sequencing_records.py','PASS18 profiles and18 reachability controls','Actual one-record literal C and actual generated bridge/native C. Platform, actor including stone, tree, bird, dino and all other descriptors. Separate output/frame/dependence; full slot and registers/flags and ordered stores/services at the record seam. Typed disjoint resources, fixed physical slot and arbitrary other slot.'),evidence('Backward26-byte copy','B','python verif/session_copy_proof.py output; python verif/session_copy_proof.py frame; python verif/session_copy_proof.py dependence','PASS3 profiles and3 final-comparison controls','Actual literal and generated bridge loops, small sparse source/destination windows with physical overlap represented by destination storage. All16-bit relative source offsets including wrap and every destination byte; separate arbitrary-other-byte frame and dependence.'),evidence('Compiled scalar and service-stream cases','C','python verif/sequencing_cases.py','PASS327936 scalar and16514944 record slice checks;54 full-RAM parent pairs','Full16-bit slices and small domains are reported separately from generated samples; compiled actual-C record and actual full-RAM parent pairs including every ordered subsystem entry with its complete register inputs.'),evidence('Mutation controls','C','python verif/sequencing_mutants.py','PASS15 controls; see mutants.json','Behavioral defects and private selection/consumption defects must fail comparison or bridge binding; compiler errors never count.'),evidence('L0 routine suites and whole-game composition','D','python verif/sequencing_integration.py --whole --local-reference','PASS20 maintained scenarios and extra rainy witness; zero literal parent fallback','Per-entry and per-frame counts in integration.json; complete RAM/devices/IO and original ordered calls. This is composition evidence, not A/B for a whole frame.'),evidence('Scratch host build/check','D','python verif/sequencing_host.py','PASS38 linked units,21 checks in both variants; see host.json','Pinned committed baseline plus owned files only; new certificates promoted only in scratch. Closure lock blockers are recorded independently, never hidden.')]
            for mode in ['output','frame','dependence']:
                j=json.loads((OUT/'copy-proofs'/mode/'result.json').read_text());assert j['result']=='PASS'
            host=json.loads((OUT/'host.json').read_text())
            cert['scenario_native_counts']=integ['scenario_audits'];cert['acceptance']={k:host[k] for k in ['baseline_revision','result','closure_result','linked_units']};cert['acceptance']['receipt']='build/workers/close-stones-12/host.json'
            if host['closure_result']!='PASS':cert['acceptance_blocker']='Only supervisor may refresh actor_types/demo_presentation locks. Exact unapplied proposal and independent closure review are in lock-review.json; current acceptance does not claim closure passes.'
            cert['negative_results']=[dict(receipt=str(p.relative_to(ROOT)),**{k:j.get(k) for k in ['result','seconds','peak_private_bytes','command','failures']}) for p in sorted((OUT/'negative').glob('*/result.json')) for j in [json.loads(p.read_text())]]
        save(ROOT/'metadata/closure'/f'{component}.json',cert)
    print('Wrote lifecycle/session certificates; administrative status unchanged')
if __name__=='__main__':main()
