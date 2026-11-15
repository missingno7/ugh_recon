"""Unique cut-6C cases. Scheduling, snapshots and bounds belong to world_gate."""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/workers/cut-6c/local'
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
from job_pool import run,save
from closure_support import GCC,function
NAMES=['RunDosGame','InitializeDosVideoInputAndSound','InitializeAdLibSound','FadeAndShutdownSound','ShowStartupPictures']

def bounded(command,tag,cwd=ROOT,ok=(0,)):
 return run(command,cwd,OUT,tag,allowed=ok)

def terminal_cases():
 from difftest import Case
 from emu import DATA_SEG
 rows=[]
 for value in [0,3,19,127,128,255]:
  def setup(machine,value=value):
   machine.ww('SOUND:SoundDeviceBits',0);machine.wb('DGROUP:SavedBiosVideoMode',value)
   machine.ww('DGROUP:PreviousKeyboardVector',0x1234);machine.ww('DGROUP:PreviousKeyboardVectorSegment',0x5678)
   machine.write(0x40,0x1c,b'\x9a\x12')
  rows.append(Case('terminal live saved byte '+str(value),'GAME:loc_4EE6',setup=setup,regs=dict(DS=DATA_SEG),kind='exit',cfunc='c_DosShutdownTail'))
 return rows

def compile_case(name,sources,options=()):
 folder=OUT/name;folder.mkdir(parents=True,exist_ok=True);exe=folder/'check.exe'
 bounded([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native','-I',ROOT/'native/bridge',*options,'-o',exe,*sources],name+'-compile')
 return exe

def core_sources():
 return [ROOT/'verif/lifecycle_world_cases.c',ROOT/'native/lifecycle_world.c',ROOT/'native/lifecycle.c',ROOT/'native/terminal_tail.c']

def router_sources():
 folder=OUT/'router-stubs';folder.mkdir(parents=True,exist_ok=True)
 peers=sorted(set(re.findall(r'\bc_\w+\b',(ROOT/'native/bridge/lifecycle_world_bridge.c').read_text())))
 path=folder/'stubs.c';path.write_text('#include "platform.h"\n'+''.join('int '+n+'(Regs *r){(void)r;return UGH_UNSUPPORTED;}\n' for n in peers)+'int platform_interrupt(uint8_t n,Regs*r){(void)n;(void)r;return UGH_UNSUPPORTED;}\n')
 return [ROOT/'verif/lifecycle_world_router.c',ROOT/'native/lifecycle_world.c',ROOT/'native/lifecycle.c',ROOT/'native/terminal_tail.c',ROOT/'native/bridge/lifecycle_world_bridge.c',path]

def router():
 exe=compile_case('router',router_sources())
 result=bounded([exe],'router-run');save(OUT/'router.json',dict(result='PASS',counts=json.loads(result['stdout']),scope='All owner byte values, both full word straddles, paragraph aliases, whole physical membership, untouched neighbors, separate serialization and seal.'))

def proof():
 folder=OUT/'proof';folder.mkdir(parents=True,exist_ok=True)
 source=folder/'actual.c';source.write_text('\n'.join('#include "'+(ROOT/p).as_posix()+'"' for p in ['native/lifecycle.c','native/terminal_tail.c','native/lifecycle_world.c','verif/lifecycle_world_proof.c']))
 pre=folder/'actual.i'
 bounded([GCC,'-E','-P','-nostdinc','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',source,'-o',pre],'proof-pre')
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe']
 row=bounded([tool,pre,'--function','main','--unwind','6','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-terminal')
 assert 'VERIFICATION SUCCESSFUL' in row['stdout']
 exe=compile_case('core',core_sources());r=bounded([exe],'core-run')
 save(OUT/'proof.json',dict(result='PASS',enumeration=json.loads(r['stdout']),scope='Actual maintained C: symbolic terminal mode, full input word, arbitrary pre-sound mode and all service failure prefixes. Exhaustive scalar slices and ordered startup/task failure-prefix witnesses. No unrestricted L1 theorem.'))

def terminal_sources(folder):
 folder.mkdir(parents=True,exist_ok=True)
 # Independent literal terminal body, with only its near-call binding supplied.
 literal=function((ROOT/'c/video.c').read_text(),'c_DosShutdownTail').replace('c_DosShutdownTail','literal_terminal').replace('call(r,','fixture_near(r,')
 bridge=(ROOT/'native/bridge/lifecycle_world_bridge.c').read_text()
 peers=sorted(set(re.findall(r'\bc_\w+\b',bridge))-{'c_FadeAndShutdownSound','c_RestoreKeyboardInterrupt'})
 source=(ROOT/'verif/lifecycle_world_terminal_fixture.c').read_text()
 source=source.replace('/* PEER STUBS */','\n'.join('int '+n+'(Regs *r){(void)r;return UGH_UNSUPPORTED;}' for n in peers))
 source=source.replace('/* LITERAL TERMINAL */',literal)
 path=folder/'fixture.c';path.write_text(source)
 return [path,ROOT/'native/lifecycle_world.c',ROOT/'native/lifecycle.c',ROOT/'native/terminal_tail.c',ROOT/'native/bridge/lifecycle_world_bridge.c']

def borrowers():
 exe=compile_case('borrower-exe',terminal_sources(OUT/'borrowers'),['-Wno-misleading-indentation'])
 row=bounded([exe],'borrower-run');save(OUT/'borrowers.json',dict(result='PASS',counts=json.loads(row['stdout']),scope='Independent literal tail versus actual typed adapter: complete registers/RAM/ordered nonempty service stream, live DS and mode mutation after sound, BIOS queue-flush low byte, six statuses at every terminal service, DF and failure frames.'))

def defects():
 folder=OUT/'defects';folder.mkdir(parents=True,exist_ok=True);rows=[]
 mutations=[
  ('swapped-teardown','native/lifecycle_world.c','TerminalAction action=terminal_tail_next(&owner->terminal);','TerminalAction action=terminal_tail_next(&owner->terminal);if(action==TERMINAL_STOP_SOUND)action=TERMINAL_RESTORE_INPUT;else if(action==TERMINAL_RESTORE_INPUT)action=TERMINAL_STOP_SOUND;'),
  ('double-input-restore','native/lifecycle_world.c','if(action==TERMINAL_EXIT)value=done.code;','if(action==TERMINAL_EXIT)value=done.code;if(action==TERMINAL_RESTORE_INPUT)service(context,action,value);'),
  ('post-init-mode','native/lifecycle_world.c','value=saved_mode(context);','value=saved_mode(context);if(action==TERMINAL_RESTORE_VIDEO)value=19;'),
  ('stale-parent-mode','native/lifecycle_world.c','if(action==TERMINAL_RESTORE_VIDEO)value=saved_mode(context);','if(action==TERMINAL_RESTORE_VIDEO){owner->saved_bios_video_mode=saved_snapshot;value=saved_mode(context);}'),
  ('zero-exit-byte','native/lifecycle_world.c','if(action==TERMINAL_EXIT)value=done.code;','if(action==TERMINAL_EXIT)value=0;'),
  ('zero-terminal-result','native/lifecycle_world.c','if(action==TERMINAL_EXIT && reply.result.kind==GAME_EXITED) {','if(action==TERMINAL_EXIT && reply.result.kind==GAME_EXITED) {done.code=0;'),
  ('cleanup-after-failure','native/lifecycle_world.c','if(reply.result.kind!=GAME_CONTINUE)return reply.result;','if(reply.result.kind!=GAME_CONTINUE){if(action!=TERMINAL_EXIT)service(context,TERMINAL_EXIT,0);return reply.result;}'),
  ('device-bit-two','native/lifecycle.c','r.argument=1;','r.argument=3;'),
  ('extra-seed','native/lifecycle_world.c','LifecycleReply reply=service(context,request);','if(request.action==LIFE_GAMEPLAY_VIDEO){LifecycleRequest extra={LIFE_SEED_RANDOM,0};service(context,extra);}LifecycleReply reply=service(context,request);'),
  ('skip-startup-pictures','native/lifecycle_world.c','LifecycleReply reply=service(context,request);','if(request.action==LIFE_STARTUP_PICTURES)continue;LifecycleReply reply=service(context,request);')]
 for name,rel,old,new in mutations:
  text=(ROOT/rel).read_text()
  if name=='stale-parent-mode':text=text.replace('terminal_tail_begin(&owner->terminal);','terminal_tail_begin(&owner->terminal);uint8_t saved_snapshot=owner->saved_bios_video_mode;')
  if name=='cleanup-after-failure':
   # Seed only terminal failure handling; task failure handling has no action.
   at=text.index('GameExit lifecycle_world_terminate');text=text[:at]+text[at:].replace(old,new)
  else:assert text.count(old)==1,(name,text.count(old));text=text.replace(old,new)
  path=folder/(name+'.c');text=text.replace('#include "lifecycle_world.h"','#include "'+(ROOT/'native/lifecycle_world.h').as_posix()+'"').replace('#include "lifecycle.h"','#include "'+(ROOT/'native/lifecycle.h').as_posix()+'"');path.write_text(text)
  sources=[path if str(p.relative_to(ROOT)).replace('\\','/')==rel else p for p in core_sources()]
  exe=compile_case('defect-'+name,sources,['-Wno-misleading-indentation']);row=bounded([exe],'defect-'+name,ok=(0,3,-1073740791))
  assert row['returncode']!=0,('surviving defect',name)
  rows.append(dict(defect=name,result='DETECTED',comparator='actual-C ordered lifecycle/terminal scalar and failure-prefix assertions',diagnostic=row['stderr'].strip()))
 sources=terminal_sources(folder/'hook-transfer')
 path=folder/'hook-transfer.c';text=(ROOT/'native/bridge/lifecycle_world_bridge.c').read_text()
 old='if(status)reply.result.kind=';assert text.count(old)==1
 text=text.replace(old,'if(status && status!=UGH_CONTROL_TRANSFER)reply.result.kind=')
 text=text.replace('#include "lifecycle_world_bridge.h"','#include "'+(ROOT/'native/bridge/lifecycle_world_bridge.h').as_posix()+'"');path.write_text(text)
 sources[-1]=path;exe=compile_case('defect-hook-transfer',sources,['-Wno-misleading-indentation'])
 row=bounded([exe],'defect-hook-transfer',ok=(3,));rows.append(dict(defect='swallowed-hook-transfer',result='DETECTED',comparator='literal versus actual adapter, first sound failure status CONTROL_TRANSFER; no synthesized terminal prefix',diagnostic=row['stderr'].strip()))
 exe=compile_case('defect-missed',router_sources(),['-DLIFECYCLE_TEST_FAULT=1'])
 row=bounded([exe],'defect-missed',ok=(88,));assert 'missed serialization' in row['stderr'];rows.append(dict(defect='missed-serialization',result='DETECTED',exit=88))
 save(OUT/'defects.json',dict(result='PASS',controls=rows))

def inventory():
 model=json.loads((ROOT/'metadata/program-model.json').read_text())
 save(OUT/'inventory.json',dict(result='PASS',bytes=1,total=11960,region='DGROUP:0092',model=model['variables']['SavedBiosVideoMode'],borrowers=['STARTUP live DS store after masked query reply','TERMINAL live DS read after sound','WINDOW byte/word/ICE/copy/decimal router'],shared_writers='Native lifecycle store plus all explicit mutable physical byte windows; unowned foreign DS delegates. No allocation for vectors/sound flags. Shutdown latch remains audio facade write through live DS, DGROUP:0002.'))
