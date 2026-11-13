"""Run the unchanged native host CLI with a real scratch passenger water promotion."""
import io,json,shutil,subprocess,sys,os,tarfile
from pathlib import Path
from closure_support import ROOT,receipt,save
from water_build import OUT
def main():
    import contacts_reference
    contacts_reference.OUT=OUT/'reference';plain=contacts_reference.prepare_reference(local=True)
    scratch=OUT/f'host-promotion-{os.getpid()}';scratch.mkdir(parents=True,exist_ok=True)
    # Reproduce a clean committed baseline plus this work order's owned files.
    # The concurrent audio worker's untracked/in-progress files are not inputs
    # to a passenger review. No errors are filtered from the scratch checker.
    directories=['c','src','native','tools','metadata','host','tests','verif','docs']
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    archive=subprocess.check_output(['git','archive','--format=tar',revision,*directories],cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive),mode='r:') as baseline:
        for member in baseline.getmembers():
            if not member.isfile():continue
            target=(scratch/member.name).resolve()
            assert target.is_relative_to(scratch.resolve()),member.name
            data=baseline.extractfile(member).read();current=ROOT/member.name
            # Preserve checkout EOL bytes for the L0 build receipt, but only
            # after proving content equals the pinned committed snapshot.
            if current.is_file():
                checked=current.read_bytes()
                if checked.replace(b'\r\n',b'\n')==data.replace(b'\r\n',b'\n'):data=checked
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    additions=['native/passenger_water.h','native/passenger_water.c','native/bridge/passenger_water_bridge.c',
        'metadata/closure/passenger_water.json',*[p.relative_to(ROOT).as_posix() for p in (ROOT/'verif').glob('water*')]]
    for name in sorted(set(additions)):
        if not name or Path(name).parts[0] not in directories:continue
        source=ROOT/name
        if not source.is_file():continue
        target=scratch/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    shutil.copytree(plain.parent,scratch/'build/link/plain',dirs_exist_ok=True)
    path=scratch/'metadata/closure/passenger_water.json';cert=json.loads(path.read_text());cert['status']='migrated';save(path,cert)
    references=scratch/'build/whole';references.mkdir(parents=True,exist_ok=True)
    for path in (OUT/'whole').glob('*.ref.json'):shutil.copyfile(path,references/path.name)
    missing=[p.stem for p in (scratch/'tests/scenarios').glob('*.txt') if not (references/(p.stem+'.ref.json')).is_file()]
    if missing:raise RuntimeError('Committed scenario set changed; rerun water_integration.py --whole --local-reference: '+', '.join(missing))
    shutil.copyfile(ROOT/'verif/water_witness.txt',scratch/'tests/scenarios/water-physics.txt')
    shutil.copyfile(OUT/'witness-extend/reference.json',references/'water-physics.ref.json')
    commands=[[sys.executable,'tools/closure.py'],[sys.executable,'tools/hostbuild.py'],[sys.executable,'host/check.py','--variant','native']]
    for i,command in enumerate(commands):
        run=subprocess.run(command,cwd=scratch,capture_output=True,text=True)
        (scratch/f'command-{i}.log').write_text(run.stdout+run.stderr);print(run.stdout+run.stderr,flush=True);assert not run.returncode
    check=json.loads((scratch/'build/workers/host-native/host-check-native.json').read_text())
    build=json.loads((scratch/'build/host/hostbuild.json').read_text())
    assert 'passenger_water' in [unit['component'] for unit in build['linked_units']]
    save(OUT/'host.json',receipt(commands[0],[Path(__file__),ROOT/'metadata/closure/passenger_water.json',ROOT/'tools/hostbuild.py',ROOT/'host/check.py'],
        result='PASS',commands=commands,baseline_revision=revision,scratch=str(scratch.relative_to(ROOT)),build=build,check=check))
if __name__=='__main__':main()
