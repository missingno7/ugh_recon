"""Two capped solvers; checked branch stages plus independent small properties."""
import argparse,concurrent.futures,hashlib,json,subprocess,sys,time
from pathlib import Path
from closure_support import ROOT,save
from player_physics_build import OUT
from player_physics_proof import STAGES
def jobs():
    jobs=[(['verif/player_physics_proof.py',key,'outputs'],OUT/'proofs'/(key+'-outputs')/'result.json') for key in ['sar','limit','reflect','sample']]
    jobs += [(['verif/player_physics_proof.py','sample',mode],OUT/'proofs'/('sample-'+mode)/'result.json') for mode in ['frame','dependence']]
    jobs += [(['verif/player_physics_proof.py',key,mode],OUT/'proofs'/(key+'-'+mode)/'result.json') for key in STAGES for mode in ['frame','dependence']]
    jobs += [(['verif/player_physics_stage.py',key],OUT/'stages'/key/'result.json') for key in STAGES]
    jobs += [(['verif/player_physics_children.py',key],OUT/'children'/key/'result.json') for key in ['address','landing','scan-index']]
    jobs += [(['verif/player_physics_kernel.py',key],OUT/'kernel'/key/'result.json') for key in ['open','projection','write','out','complete','append','poll-reply']]
    jobs += [(['verif/player_physics_nontermination.py','--proof-only'],OUT/'proofs/nontermination/result.json')]
    return jobs

def current(path):
    if not path.exists():return False
    proof=json.loads(path.read_text())
    return proof['result']=='PASS' and all((Path(n) if Path(n).is_absolute() else ROOT/n).is_file() and hashlib.sha256((Path(n) if Path(n).is_absolute() else ROOT/n).read_bytes()).hexdigest()==h for n,h in proof['inputs'].items())
def one(job,resume):
    command,path=job
    if resume and current(path):return dict(command=command,receipt=str(path.relative_to(ROOT)),result='PASS',reused=True)
    run=subprocess.run([sys.executable,*command,'--timeout','600'],cwd=ROOT,capture_output=True,text=True);path.parent.mkdir(parents=True,exist_ok=True);(path.parent/'runner.log').write_text(run.stdout+run.stderr)
    proof=json.loads(path.read_text()) if path.exists() else {};return dict(command=command,receipt=str(path.relative_to(ROOT)),result=proof.get('result','RUNNER_ERROR'),exit_code=run.returncode,reused=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--resume',action='store_true');a=p.parse_args();rows=[];start=time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for future in concurrent.futures.as_completed([pool.submit(one,j,a.resume) for j in jobs()]):
            row=future.result();rows.append(row);print(row['result']+' '+' '.join(row['command']),flush=True)
    events=[]
    for _,path in jobs():
        if path.exists():
            proof=json.loads(path.read_text());events += [(proof['started_utc'],1),(proof['finished_utc'],-1)] if 'started_utc' in proof else []
    live=peak=0
    for _,delta in sorted(events):live+=delta;peak=max(peak,live)
    result='PASS' if peak<=2 and all(current(p) for _,p in jobs()) else 'INCOMPLETE';save(OUT/'proof-matrix.json',dict(result=result,rows=rows,maximum_concurrent_solver_jobs=peak,seconds=time.perf_counter()-start));print(result,flush=True);assert result=='PASS'
if __name__=='__main__':main()
