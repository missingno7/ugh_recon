"""Reuse the maintained tests against the bridge DLL, without modifying tools/tests."""
import importlib.util,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild

def main():
    start=time.perf_counter()
    dll=nbuild.load_l1(nbuild.build('bridge'))
    m=difftest.Machine(); rows=[]
    for poison in (False,True):
        for case in difftest.load_suite('ice').CASES:
            problems=difftest.run(case,m,dll,poison)
            rows.append(dict(case=case.title,poison=poison,problems=problems))
            if problems: print(rows[-1],flush=True)
    print(f'ICE bridge: {sum(not r["problems"] for r in rows)}/{len(rows)}',flush=True)
    spec=importlib.util.spec_from_file_location('whole_program',ROOT/'tests/_whole_program.py')
    whole=importlib.util.module_from_spec(spec);spec.loader.exec_module(whole)
    whole.load_dll=lambda:dll
    # Redirect only this runner's result write; the shared test is untouched.
    class LocalPath:
        def __new__(cls,value):
            return ROOT/'build/workers/pilot-ice/whole-program.json'
    whole.Path=LocalPath
    status=whole.main()
    result=dict(cases=rows,whole_status=status,seconds=time.perf_counter()-start)
    (ROOT/'build/workers/pilot-ice/integration.json').write_text(json.dumps(result,indent=2)+'\n')
    return int(bool(status or any(r['problems'] for r in rows)))
if __name__=='__main__': raise SystemExit(main())
