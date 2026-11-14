"""Compare the standalone native host with existing wholegame references.

Run python tools/wholegame.py first to certify/refresh those references.
No reference is created here, and no CPU emulator runs in this checker.
All child processes have wall bounds; one compact receipt is written at end.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/workers/host-native'
BUILD_VARIANT = {'native': 'native-bridged', 'literal': 'literal'}


def require_built_variant(variant):
    """Refuse to check an executable that tools/hostbuild.py did not build as this variant."""
    receipt = json.loads((ROOT/'build/host/hostbuild.json').read_text())
    if receipt.get('variant') != BUILD_VARIANT[variant]:
        raise SystemExit(f"build/host/ugh.exe is the {receipt.get('variant')!r} build; "
                         f"run python tools/hostbuild.py{' --literal' if variant == 'literal' else ''} first")
    digest = hashlib.sha256((ROOT/'build/host/ugh.exe').read_bytes()).hexdigest()
    if receipt.get('executable_sha256') != digest:
        raise SystemExit('build/host/ugh.exe does not match build/host/hostbuild.json; rebuild it')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scenarios', nargs='*')
    parser.add_argument('--variant',choices=('native','literal'),default='native')
    args = parser.parse_args()
    build = require_built_variant(args.variant)
    OUT.mkdir(parents=True,exist_ok=True)
    paths=sorted((ROOT/'tests/scenarios').glob('*.txt'))
    if args.scenarios:
        missing=set(args.scenarios)-{p.stem for p in paths}
        if missing: raise ValueError('unknown scenarios: '+', '.join(sorted(missing)))
        paths=[p for p in paths if p.stem in args.scenarios]
    results=[]
    for path in paths:
        reference=json.loads((ROOT/'build/whole'/f'{path.stem}.ref.json').read_text())['frames']
        # Scenario frame bound includes room for a terminal record.
        frames=next(int(line.split()[1]) for line in path.read_text().splitlines() if line.startswith('frames '))
        command=[str(ROOT/'build/host/ugh.exe'),'--headless',str(frames),'--script',str(path),'--timeout','90']
        started=time.perf_counter()
        try:
            p=subprocess.run(command,capture_output=True,text=True,timeout=95,cwd=ROOT)
            got=[json.loads(line) for line in p.stdout.splitlines()]
            mismatch=next((i+1 for i,(a,b) in enumerate(zip(got,reference)) if a!=b),None)
            passed=p.returncode==0 and len(got)==len(reference) and mismatch is None
            row=dict(scenario=path.stem,passed=passed,boundaries=len(got),expected=len(reference),
                     first_divergence=mismatch,seconds=time.perf_counter()-started,stderr=p.stderr)
            if mismatch: row.update(actual=got[mismatch-1],expected_record=reference[mismatch-1])
        except subprocess.TimeoutExpired:
            row=dict(scenario=path.stem,passed=False,error='95 second wall timeout')
        results.append(row)
        print(('PASS' if row['passed'] else 'FAIL')+f' {path.stem}: '+str(row.get('boundaries',0))+' boundaries',flush=True)
    # The smoke mode runs the original recorded attract scripts, bounded by flips.
    p=subprocess.run([str(ROOT/'build/host/ugh.exe'),'--headless','256','--smoke','256','--timeout','30'],
                     capture_output=True,text=True,timeout=35,cwd=ROOT)
    smoke=dict(passed=p.returncode==0 and len(p.stdout.splitlines())==256,stderr=p.stderr)
    print('PASS smoke: 256 attract frames' if smoke['passed'] else 'FAIL smoke',flush=True)
    receipt=dict(variant=args.variant,executable_sha256=build['executable_sha256'],
                 linked_units=len(build.get('linked_units',[])),passed=all(r['passed'] for r in results) and smoke['passed'],scenarios=results,smoke=smoke)
    (OUT/f'host-check-{args.variant}.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return 0 if receipt['passed'] else 1


if __name__=='__main__': raise SystemExit(main())
