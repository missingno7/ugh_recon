"""Rebuild front-end evidence from a clean committed baseline plus owned files."""
import argparse,os,shutil,subprocess,sys,tarfile,time
from pathlib import Path
from closure_support import ROOT,receipt,save
from front_end_host import BASELINE,OUT,own_files

HIGH=['row','qualification','format','complement','copy','insertion','file','editor']
MENU=['text','centering','copy-index','copy-step','control','mutators','selector','attract','editor','header']

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--clean',action='store_true');p.add_argument('--fresh',action='store_true');p.add_argument('--working-tree-host',action='store_true');a=p.parse_args();start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
 if a.clean:
  folder=OUT/f'clean-replay-{os.getpid()}';folder.mkdir();archive=OUT/f'clean-baseline-{os.getpid()}.tar';subprocess.run(['git','archive','--format=tar','--output',str(archive),BASELINE],cwd=ROOT,check=True)
  with tarfile.open(archive) as tree:
   assert all((folder/x.name).resolve().is_relative_to(folder.resolve()) and not x.issym() and not x.islnk() for x in tree.getmembers());tree.extractall(folder,filter='data')
  for source in own_files(True):
   target=folder/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
  cached=folder/'build/whole';cached.mkdir(parents=True)
  # Normally keyed L0 references only: never DLLs, proof outputs or host results.
  reference_cache=ROOT/'build/workers/close-adlx-12/clean-replay-11672/build/workers/close-adlx-12/whole'
  if len(list(reference_cache.glob('*.ref.json')))!=20:reference_cache=OUT/'whole'
  for source in reference_cache.glob('*.ref.json'):shutil.copyfile(source,cached/source.name)
  amiga=ROOT/'build/amiga/files/t'
  if amiga.exists():
   target=folder/'build/amiga/files/t';target.parent.mkdir(parents=True);shutil.copyfile(amiga,target)
  command=[sys.executable,'verif/front_end_reproduce.py','--fresh','--working-tree-host'];result=subprocess.run(command,cwd=folder)
  save(OUT/'clean-replay.json',receipt(command,[Path(__file__),*own_files(True)],result='PASS' if not result.returncode else 'FAIL',baseline=BASELINE,scratch=str(folder.relative_to(ROOT)),prebuilt_libraries=False,reference_note='Only normally keyed L0 caches plus optional hash-pinned Amiga meaning input. Plain image, every DLL and solver harness freshly rebuilt.',seconds=time.perf_counter()-start));return result.returncode
 if a.fresh:
  import contacts_reference
  contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True,fresh=True)
 commands=[['verif/front_end_inventory.py'],['verif/high_scores_enumerate.py'],*[['verif/high_scores_proofs.py',n] for n in HIGH],*[['verif/high_scores_proofs.py',n,'--negative'] for n in ['qualification','format','copy','file','editor']],['verif/high_scores_enumerate.py','--negative'],['verif/high_scores_evidence.py'],['verif/high_scores_integration.py','--whole'],['verif/high_scores_certificate.py'],['verif/menus_enumerate.py'],['verif/menus_passwords.py'],*[['verif/menus_proofs.py',n] for n in MENU],*[['verif/menus_proofs.py',n,'--negative'] for n in MENU],['verif/menus_enumerate.py','--negative'],['verif/menus_passwords.py','--negative'],['verif/menus_evidence.py'],['verif/menus_integration.py','--whole'],['verif/menus_certificate.py'],['verif/front_end_host.py','--all',*(['--working-tree'] if a.working_tree_host else [])],['tools/closure.py']]
 rows=[]
 for command in commands:
  print('RUN',' '.join(command),flush=True);run=subprocess.run([sys.executable,*command],cwd=ROOT);rows.append(dict(command=command,returncode=run.returncode))
  if run.returncode:break
 save(OUT/'reproduce.json',receipt([sys.executable,'verif/front_end_reproduce.py',*sys.argv[1:]],[Path(__file__),*own_files(True)],result='PASS' if not any(r['returncode'] for r in rows) else 'FAIL',commands=rows,seconds=time.perf_counter()-start));return int(any(r['returncode'] for r in rows))
if __name__=='__main__':raise SystemExit(main())
