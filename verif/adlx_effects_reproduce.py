"""Reproduce the effects closure using only maintained inputs and pinned tools."""
import argparse,subprocess,sys,json,time
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_effects_build import OUT

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--skip-proofs',action='store_true');p.add_argument('--fresh-reference',action='store_true');a=p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);started=time.perf_counter()
    if a.fresh_reference:
        import contacts_reference
        contacts_reference.OUT=OUT/'reference'
        contacts_reference.prepare_reference(local=True,fresh=True)
        contacts_reference.expanded_image(local=True,fresh=True)
    commands=[['verif/adlx_effects_evidence.py','samples'],['verif/adlx_effects_corpus.py'],['verif/adlx_effects_faults.py']]
    if not a.skip_proofs:
        commands += [['verif/adlx_effects_main_compat.py'],['verif/adlx_effects_proofs.py']]
        commands += [['verif/adlx_effects_timer_scalar.py',mode] for mode in ['outputs','frame','dependencies']]
        commands += [['verif/adlx_effects_proofs.py','--op','4','--negative','--timeout','120']]
    commands += [['verif/adlx_effects_integration.py','--whole','--local-reference'],['verif/adlx_effects_scenario.py'],['verif/adlx_effects_host.py'],['tools/closure.py']]
    runs=[]
    for command in commands:
        print('RUN python '+' '.join(command),flush=True)
        run=subprocess.run([sys.executable,*command],cwd=ROOT)
        runs.append(dict(command=[sys.executable,*command],returncode=run.returncode))
        if run.returncode and command!=['tools/closure.py']:break
    result=receipt([sys.executable,'verif/adlx_effects_reproduce.py',*(['--skip-proofs'] if a.skip_proofs else []),*(['--fresh-reference'] if a.fresh_reference else [])],
        [Path(__file__),ROOT/'native/adlx_effects.c',ROOT/'native/adlx_effects.h',ROOT/'native/bridge/adlx_effects_bridge.c',ROOT/'metadata/closure/adlx_effects.json'],
        commands=runs,result='PASS' if all(r['returncode']==0 for r in runs) else 'FAIL',seconds=time.perf_counter()-started)
    save(OUT/'reproduce.json',result)
    return int(any(r['returncode'] for r in runs))
if __name__=='__main__':raise SystemExit(main())
