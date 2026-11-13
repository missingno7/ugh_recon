"""Actual-C symbolic proof, finite compiled families and semantic controls."""
import argparse,json,re,subprocess,time
from pathlib import Path
from closure_support import ROOT,function,compile_c,cbmc,receipt,save,digest
OUT=ROOT/'build/workers/close-random'
NAMES=['NextRandomBelowAx','SeedRandomFromDosSeconds']

def pair(folder,mutation=None,cutpoints=False):
    folder.mkdir(parents=True,exist_ok=True)
    inputs=[ROOT/'c/dos_input.c',ROOT/'native/random.c',ROOT/'native/random.h',
            ROOT/'native/bridge/random_bridge.c',*sorted((ROOT/'c').glob('*.h'))]
    text=f'#include "{(ROOT/"c/platform.h").as_posix()}"\n'
    raw=inputs[0].read_text()
    if cutpoints:
        text+='void __CPROVER_assert(_Bool,const char *);\nstatic uint16_t proof_first,proof_bound;static unsigned proof_seen;\n'
    for name in NAMES:
        body=function(raw,'c_'+name).replace('c_'+name,'l1_'+name)
        if cutpoints and name=='NextRandomBelowAx':
            point='uint32_t product=(uint32_t)a*bound;';assert body.count(point)==1
            body=body.replace(point,'__CPROVER_assert(a==proof_first && bound==proof_bound,"L1 final-word cutpoint");\nuint32_t product=(uint32_t)proof_first*proof_bound;')
        text+=body
    native=inputs[1]
    if mutation or cutpoints:
        raw=native.read_text()
        if mutation:
            old,new=mutation;assert raw.count(old)==1;raw=raw.replace(old,new)
        if cutpoints:
            point='return (uint16_t)(((uint32_t)state->word[0]*bound)>>16);';assert raw.count(point)==1
            raw=raw.replace(point,'if(proof_seen) {\n__CPROVER_assert(state->word[0]==proof_first && bound==proof_bound,"native final-word cutpoint");\n} else {proof_first=state->word[0];proof_bound=bound;proof_seen=1;}\nreturn (uint16_t)(((uint32_t)proof_first*proof_bound)>>16);')
        native=folder/'native_proof.c';native.write_text(raw.replace(
            '#include "random.h"','#include "'+(ROOT/'native/random.h').as_posix()+'"'))
        inputs.append(native)
    for p in [native,inputs[3]]:text+=f'#include "{p.as_posix()}"\n'
    (folder/'pair.inc').write_text(text)
    return inputs

def prove(mode,timeout,negative=False,direct=False,backend=None):
    backend=backend or ('sat' if mode=='next' else 'smt')
    folder=OUT/('cbmc_'+mode+('_direct_'+backend if direct else '')+('_negative' if negative else ''))
    inputs=pair(folder,cutpoints=mode=='next' and not direct)
    if negative:
        inputs=pair(folder,('sum=(uint32_t)state->word[1]+first+(sum>>16);',
                            'sum=(uint32_t)state->word[1]+first;'),cutpoints=mode=='next' and not direct)
    h=folder/'harness.c';h.write_text('#include "pair.inc"\n'+(ROOT/'verif/random_cbmc.c').read_text())
    solver=None;extra=[]
    if backend=='smt':
        solver=Path('C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe')
        assert digest(solver)=='3d51a3aacb54506245e205759ee553ac358f1e4b64eccbd056125b685b26b780'
        extra=['--smt2','--z3','--external-smt2-solver',str(solver)]
    elif backend=='refine':extra=['--refine-arithmetic']
    result=cbmc(h,folder,[*inputs,Path(__file__),ROOT/'verif/random_cbmc.c'],unwind=16,
        timeout=timeout,defines=[f'-DRANDOM_SEED={int(mode=="seed")}'],
        extra=extra)
    if solver:result['solver_sha256']=digest(solver)
    result['checked_cutpoints']=mode=='next' and not direct
    save(folder/'result.json',result)
    print(json.dumps({k:result[k] for k in ('result','seconds','failures')}),flush=True)
    if negative:
        assert result['result']=='FAIL' and any('cutpoint' in row[1] or 'native/L1' in row[1] for row in result['failures']),result
    else:assert result['result']=='PASS',result['result']

def enumerate_cases(mutants):
    folder=OUT/'enumeration';inputs=pair(folder)
    h=folder/'enumerate.c';h.write_text('#include "pair.inc"\n'+(ROOT/'verif/random_enumeration.c').read_text())
    exe=folder/'enumerate.exe';built=compile_c([h],exe,[ROOT/'c'])
    start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
    assert run.returncode==0,run.stdout+run.stderr
    result=receipt(built['command'],[*inputs,Path(__file__),ROOT/'verif/random_enumeration.c'],
        result='PASS',counts=json.loads(run.stdout),seconds=time.perf_counter()-start,
        compiler_sha256=built['compiler_sha256'])
    if mutants:
        rows=[]
        for name,old,new in [
            ('carry','sum=(uint32_t)state->word[1]+first+(sum>>16);','sum=(uint32_t)state->word[1]+first;'),
            ('bound-feedback','uint32_t sum=(uint32_t)bound+state->word[0];','uint32_t sum=state->word[0];'),
            ('modulo','((uint32_t)state->word[0]*bound)>>16','bound ? state->word[0]%bound : 0'),
            ('seed-clobber','(state->word[0]&255u)','0u')]:
            scratch=OUT/'mutants'/name;ins=pair(scratch,(old,new));target=scratch/'enumerate.exe'
            harness=scratch/'enumerate.c';harness.write_text(h.read_text())
            b=compile_c([harness],target,[ROOT/'c']);r=subprocess.run([str(target)],capture_output=True,text=True)
            assert r.returncode==23,(name,r.returncode,r.stderr)
            rows.append(receipt(b['command'],ins,mutation=name,result='DETECTED',diagnostic=r.stderr.strip()))
        result['mutants']=rows
    save(folder/'result.json',result);print(json.dumps({k:result[k] for k in ('result','counts','seconds')}),flush=True)

def reduction():
    folder=OUT/'reduction';folder.mkdir(parents=True,exist_ok=True)
    # Extract the production final expression verbatim; the input state word is
    # arbitrary here, independently of how the recurrence produced it.
    raw=(ROOT/'native/random.c').read_text()
    expression=re.search(r'    return \(uint16_t\)\(\(\(uint32_t\)state->word\[0\]\*bound\)>>16\);',raw)
    assert expression
    source=folder/'reduce.c'
    source.write_text('#include "'+(ROOT/'native/random.h').as_posix()+'"\n'
        +'uint16_t tested_reduce(RandomState *state,uint16_t bound) {\n'+expression[0]+'\n}\n')
    h=ROOT/'verif/random_reduction.c';exe=folder/'reduce.exe'
    built=compile_c([source,h],exe,[ROOT/'native'])
    start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
    assert run.returncode==0,run.stdout+run.stderr
    result=receipt(built['command'],[source,h,ROOT/'native/random.c',ROOT/'native/random.h',Path(__file__)],
        compiler_sha256=built['compiler_sha256'],result='PASS',counts=json.loads(run.stdout),seconds=time.perf_counter()-start)
    save(folder/'result.json',result);print(json.dumps({k:result[k] for k in ('result','counts','seconds')}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['next','seed','enumerate','reduction'])
    p.add_argument('--timeout',type=int,default=60);p.add_argument('--negative',action='store_true')
    p.add_argument('--mutants',action='store_true');p.add_argument('--direct',action='store_true')
    p.add_argument('--backend',choices=['sat','smt','refine']);a=p.parse_args()
    if a.mode=='reduction':reduction()
    elif a.mode=='enumerate':enumerate_cases(a.mutants)
    else:prove(a.mode,a.timeout,a.negative,a.direct,a.backend)
