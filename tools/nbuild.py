"""Build native library, or an L1 variant without editing/generated writes in c/."""
import argparse, ctypes as C, hashlib, json, os, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GCC=Path(r'C:\msys64\mingw64\bin\gcc.exe')
OUT=ROOT/'build/native'
import sys
sys.path.insert(0,str(ROOT/'verif'))
from closure_support import checked_compile,hashes

COMPONENTS={
    'ice':('ice.c',['UnpackIceStream']),
    'far_copy':('game_services.c',['CopyFarBytes']),
    'decimal':('render_primitives.c',['EncodeTwoDecimalDigits','EncodeFourDecimalDigits','EncodeSixDecimalDigits']),
    'coordinate_scale':('render_primitives.c',['ScaleLevelYToThreeQuarters','ScaleLevelSpeedToThreeHalves'])}

def build(kind='native', source=None, tag='', components=None):
    OUT.mkdir(parents=True,exist_ok=True)
    components=list(components or ['ice'])
    for name in components:
        if name not in COMPONENTS:raise ValueError('unknown component '+name)
    if source and components!=['ice']:raise ValueError('source override is ICE-only')
    natives=[Path(source) if source else ROOT/'native'/f'{name}.c' for name in components]
    sources=[]; originals=[]
    if kind=='native':sources=natives
    else:
        folder=OUT/f'sources{tag}_{os.getpid()}';folder.mkdir(exist_ok=True)
        for p in sorted((ROOT/'c').glob('*.c')):
            names=[symbol for name in components for module,symbols in [COMPONENTS[name]]
                   if module==p.name for symbol in symbols] if kind=='bridge' else []
            if names:
                # Keep the actual L1 functions available as l1_* for enumeration.
                # Other modules dispatch to the original symbol, now the bridge.
                import re
                text=p.read_text()
                for name in names:text=re.sub(r'\bc_'+name+r'\b','l1_'+name,text)
                generated=folder/p.name;generated.write_text(text);sources.append(generated);originals.append(p)
            else:sources.append(p)
        if kind=='bridge':sources+=natives+[ROOT/'native/bridge'/f'{name}_bridge.c' for name in components]
    path=OUT/f'{kind}{tag}_{os.getpid()}.dll'
    cmd=[str(GCC),'-shared','-O2','-std=c11','-Wall','-Wextra','-Werror','-fwrapv',
         '-I',str(ROOT/'c'),'-I',str(ROOT/'native'),'-o',str(path),*map(str,sources)]
    env=dict(os.environ,PATH=str(GCC.parent)+os.pathsep+os.environ.get('PATH',''))
    p=checked_compile(cmd)
    (OUT/f'{kind}{tag}.log').write_text(p.stdout+p.stderr)
    if p.returncode: raise RuntimeError(p.stdout+p.stderr)
    inputs=sources+list((ROOT/'native').rglob('*.h'))
    if kind!='native': inputs+=list((ROOT/'c').glob('*.h'))+list((ROOT/'c').glob('*.inc'))
    receipt=dict(command=cmd,components=components,compiler_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),
                 inputs=hashes(inputs+originals+[ROOT/'tools/nbuild.py',ROOT/'verif/closure_support.py']))
    (OUT/f'{kind}{tag}.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return path

def load_l1(path):
    from difftest import DeviceState,MEM_SIZE
    dll=C.CDLL(str(path))
    dll.ugh_memory.restype=C.POINTER(C.c_uint8*MEM_SIZE)
    dll.ugh_device_state.restype=C.POINTER(DeviceState)
    dll.ugh_device_size.restype=C.c_uint32
    if dll.ugh_device_size()!=C.sizeof(DeviceState): raise RuntimeError('device layout drift')
    return dll

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind',choices=['native','bridge','reference'],nargs='?',default='native')
    parser.add_argument('--components',nargs='+',choices=sorted(COMPONENTS))
    args=parser.parse_args();print(build(args.kind,components=args.components))
