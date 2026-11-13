"""Actual-C hazard transition proofs and finite compiled comparisons."""
import argparse,json,subprocess
from pathlib import Path
from closure_support import ROOT,compile_c,cbmc,receipt,save
from hazards_pair import pair
from hazards_build import OUT,ENTRIES

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('entry',choices=['generated','dispatcher',*ENTRIES]);p.add_argument('--stones',type=int,choices=range(17),default=1)
    p.add_argument('--timeout',type=int,default=60);p.add_argument('--negative',action='store_true');p.add_argument('--contracts',action='store_true');p.add_argument('--arrays-uf',action='store_true');p.add_argument('--semantic',action='store_true');p.add_argument('--wide-cursor',action='store_true');a=p.parse_args()
    folder=OUT/(a.entry+f'-s{a.stones}'+('-contracts' if a.contracts else '')+('-semantic' if a.semantic else '')+('-wide' if a.wide_cursor else '')+('-uf' if a.arrays_uf else '')+('-negative' if a.negative else ''));inputs=pair(folder)
    source=ROOT/'verif/hazards_harness.c';harness=folder/'harness.c';harness.write_text('#include "pair.inc"\n'+source.read_text())
    inputs+=[source,Path(__file__),ROOT/'verif/hazards_build.py']
    if a.entry=='generated':
        exe=folder/'generated.exe';built=compile_c([harness],exe,[ROOT/'c',ROOT/'native'])
        run=subprocess.run([str(exe)],capture_output=True,text=True)
        save(folder/'result.json',receipt(built['command'],inputs,result='PASS' if not run.returncode else 'FAIL',stdout=run.stdout,stderr=run.stderr))
        print(run.stdout+run.stderr);assert not run.returncode
    else:
        result=cbmc(harness,folder,inputs,unwind=1 if a.negative else 17,timeout=a.timeout,
            defines=['-D__CPROVER__',f'-DOPERATION={ENTRIES.get(a.entry,"H_IGNORE")}',f'-DSTONES={a.stones}',*(['-DDISPATCH_PROOF'] if a.entry=='dispatcher' else []),*(['-DCONTACT_CONTRACT'] if a.contracts else []),*(['-DSEMANTIC_ONLY'] if a.semantic else []),*(['-DWIDE_CURSOR'] if a.wide_cursor else [])],
            extra=['--unwindset',f'reference_FindThrownStoneHittingEnemy.0:{a.stones+1},ref1_enemy_player.0:3,ref0_contact.0:3,ref1_frame.0:2,ref0_enemy_frame.0:2,reference_UpdateBirdFlight.0:2',
                *(['--no-array-field-sensitivity','--arrays-uf-always'] if a.arrays_uf else [])])
        print(json.dumps({k:result[k] for k in ['result','seconds','failures']}),flush=True)
        if a.negative:assert result['result']=='FAIL' and any('unwind' in f[0] for f in result['failures'])
        else:assert result['result']=='PASS'
if __name__=='__main__':main()
