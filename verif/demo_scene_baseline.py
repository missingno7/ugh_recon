"""Replay in an owned committed snapshot, excluding concurrent verifier edits.

No checkout/index/ref changes. The snapshot records its revision, exact tool
blobs and overlay; normal CLI proof, integration and host tools run there.
"""
import io,json,os,shutil,subprocess,sys,tarfile
from pathlib import Path
from closure_support import ROOT,hashes,save
from demo_scene_build import OUT,FILES
def main():
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();snapshot=OUT/f'clean-replay-{os.getpid()}';snapshot.mkdir(parents=True,exist_ok=True)
    archive=subprocess.check_output(['git','archive','--format=tar',revision,'c','src','native','tools','metadata','host','tests','verif','docs'],cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive),mode='r:') as baseline:
        for member in baseline.getmembers():
            if not member.isfile():continue
            target=(snapshot/member.name).resolve();assert target.is_relative_to(snapshot.resolve());data=baseline.extractfile(member).read();current=ROOT/member.name
            if current.is_file() and current.read_bytes().replace(b'\r\n',b'\n')==data.replace(b'\r\n',b'\n'):data=current.read_bytes()
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    overlays=[*FILES,ROOT/'metadata/closure/actor_types.json',ROOT/'metadata/closure/demo_presentation.json',*sorted((ROOT/'verif').glob('demo_scene*'))]
    for source in overlays:
        if source.is_file():target=snapshot/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    asset=snapshot/'assets/dos/UGH.EXE';asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'assets/dos/UGH.EXE',asset)
    save(snapshot/'.closure-baseline.json',dict(revision=revision,repository=str(ROOT),purpose='Committed current20 scenario baseline; excludes unrelated uncommitted SoundBlaster verifier and audio work.'))
    # Cache reuse is optional and identity checked by the unchanged wholegame.
    cached=snapshot/'build/whole';cached.mkdir(parents=True,exist_ok=True)
    for path in (ROOT/'build/whole').glob('*.ref.json'):shutil.copyfile(path,cached/path.name)
    command=[sys.executable,'verif/demo_scene_reproduce.py','--fresh']
    run=subprocess.run(command,cwd=snapshot,stdout=(snapshot/'replay.log').open('w'),stderr=subprocess.STDOUT)
    print((snapshot/'replay.log').read_text(),flush=True)
    save(OUT/'baseline-replay.json',dict(result='PASS' if not run.returncode else 'FAIL',returncode=run.returncode,command=command,snapshot=str(snapshot.relative_to(ROOT)),revision=revision,tool_inputs=hashes([snapshot/'tools/emu.py',snapshot/'tools/wholegame.py']),overlay_inputs=hashes(overlays)))
    assert not run.returncode
    artifacts=snapshot/'build/workers/close-stones-7'
    for source in artifacts.iterdir():
        if source.is_dir():shutil.copytree(source,OUT/source.name,dirs_exist_ok=True)
        elif source.is_file():shutil.copyfile(source,OUT/source.name)
    # The raw receipts retain their actual snapshot paths. Only the convenience
    # host location is rebased for root-side review tooling.
    host=json.loads((OUT/'host.json').read_text());host['scratch']=str((snapshot/host['scratch']).relative_to(ROOT));host['source_snapshot']=str(snapshot.relative_to(ROOT));save(OUT/'host.json',host)
    for name in ['actor_types','demo_presentation']:
        source=snapshot/f'metadata/closure/{name}.json';shutil.copyfile(source,ROOT/f'metadata/closure/{name}.json')
    print('PASS owned committed baseline replay',revision,str(snapshot.relative_to(ROOT)),flush=True)
if __name__=='__main__':main()
