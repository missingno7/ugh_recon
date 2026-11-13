"""RNG bridge versus L0 suites and all 14 maintained whole-game scenarios.

All builds, reports and uncached references stay under this worker directory.
"""
import argparse,ctypes as C,json,shutil,sys,time
from pathlib import Path
from closure_support import ROOT,receipt,save
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'tests'))
import difftest,nbuild
from random_build import build
from random_evidence import OUT
from random_reference import prepare_reference

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--whole',action='store_true')
    p.add_argument('--local-reference',action='store_true');p.add_argument('--fresh',action='store_true')
    p.add_argument('--rain-only',action='store_true',help='only the additional shipped rainy-level frame scenario')
    p.add_argument('--uncached',action='store_true',help='regenerate oracle frame references in this worker')
    a=p.parse_args();start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    reference=prepare_reference(local=a.local_reference,fresh=a.fresh)
    path=build();dll=nbuild.load_l1(path);machine=difftest.Machine()
    audit=(C.c_uint32*2).in_dll(dll,'random_audit');rows=[]
    for suite in ([] if a.rain_only else ['dos_input','render','items_water','random_cases']):
        module=__import__(suite) if suite=='random_cases' else difftest.load_suite(suite)
        for poison in (False,True):
            for case in module.CASES:
                problems=difftest.run(case,machine,dll,poison)
                rows.append(dict(suite=suite,case=case.title,poison=poison,problems=problems))
                if problems:print(rows[-1],flush=True)
        selected=[r for r in rows if r['suite']==suite]
        print(f'{suite}: {sum(not r["problems"] for r in selected)}/{len(selected)}',flush=True)
    routine_counts=list(audit);whole_status=None;scenario_counts={};rain_status=None
    if a.whole or a.rain_only:
        import wholegame
        folder=OUT/'whole';folder.mkdir(exist_ok=True)
        if not a.uncached:
            for cached in (ROOT/'build/whole').glob('*.ref.json'):shutil.copyfile(cached,folder/cached.name)
        wholegame.OUT=folder
        ledger=folder/'prior-edges.json';prior=ROOT/'build/workers/c-close/call-edges.json'
        if prior.exists():shutil.copyfile(prior,ledger)
        else:ledger.write_text('[]\n')
        class ReadRoot(type(ROOT)):
            def __truediv__(self,value):
                if str(value)=='build/workers/c-close/call-edges.json':return ledger
                if str(value)=='build/link/plain/UGH.EXE':return reference
                return super().__truediv__(value)
        wholegame.ROOT=ReadRoot(ROOT)
        def variant(out=None,trace_dir=None):
            if trace_dir is not None:raise RuntimeError('variant tracing requires a separate build hook')
            return nbuild.load_l1(path) # wholegame owns this separate loader reference
        wholegame.load_dll=variant
        original_native=wholegame.native
        def measured(s,*args,**kwargs):
            before=list(audit);result=original_native(s,*args,**kwargs)
            scenario_counts[s['name']]=[audit[i]-before[i] for i in range(2)]
            return result
        wholegame.native=measured
        previous=sys.argv;sys.argv=['tools/wholegame.py',*(['--refresh'] if a.uncached else [])]
        try:
            if not a.rain_only:whole_status=wholegame.main()
            rain=OUT/'rain';rain.mkdir(exist_ok=True)
            scenarios=OUT/'rain-scenarios';scenarios.mkdir(exist_ok=True)
            shutil.copyfile(ROOT/'verif/random_rain.txt',scenarios/'random-rain.txt')
            class RainRoot(ReadRoot):
                def __truediv__(self,value):
                    if str(value)=='tests/scenarios':return scenarios
                    return super().__truediv__(value)
            wholegame.ROOT=RainRoot(ROOT);wholegame.OUT=rain
            rain_status=wholegame.main()
        finally:sys.argv=previous
        assert scenario_counts.get('random-rain',[0])[0]>0,'rain scenario must enter the native RNG'
    result=receipt(['python','verif/random_integration.py',*sys.argv[1:]],
        [ROOT/'verif/random_integration.py',ROOT/'verif/random_build.py',ROOT/'verif/random_reference.py',
         ROOT/'verif/random_cases.py',ROOT/'verif/random_rain.txt',ROOT/'tools/wholegame.py',ROOT/'tools/difftest.py',ROOT/'tools/emu.py',
         *sorted((ROOT/'c').glob('*.[ch]')),*[ROOT/f'tests/{s}.py' for s in ['dos_input','render','items_water']],
         *sorted((ROOT/'tests/scenarios').glob('*.txt'))],
        result='PASS' if not any(r['problems'] for r in rows) and not whole_status and not rain_status else 'FAIL',
        cases=rows,audit_order=['next','seed'],routine_counts=routine_counts,scenario_counts=scenario_counts,
        whole_status=whole_status,rain_status=rain_status,seconds=time.perf_counter()-start,build=json.loads((OUT/'build.json').read_text()))
    save(OUT/('rain-integration.json' if a.rain_only else 'integration.json'),result)
    print('Bridge audits:',routine_counts,scenario_counts,flush=True)
    return int(result['result']!='PASS')

if __name__=='__main__':raise SystemExit(main())
