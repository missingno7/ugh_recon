"""Live shared writers, ordered service cuts and mutation controls for cut5C."""
import ctypes as C,json,struct,sys
from pathlib import Path

def libraries(ROOT,OUT,bounded):
 helper=r'''#include "platform.h"
#include <string.h>
typedef struct PlayerTrace {uint32_t address;uint8_t value,players[92];} PlayerTrace;
static PlayerTrace traces[8192];static unsigned enabled,used;
static int owned(uint32_t a){uint32_t b=(uint32_t)DATA_SEG<<4;if(a<b)return 0;unsigned o=a-b;return(o>=0x278c&&o<0x27a0)||(o>=0x27d0&&o<0x2800)||(o>=0x2804&&o<0x281c);}
EXPORT void api_trace_begin(void){enabled=1;used=0;}
EXPORT unsigned api_trace_count(void){return used;}
EXPORT PlayerTrace *api_trace_data(void){return traces;}
void api_player_notify(uint32_t a,uint8_t v){
 if(!enabled||!owned(a))return;
 if(used==8192)return;
 PlayerTrace*t=traces+used++;memset(t,0,sizeof *t);t->address=a;t->value=v;unsigned at=0;
 for(unsigned i=0x278c;i<0x281c;i++)if(owned(lin(DATA_SEG,(uint16_t)i)))t->players[at++]=rd8(DATA_SEG,(uint16_t)i);
}
void api_device_write(uint32_t,uint8_t);
void ugh_write(uint32_t a,uint8_t v){api_device_write(a,v);
#ifdef UGH_NATIVE_PLAYER
 if(owned(a))return;
#endif
 api_player_notify(a,v);
}
'''
 folders=[]
 for label in ['reference','composed']:
  folder=OUT/'borrowers'/label;folder.mkdir(parents=True,exist_ok=True)
  cmd=json.loads((OUT/'children'/('api-input-'+label+'-compile.json')).read_text())['command'];cmd[cmd.index('-o')+1]=str(folder/'api.dll')
  for i,value in enumerate(cmd):
   if not value.endswith('.c'):continue
   original=Path(value);text=original.read_text()
   if original.name=='memory.c':assert text.count('void ugh_write(')==1;text=text.replace('void ugh_write(','void api_device_write(',1)
   elif original.name=='player_world_bridge.c':
    needle='player_field_put(fields+slot,lane,value);return 1;';assert text.count(needle)==1
    text='extern void api_player_notify(unsigned int,unsigned char);\n'+text.replace(needle,'player_field_put(fields+slot,lane,value);api_player_notify(address,value);return 1;')
   elif original.name=='dispatch.c':
    assert text.count('int status=fn(r);')==2;text=text.replace('int status=fn(r);','platform_trace_entry(segment,offset,r); int status=fn(r);')
   else:continue
   p=folder/original.name;p.write_text(text);cmd[i]=str(p)
  p=folder/'trace.c';p.write_text(helper);cmd.append(str(p));bounded(cmd,'borrowers-'+label+'-compile');folders.append(folder)
 return folders

def run(ROOT,OUT,bounded,save):
 import nbuild,difftest
 folders=libraries(ROOT,OUT,bounded);dlls=[nbuild.load_l1(f/'api.dll') for f in folders]
 class Trace(C.Structure):_fields_=[('address',C.c_uint32),('value',C.c_uint8),('players',C.c_uint8*92)]
 for dll in dlls:
  dll.api_trace_data.restype=C.POINTER(Trace);dll.api_trace_count.restype=C.c_uint
  dll.api_live_word.argtypes=[C.c_uint16,C.c_uint16];dll.api_live_word.restype=C.c_uint16
  dll.api_live_store.argtypes=[C.c_uint16,C.c_uint16,C.c_uint16]
 m=difftest.Machine();data=m.seg('DGROUP:PlayerCount');rows=[];prefixes=[]
 ranges=[(0x278c,20),(0x27d0,48),(0x2804,24)]
 def current(memory):return b''.join(memory[data*16+a:data*16+a+n] for a,n in ranges)
 def pair(name,regs=None,args=(),flags=0x202,stop=False,live=None,label=None,follow=None,trace=True):
  initial=m.prepare('GAME:'+name,{**difftest.POISON,'DS':data,**(regs or {})},'far',args,flags);memory=m.snapshot();state=m.device.state();out=[]
  for dll in dlls:
   C.memmove(dll.ugh_memory().contents,memory,len(memory));dll.ugh_devices_reset();dev=dll.ugh_device_state().contents;C.memmove(C.addressof(dev),state,len(state));dll.api_begin();dll.api_trace_begin();C.c_int.in_dll(dll,'api_stop_at_load').value=int(stop)
   output=C.CFUNCTYPE(None,C.c_uint16,C.c_uint,C.c_uint32);hits=[0];callback_errors=[]
   def callback(port,size,value,dll=dll,hits=hits,dev=dev):
    if live=='pixels' and port==0x3cf:
     hits[0]+=1;fill=0x80 if hits[0]&1 else 0x17
     # This is a service reply producer, not game-state resynchronization.
     C.memset(C.addressof(dev.planes),fill,4*65536)
    elif live=='stone' and port==0x388 and not hits[0]:
     hits[0]+=1
     dll.api_live_store(data,m.off('DGROUP:PlayerHorizontalVelocities'),0x1357)
     dll.api_live_store(data,m.off('DGROUP:PlayerX32'),0x2468)
   def guarded_callback(*args):
    try:callback(*args)
    except BaseException as error:callback_errors.append(repr(error))
   cb=output(guarded_callback) if live else output();dll.ugh_set_output_observer.argtypes=[output];dll.ugh_set_output_observer(cb)
   entry_type=C.CFUNCTYPE(None,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs))
   def at_entry(segment,offset,rp,dll=dll,hits=hits):
    if live=='stone' and (segment,offset)==m.address('C:PlayAdlibEffect') and not hits[0]:
     hits[0]+=1;dll.api_live_store(data,m.off('DGROUP:PlayerHorizontalVelocities'),0x1357);dll.api_live_store(data,m.off('DGROUP:PlayerX32'),0x2468)
   def guarded_entry(*args):
    try:at_entry(*args)
    except BaseException as error:callback_errors.append(repr(error))
   entry=entry_type(guarded_entry);dll.ugh_set_entry_observer.argtypes=[entry_type];dll.ugh_set_entry_observer(entry)
   r=difftest.Regs(**{k.lower():v for k,v in initial.items()});fn=getattr(dll,'api_c_'+name);fn.argtypes=[C.POINTER(difftest.Regs)];status=fn(C.byref(r))
   dll.ugh_set_output_observer(output())
   dll.ugh_set_entry_observer(entry_type())
   assert not callback_errors,callback_errors
   if follow:
    for child,updates in follow:
     for k,v in updates.items():setattr(r,k,v)
     fn=getattr(dll,'api_c_'+child);fn.argtypes=[C.POINTER(difftest.Regs)];status=fn(C.byref(r));assert status==0,(child,status)
   ram=bytes(dll.ugh_memory().contents);lo=initial['SS']*16;hi=lo+initial['SP'];count=dll.api_trace_count();assert count<8192
   stream=C.string_at(dll.api_trace_data(),count*C.sizeof(Trace))
   out.append((status,ram[:lo]+ram[hi:],bytes(dev),stream,hits[0],ram,current(ram)))
  compare=[(a[0],a[1],a[2],a[3] if trace else None,a[4]) for a in out]
  if compare[0]!=compare[1]:
   save(OUT/'borrower-difference.json',dict(entry=name,label=label,status=[a[0] for a in out],first_ram=next((i for i,(a,b) in enumerate(zip(out[0][1],out[1][1])) if a!=b),None),trace_counts=[len(a[3])//C.sizeof(Trace) for a in out],live_cuts=[a[4] for a in out]));raise AssertionError((name,label,'borrower mismatch'))
  if live:assert out[0][4]>0,(name,label,'vacuous live service')
  rows.append(dict(entry=name,label=label or name,status=out[0][0],player_writes=len(out[0][3])//C.sizeof(Trace),trace_compared=trace,live_cuts=out[0][4],follow=follow))
  return out[0][5],out[0][3]
 # Every shipped logical level seed; minimum fares/impact and cached sprite
 # history are deliberately distinct, so a cold normalization cannot pass.
 for players,count in [(1,69),(2,81)]:
  for level in range(count):
   m.reset();m.ww('DGROUP:PlayerCount',players);m.ww('DGROUP:PlayerArrayBytes',2*players);m.ww('DGROUP:CurrentLevelIndex',level)
   for a,n in ranges:m.write(data,a,bytes((i*73+a+level)&255 for i in range(n)))
   before=m.snapshot();ram,events=pair('LoadCurrentLevelState',label=f'loader both records p={players} level={level}')
   for a in [0x27ec,0x27ee,0x280c,0x280e,0x2818,0x281a]:assert ram[data*16+a:data*16+a+2]==before[data*16+a:data*16+a+2],('retained loader field',a)
   writes=[Trace.from_buffer_copy(events[i:i+C.sizeof(Trace)]).address-data*16 for i in range(0,len(events),C.sizeof(Trace))]
   assert all(a in writes for a in [0x27d0,0x27d2,0x27d4,0x27d6,0x27e0,0x27e2,0x27e4,0x27e6]),(players,level,'both players were not seeded')
   prefixes.append(dict(players=players,level=level,byte_store_order=writes))
 for df in [0x202,0x602]:
  for players,byte_count in [(0,0xffff),(1,2),(2,4),(2,2)]:
   m.reset();m.ww('DGROUP:PlayerCount',players);m.ww('DGROUP:PlayerArrayBytes',byte_count);m.ww('DGROUP:LevelWorkspacePointer',0x2648);m.ww('DGROUP:LevelWorkspacePointer',data,2)
   for a,n in ranges:m.write(data,a,bytes((i*73+a)&255 for i in range(n)))
   pair('InitializeLevelDisplay',stop=True,flags=df,label=f'multi-owner clear DF={bool(df&0x400)} raw counts={players,byte_count}')
 for index in [0,1]:
  for scan in range(256):
   m.reset();m.device.script(0x60,[scan],cycles=0xffffffff);m.wb('DGROUP:KeyboardSequenceIndex',index)
   m.ww('DGROUP:PlayerOneControlMode',0xffff);m.ww('DGROUP:PlayerTwoControlMode',0xffff)
   for i in range(0,65536,6):
    if m.rb('DGROUP:KeyboardSequenceRecords',i)==255:break
    m.wb('DGROUP:KeyboardSequenceCandidateState',0,i)
   for a in range(0x278c,0x27a0,2):m.write(data,a,b'\x63\xa7')
   ram,events=pair('HandleKeyboardScanInterrupt',label=f'IRQ index={index} scan={scan:02x} retained high bytes')
   assert all(ram[data*16+a+1]==0xa7 for a in range(0x278c,0x27a0,2)),scan
 scene=difftest.load_suite('scene')
 for slot in [0,2]:
  for hv,vv in [(-6144,0),(6144,0),(0,-6144),(0,6144)]:
   m.reset();case=scene.move_case('live collision reply',slot=slot,hv=hv,vv=vv);case.setup(m)
   pair('MovePlayerWithVgaCollisions',regs=dict(BX=slot),live='pixels',label=f'live plane reply slot={slot} velocity={hv,vv}')
 # A stone service can mutate live player state. A subsequent player cache
 # operation must consume the current store, not a pre-service projection.
 stone=next(c for c in difftest.load_suite('actors_states').CASES if c.routine=='GAME:ThrowCarriedStone')
 for slot in [0,2]:
  m.reset();stone.setup(m);regs=stone.regs(m) if callable(stone.regs) else stone.regs
  scene.move_case('post stone motion',slot=0).setup(m)
  m.ww('DGROUP:PlayerCount',2);regs={**regs,'DI':slot}
  ram,events=pair('ThrowCarriedStone',regs=regs,live='stone',follow=[('MovePlayerWithVgaCollisions',dict(bx=0,ds=data)),('CachePlayerDrawState',dict(bx=0,ds=data))],label=f'live state after stone service carrier={slot}')
  assert int.from_bytes(ram[data*16+0x27d0:data*16+0x27d2],'little')!=0x2468,'following movement did not consume the live state'
 for offset in [0x278b,0x278c,0x279e,0x27cf,0x27e0,0x27fc,0x2800,0x2803,0x281a]:
  for delta in [-1,0,1]:
   for n in [0,1,2,20,48]:
    m.reset();pair('CopyFarBytes',args=(n,0,offset,data,(offset+delta)&65535,data),flags=0x602 if delta<0 else 0x202,label=f'byte-window {offset:x},{delta},{n}')
 for value in [0,1,99,100,65535,0xffffffff]:
  for at in [0x278c,0x27fe,0x2816]:
   for entry in ['EncodeTwoDecimalDigits','EncodeFourDecimalDigits','EncodeSixDecimalDigits']:
    m.reset();pair(entry,regs=dict(SI=at,AX=value&65535,DX=value>>16),label=f'decimal player view {at:x} {value}')
 from dataprobe import ice_pack235
 for size in [0x478c,0x47a0,0x47d1,0x4804,0x481c]:
  m.reset();raw=(bytes(range(256))*(size//256+1))[:size];m.write(0x7500,0,ice_pack235(raw))
  # Accepted atomic ICE service: L1 writes backwards; the native bridge
  # publishes the completed buffer ascending. Returned state/ports must agree.
  pair('UnpackIceStream',regs=dict(DS=0x7500,ES=data-0x200,SI=0,DI=0xbeef),trace=False,label=f'atomic ICE crossing player lanes {size:x}')
 assert rows and prefixes and all(r['player_writes']>0 for r in rows if r['entry']=='LoadCurrentLevelState')
 assert any(r['player_writes'] for r in rows if r['entry']=='HandleKeyboardScanInterrupt'),'vacuous IRQ command writer evidence'
 save(OUT/'borrowers.json',dict(result='PASS',cases=rows,level_seed_prefixes=prefixes,scope='Full RAM outside ABI scratch stack, full Devices/ordered ports and nonempty ordered player-byte stores with complete live player snapshots; every logical level seeds both players, retained unseeded fields, DF clear/counts, all256 IRQ bytes/high-lane retention, live collision service replies, post-stone service state/cache consumer and physical aliases. No new asynchronous delivery policy.'))
def defects(ROOT,OUT,bounded,save,snapshot,previous):
 import wholegame
 folder=OUT/'defects';folder.mkdir(exist_ok=True);capture=folder/'capture.py';capture.write_text('import subprocess,sys,json\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)))\n')
 names=['cleared-command-high-byte','aliased-second-player','lost-draw-history-store','lost-carried-fare-store','lost-dino-velocity-store','missed-serialization','rebuilt-cache-from-fixed'];rows=[]
 for fault,name in enumerate(names,1):
  exe=folder/(name+'.exe');bounded([previous.timing.common.GCC,'-O2','-std=c11','-DPLAYER_TEST_FAULT='+str(fault),'-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/player_world_router.c',ROOT/'native/player_world.c',ROOT/'native/bridge/player_world_bridge.c'],'defect-router-'+str(fault)+'-compile')
  r=json.loads(bounded([sys.executable,capture,exe],'defect-router-'+str(fault)+'-run')['stdout']);assert r['returncode']!=0,(name,'survived')
  if fault==6:assert r['returncode']==88 and 'missed serialization' in r['stderr'],r
  rows.append(dict(defect=name,scope='Independent actual byte-router oracle',result='DETECTED',exit=r['returncode']))
 for tag,fault,entry in [('dino',5,'UpdateDinoForce'),('retained-loader',None,'LoadCurrentLevelState'),('stale-after-stone',None,'ThrowCarriedStone'),('collision-order',None,'SamplePlayerCollisionPixels')]:
  dest=folder/tag;dest.mkdir(exist_ok=True);cmd=json.loads((OUT/'children/api-input-composed-compile.json').read_text())['command'];cmd[cmd.index('-o')+1]=str(dest/'api.dll')
  if fault:cmd.insert(1,'-DPLAYER_TEST_FAULT='+str(fault))
  for i,v in enumerate(cmd):
   if not v.endswith('.c'):continue
   p=Path(v);text=p.read_text();changed=False
   if tag=='retained-loader' and p.name.endswith('session_bridge.c'):
    needle='EXPORT int '+('fixture_load_body' if 'EXPORT int fixture_load_body(' in text else 'c_LoadCurrentLevelState')+'(Regs *r) {';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n player_write16(DATA_SEG,D(PlayerCachedSpriteIds),0);player_write16(DATA_SEG,D(PlayerMinimumFares),0);',1);changed=True
   elif tag=='stale-after-stone' and p.name=='player_physics_bridge.c':
    # Registry composition routes PlayerPlatformIndices and velocities through
    # the player owner, bypassing the old borrower hook. Seed the stale-value
    # fault at the live physics projection consumed after the stone service.
    needle='static uint16_t physics_read(Regs *r,uint16_t base) {return '
    assert text.count(needle)==1
    replacement='static uint16_t physics_read(Regs *r,uint16_t base) {if(base==D(PlayerHorizontalVelocities))return 0;return '
    text=text.replace(needle,replacement)
    changed=True
   elif tag=='collision-order' and p.name=='player_physics_bridge.c':
    needle='pixel_collision_position(r->si,i)';assert text.count(needle)==1;text=text.replace(needle,'pixel_collision_position(r->si,9-i)');changed=True
   elif tag=='stale-after-stone' and p.name=='dispatch.c':
    assert text.count('int status=fn(r);')==2;text=text.replace('int status=fn(r);','platform_trace_entry(segment,offset,r); int status=fn(r);');changed=True
   if changed:q=dest/p.name;q.write_text(text);cmd[i]=str(q)
  guard=dest/'control.h';guard.write_text('#include <stdio.h>\n#include <stdlib.h>\n_Noreturn static inline void player_control_abort(void){fputs("PLAYER_CONTROL_BRIDGE_ASSERT\\n",stderr);exit(87);}\n#define abort player_control_abort\n')
  cmd[1:1]=['-include',str(guard)];bounded(cmd,'defect-api-'+tag+'-compile')
  consumer=dest/'consume.py';consumer.write_text('import sys\nsys.path[:0]='+repr([str(ROOT/'verif'),str(ROOT/'tools')])+'\nfrom pathlib import Path\nfrom player_world_cases import check_mutant\ncheck_mutant(Path('+repr(str(ROOT))+'),Path('+repr(str(OUT))+'),'+repr(tag)+',Path('+repr(str(dest/'api.dll'))+'))\n')
  r=json.loads(bounded([sys.executable,capture,sys.executable,consumer],'defect-api-'+tag+'-run')['stdout'])
  assert r['returncode']==87 and 'PLAYER_CONTROL_BRIDGE_ASSERT' in r['stderr'] or r['returncode']==0 and 'DETECTED' in r['stdout'],(tag,r)
  rows.append(dict(defect=tag,scope='Independent compiled L1 versus mutant composed API',entry=entry,result='DETECTED_BY_GUARD' if r['returncode']==87 else 'DETECTED',exit=r['returncode'],diagnostic=r['stdout']+r['stderr']))
 target=snapshot()
 for fault,name,scenario in [(2,'aliased-second-player','two-player'),(6,'missed-serialization','two-player')]:
  dest=folder/('host-'+name);hostcapture=previous.copy_host(target,dest);p=dest/'tools/hostbuild.py';text=p.read_text();needle="return (['-DUGH_NATIVE_PLAYER']";assert text.count(needle)==1;p.write_text(text.replace(needle,"return (['-DPLAYER_TEST_FAULT="+str(fault)+"','-DUGH_NATIVE_PLAYER']",1))
  for p in (dest/'native/bridge').glob('*'):
   if p.suffix not in ['.c','.h']:continue
   text=p.read_text()
   if 'abort()' in text:p.write_text('#include <stdio.h>\n#include <stdlib.h>\n'+text.replace('abort()','(fputs("PLAYER_CONTROL_BRIDGE_ASSERT\\n",stderr),exit(87))'))
  bounded([sys.executable,'tools/hostbuild.py'],'defect-host-'+name+'-build',dest)
  script=target/('tests/scenarios/'+scenario+'.txt');ref=json.loads((target/('build/whole/'+scenario+'.ref.json')).read_text())['frames']
  r=json.loads(bounded([sys.executable,hostcapture,dest/'build/host/ugh.exe','--headless',str(wholegame.scenario(script)['frames']),'--script',script,'--timeout','590'],'defect-host-'+name+'-run')['stdout']);got=[json.loads(line) for line in r['stdout'].splitlines()];first=next((i for i,(a,b) in enumerate(zip(got,ref)) if a!=b),None)
  assert first is not None or r['returncode']==88 and 'missed serialization' in r['stderr'] or r['returncode']==87 and 'PLAYER_CONTROL_BRIDGE_ASSERT' in r['stderr'],(name,r)
  rows.append(dict(defect=name,scenario=scenario,frame=first+1 if first is not None else len(got)+1,result='DETECTED',exit=r['returncode'],diagnostic=r['stderr']))
 save(OUT/'defects.json',dict(result='PASS',controls=rows,scope='Seven actual owner/router faults; four consuming API mutations for Dino velocity, incorrect new-level normalization, stale state after a stone service and collision-read order; two whole two-player host controls. Mutated copies only.'))

def check_mutant(ROOT,OUT,tag,path):
 import nbuild,difftest
 dlls=[nbuild.load_l1(OUT/'borrowers/reference/api.dll'),nbuild.load_l1(path)];m=difftest.Machine();data=m.seg('DGROUP:PlayerCount')
 for d in dlls:d.api_live_store.argtypes=[C.c_uint16,C.c_uint16,C.c_uint16]
 if tag=='dino':cases=[c for c in difftest.load_suite('actors_states').CASES if c.routine=='GAME:UpdateDinoForce']
 else:cases=[None]
 for case in cases:
  m.reset();regs=dict(DS=data)
  if tag=='dino':case.setup(m);regs.update(case.regs(m) if callable(case.regs) else case.regs);entry='UpdateDinoForce'
  elif tag=='retained-loader':
   m.ww('DGROUP:PlayerCount',1);m.ww('DGROUP:PlayerArrayBytes',2);m.ww('DGROUP:CurrentLevelIndex',0);m.ww('DGROUP:PlayerCachedSpriteIds',0xbabe);m.ww('DGROUP:PlayerMinimumFares',0xbeef);entry='LoadCurrentLevelState'
  elif tag=='collision-order':
   m.device.read_map=1
   for i in range(4*65536):m.device.planes[i]=((i*13+(i>>8)*37)^(i>>4))&255
   regs.update(ES=0xa000,SI=0xfffe);entry='SamplePlayerCollisionPixels'
  else:
   case=next(c for c in difftest.load_suite('actors_states').CASES if c.routine=='GAME:ThrowCarriedStone');case.setup(m);regs.update(case.regs(m) if callable(case.regs) else case.regs);difftest.load_suite('scene').move_case('post-stone').setup(m);entry='ThrowCarriedStone'
  initial=m.prepare('GAME:'+entry,{**difftest.POISON,**regs},'far',(),0x202);memory=m.snapshot();device=m.device.state();results=[]
  for d in dlls:
   C.memmove(d.ugh_memory().contents,memory,len(memory));d.ugh_devices_reset();dev=d.ugh_device_state().contents;C.memmove(C.addressof(dev),device,len(device));d.api_begin();hits=[0]
   entry_type=C.CFUNCTYPE(None,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs))
   def cut(s,o,rp,d=d,hits=hits):
    if tag=='stale-after-stone' and (s,o)==m.address('C:PlayAdlibEffect') and not hits[0]:hits[0]+=1;d.api_live_store(data,m.off('DGROUP:PlayerHorizontalVelocities'),0x1357);d.api_live_store(data,m.off('DGROUP:PlayerX32'),0x2468)
   cb=entry_type(cut);d.ugh_set_entry_observer.argtypes=[entry_type];d.ugh_set_entry_observer(cb)
   r=difftest.Regs(**{k.lower():v for k,v in initial.items()});f=getattr(d,'api_c_'+entry);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r));d.ugh_set_entry_observer(entry_type())
   if tag=='stale-after-stone':
    assert hits[0], 'vacuous stone cut';r.bx=0;r.ds=data;status=d.api_c_MovePlayerWithVgaCollisions(C.byref(r))
   ram=bytes(d.ugh_memory().contents);lo=initial['SS']*16;hi=lo+initial['SP'];results.append((status,ram[:lo]+ram[hi:],bytes(dev)))
  if results[0]!=results[1]:print('DETECTED',tag,case.title if case else entry,flush=True);return
 raise AssertionError((tag,'mutant survived independent full-state comparator'))
