"""Shared actual compiled L1/native/Unicorn API fixture and replay."""
import ctypes as C,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
from job_pool import run,save

def load_cut(text):
 name='EXPORT int c_LoadCurrentLevelState(Regs *r)'
 if name in text:
  text=text.replace(name,'EXPORT int fixture_load_body(Regs *r)',1)+'\nextern int api_stop_at_load;EXPORT int c_LoadCurrentLevelState(Regs*r){if(api_stop_at_load)return UGH_BUDGET;return fixture_load_body(r);}\n'
 return text

def build(profile,out,worlds_enabled=None):
 import hostbuild,world_registry
 out=Path(out);folder=out/profile;folder.mkdir(parents=True,exist_ok=True);all_units=hostbuild.selected_units();worlds={r['component'] for r in world_registry.entries()}
 scope=set(worlds if worlds_enabled is None else worlds_enabled)
 excluded=scope|({'audio_world'} if scope=={'timing_world'} else set())
 units=[] if profile=='reference' else [u for u in all_units if u['component'] not in excluded or (profile=='composed' and u['component'] in scope)]
 imports=''.join(r['cold_import']+'(ugh_mem);' for r in world_registry.entries() if r['component'] in scope and r['cold_import']) if profile=='composed' else ''
 exports={n for u in units for n in u['exports']};wrappers=sorted({n for u in all_units for n in u['exports']}|{n for p in (ROOT/'c').glob('*.c') for n in re.findall(r'EXPORT\s+int\s+(c_\w+)\s*\(',p.read_text())});sources=[]
 for p in sorted((ROOT/'c').glob('*.c')):
  text=p.read_text()
  for n in exports:text=re.sub(r'\b'+re.escape(n)+r'\b','l1_'+n[2:],text)
  text=re.sub(r'(EXPORT int l1_\w+\(Regs \*r\)\s*\{)',r'\1 api_timer_fallbacks++;',text)
  text='extern unsigned api_timer_fallbacks;\n'+text
  text=load_cut(hostbuild.composition_source('c/'+p.name,text,units))
  if p.name=='memory.c':text='#include "ugh.h"\nextern uint8_t timing_api_observation[UGH_MEM_SIZE];\n'+text.replace('return ugh_mem;','return timing_api_observation;',1)
  q=folder/p.name;q.write_text(text);sources.append(q)
 for u in units:
  for p in [u['native'],u['bridge']]:
   text=load_cut(hostbuild.composition_source(p.relative_to(ROOT).as_posix(),p.read_text(),units))
   if text!=p.read_text():q=folder/'native'/p.relative_to(ROOT/'native');q.parent.mkdir(parents=True,exist_ok=True);q.write_text(text);sources.append(q)
   else:sources.append(p)
 fixture=folder/'fixture.c';fixture.write_text('''#include "ugh.h"
#ifdef UGH_WORLD_REGISTRY
#include "world_registry_generated.h"
#endif
#include <string.h>
uint8_t timing_api_observation[UGH_MEM_SIZE];
EXPORT unsigned api_timer_fallbacks;EXPORT int api_status,api_stop_at_load;
static unsigned continuing,started;
EXPORT void api_begin(void){continuing=1;started=0;}
EXPORT uint16_t api_live_word(uint16_t bank,uint16_t offset){return rd16(bank,offset);}
EXPORT void api_live_store(uint16_t bank,uint16_t offset,uint16_t value){wr16(bank,offset,value);}
EXPORT uint8_t *api_observe(void){
#ifdef UGH_WORLD_REGISTRY
 world_registry_require_seal(ugh_mem);
#endif
 memcpy(timing_api_observation,ugh_mem,UGH_MEM_SIZE);
#ifdef UGH_WORLD_REGISTRY
 world_registry_serialize(timing_api_observation);
#endif
 return timing_api_observation;
}
static void api_start(void){if(!continuing||!started){memcpy(ugh_mem,timing_api_observation,UGH_MEM_SIZE);
#ifdef UGH_WORLD_REGISTRY
 '''+imports+'''
#endif
 started=1;}}
'''+''.join('EXPORT int api_'+n+'(Regs*r){api_timer_fallbacks=0;api_start();int s='+n+'(r);api_observe();api_status=s;return s;}\n' for n in wrappers))
 sources.append(fixture);fallbacks=folder/'fallbacks.h';fallbacks.write_text('#include "ugh.h"\n'+''.join('int l1_'+n[2:]+'(Regs*);\n' for n in sorted(exports)))
 command=[hostbuild.GCC,'-shared','-O2','-std=c11','-Wall','-Wextra','-Werror','-fwrapv',*hostbuild.composition_options(units,folder/'registry'),'-include',fallbacks,'-I',ROOT/'c','-I',ROOT/'native/bridge','-o',folder/'api.dll',*sources]
 run(command,ROOT,out,'api-'+profile+'-compile');return folder/'api.dll'

def replay(group,cases,out,allowed_rejections=None,worlds_enabled=None):
 import nbuild,difftest
 out=Path(out);profiles={};paths={p:build(p,out,worlds_enabled) for p in ['reference','legacy','composed']}
 for profile in ['legacy','composed']:
  dll=nbuild.load_l1(paths[profile]);machine=difftest.Machine();rows=[]
  for suite,case in cases:
   prior=case.cfunc;case.cfunc='api_'+(prior or 'c_'+case.routine.split(':')[1])
   try:
    for poison in [False,True]:
     problems=difftest.run(case,machine,dll,poison);rows.append(dict(suite=suite,case=case.title,poison=poison,problems=problems,timer_fallbacks=C.c_uint.in_dll(dll,'api_timer_fallbacks').value,status=C.c_int.in_dll(dll,'api_status').value))
   finally:case.cfunc=prior
  profiles[profile]=dict(cases=rows)
 assert all(not r['problems'] for r in profiles['legacy']['cases']),[r for r in profiles['legacy']['cases'] if r['problems']][:3]
 rejects=[r for r in profiles['composed']['cases'] if r['problems']]
 expected={tuple(r) for r in (allowed_rejections or [])};actual={(r['suite'],r['case'],r['poison']) for r in rejects}
 assert actual==expected,dict(new=list(actual-expected),missing=list(expected-actual))
 assert all(r['status'] in [1,3] for r in rejects)
 result=dict(result='PASS',group=group,composed_matching=len(cases)*2-len(rejects),legacy_matching=len(cases)*2,explicit_out_of_domain=rejects,compatibility_cases=[r for r in profiles['composed']['cases'] if r['timer_fallbacks']],profiles=profiles)
 save(out/'receipt.json',result);return result
