"""Run all audio suites and the maintained whole-game scenarios, with audits."""
import argparse,ctypes as C,json,shutil,sys,time
from closure_support import ROOT,receipt,save
from adlx_main_build import OUT,build
import contacts_reference
contacts_reference.OUT=OUT/'reference'
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--whole',action='store_true');p.add_argument('--local-reference',action='store_true');a=p.parse_args()
    plain=contacts_reference.prepare_reference(local=a.local_reference)
    start=time.perf_counter();path=build();dll=nbuild.load_l1(path);machine=difftest.Machine();rows=[]
    audit=(C.c_uint32*32).in_dll(dll,'adlx_main_audit')
    suites=['adlib','sound_engine','sound_api','music_analysis','music_clock']
    for suite in suites:
        for poison in (False,True):
            for case in difftest.load_suite(suite).CASES:
                problems=difftest.run(case,machine,dll,poison)
                rows.append(dict(suite=suite,title=case.title,routine=case.routine,poison=poison,problems=problems))
                if problems:print(rows[-1],flush=True)
        selected=[r for r in rows if r['suite']==suite]
        print(f'{suite}: {sum(not r["problems"] for r in selected)}/{len(selected)}',flush=True)
    routine_counts=list(audit);status=None
    if a.whole:
        import wholegame
        folder=OUT/'whole';folder.mkdir(exist_ok=True)
        for cached in (ROOT/'build/whole').glob('*.ref.json'):shutil.copyfile(cached,folder/cached.name)
        wholegame.OUT=folder
        ledger=folder/'prior-edges.json';ledger.write_text('[]\n')
        class ReadRoot(type(ROOT)):
            def __truediv__(self,value):
                if str(value)=='build/workers/c-close/call-edges.json':return ledger
                if str(value)=='build/link/plain/UGH.EXE':return plain
                return super().__truediv__(value)
        wholegame.ROOT=ReadRoot(ROOT)
        def variant(out=None,trace_dir=None):
            if trace_dir is not None:raise RuntimeError('separate instrumented build required for divergence tracing')
            return nbuild.load_l1(path)
        wholegame.load_dll=variant
        previous=sys.argv;sys.argv=['tools/wholegame.py']
        try:status=wholegame.main()
        finally:sys.argv=previous
    save(OUT/'integration.json',receipt(['python','verif/adlx_main_integration.py',*sys.argv[1:]],
        [__file__,ROOT/'verif/adlx_main_build.py',ROOT/'verif/contacts_reference.py',plain,ROOT/'tools/wholegame.py',ROOT/'tools/difftest.py',
         *[ROOT/'tests'/f'{s}.py' for s in suites],*sorted((ROOT/'tests/scenarios').glob('*.txt'))],
        cases=rows,routine_counts=routine_counts,whole_counts=[audit[i]-routine_counts[i] for i in range(32)],
        whole_status=status,seconds=time.perf_counter()-start))
    print('audit native steps/fallback instrument/fallback table:',list(audit)[16:19],flush=True)
    return int(any(r['problems'] for r in rows) or bool(status))
if __name__=='__main__':raise SystemExit(main())
