"""Audio API closure evidence; SB gameplay limitation stays explicit."""
import argparse,subprocess,sys,time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_samples_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--proofs-only',action='store_true');p.add_argument('--skip-proofs',action='store_true');a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True);start=time.perf_counter();rows=[]
    def run(command):
        print('RUN',' '.join(command),flush=True);result=subprocess.run([sys.executable,*command],cwd=ROOT);return dict(command=command,returncode=result.returncode)
    if not a.proofs_only:
        for command in [['verif/adlx_samples_inventory.py'],['verif/adlx_samples_evidence.py'],['verif/adlx_samples_corpus.py'],['verif/adlx_samples_sb.py'],['verif/adlx_samples_integration.py','--whole','--local-reference']]:
            rows.append(run(command))
            if rows[-1]['returncode']:break
    if not a.skip_proofs and not any(r['returncode'] for r in rows):
        commands=[['verif/adlx_samples_proofs.py',entry,'outputs',*(['--bounded-divisor'] if entry=='division' else [])] for entry in ['reset','scale','offset','division','import']]
        commands += [['verif/adlx_samples_voice.py',role,mode] for role in ['select','accumulate'] for mode in ['outputs','frame','dependence']]
        commands += [['verif/adlx_samples_proofs.py',entry,'outputs','--negative',*(['--bounded-divisor'] if entry=='division' else [])] for entry in ['reset','scale','division','import']]
        with ThreadPoolExecutor(max_workers=2) as pool:
            for i in range(0,len(commands),2):
                rows.extend(pool.map(run,commands[i:i+2]))
                if any(r['returncode'] for r in rows):break
    save(OUT/('proofs-replay.json' if a.proofs_only else 'reproduce.json'),receipt([sys.executable,'verif/adlx_samples_reproduce.py',*sys.argv[1:]],[Path(__file__),ROOT/'native/adlx_samples.c',ROOT/'native/adlx_samples.h',ROOT/'native/bridge/adlx_samples_bridge.c'],commands=rows,result='PASS' if not any(r['returncode'] for r in rows) else 'FAIL',seconds=time.perf_counter()-start))
    return int(any(r['returncode'] for r in rows))
if __name__=='__main__':raise SystemExit(main())
