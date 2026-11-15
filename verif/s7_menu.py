"""Production menu frame proof against independent whole-game records."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'verif')]
import nativebuild,s7_audio,s7_menu_record
from job_pool import run,save

def verify(out,build=True):
 out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True);prod=out/'production'
 if build:nativebuild.build('test',prod)
 cases=out/'cases';cases.mkdir(exist_ok=True);exe=s7_audio.executable(ROOT/'verif/s7_menu_cases.c',cases,prod)
 print(run([exe,prod/'ugh.res'],ROOT,cases,'run')['stdout'].strip(),flush=True)
 results={}
 for name in ['menu','startup','adlib','gameplay-adlib']:
  folder=out/name;folder.mkdir(exist_ok=True);source=s7_menu_record.generate(folder,name);exe=s7_audio.executable(source,folder,prod)
  row=run([exe,prod/'ugh.res',folder/'baseline.bin',folder],ROOT,folder,'record')
  got=[json.loads(x) for x in row['stdout'].splitlines()]
  want=json.loads((ROOT/'build/whole'/f'{name}.ref.json').read_text())['frames']
  total=len(want)
  if name=='gameplay-adlib':
   assert len(got)==9 and 'slice kind=0 status=0 action=20 frames=9' in row['stderr'],row['stderr']
   want=want[:9]
  diff=[dict(frame=i,field=k,actual=a.get(k),expected=b.get(k)) for i,(a,b) in enumerate(zip(got,want)) for k in set(a)|set(b) if a.get(k)!=b.get(k)]
  if len(got)!=len(want):diff.append(dict(field='count',actual=len(got),expected=len(want)))
  save(folder/'actual.json',got);save(folder/'differences.json',diff);results[name]=dict(records=len(got),differences=diff,unreachable=None if name!='gameplay-adlib' else dict(first_record=9,remaining=total-9,boundary='GAME_MENU_SESSION_ENTRY before session resource/level selection'))
  if name in ['menu','adlib']:
   defect='missed-players' if name=='menu' else 'missed-exit';define='S7_MENU_MISS_PLAYERS' if name=='menu' else 'S7_MENU_MISS_EXIT'
   badfolder=folder/defect;badfolder.mkdir(exist_ok=True);badsource=badfolder/'record.c';badsource.write_text('#define '+define+'\n'+source.read_text())
   badexe=s7_audio.executable(badsource,badfolder,prod);badrow=run([badexe,prod/'ugh.res',folder/'baseline.bin',badfolder],ROOT,badfolder,'record')
   bad=[json.loads(x) for x in badrow['stdout'].splitlines()]
   caught=[i for i,(a,b) in enumerate(zip(bad,want)) if a!=b];assert caught,defect+' escaped comparator'
   results[name]['control']=dict(defect=defect,detected_frames=caught)
  print(name,len(got),[(d.get('frame'),d['field']) for d in diff][:20],flush=True)
 save(out/'receipt.json',dict(result='FAIL' if any(r['differences'] for r in results.values()) else 'PASS',scenarios=results))
 return not any(r['differences'] for r in results.values())
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'build/workers/s7-menu');p.add_argument('--no-build',action='store_true');a=p.parse_args();raise SystemExit(0 if verify(a.out,not a.no_build) else 1)
