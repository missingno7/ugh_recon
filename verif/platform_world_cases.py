"""Compiled platform borrower and defect evidence; generated copies only."""
import ctypes as C,json,sys,re
from pathlib import Path

def libraries(ROOT,OUT,bounded):
 helper=r'''#include "platform.h"
#include <string.h>
typedef struct PlatformsTrace {uint32_t address;uint8_t value,slots[160];} PlatformsTrace;
static PlatformsTrace traces[8192];static unsigned used,enabled;
EXPORT void api_trace_begin(void){used=0;enabled=1;}
EXPORT unsigned api_trace_count(void){return used;}
EXPORT PlatformsTrace *api_trace_data(void){return traces;}
static int owned(uint32_t a){return a>=lin(DATA_SEG,0x290d)&&a<lin(DATA_SEG,0x29ad);}
void api_platforms_notify(uint32_t a,uint8_t v){
 if(!enabled||!owned(a))return;
 if(used==8192)return;
 PlatformsTrace*t=traces+used++;memset(t,0,sizeof *t);t->address=a;t->value=v;
 for(unsigned i=0;i<160;i++)t->slots[i]=rd8(DATA_SEG,(uint16_t)(0x290d+i));
}
void api_device_write(uint32_t,uint8_t);
void ugh_write(uint32_t a,uint8_t v){api_device_write(a,v);
#ifdef UGH_NATIVE_PLATFORMS
 if(owned(a))return;
#endif
 api_platforms_notify(a,v);
}
'''
 folders=[]
 for label in ['reference','composed']:
  folder=OUT/'borrowers'/label;folder.mkdir(parents=True,exist_ok=True);cmd=json.loads((OUT/'children'/('api-input-'+label+'-compile.json')).read_text())['command'];cmd[cmd.index('-o')+1]=str(folder/'api.dll')
  for i,v in enumerate(cmd):
   if not v.endswith('.c'):continue
   p=Path(v);t=p.read_text()
   if p.name=='memory.c':assert t.count('void ugh_write(')==1;t=t.replace('void ugh_write(','void api_device_write(',1)
   elif p.name=='platform_world_bridge.c':
    n='platforms_field_put(fields+slot,lane,value);return 1;';assert t.count(n)==1;t='extern void api_platforms_notify(unsigned int,unsigned char);\n'+t.replace(n,'platforms_field_put(fields+slot,lane,value);api_platforms_notify(address,value);return 1;')
   elif p.name=='dispatch.c':assert t.count('int status=fn(r);')==2;t=t.replace('int status=fn(r);','platform_trace_entry(segment,offset,r); int status=fn(r);')
   else:continue
   q=folder/p.name;q.write_text(t);cmd[i]=str(q)
  q=folder/'trace.c';q.write_text(helper);cmd.append(str(q));bounded(cmd,'borrowers-'+label+'-compile');folders.append(folder)
 return folders

def run(ROOT,OUT,bounded,save):
 import nbuild,difftest
 dlls=[nbuild.load_l1(p/'api.dll') for p in libraries(ROOT,OUT,bounded)]
 class Trace(C.Structure):_fields_=[('address',C.c_uint32),('value',C.c_uint8),('slots',C.c_uint8*160)]
 for d in dlls:
  d.api_trace_data.restype=C.POINTER(Trace);d.api_trace_count.restype=C.c_uint;d.api_live_store.argtypes=[C.c_uint16,C.c_uint16,C.c_uint16]
 m=difftest.Machine();data=m.seg('DGROUP:PlayerCount');rows=[];seeds=[]
 def pair(entry,regs=None,args=(),flags=0x202,stop=False,label=None,follow=(),atomic=False,live=False):
  initial=m.prepare('GAME:'+entry,{**difftest.POISON,'DS':data,**(regs or {})},'far',args,flags);memory=m.snapshot();state=m.device.state();out=[]
  for d in dlls:
   C.memmove(d.ugh_memory().contents,memory,len(memory));d.ugh_devices_reset();dev=d.ugh_device_state().contents;C.memmove(C.addressof(dev),state,len(state));d.api_begin();d.api_trace_begin();C.c_int.in_dll(d,'api_stop_at_load').value=int(stop)
   kind=C.CFUNCTYPE(None,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs));hits=[];errors=[]
   def callback(s,o,rp,d=d):
    try:
     if live and (s,o)==m.address('C:PlayAdlibEffect') and not hits:hits.append((s,o));d.api_live_store(data,0x29ab,0xbeef)
    except BaseException as error:errors.append(repr(error))
   cb=kind(callback);d.ugh_set_entry_observer.argtypes=[kind];d.ugh_set_entry_observer(cb)
   r=difftest.Regs(**{k.lower():v for k,v in initial.items()});f=getattr(d,'api_c_'+entry);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r))
   for child,updates in follow:
    for k,v in updates.items():setattr(r,k,v)
    f=getattr(d,'api_c_'+child);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r))
   d.ugh_set_entry_observer(kind());assert not errors,errors
   ram=bytes(d.ugh_memory().contents);lo=initial['SS']*16;hi=lo+initial['SP'];count=d.api_trace_count();assert count<8192
   stream=C.string_at(d.api_trace_data(),count*C.sizeof(Trace));out.append((status,ram[:lo]+ram[hi:],bytes(dev),None if atomic else stream,hits,ram,stream))
  if [x[:5] for x in out][0]!=[x[:5] for x in out][1]:
   save(OUT/'borrower-difference.json',dict(entry=entry,label=label,first_ram=next((i for i,(a,b) in enumerate(zip(out[0][1],out[1][1])) if a!=b),None),statuses=[x[0] for x in out]));raise AssertionError((entry,label,'full RAM/device/store mismatch'))
  if live:assert out[0][4],(entry,'vacuous live cut');assert out[0][5][data*16+0x29ab:data*16+0x29ad]==b'\xef\xbe'
  rows.append(dict(entry=entry,label=label or entry,status=out[0][0],ordered_byte_stores=len(out[0][6])//C.sizeof(Trace),trace_compared=not atomic,live_cuts=len(out[0][4]),follow=follow));return out[0][5],out[0][6]
 # All shipped logical records; mutate a real source-list spare word without
 # assigning that source record to this owner. The source must stay mutable.
 for players,count in [(1,69),(2,81)]:
  for level in range(count):
   m.reset();m.ww('DGROUP:PlayerCount',players);m.ww('DGROUP:PlayerArrayBytes',2*players);m.ww('DGROUP:CurrentLevelIndex',level)
   table=m.rw('DGROUP:LevelOrderTables',2*(players-1));record=int.from_bytes(m.read(data,table+level*2,2),'little');source=int.from_bytes(m.read(data,record+2,2),'little')
   spare=source+14;before=m.read(data,spare,2);m.write(data,spare,b'\xa7\xd3')
   for a in range(0x290d,0x29ad,2):m.write(data,a,((a*73+level)&65535).to_bytes(2,'little'))
   ram,stream=pair('LoadCurrentLevelState',label=f'load p={players} level={level} mutable source spare')
   assert ram[data*16+spare:data*16+spare+2]==b'\xa7\xd3'
   writes=[Trace.from_buffer_copy(stream[i:i+C.sizeof(Trace)]) for i in range(0,len(stream),C.sizeof(Trace))];assert writes
   seeds.append(dict(players=players,level=level,source=source,spare_before=before.hex(),ordered_stores=[dict(address=w.address,value=w.value) for w in writes]))
 for suite in ['actors','actors_states']:
  for case in difftest.load_suite(suite).CASES:
   if case.routine.split(':')[1] not in ['PlacePassengerOnPlatform','WaitForPassengerPlatform','BoardPassenger','BeginPassengerResurfacing','UpdatePassengerApproach','UpdatePassengerDestinationDisplay','DeliverPassenger']:continue
   m.reset();case.setup(m);regs=case.regs(m) if callable(case.regs) else case.regs
   pair(case.routine.split(':')[1],regs=regs,flags=case.flags or 0x202,label=case.title)
 # Persistent occupancy handoff: no import between these consumers.
 case=next(c for c in difftest.load_suite('actors').CASES if c.routine=='GAME:BoardPassenger')
 m.reset();case.setup(m);regs=case.regs(m) if callable(case.regs) else case.regs
 pair('PlacePassengerOnPlatform',regs=regs,follow=[('BoardPassenger',dict(di=2)),('BeginPassengerResurfacing',{}),('PlacePassengerOnPlatform',{})],label='place-board-resurface-place persistent occupancy')
 # Actual sound-entry cut in delivery, where an unrelated slot can change.
 for case in difftest.load_suite('actors_states').CASES:
  if case.routine!='GAME:DeliverPassenger':continue
  m.reset();case.setup(m);regs=case.regs(m) if callable(case.regs) else case.regs
  # Only sound-reaching cases are claimed as live cuts; all cases are replayed
  # above or by API. This selected branch has a known actual child call.
  if 'delivery reward' not in case.title:continue
  pair('DeliverPassenger',regs=regs,live=True,label=case.title+' live unrelated occupancy');break
 scene=difftest.load_suite('scene')
 for platforms in [((0,319,100),(0,319,100)),((116,116,100),(116,116,100)),((0x8000,319,100),(0,319,100)),tuple((0,319,99+i) for i in range(11))]:
  for slot in [0,2]:
   m.reset();case=scene.move_case(slot=slot,vv=2048,solid=True,platforms=platforms);case.setup(m);pair('MovePlayerWithVgaCollisions',regs=dict(BX=slot),label=f'platform equality/signed/raw list {platforms} slot={slot}')
 for df in [0x202,0x602]:
  m.reset();m.ww('DGROUP:LevelWorkspacePointer',0x2648);m.ww('DGROUP:LevelWorkspacePointer',data,2);pair('InitializeLevelDisplay',stop=True,flags=df,label='multi-owner clear '+hex(df))
 for offset in [0x290c,0x290d,0x2920,0x2998,0x29ab,0x29ad]:
  for delta in [-1,0,1]:
   for count in [0,1,2,20,160]:
    m.reset();pair('CopyFarBytes',args=(count,0,offset,data,(offset+delta)&65535,data),flags=0x602 if delta<0 else 0x202,label=f'physical window {offset:x},{delta},{count}')
 from dataprobe import ice_pack235
 for size in [0x490d,0x4921,0x49ad]:
  m.reset();raw=(bytes(range(256))*(size//256+1))[:size];m.write(0x7500,0,ice_pack235(raw));pair('UnpackIceStream',regs=dict(DS=0x7500,ES=data-0x200,SI=0,DI=0xbeef),atomic=True,label=f'atomic ICE platform window {size:x}')
 assert len(seeds)==150 and any(r['ordered_byte_stores'] for r in rows if r['entry']=='BoardPassenger')
 assert any(r['live_cuts'] for r in rows),'vacuous passenger service mutation'
 save(OUT/'borrowers.json',dict(result='PASS',cases=rows,level_seed_prefixes=seeds,scope='Independent compiled L1/native: full RAM outside ABI scratch stack, full Devices/ordered ports and ordered platform-byte stores with complete live160-byte snapshots. All150 logical level seeds; mutable source spare words, occupancy handoff, consumer policies, raw11-entry aliases, DF reset and copy/ICE views. Atomic ICE returned-state exception explicit.'))

def defects(ROOT,OUT,bounded,save,snapshot,previous):
 import wholegame
 folder=OUT/'defects';folder.mkdir(exist_ok=True);capture=folder/'capture.py';capture.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n')
 rows=[]
 for fault,name in [(1,'stale-occupancy'),(2,'slot-alias'),(3,'cleared-high-lane'),(4,'missed-serialization')]:
  exe=folder/(name+'.exe');bounded([previous.timing.common.GCC,'-O2','-std=c11','-DPLATFORMS_TEST_FAULT='+str(fault),'-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/platform_world_router.c',ROOT/'native/platform_world.c',ROOT/'native/bridge/platform_world_bridge.c'],'defect-router-'+name+'-compile')
  r=json.loads(bounded([sys.executable,capture,exe],'defect-router-'+name+'-run')['stdout']);assert r['returncode']!=0
  if fault==4:assert r['returncode']==88 and 'missed serialization' in r['stderr']
  rows.append(dict(defect=name,scope='Independent compiled byte-router',result='DETECTED',exit=r['returncode']))
 for tag in ['boarding','resurfacing','last-equal','exclusive-edge','wrong-sentinel','recomputed-index']:
  dest=folder/tag;dest.mkdir(exist_ok=True);cmd=json.loads((OUT/'children/api-input-composed-compile.json').read_text())['command'];cmd[cmd.index('-o')+1]=str(dest/'api.dll');changed=False
  for i,v in enumerate(cmd):
   if not v.endswith('.c'):continue
   p=Path(v);t=p.read_text();old=t
   if tag in ['boarding','resurfacing'] and p.name=='platform_world_bridge.c':
    n=' platforms_field_put(fields+slot,lane,value);return 1;';assert t.count(n)==1
    guard=' if(address>=A(PlatformActorOccupants) && address<A(PlatformActorOccupants)+20u'+(' && value==255' if tag=='resurfacing' else '')+'){return 1;}\n'
    t=t.replace(n,guard+n)
   elif tag=='recomputed-index' and p.name=='player_world_bridge.c':
    # PlayerPlatformIndices is owned and read through the player world in
    # composed mode; the old platform borrow hook is bypassed after registry
    # routing. Corrupt the actual owner read consumed by MovePlayerWithVgaCollisions.
    n='return (uint8_t)(value>>shift);';assert t.count(n)==1
    t=t.replace(n,'if(field->member==offsetof(NativePlayerWorld,player[0].platform))value=0;\n '+n)
   elif tag in ['last-equal','exclusive-edge','wrong-sentinel'] and p.name=='player_physics.c':
    if tag=='last-equal':
     n='if(decision)return (int)i;';assert t.count(n)==1;t=t.replace(n,'if(decision){int found=(int)i;for(size_t j=i+1;j<w->platform_count;j++){int next=pp_platform_decision(&w->platforms[j],height,center);if(next<0)break;if(next)found=(int)j;}return found;}')
    elif tag=='exclusive-edge':
     n='pp_signed(center)>=pp_signed(platform->left)';assert t.count(n)==1;t=t.replace(n,'pp_signed(center)>pp_signed(platform->left)')
    else:
     n='if(pp_signed(platform->left)<0)return -1;';assert t.count(n)==1;t=t.replace(n,'if(platform->left==65535u)return -1;')
   if t!=old:q=dest/p.name;q.write_text(t);cmd[i]=str(q);changed=True
  assert changed,tag
  guard=dest/'control.h';guard.write_text('#include <stdio.h>\n#include <stdlib.h>\n_Noreturn static inline void control_abort(void){fputs("PLATFORM_CONTROL_BRIDGE_ASSERT\\n",stderr);exit(87);}\n#define abort control_abort\n');cmd[1:1]=['-I',str(ROOT/'native'),'-include',str(guard)];bounded(cmd,'defect-api-'+tag+'-compile')
  script=dest/'consume.py';script.write_text('import sys\nsys.path[:0]='+repr([str(ROOT/'verif'),str(ROOT/'tools')])+'\nfrom pathlib import Path\nfrom platform_world_cases import check_mutant\ncheck_mutant(Path('+repr(str(ROOT))+'),Path('+repr(str(OUT))+'),'+repr(tag)+',Path('+repr(str(dest/'api.dll'))+'))\n')
  r=json.loads(bounded([sys.executable,capture,sys.executable,script],'defect-api-'+tag+'-run')['stdout']);assert r['returncode']==87 and 'PLATFORM_CONTROL_BRIDGE_ASSERT' in r['stderr'] or r['returncode']==0 and 'DETECTED' in r['stdout'],(tag,r)
  rows.append(dict(defect=tag,result='DETECTED',scope='Independent compiled L1 versus composed API',diagnostic=r['stdout']+r['stderr'],exit=r['returncode']))
 target=snapshot()
 for fault,name in [(1,'stale-occupancy'),(4,'missed-serialization')]:
  dest=folder/('host-'+name);hc=previous.copy_host(target,dest);p=dest/'tools/hostbuild.py';t=p.read_text();n="return (['-DUGH_NATIVE_PLATFORMS']";assert t.count(n)==1;p.write_text(t.replace(n,"return (['-DPLATFORMS_TEST_FAULT="+str(fault)+"','-DUGH_NATIVE_PLATFORMS']",1))
  for p in (dest/'native/bridge').glob('*'):
   if p.suffix in ['.c','.h'] and 'abort()' in p.read_text():p.write_text('#include <stdio.h>\n#include <stdlib.h>\n'+p.read_text().replace('abort()','(fputs("PLATFORM_CONTROL_BRIDGE_ASSERT\\n",stderr),exit(87))'))
  bounded([sys.executable,'tools/hostbuild.py'],'defect-host-'+name+'-build',dest);script=target/'tests/scenarios/passenger.txt';ref=json.loads((target/'build/whole/passenger.ref.json').read_text())['frames']
  r=json.loads(bounded([sys.executable,hc,dest/'build/host/ugh.exe','--headless',str(wholegame.scenario(script)['frames']),'--script',script,'--timeout','590'],'defect-host-'+name+'-run')['stdout']);frames=[json.loads(x) for x in r['stdout'].splitlines()];first=next((i for i,(a,b) in enumerate(zip(frames,ref)) if a!=b),None)
  assert first is not None or r['returncode'] in [87,88],(name,r)
  rows.append(dict(defect=name,result='DETECTED',scenario='passenger',frame=first+1 if first is not None else len(frames)+1,exit=r['returncode']))
 save(OUT/'defects.json',dict(result='PASS',controls=rows,scope='Four byte-route defects, consuming boarding/resurfacing occupancy, last-equal selection, exclusive boundary, wrong negative sentinel and recomputed cached index API mutants; two whole-host controls. All changes generated copies only.'))

def check_mutant(ROOT,OUT,tag,path):
 import nbuild,difftest
 dlls=[nbuild.load_l1(OUT/'borrowers/reference/api.dll'),nbuild.load_l1(path)];m=difftest.Machine();data=m.seg('DGROUP:PlayerCount');scene=difftest.load_suite('scene')
 if tag in ['boarding','resurfacing']:
  name='BoardPassenger' if tag=='boarding' else 'BeginPassengerResurfacing';cases=[c for s in ['actors','actors_states'] for c in difftest.load_suite(s).CASES if c.routine=='GAME:'+name]
 else:
  ps=((0,319,100),(0,319,100)) if tag=='last-equal' else ((116,116,100),) if tag=='exclusive-edge' else ((0x8000,319,100),(0,319,100))
  cases=[scene.move_case(tag,vv=2048,solid=True,platforms=ps),scene.move_case(tag,platform=3,vv=1)]
 for case in cases:
  m.reset();case.setup(m);regs=case.regs(m) if callable(case.regs) else case.regs
  if tag in ['boarding','resurfacing']:
   actor=regs['BX'];source=m.rw('DGROUP:ActorSourcePlatformByteIndices',actor)
   m.ww('DGROUP:PlatformActorOccupants',actor,source)
   assert m.rw('DGROUP:PlatformActorOccupants',source)!=65535,'vacuous occupancy-clear fixture'
  entry=case.routine.split(':')[1];initial=m.prepare(case.routine,{**difftest.POISON,**regs},'far',(),0x202);memory=m.snapshot();state=m.device.state();out=[]
  for d in dlls:
   C.memmove(d.ugh_memory().contents,memory,len(memory));d.ugh_devices_reset();dev=d.ugh_device_state().contents;C.memmove(C.addressof(dev),state,len(state));d.api_begin();r=difftest.Regs(**{k.lower():v for k,v in initial.items()});fn=getattr(d,'api_c_'+entry);fn.argtypes=[C.POINTER(difftest.Regs)];status=fn(C.byref(r));ram=bytes(d.ugh_memory().contents);lo=initial['SS']*16;hi=lo+initial['SP'];out.append((status,ram[:lo]+ram[hi:],bytes(dev),r.di))
  if out[0]!=out[1]:print('DETECTED',tag,case.title,flush=True);return
 raise AssertionError((tag,'survived consuming comparator'))

def deepcounts(ROOT,OUT,bounded,save,snapshot,previous):
 import os,wholegame
 from closure_support import function
 target=snapshot();folder=OUT/'deep-counts';capture=previous.copy_host(target,folder);names=['BoardPassenger','DeliverPassenger','PlacePassengerOnPlatform','BeginPassengerResurfacing','WaitForPassengerPlatform']
 (folder/'host/platform_counts.c').write_text('#include <stdio.h>\n#include <stdlib.h>\nstatic unsigned long long counts[5];static void dump(void){const char*p=getenv("PLATFORM_COUNTS");if(!p)return;FILE*f=fopen(p,"w");if(!f)exit(87);for(unsigned i=0;i<5;i++)fprintf(f,"%llu\\n",counts[i]);fclose(f);}\nvoid platform_count(unsigned i){static int ready;if(!ready){atexit(dump);ready=1;}counts[i]++;}\n')
 for bridge,selected in [('passenger_delivery',names[:2]),('passenger_itinerary',names[2:3]+names[4:]),('passenger_water',names[3:4])]:
  p=folder/('native/bridge/'+bridge+'_bridge.c');t=p.read_text();wrappers=[]
  for name in selected:
   body=function(t,'c_'+name);t=t.replace(body,body.replace('c_'+name+'(','counted_'+name+'(',1));wrappers.append('EXPORT int c_'+name+'(Regs*r){platform_count('+str(names.index(name))+');return counted_'+name+'(r);}\n')
  p.write_text('extern void platform_count(unsigned);\n'+t+'\n'+''.join(wrappers))
 bounded([sys.executable,'tools/hostbuild.py'],'deep-counts-build',folder);rows=[]
 for path in sorted((target/'tests/levels-deep').glob('*.txt')):
  # Same LF/CRLF provenance reconstruction as the accepted level driver.
  ref=json.loads((target/'build/levels-deep'/(path.stem+'.ref.json')).read_text());counter=folder/(path.stem+'.counts');os.environ['PLATFORM_COUNTS']=str(counter)
  try:r=bounded([sys.executable,capture,folder/'build/host/ugh.exe','--headless',str(wholegame.scenario(path)['frames']),'--script',path,'--timeout','590'],'deep-counts-'+path.stem)
  finally:os.environ.pop('PLATFORM_COUNTS',None)
  actual=json.loads(r['stdout']);assert actual['returncode']==0,actual['stderr'];assert [json.loads(x) for x in actual['stdout'].splitlines()]==ref['frames'],path.stem
  counts=dict(zip(names,map(int,counter.read_text().splitlines())));rows.append(dict(scenario=path.stem,entries=counts,frames=len(ref['frames'])))
 assert len(rows)==8 and sum(r['entries']['BoardPassenger'] for r in rows)>0 and sum(r['entries']['DeliverPassenger'] for r in rows)>0
 save(OUT/'deep-counts.json',dict(result='PASS',runs=rows,scope='Generated entry-only counters, every frame matches independent ASM deep references; explicit boarding/delivery/occupancy routine counts and zeros.'))
