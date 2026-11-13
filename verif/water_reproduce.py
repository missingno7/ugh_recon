"""Clean-checkout reproduction, capped split proofs and real scratch promotion."""
import argparse,subprocess,sys
from closure_support import ROOT
from water_build import OUT
def run(*args,allow_failure=False):
    print('RUN '+' '.join(args),flush=True);value=subprocess.run([sys.executable,*args],cwd=ROOT)
    if not allow_failure:value.check_returncode()
def main():
    p=argparse.ArgumentParser();p.add_argument('--fresh',action='store_true');p.add_argument('--resume',action='store_true');p.add_argument('--record-stop',action='store_true');p.add_argument('--working-tree-lint',action='store_true');a=p.parse_args()
    if a.fresh:
        import contacts_reference as reference
        reference.OUT=OUT/'reference';reference.prepare_reference(local=True,fresh=True);reference.expanded_image(local=True,fresh=True)
    run('verif/water_shells.py');run('verif/water_coverage.py');run('verif/water_limits.py')
    run('verif/water_proofs.py',*(['--resume'] if a.resume else []),allow_failure=a.record_stop)
    run('verif/water_bound.py');run('verif/water_cases.py');run('verif/water_extra_cases.py');run('verif/water_mutants.py')
    run('verif/water_composition.py');run('verif/water_integration.py','--whole','--local-reference');run('verif/water_reachability.py')
    run('verif/water_witness.py','probe','--frames','2400');run('verif/water_witness.py','verify')
    run('verif/water_certificate.py','--draft');run('verif/water_host.py');run('verif/water_certificate.py',*(['--record-stop'] if a.record_stop else []))
    if a.working_tree_lint:run('tools/closure.py')
if __name__=='__main__':main()
