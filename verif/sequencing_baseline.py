"""Archive e4e69a0 and overlay only close-stones-12's owned files."""
import hashlib,io,json,shutil,subprocess,sys,tarfile
from closure_support import ROOT,save,hashes
from sequencing_build import OUT,BASELINE
from lifecycle_shells import FILES as LIFEFILES
from session_bridge import FILES as SESSIONFILES
def overlays():
    return [*LIFEFILES,*SESSIONFILES,*sorted((ROOT/'verif').glob('sequencing_*')),
      *[ROOT/'verif'/n for n in ['lifecycle_shells.py','session_bridge.py','session_loader.py','session_record_proof.py','session_copy_proof.py','render_history_build.py','render_history_shells.py','render_history_coverage.py']],
      ROOT/'native/bridge/actor_render_bridge.c',*[ROOT/'metadata/closure'/f'{n}.json' for n in ['lifecycle','session','actor_render']]]
def prepare():
    revision=subprocess.check_output(['git','rev-parse',BASELINE],cwd=ROOT,text=True).strip();snapshot=OUT/f'committed-{revision[:12]}';snapshot.mkdir(parents=True,exist_ok=True)
    if not (snapshot/'.closure-baseline.json').exists():
        archive=subprocess.check_output(['git','archive','--format=tar',revision,'c','src','native','tools','metadata','host','tests','verif','docs'],cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(archive),mode='r:') as baseline:
            for member in baseline.getmembers():
                if not member.isfile():continue
                target=(snapshot/member.name).resolve();assert target.is_relative_to(snapshot.resolve());data=baseline.extractfile(member).read();current=ROOT/member.name
                # Preserve byte hashes where archive LF differs only from this
                # installation's checked-out line endings, never content edits.
                if current.is_file() and current.read_bytes().replace(b'\r\n',b'\n')==data.replace(b'\r\n',b'\n'):data=current.read_bytes()
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        save(snapshot/'.closure-baseline.json',dict(revision=revision,repository=str(ROOT),purpose='Committed baseline plus sequencing-owned overlay; excludes concurrent high_scores/menus/input/video_dos edits.'))
    for source in overlays():
        if source.is_file():target=snapshot/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    original=ROOT/'assets/dos/UGH.EXE'
    if not original.exists():original=ROOT/'build/workers/close-stones-7/clean-replay-71900/assets/dos/UGH.EXE'
    lock=json.loads((ROOT/'metadata/oracle.json').read_text())['packed']['file_sha256'];assert hashlib.sha256(original.read_bytes()).hexdigest()==lock
    asset=snapshot/'assets/dos/UGH.EXE';asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,asset)
    reference=OUT/'reference'
    if reference.is_dir():shutil.copytree(reference,snapshot/OUT.relative_to(ROOT)/'reference',dirs_exist_ok=True)
    for folder in ['whole','rain']:
        dest=snapshot/OUT.relative_to(ROOT)/folder;dest.mkdir(parents=True,exist_ok=True)
        for cached in (OUT/folder).glob('*.ref.json'):shutil.copyfile(cached,dest/cached.name)
    save(OUT/'snapshot.json',dict(snapshot=str(snapshot.relative_to(ROOT)),revision=revision,overlay_inputs=hashes([p for p in overlays() if p.is_file()]),tool_inputs=hashes([snapshot/'tools/emu.py',snapshot/'tools/wholegame.py'])))
    return snapshot
def main():
    snapshot=prepare();print(snapshot,flush=True)
    if len(sys.argv)>1:raise SystemExit(subprocess.run([sys.executable,*sys.argv[1:]],cwd=snapshot).returncode)
if __name__=='__main__':main()
