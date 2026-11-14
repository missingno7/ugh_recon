"""Materialize HEAD and this worker's overlay, without changing Git state."""
import hashlib,io,json,os,shutil,subprocess,sys,tarfile
from pathlib import Path
from closure_support import ROOT,hashes,save
from player_physics_build import OUT,FILES
def prepare(fresh=False):
    OUT.mkdir(parents=True,exist_ok=True)
    marker=OUT/'snapshot.json'
    if marker.exists() and not fresh:
        recorded=json.loads(marker.read_text());snapshot=ROOT/recorded['snapshot'];revision=recorded['revision']
    else:
        revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        snapshot=OUT/f'committed-{revision[:12]}';snapshot.mkdir(parents=True,exist_ok=True)
        archive=subprocess.check_output(['git','archive','--format=tar',revision,'c','src','native','tools','metadata','host','tests','verif','docs'],cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(archive),mode='r:') as baseline:
            for member in baseline.getmembers():
                if not member.isfile():continue
                target=(snapshot/member.name).resolve();assert target.is_relative_to(snapshot.resolve())
                data=baseline.extractfile(member).read();current=ROOT/member.name
                if current.is_file() and current.read_bytes().replace(b'\r\n',b'\n')==data.replace(b'\r\n',b'\n'):data=current.read_bytes()
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        asset=snapshot/'assets/dos/UGH.EXE';asset.parent.mkdir(parents=True,exist_ok=True)
        original=ROOT/'assets/dos/UGH.EXE'
        if not original.is_file():
            # This installation retains the immutable input in the previous
            # accepted snapshot. Its bytes must match the curated oracle lock.
            original=ROOT/'build/workers/close-stones-7/clean-replay-71900/assets/dos/UGH.EXE'
        lock=json.loads((ROOT/'metadata/oracle.json').read_text())['packed']['file_sha256']
        assert hashlib.sha256(original.read_bytes()).hexdigest()==lock
        shutil.copyfile(original,asset)
        save(snapshot/'.closure-baseline.json',dict(revision=revision,repository=str(ROOT),purpose='Committed20-scenario baseline; excludes concurrent SoundBlaster harness edits and audio work.'))
        cache=snapshot/'build/whole';cache.mkdir(parents=True,exist_ok=True)
        for path in (ROOT/'build/whole').glob('*.ref.json'):shutil.copyfile(path,cache/path.name)
    overlays=[*FILES,ROOT/'metadata/closure/player_physics.json',*sorted((ROOT/'verif').glob('player_physics*'))]
    for source in overlays:
        if source.is_file():target=snapshot/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    negative=OUT/'negative'
    if negative.is_dir():shutil.copytree(negative,snapshot/OUT.relative_to(ROOT)/'negative',dirs_exist_ok=True)
    save(marker,dict(snapshot=str(snapshot.relative_to(ROOT)),revision=revision,tool_inputs=hashes([snapshot/'tools/emu.py',snapshot/'tools/wholegame.py']),overlay_inputs=hashes([p for p in overlays if p.is_file()])))
    return snapshot
def main():
    if '--collect' in sys.argv:
        record=json.loads((OUT/'snapshot.json').read_text());snapshot=ROOT/record['snapshot'];artifacts=snapshot/OUT.relative_to(ROOT)
        for source in artifacts.iterdir():
            if source.is_dir():shutil.copytree(source,OUT/source.name,dirs_exist_ok=True)
            else:shutil.copyfile(source,OUT/source.name)
        host=json.loads((OUT/'host.json').read_text());host['scratch']=str((snapshot/host['scratch']).relative_to(ROOT));host['source_snapshot']=str(snapshot.relative_to(ROOT));save(OUT/'host.json',host)
        shutil.copyfile(snapshot/'metadata/closure/player_physics.json',ROOT/'metadata/closure/player_physics.json')
        save(OUT/'baseline-replay.json',dict(result='PASS',**record,source_snapshot=str(snapshot.relative_to(ROOT))))
        print('Collected committed-baseline replay',record['revision'],flush=True);return
    fresh='--new-baseline' in sys.argv
    if fresh:sys.argv.remove('--new-baseline')
    snapshot=prepare(fresh=fresh);print(snapshot,flush=True)
    if len(sys.argv)>1:
        command=[sys.executable,*sys.argv[1:]]
        result=subprocess.run(command,cwd=snapshot)
        raise SystemExit(result.returncode)
if __name__=='__main__':main()
