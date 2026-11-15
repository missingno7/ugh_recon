"""Process-refactor controls and all-world replay using isolated bounded stages."""
import argparse,ast,concurrent.futures,hashlib,importlib,json,os,shutil,sys,time,threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
from job_pool import run,save
import world_gate,world_registry

def compiled_inputs(root):
 root=Path(root);files=[]
 for folder in ['c','native']:
  files += [p for p in (root/folder).rglob('*') if p.suffix in ['.c','.h']]
 for folder in ['metadata/worlds']:
  files += list((root/folder).glob('*.json'))
 files += [root/p for p in ['tools/hostbuild.py','tools/world_registry.py','verif/world_api.py']]
 files += list((root/'verif').glob('*_platform*.inc'))
 result={p.relative_to(root).as_posix():world_gate.sha(p) for p in files}
 result['selected contracts']=[(p.name,c.get('status'),c.get('component'),c.get('native',{}).get('files')) for p in sorted((root/'metadata/closure').glob('*.json')) for c in [json.loads(p.read_text())]]
 return result

def shared_api(component,shared,out,fixtures_only=False):
 """Same compiled sources/flags for all worlds; only case inputs differ.

 Reuse is checked against source fingerprints, never against output equality.
 The independent L1 and Unicorn comparisons still run for every admitted case.
 """
 import world_api
 out=Path(out);shared=Path(shared);cfg,module,bounded=world_gate.load_cases(component,out);results={}
 if cfg.get('worlds_enabled'):shared=shared/'variants'/component
 prior=world_api.build
 origin=Path(json.loads((shared/'diagnostics/api-composed-compile.json').read_text())['cwd'])
 assert compiled_inputs(origin)==compiled_inputs(ROOT),'shared API build inputs differ; rebuild rather than reuse'
 def compiled(profile,folder,worlds_enabled=None):
  p=shared/profile/'api.dll';assert p.is_file()
  command=json.loads((shared/'diagnostics'/('api-'+profile+'-compile.json')).read_text())
  for source in command['command']:
   if source.endswith('.c'):assert Path(source).is_file(),source
  shutil.copytree(shared/profile,Path(folder)/profile,dirs_exist_ok=True)
  save(Path(folder)/'diagnostics'/('api-'+profile+'-compile.json'),command)
  return Path(folder)/profile/'api.dll'
 world_api.build=compiled
 try:
  for group in cfg['api']:
   if fixtures_only:
    for profile in ['reference','legacy','composed']:compiled(profile,out/group/'api',cfg.get('worlds_enabled'))
    results[group]=str(out/group);save(out/group/'receipt.json',dict(result='PASS',scope='Compiled fixture dependency; API cases are a separate stage'));continue
   cases=world_gate.api_cases(cfg,module,group)
   if cases:result=world_api.replay(group,cases,out/group/'api',cfg['api'][group].get('allowed_rejections',[]),cfg.get('worlds_enabled'))
   else:result=dict(result='PASS',composed_matching=0,legacy_matching=0,explicit_out_of_domain=[],compatibility_cases=[])
   save(out/group/'receipt.json',result);results[group]=str(out/group)
 finally:world_api.build=prior
 save(out/'receipt.json',dict(result='PASS',component=component,groups=results));return results

def world_checks(component,out,shared,revision):
 out=Path(out);cfg,module,bounded=world_gate.load_cases(component,out);apis=shared_api(component,shared,out/'apis');dependencies={'api-'+g:p for g,p in apis.items()}
 world_gate.aliases(out,dependencies);results={}
 # These are the actual case-specific C/CBMC programs, not mirror tests.
 names=[n for n in ['router','proof','backend','borrowers',*cfg.get('extra_stages',[]),'defects'] if callable(getattr(module,n,None))]
 for name in names:
  world_gate.child(component,name,out,revision,dependencies);p=out/(name+'.json')
  if p.exists():results[name]=json.loads(p.read_text())
  if name in ['backend','borrowers']:
   # Same stage directory is private to this world. Mutant recipes consume the
   # compiled borrower/backend commands without racing another world.
   pass
 save(out/'all-world.json',dict(result='PASS',component=component,stages=list(results),defects=results.get('defects')))

def all_worlds(out,shared,jobs=3,defects_only=False,worlds=None):
 out=Path(out).resolve();shared=Path(shared).resolve();base=world_gate.freeze(out);snapshot=json.loads((out/'snapshot.json').read_text());start=time.perf_counter();results={};stop=threading.Event()
 def one(row):
  if stop.is_set():return None
  component=row['component'];target=out/'worlds'/component;tree=target/'baseline';shutil.copytree(base,tree,dirs_exist_ok=True);artifact=tree/'build/world-check'
  api_request=target/'api.json';save(api_request,dict(component=component,shared=str(Path(shared).resolve()),out=str(artifact/'apis'),fixtures_only=defects_only))
  run([sys.executable,tree/'verif/process_refactor.py','--api-child',api_request],tree,target,'apis')
  api_info=json.loads((artifact/'apis/receipt.json').read_text());dependencies={'api-'+g:p for g,p in api_info['groups'].items()}
  cfg=world_gate.spec(component);source=tree/('verif/'+cfg['legacy'].replace('.','/')+'.py')
  # module path is already under verif; select explicit case functions only.
  if not source.exists():source=tree/(cfg['legacy'].replace('.','/')+'.py')
  definitions={n.name for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef)}
  stages=[n for n in ['router','proof','backend','borrowers',*cfg.get('extra_stages',[]),'defects'] if n in definitions]
  if defects_only:stages=[n for n in stages if n in ['router','backend','borrowers','defects']]
  rows={}
  for name in stages:
   if stop.is_set():return None
   request=target/(name+'.json');save(request,dict(component=component,stage=name,out=str(artifact),revision=snapshot['revision'],dependencies=dependencies))
   run([sys.executable,tree/'verif/world_gate.py','--child',request],tree,target,name)
   rows[name]=json.loads((artifact/'receipt.json').read_text())
  result=dict(result='PASS',component=component,stages=stages,defects=rows.get('defects'));save(target/'receipt.json',result);return result
 with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
  tasks={executor.submit(one,row):row['component'] for row in world_registry.entries() if not worlds or row['component'] in worlds}
  try:
   for future in concurrent.futures.as_completed(tasks):results[tasks[future]]=future.result()
  except BaseException:
   stop.set()
   for future in tasks:future.cancel()
   raise
 assert all(world_gate.sha(ROOT/p)==h for p,h in snapshot['inputs'].items()),'all-world input changed'
 save(out/'receipt.json',dict(result='PASS',worlds={k:world_gate.canonical(results[k],out) for k in sorted(results)}));save(out/'timings.json',dict(jobs=jobs,wall_seconds=time.perf_counter()-start))

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--all',action='store_true');p.add_argument('--defects-only',action='store_true');p.add_argument('--worlds',nargs='+');p.add_argument('--world-child',type=Path);p.add_argument('--api-child',type=Path);p.add_argument('--shared-api',type=Path);p.add_argument('--jobs',type=int,default=3);p.add_argument('--out',type=Path,default=ROOT/'build/workers/close-adlx-29/all-worlds');a=p.parse_args()
 if a.api_child:
  r=json.loads(a.api_child.read_text());shared_api(**r);return
 if a.world_child:
  r=json.loads(a.world_child.read_text());world_checks(**r);return
 if a.all:
  assert a.shared_api,'--shared-api is an immutable generic API artifact directory';all_worlds(a.out,a.shared_api,a.jobs,a.defects_only,a.worlds)
if __name__=='__main__':main()
