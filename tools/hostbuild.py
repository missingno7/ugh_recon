"""Build the SDL3 host from literal c/ plus host/, with certified native bridges by default.

First run python tools/build.py. Data is build/link/plain/UGH.EXE, copied beside
ugh.exe as ugh-data.exe. Its MZ load image and relocations seed the original RAM;
none of its code bytes are executed by the host.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import re
from common import ROOT, sha256
import cgen
from cbuild import GCC

SDL_ROOT = Path('C:/tools/sdl3-3.4.16-mingw')
SDL = SDL_ROOT/'SDL3-3.4.16/x86_64-w64-mingw32'
OPL = Path('C:/tools/nuked-opl3-765ec962e473')
STATUS_ORDER = ['unanalyzed', 'analyzed', 'boundary-established', 'migrated',
                'verified-under-assumptions', 'verified-within-contract',
                'integration-validated']


def selected_units(literal=False):
    if literal:
        return []
    selected=[]
    for cert_path in sorted((ROOT/'metadata/closure').glob('*.json')):
        cert=json.loads(cert_path.read_text())
        status=cert.get('status')
        if status not in STATUS_ORDER or STATUS_ORDER.index(status)<STATUS_ORDER.index('migrated'):
            continue
        component=cert.get('component',cert_path.stem)
        files=cert.get('native',{}).get('files',[])
        native=[ROOT/f for f in files if f.startswith('native/') and '/bridge/' not in f and f.endswith('.c')]
        bridges=[ROOT/f for f in files if f.startswith('native/bridge/') and f.endswith('.c')]
        if len(native)!=1 or len(bridges)!=1:
            raise RuntimeError(f'{component}: host bridge build requires one native .c and one bridge .c; got {native} / {bridges}')
        bridge_text=bridges[0].read_text()
        exports=sorted(set(re.findall(r'\bEXPORT\s+int\s+(c_[A-Za-z0-9_]+)\s*\(',bridge_text)))
        # A bridge without c_ exports is a library unit (for example the level view used by
        # other bridges): it is linked and replaces no L1 routine.
        selected.append(dict(component=component,status=status,native=native[0],bridge=bridges[0],exports=exports))
    return selected


def build(literal=False):
    out = ROOT/'build/host'
    out.mkdir(parents=True, exist_ok=True)
    units=selected_units(literal)
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
    # Replace only endpoints named by selected bridges. The generated L1 copies
    # retain the original functions as l1_* for each bridge's fallback path.
    substitutions={name:'l1_'+name[2:] for unit in units for name in unit['exports']}
    generated=out/'sources'
    generated.mkdir(exist_ok=True)
    sources=[]
    for source in sorted((ROOT/'c').glob('*.c')):
        text=source.read_text()
        changed=False
        for name,replacement in substitutions.items():
            text2=re.sub(r'\bc_'+re.escape(name[2:])+r'\b',replacement,text)
            changed |= text2!=text
            text=text2
        if changed:
            target=generated/source.name
            target.write_text(text)
            sources.append(target)
        else:
            sources.append(source)
    sources += sorted((ROOT/'host').glob('*.c'))
    sources += [unit['native'] for unit in units] + [unit['bridge'] for unit in units]
    unit_names=[u['component'] for u in units]
    (out/'units.c').write_text('/* Generated host variant metadata. */\n#include "host.h"\n'+
        'const char *host_native_units[] = {'+','.join(json.dumps(x) for x in unit_names)+'};\n'+
        f'const unsigned host_native_unit_count = {len(unit_names)};\n'+
        'const char *host_variant = '+json.dumps('literal' if literal else 'native-bridged')+';\n')
    fallbacks=out/'bridge_fallbacks.h'
    fallbacks.write_text('#include "ugh.h"\n'+''.join(f'int l1_{name[2:]}(Regs *);\n'
        for name in sorted(substitutions)))
    sources.append(out/'units.c')
    cmd = [str(GCC), '-O2', '-g', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fwrapv',
           '-include',str(fallbacks),'-I', str(ROOT/'c'), '-I', str(ROOT/'host'), '-I', str(SDL/'include'),
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
    inputs = sources+[fallbacks,out/'symbols.c']+sorted((ROOT/'c').glob('*.c'))+sorted((ROOT/'c').glob('*.h'))+sorted((ROOT/'host').glob('*.h'))+[
        OPL/'opl3.c',OPL/'opl3.h',ROOT/'tools/hostbuild.py']
    inputs += [ROOT/'metadata/closure'/f"{unit['component']}.json" for unit in units]
    inputs += [unit['native'] for unit in units]+[unit['bridge'] for unit in units]
    inputs += [header for unit in units for header in sorted(unit['native'].parent.glob('*.h'))]
    receipt=dict(command=cmd,compiler_sha256=sha256(GCC.read_bytes()),
        image_sha256=sha256(mz.image),data='ugh-data.exe (MZ image + all relocations)',
        sdl_provenance=json.loads((SDL_ROOT/'provenance.json').read_text()),
        opl=json.loads((ROOT/'metadata/verif-tools.json').read_text())['nuked_opl3'],
        inputs={str(f):sha256(f.read_bytes()) for f in dict.fromkeys(inputs)},
        variant='literal' if literal else 'native-bridged',
        executable_sha256=sha256((out/'ugh.exe').read_bytes()),
        linked_units=[dict(component=u['component'],status=u['status'],exports=u['exports']) for u in units])
    (out/'hostbuild.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(out/'ugh.exe')
    return out/'ugh.exe'


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--literal',action='store_true',help='build pure L1 host without native bridges')
    build(parser.parse_args().literal)
