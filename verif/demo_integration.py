"""Run maintained demo/scene suites and all whole-game scenarios."""
import argparse,ctypes as C,json,shutil,sys,time
from closure_support import ROOT,receipt,save
from demo_build import OUT,build
import contacts_reference
contacts_reference.OUT=OUT/'reference'
from contacts_reference import prepare_reference
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--whole',action='store_true');p.add_argument('--local-reference',action='store_true');a=p.parse_args()
    plain=prepare_reference(local=a.local_reference);start=time.perf_counter()
    dll=nbuild.load_l1(build());machine=difftest.Machine();rows=[];audit=(C.c_uint32*6).in_dll(dll,'demo_audit')
    for suite in ['demo_scripts','scene','game_services']:
        for poison in (False,True):
            for case in difftest.load_suite(suite).CASES:
                problems=difftest.run(case,machine,dll,poison)
                rows.append(dict(suite=suite,case=case.title,poison=poison,problems=problems))
                if problems:print(rows[-1],flush=True)
        selected=[r for r in rows if r['suite']==suite]
        print(suite,sum(not r['problems'] for r in selected),'/',len(selected),flush=True)
    routine=list(audit);status=None;whole=None
    if a.whole:
        import wholegame
        folder=OUT/'whole';folder.mkdir(exist_ok=True)
        for cached in (ROOT/'build/whole').glob('*.ref.json'):shutil.copyfile(cached,folder/cached.name)
        wholegame.OUT=folder;ledger=folder/'prior-edges.json'
        prior=ROOT/'build/workers/c-close/call-edges.json'
        if prior.exists():shutil.copyfile(prior,ledger)
        else:ledger.write_text('[]\n')
        class ReadRoot(type(ROOT)):
            def __truediv__(self,value):
                if str(value)=='build/workers/c-close/call-edges.json':return ledger
                if str(value)=='build/link/plain/UGH.EXE':return plain
                return super().__truediv__(value)
        wholegame.ROOT=ReadRoot(ROOT)
        def variant(out=None,trace_dir=None):
            if trace_dir is not None:raise RuntimeError('variant failure tracing requires instrumented build')
            return nbuild.load_l1(dll._name)
        wholegame.load_dll=variant;before=list(audit);previous=sys.argv;sys.argv=['tools/wholegame.py']
        try:status=wholegame.main()
        finally:sys.argv=previous
        whole=[audit[i]-before[i] for i in range(6)]
    save(OUT/'integration.json',receipt(['python','verif/demo_integration.py',*(['--whole'] if a.whole else [])],
        [__file__,ROOT/'verif/demo_build.py',ROOT/'verif/contacts_reference.py',plain,ROOT/'tools/wholegame.py',ROOT/'tools/difftest.py',
         *[ROOT/'tests'/f'{s}.py' for s in ['demo_scripts','scene','game_services']],*sorted((ROOT/'tests/scenarios').glob('*.txt'))],
        build=json.loads((OUT/'build.json').read_text()),result='PASS' if not any(r['problems'] for r in rows) and not status else 'FAIL',
        cases=rows,routine_audit=routine,whole_audit=whole,whole_status=status,seconds=time.perf_counter()-start))
    return int(any(r['problems'] for r in rows) or bool(status))
if __name__=='__main__':raise SystemExit(main())
