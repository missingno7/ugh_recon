"""Run maintained stone/caller suites and all seventeen scenarios with audit."""
import argparse,ctypes as C,json,shutil,sys,time
from closure_support import ROOT,receipt,save
from stones_build import OUT,build
import contacts_reference
contacts_reference.OUT=OUT/'reference'
from contacts_reference import prepare_reference
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--whole',action='store_true');p.add_argument('--local-reference',action='store_true');a=p.parse_args()
    plain=prepare_reference(local=a.local_reference)
    start=time.perf_counter();dll=nbuild.load_l1(build());machine=difftest.Machine();rows=[]
    audit=(C.c_uint32*12).in_dll(dll,'stones_audit')
    for suite in ['items_water','actors_states','actors','render','scene']:
        for poison in (False,True):
            for case in difftest.load_suite(suite).CASES:
                problems=difftest.run(case,machine,dll,poison)
                rows.append(dict(suite=suite,case=case.title,routine=case.routine,poison=poison,problems=problems))
                if problems:print(rows[-1],flush=True)
        selected=[r for r in rows if r['suite']==suite]
        print(f'{suite}: {sum(not r["problems"] for r in selected)}/{len(selected)}',flush=True)
    machine.reset();C.memmove(dll.ugh_memory().contents,bytes(machine.uc.mem_read(0,difftest.MEM_SIZE)),difftest.MEM_SIZE)
    dll.ugh_devices_reset();cross=dll.stones_cross_mode();assert cross==1,cross
    print('cross-mode demo history: PASS',flush=True)
    routine_audit=list(audit);status=None;whole_audit=None
    if a.whole:
        import wholegame
        folder=OUT/'whole';folder.mkdir(exist_ok=True)
        for cached in (ROOT/'build/whole').glob('*.ref.json'):shutil.copyfile(cached,folder/cached.name)
        wholegame.OUT=folder
        prior=ROOT/'build/workers/c-close/call-edges.json';ledger=folder/'prior-edges.json'
        if prior.exists():shutil.copyfile(prior,ledger)
        else:ledger.write_text('[]\n')
        class ReadRoot(type(ROOT)):
            def __truediv__(self,value):
                if str(value)=='build/workers/c-close/call-edges.json':return ledger
                if str(value)=='build/link/plain/UGH.EXE':return plain
                return super().__truediv__(value)
        wholegame.ROOT=ReadRoot(ROOT)
        def variant(out=None,trace_dir=None):
            if trace_dir is not None:raise RuntimeError('variant failure tracing requires an instrumented build')
            return nbuild.load_l1(dll._name)
        wholegame.load_dll=variant
        before=list(audit);previous=sys.argv;sys.argv=['tools/wholegame.py']
        try:status=wholegame.main()
        finally:sys.argv=previous
        whole_audit=[audit[i]-before[i] for i in range(12)]
    result=receipt(['python','verif/stones_integration.py',*(['--whole'] if a.whole else []),*(['--local-reference'] if a.local_reference else [])],
        [__file__,ROOT/'verif/stones_build.py',ROOT/'verif/contacts_reference.py',plain,ROOT/'tools/wholegame.py',ROOT/'tools/difftest.py',
         *[ROOT/'tests'/f'{s}.py' for s in ['items_water','actors_states','actors','render','scene']],*sorted((ROOT/'tests/scenarios').glob('*.txt'))],
        build=json.loads((OUT/'build.json').read_text()),cases=rows,routine_audit=routine_audit,
        whole_audit=whole_audit,whole_status=status,cross_mode=cross,seconds=time.perf_counter()-start)
    save(OUT/'integration.json',result)
    return int(any(r['problems'] for r in rows) or bool(status))

if __name__=='__main__':raise SystemExit(main())
