"""Assemble measured review evidence without granting administrative status."""
import hashlib,json,sys
from pathlib import Path
from closure_support import ROOT,hashes
from hazards_build import OUT,NAMES,ENTRIES,SOURCES
sys.path.insert(0,str(ROOT/'tools'))
import closure

def entry(prop,level,method,command,result):
    return dict(property=prop,level=level,method=method,command=command,result=result,date='2026-11-13')

def main():
    path=ROOT/'metadata/closure/hazards.json';cert=json.loads(path.read_text())
    host=json.loads((OUT/'host.json').read_text())
    assert host['result']=='PASS' and host['check']['passed'],'native host review is required before proposing migration'
    scratch=ROOT/host['scratch']
    for name in ['native/hazards.c','native/hazards.h','native/bridge/hazards_bridge.c']:
        assert host['build']['inputs'][str(scratch/name)]==hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),f'stale native host review: {name}'
    cert['dependencies']={name:closure.actual_dependencies(ROOT/name) for name in cert['native']['files']}
    cert['indirect']['targets']=json.loads((ROOT/'metadata/program-model.json').read_text())['indirect_sites']['013B:236F']['targets']
    cert['interface']['preconditions']=list(dict.fromkeys([*cert['interface']['preconditions'],
        'Native bridge animation cursor is FFFE or an even word 0..30; larger/odd cursors use L1. All shipped sequences have at most fourteen frames.',
        'Tree release/cooldown use canonical finite reward-list ordinals 0..9. Bird flight uses one of the descriptor flight vectors.']))
    evidence=[entry('Full dispatcher descriptor target set','C','Independent expanded oracle bytes against all program-model origin_words; every zero and no-op retained',
        'python verif/hazards_inventory.py','PASS: 52 fields, 31 distinct targets'),
        entry('Compiled finite and generated transitions','A','Actual L1 and native C; five full 16-bit countdown domains, three full low-score-word domains at high FFFF, complete Dino phase word domain; other inputs fixed in these finite domains',
        'python verif/hazards_evidence.py generated','PASS: 589824 exhaustive-domain comparisons plus 30000 generated cases (generated subset is C, not A)'),
        entry('Journal/register/flag shell and native contacts/items composition','C','Original L0 versus combined bridged L1, normal and poisoned register inputs',
        'python verif/hazards_integration.py --whole --local-reference','PASS: 804 focused hazard cases; 940 wrapper entries with 26 out-of-contract fallback calls. Whole-game fallback count zero. Earlier broad run also passed 2754 item/actor/render cases'),
        entry('Whole-game observations','D','All deterministic page-boundary RAM/device and ordered-log digests against the independent rebuilt original',
        'python verif/hazards_integration.py --whole --local-reference','PASS all 16 maintained scenarios; enemy reaches bird, Triopterus and tree, not Dino'),
        entry('Additional Dino witness','D','Exact input-only real-entry/password scenario; no simulation RAM edits',
        'python verif/hazards_scenario.py','PASS 300 boundaries and 268 native Dino force updates, no fallback'),
        entry('Actual scratch promotion and native host','D','Maintained sources copied into scratch; certificate status=migrated there; actual unmodified CLI builder/checker, no selection monkeypatch',
        'python verif/hazards_host.py -> python tools/hostbuild.py; python host/check.py --variant native',
        'PASS 17 scenarios including Dino and 256-frame attract smoke'),
        entry('Exhaustive input-domain and routing defect controls','C','Scratch native timer70->71, impact ordinary->alternate, Dino +41->+40; comparison executable must reject each',
        'python verif/hazards_mutants.py','PASS all three detected after adding an explicit complete Dino phase domain; first random-only force experiment missed its defect')]
    successful=[];incomplete=[]
    for name in [*ENTRIES,'dispatcher']:
        folder=OUT/f'{name}-s1';file=folder/'result.json'
        if not file.exists():incomplete.append(name);continue
        result=json.loads(file.read_text())
        if result['result']!='PASS':incomplete.append(name);continue
        proof_inputs=['native/hazards.c','native/hazards.h','verif/hazards_harness.c']
        if any(result['inputs'].get(p)!=hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in proof_inputs):
            incomplete.append(name+' (stale receipt)');continue
        successful.append(name)
        evidence.append(entry(name+' actual-C one-step equivalence','B',
            'Actual extracted L1 and maintained native C; arbitrary scalar words under the harness assumptions (platform<10, valid direction/player-array sizes, even cursor0..30 or FFFE, immutable consistent animation windows). Actual contacts with one stone; direct release input index0. Compare resulting slot/shared craft/stone state, requests and ordered semantic stores. Dispatcher instead uses arbitrary count0..5 and observing no-op callbacks.',
            f'python verif/hazards_evidence.py {name} --timeout {300 if name=="UpdateTriopterusCharge" else 30 if name=="dispatcher" else 60}',
            f"PASS: unwind {result['unwind']}, per-loop unwind assertions, bounds/pointer/signed-overflow checks; {result['seconds']:.3f}s. One-stone footprint is an explicit B bound, not sixteen-stone composition."))
    cert['evidence']=evidence
    cert['proposed_status']='migrated'
    cert['proposed_status_reason']='Native implementation and bridge pass C/D and an actual native-host scratch promotion. The general sixteen-stone contract and full bridge projection remain C; do not propose verified-under-assumptions or integration-validated for the whole contract.'
    random_cert=json.loads((ROOT/'metadata/closure/random.json').read_text())
    modern_hash=hashlib.sha256((ROOT/'docs/modernization.md').read_bytes().replace(b'\r\n',b'\n')).hexdigest()
    random_stale=random_cert['verification_inputs']['docs/modernization.md']!=modern_hash
    cert['uncertainty']=[
        ('Repository-wide closure gate is blocked by pre-existing metadata/closure/random.json locking the old docs/modernization.md.' if random_stale else
         'The earlier stale random documentation lock was refreshed externally during this round. This worker did not edit that certificate or bypass any lock; the final global gate is recorded in the report.'),
        'Small-footprint CBMC successes: '+', '.join(successful)+'. Missing/unproved standard profiles: '+(', '.join(incomplete) if incomplete else 'none')+'.',
        'Sixteen-stone whole-transition profiles timed out; no proof is claimed for them. Relational contact-contract and semantic-only experiments are separate receipts, never silently substituted for full actual-contact composition.',
        'The native module is therefore a migration candidate, not a completed level-B closure. Bridge malformed-index/resource/alias fallbacks are compatibility, not native proofs.',
        'The normal-state bridge retains a detailed machine shell to preserve all deterministic register/flag outputs. Eliminating that shell requires caller liveness review outside this round.',
        'Only the supervisor can promote status. Administrative status stays unanalyzed.']
    cert['verification_input_hashing']='sha256-lf-text'
    inputs=[*SOURCES,*[ROOT/name for name in ['native/hazards.h','native/contacts.h','native/items.h','native/geometry.h','native/level.h','native/bridge/level_projection.h']],*sorted((ROOT/'verif').glob('hazards*')),
        ROOT/'verif/closure_support.py',ROOT/'verif/windows_job.py',ROOT/'tools/closure.py',ROOT/'tools/hostbuild.py',ROOT/'host/check.py',
        ROOT/'c/actors.c',ROOT/'c/actors_states.c',ROOT/'c/items_water.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',ROOT/'metadata/program-model.json',ROOT/'metadata/verif-tools.json']
    cert['verification_inputs']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest() for p in inputs if p.is_file()}
    path.write_text(json.dumps(cert,indent=2)+'\n')
    print('CBMC standard successes',len(successful),'unproved',incomplete)
if __name__=='__main__':main()
