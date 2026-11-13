"""Unmodified closure/build/check CLIs in a real clean-baseline scratch tree."""
import io,json,os,shutil,subprocess,sys,tarfile
from closure_support import ROOT,receipt,save
from render_history_build import OUT,FILES
def main():
    import contacts_reference as reference
    reference.OUT=OUT/'reference';plain=reference.prepare_reference(local=True)
    scratch=OUT/f'host-promotion-{os.getpid()}';scratch.mkdir(parents=True,exist_ok=True)
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    archive=subprocess.check_output(['git','archive','--format=tar',revision,'c','src','native','tools','metadata','host','tests','verif','docs'],cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive),mode='r:') as baseline:
        for member in baseline.getmembers():
            if not member.isfile():continue
            target=(scratch/member.name).resolve();assert target.is_relative_to(scratch.resolve());data=baseline.extractfile(member).read();current=ROOT/member.name
            if current.is_file() and current.read_bytes().replace(b'\r\n',b'\n')==data.replace(b'\r\n',b'\n'):data=current.read_bytes()
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    additions=[*FILES,ROOT/'metadata/closure/actor_render.json',ROOT/'docs/closure-howto.md',*sorted((ROOT/'verif').glob('render_history*'))]
    for source in additions:
        if source.is_file():target=scratch/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    shutil.copytree(plain.parent,scratch/'build/link/plain',dirs_exist_ok=True)
    cert_path=scratch/'metadata/closure/actor_render.json';cert=json.loads(cert_path.read_text());cert['status']='migrated';save(cert_path,cert)
    references=scratch/'build/whole';references.mkdir(parents=True,exist_ok=True)
    for path in (OUT/'whole').glob('*.ref.json'):shutil.copyfile(path,references/path.name)
    assert all((references/(p.stem+'.ref.json')).is_file() for p in (scratch/'tests/scenarios').glob('*.txt'))
    commands=[[sys.executable,'tools/closure.py'],[sys.executable,'tools/hostbuild.py'],[sys.executable,'host/check.py','--variant','native']]
    for i,command in enumerate(commands):
        run=subprocess.run(command,cwd=scratch,capture_output=True,text=True);(scratch/f'command-{i}.log').write_text(run.stdout+run.stderr);print(run.stdout+run.stderr,flush=True);assert not run.returncode
    build=json.loads((scratch/'build/host/hostbuild.json').read_text());check=json.loads((scratch/'build/workers/host-native/host-check-native.json').read_text());assert 'actor_render' in [r['component'] for r in build['linked_units']]
    save(OUT/'host.json',receipt(commands[0],[__file__,ROOT/'tools/hostbuild.py',ROOT/'host/check.py',ROOT/'metadata/closure/actor_render.json'],result='PASS',baseline_revision=revision,scratch=str(scratch.relative_to(ROOT)),commands=commands,build=build,check=check))
if __name__=='__main__':main()
