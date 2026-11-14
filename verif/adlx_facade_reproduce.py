"""Reproduce both final audio units, in order; optional clean baseline archive."""
import argparse,subprocess,sys,json,shutil,tarfile,os,time
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_facade_build import OUT
BASELINE='bba2c2ba528d7fe512885b091cb7f9da85706608'

def own_files():
 return [ROOT/'native'/f'adlx_{n}.{ext}' for n in ['facade','digital'] for ext in ['c','h']]+[ROOT/'native/bridge'/f'adlx_{n}_bridge.c' for n in ['facade','digital']]+[ROOT/'metadata/closure'/f'adlx_{n}.json' for n in ['facade','digital']]+[p for n in ['facade','digital'] for p in (ROOT/'verif').glob(f'adlx_{n}*') if p.is_file()]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--clean',action='store_true');p.add_argument('--fresh',action='store_true');p.add_argument('--working-tree-host',action='store_true');a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
 if a.clean:
  folder=OUT/f'clean-replay-{os.getpid()}';folder.mkdir();archive=OUT/f'clean-baseline-{os.getpid()}.tar';subprocess.run(['git','archive','--format=tar','--output',str(archive),BASELINE],cwd=ROOT,check=True)
  with tarfile.open(archive) as tree:
   assert all((folder/x.name).resolve().is_relative_to(folder.resolve()) and not x.issym() and not x.islnk() for x in tree.getmembers());tree.extractall(folder,filter='data')
  for source in own_files():
   target=folder/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
  cached=folder/'build/whole';cached.mkdir(parents=True)
  for source in (ROOT/'build/whole').glob('*.ref.json'):shutil.copyfile(source,cached/source.name)
  command=[sys.executable,'verif/adlx_facade_reproduce.py','--fresh','--working-tree-host'];run=subprocess.run(command,cwd=folder)
  save(OUT/'clean-replay.json',receipt(command,[Path(__file__),*own_files()],result='PASS' if not run.returncode else 'FAIL',baseline=BASELINE,scratch=str(folder.relative_to(ROOT)),prebuilt_libraries=False,reference_note='Only maintained L0 scenario caches copied; their normal harness locks remain enabled. Plain rebuilt fresh from archived maintained sources.',seconds=time.perf_counter()-start));return run.returncode
 if a.fresh:
  import contacts_reference
  contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True,fresh=True)
 commands=[['verif/adlx_facade_evidence.py'],*[['verif/adlx_facade_proofs.py',mode] for mode in ['outputs','frame','dependence']],['verif/adlx_facade_proofs.py','outputs','--negative'],['verif/adlx_facade_integration.py','--whole','--local-reference'],['verif/adlx_facade_inventory.py'],['verif/adlx_facade_certificate.py'],['verif/adlx_facade_host.py',*(['--working-tree'] if a.working_tree_host else [])],['verif/adlx_digital_evidence.py'],*[['verif/adlx_digital_proofs.py',entry] for entry in ['block','poll','bank','locate']],['verif/adlx_digital_proofs.py','block','--negative'],['verif/adlx_digital_sb.py'],['verif/adlx_digital_integration.py','--whole','--local-reference'],['verif/adlx_digital_certificate.py'],['verif/adlx_digital_host.py',*(['--working-tree'] if a.working_tree_host else [])],['tools/closure.py']]
 rows=[]
 for command in commands:
  print('RUN',' '.join(command),flush=True);run=subprocess.run([sys.executable,*command],cwd=ROOT);rows.append(dict(command=command,returncode=run.returncode))
  if run.returncode:break
 save(OUT/'reproduce.json',receipt([sys.executable,'verif/adlx_facade_reproduce.py',*sys.argv[1:]],[Path(__file__),*own_files()],result='PASS' if not any(r['returncode'] for r in rows) else 'FAIL',commands=rows,seconds=time.perf_counter()-start));return int(any(r['returncode'] for r in rows))
if __name__=='__main__':raise SystemExit(main())
