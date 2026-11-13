"""Fresh six-entry lifetime corpus, capped split proofs, actual scratch host gates."""
import argparse,subprocess,sys,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from closure_support import ROOT,receipt,save
from adlx_lifetime_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fresh-reference',action='store_true');p.add_argument('--skip-proofs',action='store_true');p.add_argument('--proofs-only',action='store_true');a=p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);start=time.perf_counter();rows=[]
    if a.fresh_reference:
        import contacts_reference
        contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True,fresh=True);contacts_reference.expanded_image(local=True,fresh=True)
    def run(command):
        print('RUN python '+' '.join(command),flush=True);r=subprocess.run([sys.executable,*command],cwd=ROOT)
        return dict(command=[sys.executable,*command],returncode=r.returncode)
    if not a.proofs_only:
        commands=[['verif/adlx_lifetime_inventory.py'],['verif/adlx_lifetime_evidence.py'],['verif/adlx_lifetime_evidence.py','--exhaustive-probe'],*([ 'verif/adlx_lifetime_evidence.py','--negative',n] for n in ['reset','probe','measure']),['verif/adlx_lifetime_corpus.py'],['verif/adlx_lifetime_integration.py','--whole','--local-reference']]
        for command in commands:
            rows.append(run(command))
            if rows[-1]['returncode']:break
    if not a.skip_proofs and not any(row['returncode'] for row in rows):
        commands=[['verif/adlx_lifetime_proofs.py',entry,mode] for entry in ['reset','initialize','shutdown','begin','finish','calibrate'] for mode in ['outputs','frame','dependence']]
        commands += [['verif/adlx_lifetime_scalar.py',mode] for mode in ['outputs','frame','dependence']]
        commands += [['verif/adlx_lifetime_proofs.py','finish','outputs','--negative'],['verif/adlx_lifetime_proofs.py','initialize','outputs','--negative'],['verif/adlx_lifetime_scalar.py','outputs','--negative']]
        with ThreadPoolExecutor(max_workers=2) as executor:
            for i in range(0,len(commands),2):
                rows.extend(executor.map(run,commands[i:i+2]))
                if any(row['returncode'] for row in rows):break
    if not a.proofs_only and not any(row['returncode'] for row in rows):
        rows.append(run(['verif/adlx_lifetime_host.py']))
        if not rows[-1]['returncode']:rows.append(run(['tools/closure.py']))
    save(OUT/('proofs-replay.json' if a.proofs_only else 'reproduce.json'),receipt([sys.executable,'verif/adlx_lifetime_reproduce.py',*sys.argv[1:]],[Path(__file__),ROOT/'native/adlx_lifetime.c',ROOT/'native/adlx_lifetime.h',ROOT/'native/bridge/adlx_lifetime_bridge.c',ROOT/'metadata/closure/adlx_lifetime.json'],result='PASS' if not any(row['returncode'] for row in rows) else 'FAIL',commands=rows,max_concurrent_cbmc=2,seconds=time.perf_counter()-start))
    return int(any(row['returncode'] for row in rows))
if __name__=='__main__':raise SystemExit(main())
