"""Actual host CLI gates with only this certificate promoted in a scratch tree."""
import argparse,json,shutil,subprocess,sys,os,tarfile,hashlib
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_samples_build import OUT
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--baseline',default='f647495');parser.add_argument('--working-tree',action='store_true');args=parser.parse_args()
    import contacts_reference
    contacts_reference.OUT=OUT/'reference';plain=contacts_reference.prepare_reference(local=True)
    scratch=OUT/f'host-promotion-{os.getpid()}';scratch.mkdir(parents=True,exist_ok=True)
    baseline=None
    if args.working_tree:
        for directory in ['c','src','native','tools','metadata','host','tests','verif','docs']:
            shutil.copytree(ROOT/directory,scratch/directory,ignore=shutil.ignore_patterns('__pycache__'),dirs_exist_ok=True)
    else:
        baseline=subprocess.check_output(['git','rev-parse',args.baseline],cwd=ROOT,text=True).strip()
        archive=OUT/f'host-baseline-{os.getpid()}.tar'
        subprocess.run(['git','archive','--format=tar','--output',str(archive),baseline],cwd=ROOT,check=True)
        with tarfile.open(archive) as tree:
            for member in tree.getmembers():
                target=(scratch/member.name).resolve()
                assert target.is_relative_to(scratch.resolve()) and not member.issym() and not member.islnk(),'unsafe archive member'
            tree.extractall(scratch,filter='data')
        # git archive stores LF; the checked pinned-tool receipt hashes the
        # checkout's actual bytes. Restore only line-ending-equivalent inputs,
        # after proving they are the same baseline source text.
        checked=json.loads((plain.parent/'build.json').read_text())
        for name in checked['source_sha256']:
            source=ROOT/name;target=scratch/name
            assert target.is_file() and target.read_bytes().replace(b'\r\n',b'\n')==source.read_bytes().replace(b'\r\n',b'\n'),f'baseline build input changed: {name}'
            shutil.copyfile(source,target)
        own=[ROOT/'native/adlx_samples.c',ROOT/'native/adlx_samples.h',ROOT/'native/bridge/adlx_samples_bridge.c',ROOT/'metadata/closure/adlx_samples.json',ROOT/'verif/sb_gameplay.txt',*sorted((ROOT/'verif').glob('adlx_samples*'))]
        for source in own:
            if source.is_file():
                target=scratch/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    # Preview only the explicitly requested harness compatibility relock in
    # this scratch tree. Root accepted certificates are never edited here.
    # Native/L1/formal sources are unchanged; legacy L0 suites and all20 exact
    # observations are independently rerun before this gate.
    compatibility=json.loads((OUT/'compat.json').read_text());legacy=json.loads((OUT/'legacy.json').read_text())
    assert compatibility['result']=='PASS' and legacy['result']=='PASS'
    tool_names=['tools/emu.py','tools/wholegame.py'];baseline_tool={name:hashlib.sha256((scratch/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in tool_names}
    for name in tool_names:shutil.copyfile(ROOT/name,scratch/name)
    refreshed=[]
    for cert_path in (scratch/'metadata/closure').glob('*.json'):
        cert=json.loads(cert_path.read_text());changed=[]
        for name in tool_names:
            expected=cert.get('verification_inputs',{}).get(name)
            if expected:
                raw=(scratch/name).read_bytes()
                if cert.get('verification_input_hashing')=='sha256-lf-text':raw=raw.replace(b'\r\n',b'\n')
                actual=hashlib.sha256(raw).hexdigest()
                if expected!=actual:
                    assert expected==baseline_tool[name],('unrelated stale certificate',cert_path,name)
                    cert['verification_inputs'][name]=actual;changed.append(name)
        if changed:
            cert['evidence_refreshed']=dict(reason='Scratch-only preview: additive SB harness; all20 legacy frame/terminal/coverage records unchanged, full L0/L1 suites replayed normal+poison; no native algorithm/proof input change.',inputs=changed)
            cert_path.write_text(json.dumps(cert,indent=2)+'\n');refreshed.append(dict(certificate=cert_path.name,inputs=changed))
    shutil.copytree(plain.parent,scratch/'build/link/plain',dirs_exist_ok=True)
    path=scratch/'metadata/closure/adlx_samples.json';cert=json.loads(path.read_text());cert['status']='migrated';path.write_text(json.dumps(cert,indent=2)+'\n')
    references=scratch/'build/whole';references.mkdir(parents=True,exist_ok=True)
    for path in (OUT/'whole').glob('*.ref.json'):shutil.copyfile(path,references/path.name)
    for path in (scratch/'tests/scenarios').glob('*.txt'):assert (references/f'{path.stem}.ref.json').exists(),'run integration --whole first'
    commands=[[sys.executable,'tools/hostbuild.py'],[sys.executable,'host/check.py','--variant','native']]
    if baseline:commands.append([sys.executable,'tools/closure.py'])
    for i,command in enumerate(commands):
        run=subprocess.run(command,cwd=scratch,capture_output=True,text=True)
        (scratch/f'command-{i}.log').write_text(run.stdout+run.stderr);print(run.stdout+run.stderr,flush=True);assert not run.returncode
    check=json.loads((scratch/'build/workers/host-native/host-check-native.json').read_text())
    built=json.loads((scratch/'build/host/hostbuild.json').read_text())
    assert 'adlx_samples' in [unit['component'] for unit in built['linked_units']]
    save(OUT/('host-working.json' if args.working_tree else 'host.json'),receipt(commands[0],[Path(__file__),ROOT/'metadata/closure/adlx_samples.json',scratch/'tools/hostbuild.py',scratch/'host/check.py',scratch/'tools/closure.py'],
        result='PASS',commands=commands,baseline=baseline,scratch=str(scratch.relative_to(ROOT)),build=built,check=check,scratch_compatibility_relocks=refreshed))
if __name__=='__main__':main()
