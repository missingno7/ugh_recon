"""Frame-by-frame production demo composition against independent references."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
import nativebuild,s7_demo_record
from cbuild import GCC
from job_pool import run,save

def verify(out,build=True,controls=True,smoke=True):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True);prod=out/'production'
    if build:nativebuild.build('test',prod)
    manifest=json.loads((ROOT/'metadata/native-manifest.json').read_text());sources=manifest['core']+manifest['backends']['test']
    objects=[prod/('object-%02d.o'%i) for i,s in enumerate(sources) if s!='port/test/main.c']
    cases=out/'cases';cases.mkdir(exist_ok=True);obj=cases/'cases.o';exe=cases/'cases.exe'
    run([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I',ROOT,'-I',ROOT/'port','-I',prod,'-c',ROOT/'verif/s7_demo_cases.c','-o',obj],ROOT,cases,'compile')
    run([GCC,*objects,obj,'-o',exe],ROOT,cases,'link')
    print(run([exe,prod/'ugh.res'],ROOT,cases,'run')['stdout'].strip(),flush=True)
    results={}
    for scenario in list(s7_demo_record.KINDS)+(['smoke'] if smoke else []):
        folder=out/scenario;folder.mkdir(exist_ok=True);source=s7_demo_record.generate(folder,'attract' if scenario=='smoke' else scenario,256 if scenario=='smoke' else None)
        def record(where,define=None):
            where.mkdir(exist_ok=True);obj=where/'record.o';exe=where/'record.exe'
            flags=['-D'+define] if define else []
            run([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',*flags,'-I',ROOT,'-I',ROOT/'port','-I',prod,'-c',source,'-o',obj],ROOT,where,'compile')
            run([GCC,*objects,obj,'-o',exe],ROOT,where,'link')
            row=run([exe,prod/'ugh.res',folder/'baseline.bin',where],ROOT,where,'record')
            return [json.loads(line) for line in row['stdout'].splitlines()]
        actual=record(folder)
        # Expected records are opened only after the native process exits.
        if scenario=='smoke':
            run([sys.executable,ROOT/'verif/s7_demo_diagnose.py','--smoke-worker',out/'literal'],ROOT,out,'smoke-reference')
            expected=json.loads((out/'literal/smoke/reference.json').read_text())['frames']
        else:expected=json.loads((ROOT/'build/whole'/f'{scenario}.ref.json').read_text())['frames']
        differences=[]
        for i,(got,want) in enumerate(zip(actual,expected)):
            for field in sorted(set(got)|set(want)):
                if got.get(field)!=want.get(field):differences.append(dict(frame=i,field=field,actual=got.get(field),expected=want.get(field)))
        if len(actual)!=len(expected):differences.append(dict(field='record_count',actual=len(actual),expected=len(expected)))
        save(folder/'actual.json',dict(frames=actual));save(folder/'differences.json',differences)
        checks=[]
        if controls:
            for name,define in [('missed-actor','S7_DEMO_MISS_ACTOR')]+([('missed-width','S7_DEMO_MISS_WIDTH')] if scenario=='reveal' else []):
                bad=record(folder/name,define);caught=[i for i,(g,e) in enumerate(zip(bad,expected)) if g['ram']!=e['ram']]
                assert caught,name+' escaped comparison';checks.append(dict(defect=name,detected_frames=caught))
        results[scenario]=dict(records=len(actual),expected=len(expected),differences=differences,controls=checks,audio_boundary=None)
        print(scenario,len(actual),'records',[(d.get('frame'),d['field']) for d in differences][:12],flush=True)
    save(out/'receipt.json',dict(result='FAIL' if any(r['differences'] for r in results.values()) else 'PASS',scenarios=results))
    return not any(r['differences'] for r in results.values())
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=ROOT/'build/workers/s7-demo');p.add_argument('--no-build',action='store_true');p.add_argument('--no-controls',action='store_true');p.add_argument('--no-smoke',action='store_true');a=p.parse_args();raise SystemExit(0 if verify(a.out,not a.no_build,not a.no_controls,not a.no_smoke) else 1)
