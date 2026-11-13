"""Actual fare MUL over two scalar words; no unrelated RAM in this lemma."""
import argparse,json
from pathlib import Path
from closure_support import ROOT,function
from delivery_build import OUT
from delivery_limits import cbmc,SMT
from delivery_pieces import pieces

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--timeout',type=int,default=120);a=p.parse_args()
    folder=OUT/'product-scalar';folder.mkdir(parents=True,exist_ok=True)
    core=ROOT/'native/passenger_delivery.c';l1=ROOT/'c/actors_states.c'
    body=pieces()['product'][1]
    code='''#include "ugh.h"
static uint16_t scale;
uint16_t scalar_read(uint16_t bank,uint16_t address) {
 __CPROVER_assert(bank==DATA_SEG && address==D(ScoreMultiplier),"only multiplier input read");return scale;
}
#define R(n,i) scalar_read(r->ds,(uint16_t)(D(n)+(i)))
'''+function(core.read_text(),'pd_fare_product')+'static void original(Regs *r) {\n'+body+'}\n'
    code+='''int main(void) {
 uint16_t fare,multiplier;scale=multiplier;Regs r,bridge;r.ds=DATA_SEG;r.ax=fare;bridge=r;
 uint32_t actual=pd_fare_product(fare,multiplier);original(&r);original(&bridge);
 __CPROVER_assert(actual==((uint32_t)r.ax|((uint32_t)r.dx<<16)),"actual C scalar product equals L1 MUL");
 __CPROVER_assert(r.ax==bridge.ax && r.bx==bridge.bx && r.cx==bridge.cx && r.dx==bridge.dx && r.si==bridge.si && r.di==bridge.di && r.bp==bridge.bp && r.sp==bridge.sp && r.cs==bridge.cs && r.ds==bridge.ds && r.es==bridge.es && r.ss==bridge.ss && r.ip==bridge.ip && r.flags==bridge.flags,"complete MUL machine shell outputs");
 return 0;}
'''
    source=folder/'harness.c';source.write_text(code)
    result=cbmc(source,folder,[Path(__file__),core,l1,ROOT/'verif/delivery_pieces.py',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=2,timeout=a.timeout,extra=SMT)
    print(json.dumps({k:result[k] for k in ['result','seconds','peak_private_bytes','failures']}),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
