"""Build, audit and independently compare the first production startup slice."""
from pathlib import Path
import argparse,json,os,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
import nativebuild,s7_core_record,respack
from job_pool import run,save
from cbuild import GCC

def verify(out):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    (out/'receipt.json').unlink(missing_ok=True)
    prod=out/'production';exe=nativebuild.build('test',prod)
    cases={}
    for name,args in [('absent',['--no-adlib']),('present',[])]:
        row=run([exe,'--pack',prod/'ugh.res','--replay',*args],ROOT,out,'boot-'+name)
        actual=json.loads(row['stdout']);assert actual['result']=='slice_end' and actual['frames']==6
        cases[name]=actual
    # Only the executable, pack and ordinary runtime DLLs are available in this
    # launch directory. Neither recorder nor executable/MZ fixtures are copied.
    isolated=out/'machine-free';isolated.mkdir(exist_ok=True)
    for source in [exe,prod/'ugh.res',*prod.glob('*.dll')]:shutil.copyfile(source,isolated/source.name)
    witness=run([isolated/exe.name,'--replay','--no-adlib'],isolated,out,'machine-free')
    assert json.loads(witness['stdout'])['result']=='slice_end'
    negative=run([sys.executable,ROOT/'tools/nativebuild.py','--negative-control','--out',out/'negative'],ROOT,out,'negative-include',allowed=(1,))
    assert 'banned include/source: c/ugh.h' in negative['stderr'],negative
    missing=run([exe,'--pack',out/'missing.res'],ROOT,out,'missing-pack',allowed=(2,))
    assert 'cannot open required file' in missing['stderr']
    corrupt=out/'corrupt.res';data=bytearray((prod/'ugh.res').read_bytes());data[-1]^=1;corrupt.write_bytes(data)
    rejected=run([exe,'--pack',corrupt],ROOT,out,'corrupt-pack',allowed=(2,))
    assert 'payload hash mismatch' in rejected['stderr']
    record=out/'record';record.mkdir(exist_ok=True)
    source=s7_core_record.generate(record)
    # Compile observer separately. The same already audited core objects are
    # reused byte for byte; only the production backend's main is replaced.
    observer=record/'recorder.o'
    run([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',
      '-I',ROOT,'-I',ROOT/'port','-I',prod,'-c',source,'-o',observer],ROOT,out,'recorder-compile')
    manifest=json.loads((ROOT/'metadata/native-manifest.json').read_text())
    sources=manifest['core']+manifest['backends']['test'];main=sources.index('port/test/main.c')
    objects=[prod/('object-%02d.o'%i) for i in range(len(sources)) if i!=main]
    rex=record/'record.exe';run([GCC,*objects,observer,'-o',rex],ROOT,out,'recorder-link')
    result=run([rex,prod/'ugh.res',record/'baseline.bin',record],ROOT,out,'record')
    actual=[json.loads(line) for line in result['stdout'].splitlines()]
    # Expected records are first opened here, after the native process exits.
    reference=json.loads((ROOT/'build/whole/startup.ref.json').read_text())['frames']
    differences=[]
    for i,(got,want) in enumerate(zip(actual,reference)):
        for field in ['ram','device','log','scalars']:
            if got[field]!=want[field]:differences.append(dict(frame=i,field=field,actual=got[field],expected=want[field]))
    save(out/'actual.json',dict(frames=actual));save(out/'differences.json',differences)
    assert len(actual)==6,'missing frame records'
    defects=[]
    for name,define in [('missed-palette','S7_RECORD_MISS_PALETTE'),('stale-seed','S7_RECORD_STALE_SEED')]:
        obj=record/(name+'.o');badexe=record/(name+'.exe');folder=record/name;folder.mkdir(exist_ok=True)
        run([GCC,'-O2','-std=c11','-D'+define,'-I',ROOT,'-I',ROOT/'port','-I',prod,'-c',source,'-o',obj],ROOT,out,name+'-compile')
        run([GCC,*objects,obj,'-o',badexe],ROOT,out,name+'-link')
        bad=run([badexe,prod/'ugh.res',record/'baseline.bin',folder],ROOT,out,name+'-run')
        records=[json.loads(line) for line in bad['stdout'].splitlines()]
        caught=[i for i,(got,want) in enumerate(zip(records,reference)) if got['ram']!=want['ram']]
        assert caught,name+' negative control escaped comparator'
        defects.append(dict(defect=name,detected_frames=caught,comparator='full historical RAM hash'))
    sdlout=out/'sdl';sdlexe=nativebuild.build('sdl',sdlout)
    environment=dict(os.environ,SDL_VIDEO_DRIVER='dummy',SDL_AUDIO_DRIVER='dummy')
    sdl_cases={}
    for name,args in [('absent',['--no-adlib']),('present',[])]:
        row=run([sdlexe,'--pack',sdlout/'ugh.res','--scores',sdlout/'missing.hi','--headless','--unpaced','--replay',*args],ROOT,out,'sdl-'+name,env=environment)
        got=json.loads(row['stdout']);assert got['result']=='slice_end' and got['frames']==6;sdl_cases[name]=got
    window=run([sdlexe,'--pack',sdlout/'ugh.res','--scores',sdlout/'missing.hi','--unpaced','--replay','--no-adlib'],ROOT,out,'sdl-window',env=environment)
    got=json.loads(window['stdout']);assert got['result']=='slice_end' and got['frames']==6 and got['presentations']>6
    sdl_cases['dummy-window']=got
    receipt=dict(result='FAIL' if differences else 'PASS',frames=len(actual),reference_prefix=6,
      production_cases=cases,negative_control='banned include rejected',pack_rejection=['missing','corrupt'],
      recorder_direction='verification -> audited core; expected records opened only after process exit',
      machine_free=witness['stdout'].strip(),defects=defects,sdl=sdl_cases,differences=differences)
    save(out/'receipt.json',receipt)
    if differences:raise RuntimeError('startup prefix differs: '+str([(x['frame'],x['field']) for x in differences]))
    print('PASS native startup: 6/6 RAM, devices and ordered I/O records')
    return receipt
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=ROOT/'build/workers/s7-core/core');a=p.parse_args();verify(a.out)
