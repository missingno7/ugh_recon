"""Check that finite actual-C evidence detects retained-semantic regressions."""
import subprocess,json
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save
from timer_evidence import pair,OUT

def main():
    raw=(ROOT/'native/timer.c').read_text();rows=[]
    mutants=[('callback_stride','timer_put_fragment(state,destination,timer_fragment(state,tail));',
              'timer_put_fragment(state,destination*2,timer_fragment(state,tail*2));'),
             ('countdown_sign','(slot->remaining&2147483648u)','(0u)'),
             ('setter_reset','state->slots[timer_handle_slot(state,handle)].interval=interval;',
              'state->slots[timer_handle_slot(state,handle)].interval=interval; state->slots[timer_handle_slot(state,handle)].remaining=interval;'),
             ('stale_due','/* Due is intentionally stale across reuse. */',
              'slot->due=0;')]
    for name,old,new in mutants:
        folder=OUT/'mutants'/name;inputs=pair(folder)
        assert raw.count(old)==1
        source=folder/'timer.c';source.write_text(raw.replace(old,new))
        p=folder/'pair.inc';p.write_text(p.read_text().replace((ROOT/'native/timer.c').as_posix(),source.as_posix()))
        harness=folder/'enumeration.c'
        harness.write_text('#include <stdio.h>\n#include <stdlib.h>\n#define CHECK(c,m) do { if(!(c)) { puts(m);exit(23); } } while(0)\n#include "pair.inc"\n#include "'+(ROOT/'verif/timer_enumeration.c').as_posix()+'"\n')
        exe=folder/'enumeration.exe';build=compile_c([harness],exe,[ROOT/'native',ROOT/'c'])
        run=subprocess.run([str(exe)],capture_output=True,text=True)
        if run.returncode!=23:raise RuntimeError(f'{name} escaped: {run.returncode}')
        rows.append(receipt(build['command'],[*inputs,ROOT/'verif/timer_enumeration.c',source,Path(__file__)],
                            name=name,detected=True,returncode=run.returncode,diagnostic=run.stdout.strip()))
    save(OUT/'mutants/result.json',rows)
    print(json.dumps([dict(name=r['name'],diagnostic=r['diagnostic']) for r in rows]))

if __name__=='__main__':main()
