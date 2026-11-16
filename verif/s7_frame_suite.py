"""Bounded native frame corpus, focused cases and independent negative controls."""
import argparse
import concurrent.futures
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
import nativebuild
import s7_audio
import s7_frame
from cbuild import GCC
from job_pool import run,save


def negative_controls(out,prod):
    controls={};source=ROOT/'tests/levels/one-43.txt'
    folder=out/'controls/missed-timer';assert not s7_frame.verify(source,folder,prod,define='S7_FRAME_MISS_TIMER')
    controls['recorder']=json.loads((folder/'receipt.json').read_text())
    folder=out/'controls/changed-fade';folder.mkdir(parents=True,exist_ok=True)
    text=(ROOT/'native/compose_frame.c').read_text();old='case SESSION_FADE_ADVANCE:w->run.fade_level=e.value;'
    assert text.count(old)==1
    changed=folder/'compose_frame.c';changed.write_text(text.replace(old,'case SESSION_FADE_ADVANCE:w->run.fade_level=(uint16_t)(e.value+2u);'))
    obj=folder/'changed.o'
    run([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I',ROOT,'-I',ROOT/'native','-I',prod,'-c',changed,'-o',obj],ROOT,folder,'compile-defect')
    manifest=json.loads((ROOT/'metadata/native-manifest.json').read_text());original=prod/('object-%02d.o'%manifest['core'].index('native/compose_frame.c'))
    assert not s7_frame.verify(source,folder,prod,replacements={original:obj})
    controls['composition']=json.loads((folder/'receipt.json').read_text())
    folder=out/'controls/missed-enemy-role'
    assert not s7_frame.verify(ROOT/'tests/scenarios/gameplay.txt',folder,prod,define='S7_FRAME_MISS_ENEMY_ROLE')
    controls['enemy_role_observer']=json.loads((folder/'receipt.json').read_text())
    save(out/'controls.json',controls)
    return controls


def verify(out,build=True):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True);prod=out/'production'
    if build:nativebuild.build('test',prod)
    cases=out/'cases';cases.mkdir(exist_ok=True)
    exe=s7_audio.executable(ROOT/'verif/s7_frame_cases.c',cases,prod)
    print(run([exe,prod/'ugh.res'],ROOT,cases,'run')['stdout'].strip(),flush=True)
    names=['gameplay','gameplay-adlib','departure','passenger','water','water-physics','items-multiplier','items-timer','two-player','dino','enemy','completion']
    paths=[ROOT/'tests/scenarios'/(n+'.txt') for n in names]
    for group in ['levels','levels-audio','levels-deep','native-frame']:paths+=sorted((ROOT/'tests'/group).glob('*.txt'))
    def check(path):
        folder=out/'corpus'/path.parent.name/path.stem
        try:
            s7_frame.verify(path,folder,prod)
            return path.relative_to(ROOT).as_posix(),json.loads((folder/'receipt.json').read_text())
        except Exception as error:
            return path.relative_to(ROOT).as_posix(),dict(result='BLOCKED',classification='blocked',reason=str(error))
    # Every compiler/replay/reference child has its own 8-GiB/600-s job. Three
    # workers total, including independently executed original-ASM diagnostics.
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=dict(pool.map(check,paths))
    save(out/'corpus.json',results)
    controls=negative_controls(out,prod)
    failed={name:r for name,r in results.items() if r['result']!='PASS'}
    passed={name:r['records'] for name,r in results.items() if r['result']=='PASS'}
    receipt=dict(result='FAIL' if failed else 'PASS',passed=passed,failed=failed,negative_controls='3/3 detected')
    save(out/'frame-receipt.json',receipt)
    print('native frame suite:',receipt['result'],len(passed),'complete',len(failed),'failures',flush=True)
    return not failed


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'build/workers/s7-frame');p.add_argument('--no-build',action='store_true');p.add_argument('--controls-only',action='store_true');a=p.parse_args()
    if a.controls_only:
        out=a.out.resolve();checks=negative_controls(out,out/'production')
        receipt=json.loads((out/'frame-receipt.json').read_text());receipt['negative_controls']='%d/%d detected'%(len(checks),len(checks));save(out/'frame-receipt.json',receipt)
    else:raise SystemExit(0 if verify(a.out,not a.no_build) else 1)
