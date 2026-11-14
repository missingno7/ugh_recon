"""Rebuild pictures evidence from a clean committed baseline plus owned files."""
import argparse,os,shutil,subprocess,sys,tarfile,time
from pathlib import Path
from closure_support import ROOT,receipt,save
from pictures_host import BASELINE,OUT,own_files

PROFILES=['palette-prefix','palette-step','input','show','startup']

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--clean',action='store_true');p.add_argument('--fresh',action='store_true');p.add_argument('--working-tree-host',action='store_true');a=p.parse_args();start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
 if a.clean:
  folder=OUT/f'clean-replay-{os.getpid()}';folder.mkdir();archive=OUT/f'clean-baseline-{os.getpid()}.tar';subprocess.run(['git','archive','--format=tar','--output',str(archive),BASELINE],cwd=ROOT,check=True)
  with tarfile.open(archive) as tree:
   assert all((folder/x.name).resolve().is_relative_to(folder.resolve()) and not x.issym() and not x.islnk() for x in tree.getmembers());tree.extractall(folder,filter='data')
  for source in own_files():
   target=folder/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
  cached=folder/'build/whole';cached.mkdir(parents=True)
  # Normally keyed L0 references only: never DLLs, proof outputs or host results.
  reference_cache=ROOT/'build/workers/close-adlx-13/clean-replay-11060/build/workers/close-adlx-13/whole'
  if len(list(reference_cache.glob('*.ref.json')))!=20:reference_cache=OUT/'whole'
  for source in reference_cache.glob('*.ref.json'):shutil.copyfile(source,cached/source.name)
  amiga=ROOT/'build/amiga/files/t'
  if amiga.exists():
   target=folder/'build/amiga/files/t';target.parent.mkdir(parents=True);shutil.copyfile(amiga,target)
  command=[sys.executable,'verif/pictures_reproduce.py','--fresh','--working-tree-host'];result=subprocess.run(command,cwd=folder)
  save(OUT/'clean-replay.json',receipt(command,[Path(__file__),*own_files()],result='PASS' if not result.returncode else 'FAIL',baseline=BASELINE,scratch=str(folder.relative_to(ROOT)),prebuilt_libraries=False,reference_note='Only normally keyed L0 caches plus optional hash-pinned Amiga meaning input. Plain image, every DLL and solver harness freshly rebuilt.',seconds=time.perf_counter()-start));return result.returncode
 if a.fresh:
  import contacts_reference
  contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True,fresh=True)
 commands=[['verif/pictures_inventory.py'],['verif/pictures_enumerate.py'],['verif/pictures_enumerate.py','--negative'],*[['verif/pictures_proofs.py',n] for n in PROFILES],*[['verif/pictures_proofs.py',n,'--negative'] for n in PROFILES],['verif/pictures_evidence.py'],['verif/pictures_integration.py','--whole'],['verif/pictures_certificate.py'],['verif/pictures_host.py',*(['--working-tree'] if a.working_tree_host else [])],['tools/closure.py']]
 rows=[]
 for command in commands:
  print('RUN',' '.join(command),flush=True);run=subprocess.run([sys.executable,*command],cwd=ROOT);rows.append(dict(command=command,returncode=run.returncode))
  if run.returncode:break
 save(OUT/'reproduce.json',receipt([sys.executable,'verif/pictures_reproduce.py',*sys.argv[1:]],[Path(__file__),*own_files()],result='PASS' if not any(r['returncode'] for r in rows) else 'FAIL',commands=rows,seconds=time.perf_counter()-start));return int(any(r['returncode'] for r in rows))
if __name__=='__main__':raise SystemExit(main())
