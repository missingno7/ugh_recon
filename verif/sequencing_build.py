"""Pinned committed units plus lifecycle/session, with entry and frame audits."""
import os,re,subprocess,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
from lifecycle_shells import FILES as LIFEFILES,NAMES as LIFENAMES
from session_bridge import FILES as SESSIONFILES,NAMES as SESSIONNAMES
OUT=ROOT/'build/workers/close-stones-12'
BASELINE='e4e69a0'
sys.path.insert(0,str(ROOT/'tools'))
def absolute(text,path):return re.sub(r'#include "([^"]+)"',lambda m:'#include "'+(path.parent/m[1]).resolve().as_posix()+'"' if (path.parent/m[1]).is_file() else m[0],text)
def build():
    import hostbuild
    tracked=set(subprocess.check_output(['git','ls-tree','-r','--name-only',BASELINE,'metadata/closure','native'],cwd=ROOT,text=True).splitlines()) if not (ROOT/'.closure-baseline.json').is_file() else {p.relative_to(ROOT).as_posix() for folder in ['native','metadata/closure'] for p in (ROOT/folder).rglob('*') if p.is_file()}
    units=[u for u in hostbuild.selected_units() if u['component'] not in ['lifecycle','session'] and 'metadata/closure/'+u['component']+'.json' in tracked]
    names=[*LIFENAMES,*SESSIONNAMES];exports=[*names,*[n[2:] for u in units for n in u['exports']]]
    folder=OUT/f'variant-{os.getpid()}';folder.mkdir(parents=True,exist_ok=True);sources=[]
    for p in sorted((ROOT/'c').glob('*.c')):
        text=p.read_text();changed=False
        for name in exports:text,count=re.subn(r'\bc_'+name+r'\b','l1_'+name,text);changed|=bool(count)
        if p.name=='dispatch.c':text=text.replace('uint16_t cs=r->cs; r->cs=segment;','uint16_t cs=r->cs; r->cs=segment;platform_trace_entry(segment,offset,r);');changed=True
        for i,name in enumerate(names):
            try:body=function(text,'l1_'+name)
            except ValueError:continue
            text=text.replace(body,body.replace('{','{sequencing_audit['+str(8+i)+']++;',1))
        if changed:target=folder/p.name;target.write_text(text);sources.append(target)
        else:sources.append(p)
    own=[(ROOT/'native/lifecycle.c',ROOT/'native/bridge/lifecycle_bridge.c'),(ROOT/'native/session.c',ROOT/'native/bridge/session_bridge.c')]
    declarations=folder/'declarations.h';declarations.write_text('#include "ugh.h"\nextern uint32_t sequencing_audit[16],session_frame_audit[4],sequence_actor_audit[12];\n'+''.join('int l1_'+n+'(Regs *);\n' for n in exports))
    definitions=folder/'audit.c';definitions.write_text('#include "ugh.h"\nEXPORT uint32_t sequencing_audit[16],session_frame_audit[4],sequence_actor_audit[12];\n');sources.append(definitions)
    for native,bridge in [*[(u['native'],u['bridge']) for u in units],*own]:
        text=absolute(bridge.read_text(),bridge)
        for i,name in enumerate(names):
            try:body=function(text,'c_'+name)
            except ValueError:continue
            text=text.replace(body,body.replace('{','{sequencing_audit['+str(i)+']++;',1))
        if bridge.name=='session_bridge.c':
            text=text.replace('  switch(e.action){','  if(process.phase==SP_FRAME_BEGIN){session_frame_audit[0]++;}\n  if(e.action==SESSION_SWAP_PAGE){session_frame_audit[1]++;}\n  switch(e.action){',1)
            text=text.replace('if(process.completed_frames==100000)return UGH_BUDGET;','if(process.completed_frames==100000){session_frame_audit[3]++;return UGH_BUDGET;}')
        if bridge.name=='actor_render_bridge.c':
            text=text.replace('*plan=(RenderPlan){0};','sequence_actor_audit[operation]++;*plan=(RenderPlan){0};',1)
            text=text.replace('if(!plan->active) return;','if(!plan->active){sequence_actor_audit[6+operation]++;return;}',1)
        target=folder/bridge.name;target.write_text(text);sources += [native,target]
    dll=folder/'sequencing.dll';result=compile_c(sources,dll,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared','-DACTOR_VERIFY','-include',str(declarations)])
    headers=[p for p in (ROOT/'native').rglob('*.h') if p.relative_to(ROOT).as_posix() in tracked or p in [*LIFEFILES,*SESSIONFILES]]
    result['maintained_inputs']=hashes([*LIFEFILES,*SESSIONFILES,*[p for u in units for p in [u['native'],u['bridge']]],*headers,*sorted((ROOT/'c').glob('*.[ch]')),Path(__file__),ROOT/'verif/lifecycle_shells.py',ROOT/'verif/session_bridge.py']);result['baseline_units']=[u['component'] for u in units];result['entries']=names
    result['maintained_inputs'].update(hashes([ROOT/'verif/session_loader.py']))
    save(OUT/'build.json',result);return dll
if __name__=='__main__':print(build())
