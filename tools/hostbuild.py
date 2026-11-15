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

def timing_composed(units):
    return any(u['component']=='timing_world' for u in units)

def composition_options(units, base=None):
    if not timing_composed(units): return []
    return (['-DUGH_NATIVE_INPUT'] if any(u['component']=='input_world' for u in units) else [])+(['-DUGH_NATIVE_PALETTE'] if any(u['component']=='palette_world' for u in units) else [])+(['-DUGH_NATIVE_AUDIO'] if any(u['component']=='audio_world' for u in units) else [])+['-DUGH_NATIVE_TIMING', '-DNATIVE_AUDIO_BYTE_SERVICE', '-I', str((base or ROOT)/'native/bridge'),
            '-I', str(ROOT/'verif/projector')]

def _previous_composition_source(relative, text, units):
    """Generated interop services only; the literal build is unchanged."""
    if relative in ('native/far_copy.c','native/decimal.c') and any(u['component']=='audio_world' for u in units):
        header='far_copy.h' if relative.endswith('far_copy.c') else 'decimal.h'
        text=text.replace('#include "'+header+'"','#include "'+(ROOT/'native'/header).as_posix()+'"\n#include "'+(ROOT/'native/audio_bytes.h').as_posix()+'"')
        if header=='far_copy.h':
            statement='destination[destination_cursor]=source[source_cursor];';assert text.count(statement)==1
            return text.replace(statement,'audio_borrowed_store(destination,destination_cursor,audio_borrowed_byte(source,source_cursor));')
        for value in ('digit','255'):
            statement='output->bytes[output->cursor]='+value+';';assert text.count(statement)==1
            text=text.replace(statement,'audio_borrowed_store(output->bytes,output->cursor,'+value+');')
        statement='bytes[0]+(uint16_t)bytes[1]*256u';assert text.count(statement)==1
        text=text.replace(statement,'audio_borrowed_byte(bytes,0)+(uint16_t)audio_borrowed_byte(bytes,1)*256u')
        for member in ('ten','hundred'):
            statement='*divisors.'+member;assert text.count(statement)==1
            text=text.replace(statement,'audio_borrowed_byte(divisors.'+member+',0)')
        return text
    if relative in ('native/bridge/ice_scratch_bridge.c','native/bridge/ice_bridge.c') and any(u['component']=='audio_world' for u in units):
        # The fixed workspace's trailing seed overlaps the C audio facade flags.
        # No maintained ICE source changes, and no native state is put into RAM.
        header='ice_scratch.h' if 'ice_scratch_bridge' in relative else 'ice.h'
        text=text.replace('#include "../'+header+'"',
            '#include "'+(ROOT/'native'/header).as_posix()+'"\n#include "audio_world_bridge.h"')
        seed='memcpy(output,ugh_mem+destination,sizeof output);'
        publish='memcpy(ugh_mem+destination,output,sizeof output);'
        assert text.count(seed)==text.count(publish)==1
        written='result.decoder.bytes_written' if 'ice_scratch_bridge' in relative else 'result.bytes_written'
        return text.replace('memcpy(input,ugh_mem+source,sizeof input);','audio_workspace_read(input,source,sizeof input);').replace(seed,
            'audio_workspace_read(output,destination,sizeof output);').replace(publish,
            'audio_workspace_publish(destination,output,sizeof output,unpacked,'+written+');')
    if not timing_composed(units) or relative!='c/memory.c': return text
    text='#include "timing_world_bridge.h"\n'+text
    text=text.replace('uint8_t ugh_read(uint32_t a) {',
        'uint8_t ugh_read(uint32_t a) { uint8_t owned; if(timing_shared_read(a,&owned))return owned;')
    text=text.replace('void ugh_write(uint32_t a, uint8_t v) {',
        'void ugh_write(uint32_t a, uint8_t v) { if(timing_shared_write(a,v))return;')
    return text


def _palette_composition_source(relative,text,units):
    text=_previous_composition_source(relative,text,units)
    if not any(u['component']=='palette_world' for u in units):return text
    header='#include "'+(ROOT/'native/bridge/palette_world_bridge.h').as_posix()+'"\n'
    if relative=='c/memory.c':
        text=header+text
        text=text.replace('uint8_t ugh_read(uint32_t a) {','uint8_t ugh_read(uint32_t a) { uint8_t colour; if(palette_shared_read(a,&colour))return colour;')
        text=text.replace('void ugh_write(uint32_t a, uint8_t v) {','void ugh_write(uint32_t a, uint8_t v) { if(palette_shared_write(a,v))return;')
    if relative in ('native/far_copy.c','native/decimal.c'):
        text=header+text.replace('audio_borrowed_byte(','palette_borrowed_byte(').replace('audio_borrowed_store(','palette_borrowed_store(')
    if relative=='native/bridge/timing_world_bridge.c':
        text=header+text
        old='timing_shared_read((uint32_t)(source-base+index),&value)'
        assert text.count(old)==1
        text=text.replace(old,'(palette_shared_read((uint32_t)(source-base+index),&value)||'+old+')')
    if relative=='native/bridge/audio_world_bridge.c':
        text=header+text
        old='timing_shared_read(address+i,&value)';assert text.count(old)==1
        text=text.replace(old,'(palette_shared_read(address+i,&value)||'+old+')')
        old='timing_shared_write((uint32_t)(destination-base+index),value)';assert text.count(old)==1
        text=text.replace(old,'(palette_shared_write((uint32_t)(destination-base+index),value)||'+old+')')
        text=text.replace('if(timing_is_owned(address))','if(palette_is_owned(address)||timing_is_owned(address))')
        old='if(written>distance)timing_shared_write(address,source[i]);';assert text.count(old)==1
        text=text.replace(old,'if(written>distance){if(!palette_shared_write(address,source[i]))timing_shared_write(address,source[i]);}')
    if relative=='c/platform.c':
        text=header+text+"\n"+r'''void palette_service_dac(PaletteDacWrite request){
#if PALETTE_TEST_FAULT == 2
 static unsigned held,done;static uint8_t pending;
 if(!done && request.kind==PALETTE_DAC_COMPONENT){
  if(held){
   platform_out(0x3c9,1,pending==request.value?pending:request.value);
   platform_out(0x3c9,1,pending==request.value?request.value:pending);
   if(pending!=request.value)done=1;
   held=0;return;
  }
  if(!ugh_devices.dac_component){pending=request.value;held=1;return;}
 }
#endif
#if PALETTE_TEST_FAULT == 4
 static unsigned dropped;
 if(!dropped && request.kind==PALETTE_DAC_COMPONENT && request.value){dropped=1;return;}
#endif
#if PALETTE_TEST_FAULT == 5
 ugh_devices.map_mask=0;
#endif
#if PALETTE_TEST_FAULT == 6
 ugh_devices.read_map=0;
#endif
 platform_out(request.kind==PALETTE_DAC_SELECT?0x3c8:0x3c9,1,request.value);
}
'''
    return text


def composition_source(relative,text,units):
    text=_palette_composition_source(relative,text,units)
    if not any(u['component']=='input_world' for u in units):return text
    header='#include "'+(ROOT/'native/bridge/input_world_bridge.h').as_posix()+'"\n'
    if relative=='c/memory.c':
        text=header+text
        text=text.replace('uint8_t ugh_read(uint32_t a) {','uint8_t ugh_read(uint32_t a) { uint8_t input; if(input_shared_read(a,&input))return input;')
        text=text.replace('void ugh_write(uint32_t a, uint8_t v) {','void ugh_write(uint32_t a, uint8_t v) { if(input_shared_write(a,v))return;')
    if relative in ('native/far_copy.c','native/decimal.c'):
        text=header+text.replace('palette_borrowed_byte(','input_borrowed_byte(').replace('palette_borrowed_store(','input_borrowed_store(')
    if relative=='native/bridge/timing_world_bridge.c':
        text=header+text;old='palette_shared_read((uint32_t)(source-base+index),&value)';assert text.count(old)==1
        text=text.replace(old,'(input_shared_read((uint32_t)(source-base+index),&value)||'+old+')')
    if relative=='native/bridge/audio_world_bridge.c':
        text=header+text
        old='palette_shared_read(address+i,&value)';assert text.count(old)==1
        text=text.replace(old,'(input_shared_read(address+i,&value)||'+old+')')
        old='palette_shared_write((uint32_t)(destination-base+index),value)';assert text.count(old)==1
        text=text.replace(old,'(input_shared_write((uint32_t)(destination-base+index),value)||'+old+')')
        text=text.replace('if(palette_is_owned(address)||timing_is_owned(address))','if(input_is_owned(address)||palette_is_owned(address)||timing_is_owned(address))')
        old='if(!palette_shared_write(address,source[i]))timing_shared_write(address,source[i]);';assert text.count(old)==1
        text=text.replace(old,'if(!input_shared_write(address,source[i]) && !palette_shared_write(address,source[i]))timing_shared_write(address,source[i]);')
    if relative in ('native/bridge/menus_bridge.c','native/bridge/high_scores_bridge.c'):
        text=header+text
        assert text.count('platform_interrupt(0x16,r)')==2
        text=text.replace('platform_interrupt(0x16,r)','input_editor_queue(r)')
    if relative=='c/platform.c':text+='\n'+(ROOT/'verif/input_platform_model.inc').read_text()
    return text


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
        composed=composition_source('c/'+source.name,text,units)
        changed=composed!=text
        text=composed
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
    for original in [unit['native'] for unit in units]+[unit['bridge'] for unit in units]:
        text=original.read_text()
        composed=composition_source(original.relative_to(ROOT).as_posix(),text,units)
        if composed!=text:
            target=generated/('native_'+original.name);target.write_text(composed);sources.append(target)
        else:sources.append(original)
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
           *composition_options(units),
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
