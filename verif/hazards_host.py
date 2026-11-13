"""Run the unchanged host builder/checker in an actual scratch promotion.

Only build/workers/close-hazards/ is written. All maintained source files, including
host/ and c/, are copied, then only the scratch hazard status is set to migrated.
The real CLI commands run without selection or generation monkeypatches.
"""
import json,shutil,subprocess,sys,os
from pathlib import Path
from closure_support import ROOT,receipt,save
from hazards_build import OUT

def main():
    import contacts_reference
    contacts_reference.OUT=OUT/'reference'
    plain=contacts_reference.prepare_reference(local=True)
    scratch=OUT/f'host-promotion-{os.getpid()}';scratch.mkdir(parents=True,exist_ok=True)
    for directory in ['c','src','native','tools','metadata','host','tests','verif','docs']:
        shutil.copytree(ROOT/directory,scratch/directory,ignore=shutil.ignore_patterns('__pycache__'),dirs_exist_ok=True)
    target=scratch/'build/link/plain';shutil.copytree(plain.parent,target,dirs_exist_ok=True)
    # read_symbols also validates the exact maintained source/build-tool inputs.
    cert_path=scratch/'metadata/closure/hazards.json';cert=json.loads(cert_path.read_text());cert['status']='migrated'
    cert_path.write_text(json.dumps(cert,indent=2)+'\n')
    references=scratch/'build/whole';references.mkdir(parents=True,exist_ok=True)
    for path in (OUT/'whole').glob('*.ref.json'):shutil.copyfile(path,references/path.name)
    # The unchanged checker accepts an extra scenario from its normal folder.
    shutil.copyfile(ROOT/'verif/hazards_dino.txt',scratch/'tests/scenarios/hazards_dino.txt')
    dino=json.loads((OUT/'dino/reference.json').read_text());save(references/'hazards_dino.ref.json',dino)
    commands=[[sys.executable,'tools/hostbuild.py'],[sys.executable,'host/check.py','--variant','native']]
    for i,command in enumerate(commands):
        run=subprocess.run(command,cwd=scratch,capture_output=True,text=True)
        (scratch/f'command-{i}.log').write_text(run.stdout+run.stderr)
        print(run.stdout+run.stderr,flush=True);assert not run.returncode
    check=json.loads((scratch/'build/workers/host-native/host-check-native.json').read_text())
    build=json.loads((scratch/'build/host/hostbuild.json').read_text())
    assert 'hazards' in [unit['component'] for unit in build['linked_units']]
    save(OUT/'host.json',receipt(commands[0],[Path(__file__),ROOT/'metadata/closure/hazards.json',ROOT/'tools/hostbuild.py',ROOT/'host/check.py'],
        result='PASS',commands=commands,scratch=str(scratch.relative_to(ROOT)),build=build,check=check))
if __name__=='__main__':main()
