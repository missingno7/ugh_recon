"""Rebuild references and replay accepted audio allocation evidence."""
import argparse,subprocess,sys,time
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_allocation_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fresh-reference',action='store_true');a=p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    if a.fresh_reference:
        import contacts_reference
        contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True,fresh=True);contacts_reference.expanded_image(local=True,fresh=True)
    commands=[['verif/adlx_allocation_evidence.py'],['verif/adlx_allocation_evidence.py','--negative'],
        ['verif/adlx_allocation_selection.py'],['verif/adlx_allocation_selection.py','--negative'],
        ['verif/adlx_allocation_corpus.py'],['verif/adlx_allocation_integration.py','--whole','--local-reference'],
        ['verif/adlx_allocation_host.py'],['tools/closure.py']]
    runs=[]
    for command in commands:
        print('RUN python '+' '.join(command),flush=True);run=subprocess.run([sys.executable,*command],cwd=ROOT)
        runs.append(dict(command=[sys.executable,*command],returncode=run.returncode))
        if run.returncode and command!=['tools/closure.py']:break
    save(OUT/'reproduce.json',receipt([sys.executable,'verif/adlx_allocation_reproduce.py',*(['--fresh-reference'] if a.fresh_reference else [])],
        [Path(__file__),ROOT/'native/adlx_allocation.c',ROOT/'native/adlx_allocation.h',ROOT/'native/bridge/adlx_allocation_bridge.c',ROOT/'metadata/closure/adlx_allocation.json'],
        commands=runs,result='PASS' if all(x['returncode']==0 for x in runs) else 'FAIL',seconds=time.perf_counter()-start))
    return int(any(x['returncode'] for x in runs))
if __name__=='__main__':raise SystemExit(main())
