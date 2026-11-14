"""Input evidence replay; clean archive uses the task's committed starting baseline."""
import argparse,subprocess,sys,shutil,tarfile,os,time,json
from pathlib import Path
from closure_support import ROOT,receipt,save
from input_build import OUT
BASELINE='2dff5890152e2bc7213fc4657b784d18c9cb5610'

def own_files():
 return [ROOT/'native/input.c',ROOT/'native/input.h',ROOT/'native/bridge/input_bridge.c',ROOT/'metadata/closure/input.json',*[p for p in (ROOT/'verif').glob('input*') if p.is_file()]]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--clean',action='store_true');p.add_argument('--fresh',action='store_true');p.add_argument('--working-tree-host',action='store_true');a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
 if a.clean:
  folder=OUT/f'clean-replay-{os.getpid()}';folder.mkdir();archive=OUT/f'clean-baseline-{os.getpid()}.tar';subprocess.run(['git','archive','--format=tar','--output',str(archive),BASELINE],cwd=ROOT,check=True)
  with tarfile.open(archive) as tree:
   assert all((folder/x.name).resolve().is_relative_to(folder.resolve()) and not x.issym() and not x.islnk() for x in tree.getmembers());tree.extractall(folder,filter='data')
  for source in own_files():
   target=folder/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
  cached=folder/'build/whole';cached.mkdir(parents=True)
  reference_cache=ROOT/'build/whole'
  # Prior owned clean L0 references are safe to reuse only through the normal
  # harness key check. Native DLLs/receipts are never imported.
  for prior in sorted(OUT.glob('clean-replay-*'),key=lambda q:q.stat().st_mtime,reverse=True):
   candidate=prior/'build/workers/close-adlx-11/whole'
   if len(list(candidate.glob('*.ref.json')))==20:reference_cache=candidate;break
  for source in reference_cache.glob('*.ref.json'):shutil.copyfile(source,cached/source.name)
  # Meaning-only evidence uses the pinned extracted Amiga file when available.
  amiga=ROOT/'build/amiga/files/t'
  if amiga.exists():
   target=folder/'build/amiga/files/t';target.parent.mkdir(parents=True);shutil.copyfile(amiga,target)
  command=[sys.executable,'verif/input_reproduce.py','--fresh','--working-tree-host'];result=subprocess.run(command,cwd=folder)
  save(OUT/'clean-replay.json',receipt(command,[Path(__file__),*own_files()],result='PASS' if not result.returncode else 'FAIL',baseline=BASELINE,scratch=str(folder.relative_to(ROOT)),prebuilt_libraries=False,reference_note='Only normally locked L0 scenario caches and optional hash-checked Amiga meaning input copied. Plain rebuilt fresh; all native/reference DLLs and solver harnesses rebuilt.',seconds=time.perf_counter()-start));return result.returncode
 if a.fresh:
  import contacts_reference
  contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True,fresh=True)
 scalars=['threshold','direction','maximum','timer','sample-gate','reset','source','mapping-domain','mapping','players']
 commands=[['verif/input_inventory.py'],['verif/input_enumerate.py'],['verif/input_evidence.py'],*[['verif/input_proofs.py',entry] for entry in scalars],*[['verif/input_keyboard_step.py',mode] for mode in ['outputs','frame','dependence']],*[['verif/input_proofs.py',entry,'--negative'] for entry in ['threshold','direction','timer']],['verif/input_keyboard_step.py','outputs','--negative'],['verif/input_integration.py','--whole'],['verif/input_witness.py'],['verif/input_certificate.py'],['verif/input_host.py',*(['--working-tree'] if a.working_tree_host else ['--baseline',BASELINE])],['tools/closure.py']]
 rows=[]
 for command in commands:
  print('RUN',' '.join(command),flush=True);run=subprocess.run([sys.executable,*command],cwd=ROOT);rows.append(dict(command=command,returncode=run.returncode))
  if run.returncode:break
 save(OUT/'reproduce.json',receipt([sys.executable,'verif/input_reproduce.py',*sys.argv[1:]],[Path(__file__),*own_files()],result='PASS' if not any(r['returncode'] for r in rows) else 'FAIL',commands=rows,seconds=time.perf_counter()-start));return int(any(r['returncode'] for r in rows))
if __name__=='__main__':raise SystemExit(main())
