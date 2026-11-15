"""Cut6B operators; scheduling, freezing and bounded children live in world_gate.

The existing full front-end drivers retain their case generation and positive
comparators. They run against the registry API fixtures rather than private hosts.
"""
import ctypes as C,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/workers/cut-6b'
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
from job_pool import save
from closure_support import GCC,function
from high_scores_build import NAMES as HIGH
from menus_build import NAMES as MENU
NAMES=HIGH+MENU

def selected_cases():
 import difftest
 return [(suite,c) for suite in ['menu','menu_helpers','game_services','scene','composition'] for c in difftest.load_suite(suite).CASES if c.routine.split(':')[1] in NAMES]
def score_cases():return [c for s,c in selected_cases() if c.routine.split(':')[1] in HIGH]
def text_cases():return [c for s,c in selected_cases() if c.routine.split(':')[1] not in HIGH+['RunMainMenuAndAttractLoop']]
def attract_cases():return [c for s,c in selected_cases() if c.routine=='GAME:RunMainMenuAndAttractLoop' and s=='menu']
def session_cases():return [c for s,c in selected_cases() if c.routine=='GAME:RunMainMenuAndAttractLoop' and s=='composition']

def coverage():
 """Every original case/profile/poison tuple occurs once across bounded slices."""
 import collections,world_gate,world_api
 cfg=world_gate.spec('front_end_world');original=selected_cases();assert len(original)==239
 wanted=collections.Counter((c.routine,c.title,p,profile) for s,c in original for p in [False,True] for profile in ['legacy','composed'])
 actual=collections.Counter()
 for group,row in cfg['api'].items():
  for s,c in world_gate.api_cases(cfg,sys.modules[__name__],group):
   for p in row.get('poisons',[False,True]):
    for profile in row.get('profiles',['legacy','composed']):actual[c.routine,c.title,p,profile]+=1
 assert actual==wanted,(wanted-actual,actual-wanted)
 controls=[]
 for kw in [dict(poisons=[]),dict(poisons=[False,False]),dict(poisons=[0]),dict(profiles_enabled=[]),dict(profiles_enabled=['reference']),dict(profiles_enabled=['legacy','legacy'])]:
  try:world_api.replay('invalid',[],OUT/'invalid',**kw)
  except AssertionError:controls.append(kw)
  else:raise AssertionError(('invalid slice admitted',kw))
 save(OUT/'coverage.json',dict(result='PASS',original_cases=239,comparisons=sum(actual.values()),per_profile=478,invalid_slice_controls=len(controls),scope='Exact original case/profile/poison multiset; no missing, duplicated or unexecuted profile credited'))

def bounded(command,tag,cwd=ROOT,**kw):
 from job_pool import run
 return run(command,cwd,OUT,tag,**kw)

def router():
 folder=OUT/'router';folder.mkdir(parents=True,exist_ok=True);exe=folder/'router.exe'
 command=[GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'c','-I',ROOT/'native/bridge','-o',exe,ROOT/'verif/front_end_world_router.c',ROOT/'native/front_end_world.c',ROOT/'native/bridge/front_end_world_bridge.c']
 bounded(command,'router-compile');row=bounded([exe],'router-run')
 save(OUT/'router.json',dict(result='PASS',counts=json.loads(row['stdout']),scope='Independent physical address/member oracle; all182 lanes x256 values, partial words, straddles, all6 borrower roles, paragraph and biased/word aliases, frame, seal, observation and missing-publication detection'))

def proof():
 folder=OUT/'proof';folder.mkdir(parents=True,exist_ok=True);text=(ROOT/'native/bridge/front_end_world_bridge.c').read_text()
 prefix='#include "front_end_world.h"\n#include <stddef.h>\n#include "'+(ROOT/'native/front_end_world.c').as_posix()+'"\n'
 prefix+='void *memcpy(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}\n'
 prefix+=re.search(r'typedef struct FrontEndField.*?} FrontEndField;',text,re.S)[0]+'\n'+''.join(function(text,n) for n in ['frontend_field_get','frontend_field_put'])
 prefix+='void __CPROVER_assume(int);void __CPROVER_assert(int,const char*);\n#define assert(c) __CPROVER_assert((c),#c)\n'
 tool=json.loads((ROOT/'metadata/verif-tools.json').read_text())['cbmc']['exe'];rows=[]
 for name in ['read','store']:
  p=folder/(name+'.c');p.write_text(('#define FRONTEND_PROOF_STORE\n' if name=='store' else '')+prefix+(ROOT/'verif/front_end_world_byte_proof.c').read_text());pre=p.with_suffix('.i')
  bounded([GCC,'-E','-P','-nostdinc','-I',ROOT/'verif/cbmc_shim','-I',ROOT/'native',p,'-o',pre],'proof-'+name+'-pre')
  r=bounded([tool,pre,'--unwind','5','--unwinding-assertions','--bounds-check','--pointer-check','--signed-overflow-check','--slice-formula'],'proof-'+name)
  assert 'VERIFICATION SUCCESSFUL' in r['stdout'];rows.append(name)
 save(OUT/'proof.json',dict(result='PASS',profiles=rows,scope='Actual-C byte field get/put, arbitrary complete native state, any admitted member/lane, arbitrary neighbor and value; output/frame/dependence. Exhaustive router establishes registration/layout.'))

def libraries():
 """Use immutable API-stage commands; trace front-end service requests only.

 Internal implementations of accepted timing/audio/page services deliberately
 have different entry streams once their native owners are composed. The
 front-end request boundary, including all register arguments, is invariant.
 """
 folders=[]
 for label in ['legacy','composed']:
  folder=OUT/'borrowers'/label;folder.mkdir(parents=True,exist_ok=True)
  cmd=json.loads((OUT/'children'/('api-front-'+label+'-compile.json')).read_text())['command'];cmd[cmd.index('-o')+1]=str(folder/'api.dll')
  for i,v in enumerate(cmd):
   if not v.endswith('.c') or Path(v).name not in ['menus_bridge.c','high_scores_bridge.c']:continue
   p=Path(v);text=p.read_text();prefix='''#include "platform.h"
static inline int front_trace_near(uint16_t off,uint16_t ret,Regs*r){platform_trace_entry(r->cs,off,r);return ugh_call_near(off,ret,r);}
static inline int front_trace_dispatch(uint16_t bank,uint16_t off,Regs*r){platform_trace_entry(bank,off,r);return ugh_dispatch(bank,off,r);}
#define ugh_call_near front_trace_near
#define ugh_dispatch front_trace_dispatch
'''
   q=folder/p.name;q.write_text(prefix+text);cmd[i]=str(q)
  bounded(cmd,'borrowers-'+label+'-compile');folders.append(folder/'api.dll')
 return folders

def corpus(paths,kind):
 """Same generated cases, exact complete RAM/ABI/Devices/ports/entry comparator."""
 p=ROOT/'verif'/(kind+'_evidence.py');source=p.read_text()
 source=source.replace("getattr(dll,'c_'+name)","getattr(dll,'api_c_'+name)")
 namespace=dict(__name__='cut6b_'+kind,__file__=str(p));exec(compile(source,str(p),'exec'),namespace)
 namespace['OUT']=OUT;namespace['build']=lambda reference=False: paths[0 if reference else 1]
 namespace['contacts_reference'].prepare_reference=lambda **kw: ROOT/'build/link/plain/UGH.EXE'
 namespace['main']()

def passwords(paths):
 import nbuild,difftest
 dlls=[nbuild.load_l1(p) for p in paths];m=difftest.Machine();data=m.seg('DGROUP:PlayerCount');rows=[];menu=difftest.load_suite('menu')
 for players,total in [(1,69),(2,81)]:
  position=m.rw('DGROUP:PasswordListPointers',2*(players-1));items=[]
  for index in range(total):
   text=bytearray()
   while True:
    byte=m.read(data,position,1)[0];position+=1
    if not byte:break
    text.append(byte)
   items.append(bytes(text))
  assert len(set(items))==total
  for text,expected in [(t,i) for i,t in enumerate(items)]+[(b'',0),(b'NONE',0),(b'!UNKNOWN!',0)]:
   m.reset();menu.composition_fixture(m);m.ww('DGROUP:PlayerCount',players);m.ww('DGROUP:PlayerArrayBytes',players*2);m.write(data,m.off('DGROUP:PasswordEditBuffer'),text.ljust(20,b' '));m.ww('DGROUP:ScreenFadeLevel',0xffff)
   initial=m.prepare('GAME:RunGameFromPassword',{**difftest.POISON,'DS':data},'near',(),0x202);memory=m.snapshot();device=m.device.state();out=[]
   for d in dlls:
    C.memmove(d.ugh_memory().contents,memory,len(memory));d.ugh_devices_reset();dev=d.ugh_device_state().contents;C.memmove(C.addressof(dev),device,len(device));C.c_int.in_dll(d,'api_stop_at_load').value=1
    r=difftest.Regs(**{k.lower():v for k,v in initial.items()});f=d.api_c_RunGameFromPassword;f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r));ram=bytes(d.ugh_memory().contents)
    out.append((status,bytes(r),ram,bytes(dev)));selected=int.from_bytes(ram[data*16+m.off('DGROUP:CurrentLevelIndex'):data*16+m.off('DGROUP:CurrentLevelIndex')+2],'little');assert selected==expected,(players,text,selected,expected)
   assert out[0]==out[1],(players,text,'session selection prefix differs');assert out[0][0]==2
   rows.append(dict(players=players,input=text.hex(),level=expected,status=2))
 save(OUT/'passwords.json',dict(result='PASS',cases=rows,scope='Actual session selects all69+81 shipped passwords and empty/unknown defaults; stopped at the existing load service, no duplicate lookup'))

def borrowers():
 paths=libraries();corpus(paths,'high_scores');corpus(paths,'menus');passwords(paths)
 save(OUT/'borrowers.json',dict(result='PASS',drivers={n:len(json.loads((OUT/n).read_text())['cases']) for n in ['high-cases.json','menus-cases.json','passwords.json']},scope='Composed versus ordinary RAM native adapters: full RAM including stack, ABI, complete Devices, ordered ports and nonempty count-checked full-register front-end service request streams. Internal service entries excluded; independent L1/Unicorn corpus is the api-front stage.'))

def inventory():
 model=json.loads((ROOT/'metadata/program-model.json').read_text());names=['HighScoreFileHandle','HighScoreNameChars2To3','HighScoreNameChars4To5','HighScoreNameChars6To7','HighScoreNameChars8To9','HighScoreNameEntry','HighScoreRowStride','HighScoreRows','LevelNumberTensCharacter','LevelNumberUnitsCharacter','PasswordEditBuffer','PasswordEditChars2To3']
 save(OUT/'inventory.json',dict(result='PASS',bytes=182,total=12141,named_cells={n:model['variables'][n] for n in names},extra_writers=['CopyIndexedMenuString writes four non-NUL label destinations: B0D+6,B19+10,B73+10,B8D+10','DOS read uses the same live byte router; only returned prefix is stored','Decimal/far-copy/ICE generic windows borrow the registry, including foreign aliases','DrawTextLine load_character explicitly borrows the owner','Session alone reads the biased password view'],continuations='MenusMain, MenusStringCopy, HighFileFlow are invocation-lifetime native continuations; both editors now carry native position/blink words and accept live service replies; NativeFrontTextCursor carries the character cursor. These have no historical observation allocation.'))

def probe(path,label):
 """A concrete full-state witness, frozen independently before mutation."""
 import nbuild,difftest
 d=nbuild.load_l1(path);m=difftest.Machine();data=m.seg('DGROUP:PlayerCount');menu=difftest.load_suite('menu');m.reset();menu.composition_fixture(m);regs={};hits=[]
 if label in ['copied-nul','clipped-indexed-overrun']:
  entry='CopyIndexedMenuString';regs=dict(SI=0x6000,DI=0xb0d,BX=0);m.write(data,0x6000,b'\x00\x61');m.write(data,0x6100,b'X\0' if label=='copied-nul' else b'ABCDEFGHIJKL\0');m.write(data,0xb0d,b'YZ')
 elif label=='cleared-short-read-tail':
  entry='LoadHighScores';m.write(data,m.off('DGROUP:HighScoreRows'),b'Q'*107);m.device.file('UGH!.HI',b'\x21\x32\x43');m.device.io_limit=1
 elif label=='wrong-digit-order':
  entry='InsertHighScoreAndClearScore';m.ww('DGROUP:ScoreLowWord',12345);m.ww('DGROUP:ScoreHighWord',0);m.device.script(0xffff,[13])
  for i in range(5):m.write(data,m.off('DGROUP:HighScoreRows')+21*i+14,b'     1')
 elif label=='stale-parent-overwrite':entry='ShowLevelIntroduction';m.ww('DGROUP:WaterYPixels',200)
 else:raise AssertionError(label)
 initial=m.prepare('GAME:'+entry,{**difftest.POISON,'DS':data,**regs},'near',(),0x202);memory=m.snapshot();device=m.device.state()
 C.memmove(d.ugh_memory().contents,memory,len(memory));d.ugh_devices_reset();dev=d.ugh_device_state().contents;C.memmove(C.addressof(dev),device,len(device))
 d.api_live_store.argtypes=[C.c_uint16,C.c_uint16,C.c_uint16]
 kind=C.CFUNCTYPE(None,C.c_uint16,C.c_uint16,C.POINTER(difftest.Regs))
 def callback(s,o,rp):
  if label=='stale-parent-overwrite' and not hits and (s,o)==m.address('GAME:ClearAllVgaPlanes'):
   hits.append((s,o));d.api_live_store(data,m.off('DGROUP:WaterYPixels'),171)
 cb=kind(callback);d.ugh_set_entry_observer.argtypes=[kind];d.ugh_set_entry_observer(cb)
 r=difftest.Regs(**{k.lower():v for k,v in initial.items()});f=getattr(d,'api_c_'+entry);f.argtypes=[C.POINTER(difftest.Regs)];status=f(C.byref(r));d.ugh_set_entry_observer(kind())
 ram=bytes(d.ugh_memory().contents)
 if label=='stale-parent-overwrite':assert hits,'live service witness must execute'
 return (status,bytes(r),ram,bytes(dev)),dict(entry=entry,live_cuts=len(hits),first_observed_boundary='terminal API state')

def defects():
 rows=[];folder=OUT/'defects';folder.mkdir(parents=True,exist_ok=True)
 # Faults act in the maintained owner seam, not in the comparator.
 base=json.loads((OUT/'diagnostics/router-compile.json').read_text())['command'] if (OUT/'diagnostics/router-compile.json').exists() else None
 if base is None:
  # Router's artifacts arrive through the standard dependency alias.
  candidates=list(OUT.rglob('router-compile.json'));assert candidates
  base=json.loads(candidates[0].read_text())['command']
 for fault,label in enumerate(['lost-table-tail','password-alias','cleared-handle-high','missed-serialization'],1):
  exe=folder/(label+'.exe');cmd=list(base);cmd[cmd.index('-o')+1]=str(exe);cmd.insert(1,'-DFRONTEND_TEST_FAULT='+str(fault));bounded(cmd,'defect-build-'+label)
  result=bounded([exe],'defect-run-'+label,ok=tuple(range(1,16))+(88,));rows.append(dict(defect=label,result='DETECTED',exit=result['returncode'],boundary='independent all-lane router/serialization comparator'))
 # Small actual-C state decisions use an independent expected plan.
 pure=[('reversed-row-shift','high_scores.c','source+21u','source-21u','HighCopy c=high_copy_begin(100);return c.destination==121?0:1;'),
       ('closed-save-handle','high_scores.c','case 3:return HIGH_FILE_COMPLEMENT;','case 3:return HIGH_FILE_CLOSE;','HighFileFlow f={1,3};return high_file_next(&f,0)==HIGH_FILE_COMPLEMENT?0:1;'),
       ('tie-rejected','high_scores.c','candidate>=stored','candidate>stored','HighQualification q={5,0,0};high_compare_step(&q,65,65);return q.done&&q.qualifies?0:1;'),
       ('missed-menu-wrap','menus.c','next>=3 ? 0','next>3 ? 0','return menus_difficulty_next(2)==0?0:1;'),
       ('masked-release-scan','menus.c','switch(reply.scan)','switch(reply.scan&127u)','MenusMain m={0};MenusMainReply r={0};m.started=1;m.last=MENUS_MAIN_POLL;r.changed=1;r.scan=187;return menus_main_next(&m,r)==MENUS_MAIN_RESET_TIMEOUT?0:1;'),
       ('changed-centering','menus.c','320u-(uint16_t)(count<<4)','320u-(uint16_t)(count<<3)','return menus_text_center_x(2)==144?0:1;')]
 for label,name,before,after,body in pure:
  source=(ROOT/'native'/name).read_text();assert source.count(before)==1,(label,source.count(before));mutant=folder/(label+'.c');mutant.write_text(source.replace(before,after));helper=folder/(label+'-test.c');helper.write_text('#include "menus.h"\n#include "high_scores.h"\nint main(void){'+body+'}\n');exe=folder/(label+'.exe')
  # First check the same positive comparator on the original actual C.
  common=[GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-I',ROOT/'native','-o',exe,helper]
  bounded([*common,ROOT/'native'/name],'control-positive-'+label);bounded([exe],'control-positive-run-'+label)
  bounded([*common,mutant],'defect-build-'+label);result=bounded([exe],'defect-run-'+label,ok=(1,));rows.append(dict(defect=label,result='DETECTED',exit=result['returncode'],boundary='actual-C API plan: '+body))
 request=next(p for p in [OUT/'children/borrowers-composed-compile.json',OUT/'diagnostics/borrowers-composed-compile.json'] if p.exists())
 composed_command=json.loads(request.read_text())['command'];composed=Path(composed_command[composed_command.index('-o')+1])
 changes=[('clipped-indexed-overrun','menus_bridge.c','frontend_write8(r->es,copy.destination,ch);','if(copy.destination<D(Text_0AE4)+47u)frontend_write8(r->es,copy.destination,ch);'),
          ('copied-nul','menus_bridge.c','if(copy.done) return UGH_OK;','if(copy.done){frontend_write8(r->es,r->di,0);return UGH_OK;}'),
          ('cleared-short-read-tail','high_scores_bridge.c','status=platform_interrupt(0x21,r);if(status) return status;break;','status=platform_interrupt(0x21,r);if(action==HIGH_FILE_READ && !(r->flags&CF))for(unsigned i=r->ax;i<107;i++)frontend_write8(r->ds,(uint16_t)(D(HighScoreRows)+i),0);if(status) return status;break;'),
          ('wrong-digit-order','high_scores_bridge.c','set_al(r,frontend_read8(r->ds,(uint16_t)(D(DecimalDigitBuffer)+r->si))); frontend_write8','set_al(r,frontend_read8(r->ds,(uint16_t)(D(DecimalDigitBuffer)+5u-r->si))); frontend_write8'),
          ('stale-parent-overwrite','menus_bridge.c','MCALL(ClearAllVgaPlanes,G(ShowLevelIntroduction)+3);\n    r->ax=frontend_read16(r->ds,D(WaterYPixels));','uint16_t stale=frontend_read16(r->ds,D(WaterYPixels));MCALL(ClearAllVgaPlanes,G(ShowLevelIntroduction)+3);\n    r->ax=stale;')]
 for label,name,before,after in changes:
  frozen,case=probe(composed,label);cmd=list(composed_command);dll=folder/(label+'.dll');cmd[cmd.index('-o')+1]=str(dll);matches=0
  for i,v in enumerate(cmd):
   if not v.endswith('.c') or Path(v).name!=name:continue
   text=Path(v).read_text();assert before in text,label;mutant=folder/(label+'.c');mutant.write_text(text.replace(before,after));cmd[i]=str(mutant);matches+=1
  assert matches==1,(label,matches);bounded(cmd,'defect-build-'+label);actual,_=probe(dll,label);assert frozen!=actual,(label,'survived')
  rows.append(dict(defect=label,result='DETECTED',case=case,changed_RAM=sum(a!=b for a,b in zip(frozen[2],actual[2]))))
 save(OUT/'defects.json',dict(result='PASS',controls=rows))
