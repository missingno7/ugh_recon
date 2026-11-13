"""Fresh compiled music evidence, capped split proofs, real scratch host gate."""
import argparse,subprocess,sys,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from closure_support import ROOT,receipt,save
from adlx_music_build import OUT
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
    commands=[['verif/adlx_music_inventory.py'],['verif/adlx_music_evidence.py'],['verif/adlx_music_evidence.py','--budget'],
        *[['verif/adlx_music_evidence.py','--negative',n] for n in ['signed','wait','volume']],
        ['verif/adlx_music_corpus.py'],['verif/adlx_music_integration.py','--whole','--local-reference']]
    for command in commands:
        rows.append(run(command))
        if rows[-1]['returncode']:break
    if not a.skip_proofs and not any(r['returncode'] for r in rows):
        proofs=[['verif/adlx_music_fade.py',mode,*(['--word-memory'] if mode=='outputs' else [])] for mode in ['outputs','frame','dependence','timer','timer-frame','timer-dependence']]
        proofs += [['verif/adlx_music_flow.py',mode] for mode in ['outputs','frame','dependence']]
        proofs += [['verif/adlx_music_volume.py',mode] for mode in ['outputs','frame','dependence']]
        proofs += [['verif/adlx_music_misc.py',mode,*(['--word-memory'] if mode=='guard' else [])] for mode in ['guard','silence','frame','dependence']]
        proofs += [['verif/adlx_music_fade.py','outputs','--word-memory','--negative'],['verif/adlx_music_flow.py','outputs','--negative']]
        with ThreadPoolExecutor(max_workers=2) as executor:
            for i in range(0,len(proofs),2):
                rows.extend(executor.map(run,proofs[i:i+2]))
                if any(r['returncode'] for r in rows):break
    if not any(r['returncode'] for r in rows):
        rows.append(run(['verif/adlx_music_host.py']))
        if not rows[-1]['returncode']:rows.append(run(['tools/closure.py']))
    save(OUT/'reproduce.json',receipt([sys.executable,'verif/adlx_music_reproduce.py',*(['--fresh-reference'] if a.fresh_reference else []),*(['--skip-proofs'] if a.skip_proofs else [])],[Path(__file__),ROOT/'native/adlx_music.c',ROOT/'native/adlx_music.h',ROOT/'native/bridge/adlx_music_bridge.c',ROOT/'metadata/closure/adlx_music.json'],result='PASS' if not any(r['returncode'] for r in rows) else 'FAIL',commands=rows,max_concurrent_cbmc=2,seconds=time.perf_counter()-started))
    return int(any(r['returncode'] for r in rows))
if __name__=='__main__':raise SystemExit(main())
