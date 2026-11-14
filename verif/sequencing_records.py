"""Two capped CBMC jobs for six complete actual level-record pairs."""
import concurrent.futures,json,subprocess,sys,time
from closure_support import ROOT,save
from sequencing_build import OUT
from session_record_proof import KEYS
def one(job):
    key,mode,reach=job;folder=OUT/('record-reach' if reach else 'record-proofs')/(key+'-'+mode)
    command=[sys.executable,'verif/session_record_proof.py',key,mode,*(['--reachability'] if reach else [])]
    p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);folder.mkdir(parents=True,exist_ok=True);(folder/'runner.log').write_text(p.stdout+p.stderr)
    r=json.loads((folder/'result.json').read_text()) if (folder/'result.json').exists() else {};result=r.get('result','RUNNER_ERROR')
    good=(result=='FAIL' and r.get('failures') and all('REACHED_FINAL_COMPARISON' in str(f) for f in r['failures'])) if reach else result=='PASS'
    print(key,mode,'reach' if reach else 'proof',result,flush=True)
    return dict(key=key,mode=mode,reach=reach,result=result,accepted=bool(good and p.returncode==0))
def main():
    start=time.perf_counter();jobs=[(k,m,r) for k in KEYS for m in ['output','frame','dependence'] for r in [False,True]]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(one,jobs))
    result='PASS' if all(r['accepted'] for r in rows) else 'INCOMPLETE';save(OUT/'record-matrix.json',dict(result=result,rows=rows,maximum_concurrent_solver_jobs=2,seconds=time.perf_counter()-start));assert result=='PASS'
if __name__=='__main__':main()
