"""Exhaustive finite domains and CBMC on the actual passenger C implementations."""
import argparse,json,subprocess,time
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save,cbmc
from itinerary_build import OUT,NAMES,pair
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['enumerate',*NAMES]);p.add_argument('--timeout',type=int,default=180)
    p.add_argument('--negative',action='store_true');p.add_argument('--arrays-uf',action='store_true');a=p.parse_args()
    folder=OUT/'evidence'/(a.mode+('_uf' if a.arrays_uf else '_bit')+('_negative' if a.negative else ''));inputs=pair(folder)
    source=ROOT/'verif/itinerary_harness.c';harness=folder/'harness.c';harness.write_text('#include "pair.inc"\n'+source.read_text())
    inputs += [source,Path(__file__),*sorted((ROOT/'native').rglob('*.h'))]
    if a.mode=='enumerate':
        exe=folder/'enumerate.exe';built=compile_c([harness],exe,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'])
        start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
        save(folder/'result.json',receipt(built['command'],inputs,execution=[str(exe)],compiler_sha256=built['compiler_sha256'],
            seconds=time.perf_counter()-start,result='PASS' if not run.returncode else 'FAIL',stdout=run.stdout,stderr=run.stderr))
        print(run.stdout+run.stderr,flush=True);assert not run.returncode
    else:
        loops='it_ref0_actor_frame.0:3,it_shell0_actor_frame.0:3,itinerary_vector.0:4,actor_bridge_journey.0:5'
        if a.negative:loops+=',itinerary_prepare.0:1'
        result=cbmc(harness,folder,inputs,unwind=40,timeout=a.timeout,
            defines=['-D__CPROVER__','-DACTOR_VERIFY','-DUINT16_MAX=65535u',f'-DMODE={NAMES.index(a.mode)}'],
            extra=[*(['--arrays-uf-always'] if a.arrays_uf else []),'--unwindset',loops])
        print(json.dumps({k:result[k] for k in ['result','seconds','failures']}),flush=True)
        if a.negative:assert result['result']=='FAIL' and any(row[0]=='itinerary_prepare.unwind.0' for row in result['failures'])
        else:assert result['result']=='PASS'
if __name__=='__main__':main()
