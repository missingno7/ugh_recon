"""Clean checkout: approved types transfer, actual-C proofs and scratch host."""
import argparse,subprocess,sys
from closure_support import ROOT
from demo_scene_build import OUT
def run(*args):
    print('RUN '+' '.join(args),flush=True);subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('--fresh',action='store_true');p.add_argument('--resume',action='store_true');p.add_argument('--working-tree-lint',action='store_true');a=p.parse_args()
    if a.fresh:
        import contacts_reference as ref
        ref.OUT=OUT/'reference';ref.prepare_reference(local=True,fresh=True);ref.expanded_image(local=True,fresh=True)
    run('verif/demo_scene_types.py');run('verif/demo_scene_shells.py');run('verif/demo_scene_limits.py');run('verif/demo_scene_proofs.py',*(['--resume'] if a.resume else []));run('verif/demo_scene_bound.py');run('verif/demo_scene_cases.py');run('verif/demo_scene_mutants.py');run('verif/demo_scene_order.py');run('verif/demo_scene_integration.py','--whole','--local-reference');run('verif/demo_scene_coverage.py');run('verif/demo_scene_certificate.py','--draft');run('verif/demo_scene_host.py');run('verif/demo_scene_certificate.py')
    if a.working_tree_lint:run('tools/closure.py')
if __name__=='__main__':main()
