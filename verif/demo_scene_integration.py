"""Run maintained demo presentation/caller suites and all scenarios with audit."""
import argparse,ctypes as C,json,shutil,sys,time
from closure_support import ROOT,receipt,save
from demo_scene_build import OUT,build
import contacts_reference
contacts_reference.OUT=OUT/'reference'
from contacts_reference import prepare_reference
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--whole',action='store_true');p.add_argument('--local-reference',action='store_true');a=p.parse_args()
    plain=prepare_reference(local=a.local_reference)
    start=time.perf_counter();dll=nbuild.load_l1(build());machine=difftest.Machine();rows=[]
    audit=(C.c_uint32*20).in_dll(dll,'demo_scene_audit')
    for suite in ['demo_scripts','game_services','menu','actors','render','scene']:
        for poison in (False,True):
            for case in difftest.load_suite(suite).CASES:
                problems=difftest.run(case,machine,dll,poison)
                rows.append(dict(suite=suite,case=case.title,routine=case.routine,poison=poison,problems=problems))
                if problems:print(rows[-1],flush=True)
        selected=[r for r in rows if r['suite']==suite]
        print(f'{suite}: {sum(not r["problems"] for r in selected)}/{len(selected)}',flush=True)
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
        before=list(audit);previous=sys.argv;scenario_audits=[];status=0
        for path in sorted((ROOT/'tests/scenarios').glob('*.txt')):
            prior_counts=list(audit);sys.argv=['tools/wholegame.py',path.stem]
            try:one=wholegame.main()
            finally:sys.argv=previous
            scenario_audits.append(dict(scenario=path.stem,status=one,entries=[audit[i]-prior_counts[i] for i in range(10)],fallbacks=[audit[i]-prior_counts[i] for i in range(10,20)]));status|=one
        whole_audit=[audit[i]-before[i] for i in range(20)]
    result=receipt(['python','verif/demo_scene_integration.py',*(['--whole'] if a.whole else []),*(['--local-reference'] if a.local_reference else [])],
        [__file__,ROOT/'verif/demo_scene_build.py',ROOT/'verif/contacts_reference.py',plain,ROOT/'tools/wholegame.py',ROOT/'tools/difftest.py',
         *[ROOT/'tests'/f'{s}.py' for s in ['demo_scripts','game_services','menu','actors','render','scene']],*sorted((ROOT/'tests/scenarios').glob('*.txt'))],
        build=json.loads((OUT/'build.json').read_text()),cases=rows,routine_audit=routine_audit,
        whole_audit=whole_audit,whole_status=status,scenario_audits=scenario_audits if a.whole else [],seconds=time.perf_counter()-start)
    save(OUT/'integration.json',result)
    return int(any(r['problems'] for r in rows) or bool(status))

if __name__=='__main__':raise SystemExit(main())
