"""Maintained contact/caller suites and all whole-game scenarios, bridged."""
import argparse,ctypes as C,json,shutil,sys,time
from closure_support import ROOT,receipt,save
from contacts_build import OUT,build
from contacts_reference import prepare_reference
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--whole',action='store_true');p.add_argument('--local-reference',action='store_true');a=p.parse_args()
    plain=prepare_reference(local=a.local_reference)
    start=time.perf_counter();dll=nbuild.load_l1(build());machine=difftest.Machine();rows=[]
    audit=(C.c_uint32*5).in_dll(dll,'contacts_audit')
    for suite in ['actors','actors_states','items_water','render']:
        for poison in (False,True):
            for case in difftest.load_suite(suite).CASES:
                problems=difftest.run(case,machine,dll,poison)
                rows.append(dict(suite=suite,case=case.title,routine=case.routine,poison=poison,problems=problems))
                if problems:print(rows[-1],flush=True)
        selected=[r for r in rows if r['suite']==suite]
        print(f'{suite}: {sum(not r["problems"] for r in selected)}/{len(selected)}',flush=True)
    routine_audit=list(audit);status=None
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
        # main unloads its received library; give it a separate loader reference.
        def variant(out=None,trace_dir=None):
            if trace_dir is not None:raise RuntimeError('variant failure tracing needs instrumentation')
            return nbuild.load_l1(dll._name)
        wholegame.load_dll=variant
        before=list(audit);previous=sys.argv;sys.argv=['tools/wholegame.py']
        try:status=wholegame.main()
        finally:sys.argv=previous
        whole_audit=[audit[i]-before[i] for i in range(5)]
    else:whole_audit=None
    result=receipt(['python','verif/contacts_integration.py',*(['--whole'] if a.whole else []),*(['--local-reference'] if a.local_reference else [])],
        [__file__,ROOT/'verif/contacts_build.py',ROOT/'verif/contacts_reference.py',plain,ROOT/'tools/wholegame.py',ROOT/'tools/difftest.py',
         *[ROOT/'tests'/f'{s}.py' for s in ['actors','actors_states','items_water','render']],
         *sorted((ROOT/'tests/scenarios').glob('*.txt'))],
        build=json.loads((OUT/'build.json').read_text()),cases=rows,routine_audit=routine_audit,
        whole_audit=whole_audit,whole_status=status,seconds=time.perf_counter()-start)
    save(OUT/'integration.json',result)
    return int(any(r['problems'] for r in rows) or bool(status))

if __name__=='__main__':raise SystemExit(main())
