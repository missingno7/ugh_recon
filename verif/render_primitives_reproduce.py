"""Complete clean-baseline rendering-primitive evidence and scratch acceptance."""
import concurrent.futures,json,subprocess,sys
from closure_support import ROOT,save
from render_primitives_shells import OUT
from render_primitives_proof import KEYS

def run(*args):
    print('RUN '+' '.join(args),flush=True);subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
def reach(key):
    command=[sys.executable,'verif/render_primitives_proof.py',key,'--reachability']
    p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    return dict(key=key,command=command,passed=not p.returncode,output=p.stdout+p.stderr)
def main():
    run('verif/render_primitives_shells.py');run('verif/render_primitives_proofs.py');run('verif/render_primitives_cases.py')
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(reach,KEYS))
    save(OUT/'reachability.json',rows);assert all(r['passed'] for r in rows)
    run('verif/render_primitives_build.py');run('verif/render_primitives_mutants.py');run('verif/render_primitives_inventory.py');run('verif/render_primitives_integration.py','--whole','--local-reference')
    run('verif/render_primitives_certificate.py','--draft');run('verif/render_primitives_host.py');run('verif/render_primitives_certificate.py')
    host=json.loads((OUT/'host.json').read_text());scratch=ROOT/host['scratch'];cert=json.loads((ROOT/'metadata/closure/render_primitives.json').read_text());assert cert['status']=='unanalyzed';cert['status']='migrated';save(scratch/'metadata/closure/render_primitives.json',cert)
    p=subprocess.run([sys.executable,'tools/closure.py'],cwd=scratch,capture_output=True,text=True);(OUT/'final-promoted-closure.log').write_text(p.stdout+p.stderr);print(p.stdout+p.stderr,flush=True);assert not p.returncode
    run('tools/closure.py')
if __name__=='__main__':main()
