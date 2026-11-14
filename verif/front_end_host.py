"""Actual promoted host gates, excluding every uncommitted foreign file."""
import argparse,json,os,shutil,subprocess,sys,tarfile
from pathlib import Path
from closure_support import ROOT,save,receipt
OUT=ROOT/'build/workers/close-adlx-13'
BASELINE='6bfb2063a9b6c4704138273ad4ced01b30344fed'

def own_files(all_units=False):
 names=['front_end.h','high_scores.c','high_scores.h','bridge/front_end_support.h','bridge/high_scores_bridge.c']
 if all_units:names+=['menus.c','menus.h','bridge/menus_bridge.c']
 return [*[ROOT/'native'/n for n in names],ROOT/'metadata/closure/high_scores.json',*([ROOT/'metadata/closure/menus.json'] if all_units else []),*[p for p in (ROOT/'verif').glob('*') if p.is_file() and (p.name.startswith(('front_end_','high_scores_')) or (all_units and p.name.startswith('menus_')))]]

def main():
 p=argparse.ArgumentParser();p.add_argument('--all',action='store_true');p.add_argument('--working-tree',action='store_true');a=p.parse_args();scratch=OUT/f'host-{os.getpid()}';scratch.mkdir(parents=True,exist_ok=True)
 import contacts_reference
 contacts_reference.OUT=OUT/'reference';plain=contacts_reference.prepare_reference(local=True)
 if a.working_tree:
  for name in ['c','src','native','tools','metadata','host','tests','verif','docs']:shutil.copytree(ROOT/name,scratch/name,ignore=shutil.ignore_patterns('__pycache__'),dirs_exist_ok=True)
 else:
  archive=OUT/f'host-{os.getpid()}.tar';subprocess.run(['git','archive','--format=tar','--output',str(archive),BASELINE],cwd=ROOT,check=True)
  with tarfile.open(archive) as tree:
   assert all((scratch/m.name).resolve().is_relative_to(scratch.resolve()) and not m.issym() and not m.islnk() for m in tree.getmembers());tree.extractall(scratch,filter='data')
  for n in json.loads((plain.parent/'build.json').read_text())['source_sha256']:
   source=ROOT/n;target=scratch/n;assert source.read_bytes().replace(b'\r\n',b'\n')==target.read_bytes().replace(b'\r\n',b'\n');shutil.copyfile(source,target)
  for source in own_files(a.all):
   target=scratch/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
 shutil.copytree(plain.parent,scratch/'build/link/plain',dirs_exist_ok=True)
 for name in ['high_scores',*(['menus'] if a.all else [])]:
  path=scratch/f'metadata/closure/{name}.json';cert=json.loads(path.read_text());cert['status']='migrated';path.write_text(json.dumps(cert,indent=2)+'\n')
 cache=scratch/'build/whole';cache.mkdir(parents=True,exist_ok=True)
 for path in (OUT/'whole').glob('*.ref.json'):shutil.copyfile(path,cache/path.name)
 commands=[['python','tools/hostbuild.py'],['python','host/check.py','--variant','native'],['python','host/check.py','--variant','literal'],['python','tools/closure.py']]
 for i,command in enumerate(commands):
  result=subprocess.run(command,cwd=scratch,capture_output=True,text=True);(scratch/f'gate-{i}.log').write_text(result.stdout+result.stderr);print(result.stdout+result.stderr,flush=True);assert not result.returncode
 built=json.loads((scratch/'build/host/hostbuild.json').read_text());assert 'high_scores' in [u['component'] for u in built['linked_units']]
 if a.all:assert 'menus' in [u['component'] for u in built['linked_units']]
 save(OUT/('host-all.json' if a.all else 'host-high.json'),receipt(commands[0],[Path(__file__),*[p for p in own_files(a.all) if p.suffix in ('.c','.h','.json')]],result='PASS',baseline=BASELINE,scratch=str(scratch.relative_to(ROOT)),commands=commands,build=built,native=json.loads((scratch/'build/workers/host-native/host-check-native.json').read_text()),literal=json.loads((scratch/'build/workers/host-native/host-check-literal.json').read_text())))
if __name__=='__main__':main()
