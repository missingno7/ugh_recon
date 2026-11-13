"""Recreate checked L0/oracle inputs only in this worker's scratch directory."""
import argparse
from closure_support import ROOT
import contacts_reference
contacts_reference.OUT=ROOT/'build/workers/close-demo/reference'
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fresh',action='store_true');a=p.parse_args()
    print(contacts_reference.prepare_reference(local=True,fresh=a.fresh))
    print(contacts_reference.expanded_image(local=True,fresh=a.fresh))
