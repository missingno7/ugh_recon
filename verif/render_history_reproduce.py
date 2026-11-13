"""Clean-checkout actor history closure replay; no existing receipts required."""
import argparse,subprocess,sys
from closure_support import ROOT
from render_history_build import OUT
def run(*args):
    print('RUN '+' '.join(args),flush=True);subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('--fresh',action='store_true');p.add_argument('--resume',action='store_true');p.add_argument('--working-tree-lint',action='store_true');a=p.parse_args()
    if a.fresh:
        import contacts_reference as reference
        reference.OUT=OUT/'reference';reference.prepare_reference(local=True,fresh=True);reference.expanded_image(local=True,fresh=True)
    run('verif/render_history_shells.py');run('verif/render_history_limits.py');run('verif/render_history_proofs.py',*(['--resume'] if a.resume else []));run('verif/render_history_bound.py');run('verif/render_history_cases.py');run('verif/render_history_mutants.py');run('verif/render_history_cross_mode.py');run('verif/render_history_integration.py','--whole','--local-reference');run('verif/render_history_coverage.py');run('verif/render_history_certificate.py','--draft');run('verif/render_history_host.py');run('verif/render_history_certificate.py')
    if a.working_tree_lint:run('tools/closure.py')
if __name__=='__main__':main()
