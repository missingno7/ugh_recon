"""Build portable C11 into a ctypes DLL with the MSYS2 mingw64 compiler."""
import json
import os
import subprocess
from pathlib import Path
from common import ROOT, sha256
import cgen

GCC = Path(r'C:\msys64\mingw64\bin\gcc.exe')


def build(out=None):
    cgen.generate()
    out = Path(out or ROOT / 'build/c/ughcore.dll')
    out.parent.mkdir(parents=True, exist_ok=True)
    sources = sorted((ROOT / 'c').glob('*.c'))
    cmd = [str(GCC), '-shared', '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror',
           '-fwrapv', '-o', str(out), *map(str, sources)]
    env = dict(os.environ, PATH=str(GCC.parent) + os.pathsep + os.environ.get('PATH', ''))
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    (out.parent / 'gcc.log').write_text(p.stdout + p.stderr)
    if p.returncode:
        raise RuntimeError(p.stdout + p.stderr)
    inputs = sources + sorted((ROOT / 'c').glob('*.h'))
    (out.parent / 'cbuild.json').write_text(json.dumps(dict(command=cmd,
        compiler_sha256=sha256(GCC.read_bytes()),
        sources={str(f.relative_to(ROOT)): sha256(f.read_bytes()) for f in inputs}), indent=2)+'\n')
    return out


if __name__ == '__main__':
    print(build())
