"""Clean baseline: actual proofs/enumerations, L0 replay and scratch host gate."""
import argparse,subprocess,sys
from closure_support import ROOT
from player_physics_build import OUT
def run(*args):
    print('RUN '+' '.join(args),flush=True);subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fresh',action='store_true');ap.add_argument('--resume',action='store_true');a=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if a.fresh:
        import contacts_reference as ref
        ref.OUT=OUT/'reference';ref.prepare_reference(local=True,fresh=True);ref.expanded_image(local=True,fresh=True)
    run('verif/player_physics_shells.py');run('verif/player_physics_limits.py');run('verif/player_physics_proofs.py',*(['--resume'] if a.resume else []));run('verif/player_physics_bound.py');run('verif/player_physics_product.py');run('verif/player_physics_cases.py');run('verif/player_physics_pixels.py');run('verif/player_physics_mutants.py');run('verif/player_physics_coverage.py');run('verif/player_physics_nontermination.py','--witness-only');run('verif/player_physics_integration.py','--whole','--local-reference');run('verif/player_physics_certificate.py','--draft');run('verif/player_physics_host.py');run('verif/player_physics_certificate.py')
    import json,shutil
    host=json.loads((OUT/'host.json').read_text());scratch=ROOT/host['scratch'];shutil.copyfile(ROOT/'metadata/closure/player_physics.json',scratch/'metadata/closure/player_physics.json')
    cert=json.loads((scratch/'metadata/closure/player_physics.json').read_text());cert['status']='migrated';(scratch/'metadata/closure/player_physics.json').write_text(json.dumps(cert,indent=2)+'\n')
    result=subprocess.run([sys.executable,'tools/closure.py'],cwd=scratch,capture_output=True,text=True);(OUT/'final-promoted-closure.log').write_text(result.stdout+result.stderr);print(result.stdout+result.stderr,flush=True);assert not result.returncode
    run('tools/closure.py')
if __name__=='__main__':main()
