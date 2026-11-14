"""Capped actual bridge kernel matrix, at most two solvers."""
import concurrent.futures,json,subprocess,sys
from closure_support import ROOT,save
from hud_shells import OUT
from hud_kernel import KEYS

def one(key):
    cmd=[sys.executable,'verif/hud_kernel.py',key]
    p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);folder=OUT/'kernel'/key;folder.mkdir(parents=True,exist_ok=True);(folder/'runner.log').write_text(p.stdout+p.stderr)
    j=json.loads((folder/'result.json').read_text()) if (folder/'result.json').is_file() else {}
    print(key,j.get('result','ERROR'),flush=True);return dict(key=key,result=j.get('result','ERROR'),returncode=p.returncode)
def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(one,KEYS))
    result='PASS' if all(r['result']=='PASS' and not r['returncode'] for r in rows) else 'INCOMPLETE';save(OUT/'kernel-matrix.json',dict(result=result,rows=rows,maximum_concurrent_solver_jobs=2));assert result=='PASS'
if __name__=='__main__':main()
