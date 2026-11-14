"""Two solver permits, exact input reuse and the complete branch-stage matrix."""
import argparse,concurrent.futures,hashlib,json,subprocess,sys,time
from pathlib import Path
from closure_support import ROOT,save
from hud_shells import OUT
from hud_proof import KEYS,STAGES

def jobs():return [(key,mode) for key in KEYS for mode in (['output','frame','dependence'] if key in STAGES or key=='bar-next' else ['output'])]
def current(path):
    if not path.is_file():return False
    j=json.loads(path.read_text())
    return j['result']=='PASS' and all((Path(n) if Path(n).is_absolute() else ROOT/n).is_file() and hashlib.sha256((Path(n) if Path(n).is_absolute() else ROOT/n).read_bytes()).hexdigest()==h for n,h in j['inputs'].items())
def one(job,resume):
    key,mode=job;path=OUT/'proofs'/(key+'-'+mode)/'result.json'
    if resume and current(path):return dict(key=key,mode=mode,result='PASS',reused=True)
    command=[sys.executable,'verif/hud_proof.py',key,mode,'--timeout','600']
    p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);path.parent.mkdir(parents=True,exist_ok=True);(path.parent/'runner.log').write_text(p.stdout+p.stderr)
    j=json.loads(path.read_text()) if path.exists() else {}
    print(key,mode,j.get('result','RUNNER_ERROR'),flush=True)
    return dict(key=key,mode=mode,result=j.get('result','RUNNER_ERROR'),returncode=p.returncode)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resume',action='store_true');a=ap.parse_args();start=time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(lambda job:one(job,a.resume),jobs()))
    result='PASS' if all(current(OUT/'proofs'/(key+'-'+mode)/'result.json') for key,mode in jobs()) else 'INCOMPLETE'
    save(OUT/'proof-matrix.json',dict(result=result,rows=rows,seconds=time.perf_counter()-start,maximum_concurrent_solver_jobs=2));print(result,flush=True);assert result=='PASS'
if __name__=='__main__':main()
