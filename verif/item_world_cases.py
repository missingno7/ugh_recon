"""Compiled item storage borrowers, failure prefixes, controls and entry census.

L1 independently checks boundary RAM/devices/ports and common service entries.
The accepted item adapter publishes an atomic result, so its internal byte-store
order is compared between the legacy native adapter and the composed adapter,
not misrepresented as L1 instruction-by-instruction store equality.
"""
import ctypes as C,json,re,sys,shutil,os
from pathlib import Path

START,END,SIZE=0x2d6b,0x2e8b,288

def libraries(ROOT,OUT,bounded):
 helper=r'''#include "platform.h"
#include <string.h>
typedef struct ItemTrace {uint32_t address;uint8_t value,slots[288];} ItemTrace;
EXPORT int api_fail_item,api_item_flight;
static ItemTrace traces[16384];static unsigned used,enabled;
EXPORT void api_trace_begin(void){used=0;enabled=1;}
EXPORT unsigned api_trace_count(void){return used;}
EXPORT ItemTrace *api_trace_data(void){return traces;}
static int owned(uint32_t a){return a>=lin(DATA_SEG,0x2d6b)&&a<lin(DATA_SEG,0x2e8b);}
void api_items_notify(uint32_t a,uint8_t v){
 if(!enabled||!owned(a))return;
 if(used==16384)return;
 ItemTrace*t=traces+used++;memset(t,0,sizeof *t);t->address=a;t->value=v;
 for(unsigned i=0;i<288;i++)t->slots[i]=rd8(DATA_SEG,(uint16_t)(0x2d6b+i));
}
void api_items_native_notify(uint8_t *window,uint32_t index){
 uintptr_t p=(uintptr_t)window,base=(uintptr_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE)api_items_notify((uint32_t)(p-base+index),window[index]);
}
void api_device_write(uint32_t,uint8_t);
void ugh_write(uint32_t a,uint8_t v){api_device_write(a,v);
#ifdef UGH_NATIVE_ITEMS
 if(owned(a))return;
#endif
 api_items_notify(a,v);
}
'''
 folders=[]
 for label in ['reference','legacy','composed']:
  folder=OUT/'borrowers'/label;folder.mkdir(parents=True,exist_ok=True)
  cmd=json.loads((OUT/'children'/('api-input-'+label+'-compile.json')).read_text())['command'];cmd[cmd.index('-o')+1]=str(folder/'api.dll')
  for i,v in enumerate(cmd):
   if not v.endswith('.c'):continue
   p=Path(v);t=p.read_text()
   if p.name=='memory.c':
    assert t.count('void ugh_write(')==1;t=t.replace('void ugh_write(','void api_device_write(',1)
   elif p.name=='item_world_bridge.c':
    needle='itemstate_field_put(fields+slot,lane,value);return 1;';assert t.count(needle)==1
    t='extern void api_items_notify(unsigned int,unsigned char);\n'+t.replace(needle,'itemstate_field_put(fields+slot,lane,value);api_items_notify(address,value);return 1;')
   elif p.name=='dispatch.c':
    assert t.count('int status=fn(r);')==2;t=t.replace('int status=fn(r);','platform_trace_entry(segment,offset,r); int status=fn(r);')
   elif p.name=='far_copy.c' and 'destination[destination_cursor]=source[source_cursor];' in t:
    t='extern void api_items_native_notify(unsigned char*,unsigned int);\n'+t.replace('destination[destination_cursor]=source[source_cursor];','destination[destination_cursor]=source[source_cursor];api_items_native_notify(destination,destination_cursor);')
   # A real synchronous callback failure at the first selected item, before
   # any item algorithm runs. The dispatcher must return without publication.
   pattern=r'(EXPORT int c_LandFallingItem\(Regs \*r\)\s*\{)'
   if re.search(pattern,t):t='extern int api_fail_item;\n'+re.sub(pattern,r'\1 if(api_fail_item)return UGH_BUDGET;',t,count=1)
   # L1's landing tail is inlined by the accepted flight adapter. Count the
   # dispatcher callback stream separately from that internal algorithm edge.
   signature='EXPORT int c_AdvanceFallingItem(Regs *r)'
   if signature in t:
    t=t.replace(signature,'EXPORT int traced_advance_body(Regs *r)',1)
    t+='\nextern int api_item_flight;EXPORT int c_AdvanceFallingItem(Regs*r){api_item_flight++;int status=traced_advance_body(r);api_item_flight--;return status;}\n'
   t=re.sub(r'#include "([^"]+)"',lambda m:'#include "'+p.parent.joinpath(m[1]).resolve().as_posix()+'"' if p.parent.joinpath(m[1]).is_file() else m[0],t)
   q=folder/str(i)/p.name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(t);cmd[i]=str(q)
  q=folder/'trace.c';q.write_text(helper);cmd.append(str(q));bounded(cmd,'borrowers-'+label+'-compile');folders.append(folder)
 return folders

def execute(ROOT,OUT,dlls,m,entry,regs=None,label=None,follow=(),fail=False,live=False,stop=False,flags=0x202,rows=None,atomic=False,args=()):
 import difftest
 data=m.seg('DGROUP:PlayerCount')
 initial=m.prepare('GAME:'+entry,{**difftest.POISON,'DS':data,**(regs or {})},'far',args,flags)
 memory=m.snapshot();device=m.device.state();out=[]
 class Trace(C.Structure):_fields_=[('address',C.c_uint32),('value',C.c_uint8),('slots',C.c_uint8*SIZE)]
 services={m.address('GAME:'+n) for n in ['SpawnFallingItem','AdvanceFallingItem','LandFallingItem','ExpireOrCollectFallingItem','DrawTransparentSprite','RestoreSpriteBackground']}
 for d in dlls:
  d.api_trace_data.restype=C.POINTER(Trace);d.api_trace_count.restype=C.c_uint
  d.api_live_store.argtypes=[C.c_uint16,C.c_uint16,C.c_uint16]
  C.memmove(d.ugh_memory().contents,memory,len(memory));d.ugh_devices_reset();dev=d.ugh_device_state().contents;C.memmove(C.addressof(dev),device,len(device));d.api_begin();d.api_trace_begin()
  C.c_int.in_dll(d,'api_stop_at_load').value=int(stop);C.c_int.in_dll(d,'api_fail_item').value=int(fail)
  kind=C.CFUNCTYPE(None,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs));entries=[];hits=[];errors=[]
  def callback(s,o,rp,d=d):
   try:
    internal_landing=(s,o)==m.address('GAME:LandFallingItem') and C.c_int.in_dll(d,'api_item_flight').value
    if (s,o) in services and not internal_landing:entries.append((s,o,rp.contents.bx))
    if live and (s,o)==m.address('GAME:LandFallingItem') and not hits:
     hits.append((s,o));d.api_live_store(data,0x2e13,0xbeef)
   except BaseException as error:errors.append(repr(error))
  cb=kind(callback);d.ugh_set_entry_observer.argtypes=[kind];d.ugh_set_entry_observer(cb)
  r=difftest.Regs(**{k.lower():v for k,v in initial.items()});f=getattr(d,'api_c_'+entry);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r))
  for child,updates in follow:
   for k,v in updates.items():setattr(r,k,v)
   f=getattr(d,'api_c_'+child);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r))
  d.ugh_set_entry_observer(kind());assert not errors,errors
  ram=bytes(d.ugh_memory().contents);lo=initial['SS']*16;hi=lo+initial['SP'];count=d.api_trace_count();assert count<16384
  stream=C.string_at(d.api_trace_data(),count*C.sizeof(Trace))
  out.append(dict(status=status,ram=ram[:lo]+ram[hi:],devices=bytes(dev),entries=entries,hits=hits,trace=stream,full_ram=ram,fallbacks=C.c_uint.in_dll(d,'api_timer_fallbacks').value))
 keys=['status','ram','devices','entries','hits']
 if any([r[k] for k in keys]!=[out[0][k] for k in keys] for r in out[1:]):
  save=__import__('job_pool').save
  save(OUT/'borrower-difference.json',dict(entry=entry,label=label,status=[r['status'] for r in out],first_ram=[next((i for i,(a,b) in enumerate(zip(out[0]['ram'],r['ram'])) if a!=b),None) for r in out],entries=[r['entries'] for r in out]));raise AssertionError((entry,label,'L1 boundary RAM/device/service mismatch'))
 if not atomic:assert out[1]['trace']==out[2]['trace'],(entry,label,'legacy/composed store order mismatch')
 if live:
  assert all(r['hits'] for r in out),'vacuous live callback cut'
  assert all(r['full_ram'][data*16+0x2e13:data*16+0x2e15]==b'\xef\xbe' for r in out),'stale parent overwrite'
 if fail:assert out[0]['status']==2 and len(out[0]['entries'])==1,'failure prefix not observed'
 row=dict(entry=entry,label=label or entry,status=out[0]['status'],service_entries=out[0]['entries'],live_cuts=len(out[0]['hits']),ordered_owner_stores=len(out[-1]['trace'])//C.sizeof(Trace),store_trace_compared=not atomic,compatibility_fallbacks=[r['fallbacks'] for r in out[1:]],follow=follow)
 if rows is not None:rows.append(row)
 return out

def landed(m,slot=0,lifetime=5,kind=0,amount=7000,contact=True):
 data=m.seg('DGROUP:PlayerCount');desc=m.off('DGROUP:FallingDescriptor_7A38')
 m.write(data,0x6300,m.read(data,desc,20));m.write(data,0x6300+18,kind.to_bytes(2,'little'));m.write(data,0x6300+14,amount.to_bytes(2,'little'))
 for i in range(12):
  m.ww('DGROUP:FallingItemSprites',0xffff,2*i)
  for n in ['FallingItemEraseSprite','FallingItemDrawX','FallingItemDrawY','FallingItemPreviousDrawX','FallingItemPreviousDrawY']:
   m.ww('DGROUP:'+n,0xa131+2*i,2*i)
 for n,v in [('FallingItemDescriptors',0x6300),('FallingItemCallbacks',m.off('GAME:ExpireOrCollectFallingItem')),('FallingItemSprites',297),('FallingItemX',3200),('FallingItemY',2560),('FallingItemMotionOrLifetime',lifetime)]:m.ww('DGROUP:'+n,v,slot*2)
 for i in range(2):
  m.ww('DGROUP:PlayerX32',3200,2*i);m.ww('DGROUP:PlayerY32',2560 if contact else 0x6000,2*i)
 m.ww('DGROUP:PlayerCount',2);m.ww('DGROUP:PlayerArrayBytes',4);m.ww('DGROUP:LevelTimer',23098);m.ww('DGROUP:ScoreMultiplier',2);m.ww('DGROUP:SelectedDifficulty',0);m.wb('DGROUP:LivesRemaining',98)

def run(ROOT,OUT,bounded,save):
 import nbuild,difftest
 dlls=[nbuild.load_l1(p/'api.dll') for p in libraries(ROOT,OUT,bounded)]
 m=difftest.Machine();data=m.seg('DGROUP:PlayerCount');rows=[]
 def pair(entry,**kwargs):return execute(ROOT,OUT,dlls,m,entry,rows=rows,**kwargs)
 # All shipped session seeds preserve stale per-slot fields and history.
 for players,count in [(1,69),(2,81)]:
  for level in range(count):
   m.reset();m.ww('DGROUP:PlayerCount',players);m.ww('DGROUP:PlayerArrayBytes',2*players);m.ww('DGROUP:CurrentLevelIndex',level)
   for a in range(START,END,2):m.write(data,a,((a*73+level)&65535).to_bytes(2,'little'))
   pair('LoadCurrentLevelState',label=f'load p={players} level={level}')
 relevant={'SpawnFallingItem','AdvanceFallingItem','LandFallingItem','ExpireOrCollectFallingItem','DispatchFallingItems','FindPlayerTouchingFallingItem','ResetSpriteEraseState','EraseDemoSprites','ReleaseTreeReward','DeliverPassenger'}
 for suite in ['actors','actors_states','items_water','render']:
  for case in difftest.load_suite(suite).CASES:
   entry=case.routine.split(':')[1]
   if entry not in relevant:continue
   m.reset();case.setup(m) if case.setup else None;regs=case.regs(m) if callable(case.regs) else case.regs
   pair(entry,regs=regs,label=case.title,flags=case.flags or 0x202)
 for slot in range(12):
  for ticks in [0,1,2,0x7fff,0x8000,0xffff]:
   for contact in [False,True]:
    for benefit in [0,1,2]:
     m.reset();landed(m,slot,ticks,benefit,0xffff,contact)
     pair('DispatchFallingItems',label=f'slot={slot} lifetime={ticks:x} benefit={benefit} contact={contact}',follow=[('DispatchFallingItems',{})])
 # Mixed live callbacks in descending order, including a mutation of an unrelated
 # retained history at an actual callback cut; no parent snapshot may win later.
 for fail in [False,True]:
  m.reset();landed(m,11,4)
  m.ww('DGROUP:FallingItemCallbacks',m.off('GAME:LandFallingItem'),22)
  m.ww('DGROUP:FallingItemSprites',0xfffe,0);m.ww('DGROUP:FallingItemCallbacks',m.off('GAME:LandFallingItem'),0);m.ww('DGROUP:FallingItemDescriptors',m.off('DGROUP:Data_7970'),0)
  pair('DispatchFallingItems',label='live callback mutation failure='+str(fail),fail=fail,live=True)
 for flags in [0x202,0x602]:
  m.reset();m.ww('DGROUP:LevelWorkspacePointer',0x2648);m.ww('DGROUP:LevelWorkspacePointer',data,2)
  pair('InitializeLevelDisplay',stop=True,flags=flags,label='ordered multi-owner clear '+hex(flags))
 # Byte windows are already exhaustive in the router. These exercise real
 # far-copy/ICE adapters and their shared owner routing at both item edges.
 for at in [START-1,START,START+23,0x2e5b,END-1,END]:
  for delta in [-1,0,1]:
   for count in [0,1,2,24,288]:
    m.reset()
    pair('CopyFarBytes',args=(count,0,at,data,(at+delta)&65535,data),flags=0x602 if delta<0 else 0x202,label=f'copy window {at:x},{delta},{count}')
 from dataprobe import ice_pack235
 for size in [0x4d6b,0x4e13,0x4e8b]:
  m.reset();raw=(bytes(range(256))*(size//256+1))[:size];m.write(0x7500,0,ice_pack235(raw))
  pair('UnpackIceStream',regs=dict(DS=0x7500,ES=data-0x200,SI=0,DI=0xbeef),atomic=True,label='atomic ICE item window '+hex(size))
 assert any(r['service_entries'] for r in rows) and any(r['live_cuts'] for r in rows)
 assert any(r['ordered_owner_stores'] for r in rows)
 save(OUT/'borrowers.json',dict(result='PASS',cases=rows,level_seeds=150,scope=__doc__))

def deepcounts(ROOT,OUT,bounded,save):
 import wholegame
 from closure_support import function
 folder=OUT/'counts-host';folder.mkdir(exist_ok=True)
 for top in ['c','native','host','metadata','tools','src','tests','verif']:shutil.copytree(ROOT/top,folder/top,dirs_exist_ok=True)
 shutil.copytree(ROOT/'build/link',folder/'build/link',dirs_exist_ok=True)
 names=['SpawnFallingItem','AdvanceFallingItem','LandFallingItem','ExpireOrCollectFallingItem','DispatchFallingItems','FindPlayerTouchingFallingItem','item_land']
 (folder/'host/item_counts.c').write_text('#include <stdio.h>\n#include <stdlib.h>\nstatic unsigned long long counts[7];static void dump(void){const char*p=getenv("ITEM_COUNTS");if(!p)return;FILE*f=fopen(p,"w");if(!f)exit(87);for(unsigned i=0;i<7;i++)fprintf(f,"%llu\\n",counts[i]);fclose(f);}\n__attribute__((constructor)) static void begin(void){atexit(dump);}\nvoid item_count(unsigned i){counts[i]++;}\n')
 for bridge,selected in [('items',names[:5]),('contacts',names[5:6])]:
  p=folder/('native/bridge/'+bridge+'_bridge.c');text=p.read_text();wrappers=[]
  for name in selected:
   body=function(text,'c_'+name);text=text.replace(body,body.replace('c_'+name+'(','counted_'+name+'(',1));wrappers.append('EXPORT int c_'+name+'(Regs*r){item_count('+str(names.index(name))+');return counted_'+name+'(r);}\n')
  p.write_text('extern void item_count(unsigned);\n'+text+'\n'+''.join(wrappers))
 p=folder/'native/items.c';text=p.read_text();body=function(text,'item_land')
 p.write_text('extern void item_count(unsigned);\n'+text.replace(body,body.replace('{','{item_count(6);',1)))
 bounded([sys.executable,'tools/hostbuild.py','--out',folder/'host-output'],'counts-build',folder);rows=[]
 for group,scripts,bank in [('whole','tests/scenarios','build/whole'),('openings','tests/levels','build/levels'),('audio','tests/levels-audio','build/levels-audio'),('deep','tests/levels-deep','build/levels-deep')]:
  for path in sorted((ROOT/scripts).glob('*.txt')):
   ref=json.loads((ROOT/bank/(path.stem+'.ref.json')).read_text())['frames'];counter=folder/(group+'-'+path.stem+'.counts');env=dict(os.environ,ITEM_COUNTS=str(counter))
   result=bounded([folder/'host-output/ugh.exe','--headless',str(wholegame.scenario(path)['frames']),'--script',path,'--timeout','590'],'counts-'+group+'-'+path.stem,env=env)
   actual=[json.loads(line) for line in result['stdout'].splitlines()];assert actual==ref,path.stem
   rows.append(dict(group=group,scenario=path.stem,frames=len(ref),entries=dict(zip(names,map(int,counter.read_text().splitlines())))))
 assert len(rows)==116
 for name in [names[i] for i in [0,1,3,4,6]]:assert sum(r['entries'][name] for r in rows)>0,name
 import difftest
 witnesses={name:[dict(suite=suite,case=case.title) for suite in ['items_water','actors'] for case in difftest.load_suite(suite).CASES if case.routine=='GAME:'+name] for name in [names[2],names[5]]}
 assert all(witnesses.values()),'unwitnessed zero-entry adapter'
 save(OUT/'deep-counts.json',dict(result='PASS',runs=rows,api_witnesses=witnesses,scope='Entry counters over20 scenarios and81+7+8 level runs. All independent frames equal. Native item_land is counted positively. Landing and contact adapter zero counts are explicit: accepted flight/collection inline those policies. The named direct API witnesses are included in the independently replayed world API stage.'))

def defects(ROOT,OUT,bounded,save):
 import nbuild,difftest
 from closure_support import GCC,function
 folder=OUT/'defects';folder.mkdir(exist_ok=True);rows=[]
 for fault,name in [(1,'lost-motion-lifetime'),(2,'slot-alias'),(3,'cleared-high-lane'),(4,'missed-serialization')]:
  exe=folder/(name+'.exe')
  bounded([GCC,'-O2','-std=c11','-DITEMSTATE_TEST_FAULT='+str(fault),'-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/item_world_router.c',ROOT/'native/item_world.c',ROOT/'native/bridge/item_world_bridge.c'],'control-'+name+'-compile')
  result=bounded([exe],'control-'+name,ok=tuple(range(1,17))+(88,))
  rows.append(dict(defect=name,result='DETECTED',exit=result['returncode'],scope='Independent literal member/address/word oracle'))
  if fault==4:
   host=folder/'serializer-host';host.mkdir(exist_ok=True)
   for top in ['c','native','host','metadata','tools','src','tests','verif']:shutil.copytree(ROOT/top,host/top,dirs_exist_ok=True)
   shutil.copytree(ROOT/'build/link',host/'build/link',dirs_exist_ok=True)
   p=host/'metadata/worlds/item_world.json';registry=json.loads(p.read_text());registry['compile_flags'].append('-DITEMSTATE_TEST_FAULT=4');save(p,registry)
   bounded([sys.executable,'tools/hostbuild.py','--no-generate','--out',host/'host-output'],'control-serializer-host-build',host)
   result=bounded([host/'host-output/ugh.exe','--headless','4','--script',ROOT/'tests/scenarios/items-timer.txt','--timeout','590'],'control-serializer-host',ok=(88,))
   assert 'itemstate: missed serialization' in result['stderr'],result
   rows[-1]['boundary_control']=dict(scenario='items-timer',exit=88,diagnostic=result['stderr'])
 for tag in ['reverse-descending-pass','collect-twice','stale-timer-after-award','normalize-motion-lifetime','clear-inactive-erase-history','publish-after-service-failure','stale-parent-overwrite']:
  dest=folder/tag;dest.mkdir(exist_ok=True)
  command=json.loads((OUT/'children/borrowers-composed-compile.json').read_text())['command'];command[command.index('-o')+1]=str(dest/'api.dll');changed=[]
  for i,v in enumerate(command):
   if not v.endswith('.c'):continue
   p=Path(v);text=p.read_text();before=text
   if p.name=='items.c' and tag=='collect-twice':
    needle='item->sprite=65535u;return result;';at=text.rindex(needle);text=text[:at]+text[at:].replace(needle,'return result;',1)
   if p.name=='item_world_bridge.c':
    if tag=='normalize-motion-lifetime':
     needle='return (uint8_t)(value>>shift);';assert text.count(needle)==1
     text=text.replace(needle,'if(field->member==offsetof(NativeItemWorld,slot[0].motion_or_lifetime)){value&=32767u;}\n'+needle)
    if tag=='clear-inactive-erase-history':
     needle='itemstate_field_put(fields+slot,lane,value);api_items_notify(address,value);return 1;';assert text.count(needle)==1
     text=text.replace(needle,'itemstate_field_put(fields+slot,lane,value);if(slot==2 && (lane&1) && native_item_world()->slot[lane/2].sprite==65535u){native_item_world()->slot[lane/2].erase_sprite=65535u;}api_items_notify(address,value);return 1;')
   if p.name=='items_bridge.c':
    if tag=='stale-timer-after-award':
     needle='itemstate_write16(r->ds,D(LevelTimer),benefits.timer);';assert text.count(needle)==1
     text=text.replace(needle,needle+'itemstate_write16(r->ds,D(LevelTimer),before.timer);')
    if tag=='reverse-descending-pass':
     body=function(text,'c_DispatchFallingItems')
     text=text.replace(body,'EXPORT int c_DispatchFallingItems(Regs*r){for(unsigned i=0;i<12;i++){r->bx=(uint16_t)(i*2);if(item_word(r,D(FallingItemSprites),r->bx)==65535u)continue;uint16_t target=item_word(r,D(FallingItemCallbacks),r->bx);int status=ugh_call_near(target,(uint16_t)(G(DispatchFallingItems)+17),r);if(status)return status;}return UGH_OK;}')
    if tag in ['publish-after-service-failure','stale-parent-overwrite']:
     body=function(text,'c_DispatchFallingItems');mutant=body
     if tag=='publish-after-service-failure':
      needle='if(status) return status;';assert mutant.count(needle)==1
      mutant=mutant.replace(needle,'if(status){itemstate_write16(r->ds,(uint16_t)(D(FallingItemSprites)+r->bx),65535u);return status;}')
     else:
      needle='uint16_t target=item_word';assert mutant.count(needle)==1
      mutant=mutant.replace(needle,'uint16_t old_history=itemstate_read16(r->ds,D(FallingItemPreviousDrawX));'+needle)
      needle='if(status) return status;';assert mutant.count(needle)==1
      mutant=mutant.replace(needle,'itemstate_write16(r->ds,D(FallingItemPreviousDrawX),old_history);'+needle)
     text=text.replace(body,mutant)
   if text!=before:q=dest/p.name;q.write_text(text);command[i]=str(q);changed.append(p.name)
  assert changed,tag
  bounded(command,'control-'+tag+'-compile')
  dlls=[nbuild.load_l1(OUT/'borrowers/reference/api.dll'),nbuild.load_l1(OUT/'borrowers/legacy/api.dll'),nbuild.load_l1(dest/'api.dll')]
  m=difftest.Machine();m.reset();landed(m,11,0x8001 if tag=='normalize-motion-lifetime' else 4,0,3000)
  m.ww('DGROUP:LevelTimer',1000);follow=();live=False;fail=False
  if tag in ['reverse-descending-pass','publish-after-service-failure','stale-parent-overwrite']:
   m.ww('DGROUP:FallingItemCallbacks',m.off('GAME:LandFallingItem'),22)
   m.ww('DGROUP:FallingItemSprites',0xfffe,0);m.ww('DGROUP:FallingItemCallbacks',m.off('GAME:LandFallingItem'),0);m.ww('DGROUP:FallingItemDescriptors',m.off('DGROUP:Data_7970'),0)
  if tag=='publish-after-service-failure':fail=True
  if tag=='stale-parent-overwrite':live=True
  if tag=='collect-twice':follow=[('DispatchFallingItems',{})]
  try:execute(ROOT,dest,dlls,m,'DispatchFallingItems',label=tag,fail=fail,live=live,follow=follow)
  except AssertionError as error:
   assert 'L1 boundary RAM/device/service mismatch' in str(error),str(error)
   diagnostic=json.loads((dest/'borrower-difference.json').read_text())
   rows.append(dict(defect=tag,result='DETECTED',scope='Independent compiled L1 full boundary state and ordered service comparator',diagnostic=diagnostic))
  else:raise AssertionError((tag,'surviving semantic fault'))
 save(OUT/'defects.json',dict(result='PASS',controls=rows))
