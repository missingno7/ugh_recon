"""Validate current receipts and assemble the round-four certificate evidence."""
import hashlib,json
from pathlib import Path
from closure_support import ROOT
from delivery_build import OUT,SOURCES
from delivery_pieces import pieces
from delivery_proofs import jobs,current

FILES=['native/passenger_delivery.h','native/passenger_delivery.c','native/bridge/passenger_delivery_bridge.c']
def read(path):return json.loads((OUT/path).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def checked_inputs(value,names):
    for name in names:assert value['inputs'][name]==sha(ROOT/name),'stale receipt: '+name
def row(prop,level,command,result,method):
    return dict(property=prop,level=level,command=command,result=result,method=method,date='2026-11-13')

def finish(cert,args):
    cert['status']='boundary-established'
    cert['assumptions']=[
        'One-step B composition on actual maintained C, from any admitted state. No initialization reachability, scalar magnitude, cleared renderer history, free item slot or positive timer/fare restriction.',
        'Ordinary disjoint RAM/resources/stack; one or two crafts, ten platforms. Fixed selected slot0 is justified by uniform constant-offset addressing; arbitrary-other-slot byte frame checks every other physical identity. Finite tests additionally vary all sixteen physical slots.',
        'Animation primitive admits every registered nonempty bank fitting [0E20,1020), any current live/terminal cursor, arbitrary live values and all four vector kinds. Caller tick/frame seams have arbitrary shared poststates and assert input/vector equality. Resource/cursor corruption outside bridge admission keeps L1 compatibility.',
        'Contact query composes with contacts certificate kind0 whole-bridge B, including arbitrary geometry. Item request composes with falling_items spawn B, including all twelve occupied slots and its abnormal transfer. Audio uses the existing entry and a shared arbitrary status/register result at the caller proof seam; child footprints remain owned by their certificates.',
        'Output, byte frame and input dependence are distinct profiles. Literal source partition, native orchestration and journal-prefix lemmas compose the stages; all protocol/service controls and complete machine registers/flags/ordered stores are outputs. The actual complete projection predicate is proved separately and checked at matching production cuts.',
        'L0-to-L1 evidence remains independently rebuilt C/D. None of this is evidence for matching DOS bytes.'
    ]
    cert['interface']['outputs'].append('BOARD/DELIVER tails consume the full native selected craft after the parent journal and before the callee. Normal return rejects an unconsumed non-NONE next request or finish_pending. ACTOR_VERIFY checks active native working state at each matching cut.')
    cert['memory']['aliases']+=' Journal alias tags are checked against the published phase. Full size_t carrier and ordinary journal indices are range checked before inverse projection; no high-bit truncation is accepted. The phase alias table is unchanged.'
    cert['uncertainty']=['Administrative status stays boundary-established until supervisor review. Unit-six water updates remain L1; only their shared initializers/rescue entry belong here. Malformed-state fallback is compatibility evidence, not native closure outside admission.']
    cert['evidence']=[row('Round-four replay','C','python verif/delivery_reproduce.py --fresh','Pending final split matrix and scratch promotion','No migration proposal is made by a draft certificate.')]
    if args.draft:return
    finite=read('evidence/enumerate_current/result.json');cases=read('cases/result.json');selection=read('cases-selection-mutant/result.json');gap=read('selection-gap/result.json');mutants=read('mutants.json');integration=read('integration.json');host=read('host.json');coverage=read('coverage.json')
    for receipt in [finite,cases,selection,gap]:checked_inputs(receipt,[*FILES[1:], 'verif/delivery_build.py','verif/delivery_shells.py'])
    assert finite['result']==cases['result']=='PASS' and selection['result']=='DETECTED' and gap['result']=='DETECTED_BY_BRIDGE'
    assert len(mutants)==15 and all(r['result']=='DETECTED' for r in mutants)
    unwind=read('evidence/BeginPassengerPlatformWait_compact_negative/result.json')
    assert unwind['result']=='FAIL' and any(r[0]=='delivery_prepare.unwind.0' for r in unwind['failures'])
    checked_inputs(unwind,FILES[1:])
    for mutant in mutants:checked_inputs(read('mutants/'+mutant['mutant']+'/result.json'),FILES[1:])
    assert coverage['result']=='PASS';checked_inputs(coverage,FILES[1:])
    assert integration['whole_status']==0 and all(not r['problems'] for r in integration['cases'])
    scenario_paths=sorted((ROOT/'tests/scenarios').glob('*.txt'));scenario_names={p.stem for p in scenario_paths}
    assert {n for n in integration['inputs'] if n.startswith('tests/scenarios/') and n.endswith('.txt')}=={p.relative_to(ROOT).as_posix() for p in scenario_paths}
    checked_inputs(integration,[p.relative_to(ROOT).as_posix() for p in scenario_paths])
    for name in FILES:assert integration['build']['maintained_inputs'][name]==sha(ROOT/name),'stale integration: '+name
    assert host['result']=='PASS' and host['check']['passed'] and {r['scenario'] for r in host['check']['scenarios']}==scenario_names
    for name in FILES[1:]:assert host['build']['inputs'][str(ROOT/host['scratch']/name)]==sha(ROOT/name),'stale host: '+name
    matrix=read('proof-matrix.json');valid=[];pending=[]
    for command,path in jobs():
        if current(path):valid.append((command,path,json.loads(path.read_text())))
        else:pending.append(dict(command='python '+' '.join(command)+' --timeout 600',receipt=str(path.relative_to(ROOT)),result=json.loads(path.read_text()).get('result') if path.is_file() else 'NOT_RUN'))
    if not args.record_stop:assert matrix['result']=='PASS' and not pending and matrix['maximum_concurrent_solver_jobs']<=2,'split composition remains open'
    cert['evidence']=[
        row('Finite scalar slices','A','python verif/delivery_evidence.py enumerate',finite['stdout'].strip(),'Seven complete 65536-word slices; no Cartesian full-handler claim. Compiled with ACTOR_VERIFY. Boundary/generated cases are C.'),
        row('Resource/carrier/selection matrices','C','python verif/delivery_cases.py; python verif/delivery_cases.py --selection-mutant',cases['stdout'].strip()+'; selected-only mutant DETECTED',cases['domain']),
        row('Production bridge consumption and working-state controls','C','python verif/delivery_selection_gap.py; python verif/delivery_mutants.py','DETECTED_BY_BRIDGE; all15 defects DETECTED','Includes selected-only, private phase/craft, high carrier/index, wrong alias tag, nonconsumed next and pending; actual bridge and full machine observations.'),
        row('Actual-C unwind control','C','python verif/delivery_evidence.py BeginPassengerPlatformWait --tag compact --compact --negative --timeout 180',f'Expected FAIL delivery_prepare.unwind.0 in {unwind["seconds"]:.3f}s','Insufficient bound on the actual preparation loop is rejected; safety/unwinding assertions were not disabled.'),
        row('Literal source partition and exact orchestration','B','python verif/delivery_coverage.py',coverage['result'],coverage['coverage']),
    ]
    grouped={}
    for command,path,proof in valid:
        assert proof['hard_private_limit_bytes']==8*1024**3 and proof['peak_private_bytes']<=8*1024**3 and proof['seconds']<=601
        key=' '.join(command[:2]) if 'delivery_scalar.py' in command[0] or 'delivery_kernel.py' in command[0] else ' '.join(command)
        grouped.setdefault(key,[]).append((command,proof))
    def label(command):
        if command[0].endswith('delivery_frame_full.py'):return 'arbitrary unborrowed native fields'
        if command[0].endswith(('delivery_scalar.py','delivery_kernel.py')):return ' '.join(command[2:])
        return ' '.join(command[1:]) or 'outputs'
    for key,profiles in grouped.items():
        cert['evidence'].append(row(key,'B','; '.join('python '+' '.join(c)+' --timeout 600' for c,p in profiles),
            '; '.join(label(c)+' PASS %.3fs'%(p['seconds']) for c,p in profiles),
            'Actual extracted C; pointer/bounds/signed-overflow/unwinding assertions enabled. Output/frame/dependence split, with checked shared arbitrary helper outputs at seams where declared. See source-locked coverage and proof-matrix receipts; no timeout/cap is positive evidence.'))
    cert['evidence'] += [
        row('L0 to bridged L1 routine suites','C','python verif/delivery_integration.py --whole --local-reference',f'PASS {len(integration["cases"])} normal/poisoned cases','Actual native contact/items dependencies, full machine/device observations; receipt separates malformed/resource L1 fallbacks.'),
        row('Whole-game observations','D','python verif/delivery_integration.py --whole --local-reference',f'PASS all {len(scenario_paths)} scenarios','Per-boundary state/device/log digests, zero passenger fallback in scenario audit; unreached entries are not inferred reached.'),
        row('Scratch native-host promotion','D','python verif/delivery_host.py',f'PASS real tools/closure.py; tools/hostbuild.py; host/check.py --variant native; {len(scenario_paths)} scenarios plus256-frame smoke','Clean committed baseline plus only owned overlays. Only the scratch passenger certificate is promoted; host tooling is unchanged.'),
    ]
    cert['split_composition']=dict(matrix_result=matrix['result'],passed_properties=len(valid),pending=pending,coverage=coverage['partitions'],maximum_solver_overlap=matrix['maximum_concurrent_solver_jobs'],limits=matrix['limits'],imported_certificates=['contacts.json: kind0 whole-bridge B','falling_items.json: spawn B/full-pool transfer','adlx_effects.json: existing audio entry/child footprint'])
    negatives=[]
    for path in sorted((OUT/'negative').glob('*/result.json')):
        value=json.loads(path.read_text());negatives.append(dict(receipt=str(path.relative_to(ROOT)),result=value['result'],seconds=value['seconds'],peak_private_bytes=value.get('peak_private_bytes'),command=value['command']))
    cert['negative_results']=negatives
    if pending:
        cert['proposed_status']='boundary-established';cert['proposed_status_reason']='Recorded stop: bridge binding/projection and recorded split properties pass, but some actual-C split pieces remain open. No contract narrowing or migration proposal.'
        cert['recorded_stop']=dict(pending=pending,continuation='Keep the full scalar/resource/history/full-pool contract. Improve exact encodings or further partition the recorded failures; replay source locks, full matrix and actual scratch host before proposing migrated.')
    else:
        cert['proposed_status']='migrated';cert['proposed_status_reason']='All actual-C split output/frame/dependence pieces, matching-cut projection and protocol lemmas pass with complete compositional coverage; finite/C/D, selected-only bridge control and actual scratch host promotion pass. B is conditional on explicit disjoint resource and closed child contracts.'
    cert['scratch_acceptance']=dict(baseline_revision=host['baseline_revision'],linked_components=[r['component'] for r in host['build']['linked_units']],scenarios=[r['scenario'] for r in host['check']['scenarios']],smoke=host['check']['smoke'])
    inputs=[ROOT/n for n in FILES]+SOURCES+list((ROOT/'verif').glob('delivery*'))+[ROOT/n for n in [
        'native/actors.h','native/actor_resources.h','native/contacts.h','native/items.h','native/level.h','native/geometry.h','native/bridge/actor_projection.h',
        'c/actors.c','c/actors_states.c','c/items_water.c','c/ugh.h','c/ugh_sym.h','verif/closure_support.py','verif/windows_job.py','verif/contacts_reference.py',
        'tools/closure.py','tools/nbuild.py','tools/hostbuild.py','tools/wholegame.py','tools/difftest.py','host/check.py','metadata/verif-tools.json']]
    inputs+=scenario_paths+[ROOT/'tests'/f'{s}.py' for s in ['items_water','actors_states','actors','render','scene']]
    cert['verification_input_hashing']='sha256-lf-text';cert['verification_inputs']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest() for p in inputs}
