"""Build native library, or an L1 variant without editing/generated writes in c/."""
import argparse, ctypes as C, hashlib, json, os, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GCC=Path(r'C:\msys64\mingw64\bin\gcc.exe')
OUT=ROOT/'build/native'

def build(kind='native', source=None, tag=''):
    OUT.mkdir(parents=True,exist_ok=True)
    native=Path(source or ROOT/'native/ice.c')
    sources=([native] if kind=='native' else
             sorted(p for p in (ROOT/'c').glob('*.c') if kind=='reference' or p.name!='ice.c'))
    if kind=='bridge': sources += [native, ROOT/'native/bridge/ice_bridge.c']
    path=OUT/f'{kind}{tag}_{os.getpid()}.dll'
    cmd=[str(GCC),'-shared','-O2','-std=c11','-Wall','-Wextra','-Werror','-fwrapv',
         '-I',str(ROOT/'c'),'-I',str(ROOT/'native'),'-o',str(path),*map(str,sources)]
    env=dict(os.environ,PATH=str(GCC.parent)+os.pathsep+os.environ.get('PATH',''))
    p=subprocess.run(cmd,capture_output=True,text=True,env=env)
    (OUT/f'{kind}{tag}.log').write_text(p.stdout+p.stderr)
    if p.returncode: raise RuntimeError(p.stdout+p.stderr)
    inputs=sources+list((ROOT/'native').rglob('*.h'))
    if kind!='native': inputs+=list((ROOT/'c').glob('*.h'))+list((ROOT/'c').glob('*.inc'))
    receipt=dict(command=cmd,compiler_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),
                 inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
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
    print(build(parser.parse_args().kind))
