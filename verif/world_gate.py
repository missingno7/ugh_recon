"""Shared composition evidence gate. Worlds provide selectors and case operators.

Each independent stage gets a private source/data tree and a private8-GiB,
600-second Job. Scheduling metadata lives outside deterministic receipts.
"""
import argparse,ast,collections,concurrent.futures,hashlib,importlib,importlib.util,io,json,os,re,shutil,subprocess,sys,tarfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
import world_registry
from job_pool import run,save

NEW_FILES=['tools/world_registry.py','tools/gate.py','verif/world_gate.py','verif/world_api.py','verif/job_pool.py','verif/contract_locks.py','verif/level_check.py','verif/process_refactor.py','verif/world_registry_cases.py','verif/palette_platform_model.inc']
def declared_world_files(row):
 """Explicit per-world sources; never sweep another worker's untracked files."""
 name=row['component'];files={row['registry_file'].relative_to(ROOT).as_posix(),row['header'],row['bridge'],row['gate']['cases']}
 certificate=ROOT/'metadata/closure'/(name+'.json')
 if certificate.exists():
  c=json.loads(certificate.read_text());files.add(certificate.relative_to(ROOT).as_posix());files.update(c.get('native',{}).get('files',[]));files.update(c.get('verification_inputs',{}))
 if row.get('platform_provider'):files.add(row['platform_provider'])
 files.update(row.get('files',[]))
 case=ROOT/row['gate']['cases']
 if case.is_file():
  cfg=ast.literal_eval(ast.parse(case.read_text()).body[1].value)
  if cfg.get('legacy'):files.add('verif/'+cfg['legacy'].replace('.','/')+'.py')
  for module in cfg.get('case_adapters',[]):files.add('verif/'+module.replace('.','/')+'.py')
 return files

def owned_files(component=None,baseline=None):
 modified=set(subprocess.check_output(['git','diff','HEAD','--name-only'],cwd=ROOT,text=True).splitlines())
 untracked=set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines())
 if baseline is None:
  tracked=set(subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=ROOT,text=True).splitlines())
  certificates={Path(f).stem:json.loads(subprocess.check_output(['git','show','HEAD:'+f],cwd=ROOT,text=True)) for f in tracked if f.startswith('metadata/closure/') and f.endswith('.json')}
 else:
  baseline=Path(baseline);tracked={p.relative_to(baseline).as_posix() for p in baseline.rglob('*') if p.is_file()}
  certificates={p.stem:json.loads(p.read_text()) for p in (baseline/'metadata/closure').glob('*.json')}
 admitted={c.get('component',name) for name,c in certificates.items() if c.get('status') in ['migrated','verified-under-assumptions','verified-within-contract','integration-validated']}
 if component:admitted.add(component)
 declared=set();inactive=set()
 for row in world_registry.entries(components=admitted):declared.update(declared_world_files(row))
 if baseline:
  for p in (baseline/'metadata/worlds').glob('*.json'):
   if p.stem in admitted:continue
   row=json.loads(p.read_text());c=certificates.get(p.stem,{})
   inactive.update([p.relative_to(baseline).as_posix(),'metadata/closure/'+p.name,row['header'],row['bridge'],row['gate']['cases'],*row.get('files',[]),*c.get('native',{}).get('files',[])])
 shared=[*NEW_FILES,'verif/world_cases/__init__.py','verif/world_cases/legacy_adapter.py']
 paths=((modified & (tracked|declared))-inactive) | (untracked & declared) | {p for p in shared if (ROOT/p).is_file()}
 return sorted(p for p in paths if not p.startswith(('port/','tests/port/','verif/port_')) and p!='tools/respack.py')

def sha(p):return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def reset_generated(path,parent):
 path=Path(path);parent=Path(parent).resolve()
 assert parent.is_relative_to((ROOT/'build').resolve()),('generated output must be under build',parent)
 assert path.resolve().parent==parent and path.name in ['frozen','baseline'],('unsafe generated reset',path)
 if path.exists():shutil.rmtree(path)

def freeze(out,component=None):
 out=Path(out);tree=out/'frozen';out.mkdir(parents=True,exist_ok=True);reset_generated(tree,out);revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 raw=subprocess.check_output(['git','archive','--format=tar',revision],cwd=ROOT)
 with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
  for m in archive.getmembers():
   if m.isfile():p=tree/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(archive.extractfile(m).read())
 overlay=owned_files(component,tree)
 for rel in overlay:p=tree/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,p)
 for bank in ['link','oracle','whole','levels','levels-audio','levels-deep']:
  if bank in ['link','oracle']:shutil.copytree(ROOT/'build'/bank,tree/'build'/bank,dirs_exist_ok=True)
  else:
   target=tree/'build'/bank;target.mkdir(parents=True,exist_ok=True)
   for p in (ROOT/'build'/bank).glob('*.ref.json'):shutil.copyfile(p,target/p.name)
 # Preserve independently recorded raw source bytes (not expected observations).
 # git archive uses LF; the DOS build receipt may pin unchanged CRLF inputs.
 build_inputs=json.loads((ROOT/'build/link/plain/build.json').read_text())['source_sha256']
 for rel,digest in build_inputs.items():
  source=ROOT/rel;assert hashlib.sha256(source.read_bytes()).hexdigest()==digest,('stale DOS build input',rel)
  target=tree/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
 shutil.copytree(ROOT/'assets',tree/'assets',dirs_exist_ok=True)
 inputs={p:sha(ROOT/p) for p in overlay}
 if component:
  certificate=tree/'metadata/closure'/(component+'.json');c=json.loads(certificate.read_text())
  if c['status'] in ['unanalyzed','analyzed','boundary-established']:
   c['status']='migrated';save(certificate,c)
 save(out/'snapshot.json',dict(revision=revision,inputs=inputs));return tree

def entry(component):return next(iter(world_registry.entries(components={component})))
def spec(component):
 p=ROOT/entry(component)['gate']['cases'];return ast.literal_eval(ast.parse(p.read_text()).body[1].value)

def load_cases(component,out):
 from world_cases import legacy_adapter
 cfg=spec(component);module=importlib.import_module(cfg['legacy']);
 for name,m in list(sys.modules.items()):
  if name.startswith('world_cases.legacy_') and name!='world_cases.legacy_adapter':legacy_adapter.module(name,Path(m.__file__))
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 for name in cfg.get('case_adapters',[]):importlib.import_module(name).install(legacy_adapter)
 # Helpers keep their original input fixtures and compare code. Only retired
 # hostbuild compiler-selector edits become explicit registry flag operations.
 helper_names={p.stem for p in (ROOT/'verif').glob('*_cases.py') if not p.stem.startswith(('port_','world_'))}
 for name in helper_names:
  p=ROOT/'verif'/(name+'.py')
  if 'tools/hostbuild.py' in p.read_text():legacy_adapter.module(name,p)
 import closure
 def bounded(command,tag,cwd=ROOT,env=None,ok=(0,),**kw):
  r=run(command,cwd,out,tag,env=env,allowed=ok);save(out/'children'/(tag+'.json'),r);return r
 def snapshot():return ROOT
 for m in list(sys.modules.values()):
  if m is None:continue
  f=getattr(m,'__file__','') or ''
  if not f or not str(Path(f).resolve()).startswith(str(ROOT/'verif')):continue
  if m.__name__ in ['world_gate','world_api','job_pool']:continue
  if hasattr(m,'OUT'):m.OUT=out
  if hasattr(m,'ROOT'):m.ROOT=ROOT
  if hasattr(m,'bounded'):m.bounded=bounded
  if hasattr(m,'snapshot'):m.snapshot=snapshot
  if hasattr(m,'relock'):m.relock=lambda *a,**k:None
  if hasattr(m,'locks'):m.locks=lambda *a,**k:None
 return cfg,module,bounded

def api_cases(cfg,module,group):
 import difftest
 row=cfg['api'][group];cases=[(s,c) for s in row['suites'] for c in difftest.load_suite(s).CASES]
 names=getattr(module,'NAMES',[])+row.get('extra_names',[])
 if row.get('names_kind')=='hud':names=module.NAMES[:8]+module.NAMES[17:]+['InsertHighScoreAndClearScore','GetHighScoreDigits']
 if row.get('names_kind')=='weather':names=module.NAMES[8:17]
 if row.get('filter'):cases=[(s,c) for s,c in cases if c.routine.split(':')[1] in names]
 if row.get('callbacks'):
  import timer_callbacks;cases += [('timer_callbacks',c) for c in timer_callbacks.CASES]
 for name in row.get('extra_modules',[]):cases += [('scene',c) for c in importlib.import_module(name).cases()]
 for name in row.get('extra_case_modules',[]):cases += [('dos_input',c) for c in importlib.import_module(name).CASES]
 if row.get('extra_case_function'):cases += [('scene',c) for c in getattr(module,row['extra_case_function'])()]
 if row.get('expected_cases') is not None:assert len(cases)*2>=row['expected_cases'],(group,len(cases)*2,row['expected_cases'],'lost API cases')
 return cases

def aliases(out,dependencies):
 # Historical case consumers take compiled commands as structured inputs. They
 # receive references to immutable API-stage sources, never another stage's output.
 out=Path(out)
 for name,path in dependencies.items():
  if not name.startswith('api-'):
   for p in Path(path).iterdir():
    if p.name in ['receipt.json','baseline']:continue
    target=out/p.name
    if p.is_dir():shutil.copytree(p,target,dirs_exist_ok=True)
    else:target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
   continue
  group=name[4:];api=Path(path)/'api'
  if not api.exists():continue
  for profile in ['reference','legacy','composed']:
   p=api/'diagnostics'/('api-'+profile+'-compile.json')
   if p.exists():
    save(out/'children'/('api-'+group+'-'+profile+'-compile.json'),json.loads(p.read_text()))
    if group=='api':save(out/'children'/('api-'+profile+'-compile.json'),json.loads(p.read_text()))
   source=api/profile
   for target in [out/'api'/group/profile,out/'api'/profile]:
    if source.exists():shutil.copytree(source,target,dirs_exist_ok=True)

def stage_projector(out,revision):
 import projector_evidence as pe
 out=Path(out);pe.OUT=out/'projector';pe.OUT.mkdir(parents=True,exist_ok=True);target=pe.OUT/'frozen'
 for top in ['c','native','host','metadata','tests','tools','src']:shutil.copytree(ROOT/top,target/top,dirs_exist_ok=True)
 save(pe.OUT/'baseline.json',dict(commit=revision,scope='Frozen registry composition overlay'))
 pe.build(False,revision);pe.build(True,revision)
 for p in sorted((target/'tests/scenarios').glob('*.txt')):pe.one(p.stem,p.stem=='gameplay')
 pe.one('smoke');pe.summarize()
 rows=[json.loads(p.read_text()) for p in (pe.OUT/'runs').glob('*.json')];assert len(rows)==21
 assert all(r['canonical_native_owned_bytes']==sum(w['lanes']['bytes'] for w in world_registry.selected(__import__('hostbuild').selected_units())) and not r['native_owned_journal_publications'] for r in rows)
 result=dict(result='PASS',runs=rows);save(out/'projector.json',result);return result

def stage_census(out,bounded,revision):
 # Instrument a generated copy. Hot numeric leaves have a static no-machine-edge
 # check instead of billions of artificial enter/leave events.
 p=ROOT/'verif/standalone_census.py';text=p.read_text();marker="        if source=='native/bridge/timing_world_bridge.c' and name in {";assert text.count(marker)==1
 names={r['bridge'] for r in world_registry.entries()};addition="        if source in "+repr(names)+" and re.search(r'(?:_field(?:_get|_put)?|_shared_(?:read|write)|_is_owned|_borrow(?:ed_(?:byte|store)|_(?:read|write)))$',name):\n            assert not re.search(r'\\b(?:l1_\\w+|ugh_dispatch\\w*|ugh_call_near\\w*|platform_\\w+)\\s*\\(',text[b+1:e])\n            continue\n"
 text=text.replace("revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()",'revision='+repr(revision))
 p.write_text(text.replace(marker,addition+marker));bounded([sys.executable,p,'--all'],'census')
 folder=ROOT/'build/workers/close-adlx-19';summary=json.loads((folder/'census.json').read_text());assert len(summary['scenarios'])==21
 assert all(not x['fallback_calls'] and not x['l1_body_calls'] for x in summary['scenarios'])
 save(Path(out)/'census.json',dict(result='PASS',summary=summary));return dict(result='PASS',summary=summary)

def declared_defects(component,cfg,out,bounded):
 """New worlds can seed host faults without a private scheduling/build driver.

 Historical-case operators remain grouped adapters with exact inventory checks.
 Scenario-flag operators are fully described by this declarative request.
 """
 rows=[];out=Path(out)
 for case in cfg['defects']:
  assert case['kind']=='scenario-flag',case
  folder=out/'defects'/case['id'];folder.mkdir(parents=True,exist_ok=True)
  for top in ['c','native','host','metadata','tools','verif','src','tests']:
   shutil.copytree(ROOT/top,folder/top,dirs_exist_ok=True)
  shutil.copytree(ROOT/'build/link',folder/'build/link',dirs_exist_ok=True)
  row=entry(component);p=folder/row['registry_file'].relative_to(ROOT);r=json.loads(p.read_text());r['compile_flags'].append(case['flag']);save(p,r)
  host=folder/'host-output';bounded([sys.executable,'tools/hostbuild.py','--no-generate','--out',host],'defect-build-'+case['id'],cwd=folder)
  command=[host/'ugh.exe','--headless',str(case.get('frames',48)),'--script',folder/'tests/scenarios'/(case['scenario']+'.txt'),'--timeout','590']
  result=bounded(command,'defect-run-'+case['id'],cwd=folder,ok=(case.get('exit',0),))
  if case.get('exit',0):
   assert case['stderr_contains'] in result['stderr'],result
   rows.append(dict(defect=case['id'],result='DETECTED',exit=case['exit']))
  else:
   actual=[json.loads(line) for line in result['stdout'].splitlines()];expected=json.loads((ROOT/'build/whole'/(case['scenario']+'.ref.json')).read_text())['frames']
   assert len(actual)>=2,'empty defect observation'
   first=next((i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b),None);assert first is not None,('surviving defect',case['id'])
   rows.append(dict(defect=case['id'],result='DETECTED',scenario=case['scenario'],frame=first))
 result=dict(result='PASS',controls=rows);save(out/'defects.json',result);return result

def child(component,stage,out,revision,dependencies):
 out=Path(out);os.environ['UGH_WORLD_BUILD_DIR']=str(out/'registry');cfg,module,bounded=load_cases(component,out);aliases(out,dependencies)
 if stage.startswith('api-'):
  import world_api
  group=stage[4:];cases=api_cases(cfg,module,group)
  if not cases:result=dict(result='PASS',group=group,composed_matching=0,legacy_matching=0,explicit_out_of_domain=[],compatibility_cases=[],scope='Zero relevant API cases explicitly inventoried')
  else:result=world_api.replay(group,cases,out/'api',cfg['api'][group].get('allowed_rejections',[]),cfg.get('worlds_enabled'),cfg['api'][group].get('poisons'),cfg['api'][group].get('profiles'))
 elif stage=='projector':result=stage_projector(out,revision)
 elif stage=='census':result=stage_census(out,bounded,revision)
 elif stage=='build':
  bounded([sys.executable,'tools/gate.py','--jobs','1','--out',out/'gate'],'gate');result=json.loads((out/'gate/receipt.json').read_text())
 elif stage=='levels':
  rows={}
  for variant in ['native','literal']:
   host=out/('host-'+variant);bounded([sys.executable,'tools/hostbuild.py','--out',host,*(['--literal'] if variant=='literal' else [])],'levels-build-'+variant);rows[variant]={}
   for group in ['openings','audio','deep']:
    folder=out/variant/group;bounded([sys.executable,'verif/level_check.py','--host',host,'--out',folder,'--group',group,'--variant',variant],'levels-'+variant+'-'+group);rows[variant][group]=json.loads((folder/'receipt.json').read_text())
  result=dict(result='PASS',groups=rows);save(out/'levels.json',result)
 else:
  if stage=='defects' and all(r['kind']=='scenario-flag' for r in cfg['defects']):declared_defects(component,cfg,out,bounded)
  else:getattr(module,stage)()
  p=out/cfg.get('result_files',{}).get(stage,stage+'.json')
  if stage=='defects' and not p.exists():p=out/'mutations.json'
  assert p.exists(),(component,stage,'no result receipt');result=json.loads(p.read_text());assert result.get('result','PASS')=='PASS',result
  if stage=='defects':
   controls=result.get('controls',result.get('mutations',result.get('cases',[])))
   observed=[r.get('defect',r.get('mutation',r.get('label',str(i)))) for i,r in enumerate(controls)]
   assert collections.Counter(observed)==collections.Counter(r['id'] for r in cfg['defects']),(component,'changed defect inventory',observed,cfg['defects'])
   assert all(str(r.get('result','')).startswith('DETECTED') or r.get('detected') or any(d['id']==r.get('defect') and d.get('expected_result')==r.get('result') and d.get('expected_exit')==r.get('exit') for d in cfg['defects']) for r in controls),(component,'surviving defect',controls)
 save(out/'receipt.json',result);return result

def canonical(value,root):
 if isinstance(value,dict):return {k:canonical(v,root) for k,v in value.items() if k not in ['seconds','wall_seconds','command','cwd','dll','executable_sha256','build_sha256','inputs','frozen_inputs','seam_inputs','reference_sha256']}
 if isinstance(value,list):return [canonical(x,root) for x in value]
 if isinstance(value,str):return re.sub(r'(?<=wall=)[0-9]+(?:\.[0-9]+)?s\b','<time>s',value.replace(str(root),'<gate>').replace(str(ROOT),'<source>'))
 return value

def standard_stages(component):
 cfg=spec(component)
 return ['router','proof',*('api-'+g for g in cfg['api']),*([n for n in ['backend','borrowers'] if callable(getattr(importlib.import_module(cfg['legacy']),n,None))]),*cfg.get('extra_stages',[]),'defects','build','projector','census','levels',*([n for n in ['inventory','reuse','deepcounts'] if callable(getattr(importlib.import_module(cfg['legacy']),n,None))])]

def gate(component,out,jobs=3,stages=None):
 if not 1<=jobs<=6:raise ValueError('jobs must be1..6')
 out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
 for stale in ['receipt.json','finalize.json']:(out/stale).unlink(missing_ok=True)
 tree=freeze(out,component);info=json.loads((out/'snapshot.json').read_text());cfg=spec(component);start=time.perf_counter()
 names=stages or standard_stages(component)
 if stages and set(names)&{'backend','borrowers','defects',*cfg.get('extra_stages',[])}:
  required=['api-'+g for g in cfg['api']]
  if 'defects' in names:required += [n for n in ['backend','borrowers',*cfg.get('extra_stages',[])] if callable(getattr(importlib.import_module(cfg['legacy']),n,None))]
  names=list(dict.fromkeys(required+names))
 if 'deepcounts' in names and 'levels' not in names:names=['levels']+names
 pending=list(names);running={};results={};artifacts={};stage_seconds={}
 with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
  while pending or running:
   for name in list(pending):
    needs=[n for n in names if n.startswith('api-')] if name in ['backend','borrowers','defects',*cfg.get('extra_stages',[])] else []
    if name=='borrowers' and 'backend' in names:needs+=['backend']
    if name=='defects':needs += [n for n in ['router','backend','borrowers',*cfg.get('extra_stages',[])] if n in names]
    if name=='deepcounts':needs += ['levels']
    if len(running)>=jobs:break
    if not all(n in results for n in needs):continue
    folder=out/'stages'/name;baseline=folder/'baseline';folder.mkdir(parents=True,exist_ok=True);reset_generated(baseline,folder);shutil.copytree(tree,baseline,dirs_exist_ok=True)
    artifact=baseline/'build/world-stage';artifact.mkdir(parents=True,exist_ok=True);deps={n:str(artifacts[n]) for n in needs};args=folder/'request.json';save(args,dict(component=component,stage=name,out=str(artifact),revision=info['revision'],dependencies=deps))
    command=[sys.executable,baseline/'verif/world_gate.py','--child',args]
    running[executor.submit(run,command,baseline,out,name)]=(name,artifact);pending.remove(name)
   if not running:raise RuntimeError('stage dependency cycle')
   done,_=concurrent.futures.wait(running,return_when=concurrent.futures.FIRST_COMPLETED)
   for future in done:
    name,artifact=running.pop(future);r=future.result();stage_seconds[name]=r['seconds'];result=json.loads((artifact/'receipt.json').read_text());assert result.get('result')=='PASS',name;results[name]=canonical(result,artifact.parent.parent);artifacts[name]=artifact
 assert all(sha(ROOT/f)==h for f,h in info['inputs'].items()),'gate source changed during evidence; no resynchronization'
 primary=dict(result='PASS',component=component,stages={n:results[n] for n in names});save(out/'receipt.json',primary);save(out/'timings.json',dict(jobs=jobs,wall_seconds=time.perf_counter()-start,child_seconds=stage_seconds))
 for n in names:print('PASS '+n)
 return primary

def main(default_world=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('world',nargs='?',default=default_world);p.add_argument('--out',type=Path);p.add_argument('--jobs',type=int,default=3);p.add_argument('--stages',nargs='+');p.add_argument('--child',type=Path);p.add_argument('--gate',action='store_true');p.add_argument('--all',action='store_true');p.add_argument('--finalize',action='store_true');p.add_argument('--locks',action='store_true')
 args,old=p.parse_known_args()
 if args.child:
  r=json.loads(args.child.read_text());child(**r);return
 if not args.world:p.error('world component required')
 out=args.out or ROOT/'build/world-gates'/args.world
 stages=args.stages or [x[2:] for x in old if x.startswith('--') and x not in ['--internal']]
 if 'api' in stages:stages=[x for x in stages if x!='api']+['api-'+g for g in spec(args.world)['api']]
 if args.finalize:
  finalize(args.world,out)
  if args.locks:
   from contract_locks import refresh
   refresh(out,final=True)
  return
 if args.locks:
  from contract_locks import refresh
  refresh(out)
  if not(args.gate or args.all or stages):return
 gate(args.world,out,args.jobs,stages or None)
 if args.gate:
  finalize(args.world,out)
  from contract_locks import refresh
  refresh(out,final=True)


def legacy_stage(module_name,name,arguments):
 """Compatibility for imported historical adapters; all new work uses SPEC."""
 module=sys.modules[module_name];stem=module_name.rsplit('legacy_',1)[-1]
 matches=[r for r in world_registry.entries() if Path(r['gate']['cases']).stem==stem];assert len(matches)==1,module_name
 component=matches[0]['component']
 if name in ['locks','relock']:
  from contract_locks import refresh
  return refresh(getattr(module,'OUT',ROOT/'build/world-gates'/component),arguments.get('final',False))
 group=arguments.get('group');stage='api-'+(group or next(iter(spec(component)['api']))) if name=='api' else name
 if name=='finalize':return None # Generic finalization is after all stage receipts.
 return gate(component,getattr(module,'OUT',ROOT/'build/world-gates'/component),1,[stage])


def finalize(component,out):
 out=Path(out);receipt=json.loads((out/'receipt.json').read_text());assert receipt['result']=='PASS' and receipt['component']==component
 missing=set(standard_stages(component))-set(receipt['stages']);assert not missing,('cannot finalize partial evidence',sorted(missing))
 snap=json.loads((out/'snapshot.json').read_text());assert all(sha(ROOT/f)==h for f,h in snap['inputs'].items()),'finalize refuses changed source; no repair'
 save(out/'finalize.json',dict(result='PASS',component=component,receipt_sha256=sha(out/'receipt.json'),status=json.loads((ROOT/'metadata/closure'/(component+'.json')).read_text())['status'],scope='Evidence finalized without status/claim changes; explicit --locks refreshes source locks'))

if __name__=='__main__':main()
