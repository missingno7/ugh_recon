"""Actual host CLIs on the committed baseline; report closure blockers separately."""
import json,shutil,subprocess,sys
from closure_support import ROOT,receipt,save
from sequencing_build import OUT
def main():
    # This command is intended inside sequencing_baseline's committed archive.
    pinned=ROOT/'.closure-baseline.json';assert pinned.exists(),'use sequencing_baseline.py'
    original=json.loads(pinned.read_text());scratch=OUT/'host-promotion';scratch.mkdir(parents=True,exist_ok=True)
    for folder in ['c','src','native','tools','metadata','host','tests','verif','docs']:
        shutil.copytree(ROOT/folder,scratch/folder,dirs_exist_ok=True)
    reference=OUT/'reference/link/plain';assert (reference/'build.json').exists();shutil.copytree(reference,scratch/'build/link/plain',dirs_exist_ok=True)
    references=scratch/'build/whole';references.mkdir(parents=True,exist_ok=True)
    for path in (OUT/'whole').glob('*.ref.json'):shutil.copyfile(path,references/path.name)
    assert all((references/(p.stem+'.ref.json')).exists() for p in (scratch/'tests/scenarios').glob('*.txt'))
    for component in ['lifecycle','session']:
        p=scratch/'metadata/closure'/f'{component}.json';j=json.loads(p.read_text());j['status']='migrated';save(p,j)
    commands=[[sys.executable,'tools/closure.py'],[sys.executable,'tools/hostbuild.py'],[sys.executable,'host/check.py','--variant','native'],[sys.executable,'tools/hostbuild.py','--literal'],[sys.executable,'host/check.py','--variant','literal']]
    rows=[];builds=[];checks=[]
    for i,command in enumerate(commands):
        p=subprocess.run(command,cwd=scratch,capture_output=True,text=True);output=p.stdout+p.stderr;(scratch/f'command-{i}.log').write_text(output);print(output,flush=True);rows.append(dict(command=command,returncode=p.returncode,output=output))
        if i:assert p.returncode==0
        if i in [1,3]:builds.append(json.loads((scratch/'build/host/hostbuild.json').read_text()))
        if i in [2,4]:checks.append(json.loads((scratch/'build/workers/host-native'/('host-check-native.json' if i==2 else 'host-check-literal.json')).read_text()))
    native_units=[u['component'] for u in builds[0]['linked_units']];assert 'lifecycle' in native_units and 'session' in native_units
    save(OUT/'host.json',receipt(['python','verif/sequencing_host.py'],[__file__,ROOT/'tools/hostbuild.py',ROOT/'host/check.py',ROOT/'metadata/closure/lifecycle.json',ROOT/'metadata/closure/session.json'],result='PASS',baseline_revision=original['revision'],scratch=str(scratch.relative_to(ROOT)),closure_result='PASS' if rows[0]['returncode']==0 else 'BLOCKED_DEPENDENT_CERTIFICATE_LOCKS',commands=rows,builds=builds,checks=checks,linked_units=native_units,
      scope='Unmodified actual host build and native/literal check. Only new certificates promoted in scratch. No unrelated certificate lock is silently changed; closure failure stays a recorded acceptance blocker.'))
if __name__=='__main__':main()
