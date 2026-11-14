"""Demo presentation verifier paths and isolated builders."""
import os,re,subprocess,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
from demo_scene_shells import BRIDGE,NAMES
OUT=ROOT/'build/workers/close-stones-7'
FILES=[ROOT/'native/demo_presentation.h',ROOT/'native/demo_presentation.c',BRIDGE]
sys.path.insert(0,str(ROOT/'tools'))
def includes(text,path):
    return re.sub(r'#include "([^"]+)"',lambda m:'#include "'+(path.parent/m[1]).resolve().as_posix()+'"' if (path.parent/m[1]).is_file() else m[0],text)
def build():
    import hostbuild
    if (ROOT/'.closure-baseline.json').is_file():
        tracked={p.relative_to(ROOT).as_posix() for folder in ['native','metadata/closure'] for p in (ROOT/folder).rglob('*') if p.is_file()}
    else:tracked=set(subprocess.check_output(['git','ls-files','metadata/closure','native'],cwd=ROOT,text=True).splitlines())
    units=[u for u in hostbuild.selected_units() if u['component']!='demo_presentation' and 'metadata/closure/'+u['component']+'.json' in tracked]
    exports=[*NAMES,*[n[2:] for u in units for n in u['exports']]]
    folder=OUT/f'variant-{os.getpid()}';folder.mkdir(parents=True,exist_ok=True);sources=[]
    for path in sorted((ROOT/'c').glob('*.c')):
        text=path.read_text();changed=False
        for name in exports:text,count=re.subn(r'\bc_'+name+r'\b','l1_'+name,text);changed|=bool(count)
        if path.name=='dispatch.c':
            old='uint16_t cs=r->cs; r->cs=segment;';assert old in text
            text=text.replace(old,old+'platform_trace_entry(segment,offset,r);');changed=True
        if path.name=='demo_scripts.c':
            text='extern uint32_t demo_scene_audit[20];\n'+text.replace('#include "ugh.h"','')
            text='#include "ugh.h"\n'+text
            text=text.replace('int c_loc_0B4E(Regs *r) {','int c_loc_0B4E(Regs *r) {demo_scene_audit[9]++;');changed=True
        if changed:generated=folder/path.name;generated.write_text(text);sources.append(generated)
        else:sources.append(path)
    text=includes(BRIDGE.read_text(),BRIDGE);text=text.replace('typedef struct DemoScenePlan','EXPORT uint32_t demo_scene_audit[20];\ntypedef struct DemoScenePlan',1)
    for i,name in enumerate(NAMES):
        body=function(text,'c_'+name);condition='!dp_environment(r)'+(' || (r->bx&1u) || r->bx>=32' if i<2 else '')
        new=body.replace('{',f'{{demo_scene_audit[{i}]++;if({condition})demo_scene_audit[{i+10}]++;',1);text=text.replace(body,new)
    generated=folder/'demo_presentation_bridge.c';generated.write_text(text);sources += [ROOT/'native/demo_presentation.c',generated]
    for unit in units:
        sources.append(unit['native']);path=unit['bridge']
        if unit['component']=='actor_render':
            text=includes(path.read_text(),path);text='#include <stdint.h>\nextern uint32_t demo_scene_audit[20];\n'+text
            for i,name in [(7,'DrawDemoSprites'),(8,'EraseDemoSprites')]:
                body=function(text,'c_'+name);text=text.replace(body,body.replace('{',f'{{demo_scene_audit[{i}]++;',1))
            copied=folder/path.name;copied.write_text(text);sources.append(copied)
        else:sources.append(path)
    declarations=folder/'fallbacks.h';declarations.write_text('#include "ugh.h"\n'+''.join('int l1_'+n+'(Regs *);\n' for n in exports))
    dll=folder/'demo-scene.dll';result=compile_c(sources,dll,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared','-DACTOR_VERIFY','-include',str(declarations)])
    headers=[p for p in (ROOT/'native').glob('*.h') if p.relative_to(ROOT).as_posix() in tracked or p in FILES]
    result['maintained_inputs']=hashes([*FILES,*[p for u in units for p in [u['native'],u['bridge']]],*sorted((ROOT/'c').glob('*.[ch]')),*headers,Path(__file__),ROOT/'verif/demo_scene_shells.py']);result['baseline_units']=[u['component'] for u in units]
    save(OUT/'build.json',result);return dll

def pair(folder):
    folder.mkdir(parents=True,exist_ok=True);scene=(ROOT/'c/scene.c').read_text();effects=(ROOT/'c/demo_scripts.c').read_text()
    text='#include "'+(ROOT/'c/platform.h').as_posix()+'"\n'
    text+='uint16_t ps_read(uint16_t,uint16_t);uint8_t ps_read8(uint16_t,uint16_t);void ps_write(uint16_t,uint16_t,uint16_t);void ps_write8(uint16_t,uint16_t,uint8_t);int ps_near(uint16_t,uint16_t,Regs *);int ps_dispatch(uint16_t,uint16_t,Regs *);int ps_direct(Regs *);void ps_abort(void);\n'
    text+='#define rd16 ps_read\n#define rd8 ps_read8\n#define wr16 ps_write\n#define wr8 ps_write8\n#define ugh_call_near ps_near\n#define ugh_dispatch ps_dispatch\n#define abort ps_abort\n'
    text+='#include "'+(ROOT/'native/demo_presentation.c').as_posix()+'"\n'
    for n in NAMES:text+='int reference_'+n+'(Regs *);\n'
    text+='\n'.join(line for line in scene.splitlines() if line.startswith('#define '))+'\n'
    for helper in ['push','pop','scene_far_call']:
        body=function(scene,helper)
        for name in ['push','pop','scene_far_call']:body=re.sub(r'\b'+name+r'\b','reference_'+name,body)
        text+=body
    for name in NAMES:
        body=function(effects if name in NAMES[:2] else scene,'c_'+name)
        body=re.sub(r'\bc_(\w+)\b',r'reference_\1',body)
        if name=='PlayAttractDemo':body=body.replace('return reference_RunScriptedDemo(r);','return ps_direct(r);')
        for helper in ['push','pop','scene_far_call']:body=re.sub(r'\b'+helper+r'\b','reference_'+helper,body)
        text+=body
    text+='#undef R\n#undef W\n#undef RX\n#undef WX\n#undef CALL\n'
    bridge=includes(BRIDGE.read_text(),BRIDGE).replace('#include <stdlib.h>','')
    bridge=bridge.replace('static void dp_require','void ps_before(DemoScenePlan *);void ps_seam(DemoScenePlan *);void ps_parent_return(DemoScenePlan *,int);\nstatic void dp_require',1)
    bridge=bridge.replace('plan->pending_action=action;plan->pending=1;','plan->pending_action=action;plan->pending=1;ps_before(plan);')
    bridge=bridge.replace('plan->pending=0;','plan->pending=0;ps_seam(plan);')
    bridge=bridge.replace('direct?c_RunScriptedDemo(r):ugh_dispatch','direct?ps_direct(r):ugh_dispatch')
    bridge=bridge.replace('if(!status) dp_finish(r,plan);return status;','if(!status) dp_finish(r,plan);ps_parent_return(plan,status);return status;')
    text+=bridge
    (folder/'pair.inc').write_text(text)
    return [*FILES,ROOT/'c/scene.c',ROOT/'c/demo_scripts.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',ROOT/'c/platform.h',Path(__file__),ROOT/'verif/demo_scene_shells.py']
if __name__=='__main__':print(build())
