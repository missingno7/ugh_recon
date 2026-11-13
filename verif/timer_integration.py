"""Existing maintained suites and wholegame.main against the selected L1 variant.

No edits to c/, tests/, or wholegame.py. References are copied read-only from
the ordinary gate cache; all report/reference writes belong to this worker.
"""
import argparse,ctypes as C,json,shutil,sys,time
from pathlib import Path
from closure_support import ROOT,receipt,save
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild
OUT=ROOT/'build/workers/close-timer'
from timer_build import build

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--whole',action='store_true')
    parser.add_argument('--suites',nargs='+',default=['timer','timer_stack','timer_system','timer_callbacks'])
    args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter();path=build()
    dll=nbuild.load_l1(path);machine=difftest.Machine();rows=[]
    audit=(C.c_uint32*8).in_dll(dll,"timer_audit")
    for suite in args.suites:
        module=__import__(suite) if suite=='timer_callbacks' else difftest.load_suite(suite)
        for poison in (False,True):
            for case in module.CASES:
                problems=difftest.run(case,machine,dll,poison)
                rows.append(dict(suite=suite,case=case.title,routine=case.routine,poison=poison,problems=problems))
                if problems:print(rows[-1],flush=True)
        selected=[r for r in rows if r['suite']==suite]
        print(f'{suite}: {sum(not r["problems"] for r in selected)}/{len(selected)}',flush=True)
    routine_counts=list(audit)
    routine_seconds=time.perf_counter()-start;whole_status=None
    if args.whole:
        import wholegame
        folder=OUT/'whole';folder.mkdir(exist_ok=True)
        for cached in (ROOT/'build/whole').glob('*.ref.json'):shutil.copyfile(cached,folder/cached.name)
        wholegame.OUT=folder
        # wholegame's prior edge-attribution ledger is an optional build-worker
        # artifact, not an oracle. Isolate that read too; a clean checkout starts
        # without prior attribution. Scenario checks and reference keys are intact.
        prior=ROOT/'build/workers/c-close/call-edges.json';ledger=folder/'prior-edges.json'
        if prior.exists():shutil.copyfile(prior,ledger)
        else:ledger.write_text('[]\n')
        class ReadRoot(type(ROOT)):
            def __truediv__(self,value):
                if str(value)=='build/workers/c-close/call-edges.json':return ledger
                return super().__truediv__(value)
        wholegame.ROOT=ReadRoot(ROOT)
        def variant(out=None,trace_dir=None):
            if trace_dir is not None:raise RuntimeError('variant trace instrumentation requires a separate build hook')
            # main owns and unloads this separate Windows LoadLibrary reference.
            return nbuild.load_l1(path)
        wholegame.load_dll=variant
        # Invoke the actual tool entry point with its full maintained scenario set.
        previous=sys.argv;sys.argv=['tools/wholegame.py']
        try:whole_status=wholegame.main()
        finally:sys.argv=previous
    inputs=[ROOT/'verif/timer_integration.py',ROOT/'tools/nbuild.py',ROOT/'tools/wholegame.py',
            ROOT/'tools/difftest.py',ROOT/'tools/emu.py',*sorted((ROOT/'native').rglob('*.[ch]')),
            *sorted((ROOT/'c').glob('*.[ch]')),*[ROOT/('verif' if s=='timer_callbacks' else 'tests')/f'{s}.py' for s in args.suites],
            *sorted((ROOT/'tests/scenarios').glob('*.txt'))]
    result=receipt(['python','verif/timer_integration.py',*(['--whole'] if args.whole else [])],inputs,
        dll=str(path),build_receipt=json.loads((OUT/'build.json').read_text()),
        cases=rows,audit_order=["register native","register L1 fallback","remove native","remove L1 fallback","set native","set L1 fallback","tick native","tick L1 fallback"],
        routine_counts=routine_counts,whole_counts=[audit[i]-routine_counts[i] for i in range(8)],
        routine_seconds=routine_seconds,whole_status=whole_status,seconds=time.perf_counter()-start)
    save(OUT/'integration.json',result)
    print('native/fallback audit:',result['routine_counts'],result['whole_counts'],flush=True)
    return int(any(r['problems'] for r in rows) or bool(whole_status))

if __name__=='__main__':raise SystemExit(main())
