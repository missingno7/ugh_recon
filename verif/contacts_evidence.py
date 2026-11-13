"""Compiled actual-C contact enumeration and symbolic equivalence proofs."""
import argparse,json,subprocess,time
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save,cbmc
from contacts_build import OUT,pair

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['enumerate','prove'])
    p.add_argument('--kind',type=int,choices=range(4),default=0)
    p.add_argument('--count',type=int,default=2)
    p.add_argument('--timeout',type=int,default=45)
    p.add_argument('--pairs',action='store_true')
    p.add_argument('--mutant',action='store_true')
    p.add_argument('--negative',action='store_true')
    p.add_argument('--word-memory',action='store_true')
    p.add_argument('--bridge',action='store_true')
    p.add_argument('--case',type=int,choices=[0,1],default=0)
    a=p.parse_args()
    folder=OUT/('enumeration'+(f'_pairs_{a.kind}_{a.case}' if a.pairs else '')+('_mutant' if a.mutant else '') if a.mode=='enumerate' else f'cbmc_{a.kind}_{a.count}'+('_negative' if a.negative else '')+('_word' if a.word_memory else '')+('_bridge' if a.bridge else ''))
    inputs=pair(folder,bridges=a.mode=='enumerate' or a.bridge,word_memory=a.word_memory)
    harness=folder/'harness.c';source=ROOT/'verif'/('contacts_enumeration.c' if a.mode=='enumerate' else 'contacts_cbmc.c')
    harness.write_text('#include "pair.inc"\n'+source.read_text())
    if a.mutant:
        maintained=ROOT/'native/contacts.c';raw=maintained.read_text()
        old='if(signed_word(result.boundary)>signed_word(player.x32))'
        assert raw.count(old)==1
        mutant=folder/'contacts.c';mutant.write_text(raw.replace(old,'if(signed_word(result.boundary)>=signed_word(player.x32))'))
        inc=folder/'pair.inc';inc.write_text(inc.read_text().replace(maintained.as_posix(),mutant.as_posix()));inputs.append(mutant)
    if a.mode=='enumerate':
        exe=folder/'enumerate.exe';built=compile_c([harness],exe,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],[f'-DPAIRS={int(a.pairs)}',f'-DPAIR_KIND={a.kind}',f'-DPAIR_CASE={a.case}'])
        start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
        result=receipt(built['command'],[*inputs,source,Path(__file__),ROOT/'verif/contacts_build.py'],
            execution=[str(exe)],compiler_sha256=built['compiler_sha256'],seconds=time.perf_counter()-start,
            result='DETECTED' if a.mutant and run.returncode==23 else 'PASS' if run.returncode==0 else 'FAIL',stdout=run.stdout,stderr=run.stderr)
        save(folder/'result.json',result);print(json.dumps(result|{'inputs':'see receipt'}),flush=True)
        assert result['result']==('DETECTED' if a.mutant else 'PASS')
    else:
        result=cbmc(harness,folder,[*inputs,source,Path(__file__),ROOT/'verif/contacts_build.py'],
            unwind=1 if a.negative else max(8,a.count+2),timeout=a.timeout,
            defines=[f'-DKIND={a.kind}',f'-DSTONES={a.count}',f'-DBRIDGE={int(a.bridge)}'],extra=['--arrays-uf-always'] if a.word_memory else [])
        print(json.dumps({k:result[k] for k in ('result','seconds','failures')}),flush=True)
        if a.negative:assert result['result']=='FAIL' and any('unwind' in x[0] for x in result['failures'])
        else:assert result['result']=='PASS'

if __name__=='__main__':main()
