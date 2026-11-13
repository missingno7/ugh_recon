"""Finite enumeration and CBMC relational item transitions on maintained C."""
import argparse,json,subprocess,time
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save,cbmc
from items_build import OUT,pair,NATIVE

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['enumerate','spawn','flight','land','collect','dispatch','dispatch-selection'])
    p.add_argument('--platforms',type=int,choices=range(11),default=1);p.add_argument('--timeout',type=int,default=60)
    p.add_argument('--negative',action='store_true');a=p.parse_args()
    folder=OUT/(a.mode+f'_{a.platforms}'+('_negative' if a.negative else ''));inputs=pair(folder)
    source=ROOT/'verif/items_harness.c';harness=folder/'harness.c';harness.write_text('#include "pair.inc"\n'+source.read_text())
    inputs+=[NATIVE[-1],source,Path(__file__),ROOT/'verif/items_build.py']
    if a.mode=='enumerate':
        exe=folder/'enumerate.exe';built=compile_c([harness],exe,[ROOT/'c',ROOT/'native'])
        start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
        result=receipt(built['command'],inputs,execution=[str(exe)],compiler_sha256=built['compiler_sha256'],
            seconds=time.perf_counter()-start,result='PASS' if run.returncode==0 else 'FAIL',stdout=run.stdout,stderr=run.stderr)
        save(folder/'result.json',result);print(run.stdout+run.stderr,flush=True);assert result['result']=='PASS'
    else:
        result=cbmc(harness,folder,inputs,unwind=1 if a.negative else 13 if a.mode=='dispatch-selection' else 25,timeout=a.timeout,
            defines=['-D__CPROVER__',f'-DMODE={dict(spawn=0,flight=1,land=2,collect=3,dispatch=4,**{"dispatch-selection":5})[a.mode]}',f'-DPLATFORMS={a.platforms}'],
            extra=['--arrays-uf-always'])
        print(json.dumps({k:result[k] for k in ['result','seconds','failures']}),flush=True)
        if a.negative:assert result['result']=='FAIL' and any('unwind' in f[0] for f in result['failures'])
        else:assert result['result']=='PASS'

if __name__=='__main__':main()
