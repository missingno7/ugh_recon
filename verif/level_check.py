"""Run the maintained level checker against an isolated host and provenance view."""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
from job_pool import run,save

def check(group,variant,host,out):
 import level_suite as ls,wholegame,cgen
 from types import SimpleNamespace
 ls.set_group(group);source=ls.SUITE;cache=ls.CACHE;out=Path(out);out.mkdir(parents=True,exist_ok=True)
 view=out/'provenance';suffix={'openings':'','audio':'-audio','deep':'-deep'}[group];suite=view/('tests/levels'+suffix);suite.mkdir(parents=True,exist_ok=True)
 references=[json.loads(p.read_text()) for p in sorted(cache.glob('*.ref.json'))];inputs={}
 for relative in ['tools/emu.py','tools/wholegame.py']:
  normal=(ROOT/relative).read_bytes().replace(b'\r\n',b'\n');wanted={r['provenance']['tools'][relative] for r in references};assert len(wanted)==1
  candidates=[b for b in [normal,normal.replace(b'\n',b'\r\n')] if hashlib.sha256(b).hexdigest() in wanted];assert len(candidates)==1,(relative,'changed reference tool')
  p=view/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(candidates[0]);inputs[relative]=hashlib.sha256(candidates[0]).hexdigest()
 mz,_=cgen.read_symbols();wholegame.ROOT=view
 for p in sorted(source.iterdir()):
  if p.suffix!='.txt':shutil.copyfile(p,suite/p.name);continue
  ref=json.loads((cache/(p.stem+'.ref.json')).read_text());normal=p.read_bytes().replace(b'\r\n',b'\n');matches=[];q=suite/p.name
  for b in set([normal,normal.replace(b'\n',b'\r\n')]):
   q.write_bytes(b)
   if wholegame.identity(q,SimpleNamespace(raw_image=mz.image))==ref['key']:matches.append(b)
  assert len(matches)==1,(p.name,'changed reference script');q.write_bytes(matches[0]);inputs[p.relative_to(ROOT).as_posix()]=hashlib.sha256(matches[0]).hexdigest()
 class Redirect(type(ROOT)):
  def __truediv__(self,value):
   if str(value)=='build/host/ugh.exe':return Path(host)/'ugh.exe'
   if str(value)=='build/host/hostbuild.json':return Path(host)/'hostbuild.json'
   return super().__truediv__(value)
 ls.ROOT=Redirect(ROOT);ls.SUITE=suite;ls.OUT=out
 ls.bounded=lambda command,tag,ok=(0,),**kw:run(command,ROOT,out,tag,allowed=ok)
 names=[p.stem for p in sorted(suite.glob('*.txt'))];assert len(names)=={'openings':81,'audio':7,'deep':8}[group]
 assert ls.check(variant,names)
 raw=json.loads((out/('check-'+variant+'-'+names[0]+'.json')).read_text())
 result=dict(result='PASS',group=group,variant=variant,inputs=inputs,scenarios=[{k:v for k,v in r.items() if k not in ['seconds','executable_sha256']} for r in raw['scenarios']])
 save(out/'receipt.json',result);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--group',choices=['openings','audio','deep'],required=True);p.add_argument('--variant',choices=['native','literal'],default='native');p.add_argument('--host',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();check(a.group,a.variant,a.host,a.out)
