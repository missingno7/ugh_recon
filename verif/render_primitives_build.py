"""Isolated 32-unit committed baseline plus native rendering primitives."""
import os,re,subprocess,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
from render_primitives_shells import OUT,FILES,BRIDGE,NAMES
sys.path.insert(0,str(ROOT/'tools'))

def build():
    import hostbuild
    OUT.mkdir(parents=True,exist_ok=True)
    tracked=set(subprocess.check_output(['git','ls-files','metadata/closure','native'],cwd=ROOT,text=True).splitlines()) if not (ROOT/'.closure-baseline.json').is_file() else {p.relative_to(ROOT).as_posix() for folder in ['native','metadata/closure'] for p in (ROOT/folder).rglob('*') if p.is_file()}
    units=[u for u in hostbuild.selected_units() if u['component'] not in ['render_primitives','hud'] and 'metadata/closure/'+u['component']+'.json' in tracked]
    exports=[*NAMES,*[n[2:] for u in units for n in u['exports']]]
    folder=OUT/f'variant-{os.getpid()}';folder.mkdir(parents=True,exist_ok=True);sources=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        text=path.read_text();changed=False
        for name in exports:text,count=re.subn(r'\bc_'+name+r'\b','l1_'+name,text);changed|=bool(count)
        if path.name=='dispatch.c':text=text.replace('uint16_t cs=r->cs; r->cs=segment;','uint16_t cs=r->cs; r->cs=segment;platform_trace_entry(segment,offset,r);');changed=True
        if changed:generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    text=BRIDGE.read_text().replace('#include "render_primitives_support.h"','#include "'+(ROOT/'native/bridge/render_primitives_support.h').as_posix()+'"')
    text='#include "ugh.h"\nEXPORT uint32_t render_primitives_audit[22];\n'+text
    for i,name in enumerate(NAMES):
        body=function(text,'c_'+name);active='r->bx<4 && !(r->bx&1)' if name in ['RestorePlayerBackground','AnimateAndDrawPlayer'] else '1'
        changed=body.replace('{','{render_primitives_audit['+str(i)+']++;if(!('+active+'))render_primitives_audit['+str(i+11)+']++;',1);text=text.replace(body,changed)
    generated=folder/'render_primitives_bridge.c';generated.write_text(text);sources += [ROOT/'native/render_primitives.c',generated]
    for unit in units:sources += [unit['native'],unit['bridge']]
    declarations=folder/'fallbacks.h';declarations.write_text('#include "ugh.h"\n'+''.join('int l1_'+n+'(Regs *);\n' for n in exports))
    dll=folder/'render-primitives.dll';result=compile_c(sources,dll,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared','-DACTOR_VERIFY','-include',str(declarations)])
    headers=[p for p in (ROOT/'native').glob('*.h') if p.relative_to(ROOT).as_posix() in tracked or p in FILES]
    result['maintained_inputs']=hashes([*FILES,*[p for u in units for p in [u['native'],u['bridge']]],*sorted((ROOT/'c').glob('*.[ch]')),*headers,Path(__file__),ROOT/'verif/render_primitives_shells.py']);result['baseline_units']=[u['component'] for u in units]
    save(OUT/'build.json',result);return dll
if __name__=='__main__':print(build())
