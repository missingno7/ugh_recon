"""Fresh standalone-facade corpus, split capped proofs and scratch host gate."""
import argparse,subprocess,sys,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from closure_support import ROOT,receipt,save
from adlx_voice_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fresh-reference',action='store_true');p.add_argument('--skip-proofs',action='store_true');a=p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);started=time.perf_counter()
    if a.fresh_reference:
        import contacts_reference
        contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True,fresh=True);contacts_reference.expanded_image(local=True,fresh=True)
    rows=[]
    def run(command):
        print('RUN python '+' '.join(command),flush=True);r=subprocess.run([sys.executable,*command],cwd=ROOT)
        return dict(command=[sys.executable,*command],returncode=r.returncode)
    commands=[['verif/adlx_voice_inventory.py'],['verif/adlx_voice_evidence.py'],['verif/adlx_voice_evidence.py','--exhaustive-delay'],
        ['verif/adlx_voice_evidence.py','--negative','source'],['verif/adlx_voice_evidence.py','--negative','gain'],['verif/adlx_voice_evidence.py','--negative','delay','--exhaustive-delay'],
        ['verif/adlx_voice_tracks.py'],['verif/adlx_voice_tracks.py','--effects'],['verif/adlx_voice_pipeline.py'],['verif/adlx_voice_integration.py','--whole','--local-reference']]
    for command in commands:
        rows.append(run(command))
        if rows[-1]['returncode']:break
    if not a.skip_proofs and not any(r['returncode'] for r in rows):
        proofs=[['verif/adlx_voice_leaf.py',mode,'--role',role] for role in ['volume','gain','key','frequency','program'] for mode in ['outputs','frame','dependence']]
        for saved in [0,1]:
            proofs += [['verif/adlx_voice_proofs.py','outputs','--operation','copy','--kernel','--word-memory','--saved',str(saved),'--delta',str(delta)] for delta in range(-11,12)]
            proofs += [['verif/adlx_voice_proofs.py','outputs','--operation','copy','--kernel','--word-memory','--saved',str(saved),'--source',source] for source in ['external','wrap']]
            proofs += [['verif/adlx_voice_proofs.py',mode,'--operation','copy','--kernel','--saved',str(saved)] for mode in ['frame','dependence']]
        proofs += [['verif/adlx_voice_proofs.py',mode,'--operation','selector','--kernel','--word-memory'] for mode in ['outputs','frame','dependence']]
        proofs += [['verif/adlx_voice_io.py',mode] for mode in ['register','delay']]
        proofs += [['verif/adlx_voice_admission.py'],['verif/adlx_voice_admission.py','--negative'],['verif/adlx_voice_proofs.py','outputs','--operation','copy','--kernel','--word-memory','--negative']]
        with ThreadPoolExecutor(max_workers=2) as executor:
            for i in range(0,len(proofs),2):
                rows.extend(executor.map(run,proofs[i:i+2]))
                if any(r['returncode'] for r in rows):break
    if not any(r['returncode'] for r in rows):
        rows.append(run(['verif/adlx_voice_host.py']))
        if not rows[-1]['returncode']:rows.append(run(['tools/closure.py']))
    save(OUT/'reproduce.json',receipt([sys.executable,'verif/adlx_voice_reproduce.py',*(['--fresh-reference'] if a.fresh_reference else []),*(['--skip-proofs'] if a.skip_proofs else [])],[Path(__file__),ROOT/'native/adlx_voice.c',ROOT/'native/adlx_voice.h',ROOT/'native/bridge/adlx_voice_bridge.c',ROOT/'metadata/closure/adlx_voice.json'],result='PASS' if not any(r['returncode'] for r in rows) else 'FAIL',commands=rows,max_concurrent_cbmc=2,seconds=time.perf_counter()-started))
    return int(any(r['returncode'] for r in rows))
if __name__=='__main__':raise SystemExit(main())
