"""Reproduce the stone evidence from maintained files and pinned tools.

All generated output is under build/workers/close-stones/. --fresh also forces
an independent local plain L0 build and locked oracle expansion/repack. No
maintained L0/L1/test/host source is generated or changed in the real checkout.
"""
import argparse,subprocess,sys
from closure_support import ROOT
from stones_build import OUT,NAMES
def run(*args):
    print('RUN '+' '.join(args),flush=True);subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fresh',action='store_true');a=p.parse_args()
    if a.fresh:
        import contacts_reference
        contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True,fresh=True);contacts_reference.expanded_image(local=True,fresh=True)
    run('verif/stones_evidence.py','enumerate')
    for name in NAMES:
        run('verif/stones_evidence.py',name,*(['--semantic'] if name in ['UpdateStonePickupWait','UpdateThrownStone'] else []),'--timeout','180')
    run('verif/stones_evidence.py','BeginStonePickupWait','--platforms','0','--negative','--timeout','30')
    run('verif/stones_sync.py');run('verif/stones_mutants.py')
    run('verif/stones_integration.py','--whole','--local-reference')
    run('verif/stones_certificate.py','--draft');run('verif/stones_host.py')
    run('verif/stones_certificate.py');run('tools/closure.py')
if __name__=='__main__':main()
