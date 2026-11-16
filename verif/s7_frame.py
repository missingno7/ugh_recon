"""Full native frame comparisons; expected JSON opens only after child exit."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
import nativebuild
import s7_audio
import s7_frame_record
from cbuild import GCC
from job_pool import run,save


def reference_worker(path,out):
    import wholegame
    from emu import NativeVga
    out=Path(out);out.mkdir(exist_ok=True)
    wholegame.VGA_ACCELERATOR=NativeVga(out)
    try:
        script=wholegame.scenario(Path(path));m,initial=wholegame.fixture(script)
        records,coverage,_=wholegame.original(script,m,initial)
        save(out/'reference.json',dict(frames=records,coverage=coverage))
    finally:wholegame.VGA_ACCELERATOR.close()


def verify(path,out,prod,dump=-1,define=None,replacements=None):
    path=Path(path);out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True);prod=Path(prod).resolve()
    receipt=json.loads((prod/'nativebuild.json').read_text())
    assert receipt['result']=='PASS' and receipt['manifest']==nativebuild.sha(ROOT/'metadata/native-manifest.json')
    for name,digest in receipt['inputs'].items():assert nativebuild.sha(ROOT/name)==digest,'stale production input: '+name
    source=s7_frame_record.generate(out,path,dump)
    if define:source.write_text('#define '+define+'\n'+source.read_text())
    obj=out/'record.o';exe=out/'record.exe'
    run([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I',ROOT,'-I',ROOT/'port','-I',prod,'-c',source,'-o',obj],ROOT,out,'compile')
    objects=[(replacements or {}).get(p,p) for p in s7_audio.objects(prod)]
    run([GCC,*objects,obj,*['-Wl,--wrap='+n for n in s7_frame_record.WRAPS],'-o',exe],ROOT,out,'link')
    row=run([exe,prod/'ugh.res',out/'baseline.bin',out],ROOT,out,'record',allowed=(0,4))
    actual=[json.loads(line) for line in row['stdout'].splitlines()]
    group={'scenarios':'whole','levels':'levels','levels-audio':'levels-audio','levels-deep':'levels-deep'}.get(path.parent.name)
    if group:reference=ROOT/'build'/group/(path.stem+'.ref.json')
    else:
        # A new diagnostic trace executes independent original ASM after the
        # production process exits. Neither its RAM nor records seed GameWorld.
        reference=out/'original/reference.json'
        run([sys.executable,Path(__file__),'--reference-worker',path,'--out',reference.parent],ROOT,out,'original')
    expected=json.loads(reference.read_text())['frames']
    diff=[dict(frame=i,field=k,actual=a.get(k),expected=b.get(k)) for i,(a,b) in enumerate(zip(actual,expected)) for k in sorted(set(a)|set(b)) if a.get(k)!=b.get(k)]
    waiting='WAIT_ENEMIES' in row['stderr']
    if len(actual)!=len(expected) and not waiting:diff.append(dict(field='count',actual=len(actual),expected=len(expected)))
    save(out/'actual.json',dict(frames=actual));save(out/'differences.json',diff)
    result=dict(result='FAIL' if diff else 'WAIT_ENEMIES' if waiting else 'PASS',scenario=str(path),records=len(actual),expected=len(expected),differences=diff,stop=row['stderr'])
    save(out/'receipt.json',result)
    print(path.stem,len(actual),'/',len(expected),result['result'],[(d.get('frame'),d['field']) for d in diff][:12],row['stderr'][-200:],flush=True)
    return not diff


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('scenario',type=Path);p.add_argument('--out',type=Path,default=ROOT/'build/workers/s7-frame/frame');p.add_argument('--production',type=Path,default=ROOT/'build/workers/s7-frame/production');p.add_argument('--dump',type=int,default=-1);p.add_argument('--build',action='store_true');p.add_argument('--reference-worker',action='store_true');a=p.parse_args()
    if a.reference_worker:reference_worker(a.scenario,a.out);raise SystemExit(0)
    if a.build:nativebuild.build('test',a.production)
    raise SystemExit(0 if verify(a.scenario,a.out,a.production,a.dump) else 1)
