"""Replay accepted main proofs after the additive audio.h constants.

All output is redirected through supported Python module globals to this
worker; no old certificate lock is changed by this runner.
"""
import argparse,sys
from closure_support import ROOT
from adlx_effects_build import OUT
import adlx_main_evidence as main_evidence

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--timeout',type=int,default=120);a=p.parse_args()
    main_evidence.OUT=OUT/'main-compatibility'
    for op in [0,1,2,5,6,7,8,3,4]:
        sys.argv=['adlx_main_evidence.py','prove','--op',str(op),'--timeout',str(a.timeout),*(['--channels'] if op in (3,4) else [])]
        main_evidence.main()
if __name__=='__main__':main()
