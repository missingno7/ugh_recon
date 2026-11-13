"""Finite scalar enumeration and actual-C one-step passenger delivery checks."""
import argparse,json,subprocess,time
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save
from delivery_limits import cbmc
from delivery_build import OUT,NAMES,pair
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['enumerate',*NAMES]);p.add_argument('--timeout',type=int,default=300);p.add_argument('--negative',action='store_true');p.add_argument('--tag',default='current');p.add_argument('--compact',action='store_true',help='Exact bit-vector arrays without eager array field expansion');a=p.parse_args()
    folder=OUT/'evidence'/(a.mode+'_'+a.tag+('_negative' if a.negative else ''));inputs=pair(folder)
    source=ROOT/'verif/delivery_harness.c';harness=folder/'harness.c';harness.write_text('#include "pair.inc"\n'+source.read_text())
    inputs += [source,Path(__file__),*sorted((ROOT/'native').rglob('*.h'))]
    if a.mode=='enumerate':
        exe=folder/'enumerate.exe';built=compile_c([harness],exe,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-DACTOR_VERIFY'])
        start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
        save(folder/'result.json',receipt(built['command'],inputs,execution=[str(exe)],compiler_sha256=built['compiler_sha256'],seconds=time.perf_counter()-start,result='PASS' if not run.returncode else 'FAIL',stdout=run.stdout,stderr=run.stderr))
        print(run.stdout+run.stderr,flush=True);assert not run.returncode
    else:
        loops='dl_ref0_contact.0:3,dl_ref1_frame.0:3,dl_ref1_platform_player.0:3,pd_shell1_frame.0:3,pd_shell1_platform_player.0:3,delivery_vector.0:4'
        if a.negative:loops+=',delivery_prepare.0:1'
        extra=['--unwindset',loops]
        if a.compact:extra+=['--no-array-field-sensitivity','--arrays-uf-never']
        result=cbmc(harness,folder,inputs,unwind=40,timeout=a.timeout,defines=['-D__CPROVER__','-DACTOR_VERIFY','-DUINT16_MAX=65535u',f'-DMODE={NAMES.index(a.mode)}'],extra=extra)
        print(json.dumps({k:result[k] for k in ['result','seconds','failures']}),flush=True)
        if a.negative:assert result['result']=='FAIL' and any(row[0]=='delivery_prepare.unwind.0' for row in result['failures'])
        else:assert result['result']=='PASS'
if __name__=='__main__':main()
