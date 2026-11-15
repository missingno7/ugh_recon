"""Compiled L1/composed borrower prefixes and live service mutation for 5A."""
import ctypes as C,json,re,struct
from pathlib import Path

def run(ROOT,OUT,bounded,save):
 import nbuild,difftest
 folders=[]
 helper=r'''#include "platform.h"
#ifdef UGH_NATIVE_RUN
#include "run_world_bridge.h"
#endif
#include <string.h>
typedef struct RunTrace {uint32_t address;uint8_t value,record[26];uint16_t water,modes[2];uint32_t score;} RunTrace;
static RunTrace traces[4096];static unsigned enabled,used;
static int owned(uint32_t a){uint32_t b=(uint32_t)DATA_SEG<<4;if(a<b)return 0;unsigned o=a-b;
 return (o>=0x261c && o<0x2624)||(o>=0x2634 && o<0x263a)||(o>=0x263c && o<0x263e)||(o>=0x263f && o<0x2643)||(o>=0x264c && o<0x278c)||(o>=0x27a8 && o<0x27ac)||o==0x27cf||(o>=0x28e9 && o<0x2905);}
EXPORT void api_trace_begin(void){enabled=1;used=0;}
EXPORT unsigned api_trace_count(void){return used;}
EXPORT RunTrace *api_trace_data(void){return traces;}
void api_run_notify(uint32_t a,uint8_t value){
 if(!enabled || !owned(a))return;
 if(used==4096)return;
 RunTrace *t=&traces[used++];memset(t,0,sizeof *t);t->address=a;t->value=value;
 for(unsigned i=0;i<26;i++)t->record[i]=rd8(DATA_SEG,(uint16_t)(0x28e9+i));
 t->water=rd16(DATA_SEG,0x2903);t->modes[0]=rd16(DATA_SEG,0x263f);t->modes[1]=rd16(DATA_SEG,0x2641);t->score=rd32(DATA_SEG,0x261e);
}
void api_device_write(uint32_t,uint8_t);
void ugh_write(uint32_t a,uint8_t v){api_device_write(a,v);
#ifdef UGH_NATIVE_RUN
 if(run_is_owned(a))return;
#endif
 api_run_notify(a,v);
}
EXPORT int api_deliver_keyboard(void){Regs r={0};r.cs=GAME_SEG;r.ds=DATA_SEG;r.ss=0x8100;r.sp=0xf000;r.flags=0x202;return c_HandleKeyboardScanInterrupt(&r);}
'''
 for label in ['reference','composed']:
  folder=OUT/'api/borrowers'/label;folder.mkdir(parents=True,exist_ok=True)
  command=json.loads((OUT/'children'/('api-input-'+label+'-compile.json')).read_text())['command']
  command[command.index('-o')+1]=str(folder/'api.dll')
  for i,value in enumerate(command):
   if not value.endswith('.c'):continue
   original=Path(value);text=original.read_text()
   if original.name=='memory.c':
    assert text.count('void ugh_write(')==1;text=text.replace('void ugh_write(','void api_device_write(',1)
   elif original.name=='run_world_bridge.c':
    needle='run_field_put(fields+slot,lane,value);return 1;';assert text.count(needle)==1
    text='#include "ugh.h"\nextern void api_run_notify(uint32_t,uint8_t);\n'+text.replace(needle,'run_field_put(fields+slot,lane,value);api_run_notify(address,value);return 1;')
   else:continue
   target=folder/original.name;target.write_text(text);command[i]=str(target)
  target=folder/'trace.c';target.write_text(helper);command.append(str(target))
  bounded(command,'borrowers-'+label+'-compile');folders.append(folder)
 dlls=[nbuild.load_l1(f/'api.dll') for f in folders]
 class Trace(C.Structure):_fields_=[('address',C.c_uint32),('value',C.c_uint8),('record',C.c_uint8*26),('water',C.c_uint16),('modes',C.c_uint16*2),('score',C.c_uint32)]
 for dll in dlls:
  dll.api_trace_data.restype=C.POINTER(Trace);dll.api_trace_count.restype=C.c_uint
  dll.api_live_store.argtypes=[C.c_uint16,C.c_uint16,C.c_uint16]
 m=difftest.Machine();data=m.seg('DGROUP:PlayerCount');rows=[];prefixes=[]
 def pair(name,args=(),regs=None,flags=0x202,stop=False,mutation=False,label=None,compare_trace=True):
  initial=m.prepare('GAME:'+name,{**difftest.POISON,**(regs or {})},'far',args,flags);memory=m.snapshot();state=m.device.state();actual=[];callbacks=[]
  for dll in dlls:
   C.memmove(dll.ugh_memory().contents,memory,len(memory));dll.ugh_devices_reset();dev=dll.ugh_device_state().contents;C.memmove(C.addressof(dev),state,len(state));dll.api_begin();dll.api_trace_begin()
   C.c_int.in_dll(dll,'api_stop_at_load').value=int(stop)
   output=C.CFUNCTYPE(None,C.c_uint16,C.c_uint,C.c_uint32);injected=[False,0]
   if mutation:
    def on_output(port,size,value,dll=dll,injected=injected):
     if port==0x3c9 and not injected[0]:
      injected[0]=True;dll.api_live_store(data,m.off('DGROUP:PlayerTwoControlMode'),0x8001);dll.api_live_store(data,m.off('DGROUP:WaterYPixels'),73)
      injected[1]=dll.api_deliver_keyboard()
    cb=output(on_output);callbacks.append(cb);dll.ugh_set_output_observer.argtypes=[output];dll.ugh_set_output_observer(cb)
   r=difftest.Regs(**{k.lower():v for k,v in initial.items()});fn=getattr(dll,'api_c_'+name);fn.argtypes=[C.POINTER(difftest.Regs)];status=fn(C.byref(r))
   if mutation:dll.ugh_set_output_observer(output())
   memory_out=bytes(dll.ugh_memory().contents);lo=initial['SS']*16;hi=lo+initial['SP']
   if mutation:
    assert int.from_bytes(memory_out[data*16+0x2903:data*16+0x2905],'little')==0x1234,'intro did not restore captured water'
    assert int.from_bytes(memory_out[data*16+0x2641:data*16+0x2643],'little')==0x8001,'stale parent overwrote live mode'
   count=dll.api_trace_count();assert count<4096,'ordered borrower trace capacity reached'
   trace=C.string_at(dll.api_trace_data(),count*C.sizeof(Trace))
   actual.append((status,memory_out[:lo]+memory_out[hi:],bytes(dev),trace,injected))
  compared=[a if compare_trace else (a[0],a[1],a[2],a[4]) for a in actual]
  if compared[0]!=compared[1]:
   save(OUT/'borrower-difference.json',dict(entry=name,label=label,status=[a[0] for a in actual],first_ram=next((i for i,(a,b) in enumerate(zip(actual[0][1],actual[1][1])) if a!=b),None),trace_counts=[len(a[3])//C.sizeof(Trace) for a in actual]));raise AssertionError((name,label,'borrower mismatch'))
  if mutation:assert actual[0][4]==[True,0],actual[0][4]
  rows.append(dict(entry=name,label=label or name,status=actual[0][0],ordered_run_writes=len(actual[0][3])//C.sizeof(Trace),trace_compared=compare_trace,live_mutation=mutation))
  return actual[0][3]
 for case in difftest.load_suite('render').CASES:
  if case.routine!='GAME:LoadCurrentLevelState':continue
  m.reset();case.setup(m)
  mode=int.from_bytes(m.uc.mem_read(data*16+m.off('DGROUP:PlayerCount'),2),'little')
  level=int.from_bytes(m.uc.mem_read(data*16+m.off('DGROUP:CurrentLevelIndex'),2),'little')
  table=int.from_bytes(m.uc.mem_read(data*16+m.off('DGROUP:LevelOrderTables')+2*(mode-1),2),'little')
  record=int.from_bytes(m.uc.mem_read(data*16+table+level*2,2),'little')
  m.write(data,record+9,b'\xa7');m.write(data,record+25,b'\xd3')
  trace=pair('LoadCurrentLevelState',regs=case.regs,label=case.title+' reserved lanes')
  first=[Trace.from_buffer_copy(trace[i*C.sizeof(Trace):(i+1)*C.sizeof(Trace)]) for i in range(26)]
  expected=[data*16+0x28e9+i+j for i in range(24,-1,-2) for j in [0,1]]
  assert [t.address for t in first]==expected
  assert first[-1].record[9]==0xa7 and first[-1].record[25]==0xd3
  prefixes.append(dict(case=case.title,events=26,descending_addresses=expected))
 for players,byte_count in [(0,0xffff),(1,0),(2,2),(0xffff,4)]:
  m.reset();m.ww('DGROUP:PlayerCount',players);m.ww('DGROUP:PlayerArrayBytes',byte_count);m.ww('DGROUP:LevelWorkspacePointer',0x2648);m.ww('DGROUP:LevelWorkspacePointer',data,2)
  pair('InitializeLevelDisplay',regs=dict(DS=data),stop=True,label='independent count/bytes '+str((players,byte_count)))
 for flags in [0x202,0x602]:
  m.reset();m.ww('DGROUP:LevelWorkspacePointer',0x2648);m.ww('DGROUP:LevelWorkspacePointer',data,2);m.wb('DGROUP:LivesRemaining',249);m.ww('DGROUP:ScoreLowWord',0x1234);m.ww('DGROUP:ScoreHighWord',0xbeef)
  pair('InitializeLevelDisplay',regs=dict(DS=data),stop=True,flags=flags,label='bulk clear live direction '+hex(flags))
 for offset in [0x261c,0x261e,0x2634,0x2641,0x264c,0x278a,0x28e9,0x28fe,0x2902]:
  for delta in [-1,0,1]:
   for count in [0,1,2,26,64]:
    m.reset();pair('CopyFarBytes',(count,0,offset,data,(offset+delta)&65535,data),flags=0x602 if delta<0 else 0x202,label='ordered copy '+str((offset,delta,count)))
 for value in [0,1,99,100,65535,0xffffffff]:
  for target in [0x261e,0x263f,0x264c,0x28e9,0x28fe]:
   for name in ['EncodeTwoDecimalDigits','EncodeFourDecimalDigits','EncodeSixDecimalDigits']:
    m.reset();pair(name,regs=dict(DS=data,SI=target,AX=value&65535,DX=value>>16),label='decimal view '+str((value,target,name)))
 from dataprobe import ice_pack235
 for length in [0x461e,0x4634,0x464d,0x478c,0x48ea,0x4905]:
  # ICE is an already accepted atomic buffer service: its bridge publishes
  # completed output in ascending order, whereas L1 decodes backwards. There
  # are no game service cuts inside decode. Compare the complete returned
  # state/ports; do not invent an internal write-instruction stream contract.
  m.reset();raw=(bytes(range(256))*(length//256+1))[:length];m.write(0x7500,0,ice_pack235(raw));pair('UnpackIceStream',regs=dict(DS=0x7500,ES=data-0x200,SI=0,DI=0xbeef),label='real ICE crossing '+hex(length),compare_trace=False)
 menu=difftest.load_suite('menu')
 m.reset();menu.composition_fixture(m);m.ww('DGROUP:WaterYPixels',0x1234);m.device.script(0x60,[0x11],cycles=0xffffffff)
 pair('ShowLevelIntroduction',regs=dict(DS=data),mutation=True,label='intro saved-water restoration with live IRQ/mode mutation')
 assert rows and prefixes and any(r['ordered_run_writes'] for r in rows)
 save(OUT/'borrowers.json',dict(result='PASS',cases=rows,record_prefixes=prefixes,scope='Independent compiled L1 versus native owner: full RAM outside ABI scratch stack, full Devices/ordered ports, ordered run byte stores plus live record/mode/water/score snapshots except within the existing atomic ICE service. Synthetic reserved lanes, count/byte independence, DF bulk reset, live output-cut keyboard/mode/water mutation, copy/decimal/ICE aliases. No new delivery policy.',atomic_ice='Internal backward decode versus ascending completed-buffer publication is intentionally not a write-instruction equivalence claim; complete returned RAM/ports must match.'))
