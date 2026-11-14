"""Composed sequencing suites, full-RAM L0 comparison and frame audits."""
import argparse,ctypes as C,json,shutil,sys,time
from closure_support import ROOT,receipt,save
from sequencing_build import OUT,build
import contacts_reference
contacts_reference.OUT=OUT/'reference'
from contacts_reference import prepare_reference
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--whole',action='store_true');p.add_argument('--local-reference',action='store_true');a=p.parse_args()
    plain=prepare_reference(local=a.local_reference)
    start=time.perf_counter();dll=nbuild.load_l1(build());machine=difftest.Machine();rows=[]
    entry_names=json.loads((OUT/'build.json').read_text())['entries'];nentries=len(entry_names)
    audit=(C.c_uint32*16).in_dll(dll,'sequencing_audit')
    frame_audit=(C.c_uint32*4).in_dll(dll,'session_frame_audit')
    actor_audit=(C.c_uint32*12).in_dll(dll,'sequence_actor_audit')
    for suite in ['actors_states','items_water','render','render_primitives','scene','menu','demo_scripts','video']:
        for poison in (False,True):
            for case in difftest.load_suite(suite).CASES:
                save(OUT/'progress.json',dict(suite=suite,case=case.title,poison=poison))
                problems=difftest.run(case,machine,dll,poison)
                rows.append(dict(suite=suite,case=case.title,routine=case.routine,poison=poison,problems=problems))
                if problems:print(rows[-1],flush=True)
        selected=[r for r in rows if r['suite']==suite]
        print(f'{suite}: {sum(not r["problems"] for r in selected)}/{len(selected)}',flush=True)
    from water_weather_l0_cases import cases
    for poison in (False,True):
        for case in cases():
            problems=difftest.run(case,machine,dll,poison);rows.append(dict(suite='inherited_vga_modes',case=case.title,routine=case.routine,poison=poison,problems=problems))
            if problems:print(rows[-1],flush=True)
    selected=[r for r in rows if r['suite']=='inherited_vga_modes'];print(f'weather_vga_modes: {sum(not r["problems"] for r in selected)}/{len(selected)}',flush=True)
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
            prior_counts=list(audit);prior_frames=list(frame_audit);prior_actors=list(actor_audit);sys.argv=['tools/wholegame.py',path.stem]
            try:one=wholegame.main()
            finally:sys.argv=previous
            scenario_audits.append(dict(scenario=path.stem,status=one,entries=[audit[i]-prior_counts[i] for i in range(nentries)],fallbacks=[audit[i]-prior_counts[i] for i in range(8,8+nentries)],frames=[frame_audit[i]-prior_frames[i] for i in range(4)],actor_operations=[actor_audit[i]-prior_actors[i] for i in range(12)]));status|=one
        rain_scenarios=OUT/'rain-scenarios';rain_scenarios.mkdir(exist_ok=True)
        shutil.copyfile(ROOT/'verif/random_rain.txt',rain_scenarios/'random-rain.txt')
        class RainRoot(ReadRoot):
            def __truediv__(self,value):
                if str(value)=='tests/scenarios':return rain_scenarios
                return super().__truediv__(value)
        wholegame.ROOT=RainRoot(ROOT);wholegame.OUT=OUT/'rain';wholegame.OUT.mkdir(exist_ok=True)
        prior_counts=list(audit);prior_frames=list(frame_audit);prior_actors=list(actor_audit);sys.argv=['tools/wholegame.py']
        try:one=wholegame.main()
        finally:sys.argv=previous
        scenario_audits.append(dict(scenario='random-rain',status=one,entries=[audit[i]-prior_counts[i] for i in range(nentries)],fallbacks=[audit[i]-prior_counts[i] for i in range(8,8+nentries)],frames=[frame_audit[i]-prior_frames[i] for i in range(4)],actor_operations=[actor_audit[i]-prior_actors[i] for i in range(12)]));status|=one
        whole_audit=[audit[i]-before[i] for i in range(16)]
    result=receipt(['python','verif/sequencing_integration.py',*(['--whole'] if a.whole else []),*(['--local-reference'] if a.local_reference else [])],
        [__file__,ROOT/'verif/sequencing_build.py',ROOT/'verif/water_weather_l0_cases.py',ROOT/'verif/random_rain.txt',ROOT/'verif/contacts_reference.py',plain,ROOT/'tools/wholegame.py',ROOT/'tools/difftest.py',
         *[ROOT/'tests'/f'{s}.py' for s in ['actors_states','items_water','render','render_primitives','scene','menu','demo_scripts','video']],*sorted((ROOT/'tests/scenarios').glob('*.txt'))],
        build=json.loads((OUT/'build.json').read_text()),cases=rows,routine_audit=routine_audit,
        whole_audit=whole_audit,whole_status=status,scenario_audits=scenario_audits if a.whole else [],seconds=time.perf_counter()-start)
    save(OUT/'integration.json',result)
    return int(any(r['problems'] for r in rows) or bool(status))

if __name__=='__main__':raise SystemExit(main())
