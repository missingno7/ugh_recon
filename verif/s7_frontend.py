"""Compare typed native front-end operations with independent whole-game records."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
import nativebuild,s7_frontend_record
from cbuild import GCC
from job_pool import run,save

def verify(out,build=True):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True);prod=out/'production'
    if build:nativebuild.build('test',prod)
    manifest=json.loads((ROOT/'metadata/native-manifest.json').read_text());sources=manifest['core']+manifest['backends']['test']
    objects=[prod/('object-%02d.o'%i) for i,s in enumerate(sources) if s!='port/test/main.c']
    checks=out/'cases';checks.mkdir(exist_ok=True);obj=checks/'cases.o';exe=checks/'cases.exe'
    run([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I',ROOT,'-I',ROOT/'port','-I',prod,'-c',ROOT/'verif/s7_frontend_cases.c','-o',obj],ROOT,checks,'compile')
    run([GCC,*objects,obj,'-o',exe],ROOT,checks,'link')
    print(run([exe,prod/'ugh.res'],ROOT,checks,'run')['stdout'].strip(),flush=True)
    results={}
    for scenario in ['high-score','password']:
        folder=out/scenario;folder.mkdir(exist_ok=True);source=s7_frontend_record.generate(folder,scenario)
        obj=folder/'record.o';exe=folder/'record.exe'
        run([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I',ROOT,'-I',ROOT/'port','-I',prod,'-c',source,'-o',obj],ROOT,folder,'compile')
        run([GCC,*objects,obj,'-o',exe],ROOT,folder,'link')
        row=run([exe,prod/'ugh.res',folder/'baseline.bin',folder],ROOT,folder,'record')
        actual=[json.loads(line) for line in row['stdout'].splitlines()]
        # Expected records are opened only after the process has exited.
        expected=json.loads((ROOT/'build/whole'/f'{scenario}.ref.json').read_text())['frames']
        differences=[]
        for i,(got,want) in enumerate(zip(actual,expected)):
            for field in sorted(set(got)|set(want)):
                if got.get(field)!=want.get(field):differences.append(dict(frame=i,field=field,actual=got.get(field),expected=want.get(field)))
        if len(actual)!=len(expected):differences.append(dict(field='record_count',actual=len(actual),expected=len(expected)))
        save(folder/'actual.json',dict(frames=actual));save(folder/'differences.json',differences)
        controls=[]
        for name,define,field in [('missed-owner','S7_FRONT_MISS_FIELD','ram'),('missed-queue','S7_FRONT_MISS_QUEUE','log')]:
            bad=folder/name;bad.mkdir(exist_ok=True);badobj=bad/'record.o';badexe=bad/'record.exe'
            run([GCC,'-O2','-std=c11','-D'+define,'-I',ROOT,'-I',ROOT/'port','-I',prod,'-c',source,'-o',badobj],ROOT,bad,'compile')
            run([GCC,*objects,badobj,'-o',badexe],ROOT,bad,'link')
            badrow=run([badexe,prod/'ugh.res',folder/'baseline.bin',bad],ROOT,bad,'run')
            badrecords=[json.loads(line) for line in badrow['stdout'].splitlines()]
            caught=[i for i,(got,want) in enumerate(zip(badrecords,expected)) if got[field]!=want[field]]
            assert caught,name+' escaped comparator'
            controls.append(dict(defect=name,field=field,detected_frames=caught))
        results[scenario]=dict(records=len(actual),expected=len(expected),differences=differences,controls=controls)
        print(scenario,len(actual),'records',[(d.get('frame'),d['field']) for d in differences],flush=True)
    save(out/'receipt.json',dict(result='FAIL' if any(r['differences'] for r in results.values()) else 'PASS',scenarios=results))
    return not any(r['differences'] for r in results.values())
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=ROOT/'build/workers/s7-frontend');p.add_argument('--no-build',action='store_true');a=p.parse_args();raise SystemExit(0 if verify(a.out,not a.no_build) else 1)

