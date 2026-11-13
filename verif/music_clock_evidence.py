"""Actual L0 C / L1 / native checks; no handwritten arithmetic reference replaces C."""
import argparse,json,re,subprocess,time,sys
from pathlib import Path
from closure_support import ROOT,function,compile_c,cbmc,receipt,save,digest
from music_clock_build import OUT,NAMES

def original_match():
    sys.path.insert(0,str(ROOT/'tools'))
    import cjudge
    from common import MZ,sha256
    raw=(ROOT/'build/oracle/UGH_X.EXE').read_bytes()
    lock=json.loads((ROOT/'metadata/oracle.json').read_text())
    assert sha256(raw)==lock['expanded']['file_sha256']
    inventory=json.loads((ROOT/'src/c/inventory.json').read_text())
    rows=cjudge.compare(ROOT/'src/c/module.c',inventory,MZ(raw),dest=OUT/'l0',verbose=False)
    assert len(rows)==23 and all(r['exact'] and r['ordered_relocations_exact'] for r in rows.values())
    save(OUT/'l0.json',receipt(['python','verif/music_clock_evidence.py','l0'],
        [ROOT/'src/c/module.c',ROOT/'src/c/inventory.json',ROOT/'tools/cjudge.py',
         ROOT/'metadata/toolchain-lock.json',ROOT/'metadata/oracle.json',Path(__file__)],
        result='PASS',functions=rows,expanded_sha256=sha256(raw)))
    print('PASS: 23/23 original C functions, 7074 bytes; ordered TU relocations exact',flush=True)

def pair(folder):
    folder.mkdir(parents=True,exist_ok=True)
    inputs=[ROOT/'c/music_clock.c',ROOT/'src/c/module.c',ROOT/'native/music_clock.c',
            ROOT/'native/music_clock.h',ROOT/'native/bridge/music_clock_bridge.c',
            *sorted((ROOT/'c').glob('*.h'))]
    text=f'#include "{(ROOT/"c/ugh.h").as_posix()}"\n'
    raw=inputs[0].read_text()
    for name in NAMES:
        text+=function(raw,'c_'+name).replace('c_'+name,'l1_'+name)
    # Only historical widths and function names change. Borland unsigned long is
    # 32 bits, unsigned/int are 16 bits. The original byte-addressed swap body is
    # included, not replaced by a shift formula. Both tools target little endian.
    text+='uint32_t AdlxTickCount,MainAdlxTimeOrigin;\nuint16_t MusicTicksPerUnit,MainAdlxPlaying,MainAdlxSectionLoopEnabled;\n'
    raw=(ROOT/'src/c/module.c').read_text()
    for name in NAMES:
        body=function(raw,name).replace(name,'original_'+name)
        body=body.replace('unsigned long','uint32_t').replace(
            'int original_DisableMusicSectionLoop','int16_t original_DisableMusicSectionLoop')
        text+=body
    for p in inputs[2:3]+inputs[4:5]:text+=f'#include "{p.as_posix()}"\n'
    (folder/'pair.inc').write_text(text)
    return inputs

def prove(mode,timeout,negative=False):
    folder=OUT/f'cbmc_{mode}'
    if mode.startswith('elapsed'):folder=OUT/f'cbmc_{mode}_smt'
    if negative:folder=folder.with_name(folder.name+'_negative')
    inputs=pair(folder)
    if negative:
        assert mode=='elapsed','negative proof control is elapsed arithmetic only'
        source=folder/'music_clock_mutant.c'
        raw=(ROOT/'native/music_clock.c').read_text()
        old='(uint32_t)(ticks - origin) / rate';assert raw.count(old)==1
        source.write_text(raw.replace(old,'ticks / rate - origin / rate').replace(
            '#include "music_clock.h"','#include "'+(ROOT/'native/music_clock.h').as_posix()+'"'))
        inc=folder/'pair.inc';inc.write_text(inc.read_text().replace((ROOT/'native/music_clock.c').as_posix(),source.as_posix()))
        inputs.append(source)
    harness=folder/'harness.c'
    harness.write_text('#include "pair.inc"\n'+(ROOT/'verif/music_clock_cbmc.c').read_text())
    extra=[];solver=None
    if mode.startswith('elapsed'):
        solver=Path('C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe')
        # Same executable as the wheel locked in metadata/verif-tools.json.
        if digest(solver)!='3d51a3aacb54506245e205759ee553ac358f1e4b64eccbd056125b685b26b780':
            raise RuntimeError('Z3 executable hash drift')
        extra=['--smt2','--z3','--external-smt2-solver',str(solver)]
    result=cbmc(harness,folder,[*inputs,Path(__file__),ROOT/'verif/music_clock_cbmc.c'],
                unwind=40,timeout=timeout,defines=[f'-DMUSIC_MODE={dict(swap=0,disable=1,elapsed_bridge=2,elapsed=3)[mode]}'],
                extra=extra)
    if solver:
        result['solver_sha256']=digest(solver);save(folder/'result.json',result)
    print(json.dumps({k:result[k] for k in ('result','seconds','failures')}),flush=True)
    if negative:
        if result['result']!='FAIL' or not any('assertion.2' in row[0] for row in result['failures']):
            raise RuntimeError('semantic negative control did not fail the arithmetic assertion')
    elif result['result']!='PASS':raise RuntimeError(result['result'])

def enumerate_cases(mutants=False):
    folder=OUT/'enumeration';inputs=pair(folder)
    harness=folder/'enumerate.c'
    harness.write_text('#include "pair.inc"\n'+(ROOT/'verif/music_clock_enumeration.c').read_text())
    exe=folder/'enumerate.exe';built=compile_c([harness],exe,[ROOT/'c'])
    start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
    if run.returncode:raise RuntimeError(run.stdout+run.stderr)
    result=receipt(built['command'],[*inputs,Path(__file__),ROOT/'verif/music_clock_enumeration.c'],
        compiler_sha256=built['compiler_sha256'],execution=[str(exe)],seconds=time.perf_counter()-start,
        result='PASS',counts=json.loads(run.stdout))
    if mutants:
        rows=[]
        for label,old,new in [
            ('swap-byte','value >> 24','value >> 16'),
            ('playing-bit','return playing ?','return (playing & 1) ?'),
            ('wrap-order','(uint32_t)(ticks - origin) / rate','ticks / rate - origin / rate'),
            ('zero-rate','MUSIC_CLOCK_DIVIDE_BY_ZERO, 0','MUSIC_CLOCK_OK, 0')]:
            scratch=OUT/'mutants'/label;mutant_inputs=pair(scratch)
            p=scratch/'music_clock.c';raw=(ROOT/'native/music_clock.c').read_text()
            assert raw.count(old)==1
            p.write_text(raw.replace(old,new).replace('#include "music_clock.h"',
                '#include "'+(ROOT/'native/music_clock.h').as_posix()+'"'))
            inc=scratch/'pair.inc';inc.write_text(inc.read_text().replace((ROOT/'native/music_clock.c').as_posix(),p.as_posix()))
            h=scratch/'enumerate.c';h.write_text(harness.read_text())
            target=scratch/'enumerate.exe';b=compile_c([h],target,[ROOT/'c',ROOT/'native'])
            r=subprocess.run([str(target)],capture_output=True,text=True)
            assert r.returncode==23,(label,r.returncode,r.stderr)
            rows.append(receipt(b['command'],[*mutant_inputs,p],mutation=label,result='DETECTED',diagnostic=r.stderr.strip()))
        result['mutants']=rows
    save(folder/'result.json',result)
    print(json.dumps({k:result[k] for k in ('result','seconds','counts')}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['enumerate','swap','disable','elapsed','elapsed_bridge','l0'])
    p.add_argument('--timeout',type=int,default=60);p.add_argument('--mutants',action='store_true')
    p.add_argument('--negative',action='store_true');a=p.parse_args()
    if a.mode=='l0':original_match()
    elif a.mode=='enumerate':enumerate_cases(a.mutants)
    else:prove(a.mode,a.timeout,a.negative)
