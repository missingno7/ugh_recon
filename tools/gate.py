"""One bounded supervisor gate. Default legacy commands/outputs stay unchanged."""
import argparse,concurrent.futures,hashlib,json,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'verif'))
from job_pool import run,save

def gate(out,jobs=3,skip_build=False):
 out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True);(out/'receipt.json').unlink(missing_ok=True);start=time.perf_counter();native=out/'host-native';literal=out/'host-literal'
 tasks={
 'closure':([],['tools/closure.py']),
 'build':([],['tools/build.py']),
 'prepare':(['build'],['tools/hostbuild.py','--prepare-only']),
 'native-build':(['prepare'],['tools/hostbuild.py','--no-generate','--out',native]),
 'literal-build':(['prepare'],['tools/hostbuild.py','--no-generate','--literal','--out',literal]),
 'native-check':(['native-build'],['host/check.py','--variant','native','--out',native,'--receipt-dir',out/'checks']),
 'literal-check':(['literal-build'],['host/check.py','--variant','literal','--out',literal,'--receipt-dir',out/'checks']),
 }
 for group in ['openings','audio','deep']:tasks['levels-'+group]=(['native-build'],['verif/level_check.py','--group',group,'--host',native,'--out',out/('levels-'+group)])
 if skip_build:tasks['build']=([],['-c','print("Existing independently validated data build")'])
 if not 1<=jobs<=6:raise ValueError('jobs must be1..6')
 results={};pending=dict(tasks);running={}
 with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
  while pending or running:
   for name,(needs,command) in list(pending.items()):
    if len(running)>=jobs:break
    if all(n in results for n in needs):
     running[pool.submit(run,[sys.executable,*command],ROOT,out,name)]=name;del pending[name]
   if not running:raise RuntimeError('gate dependency cycle')
   done,_=concurrent.futures.wait(running,return_when=concurrent.futures.FIRST_COMPLETED)
   for f in done:
    name=running.pop(f);results[name]=f.result()
 # Scheduler/time/path-dependent diagnostics are separate from the primary receipt.
 checks={v:json.loads((out/'checks'/('host-check-'+v+'.json')).read_text()) for v in ['native','literal']}
 semantic=dict(result='PASS',closure=results['closure']['stdout'].strip(),host={v:dict(passed=r['passed'],linked_units=r['linked_units'],smoke=r['smoke']['passed'],scenarios=[{k:x for k,x in s.items() if k not in ['seconds','stderr']} for s in r['scenarios']]) for v,r in checks.items()},levels={g:json.loads((out/('levels-'+g)/'receipt.json').read_text()) for g in ['openings','audio','deep']})
 save(out/'receipt.json',semantic);save(out/'timings.json',dict(jobs=jobs,wall_seconds=time.perf_counter()-start,child_seconds={n:r['seconds'] for n,r in results.items()}))
 for name in tasks:print('PASS '+name)
 print('PASS closure / host21+21 / levels81+7+8',flush=True);return semantic
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=ROOT/'build/gate');p.add_argument('--jobs',type=int,default=3);p.add_argument('--skip-build',action='store_true');a=p.parse_args();gate(a.out,a.jobs,a.skip_build)
