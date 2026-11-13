"""Actual native-host unit selection in an isolated audited DLL, plus C cuts."""
import os,re,sys,subprocess
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
from render_history_shells import BRIDGE,NAMES,OPS,partitions,adapt,gameplay_cuts
OUT=ROOT/'build/workers/close-stones-6'
FILES=[ROOT/'native/actor_render.h',ROOT/'native/actor_render.c',BRIDGE]
sys.path.insert(0,str(ROOT/'tools'))

def absolute_includes(text,path):
    return re.sub(r'#include "([^"]+)"',lambda m:'#include "'+(path.parent/m[1]).resolve().as_posix()+'"' if (path.parent/m[1]).is_file() else m[0],text)

def build():
    import hostbuild
    tracked=set(subprocess.check_output(['git','ls-files','metadata/closure','native'],cwd=ROOT,text=True).splitlines())
    units=[u for u in hostbuild.selected_units() if u['component']!='actor_render' and 'metadata/closure/'+u['component']+'.json' in tracked]
    exports=[*NAMES,*[n[2:] for u in units for n in u['exports']]]
    folder=OUT/f'variant-{os.getpid()}';folder.mkdir(parents=True,exist_ok=True);sources=[];originals=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        text=path.read_text()
        changed=False
        for name in exports:
            text,count=re.subn(r'\bc_'+name+r'\b','l1_'+name,text);changed|=bool(count)
        if changed:
            generated=folder/path.name;generated.write_text(text);sources.append(generated);originals.append(path)
        else:sources.append(path)
    text=absolute_includes(BRIDGE.read_text(),BRIDGE)
    text=text.replace('typedef struct RenderPlan','EXPORT uint32_t render_history_audit[12];\ntypedef struct RenderPlan',1)
    text=text.replace('*plan=(RenderPlan){0};','render_history_audit[operation]++; *plan=(RenderPlan){0};',1)
    text=text.replace('if(!plan->active) return;','if(!plan->active) {render_history_audit[6+operation]++;return;}',1)
    text+=gameplay_cuts(native=True)
    generated=folder/'actor_render_bridge.c';generated.write_text(text)
    sources += [ROOT/'native/actor_render.c',generated,*[p for u in units for p in [u['native'],u['bridge']]]]
    declarations=folder/'fallbacks.h';declarations.write_text('#include "ugh.h"\n'+''.join('int l1_'+n+'(Regs *);\n' for n in exports))
    dll=folder/'render-history.dll';result=compile_c(sources,dll,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared','-DACTOR_VERIFY','-include',str(declarations)])
    headers=[p for p in (ROOT/'native').glob('*.h') if p.relative_to(ROOT).as_posix() in tracked or p in FILES]
    result['maintained_inputs']=hashes([*FILES,*originals,*[p for u in units for p in [u['native'],u['bridge']]],*sorted((ROOT/'c').glob('*.[ch]')),*headers,Path(__file__),ROOT/'verif/render_history_shells.py'])
    result['baseline_units']=[u['component'] for u in units];save(OUT/'build.json',result);return dll

def pair(folder):
    folder.mkdir(parents=True,exist_ok=True)
    text='#include "'+(ROOT/'c/platform.h').as_posix()+'"\n'
    text+='uint16_t rh_read(uint16_t,uint16_t);void rh_write(uint16_t,uint16_t,uint16_t);int rh_call(uint16_t,uint16_t,Regs *);\n'
    text+='void rh_abort(void);\n#define abort rh_abort\n#define rd16 rh_read\n#define wr16 rh_write\n#define ugh_call_near rh_call\n'
    text+='#include "'+(ROOT/'native/actor_render.c').as_posix()+'"\n'
    bridge=absolute_includes(BRIDGE.read_text().split('/* BEGIN CHECKED L1 SHELLS */')[0],BRIDGE)
    text+=bridge.replace('#include <stdlib.h>','')
    scene=(ROOT/'c/scene.c').read_text();text+=function(scene,'sar')
    for op,fragment in partitions().items():
        text+='static int reference_'+op+'(Regs *r) {\n'+fragment+'\nreturn UGH_OK; }\n'
        text+='static int modern_'+op+'(Regs *r) { RenderPlan plan;ar_open(r,&plan,ACTOR_RENDER_'+op+');\n'+adapt(fragment)+'\nar_finish(r,&plan);return UGH_OK;}\n'
    (folder/'pair.inc').write_text(text)
    return [*FILES,ROOT/'native/actors.h',ROOT/'native/geometry.h',ROOT/'c/scene.c',ROOT/'c/demo_scripts.c',ROOT/'c/ugh.h',ROOT/'c/platform.h',ROOT/'c/ugh_sym.h',ROOT/'verif/render_history_shells.py',Path(__file__)]
if __name__=='__main__':print(build())
