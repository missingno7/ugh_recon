"""Replay the complete split matrix, with two capped solver processes at most.

--resume accepts only PASS receipts whose complete recorded input hashes still
match. It never treats a timeout/cap/error as a proof or overwrites its archive.
"""
import argparse,concurrent.futures,hashlib,json,subprocess,sys,time
from pathlib import Path
from closure_support import ROOT,save
from water_build import OUT
from water_pieces import pieces

def jobs():
    result=[]
    for key in pieces():
        for mode in ['outputs','native-frame','ram-frame','full-frame','dependencies']:
            result.append((['verif/water_scalar.py',key,mode],OUT/'scalar'/(key+'-'+mode)/'result.json'))
    for key in ['emit','consume','complete','dispatch','ignore']:
        for mode in ['outputs','frame','dependencies']:
            result.append((['verif/water_kernel.py',key,mode],OUT/'kernel'/(key+'-'+mode)/'result.json'))
    for mode in ['outputs','frame','dependencies']:
        result.append((['verif/water_projection.py',mode],OUT/'projection'/mode/'result.json'))
    from water_projection import FIELDS
    for field in range(len(FIELDS)):
        result.append((['verif/water_projection.py','corruption','--field',str(field)],OUT/'projection'/('corruption'+str(field))/'result.json'))
    return result

def current(path):
    if not path.is_file():return False
    receipt=json.loads(path.read_text())
    if receipt.get('result')!='PASS':return False
    for name,value in receipt['inputs'].items():
        source=Path(name) if Path(name).is_absolute() else ROOT/name
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=value:return False
    return True

def one(job,resume,timeout):
    args,path=job
    if resume and current(path):return dict(command=args,receipt=str(path.relative_to(ROOT)),result='PASS',reused=True)
    command=[sys.executable,*args,'--timeout',str(timeout)]
    run=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    path.parent.mkdir(parents=True,exist_ok=True);(path.parent/'runner.log').write_text(run.stdout+run.stderr)
    value=json.loads(path.read_text()) if path.is_file() else {}
    return dict(command=args,receipt=str(path.relative_to(ROOT)),result=value.get('result','RUNNER_ERROR'),exit_code=run.returncode,reused=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--resume',action='store_true');p.add_argument('--timeout',type=int,default=600);a=p.parse_args()
    assert 0<a.timeout<=600
    start=time.perf_counter();rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        pending=[executor.submit(one,job,a.resume,a.timeout) for job in jobs()]
        for future in concurrent.futures.as_completed(pending):
            row=future.result();rows.append(row);print(row['result']+' '+' '.join(row['command']),flush=True)
            save(OUT/'proof-matrix-progress.json',dict(rows=rows,seconds=time.perf_counter()-start))
    rows.sort(key=lambda r:r['receipt'])
    intervals=[]
    for row in rows:
        proof=json.loads((ROOT/row['receipt']).read_text())
        if proof.get('started_utc'):intervals.append((proof['started_utc'],proof['finished_utc']))
    events=sorted([(a,1) for a,b in intervals]+[(b,-1) for a,b in intervals]);live=peak=0
    for _,delta in events:live+=delta;peak=max(peak,live)
    result='PASS' if all(r['result']=='PASS' and current(ROOT/r['receipt']) for r in rows) and peak<=2 else 'INCOMPLETE'
    save(OUT/'proof-matrix.json',dict(result=result,rows=rows,seconds=time.perf_counter()-start,maximum_concurrent_solver_jobs=peak,limits=dict(private_bytes=8*1024**3,seconds=a.timeout)))
    print(result+' '+str(len(rows))+' split properties; maximum solver overlap '+str(peak),flush=True)
    assert result=='PASS'
if __name__=='__main__':main()
