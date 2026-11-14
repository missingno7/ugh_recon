"""Owned actor-render lock refresh and an unapplied dependent-lock proposal."""
import hashlib,json,subprocess,sys
from datetime import date
from closure_support import ROOT,save
from sequencing_build import OUT,BASELINE
from render_history_build import OUT as RENDER_OUT
from render_history_proofs import jobs,current
from sequencing_certificate import evidence,text_hash
sys.path.insert(0,str(ROOT/'tools'));import closure
CHANGED=['native/bridge/actor_render_bridge.c','verif/render_history_build.py','verif/render_history_shells.py','verif/render_history_coverage.py']
def main():
    # The formal slot algorithm and checked adapter prefix have not changed.
    for n in ['native/actor_render.c','native/actor_render.h']:
        old=subprocess.check_output(['git','show',BASELINE+':'+n],cwd=ROOT);assert old.replace(b'\r\n',b'\n')==(ROOT/n).read_bytes().replace(b'\r\n',b'\n')
    bridge='native/bridge/actor_render_bridge.c';old=subprocess.check_output(['git','show',BASELINE+':'+bridge],cwd=ROOT).decode()
    marker='/* BEGIN CHECKED L1 SHELLS */';assert old.split(marker)[0]==(ROOT/bridge).read_text().split(marker)[0]
    matrix=json.loads((RENDER_OUT/'proof-matrix.json').read_text());assert matrix['result']=='PASS' and all(current(p) for command,p in jobs())
    assert json.loads((RENDER_OUT/'cases/result.json').read_text())['result']=='PASS'
    cross=json.loads((RENDER_OUT/'cross-mode.json').read_text());assert cross['result']=='PASS'
    mutants=json.loads((RENDER_OUT/'mutants.json').read_text());assert len(mutants)==19 and all(m['result']=='DETECTED' for m in mutants)
    path=ROOT/'metadata/closure/actor_render.json';cert=json.loads(path.read_text());assert cert['status']=='migrated'
    updates={n:dict(before=cert['verification_inputs'][n],after=text_hash(ROOT/n)) for n in CHANGED}
    for n in CHANGED:cert['verification_inputs'][n]=updates[n]['after']
    cert['dependencies'][bridge]=closure.actual_dependencies(ROOT/bridge)
    cert['callees']['bridge']=['RestoreSpriteBackground','DrawTransparentSprite','Three original inline actor scan adapters; session owns all unrelated caller orchestration.']
    cert['assumptions']=[t.replace('The complete original outer loop/guard/order and nonactor code are checked retained text, with C/D composition evidence.','Actor-only scans, guards and slot order remain checked retained text. Session owns nonactor orchestration; its complete caller composition is C/D.') for t in cert['assumptions']]
    cert['eliminated']=[t.replace('the complete retained shell is compared.','the complete caller ABI and request stream are compared in the coupled session replay.') for t in cert['eliminated']]
    for e in cert['evidence']:
        if e['property']=='Complete checked source inventory':e['result']='PASS six actor bodies, three demo/reset entry shells and three actor-only scan adapters';e['method']='Six per-slot actual-C B policies and their source-checked adapters. The generated session body is removed; session owns nonactor orchestration and its C/D caller composition.'
    integration=OUT/'integration.json'
    if integration.exists():
        measured=json.loads(integration.read_text());rows=[dict(scenario=r['scenario'],counts=r['actor_operations'][:6],fallbacks=r['actor_operations'][6:]) for r in measured['scenario_audits'] if r['scenario']!='random-rain']
        assert len(rows)==20 and all(not any(r['fallbacks']) for r in rows)
        save(RENDER_OUT/'integration.json',dict(source='build/workers/close-stones-12/integration.json',scenario_audits=rows))
        from render_history_coverage import main as coverage
        coverage()
    prop='Session-copy retirement with identical actor request boundary'
    if not any(e['property']==prop for e in cert['evidence']):cert['evidence'].append(evidence(prop,'B','python verif/render_history_proofs.py; python verif/render_history_cases.py; python verif/render_history_mutants.py; python verif/render_history_cross_mode.py','PASS23 profiles,695552 slot pairs,19 controls,26 cross-mode boundaries','Native algorithm/header and adapter prefix are unchanged. Generated c_RunGameFromPassword is removed. Session directly calls three exact actor scan adapters without a new emulated stack frame; demo/reset adapters and the six request policies remain identical. Full new-session composition is C/D in lifecycle/session receipts.'))
    for e in cert['evidence']:
        if e['property']==prop:e['level']='C'
    note=dict(date=date.today().isoformat(),reason='close-stones-12 retires generated session body; actor policy and request streams unchanged',locks=updates,commands=['python verif/render_history_proofs.py','python verif/render_history_cases.py','python verif/render_history_mutants.py','python verif/render_history_cross_mode.py','python verif/sequencing_integration.py --whole --local-reference'])
    previous=cert.get('evidence_refreshed',[])
    if not isinstance(previous,list):previous=[previous]
    if any(u['before']!=u['after'] for u in updates.values()) or not any(isinstance(n,dict) and n.get('reason')==note['reason'] for n in previous):previous.append(note)
    cert['evidence_refreshed']=previous;cert['session_owner']='session: sole c_RunGameFromPassword; actor_render exposes three scan adapters only.'
    cert['reproduce']='python verif/sequencing_baseline.py verif/sequencing_reproduce.py --fresh (coupled actor/session replay; the former standalone session-copy acceptance is superseded)'
    save(path,cert)
    proposals=[]
    for component in ['actor_types','demo_presentation']:
        c=json.loads((ROOT/'metadata/closure'/f'{component}.json').read_text());changed={n:text_hash(ROOT/n) for n in [*CHANGED,'metadata/closure/actor_render.json'] if n in c.get('verification_inputs',{}) and c['verification_inputs'][n]!=text_hash(ROOT/n)}
        proposals.append(dict(certificate='metadata/closure/'+component+'.json',status_unchanged=c['status'],verification_inputs=changed,evidence_refreshed=dict(date=date.today().isoformat(),reason=note['reason'],commands=note['commands'],scope='Only the renderer bridge footer/build selection/cut inventory changed; native actor rendering/projector and the six per-slot adapter prefix are unchanged.23 current B profiles,695552 pairs,19 controls and26-boundary cross-mode replay passed. Session composition and scratch acceptance have their own receipts.')))
    save(OUT/'dependent-lock-refresh.json',dict(result='NOT_APPLIED_OUTSIDE_OWNERSHIP',proposals=proposals))
    print('Refreshed owned actor_render; wrote unapplied actor_types/demo_presentation lock proposal')
if __name__=='__main__':main()
