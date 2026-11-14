"""Clean-baseline HUD evidence, composed primitives and two-certificate promotion."""
import concurrent.futures,json,subprocess,sys
from closure_support import ROOT,save
from hud_shells import OUT
from hud_proof import KEYS
from hud_kernel import KEYS as KERNELS

def run(*args):
    print('RUN '+' '.join(args),flush=True);subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
def reach(command):
    p=subprocess.run([sys.executable,*command],cwd=ROOT,capture_output=True,text=True)
    return dict(command=command,passed=not p.returncode,output=p.stdout+p.stderr)
def main():
    run('verif/hud_shells.py');run('verif/hud_proofs.py');run('verif/hud_kernels.py');run('verif/hud_cases.py')
    commands=[['verif/hud_proof.py',k,'--reachability'] for k in KEYS]+[['verif/hud_kernel.py',k,'--reachability'] for k in KERNELS]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(reach,commands))
    save(OUT/'reachability.json',rows);assert all(r['passed'] for r in rows)
    run('verif/hud_build.py');run('verif/hud_full_cases.py');run('verif/hud_mutants.py');run('verif/hud_inventory.py');run('verif/hud_integration.py','--whole','--local-reference')
    run('verif/hud_certificate.py','--draft');run('verif/hud_host.py');run('verif/hud_certificate.py')
    host=json.loads((OUT/'host.json').read_text());scratch=ROOT/host['scratch'];cert=json.loads((ROOT/'metadata/closure/hud.json').read_text());assert cert['status']=='unanalyzed';cert['status']='migrated';save(scratch/'metadata/closure/hud.json',cert)
    p=subprocess.run([sys.executable,'tools/closure.py'],cwd=scratch,capture_output=True,text=True);(OUT/'final-promoted-closure.log').write_text(p.stdout+p.stderr);print(p.stdout+p.stderr,flush=True);assert not p.returncode
    run('tools/closure.py')
if __name__=='__main__':main()
