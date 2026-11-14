"""Replay only acceptance after a documentation-only committed baseline change.

Invoke through water_weather_baseline.py --new-baseline. Reuse is conditional
on exact receipt input bytes, including generated harnesses and tool binaries.
"""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
from closure_support import ROOT,save
from water_weather_build import OUT
from water_weather_proofs import jobs,current

def run(*args,cwd=ROOT):
    print('RUN '+' '.join(args),flush=True)
    subprocess.run([sys.executable,*args],cwd=cwd,check=True)

def check_inputs(label,inputs):
    for name,expected in inputs.items():
        path=Path(name)
        if not path.is_absolute():path=ROOT/path
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==expected,(label,name,'changed locked input')
    return dict(receipt=label,matched_inputs=len(inputs))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--reuse-from',required=True,type=Path);a=ap.parse_args()
    previous=a.reuse_from.resolve();source=previous/OUT.relative_to(ROOT)
    assert previous!=ROOT and (previous/'.closure-baseline.json').is_file()
    OUT.mkdir(parents=True,exist_ok=True)
    for name in ['proofs','kernel','negative','cases','enumeration','reference']:
        shutil.copytree(source/name,OUT/name,dirs_exist_ok=True)
    for name in ['proof-matrix.json','cases/result.json','enumeration/result.json','coverage.json','integration.json','mutants.json','build.json']:
        target=OUT/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/name,target)
    (OUT/'whole').mkdir(exist_ok=True)
    for path in (source/'whole').glob('*.ref.json'):shutil.copyfile(path,OUT/'whole'/path.name)
    checks=[]
    for _,path in jobs():
        assert current(path),path
        checks.append(check_inputs(str(path.relative_to(ROOT)),json.loads(path.read_text())['inputs']))
    # The previous final counter proof refreshed its source lock after the
    # inventory receipt was made. Refresh this static inventory, not the proofs.
    run('verif/water_weather_coverage.py')
    for name in ['cases/result.json','enumeration/result.json','coverage.json','integration.json']:
        data=json.loads((OUT/name).read_text());checks.append(check_inputs(name,data['inputs']))
    integration=json.loads((OUT/'integration.json').read_text())
    checks.append(check_inputs('integration.build.maintained_inputs',integration['build']['maintained_inputs']))
    compiler=Path(integration['build']['command'][0])
    assert hashlib.sha256(compiler.read_bytes()).hexdigest()==integration['build']['compiler_sha256']
    old=json.loads((previous/'.closure-baseline.json').read_text())
    new=json.loads((ROOT/'.closure-baseline.json').read_text())
    changed=subprocess.check_output(['git','diff','--name-only',old['revision'],new['revision']],cwd=new['repository'],text=True).splitlines()
    assert set(changed)<={'docs/architecture-model.md','docs/amiga.md','metadata/closure/music_clock.json'},changed
    save(OUT/'acceptance-reuse.json',dict(result='PASS',previous_baseline=old['revision'],baseline=new['revision'],changed_committed_files=changed,reused_checks=checks,reused_proofs=len(jobs()),reused_cases=len(integration['cases']),reused_scenarios=len(integration['scenario_audits']),mutants='12 detections retained; their native and compiled-harness inputs match the reused case receipts.',superseded='Previous music_clock architecture lock failure; no blocked result is current acceptance.'))
    run('verif/water_weather_certificate.py','--draft')
    run('verif/water_weather_host.py')
    run('verif/water_weather_certificate.py')
    host=json.loads((OUT/'host.json').read_text());scratch=ROOT/host['scratch']
    cert=json.loads((ROOT/'metadata/closure/water_weather.json').read_text())
    assert cert['status']=='unanalyzed' and cert['proposed_status']=='migrated'
    cert['status']='migrated';save(scratch/'metadata/closure/water_weather.json',cert)
    result=subprocess.run([sys.executable,'tools/closure.py'],cwd=scratch,capture_output=True,text=True)
    (OUT/'final-promoted-closure.log').write_text(result.stdout+result.stderr)
    print(result.stdout+result.stderr,flush=True);assert not result.returncode
    run('tools/closure.py')

if __name__=='__main__':main()
