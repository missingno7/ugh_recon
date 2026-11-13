"""Reproduce the coupled passenger unit with pinned tools and owned scratch.

The scratch host is a clean committed baseline plus this unit's owned files;
concurrent audio work is not an input. No assets, maintained L1 or Git state are
written. Split profiles use at most two capped solver jobs.
"""
import argparse,subprocess,sys
from closure_support import ROOT
from delivery_build import OUT

def run(*args,allow_failure=False):
    print('RUN '+' '.join(args),flush=True);value=subprocess.run([sys.executable,*args],cwd=ROOT)
    if not allow_failure:value.check_returncode()
    return value.returncode
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fresh',action='store_true');p.add_argument('--resume',action='store_true',help='Reuse only current source-locked PASS split receipts');p.add_argument('--working-tree-lint',action='store_true');p.add_argument('--record-stop',action='store_true',help='Record incomplete pieces instead of proposing migration');a=p.parse_args()
    if a.fresh:
        import contacts_reference
        contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True,fresh=True);contacts_reference.expanded_image(local=True,fresh=True)
    run('verif/delivery_shells.py');run('verif/delivery_coverage.py');run('verif/delivery_limits.py')
    run('verif/delivery_proofs.py',*(['--resume'] if a.resume else []),allow_failure=a.record_stop)
    run('verif/delivery_evidence.py','BeginPassengerPlatformWait','--tag','compact','--compact','--negative','--timeout','180')
    run('verif/delivery_evidence.py','enumerate')
    run('verif/delivery_mutants.py');run('verif/delivery_cases.py');run('verif/delivery_cases.py','--selection-mutant');run('verif/delivery_selection_gap.py');run('verif/delivery_integration.py','--whole','--local-reference')
    run('verif/delivery_certificate.py','--draft');run('verif/delivery_host.py');run('verif/delivery_certificate.py',*(['--record-stop'] if a.record_stop else []))
    if a.working_tree_lint:run('tools/closure.py')
if __name__=='__main__':main()
