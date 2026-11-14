"""Generated-copy and clean-overlay evidence for three retiring entries.

Serial children are limited to 600 seconds and 8 GiB. Certificates remain
unanalyzed; only the archived acceptance overlay is promoted.
"""
import argparse, ctypes as C, hashlib, io, json, os, re, shutil, subprocess, sys, tarfile, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/workers/close-adlx-21'
sys.path.insert(0,str(ROOT/'tools'))
from windows_job import WindowsJob,ExtendedLimits
from closure_support import GCC,function
NAMES=['DispatchActorUpdates','loc_0B4E','DosShutdownTail']
UNITS=['actor_pass','terminal_tail']
FILES=[*(f'native/{u}.{s}' for u in UNITS for s in ['c','h']),
       *(f'native/bridge/{u}_bridge.c' for u in UNITS),
       'verif/entry_retirement.py','verif/entry_retirement_proof.c',
       'verif/projector_evidence.py','verif/projector/publications.py',
       *(f'metadata/closure/{u}.json' for u in UNITS)]
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def bounded(command,tag,cwd=ROOT):
 OUT.mkdir(parents=True,exist_ok=True);command=list(map(str,command));start=time.perf_counter()
 env=dict(os.environ,PATH=str(GCC.parent)+os.pathsep+os.environ.get('PATH',''))
 with WindowsJob() as job:
  limits=ExtendedLimits();limits.basic.flags=0x2000|0x100|0x200;limits.process_memory=limits.job_memory=8*1024**3
  if not job.kernel.SetInformationJobObject(job.handle,9,C.byref(limits),C.sizeof(limits)):raise C.WinError(C.get_last_error())
  p=subprocess.Popen(command,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);job.assign(p)
  try:stdout,stderr=p.communicate(timeout=600)
  except subprocess.TimeoutExpired:
   job.terminate();stdout,stderr=p.communicate()
   save(OUT/'children'/f'{tag}.json',dict(result='TIMEOUT',stdout=stdout,stderr=stderr));raise RuntimeError(tag+' timed out')
 row=dict(command=command,cwd=str(cwd),stdout=stdout,stderr=stderr,returncode=p.returncode,seconds=time.perf_counter()-start,timeout_seconds=600,memory_limit_bytes=8*1024**3)
 save(OUT/'children'/f'{tag}.json',row)
 if p.returncode:
  save(OUT/'negative'/f'{tag}-{time.time_ns()}.json',row)
  raise RuntimeError(tag+': '+stdout[-2000:]+stderr[-4000:])
 print(tag,'PASS',round(row['seconds'],2),'s',flush=True);return row
def targets():
 p=json.loads((ROOT/'metadata/program-model.json').read_text());names={x['address']:n.split(':')[1] for n,x in p['routines'].items()}
 return [names[a] for a in p['indirect_sites']['013B:1492']['targets']]

def static():
 import hostbuild
 p=json.loads((ROOT/'metadata/program-model.json').read_text())
 exports={n:dict(component=u['component'],bridge=str(u['bridge'].relative_to(ROOT))) for u in hostbuild.selected_units() for n in u['exports']}
 callbacks=[]
 for name in targets():
  assert 'c_'+name in exports,(name,'not already native')
  callbacks.append(dict(name=name,**exports['c_'+name]))
 noop=p['routines']['GAME:loc_0B4E']
 indirect=[k for k,v in p['indirect_sites'].items() if '013B:0B4E' in v.get('targets',[])]
 assert not noop['callers'] and not indirect
 save(OUT/'static.json',dict(result='PASS',callbacks=callbacks,
      actor_callers=p['routines']['GAME:DispatchActorUpdates']['callers'],
      noop=dict(static_callers=noop['callers'],indirect_sites=indirect,meaning='Unexplained standalone return; distinct from IgnoreActorState'),
      terminal=dict(entry='c/dispatch_table.inc maps GAME:loc_4EE6 to c_DosShutdownTail',
                    timer_coupling='FadeAndShutdownSound -> ShutdownSoundSystem -> ShutdownAdlibPlayback -> RestoreTimerInterrupt completes before BIOS mode and keyboard restoration',
                    raw_body=function((ROOT/'c/video.c').read_text(),'c_DosShutdownTail')),
      inputs={n:sha(ROOT/n) for n in ['metadata/program-model.json','c/demo_scripts.c','c/video.c','c/dispatch_table.inc']}))

def build(seam=False,mutant=None):
 import nbuild
 tag=('seam' if seam else 'real')+('-'+mutant[0] if mutant else '')
 folder=OUT/tag;folder.mkdir(parents=True,exist_ok=True);sources=[];ts=targets()
 for p in sorted((ROOT/'c').glob('*.c')):
  text=p.read_text()
  for n in NAMES:text=re.sub(r'(EXPORT int )c_'+n+r'(?=\()',r'\1l1_'+n,text)
  for i,n in enumerate(ts+['FadeAndShutdownSound','RestoreKeyboardInterrupt']):
   if 'EXPORT int c_'+n+'(' not in text:continue
   body=function(text,'c_'+n)
   if seam:new='EXPORT int c_'+n+'(Regs *r) { return retire_service('+str(i)+',r); }\n'
   else:new=body.replace('{','{ platform_trace_entry(GAME_SEG,G('+n+'),r);',1)
   text=text.replace(body,new)
  text='#include "platform.h"\nint retire_service(unsigned,Regs *);\n'+text
  target=folder/p.name;target.write_text(text);sources.append(target)
 for u in UNITS:
  for rel in [f'native/{u}.c',f'native/bridge/{u}_bridge.c']:
   p=ROOT/rel;text=p.read_text()
   if mutant and mutant[1]==rel:
    assert mutant[2] in text;text=text.replace(mutant[2],mutant[3])
   text=re.sub(r'#include "([^"]+)"',lambda m:'#include "'+(p.parent/m[1]).resolve().as_posix()+'"' if (p.parent/m[1]).is_file() else m[0],text)
   dest=folder/('native_'+p.name);dest.write_text(text);sources.append(dest)
 helper=folder/'fixture.c';helper.write_text(r'''#include "platform.h"
EXPORT unsigned fixture_mode,fixture_arg,fixture_count,fixture_fail_at;
EXPORT int fixture_status;
EXPORT int retire_service(unsigned which,Regs *r) {
 platform_trace_entry(GAME_SEG,(uint16_t)(100+which),r); ++fixture_count;
 if(which<36) {
  if(fixture_mode==1) {r->bx=(uint16_t)fixture_arg;r->ds=0x7500;
   wr16(r->ds,(uint16_t)(D(ActorDescriptors)+r->bx+2),0xffff);}
  if(fixture_mode==2 && fixture_count==1) {
   wr16(r->ds,D(ActorUpdateOrScriptCursor)+2,G(IgnoreActorState));
   wr16(r->ds,D(ActorDescriptors)+2,0);
   wr16(r->ds,D(ActorDescriptors)+4,0xffff);
  }
  if(fixture_mode==4) r->bx=0xfffe;
 } else if(which==36) {r->ds=0x7500;set_al(r,0x75);}
 else set_al(r,(uint8_t)fixture_arg);
 return !fixture_fail_at || fixture_fail_at==which ? fixture_status : 0;
}
''')
 # Expose the actual bridge mapping, not a separate model.
 dest=folder/'native_actor_pass_bridge.c';dest.write_text(dest.read_text()+'\nEXPORT int fixture_identity(uint16_t word) {return callback_identity(word);}\n')
 sources.append(helper);dll=folder/'pair.dll'
 bounded([GCC,'-shared','-O2','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-function','-fwrapv','-I',ROOT/'c','-o',dll,*sources],tag+'-compile')
 save(folder/'inputs.json',{p.relative_to(ROOT).as_posix():sha(p) for p in [*sorted((ROOT/'c').glob('*.[ch]')),*[ROOT/f for f in FILES if f.endswith(('.c','.h','.py'))]]})
 return nbuild.load_l1(dll)

def pair(dll,initial,r,name,expected=None):
 from difftest import MEM_SIZE,Regs
 trace=[]
 typ=C.CFUNCTYPE(None,C.c_uint16,C.c_uint16,C.POINTER(Regs))
 observer=typ(lambda seg,off,reg:trace.append((seg,off,reg.contents.bx)))
 dll.ugh_set_entry_observer(observer);observations=[]
 for prefix in ['l1_','c_']:
  C.memmove(dll.ugh_memory().contents,initial,MEM_SIZE);dll.ugh_devices_reset();trace.clear()
  C.c_uint.in_dll(dll,'fixture_count').value=0
  actual=Regs.from_buffer_copy(r);code=getattr(dll,prefix+name)(C.byref(actual))
  dev=dll.ugh_device_state().contents
  observations.append((code,bytes(actual),bytes(dll.ugh_memory().contents),bytes(dev),list(trace)))
 dll.ugh_set_entry_observer(typ())
 if expected is not None:assert len(observations[0][4])==expected,(name,len(observations[0][4]),expected)
 return observations

def cases():
 from difftest import Case,Regs,run,load_suite
 from emu import Machine
 real=build();m=Machine();rows=[];unicorn=[]
 original=[c for s in ['demo_scripts','composition'] for c in load_suite(s).CASES if c.routine=='GAME:DispatchActorUpdates']
 def terminal_setup(machine,mode=3):
  machine.ww('SOUND:SoundDeviceBits',0);machine.wb('DGROUP:SavedBiosVideoMode',mode)
  machine.ww('DGROUP:PreviousKeyboardVector',0x1234);machine.ww('DGROUP:PreviousKeyboardVectorSegment',0x5678)
  machine.write(0x40,0x1c,b'\x20\x00')
 original += [Case('reserved return','GAME:loc_0B4E',out_regs=('AX','BX','CX','DX','SI','DI','BP','DF'))]
 original += [Case('terminal saved byte '+str(v),'GAME:loc_4EE6',setup=lambda a,v=v:terminal_setup(a,v),kind='exit',cfunc='c_DosShutdownTail') for v in [0,3,0x13,0xff]]
 for case in original:
  for poison in [False,True]:
   for prefix in ['l1_','c_']:
    name='DosShutdownTail' if case.kind=='exit' else case.routine.split(':')[1]
    case.cfunc=prefix+name;problems=run(case,m,real,poison);assert not problems,(case.title,prefix,poison,problems)
    unicorn.append(dict(case=case.title,target=prefix+name,poison=poison,steps=m.steps))
  m.reset()
  if case.setup:case.setup(m)
  regs=case.regs(m) if callable(case.regs) else case.regs
  rdict=m.prepare(case.routine,regs,case.kind,(),case.flags);r=Regs(**{k.lower():v for k,v in rdict.items()})
  name='DosShutdownTail' if case.kind=='exit' else case.routine.split(':')[1]
  a,b=pair(real,m.snapshot(),r,name);assert a==b,(case.title,'compiled full RAM/devices/registers/entry streams')
  if name=='DosShutdownTail':assert len(a[4])==2
  if name=='DispatchActorUpdates' and '[]' not in case.title:assert a[4],case.title
  rows.append(dict(case=case.title,entries=len(a[4])))
 seam=build(True);srows=[];mem=bytearray(m.snapshot());ds=m.seg('DGROUP:ActorDescriptors');desc=m.off('DGROUP:ActorDescriptors');cur=m.off('DGROUP:ActorUpdateOrScriptCursor')
 def word(b,seg,off,val):b[seg*16+(off&65535):seg*16+(off&65535)+2]=int(val).to_bytes(2,'little')
 def seamcase(label,mode,arg,status,target,expected):
  b=bytearray(mem);word(b,ds,desc,0);word(b,ds,desc+2,65535);word(b,ds,cur,target)
  C.c_uint.in_dll(seam,'fixture_mode').value=mode;C.c_uint.in_dll(seam,'fixture_arg').value=arg;C.c_int.in_dll(seam,'fixture_status').value=status
  r=Regs(ds=ds,cs=m.seg('GAME:DispatchActorUpdates'),ss=0x9000,sp=0x100,flags=0xed7)
  a,b=pair(seam,bytes(b),r,'DispatchActorUpdates',expected);assert a==b,(label,'seam')
  if expected:assert a[4]
  srows.append(dict(case=label,entries=len(a[4]),status=a[0]));return a
 for n in targets():seamcase(n,0,0,0,m.off('GAME:'+n),1)
 for cursor in [0,1,2,30,32,0x7fff,0xfffd,0xfffe,0xffff]:seamcase('returned cursor '+hex(cursor),1,cursor,0,m.off('GAME:IgnoreActorState'),1)
 seamcase('reread modified future callback',2,0,0,m.off('GAME:IgnoreActorState'),2)
 for status in [1,2,3,4,5]:seamcase('callback status '+str(status),0,0,status,m.off('GAME:IgnoreActorState'),1)
 seamcase('full returning budget',4,0,0,m.off('GAME:IgnoreActorState'),32768)
 seamcase('unsupported callback',0,0,0,0xffff,0)
 for status in [0,1,4,5]:
  for mode in [0,3,0xff]:
   b=bytearray(mem);b[0x75000+m.off('DGROUP:SavedBiosVideoMode')]=mode
   C.c_int.in_dll(seam,'fixture_status').value=status;C.c_uint.in_dll(seam,'fixture_arg').value=0x9a
   a,z=pair(seam,bytes(b),Regs(ds=ds,cs=m.seg('GAME:loc_4EE6'),ss=0x9000,sp=0x100,flags=0xed7),'DosShutdownTail',2 if not status else 1)
   assert a==z,('terminal live reply',mode,status)
   if not status:assert seam.ugh_device_state().contents.video_mode==mode and seam.ugh_device_state().contents.exit_code==0x9a
   srows.append(dict(case='terminal live DS/mode '+str(mode),reply=status,entries=len(a[4])))
 expected={m.off('GAME:'+n):i+1 for i,n in enumerate(targets())};seam.fixture_identity.argtypes=[C.c_uint16]
 # Fail-closed extension outside the original target-set admission: do not run
 # arbitrary valid DOS code words as L1 expected results for that extension.
 image=bytearray(mem);word(image,ds,desc,0)
 C.memmove(seam.ugh_memory().contents,bytes(image),len(image));rawmem=seam.ugh_memory().contents
 C.c_uint.in_dll(seam,'fixture_count').value=0;closed=0
 for raw in range(65536):
  assert seam.fixture_identity(raw)==expected.get(raw,0),raw
  if raw in expected:continue
  address=ds*16+cur;rawmem[address]=raw&255;rawmem[address+1]=raw>>8
  r=Regs(ds=ds,cs=m.seg('GAME:DispatchActorUpdates'),ss=0x9000,sp=0x100,flags=0xed7)
  assert seam.c_DispatchActorUpdates(C.byref(r))==3 and r.sp==0xfe and r.bx==0,raw
  assert C.c_uint.in_dll(seam,'fixture_count').value==0,raw
  closed+=1
 C.c_uint.in_dll(seam,'fixture_fail_at').value=37
 for status in [1,2,3,4,5]:
  C.c_int.in_dll(seam,'fixture_status').value=status
  a,z=pair(seam,bytes(mem),Regs(ds=ds,cs=m.seg('GAME:loc_4EE6'),ss=0x9000,sp=0x100,flags=0xed7),'DosShutdownTail',2)
  assert a==z and a[0]==status
  srows.append(dict(case='terminal input failure',reply=status,entries=2))
 C.c_int.in_dll(seam,'fixture_status').value=0
 C.c_uint.in_dll(seam,'fixture_fail_at').value=0
 typ=C.CFUNCTYPE(C.c_int,C.c_uint8,C.POINTER(Regs))
 for number in [0x10,0x21]:
  for status in [1,2,3,4,5]:
   service=typ(lambda n,r,num=number,st=status:st if n==num else -1)
   seam.ugh_set_interrupt_service(service)
   a,z=pair(seam,bytes(mem),Regs(ds=ds,cs=m.seg('GAME:loc_4EE6'),ss=0x9000,sp=0x100,flags=0xed7),'DosShutdownTail',1 if number==0x10 else 2)
   assert a==z and a[0]==status
   srows.append(dict(case='terminal interrupt failure '+hex(number),reply=status,entries=len(a[4])))
 seam.ugh_set_interrupt_service(typ())
 save(OUT/'cases.json',dict(result='PASS',real=rows,unicorn=unicorn,seams=srows,identity_domain=65536,unsupported_words_fail_closed=closed,source='Actual maintained L1 and bridges; callback seam substitutes both sides identically; unmodified callbacks separately tested.'))
 print('cases PASS',len(rows),'real;',len(unicorn),'Unicorn;',len(srows),'seam cases; 65536 identities',flush=True)

def mutations():
 from emu import Machine
 from difftest import Regs
 m=Machine();m.ww('DGROUP:ActorDescriptors',0);m.ww('DGROUP:ActorUpdateOrScriptCursor',m.off('GAME:IgnoreActorState'));m.ww('DGROUP:ActorDescriptors',65535,2)
 r=Regs(ds=m.seg('DGROUP:ActorDescriptors'),cs=m.seg('GAME:DispatchActorUpdates'),ss=0x9000,sp=0x100,flags=0xed7)
 specs=[('sentinel','native/actor_pass.c','descriptor==UINT16_MAX','descriptor==0'),
 ('cursor','native/actor_pass.c','live_cursor+2u','pass->cursor+2u+(live_cursor&0u)'),
 ('word','native/bridge/actor_pass_bridge.c','D(ActorUpdateOrScriptCursor)+pass.cursor','D(ActorUpdateOrScriptCursor)'),
 ('order','native/terminal_tail.c','TERMINAL_STOP_SOUND,TERMINAL_RESTORE_VIDEO','TERMINAL_RESTORE_VIDEO,TERMINAL_STOP_SOUND'),
 ('mode','native/terminal_tail.c','return saved_mode;','return (uint8_t)(saved_mode&127u);')]
 rows=[]
 for spec in specs:
  dll=build(True,spec);C.c_uint.in_dll(dll,'fixture_arg').value=0xfffe;C.c_uint.in_dll(dll,'fixture_mode').value=1 if spec[0]=='cursor' else 2 if spec[0]=='word' else 0
  if spec[0] in ['order','mode']:
   b=bytearray(m.snapshot());b[0x75000+m.off('DGROUP:SavedBiosVideoMode')]=0xff
   a,z=pair(dll,bytes(b),r,'DosShutdownTail')
  else:
   if spec[0]=='word':m.ww('DGROUP:ActorUpdateOrScriptCursor',m.off('GAME:BeginStonePickupWait'))
   a,z=pair(dll,m.snapshot(),r,'DispatchActorUpdates')
  assert a!=z,spec[0];rows.append(dict(mutation=spec[0],result='DETECTED'))
 save(OUT/'mutations.json',dict(result='PASS',controls=rows))

def proof():
 folder=OUT/'proof';folder.mkdir(exist_ok=True)
 bounded([GCC,'-E','-P','-nostdinc','-DUINT16_MAX=65535u','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',ROOT/'verif/entry_retirement_proof.c','-o',folder/'proof.i'],'proof-preprocess')
 manifest=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc'];tool=Path(manifest['exe'])
 assert hashlib.sha256(tool.read_bytes()).hexdigest()==manifest['exe_sha256']
 row=bounded([tool,folder/'proof.i','--unwind','7','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof')
 assert 'VERIFICATION SUCCESSFUL' in row['stdout'];save(OUT/'proof.json',dict(result='PASS',domain='Actual complete native selection/resume and terminal continuation; arbitrary descriptor/callback/cursor/count (admitted 0..32768); frame and output. Not an L1/ABI proof.',inputs={p:sha(ROOT/p) for p in FILES if p.endswith(('.c','.h','.py'))},preprocessed_sha256=sha(folder/'proof.i')))

def certificate():
 import closure
 for u,names,addresses in [('actor_pass',['DispatchActorUpdates','loc_0B4E'],['013B:1486','013B:0B4E']),('terminal_tail',['DosShutdownTail'],['013B:4EE6'])]:
  fs=[f'native/{u}.c',f'native/{u}.h',f'native/bridge/{u}_bridge.c']
  c=dict(component=u,status='unanalyzed',original=dict(owned=[dict(identity='GAME:'+('loc_4EE6' if n=='DosShutdownTail' else n),address=a) for n,a in zip(names,addresses)],L1=['c/demo_scripts.c' if u=='actor_pass' else 'c/video.c'],L0=['src/asm/GAME.ASM']),
    native=dict(files=fs,functions=['actor_pass_begin','actor_pass_select','actor_pass_resume','actor_reserved_return'] if u=='actor_pass' else ['terminal_tail_begin','terminal_tail_next','terminal_tail_video_mode'],bridge=['c_'+n for n in names]),
    purpose='Additive native continuation adapter; no changes to accepted peer semantics or state ownership.',
    interface=dict(inputs='Borrowed live actor descriptor/callback and returned cursor' if u=='actor_pass' else 'Synchronous terminal services and saved-mode byte read after sound returns',outputs='Ordered typed callback requests; stop on sentinel or first error; verification guard 32768' if u=='actor_pass' else 'Sound stop, saved-video-mode restore, input restore, terminal exit in that order; first error stops prefix'),
    callers=['session: InitializeLevelDisplay and RunGameFromPassword; no-op has no static or indirect caller' if u=='actor_pass' else 'lifecycle: RunDosGame tail; startup Q terminal transfer'],
    callees=['36 accepted native actor entry adapters, direct switches without resolver or dispatcher' if u=='actor_pass' else 'lifecycle FadeAndShutdownSound, input RestoreKeyboardInterrupt; platform BIOS set-mode and DOS exit services'],
    indirect=['Complete 36-target set at program-model indirect_sites[013B:1492]; unknown raw words fail UGH_BAD_CALLBACK after near-frame push; no L1 fallback' if u=='actor_pass' else 'No indirect native transfer'],
    memory=dict(owner='No persistent second owner',reads='Live DS, descriptor/callback word and post-callback BX/DS every iteration' if u=='actor_pass' else 'SavedBiosVideoMode through live DS after sound returns; keyboard restore owns its cells',writes='Only peer effects and retiring ABI stack; no-op preserves all' if u=='actor_pass' else 'Only peer services and retiring ABI stack'),
    assumptions=['Ordinary synchronous admitted peer bridges; executable callback code immutable, no alias into active native locals; GAME entry segment. Existing peer admission assumptions unchanged.','Native callback identities are closed; raw script cursors are not inferred as callbacks.'],
    eliminated=['Executed L1 entry body; dispatcher round trip on the new direct peer edges; no fallback.'],
    retained=['Live cursor/data-view rereads, sentinel-before-callback, 16-bit wrapping +2 and 32768 harness guard' if u=='actor_pass' else 'Mode is an unmasked byte read live after sound; input may change AL before exit; error prefix has no rollback; sound may reach timer restoration before video/input.', 'Broken hooks remain explicit existing L1 boundaries; Sound Blaster unreachable in shipped game (AdLib-only startup, absent samples/stub bank hooks, broken far-call/near-RET probe).'],
    evidence=[],amiga=dict(classification='not-used',finding='DOS boundary determined by code and accepted peers'),uncertainty=['Certificates intentionally remain unanalyzed for supervisor review. Scenario evidence does not prove all states.','Native proof is a continuation property, not a universal L1 or peer-alias theorem.'],
    dependencies={f:closure.actual_dependencies(ROOT/f) for f in fs},verification_input_hashing='sha256-lf-text')
  c['interface']['widths']='Actor descriptor and live cursor uint16_t; callback is a closed native enum (36 identities); remaining uint32_t <=32768; synchronous peer status int, zero returns normally.' if u=='actor_pass' else 'Transient cursor uint8_t; four TerminalAction requests; saved mode uint8_t copied unmasked; synchronous service status int; nonzero aborts the prefix. Exit consumes the live AL byte after input restoration.'
  if u=='terminal_tail':
   c['assumptions'][1]='GAME entry segment; BIOS set-mode service preserves the code segment; peer control-transfer/terminal statuses abort before subsequent actions.'
  for prop,level,arg,artifact in [('compiled L1/native and rebuilt ASM differential','C','--cases','cases.json'),('complete raw callback identity mapping and fail-closed extension','A','--cases','cases.json'),('actual native continuation output/frame properties (not L1 equivalence)','B','--proof','proof.json'),('seeded mutation controls','C','--mutations','mutations.json'),('clean overlay gates and census','D','--accept','acceptance.json'),('unchanged projector observations with producer publication','D','--projector','projector/summary.json'),('missed ICE publication must fail comparison','C','--missed-publication','missed-publication.json')]:
   if u!='actor_pass' and level=='A':continue
   p=OUT/artifact;c['evidence'].append(dict(property=prop,level=level,method='See reproducible driver and artifact for exact domains; no reference-derived expected state',command='python verif/entry_retirement.py '+arg,result='PASS' if p.exists() and json.loads(p.read_text()).get('result')=='PASS' else 'not run',date='2026-11-14',artifact=p.relative_to(ROOT).as_posix()))
  locks=[*fs,'verif/entry_retirement.py','verif/entry_retirement_proof.c',
         'verif/projector_evidence.py','verif/projector/publications.py','metadata/program-model.json','metadata/verif-tools.json',
         *[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'c').glob('*')) if p.suffix in ['.c','.h','.inc']],
         *[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'tests').glob('*.py'))]]
  c['verification_inputs']={p:sha(ROOT/p) for p in locks};save(ROOT/f'metadata/closure/{u}.json',c)

def snapshot():
 revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();target=OUT/'baseline'
 if target.exists():assert json.loads((OUT/'baseline.json').read_text())['revision']==revision,'HEAD changed: use a fresh archive'
 if not target.exists():
  raw=subprocess.check_output(['git','archive','--format=tar',revision],cwd=ROOT)
  with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
   for member in archive.getmembers():
    if not member.isfile():continue
    p=(target/member.name).resolve();assert p.is_relative_to(target.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(archive.extractfile(member).read())
 for f in FILES:
  p=target/f;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,p)
 for u in UNITS:
  p=target/f'metadata/closure/{u}.json';j=json.loads(p.read_text());j['status']='migrated';save(p,j)
 refs=target/'build/whole';refs.mkdir(parents=True,exist_ok=True)
 for p in (ROOT/'build/whole').glob('*.ref.json'):shutil.copyfile(p,refs/p.name)
 save(target/'build/workers/c-close/call-edges.json',[])
 save(OUT/'baseline.json',dict(revision=revision,overlay={f:sha(ROOT/f) for f in FILES},excluded='All uncommitted files except FILES; in particular timer_lifetime*'))
 return target

def accept():
 target=snapshot();rows=[]
 for i,args in enumerate([['tools/closure.py'],['tools/build.py'],['tools/hostbuild.py'],['host/check.py','--variant','native'],['tools/hostbuild.py','--literal'],['host/check.py','--variant','literal'],['verif/standalone_census.py','--all']]):rows.append(bounded([sys.executable,*args],'accept-'+str(i),target))
 census=json.loads((target/'build/workers/close-adlx-19/census.json').read_text())
 forbidden={'c_'+n for n in NAMES}|{'l1_'+n for n in NAMES}
 bodies=[f for f in census['functions'] if f['kind']=='c' and f['name'] in forbidden];assert not bodies,bodies
 assert sum(s['fallback_calls'] for s in census['scenarios'])==0
 save(OUT/'acceptance.json',dict(result='PASS',baseline=json.loads((OUT/'baseline.json').read_text()),commands=rows,retired_bodies=bodies,fallbacks=0,census_sha256=sha(target/'build/workers/close-adlx-19/census.json'),projector='Run --projector separately; artifact projector/summary.json'))

def prepare_projector(name):
 # Equivalent overlay run. Frozen sources come solely from the clean archive
 # plus this exact promoted overlay. No publication/resynchronization changes.
 target=OUT/'baseline';assert target.is_dir()
 import projector_evidence as pe
 pe.OUT=OUT/name;pe.OUT.mkdir(exist_ok=True);frozen=pe.OUT/'frozen'
 if not frozen.exists():
  for top in ['c','native','host','metadata','tests','tools','src']:shutil.copytree(target/top,frozen/top)
 # Refresh the explicitly recorded overlay, never live game observations.
 for name in FILES:
  p=frozen/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(target/name,p)
 revision=json.loads((OUT/'baseline.json').read_text())['revision']
 save(pe.OUT/'baseline.json',dict(commit=revision,scope='Committed HEAD archive plus only close-adlx-21 promoted overlay',overlay=json.loads((OUT/'baseline.json').read_text())['overlay']))
 return pe,revision,frozen

def projector():
 pe,revision,frozen=prepare_projector('projector')
 pe.build(False,revision);pe.build(True,revision)
 for p in sorted((frozen/'tests/scenarios').glob('*.txt')):pe.one(p.stem,p.stem=='gameplay')
 pe.one('smoke');pe.summarize()
 assert json.loads((pe.OUT/'summary.json').read_text())['result']=='PASS'
 print('overlay projector PASS',flush=True)

def missed_publication():
 pe,revision,frozen=prepare_projector('projector-missed-publication')
 pe.instrument_publication=lambda relative_path,text:text
 pe.build(False,revision)
 try:pe.one('adlib')
 except RuntimeError:
  failure=json.loads((pe.OUT/'children/run-adlib.json').read_text())
  assert 'difference kind=1 offset=108400' in failure['stderr']
  assert 'serialization differs at frame 3' in failure['stderr']
  save(OUT/'missed-publication.json',dict(result='PASS',control='DETECTED missing producer publication; no resynchronization',scenario='adlib',frame=3,ram_byte=108400,child=failure,executable_sha256=sha(pe.OUT/'instrumented/ugh.exe')))
 else:raise AssertionError('missed publication was not detected')

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for a in ['cases','mutations','proof','static','certificate','accept','projector','missed-publication','internal']:p.add_argument('--'+a,action='store_true')
 a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
 if a.static:static()
 for name in ['cases','mutations','proof','projector','missed_publication']:
  if getattr(a,name):
   if a.internal:globals()[name]()
   else:bounded([sys.executable,__file__,'--'+name.replace('_','-'),'--internal'],name+'-child')
 if a.certificate:certificate()
 if a.accept:accept()
if __name__=='__main__':main()
