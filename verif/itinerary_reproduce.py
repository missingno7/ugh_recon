"""Reproduce passenger evidence from maintained files and pinned tools.

Scratch acceptance uses the committed baseline plus this unit. It runs the
unmodified closure checker and actual native host commands, excluding unrelated
untracked audio work. The current working-tree gate is a separate final command.
"""
import argparse,subprocess,sys
from closure_support import ROOT
from itinerary_build import OUT,NAMES
def run(*args):
    print('RUN '+' '.join(args),flush=True);subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fresh',action='store_true');p.add_argument('--working-tree-lint',action='store_true');a=p.parse_args()
    if a.fresh:
        import contacts_reference
        contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True,fresh=True);contacts_reference.expanded_image(local=True,fresh=True)
    run('verif/itinerary_shells.py');run('verif/itinerary_evidence.py','enumerate')
    for name in NAMES:run('verif/itinerary_evidence.py',name,'--timeout','300' if name=='WalkPassengerToExit' else '180')
    run('verif/itinerary_evidence.py','PlacePassengerOnPlatform','--negative','--timeout','30')
    run('verif/itinerary_mutants.py');run('verif/itinerary_integration.py','--whole','--local-reference');run('verif/itinerary_scenario.py')
    run('verif/itinerary_certificate.py','--draft');run('verif/itinerary_host.py');run('verif/itinerary_certificate.py')
    if a.working_tree_lint:run('tools/closure.py')
if __name__=='__main__':main()
