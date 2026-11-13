"""Build the SDL3 host from literal c/ plus host/. No DOS or CPU emulator at runtime.

First run python tools/build.py. Data is build/link/plain/UGH.EXE, copied beside
ugh.exe as ugh-data.exe. Its MZ load image and relocations seed the original RAM;
none of its code bytes are executed by the host.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
from common import ROOT, sha256
import cgen
from cbuild import GCC

SDL_ROOT = Path('C:/tools/sdl3-3.4.16-mingw')
SDL = SDL_ROOT/'SDL3-3.4.16/x86_64-w64-mingw32'
OPL = Path('C:/tools/nuked-opl3-765ec962e473')


def build():
    out = ROOT/'build/host'
    out.mkdir(parents=True, exist_ok=True)
    # This checks the rebuilt image, relocation list, source receipts and symbols.
    mz, symbols = cgen.read_symbols()
    cgen.generate()
    shutil.copyfile(ROOT/'build/link/plain/UGH.EXE', out/'ugh-data.exe')
    lines = ['/* Generated from rebuilt symbols; no game code. */', '#include "host.h"',
             'const HostSymbol host_symbols[] = {']
    for name, row in sorted(symbols.items()):
        lines.append('{'+json.dumps(name)+f', {cgen.LOAD+row["frame"]}, {row["offset"]}'+'},')
    lines += ['};', 'const unsigned host_symbol_count = sizeof(host_symbols)/sizeof(host_symbols[0]);',
              f'const char host_data_hash[] = "{sha256(mz.data)}";']
    (out/'symbols.c').write_text('\n'.join(lines)+'\n')
    sources = sorted((ROOT/'c').glob('*.c')) + sorted((ROOT/'host').glob('*.c'))
    cmd = [str(GCC), '-O2', '-g', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fwrapv',
           '-I', str(ROOT/'c'), '-I', str(ROOT/'host'), '-I', str(SDL/'include'),
           '-I', str(OPL), '-o', str(out/'ugh.exe'), *map(str,sources),
           str(out/'symbols.c'), str(OPL/'opl3.c'), '-L', str(SDL/'lib'), '-lSDL3', '-lbcrypt']
    env = dict(os.environ, PATH=str(GCC.parent)+os.pathsep+os.environ.get('PATH',''))
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    (out/'gcc.log').write_text(p.stdout+p.stderr)
    if p.returncode: raise RuntimeError(p.stdout+p.stderr)
    shutil.copyfile(SDL/'bin/SDL3.dll', out/'SDL3.dll')
    for dll in ('libwinpthread-1.dll',):
        if (GCC.parent/dll).exists(): shutil.copyfile(GCC.parent/dll,out/dll)
    shutil.copyfile(OPL/'LICENSE',out/'Nuked-OPL3-LICENSE.txt')
    shutil.copyfile(SDL_ROOT/'SDL3-3.4.16/LICENSE.txt',out/'SDL-LICENSE.txt')
    # Preserve the exact LGPL source and relink command beside the application.
    for name in ('opl3.c','opl3.h'): shutil.copyfile(OPL/name,out/name)
    inputs = sources+sorted((ROOT/'c').glob('*.h'))+sorted((ROOT/'host').glob('*.h'))+[
        OPL/'opl3.c',OPL/'opl3.h',ROOT/'tools/hostbuild.py']
    receipt=dict(command=cmd,compiler_sha256=sha256(GCC.read_bytes()),
        image_sha256=sha256(mz.image),data='ugh-data.exe (MZ image + all relocations)',
        sdl_provenance=json.loads((SDL_ROOT/'provenance.json').read_text()),
        opl=json.loads((ROOT/'metadata/verif-tools.json').read_text())['nuked_opl3'],
        inputs={str(f):sha256(f.read_bytes()) for f in inputs})
    (out/'hostbuild.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(out/'ugh.exe')
    return out/'ugh.exe'


if __name__ == '__main__':
    build()
