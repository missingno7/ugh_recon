"""Run the unchanged native host CLI with a real scratch stone promotion."""
import json,shutil,subprocess,sys,os
from pathlib import Path
from closure_support import ROOT,receipt,save
from stones_build import OUT
def main():
    import contacts_reference
    contacts_reference.OUT=OUT/'reference';plain=contacts_reference.prepare_reference(local=True)
    scratch=OUT/f'host-promotion-{os.getpid()}';scratch.mkdir(parents=True,exist_ok=True)
    for directory in ['c','src','native','tools','metadata','host','tests','verif','docs']:
        shutil.copytree(ROOT/directory,scratch/directory,ignore=shutil.ignore_patterns('__pycache__'),dirs_exist_ok=True)
    shutil.copytree(plain.parent,scratch/'build/link/plain',dirs_exist_ok=True)
    path=scratch/'metadata/closure/stones.json';cert=json.loads(path.read_text());cert['status']='migrated';save(path,cert)
    references=scratch/'build/whole';references.mkdir(parents=True,exist_ok=True)
    for path in (OUT/'whole').glob('*.ref.json'):shutil.copyfile(path,references/path.name)
    commands=[[sys.executable,'tools/hostbuild.py'],[sys.executable,'host/check.py','--variant','native']]
    for i,command in enumerate(commands):
        run=subprocess.run(command,cwd=scratch,capture_output=True,text=True)
        (scratch/f'command-{i}.log').write_text(run.stdout+run.stderr);print(run.stdout+run.stderr,flush=True);assert not run.returncode
    check=json.loads((scratch/'build/workers/host-native/host-check-native.json').read_text())
    build=json.loads((scratch/'build/host/hostbuild.json').read_text())
    assert 'stones' in [unit['component'] for unit in build['linked_units']]
    save(OUT/'host.json',receipt(commands[0],[Path(__file__),ROOT/'metadata/closure/stones.json',ROOT/'tools/hostbuild.py',ROOT/'host/check.py'],
        result='PASS',commands=commands,scratch=str(scratch.relative_to(ROOT)),build=build,check=check))
if __name__=='__main__':main()
