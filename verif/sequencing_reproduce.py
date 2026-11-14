"""Complete replay inside sequencing_baseline's committed archive."""
import argparse,subprocess,sys
from closure_support import ROOT
from sequencing_build import OUT
def run(*args):
    print('RUN '+' '.join(args),flush=True);subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fresh',action='store_true');a=ap.parse_args();assert (ROOT/'.closure-baseline.json').exists(),'use sequencing_baseline.py'
    if a.fresh:
        import contacts_reference as reference
        reference.OUT=OUT/'reference';reference.prepare_reference(local=True,fresh=True);reference.expanded_image(local=True,fresh=True)
    run('verif/lifecycle_shells.py');run('verif/session_bridge.py');run('verif/sequencing_limits.py')
    run('verif/sequencing_proofs.py');run('verif/sequencing_records.py')
    for mode in ['output','frame','dependence']:
        run('verif/session_copy_proof.py',mode);run('verif/session_copy_proof.py',mode,'--reachability')
    run('verif/sequencing_mutants.py')
    for entry in ['render_history_proofs','render_history_cases','render_history_mutants','render_history_cross_mode']:
        run('verif/'+entry+'.py')
    run('verif/sequencing_inventory.py');run('verif/sequencing_integration.py','--whole','--local-reference');run('verif/sequencing_cases.py')
    run('verif/sequencing_actor_refresh.py');run('verif/sequencing_certificate.py');run('verif/sequencing_host.py');run('verif/sequencing_certificate.py','--final');run('verif/sequencing_lock_review.py')
    # Real acceptance remains blocked on the two supervisor-owned certificates.
    # The proposal-only check is intentionally not substituted for this result.
    result=subprocess.run([sys.executable,'tools/closure.py'],cwd=ROOT)
    print('Current acceptance closure:',result.returncode,'; independent proposed-lock review is in lock-review.json',flush=True)
    return result.returncode
if __name__=='__main__':raise SystemExit(main())
