"""Reproduce the bounded hazard evidence and integration from maintained files.

The standard CBMC domain uses one stone. This does not claim the timed-out
sixteen-stone composition. The final repository-wide lint remains a real gate.
"""
import argparse,subprocess,sys
from closure_support import ROOT
from hazards_build import ENTRIES

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-proofs',action='store_true',help='rerun C/D and finite evidence only')
    args=parser.parse_args()
    commands=[['verif/hazards_inventory.py'],['verif/hazards_evidence.py','generated'],['verif/hazards_mutants.py']]
    if not args.skip_proofs:
        commands += [['verif/hazards_evidence.py',name,'--timeout','300' if name=='UpdateTriopterusCharge' else '60'] for name in ENTRIES]
        commands += [['verif/hazards_evidence.py','dispatcher','--timeout','30'],['verif/hazards_evidence.py','dispatcher','--negative','--timeout','30']]
    commands += [['verif/hazards_integration.py','--whole','--local-reference'],['verif/hazards_scenario.py'],['verif/hazards_host.py'],['tools/closure.py']]
    for command in commands:
        print('python '+' '.join(command),flush=True)
        run=subprocess.run([sys.executable,*command],cwd=ROOT)
        if run.returncode:return run.returncode
    return 0
if __name__=='__main__':raise SystemExit(main())
