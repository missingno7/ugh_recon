"""Source-extracted exhaustive helper checks and bounded whole-decoder enumeration."""
import argparse,ctypes as C,hashlib,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import nbuild
from closure_support import checked_compile
OUT=ROOT/'build/workers/pilot-ice'

def extract():
    source=(ROOT/'c/ice.c').read_text()
    length=source[source.index('        uint16_t bp=3;'):source.index('        if(bx) {')]
    offset=source[source.index('        if(bx) {'):source.index('        uint16_t source=')]
    literal=source[source.index('            uint16_t dx=0;'):source.index('            do { wr8')]
    text='/* Mechanically extracted L1 statements; do not edit. */\n'
    for name,body,extra,end in [
        ('length',length,'','bx+2u'),
        ('offset',offset,',uint16_t bx','dx'),
        ('literal',literal+'\nunsigned n=0; do {++n; dx--;} while((int16_t)dx>=0);','','n')]:
        prefix='uint16_t bp=0,dx=0;' if name=='offset' else ''
        text+=f'static unsigned l1_{name}(Ice *state{extra}) {{ Ice c=*state; {prefix}\n{body}\n*state=c;return {end};\n}}\n'
    (OUT/'l1_tokens.inc').write_text(text)

def primitives(native=None):
    from emu import Machine
    extract();m=Machine();(OUT/'snapshot.bin').write_bytes(m.snapshot())
    sources=[ROOT/'verif/ice_primitives.c']+sorted(p for p in (ROOT/'c').glob('*.c') if p.name!='ice.c')
    exe=OUT/'primitives.exe'
    cmd=[str(nbuild.GCC),'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',str(ROOT/'c'),'-I',str(OUT),'-o',str(exe),*map(str,sources)]
    if native:cmd.insert(1,f'-DICE_IMPLEMENTATION="{Path(native).as_posix()}"')
    checked_compile(cmd)
    start=time.perf_counter();p=subprocess.run([str(exe),str(OUT/'snapshot.bin')],capture_output=True,text=True)
    if p.returncode:
        if native:return dict(exit_code=p.returncode,detected=True,seconds=time.perf_counter()-start)
        raise RuntimeError(f'primitive failure {p.returncode}: {p.stdout} {p.stderr}')
    return dict(counts=json.loads(p.stdout),seconds=time.perf_counter()-start,command=cmd)

def bounded(native=None,streams=None):
    # Fully enumerate this deliberately small finite initial-state family.
    # Guard both implementations after ONE outer iteration; inner loops remain
    # complete, including 16-bit cursor wrap. This is not a proof of termination
    # or equivalence for real-resource-sized streams.
    from difftest import Regs,MEM_SIZE
    from emu import Machine
    l1=(ROOT/'c/ice.c').read_text().replace('2000000','1')
    l2=Path(native or ROOT/'native/ice.c').read_text().replace('2000000u','1u')
    (OUT/'bounded_l1.c').write_text(l1.replace('c_UnpackIceStream','bounded_reference'))
    (OUT/'bounded_l2.c').write_text(l2.replace('#include "ice.h"',f'#include "{(ROOT/"native/ice.h").as_posix()}"'))
    sources=sorted(p for p in (ROOT/'c').glob('*.c') if p.name!='ice.c')
    sources += [OUT/'bounded_l1.c',OUT/'bounded_l2.c',ROOT/'native/bridge/ice_bridge.c']
    path=OUT/f'bounded_{os.getpid()}.dll'
    cmd=[str(nbuild.GCC),'-shared','-O2','-std=c11','-I',str(ROOT/'c'),'-o',str(path),*map(str,sources)]
    checked_compile(cmd)
    dll=nbuild.load_l1(path);mem=dll.ugh_memory().contents
    snapshot=Machine().snapshot();C.memmove(mem,snapshot,MEM_SIZE)
    dll.bounded_reference.argtypes=[C.POINTER(Regs)]
    dll.c_UnpackIceStream.argtypes=[C.POINTER(Regs)]
    start=time.perf_counter();count=0;outcomes={}
    cases=[(output,payload,b'ICE!'+(13).to_bytes(4,'big')+output.to_bytes(4,'big')+bytes([payload]))
           for output in range(5) for payload in range(256)]
    cases += [('mutation',i,stream) for i,stream in enumerate(streams or [])]
    for output,payload,stream in cases:
            initial=Regs(ax=1,bx=2,cx=3,dx=4,si=0,di=0xbeef,bp=5,ds=0x5000,es=0x7000,flags=0xed7)
            observations=[]
            for function in (dll.bounded_reference,dll.c_UnpackIceStream):
                C.memset(C.addressof(mem)+0x50000,0,65536)
                C.memmove(C.addressof(mem)+0x50000,stream,len(stream))
                C.memset(C.addressof(mem)+0x70000,0,65536)
                r=Regs.from_buffer_copy(initial);status=function(C.byref(r))
                observations.append((status,bytes(r),bytes(mem[0x70000:0x80000])))
            if observations[0]!=observations[1]:
                if native:return dict(detected=True,output=output,payload=payload,cases_before=count,seconds=time.perf_counter()-start)
                raise AssertionError((output,payload,observations[0][:2],observations[1][:2]))
            status=observations[0][0];outcomes[status]=outcomes.get(status,0)+1;count+=1
    return dict(cases=count,outcomes=outcomes,seconds=time.perf_counter()-start,
                bounds='packed=13, payload=one arbitrary byte, output low word=0..4, other source/output bytes zero; one full outer iteration',
                additional_mutations=len(streams or []),
                solver_seconds=None,method='complete finite enumeration of the compiled C pair; no solver',command=cmd)

def main():
    global OUT
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--native')
    parser.add_argument('--out',type=Path,help='isolate receipts and generated files from the historical pilot run')
    args=parser.parse_args()
    if args.out:OUT=args.out.resolve()
    OUT.mkdir(parents=True,exist_ok=True)
    result=dict(primitives=primitives(args.native),bounded=bounded(args.native))
    result['inputs']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                      [ROOT/'c/ice.c',ROOT/'native/ice.c',ROOT/'verif/ice_primitives.c',Path(__file__),ROOT/'verif/closure_support.py']}
    name='exhaustive.json' if not args.native else Path(args.native).stem+'_evidence.json'
    (OUT/name).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
