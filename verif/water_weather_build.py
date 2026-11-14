"""Build actual accepted units plus water and weather in an isolated native DLL."""
import os,re,subprocess,sys
from pathlib import Path
from closure_support import ROOT,compile_c,hashes,save,function
from water_weather_shells import BRIDGE,NAMES
OUT=ROOT/'build/workers/close-stones-9'
FILES=[ROOT/'native/water_weather.h',ROOT/'native/water_weather.c',BRIDGE]
sys.path.insert(0,str(ROOT/'tools'))
def includes(text,path):
    return re.sub(r'#include "([^"]+)"',lambda m:'#include "'+(path.parent/m[1]).resolve().as_posix()+'"' if (path.parent/m[1]).is_file() else m[0],text)
def build():
    import hostbuild
    OUT.mkdir(parents=True,exist_ok=True)
    if (ROOT/'.closure-baseline.json').is_file():
        tracked={p.relative_to(ROOT).as_posix() for folder in ['native','metadata/closure'] for p in (ROOT/folder).rglob('*') if p.is_file()}
    else:tracked=set(subprocess.check_output(['git','ls-files','metadata/closure','native'],cwd=ROOT,text=True).splitlines())
    units=[u for u in hostbuild.selected_units() if u['component']!='water_weather' and 'metadata/closure/'+u['component']+'.json' in tracked]
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
    text='#include "ugh.h"\nEXPORT uint32_t water_weather_audit[18];\n'+text
    for i,name in enumerate(NAMES):
        body=function(text,'c_'+name)
        active='1' if i in (2,3,4) else ('ww_rain_admit(r,'+('0' if i==7 else '1')+')' if i in (5,7,8) else 'r->ds==DATA_SEG && r->cs==GAME_SEG')
        insert='water_weather_audit['+str(i)+']++;if(!('+active+'))water_weather_audit['+str(i+9)+']++;'
        if i in (0,1,6):
            insert='water_weather_audit['+str(i)+']++;'
            changed=body.replace('{','{'+insert,1).replace('WeatherPlan *plan=&storage;','WeatherPlan *plan=&storage;if(!plan->active)water_weather_audit['+str(i+9)+']++;',1)
        else:changed=body.replace('{','{'+insert,1)
        text=text.replace(body,changed)
    generated=folder/'water_weather_bridge.c';generated.write_text(text);sources += [ROOT/'native/water_weather.c',generated]
    for unit in units:sources += [unit['native'],unit['bridge']]
    declarations=folder/'fallbacks.h';declarations.write_text('#include "ugh.h"\n'+''.join('int l1_'+n+'(Regs *);\n' for n in exports))
    dll=folder/'water-weather.dll';result=compile_c(sources,dll,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-shared','-DACTOR_VERIFY','-include',str(declarations)])
    headers=[p for p in (ROOT/'native').glob('*.h') if p.relative_to(ROOT).as_posix() in tracked or p in FILES]
    result['maintained_inputs']=hashes([*FILES,*[p for u in units for p in [u['native'],u['bridge']]],*sorted((ROOT/'c').glob('*.[ch]')),*headers,Path(__file__),ROOT/'verif/water_weather_shells.py']);result['baseline_units']=[u['component'] for u in units]
    save(OUT/'build.json',result);return dll
if __name__=='__main__':print(build())
