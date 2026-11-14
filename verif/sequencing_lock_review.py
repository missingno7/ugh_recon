"""Make an unapplied, reviewable dependent-certificate patch; test its closure.

Only build/workers is written. The real actor_types/demo_presentation certificates
are outside this worker's ownership and are deliberately left unchanged.
"""
import difflib,hashlib,json,shutil,subprocess,sys
from datetime import date
from closure_support import ROOT,save
from sequencing_build import OUT
def digest(data):return hashlib.sha256(data.replace(b'\r\n',b'\n')).hexdigest()
def main():
    assert (ROOT/'.closure-baseline.json').exists(),'run through sequencing_baseline.py'
    proposed=OUT/'dependent-certificates';proposed.mkdir(parents=True,exist_ok=True);proposals=[];patch=[];prior={}
    allowed={'native/bridge/actor_render_bridge.c','verif/render_history_build.py','verif/render_history_shells.py','verif/render_history_coverage.py','metadata/closure/actor_render.json','metadata/closure/actor_types.json'}
    for component in ['actor_types','demo_presentation']:
        n=f'metadata/closure/{component}.json';source=ROOT/n;old=source.read_text();cert=json.loads(old);updates={}
        for name,value in cert['verification_inputs'].items():
            data=prior[name] if name in prior else (ROOT/name).read_bytes();actual=digest(data)
            if actual!=value:
                assert name in allowed,(component,name)
                cert['verification_inputs'][name]=actual;updates[name]=dict(before=value,after=actual)
        note=dict(date=date.today().isoformat(),reason='Proposed by close-stones-12: retire generated actor-render session copy; no actor algorithm/projector/persistence contract or status change.',locks=updates,commands=['python verif/render_history_proofs.py','python verif/render_history_cases.py','python verif/render_history_mutants.py','python verif/render_history_cross_mode.py','python verif/sequencing_integration.py --whole --local-reference','python verif/sequencing_host.py'],results='23 renderer B profiles,695552 slot pairs,19 controls and26 cross-mode boundaries PASS. New session/lifecycle composition:20 scenarios and smoke PASS in both host variants. Proposal only; original certificates are unchanged.')
        previous=cert.get('evidence_refreshed',[])
        if not isinstance(previous,list):previous=[previous]
        cert['evidence_refreshed']=[*previous,note];data=(json.dumps(cert,indent=2)+'\n').encode();prior[n]=data
        path=proposed/f'{component}.json';path.write_bytes(data);proposals.append(dict(certificate=n,proposed_copy=str(path.relative_to(ROOT)),status=cert['status'],updates=updates))
        patch.extend(difflib.unified_diff(old.splitlines(True),data.decode().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
    (proposed/'refresh.patch').write_text(''.join(patch))
    scratch=OUT/'closure-lock-review';scratch.mkdir(parents=True,exist_ok=True)
    for folder in ['c','src','native','tools','metadata','host','tests','verif','docs']:shutil.copytree(ROOT/folder,scratch/folder,dirs_exist_ok=True)
    command=[sys.executable,'tools/closure.py'];raw=subprocess.run(command,cwd=scratch,capture_output=True,text=True);(scratch/'before.log').write_text(raw.stdout+raw.stderr);assert raw.returncode!=0
    for p in proposals:shutil.copyfile(ROOT/p['proposed_copy'],scratch/p['certificate'])
    check=subprocess.run(command,cwd=scratch,capture_output=True,text=True);(scratch/'after.log').write_text(check.stdout+check.stderr);print(check.stdout+check.stderr,flush=True);assert check.returncode==0
    save(OUT/'lock-review.json',dict(result='PASS_PROPOSAL_ONLY',original_certificates_changed=False,proposals=proposals,command=command,unrefreshed_returncode=raw.returncode,unrefreshed_output=raw.stdout+raw.stderr,proposed_returncode=check.returncode,proposed_output=check.stdout+check.stderr,scope='Independent build-directory review of exact unapplied patch; not current acceptance and not authority to alter unowned root metadata.'))
if __name__=='__main__':main()
