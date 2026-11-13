"""Clean-checkout loader evidence; at most two capped CBMC jobs at a time."""
import argparse,subprocess,sys,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from closure_support import ROOT,receipt,save
from adlx_loader_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fresh-reference',action='store_true');p.add_argument('--skip-proofs',action='store_true');a=p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    if a.fresh_reference:
        import contacts_reference
        contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True,fresh=True);contacts_reference.expanded_image(local=True,fresh=True)
    runs=[]
    def run(command):
        print('RUN python '+' '.join(command),flush=True)
        done=subprocess.run([sys.executable,*command],cwd=ROOT)
        return dict(command=[sys.executable,*command],returncode=done.returncode)
    for command in [['verif/adlx_loader_evidence.py'],['verif/adlx_loader_evidence.py','--negative'],['verif/adlx_loader_corpus.py'],['verif/adlx_loader_integration.py','--whole','--local-reference']]:
        runs.append(run(command))
        if runs[-1]['returncode']:break
    if not a.skip_proofs and not any(x['returncode'] for x in runs):
        pairs=[]
        for mode in ['outputs','frame','dependence']:
            pairs.append([['verif/adlx_loader_proofs.py',mode,'--slot',str(slot),*(['--canonical'] if mode=='outputs' else []),'--timeout','180'] for slot in [8,12]])
        pairs.append([['verif/adlx_loader_proofs.py','gate','--timeout','120'],['verif/adlx_loader_proofs.py','outputs','--slot','8','--canonical','--negative','--timeout','180']])
        for offsets in [[0,1],[65534,65535]]:pairs.append([['verif/adlx_loader_words.py','--offset',str(offset)] for offset in offsets])
        # A fresh subprocess per profile keeps receipt and Windows-job state
        # independent. Each child limits its whole solver tree to8GB/<=600s.
        with ThreadPoolExecutor(max_workers=2) as executor:
            for pair in pairs:
                runs.extend(executor.map(run,pair))
                if any(x['returncode'] for x in runs):break
    if not any(x['returncode'] for x in runs):
        runs.append(run(['verif/adlx_loader_host.py']))
        if not runs[-1]['returncode']:runs.append(run(['tools/closure.py']))
    save(OUT/'reproduce.json',receipt([sys.executable,'verif/adlx_loader_reproduce.py',*(['--fresh-reference'] if a.fresh_reference else []),*(['--skip-proofs'] if a.skip_proofs else [])],
        [Path(__file__),ROOT/'native/adlx_loader.c',ROOT/'native/adlx_loader.h',ROOT/'native/bridge/adlx_loader_bridge.c',ROOT/'metadata/closure/adlx_loader.json'],
        commands=runs,max_concurrent_cbmc=2,result='PASS' if not any(x['returncode'] for x in runs) else 'FAIL',seconds=time.perf_counter()-start))
    return int(any(x['returncode'] for x in runs))
if __name__=='__main__':raise SystemExit(main())
