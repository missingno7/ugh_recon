"""Compile exhaustive/differential cases, or run CBMC on the actual C pair."""
import argparse,json,subprocess,time
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save,cbmc
from stones_build import OUT,NAMES,pair
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['enumerate',*NAMES])
    p.add_argument('--platforms',type=int,choices=range(11),default=1);p.add_argument('--timeout',type=int,default=60)
    p.add_argument('--negative',action='store_true');p.add_argument('--semantic',action='store_true');a=p.parse_args()
    folder=OUT/'evidence'/(a.mode+f'_{a.platforms}'+('_semantic' if a.semantic else '')+('_negative' if a.negative else ''));inputs=pair(folder)
    source=ROOT/'verif/stones_harness.c';harness=folder/'harness.c';harness.write_text('#include "pair.inc"\n'+source.read_text())
    inputs += [source,Path(__file__),*sorted((ROOT/'native').rglob('*.h'))]
    if a.mode=='enumerate':
        exe=folder/'enumerate.exe';built=compile_c([harness],exe,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'])
        start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
        result=receipt(built['command'],inputs,execution=[str(exe)],compiler_sha256=built['compiler_sha256'],
            seconds=time.perf_counter()-start,result='PASS' if run.returncode==0 else 'FAIL',stdout=run.stdout,stderr=run.stderr)
        save(folder/'result.json',result);print(run.stdout+run.stderr,flush=True);assert run.returncode==0
    else:
        loops=f'ref0_contact.0:3,l1_UpdateThrownStone.0:{a.platforms+2},stone_flight.0:{a.platforms+1},c_UpdateThrownStone.0:{a.platforms+2},c_UpdateThrownStone.1:{a.platforms+2}'
        result=cbmc(harness,folder,inputs,unwind=40,timeout=a.timeout,
            defines=['-D__CPROVER__','-DACTOR_VERIFY','-DUINT16_MAX=65535u',f'-DMODE={NAMES.index(a.mode)}',f'-DPLATFORMS={a.platforms}',*(['-DSTONE_SEMANTIC'] if a.semantic else [])],
            extra=['--arrays-uf-always','--unwindset',loops+(',stone_project.0:1' if a.negative else '')])
        print(json.dumps({k:result[k] for k in ['result','seconds','failures']}),flush=True)
        if a.negative:assert result['result']=='FAIL' and any('unwind' in f[0] for f in result['failures'])
        else:assert result['result']=='PASS'
if __name__=='__main__':main()
