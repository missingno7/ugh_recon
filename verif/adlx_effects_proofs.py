"""Accepted effects proof profiles; old exploratory destinations are unused."""
import argparse,sys
from adlx_effects_build import OUT
import adlx_effects_word as word

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--op',type=int,choices=[0,1,2,3,4,5,7,8]);p.add_argument('--ops',type=int,nargs='+',choices=[0,1,2,3,4,5,7,8]);p.add_argument('--timeout',type=int,default=180);p.add_argument('--negative',action='store_true');a=p.parse_args()
    word.OUT=OUT/'accepted-step'
    for op in a.ops or ([0,1,2,3,4,5,7,8] if a.op is None else [a.op]):
        sys.argv=['adlx_effects_word.py','--op',str(op),'--record','8','--contracts','--timeout',str(a.timeout),*(['--negative'] if a.negative else [])]
        word.main()
if __name__=='__main__':main()
