"""Reproducible compiled-C enumeration and CBMC for the three small closures."""
import argparse,json,re,subprocess,sys,time
from pathlib import Path
from closure_support import ROOT,compile_c,function,receipt,save,cbmc
OUT=ROOT/'build/workers/close-small'
UNITS={
    'far_copy':('game_services.c',['CopyFarBytes'],[]),
    'decimal':('render_primitives.c',['EncodeTwoDecimalDigits','EncodeFourDecimalDigits','EncodeSixDecimalDigits'],[]),
    'coordinate_scale':('render_primitives.c',['ScaleLevelYToThreeQuarters','ScaleLevelSpeedToThreeHalves'],['sar_word'])}

def pair(folder,units,bridges=True,overrides=None):
    folder.mkdir(parents=True,exist_ok=True)
    text=f'#include "{(ROOT/"c/ugh.h").as_posix()}"\n';inputs=[]
    for unit in units:
        module,names,helpers=UNITS[unit];p=ROOT/'c'/module;inputs.append(p);raw=p.read_text()
        body=''.join(function(raw,name) for name in helpers)
        body+=''.join(function(raw,'c_'+name) for name in names)
        for name in names:body=re.sub(r'\bc_'+name+r'\b','l1_'+name,body)
        text+=body
        p=Path((overrides or {}).get(unit,ROOT/'native'/f'{unit}.c'))
        inputs.extend([p,ROOT/'native'/f'{unit}.h'])
        text+=f'#include "{p.as_posix()}"\n'
        if bridges:
            p=ROOT/'native/bridge'/f'{unit}_bridge.c';inputs.append(p)
            text+=f'#include "{p.as_posix()}"\n'
    (folder/'pair.inc').write_text(text)
    inputs+=list((ROOT/'c').glob('*.h'))
    return inputs

def enumerate_units(mutants=False):
    folder=OUT/'enumeration';inputs=pair(folder,UNITS)
    harness=folder/'enumerate.c'
    harness.write_text('#include "pair.inc"\n'+(ROOT/'verif/small_enumeration.c').read_text())
    exe=folder/'enumerate.exe'
    build=compile_c([harness],exe,[ROOT/'c'],[])
    start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
    if run.returncode:raise RuntimeError(run.stdout+run.stderr)
    result=receipt(build['command'],[*inputs,ROOT/'verif/small_enumeration.c',Path(__file__)],
        compiler_sha256=build['compiler_sha256'],execution=[str(exe)],
        seconds=time.perf_counter()-start,result='PASS',counts=json.loads(run.stdout))
    if mutants:
        rows=[]
        for unit,old,new in [('far_copy','backwards ? 65535u : 1u','backwards ? 1u : 1u'),
                             ('coordinate_scale','value&32768u','value&0u'),
                             ('decimal','uint8_t digit=255','uint8_t digit=0')]:
            scratch=OUT/'mutants'/unit;scratch.mkdir(parents=True,exist_ok=True)
            raw=(ROOT/'native'/f'{unit}.c').read_text();assert raw.count(old)==1
            source=scratch/f'{unit}.c';source.write_text(raw.replace(old,new))
            mutant_inputs=pair(scratch,UNITS,overrides={unit:source})
            harness=scratch/'enumerate.c';harness.write_text('#include "pair.inc"\n'+(ROOT/'verif/small_enumeration.c').read_text())
            exe=scratch/'enumerate.exe';built=compile_c([harness],exe,[ROOT/'c',ROOT/'native'])
            execution=subprocess.run([str(exe)],capture_output=True,text=True)
            assert execution.returncode==23,(unit,execution.returncode)
            row=receipt(built['command'],mutant_inputs,unit=unit,detected=True,
                        returncode=execution.returncode,diagnostic=execution.stderr.strip())
            rows.append(row)
        result['mutants']=rows
    save(folder/'result.json',result);print(json.dumps({k:result[k] for k in ('result','seconds','counts')}),flush=True)
    return result

def prove(unit,unwind,timeout,negative=False,bound=20,kind=2,canonical=False,storage=64,exact=False):
    tag=f'_n{bound}_s{storage}'+('_exact' if exact else '') if unit=='far_copy' else f'_k{kind}'+('_canonical' if canonical else '_live') if unit=='decimal' else ''
    if unit=='far_copy' and canonical:tag+='_disjoint'
    folder=OUT/('cbmc_'+unit+tag+('_negative' if negative else ''))
    # Actual L1 functions and actual native C, with actual ugh.h arithmetic.
    inputs=pair(folder,[unit],bridges=unit=='coordinate_scale')
    harness=folder/'harness.c'
    harness.write_text('#include "pair.inc"\n'+(ROOT/'verif'/f'{unit}_cbmc.c').read_text())
    result=cbmc(harness,folder,[*inputs,ROOT/'verif'/f'{unit}_cbmc.c',Path(__file__)],
                unwind=unwind,timeout=timeout,extra=['--arrays-uf-always'],
                defines=[f'-DCOPY_BOUND={bound}',f'-DCOPY_STORAGE={storage}',f'-DCOPY_EXACT={int(exact)}',f'-DDECIMAL_KIND={kind}',f'-DCANONICAL={int(canonical)}'])
    print(json.dumps({k:result[k] for k in ('result','seconds','failures')}),flush=True)
    if negative:
        if result['result']!='FAIL' or not any('unwind' in x[0] for x in result['failures']):
            raise RuntimeError('negative control did not fail an unwinding assertion')
    elif result['result']!='PASS':raise RuntimeError(result['result'])
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['enumerate',*UNITS])
    p.add_argument('--unwind',type=int,default=24);p.add_argument('--timeout',type=int,default=120)
    p.add_argument('--negative',action='store_true');p.add_argument('--bound',type=int,default=20)
    p.add_argument('--kind',type=int,choices=[0,1,2],default=2);p.add_argument('--canonical',action='store_true')
    p.add_argument('--storage',type=int,choices=[64,65568],default=64);p.add_argument('--exact',action='store_true')
    p.add_argument('--mutants',action='store_true');a=p.parse_args()
    if a.mode=='enumerate':enumerate_units(a.mutants)
    else:prove(a.mode,a.unwind,a.timeout,a.negative,a.bound,a.kind,a.canonical,a.storage,a.exact)
