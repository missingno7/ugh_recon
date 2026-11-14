"""Bridged input L0 cases and maintained scenarios; per-entry and mode counts."""
import sys,ctypes as C,shutil,json
from pathlib import Path
from closure_support import ROOT,receipt,save
from input_build import OUT,build,NAMES
sys.path.insert(0,str(ROOT/'tools'))
import contacts_reference,difftest,nbuild
contacts_reference.OUT=OUT/'reference'

def main():
 plain=contacts_reference.prepare_reference(local=True);path=build();dll=nbuild.load_l1(path);m=difftest.Machine();rows=[]
 for suite in ['dos_input','scene','video','game_services']:
  try:cases=difftest.load_suite(suite).CASES
  except FileNotFoundError:continue
  selected=[c for c in cases if c.routine in ['GAME:'+n for n in NAMES]]
  for poison in [False,True]:
   for case in selected:
    issues=difftest.run(case,m,dll,poison);rows.append(dict(suite=suite,name=case.title,routine=case.routine,poison=poison,issues=issues))
    if issues:print(rows[-1],flush=True)
  print(suite,sum(not r['issues'] for r in rows if r['suite']==suite),'/',sum(r['suite']==suite for r in rows),flush=True)
 if any(r['issues'] for r in rows):save(OUT/'integration-cases.json',rows);return 1
 observed=[];status=0
 if '--whole' in sys.argv:
  import wholegame
  folder=OUT/'whole';folder.mkdir(exist_ok=True)
  for p in (ROOT/'build/whole').glob('*.ref.json'):
   if not (folder/p.name).exists():shutil.copyfile(p,folder/p.name)
  wholegame.OUT=folder;ledger=OUT/'prior-edges.json';ledger.write_text('[]\n')
  class ReadRoot(type(ROOT)):
   def __truediv__(self,value):
    if str(value)=='build/workers/c-close/call-edges.json':return ledger
    if str(value)=='build/link/plain/UGH.EXE':return plain
    return super().__truediv__(value)
  wholegame.ROOT=ReadRoot(ROOT);wholegame.load_dll=lambda out=None,trace_dir=None:nbuild.load_l1(path)
  original=wholegame.native
  def native(*args,**kwargs):
   counters=(C.c_uint32*16).in_dll(dll,'input_audit');before=list(counters);result=original(*args,**kwargs);observed.append(dict(scenario=args[0]['name'],counts=[counters[i]-before[i] for i in range(16)]));return result
  wholegame.native=native;previous=sys.argv;sys.argv=['tools/wholegame.py']
  try:status=wholegame.main()
  finally:sys.argv=previous
 save(OUT/'integration.json',receipt([sys.executable,'verif/input_integration.py',*sys.argv[1:]],[Path(__file__),ROOT/'verif/input_build.py',ROOT/'native/input.c',ROOT/'native/input.h',ROOT/'native/bridge/input_bridge.c',plain,ROOT/'tools/wholegame.py'],result='PASS' if not status else 'FAIL',cases=rows,scenarios=observed));print('Counts',observed,flush=True);return status
if __name__=='__main__':raise SystemExit(main())
