"""Reproduce audio closure without maintained build products or source writes."""
import argparse,subprocess,sys
from closure_support import ROOT
from adlx_main_build import OUT

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--skip-proofs',action='store_true');p.add_argument('--fresh-reference',action='store_true');a=p.parse_args()
    if a.fresh_reference:
        import contacts_reference
        contacts_reference.OUT=OUT/'reference'
        contacts_reference.prepare_reference(local=True,fresh=True)
        contacts_reference.expanded_image(local=True,fresh=True)
    commands=[['verif/adlx_main_evidence.py','samples'],['verif/adlx_main_corpus.py'],['verif/adlx_main_corpus.py','--effects']]
    if not a.skip_proofs:
        commands += [['verif/adlx_main_evidence.py','prove','--op',str(op),'--timeout','90'] for op in [0,1,2,5,6,7,8]]
        commands += [['verif/adlx_main_evidence.py','prove','--op',str(op),'--channels','--timeout','90'] for op in [3,4]]
        commands += [['verif/adlx_main_evidence.py','prove','--op','2','--negative','--timeout','90']]
    commands += [['verif/adlx_main_integration.py','--whole','--local-reference'],['verif/adlx_main_scenario.py'],['verif/adlx_main_host.py'],['tools/closure.py']]
    for command in commands:
        print('RUN python '+' '.join(command),flush=True)
        subprocess.run([sys.executable,*command],cwd=ROOT,check=True)
if __name__=='__main__':main()
