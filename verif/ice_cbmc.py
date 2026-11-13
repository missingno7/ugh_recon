"""CBMC on actual ICE C, preprocessed with minimal Windows-compatible headers."""
import argparse,hashlib,json,re,subprocess,time
from pathlib import Path
from windows_job import WindowsJob
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/workers/pilot-ice-2'
GCC=Path('C:/msys64/mingw64/bin/gcc.exe')

def prepare(folder,native=None,mode='whole'):
    folder.mkdir(parents=True,exist_ok=True)
    l1=(ROOT/'c/ice.c').read_text().replace('#include "ugh.h"','#include <ugh.h>')
    # A pure ghost count does not change any data/control decisions of L1.
    l1=l1.replace('if(!c.budget--)','++l1_tokens; if(!c.budget--)')
    (folder/'l1.c').write_text(l1)
    asm=(ROOT/'src/asm/GAME.ASM').read_text()
    data=asm.split('IceDecoderTables:',1)[1].split('; CONTRACT',1)[0]
    values=[]
    for line in data.splitlines():
        if not line.strip().startswith('db '):continue
        for x in line.split('db ',1)[1].split(';')[0].split(','):
            x=x.strip();values.append(int(x[:-1],16) if x.lower().endswith('h') else int(x))
    assert len(values)==60
    symbols=(ROOT/'c/ugh_sym.h').read_text();macros=[]
    for name in ('IceLiteralCodeTablePivot','IceMatchLengthBitCountsMinusOne','IceMatchLengthBiases','IceMatchOffsetBitCountsMinusOne','IceMatchOffsetBiases'):
        value=re.search(r'#define UGH_O_GAME_'+name+r' (\S+)',symbols)[1]
        macros.append(f'#define ICE_O_{name} {value}')
    (folder/'tables.h').write_text('\n'.join(macros)+'\nstatic const unsigned char ice_table[60]={'+','.join(map(str,values))+'};\n')
    # Forward declarations/variables precede the real implementations.
    harness=(ROOT/'verif/ice_cbmc_whole.c').read_text()
    split=harness.index('int main(void)')
    prefix=harness[:split];main=harness[split:]
    text='#include <ugh.h>\n#include "tables.h"\n'+prefix
    text+=f'\n#include "{(folder/"l1.c").as_posix()}"\n'
    text+=f'\n#include "{Path(native or ROOT/"native/ice.c").as_posix()}"\n'
    if mode!='whole':
        raw=(ROOT/'c/ice.c').read_text();modern=Path(native or ROOT/'native/ice.c').read_text()
        length=raw[raw.index('        uint16_t bp=3;'):raw.index('        if(bx) {')]
        offset=raw[raw.index('        if(bx) {'):raw.index('        uint16_t source=')]
        literal=raw[raw.index('            uint16_t dx=0;'):raw.index('            do { wr8')]
        helpers=''
        for name,body,args,extra,result in [('length',length,'','','bx+2u'),
            ('offset',offset,',uint16_t bx','uint16_t bp=0,dx=0;','dx'),
            ('literal_code',literal,'','','dx')]:
            helpers+=f'static unsigned l1_{name}(Ice *state{args}) {{ Ice c=*state; {extra}\n{body}\n*state=c;return {result};\n}}\n'
        text+=helpers
        if mode=='init':
            old_prefix=raw[raw.index('{',raw.index('EXPORT int c_UnpackIceStream'))+1:raw.index('    for(;;)')]
            new_prefix=modern[modern.index('{',modern.index('IceStatus ice_decode'))+1:modern.index('    for (unsigned token=')]
            text+='static int l1_init(Regs *r,Ice *state) {\n'+old_prefix+'\n*state=c;return 1;}\n'
            text+='static IceStatus native_init(const uint8_t *source,size_t source_size,IceResult *result,BitReader *state,size_t *destination) {\n'+new_prefix+'\n*state=reader;*destination=cursor;return status;}\n'
            main=(ROOT/'verif/ice_cbmc_init.c').read_text()
        elif mode=='step':
            old_body=raw[raw.index('        if(next_bit(&c)) {'):raw.index('\n    }\n    r->si=c.si;')]
            old_body=old_body.replace('if(c.di==65535) break;','if(c.di==65535) {done=1;break;}')
            new_body=modern[modern.index('        if (take_bit(&reader)) {'):modern.index('\n    }\n    result->source_cursor=reader.cursor;')]
            new_body=new_body.replace('if (cursor==65535u) break;','if (cursor==65535u) { *done=1;break;}')
            text+='static int l1_step(Ice *state) {Ice c=*state;int done=0;do {\n'+old_body+'\n}while(0);*state=c;return done;}\n'
            text+='static IceStatus native_step(BitReader *state,uint8_t *output,size_t *destination,int *done) { BitReader reader=*state;size_t cursor=*destination,output_size=OUTPUT_SIZE;IceStatus status=ICE_OK;IceResult local={0};IceResult *result=&local;do {\n'+new_body+'\n}while(0);*state=reader;*destination=cursor;return status;}\n'
            main=(ROOT/'verif/ice_cbmc_step.c').read_text()
        else:main=(ROOT/'verif/ice_cbmc_primitive.c').read_text()
    text+=main
    (folder/'whole.c').write_text(text)

def run(stream,output,unwind,timeout=120,native=None,tag='whole',backend='sat',mode='whole',coverage=False):
    if not (1<=stream<=65536 and 1<=output<=65536 and unwind>=1):raise ValueError('invalid bounds')
    if mode in ('whole','init') and (stream<12 or output==65536):raise ValueError('whole/init proof needs a header and output storage below 65536 (non-wrapping write progress)')
    manifest=json.loads((ROOT/'metadata/verif-tools.json').read_text())
    cbmc=Path(manifest['cbmc']['exe'])
    if hashlib.sha256(cbmc.read_bytes()).hexdigest()!=manifest['cbmc']['exe_sha256']:raise RuntimeError('CBMC hash differs from manifest')
    folder=OUT/f'{tag}_{mode}_s{stream}_o{output}_u{unwind}';prepare(folder,native,mode)
    primitives=['reader','bits','literal','length','offset']
    cmd=[str(GCC),'-E','-P','-nostdinc','-I'+str(ROOT/'verif/cbmc_shim'),'-I'+str(ROOT/'native'),
         f'-DSTREAM_SIZE={stream}',f'-DOUTPUT_SIZE={output}',f'-DTOKEN_BOUND={output//2+1}',
         f'-DPRIMITIVE={primitives.index(mode) if mode in primitives else 0}',
         f'-DCOVER_RUN={int(coverage)}',
         str(folder/'whole.c'),'-o',str(folder/'whole.i')]
    p=subprocess.run(cmd,capture_output=True,text=True);(folder/'preprocess.log').write_text(p.stdout+p.stderr)
    if p.returncode:raise RuntimeError(p.stderr)
    loops={'main.0':stream+1,'main.1':output+1,'main.2':output+1,'read_bits.0':16,
        'c_UnpackIceStream.0':6,'c_UnpackIceStream.1':output+2,'c_UnpackIceStream.2':5,
        'c_UnpackIceStream.3':3,'c_UnpackIceStream.4':output+2,'c_UnpackIceStream.5':output//2+2,
        'ice_decode.0':output+2,'ice_decode.1':output+2,'ice_decode.2':output//2+2,
        'take_bits.0':16,'literal_length.0':6,'match_length.0':5}
    if mode!='whole':
        loops={k:v for k,v in loops.items() if not k.startswith(('main.','c_UnpackIceStream.','ice_decode.'))}
        loops.update({'l1_length.0':5,'l1_offset.0':3,'l1_literal_code.0':6})
    if mode=='step':
        loops.update({'l1_step.0':6,'l1_step.1':output+2,'l1_step.2':5,'l1_step.3':3,
                      'l1_step.4':output+2,'native_step.0':output+2,'native_step.1':output+2})
    loops={k:min(v,unwind) for k,v in loops.items()}
    command=[str(cbmc),str(folder/'whole.i'),'--unwind',str(unwind),
             '--unwindset',','.join(f'{k}:{v}' for k,v in loops.items()),'--unwinding-assertions',
             '--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula','--trace','--verbosity','8']
    if backend=='z3':
        install=Path(re.search(r'[A-Za-z]:[/\\]\S+',manifest['z3']['install'])[0])
        z3exe=next(install.rglob('z3.exe'))
        command+=['--z3','--external-smt2-solver',str(z3exe)]
    if stream>256:command+=['--arrays-uf-always']
    start=time.perf_counter()
    with WindowsJob() as job,(folder/'cbmc.log').open('w') as log:
        p=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
        job.assign(p)
        try:
            code=p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            # CBMC's external solver is a child process. Kill the entire owned
            # tree, including it, rather than leaving an orphan after timeout.
            job.terminate()
            p.wait();code=None
    elapsed=time.perf_counter()-start;log=(folder/'cbmc.log').read_text()
    failures=re.findall(r'^\[([^]]+)\] (.*): FAILURE$',log,re.M)
    witnesses=[(name,description) for name,description in failures if 'witness:' in description]
    result=dict(stream_size=stream,output_size=output,token_bound=output//2+1,unwind=unwind,seconds=elapsed,
        result='TIMEOUT' if code is None else 'WITNESSED' if coverage and len(witnesses)==4 and len(failures)==4 else 'PASS' if code==0 and 'VERIFICATION SUCCESSFUL' in log else 'FAIL' if code==10 and failures else 'ERROR',
        returncode=code,preprocess=cmd,command=command,tools=manifest,loop_unwinds=loops,backend=backend,mode=mode,
        solver_times=re.findall(r'Runtime Solver: ([^\n]+)',log),
        decision_times=re.findall(r'Runtime decision procedure: ([^\n]+)',log),failures=failures,witnesses=witnesses,
        preprocessed_sha256=hashlib.sha256((folder/'whole.i').read_bytes()).hexdigest(),
        inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                [ROOT/'c/ice.c',Path(native or ROOT/'native/ice.c'),ROOT/'native/ice.h',Path(__file__),ROOT/'verif/windows_job.py',*sorted((ROOT/'verif').glob('ice_cbmc_*.c')),*sorted((ROOT/'verif/cbmc_shim').glob('*.h'))]})
    (folder/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('result','stream_size','output_size','token_bound','unwind','seconds','solver_times')}),flush=True)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stream',type=int,default=16);parser.add_argument('--output',type=int,default=2)
    parser.add_argument('--unwind',type=int,default=17);parser.add_argument('--timeout',type=int,default=120)
    parser.add_argument('--native',type=Path);parser.add_argument('--tag',default='whole')
    parser.add_argument('--backend',choices=['sat','z3'],default='sat')
    parser.add_argument('--mode',choices=['whole','init','step','reader','bits','literal','length','offset'],default='whole')
    parser.add_argument('--coverage',action='store_true')
    a=parser.parse_args();r=run(a.stream,a.output,a.unwind,a.timeout,a.native,a.tag,a.backend,a.mode,a.coverage)
    raise SystemExit(0 if r['result'] in ('PASS','WITNESSED') else 1)
