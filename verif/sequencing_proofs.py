"""Two worker-owned solver permits, including a reachability control per profile."""
import argparse,concurrent.futures,json,subprocess,sys,time
from closure_support import ROOT,save
from sequencing_build import OUT
from sequencing_proof import KEYS
from hud_proofs import current
def one(job,resume):
    key,reach=job;folder=OUT/('proof-reach' if reach else 'proofs')/key;path=folder/'result.json'
    if resume and not reach and current(path):return dict(key=key,reach=reach,result='PASS',reused=True)
    command=[sys.executable,'verif/sequencing_proof.py',key,*(['--reachability'] if reach else [])]
    p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);folder.mkdir(parents=True,exist_ok=True);(folder/'runner.log').write_text(p.stdout+p.stderr)
    r=json.loads(path.read_text()) if path.is_file() else {};result=r.get('result','RUNNER_ERROR')
    good=(result=='FAIL' and r.get('failures') and all('REACHED_FINAL_COMPARISON' in str(f) for f in r['failures'])) if reach else result=='PASS'
    print(key,'reach' if reach else 'proof',result,flush=True)
    return dict(key=key,reach=reach,result=result,accepted=bool(good and p.returncode==0),returncode=p.returncode)
def main():
    p=argparse.ArgumentParser();p.add_argument('--resume',action='store_true');a=p.parse_args();start=time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(lambda job:one(job,a.resume),[(k,r) for k in KEYS for r in (False,True)]))
    result='PASS' if all(r.get('accepted',r.get('reused',False)) for r in rows) else 'INCOMPLETE'
    save(OUT/'proof-matrix.json',dict(result=result,rows=rows,maximum_concurrent_solver_jobs=2,seconds=time.perf_counter()-start));assert result=='PASS'
if __name__=='__main__':main()
