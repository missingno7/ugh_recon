"""Reproduce the coupled passenger unit with pinned tools and owned scratch.

The scratch host is a clean committed baseline plus this unit's owned files;
concurrent audio work is not an input. No assets, maintained L1 or Git state are
written. Per-handler proofs run sequentially to keep solver resource use bounded.
"""
import argparse,subprocess,sys
from closure_support import ROOT
from delivery_build import OUT,NAMES

def run(*args):
    print('RUN '+' '.join(args),flush=True);subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fresh',action='store_true');p.add_argument('--working-tree-lint',action='store_true');p.add_argument('--record-stop',action='store_true',help='Reproduce only the recorded proved boundary, without a migration proposal');a=p.parse_args()
    if a.fresh:
        import contacts_reference
        contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True,fresh=True);contacts_reference.expanded_image(local=True,fresh=True)
    run('verif/delivery_shells.py');run('verif/delivery_evidence.py','enumerate')
    proved=[NAMES[i] for i in [0,2,4,6,8,9]] if a.record_stop else NAMES
    for name in proved:run('verif/delivery_evidence.py',name,'--tag','compact','--compact','--timeout','600')
    run('verif/delivery_evidence.py','BeginPassengerPlatformWait','--tag','compact','--compact','--negative','--timeout','180')
    run('verif/delivery_mutants.py');run('verif/delivery_cases.py');run('verif/delivery_cases.py','--selection-mutant');run('verif/delivery_selection_gap.py');run('verif/delivery_integration.py','--whole','--local-reference')
    run('verif/delivery_certificate.py','--draft');run('verif/delivery_host.py');run('verif/delivery_certificate.py',*(['--record-stop'] if a.record_stop else []))
    if a.working_tree_lint:run('tools/closure.py')
if __name__=='__main__':main()
