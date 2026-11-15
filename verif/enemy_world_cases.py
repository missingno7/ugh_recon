"""Compiled enemy borrower and defect evidence; generated copies only."""
import ctypes as C,json,sys,re
from pathlib import Path

def libraries(ROOT,OUT,bounded):
 helper=r'''#include "platform.h"
#include <string.h>
typedef struct EnemiesTrace {uint32_t address;uint8_t value,slots[190];} EnemiesTrace;
EXPORT int api_fail_spawn;
static EnemiesTrace traces[8192];static unsigned used,enabled;
EXPORT void api_trace_begin(void){used=0;enabled=1;}
EXPORT unsigned api_trace_count(void){return used;}
EXPORT EnemiesTrace *api_trace_data(void){return traces;}
static int owned(uint32_t a){return a>=lin(DATA_SEG,0x2cad)&&a<lin(DATA_SEG,0x2d6b);}
void api_enemies_notify(uint32_t a,uint8_t v){
 if(!enabled||!owned(a))return;
 if(used==8192)return;
 EnemiesTrace*t=traces+used++;memset(t,0,sizeof *t);t->address=a;t->value=v;
 for(unsigned i=0;i<190;i++)t->slots[i]=rd8(DATA_SEG,(uint16_t)(0x2cad+i));
}
void api_device_write(uint32_t,uint8_t);
void ugh_write(uint32_t a,uint8_t v){api_device_write(a,v);
#ifdef UGH_NATIVE_ENEMIES
 if(owned(a))return;
#endif
 api_enemies_notify(a,v);
}
'''
 folders=[]
 for label in ['reference','composed']:
  folder=OUT/'borrowers'/label;folder.mkdir(parents=True,exist_ok=True);cmd=json.loads((OUT/'children'/('api-input-'+label+'-compile.json')).read_text())['command'];cmd[cmd.index('-o')+1]=str(folder/'api.dll')
  for i,v in enumerate(cmd):
   if not v.endswith('.c'):continue
   p=Path(v);t=p.read_text()
   if p.name=='memory.c':assert t.count('void ugh_write(')==1;t=t.replace('void ugh_write(','void api_device_write(',1)
   elif p.name=='enemy_world_bridge.c':
    n='enemies_field_put(fields+slot,lane,value);return 1;';assert t.count(n)==1;t='extern void api_enemies_notify(unsigned int,unsigned char);\n'+t.replace(n,'enemies_field_put(fields+slot,lane,value);api_enemies_notify(address,value);return 1;')
   elif p.name=='dispatch.c':assert t.count('int status=fn(r);')==2;t=t.replace('int status=fn(r);','platform_trace_entry(segment,offset,r); int status=fn(r);')
   else:
    if not re.search(r'EXPORT int c_SpawnFallingItem\(Regs \*r\)\s*\{',t):continue
   needle=r'(EXPORT int c_SpawnFallingItem\(Regs \*r\)\s*\{)'
   if re.search(needle,t):t='extern int api_fail_spawn;\n'+re.sub(needle,r'\1 if(api_fail_spawn)return UGH_BUDGET;',t,count=1)
   q=folder/p.name;q.write_text(t);cmd[i]=str(q)
  q=folder/'trace.c';q.write_text(helper);cmd.append(str(q));bounded(cmd,'borrowers-'+label+'-compile');folders.append(folder)
 return folders

def run(ROOT,OUT,bounded,save,paths=None):
 import nbuild,difftest
 dlls=[nbuild.load_l1(p/'api.dll') for p in (paths or libraries(ROOT,OUT,bounded))]
 class Trace(C.Structure):_fields_=[('address',C.c_uint32),('value',C.c_uint8),('slots',C.c_uint8*190)]
 for d in dlls:
  d.api_trace_data.restype=C.POINTER(Trace);d.api_trace_count.restype=C.c_uint;d.api_live_store.argtypes=[C.c_uint16,C.c_uint16,C.c_uint16]
 m=difftest.Machine();data=m.seg('DGROUP:PlayerCount');rows=[];seeds=[]
 service_ids={m.address(x) for x in ['C:PlayAdlibEffect','C:StopAdlibTrackChannel','GAME:FindPlayerTouchingEnemy','GAME:FindThrownStoneHittingEnemy','GAME:SpawnFallingItem','GAME:DrawTransparentSprite','GAME:RestoreSpriteBackground','GAME:ScaleLevelYToThreeQuarters','GAME:ScaleLevelSpeedToThreeHalves']}
 def pair(entry,regs=None,args=(),flags=0x202,stop=False,label=None,follow=(),atomic=False,live=False,fail=False):
  initial=m.prepare('GAME:'+entry,{**difftest.POISON,'DS':data,**(regs or {})},'far',args,flags);memory=m.snapshot();state=m.device.state();out=[];fallbacks=[]
  for d in dlls:
   C.memmove(d.ugh_memory().contents,memory,len(memory));d.ugh_devices_reset();dev=d.ugh_device_state().contents;C.memmove(C.addressof(dev),state,len(state));d.api_begin();d.api_trace_begin();C.c_int.in_dll(d,'api_stop_at_load').value=int(stop);C.c_int.in_dll(d,'api_fail_spawn').value=int(fail)
   kind=C.CFUNCTYPE(None,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs));hits=[];errors=[];entries=[]
   def callback(s,o,rp,d=d):
    try:
     if (s,o) in service_ids:entries.append((s,o))
     if live and (s,o)==m.address('C:PlayAdlibEffect') and not hits:hits.append((s,o));d.api_live_store(data,0x2d11,0xbeef)
    except BaseException as error:errors.append(repr(error))
   cb=kind(callback);d.ugh_set_entry_observer.argtypes=[kind];d.ugh_set_entry_observer(cb)
   r=difftest.Regs(**{k.lower():v for k,v in initial.items()});f=getattr(d,'api_c_'+entry);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r))
   for child,updates in follow:
    for k,v in updates.items():setattr(r,k,v)
    f=getattr(d,'api_c_'+child);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r))
   d.ugh_set_entry_observer(kind());assert not errors,errors
   fallbacks.append(C.c_uint.in_dll(d,'api_timer_fallbacks').value)
   ram=bytes(d.ugh_memory().contents);lo=initial['SS']*16;hi=lo+initial['SP'];count=d.api_trace_count();assert count<8192
   stream=C.string_at(d.api_trace_data(),count*C.sizeof(Trace));out.append((status,ram[:lo]+ram[hi:],bytes(dev),None if atomic else stream,(hits,entries),ram,stream))
  if [x[:5] for x in out][0]!=[x[:5] for x in out][1]:
   save(OUT/'borrower-difference.json',dict(entry=entry,label=label,first_ram=next((i for i,(a,b) in enumerate(zip(out[0][1],out[1][1])) if a!=b),None),statuses=[x[0] for x in out]));raise AssertionError((entry,label,'full RAM/device/store mismatch'))
  if fail:
   assert out[0][0]==2,(entry,'failure not delivered')
   assert out[0][4][1].count(m.address('GAME:SpawnFallingItem'))==1 and m.address('C:PlayAdlibEffect') not in out[0][4][1],(entry,'failure prefix')
  if live:assert out[0][4][0],(entry,'vacuous live cut');assert out[0][5][data*16+0x2d11:data*16+0x2d13]==b'\xef\xbe'
  rows.append(dict(entry=entry,label=label or entry,status=out[0][0],ordered_byte_stores=len(out[0][6])//C.sizeof(Trace),trace_compared=not atomic,live_cuts=len(out[0][4][0]),service_entries=out[0][4][1],compatibility_fallbacks=fallbacks,follow=follow));return out[0][5],out[0][6]
 # All shipped logical level seeds, stale histories and mutable source records.
 for players,count in [(1,69),(2,81)]:
  for level in range(count):
   m.reset();m.ww('DGROUP:PlayerCount',players);m.ww('DGROUP:PlayerArrayBytes',2*players);m.ww('DGROUP:CurrentLevelIndex',level)
   for a in range(0x2cad,0x2d6b,2):m.write(data,a,((a*73+level)&65535).to_bytes(2,'little'))
   ram,stream=pair('LoadCurrentLevelState',label=f'load p={players} level={level}')
   writes=[Trace.from_buffer_copy(stream[i:i+C.sizeof(Trace)]) for i in range(0,len(stream),C.sizeof(Trace))];assert writes
   seeds.append(dict(players=players,level=level,ordered_stores=[dict(address=w.address,value=w.value) for w in writes]))
 # Raw descriptor default is distinct from a known typed identity. An unknown
 # source word takes Triopterus, with every list read still live in sq_load_lists.
 m.reset();m.ww('DGROUP:PlayerCount',1);m.ww('DGROUP:PlayerArrayBytes',2);m.ww('DGROUP:CurrentLevelIndex',0)
 table=m.rw('DGROUP:LevelOrderTables');record=int.from_bytes(m.read(data,table,2),'little');source=int.from_bytes(m.read(data,record+6,2),'little')
 # Resource list is not owned. Copy a complete real Triopterus record to spare
 # resource coordinates, then use the unknown identity in a one-entry list.
 original=m.off('DGROUP:Data_766C');m.write(data,0x7200,m.read(data,original,60));m.write(data,0x7240,b'\x00\x72\x00\x00\x34\x12\x20\x00\xff\xff')
 m.write(data,record+6,(0x7240).to_bytes(2,'little'))
 ram,stream=pair('LoadCurrentLevelState',label='unknown enemy descriptor -> live Triopterus default')
 assert int.from_bytes(ram[data*16+0x2cad:data*16+0x2caf],'little')==0x7200
 assert int.from_bytes(ram[data*16+0x2cf3:data*16+0x2cf5],'little')==m.off('GAME:BeginTriopterusPatrol')
 # Native persistent state and all existing hazard/contact APIs, including signed
 # countdown boundaries, player selectors and alternate stone IDs.
 import hazards_build
 selected=set(hazards_build.NAMES)|{'FindPlayerTouchingEnemy','FindThrownStoneHittingEnemy','EraseDemoSprites'}
 for suite in ['actors','actors_states','items_water','render']:
  for case in difftest.load_suite(suite).CASES:
   if case.routine.split(':')[1] not in selected:continue
   m.reset();case.setup(m) if case.setup else None;regs=case.regs(m) if callable(case.regs) else case.regs
   pair(case.routine.split(':')[1],regs=regs,flags=case.flags or 0x202,label=case.title)
 # Failing spawn is a synchronous service cut; no award or later sound follows.
 for case in difftest.load_suite('actors_states').CASES:
  if case.routine!='GAME:ReleaseTreeReward':continue
  m.reset();case.setup(m) if case.setup else None;regs=case.regs(m) if callable(case.regs) else case.regs
  m.ww('DGROUP:EnemyAnimationOrDropLists',m.off('DGROUP:Treerewardlist_3CB3'),4)
  pair('ReleaseTreeReward',regs=regs,fail=True,label=case.title+' failing spawn')
  assert rows[-1]['compatibility_fallbacks']==[0,0], 'failing-spawn fixture must exercise native hazard adapter'
 # Both direction/target interpretations share one retained word, no conversion.
 for ticks in [0,1,2,0x7fff,0x8000,0xffff]:
  for target in [0,1]:
   suite=difftest.load_suite('actors_states');case=next(c for c in suite.CASES if c.routine=='GAME:UpdateBirdFlight')
   m.reset();case.setup(m) if case.setup else None;m.ww('DGROUP:EnemyDirectionOrTargetPlayer',target,4);m.ww('DGROUP:EnemyAnimationCountdowns',ticks,4)
   pair('UpdateBirdFlight',regs=dict(BX=4),label=f'bird countdown {ticks:04x}, target {target}')
 # Actual sound service observer changes an unrelated history while native state
 # is live. The borrower must retain this mutation across sound completion.
 suite=difftest.load_suite('actors_states');case=next(c for c in suite.CASES if c.routine=='GAME:LaunchBirdTowardPlayer')
 m.reset();case.setup(m) if case.setup else None;regs=case.regs(m) if callable(case.regs) else case.regs
 pair('LaunchBirdTowardPlayer',regs=regs,live=True,label='live history mutation across bird sound service')
 for df in [0x202,0x602]:
  m.reset();m.ww('DGROUP:LevelWorkspacePointer',0x2648);m.ww('DGROUP:LevelWorkspacePointer',data,2);pair('InitializeLevelDisplay',stop=True,flags=df,label='multi-owner clear '+hex(df))
 for offset in [0x2cac,0x2cad,0x2cb6,0x2d61,0x2d6a,0x2d6b]:
  for delta in [-1,0,1]:
   for count in [0,1,2,20,160]:
    m.reset();pair('CopyFarBytes',args=(count,0,offset,data,(offset+delta)&65535,data),flags=0x602 if delta<0 else 0x202,label=f'physical window {offset:x},{delta},{count}')
 from dataprobe import ice_pack235
 for size in [0x4cad,0x4d11,0x4d6b]:
  m.reset();raw=(bytes(range(256))*(size//256+1))[:size];m.write(0x7500,0,ice_pack235(raw));pair('UnpackIceStream',regs=dict(DS=0x7500,ES=data-0x200,SI=0,DI=0xbeef),atomic=True,label=f'atomic ICE enemy window {size:x}')
 assert len(seeds)==150 and any(r['live_cuts'] for r in rows)
 assert any(r['service_entries'] for r in rows),'vacuous service stream'
 assert any(r['ordered_byte_stores'] for r in rows if r['entry']=='LaunchBirdTowardPlayer')
 save(OUT/'borrowers.json',dict(result='PASS',cases=rows,level_seeds=seeds,scope='Independent compiled L1/native: full RAM excluding ABI stack, full Devices/ordered ports, filtered ordered cross-unit entry stream, ordered190-byte owner stores with full slot snapshots.150 level seeds; unknown descriptor default; live mutation at sound service; alias/reset/DF/copy and atomic ICE returned-state exception.'))

def deepcounts(ROOT,OUT,bounded,save,snapshot,previous):
 import os,wholegame,hazards_build
 from closure_support import function
 target=OUT/'baseline';assert (OUT/'levels.json').is_file()
 folder=OUT/'deep-counts';capture=previous.copy_host(target,folder)
 names=hazards_build.NAMES+['FindPlayerTouchingEnemy','FindThrownStoneHittingEnemy']
 (folder/'host/enemy_counts.c').write_text('#include <stdio.h>\n#include <stdlib.h>\nstatic unsigned long long counts['+str(len(names))+'];static void dump(void){const char*p=getenv("ENEMY_COUNTS");if(!p)return;FILE*f=fopen(p,"w");if(!f)exit(87);for(unsigned i=0;i<'+str(len(names))+';i++)fprintf(f,"%llu\\n",counts[i]);fclose(f);}\n__attribute__((constructor)) static void enemy_counts_begin(void){atexit(dump);}\nvoid enemy_count(unsigned i){counts[i]++;}\n')
 for bridge,selected in [('hazards',hazards_build.NAMES),('contacts',names[-2:])]:
  p=folder/('native/bridge/'+bridge+'_bridge.c');t=p.read_text();wrappers=[]
  for name in selected:
   body=function(t,'c_'+name);t=t.replace(body,body.replace('c_'+name+'(','counted_'+name+'(',1));wrappers.append('EXPORT int c_'+name+'(Regs*r){enemy_count('+str(names.index(name))+');return counted_'+name+'(r);}\n')
  p.write_text('extern void enemy_count(unsigned);\n'+t+'\n'+''.join(wrappers))
 bounded([sys.executable,'tools/hostbuild.py'],'deep-counts-build',folder);rows=[]
 groups=[('whole','tests/scenarios','build/whole'),('openings','tests/levels','build/levels'),('audio','tests/levels-audio','build/levels-audio'),('deep','tests/levels-deep','build/levels-deep')]
 for group,scripts,bank in groups:
  for path in sorted((target/scripts).glob('*.txt')):
   ref=json.loads((target/bank/(path.stem+'.ref.json')).read_text());counter=folder/(group+'-'+path.stem+'.counts');os.environ['ENEMY_COUNTS']=str(counter)
   try:r=bounded([sys.executable,capture,folder/'build/host/ugh.exe','--headless',str(wholegame.scenario(path)['frames']),'--script',path,'--timeout','590'],'counts-'+group+'-'+path.stem)
   finally:os.environ.pop('ENEMY_COUNTS',None)
   actual=json.loads(r['stdout']);assert actual['returncode']==0,actual['stderr'];assert [json.loads(x) for x in actual['stdout'].splitlines()]==ref['frames'],path.stem
   counts=dict(zip(names,map(int,counter.read_text().splitlines())));rows.append(dict(group=group,scenario=path.stem,entries=counts,frames=len(ref['frames'])))
 assert len(rows)==116
 for name in ['UpdateBirdFlight','UpdateDinoForce','UpdateTriopterusPatrol','UpdateTriopterusCharge','ReleaseTreeReward']:assert sum(r['entries'][name] for r in rows)>0,name
 save(OUT/'deep-counts.json',dict(result='PASS',runs=rows,scope='Entry-only counters over all20 maintained scenarios and81+7+8 levels; all independent reference frames equal. Every hazard/contact entry reported including zeros.'))

def check_mutant(ROOT,OUT,tag,path):
 import nbuild,difftest
 dlls=[nbuild.load_l1(OUT/'borrowers/reference/api.dll'),nbuild.load_l1(path)];m=difftest.Machine();data=m.seg('DGROUP:PlayerCount')
 select={'stale-selected-player':{'UpdateDinoForce'},'wrong-stone-id':{'FindThrownStoneHittingEnemy','UpdateBirdFlight','UpdateTriopterusPatrol','UpdateDinoForce','UpdateFruitTreeAnimation'},'award-after-failed-service':{'ReleaseTreeReward'},'lost-bird-handle':{'LaunchBirdTowardPlayer'},'collapsed-target-direction':{'LaunchBirdTowardPlayer','UpdateBirdFlight'},'normalized-countdown':{'UpdateDinoForce','UpdateTriopterusPatrol','UpdateBirdFlight'}}[tag]
 for suite in ['actors_states','actors','items_water']:
  for case in difftest.load_suite(suite).CASES:
   entry=case.routine.split(':')[1]
   if entry not in select:continue
   m.reset();case.setup(m) if case.setup else None;regs=case.regs(m) if callable(case.regs) else case.regs
   if tag=='wrong-stone-id':
    for i in range(16):
     if m.rw('DGROUP:ActorDescriptors',2*i)==m.off('DGROUP:Data_78DC'):m.ww('DGROUP:ActorDescriptors',m.off('DGROUP:Data_7926'),2*i)
   if tag=='award-after-failed-service':m.ww('DGROUP:EnemyAnimationOrDropLists',m.off('DGROUP:Treerewardlist_3CB3'),4)
   if tag=='lost-bird-handle':m.ww('DGROUP:EnemyFlightSoundHandles',0x1357,4)
   if tag=='stale-selected-player':
    m.ww('DGROUP:PlayerHorizontalVelocities',0x1357);m.ww('DGROUP:PlayerHorizontalVelocities',0x2468,2)
   if tag=='normalized-countdown':m.ww('DGROUP:EnemyAnimationCountdowns',0x8000,4)
   initial=m.prepare('GAME:'+entry,{**difftest.POISON,'DS':data,**regs},'far',(),case.flags or 0x202);memory=m.snapshot();device=m.device.state();results=[]
   for d in dlls:
    C.memmove(d.ugh_memory().contents,memory,len(memory));d.ugh_devices_reset();dev=d.ugh_device_state().contents;C.memmove(C.addressof(dev),device,len(device));d.api_begin();C.c_int.in_dll(d,'api_fail_spawn').value=int(tag=='award-after-failed-service')
    r=difftest.Regs(**{k.lower():v for k,v in initial.items()});f=getattr(d,'api_c_'+entry);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r));ram=bytes(d.ugh_memory().contents);lo=initial['SS']*16;hi=lo+initial['SP'];results.append((status,ram[:lo]+ram[hi:],bytes(dev)))
   if results[0]!=results[1]:print('DETECTED',tag,suite,case.title,flush=True);return
 raise AssertionError((tag,'survived independent comparator'))


def defects(ROOT,OUT,bounded,save,snapshot,previous):
 import wholegame
 folder=OUT/'defects';folder.mkdir(exist_ok=True);capture=folder/'capture.py';capture.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n');rows=[]
 for fault,name in [(1,'lost-bird-handle'),(2,'slot-alias'),(3,'cleared-high-lane'),(4,'missed-serialization')]:
  exe=folder/(name+'.exe');bounded([previous.timing.common.GCC,'-O2','-std=c11','-DENEMIES_TEST_FAULT='+str(fault),'-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/enemy_world_router.c',ROOT/'native/enemy_world.c',ROOT/'native/bridge/enemy_world_bridge.c'],'defect-router-'+name+'-compile')
  r=json.loads(bounded([sys.executable,capture,exe],'defect-router-'+name+'-run')['stdout']);assert r['returncode']!=0,(name,r)
  rows.append(dict(defect=name,scope='Independent literal byte/word/member oracle',result='DETECTED',exit=r['returncode']))
 for tag in ['stale-selected-player','wrong-stone-id','award-after-failed-service','lost-bird-handle','collapsed-target-direction','normalized-countdown']:
  dest=folder/tag;dest.mkdir(exist_ok=True);cmd=json.loads((OUT/'children/borrowers-composed-compile.json').read_text())['command'];cmd[cmd.index('-o')+1]=str(dest/'api.dll');changed=[]
  for i,v in enumerate(cmd):
   if not v.endswith('.c'):continue
   p=Path(v);text=p.read_text();before=text
   if p.name=='enemy_world_bridge.c':
    if tag=='lost-bird-handle':cmd.insert(1,'-DENEMIES_TEST_FAULT=1');break
    if tag in ['collapsed-target-direction','normalized-countdown']:
     needle='return (uint8_t)(value>>shift);';assert text.count(needle)==1
     field='direction_or_target_word' if tag=='collapsed-target-direction' else 'countdown'
     action='if(value==1)value=2;' if tag=='collapsed-target-direction' else 'value&=0x7fff;'
     text=text.replace(needle,'if(field->member==offsetof(NativeEnemyWorld,slot[0].'+field+')){'+action+'}'+needle)
    elif tag=='stale-selected-player':
     needle='uint32_t result=0,address=lin(bank,position);';assert text.count(needle)==1
     text=text.replace(needle,needle+'if(width==2 && address>=A(PlayerHorizontalVelocities) && address<A(PlayerHorizontalVelocities)+4)return 0;')
    elif tag=='wrong-stone-id':
     needle='return result;';assert text.count(needle)==1
     text=text.replace(needle,'if(width==2 && address>=A(ActorDescriptors) && address<A(ActorDescriptors)+32 && result==D(Data_7926)){return D(Data_78DC);}'+needle)
   if tag=='award-after-failed-service' and p.name=='hazards_bridge.c':
    needle='return ugh_call_near(target,ret,r);';assert text.count(needle)==1
    text=text.replace(needle,'int failed=ugh_call_near(target,ret,r);if(failed)enemies_write16(r->ds,D(ScoreLowWord),(uint16_t)(enemies_read16(r->ds,D(ScoreLowWord))+1u));return failed;')
   if text!=before:q=dest/p.name;q.write_text(text);cmd[i]=str(q);changed.append(p.name)
  if tag!='lost-bird-handle':assert changed,tag
  guard=dest/'control.h';guard.write_text('#include <stdio.h>\n#include <stdlib.h>\n_Noreturn static inline void enemy_control_abort(void){fputs("ENEMY_CONTROL_BRIDGE_ASSERT\\n",stderr);exit(87);}\n#define abort enemy_control_abort\n');cmd[1:1]=['-include',str(guard)]
  bounded(cmd,'defect-api-'+tag+'-compile')
  child=dest/'consume.py';child.write_text('import sys\nsys.path[:0]='+repr([str(ROOT/'verif'),str(ROOT/'tools')])+'\nfrom pathlib import Path\nfrom enemy_world_cases import check_mutant\ncheck_mutant(Path('+repr(str(ROOT))+'),Path('+repr(str(OUT))+'),'+repr(tag)+',Path('+repr(str(dest/'api.dll'))+'))\n')
  r=json.loads(bounded([sys.executable,capture,sys.executable,child],'defect-api-'+tag+'-run')['stdout']);assert r['returncode']==0 and 'DETECTED' in r['stdout'] or r['returncode']==87 and 'ENEMY_CONTROL_BRIDGE_ASSERT' in r['stderr'],(tag,r)
  rows.append(dict(defect=tag,scope='Compiled L1 versus generated composed mutant',result='DETECTED',exit=r['returncode'],diagnostic=r['stdout']+r['stderr']))
 target=snapshot()
 for fault,name in [(4,'missed-serialization'),(0,'reversed-enemy-layers')]:
  dest=folder/('host-'+name);hc=previous.copy_host(target,dest);p=dest/'tools/hostbuild.py';t=p.read_text();needle="return (['-DUGH_NATIVE_ENEMIES']";assert t.count(needle)==1;p.write_text(t.replace(needle,"return (['-DENEMIES_TEST_FAULT="+str(fault)+"','-DUGH_NATIVE_ENEMIES']",1))
  if not fault:
   p=dest/'native/bridge/session_bridge.c';t=p.read_text()
   back='case SESSION_DRAW_ENEMIES_BACK:status=sq_draw_enemies(r,0);';front='case SESSION_DRAW_ENEMIES_FRONT:status=sq_draw_enemies(r,1);'
   assert t.count(back)==1 and t.count(front)==1
   p.write_text(t.replace(back,back.replace('(r,0)','(r,1)')).replace(front,front.replace('(r,1)','(r,0)')))
  for p in (dest/'native/bridge').glob('*'):
   if p.suffix in ['.c','.h'] and 'abort()' in p.read_text():p.write_text('#include <stdio.h>\n#include <stdlib.h>\n'+p.read_text().replace('abort()','(fputs("ENEMY_CONTROL_BRIDGE_ASSERT\\n",stderr),exit(87))'))
  bounded([sys.executable,'tools/hostbuild.py'],'defect-host-'+name+'-build',dest);scenario='enemy';script=target/('tests/scenarios/'+scenario+'.txt');ref=json.loads((target/('build/whole/'+scenario+'.ref.json')).read_text())['frames']
  r=json.loads(bounded([sys.executable,hc,dest/'build/host/ugh.exe','--headless',str(wholegame.scenario(script)['frames']),'--script',script,'--timeout','590'],'defect-host-'+name+'-run')['stdout']);frames=[json.loads(x) for x in r['stdout'].splitlines()];first=next((i for i,(a,b) in enumerate(zip(frames,ref)) if a!=b),None)
  assert first is not None or r['returncode']==88 and 'missed serialization' in r['stderr'] or r['returncode']==87 and 'ENEMY_CONTROL_BRIDGE_ASSERT' in r['stderr'],(name,r)
  rows.append(dict(defect=name,result='DETECTED',scenario=scenario,frame=first+1 if first is not None else len(frames)+1,exit=r['returncode'],diagnostic=r['stderr']))
 save(OUT/'defects.json',dict(result='PASS',controls=rows,scope='Independent router seam faults, all seven cut5F plan defect classes through compiled consuming APIs and actual host. Frozen owner/state and live service errors compared; generated copies only.'))
