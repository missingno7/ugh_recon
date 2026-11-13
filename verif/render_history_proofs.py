"""Two capped jobs at a time; source-locked successful receipts only."""
import argparse,concurrent.futures,hashlib,json,subprocess,sys,time
from pathlib import Path
from closure_support import ROOT,save
from render_history_build import OUT
from render_history_shells import OPS
def jobs():
    return [(['verif/render_history_proof.py',op,mode],OUT/'proofs'/(op+'-'+mode)/'result.json') for op in OPS for mode in ['outputs','native-frame','dependencies']]+[(['verif/render_history_sequences.py',mode],OUT/'sequences'/mode/'result.json') for mode in ['pages','seeds','initialize-frame','loader-frame']]+[(['verif/render_history_projection.py'],OUT/'projection/result.json')]
def current(path):
    if not path.exists():return False
    proof=json.loads(path.read_text())
    return proof['result']=='PASS' and all((Path(n) if Path(n).is_absolute() else ROOT/n).is_file() and hashlib.sha256((Path(n) if Path(n).is_absolute() else ROOT/n).read_bytes()).hexdigest()==v for n,v in proof['inputs'].items())
def one(job,resume):
    command,path=job
    if resume and current(path):return dict(command=command,receipt=str(path.relative_to(ROOT)),result='PASS',reused=True)
    run=subprocess.run([sys.executable,*command,'--timeout','600'],cwd=ROOT,capture_output=True,text=True)
    path.parent.mkdir(parents=True,exist_ok=True);(path.parent/'runner.log').write_text(run.stdout+run.stderr)
    proof=json.loads(path.read_text()) if path.exists() else {}
    return dict(command=command,receipt=str(path.relative_to(ROOT)),result=proof.get('result','RUNNER_ERROR'),reused=False,exit_code=run.returncode)
def main():
    p=argparse.ArgumentParser();p.add_argument('--resume',action='store_true');a=p.parse_args();start=time.perf_counter();rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for future in concurrent.futures.as_completed([pool.submit(one,j,a.resume) for j in jobs()]):
            row=future.result();rows.append(row);print(row['result']+' '+' '.join(row['command']),flush=True)
    events=[]
    for _,path in jobs():
        if path.exists():
            proof=json.loads(path.read_text());events += [(proof['started_utc'],1),(proof['finished_utc'],-1)] if 'started_utc' in proof else []
    live=peak=0
    for _,delta in sorted(events):live+=delta;peak=max(peak,live)
    result='PASS' if peak<=2 and all(current(path) for _,path in jobs()) else 'INCOMPLETE'
    save(OUT/'proof-matrix.json',dict(result=result,rows=rows,maximum_concurrent_solver_jobs=peak,seconds=time.perf_counter()-start));print(result,flush=True);assert result=='PASS'
if __name__=='__main__':main()
