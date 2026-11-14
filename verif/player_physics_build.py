"""Build actual accepted units plus craft physics in an isolated native DLL."""
import os,re,subprocess,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
from player_physics_shells import BRIDGE,NAMES
OUT=ROOT/'build/workers/close-stones-8'
FILES=[ROOT/'native/player_physics.h',ROOT/'native/player_physics.c',BRIDGE]
sys.path.insert(0,str(ROOT/'tools'))
def includes(text,path):
    return re.sub(r'#include "([^"]+)"',lambda m:'#include "'+(path.parent/m[1]).resolve().as_posix()+'"' if (path.parent/m[1]).is_file() else m[0],text)
def build():
    import hostbuild
    OUT.mkdir(parents=True,exist_ok=True)
    if (ROOT/'.closure-baseline.json').is_file():
        tracked={p.relative_to(ROOT).as_posix() for folder in ['native','metadata/closure'] for p in (ROOT/folder).rglob('*') if p.is_file()}
    else:tracked=set(subprocess.check_output(['git','ls-files','metadata/closure','native'],cwd=ROOT,text=True).splitlines())
    units=[u for u in hostbuild.selected_units() if u['component']!='player_physics' and 'metadata/closure/'+u['component']+'.json' in tracked]
    exports=[*NAMES,*[n[2:] for u in units for n in u['exports']]]
    folder=OUT/f'variant-{os.getpid()}';folder.mkdir(parents=True,exist_ok=True);sources=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        text=path.read_text();changed=False
        for name in exports:text,count=re.subn(r'\bc_'+name+r'\b','l1_'+name,text);changed|=bool(count)
        if path.name=='dispatch.c':
            old='uint16_t cs=r->cs; r->cs=segment;';assert old in text
            text=text.replace(old,old+'platform_trace_entry(segment,offset,r);');changed=True
        if changed:generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    text=includes(BRIDGE.read_text(),BRIDGE)
    text='EXPORT uint32_t player_physics_audit[3];\n'+text
    text=text.replace('EXPORT uint32_t', '#include "ugh.h"\nEXPORT uint32_t',1)
    text=text.replace('PhysicsPlan *plan=&storage;', 'PhysicsPlan *plan=&storage;player_physics_audit[0]++;if(!storage.active)player_physics_audit[2]++;')
    text=text.replace('int c_SamplePlayerCollisionPixels(Regs *r) {','int c_SamplePlayerCollisionPixels(Regs *r) {player_physics_audit[1]++;')
    generated=folder/'player_physics_bridge.c';generated.write_text(text);sources += [ROOT/'native/player_physics.c',generated]
    for unit in units:sources += [unit['native'],unit['bridge']]
    declarations=folder/'fallbacks.h';declarations.write_text('#include "ugh.h"\n'+''.join('int l1_'+n+'(Regs *);\n' for n in exports))
    dll=folder/'player-physics.dll';result=compile_c(sources,dll,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared','-DACTOR_VERIFY','-include',str(declarations)])
    headers=[p for p in (ROOT/'native').glob('*.h') if p.relative_to(ROOT).as_posix() in tracked or p in FILES]
    result['maintained_inputs']=hashes([*FILES,*[p for u in units for p in [u['native'],u['bridge']]],*sorted((ROOT/'c').glob('*.[ch]')),*headers,Path(__file__),ROOT/'verif/player_physics_shells.py']);result['baseline_units']=[u['component'] for u in units]
    save(OUT/'build.json',result);return dll
if __name__=='__main__':print(build())
