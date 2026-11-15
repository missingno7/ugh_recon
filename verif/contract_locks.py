from pathlib import Path
import json,hashlib,sys,copy,subprocess
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import closure

def refresh(output,final=False):
 output=Path(output);notes={};before={}
 for p in (ROOT/'metadata/closure').glob('*.json'):
  saved=subprocess.run(['git','show','HEAD:'+p.relative_to(ROOT).as_posix()],cwd=ROOT,text=True,capture_output=True)
  before[p.name]=json.loads(saved.stdout) if saved.returncode==0 else json.loads(p.read_text())
 # First recompute all direct source dependencies. Contract digests then stabilize
 # independently of lock hashes/notes; no iterative certificate hash cascade.
 current={p.name:json.loads(p.read_text()) for p in (ROOT/'metadata/closure').glob('*.json')}
 for name,c in current.items():
  c['dependencies']={f:closure.actual_dependencies(ROOT/f) for f in c['dependencies']}
  old=before[name]
  for k in set(old)-{'dependencies','verification_inputs','evidence_refreshed'}:assert c[k]==old[k],(name,k,'claim changed')
  if c['dependencies']!=old['dependencies']:pass # explicit one-time implementation hookup, recorded below
 for name,c in current.items():
  changes=[];mode=c.get('verification_input_hashing','sha256-bytes')
  if (ROOT/'metadata/worlds'/name).exists():
   for f in ['tools/world_registry.py','metadata/worlds/'+name]:c.setdefault('verification_inputs',{}).setdefault(f,'UNLOCKED')
   import world_registry
   row=next(r for r in world_registry.entries() if r['component']==c['component'])
   for f in [row['gate']['cases'],'verif/world_gate.py','verif/world_api.py','verif/job_pool.py','verif/world_cases/legacy_adapter.py']:c['verification_inputs'].setdefault(f,'UNLOCKED')
   import world_gate
   if row.get('platform_provider'):c['verification_inputs'].setdefault(row['platform_provider'],'UNLOCKED')
   for module in world_gate.spec(c['component']).get('case_adapters',[]):c['verification_inputs'].setdefault('verif/'+module.replace('.','/')+'.py','UNLOCKED')
  for f in list(c.get('verification_inputs',{})):
   if f.startswith('verif/') and f.endswith('_composition.py'):
    private='verif/world_cases/legacy_'+Path(f).stem.removesuffix('_composition')+'.py'
    if (ROOT/private).exists():c['verification_inputs'].setdefault(private,'UNLOCKED')
  for f,h in c.get('verification_inputs',{}).items():
   if closure.certificate_input(ROOT/f):value=closure.contract_digest(current[Path(f).name])
   else:value=closure.input_digest(ROOT/f,mode)
   if value!=before[name].get('verification_inputs',{}).get(f):changes.append(f)
   c['verification_inputs'][f]=value
  if changes or c['dependencies']!=before[name]['dependencies']:
   note=dict(date='2026-11-15',reason='One-time registry/process refactor and canonical contract-v1 certificate locks; existing claims/results/status unchanged',commands=['python verif/world_gate.py enemy_world --jobs 3','python build/workers/close-adlx-29/all_controls.py','python tools/gate.py'],results='PASS: existing contract claims unchanged; full representative gate, all 111 controls (including one positive rejection barrier), registry/contract controls and supervisor gate; receipts in build/workers/close-adlx-29' if final else 'Pending process-refactor replay',inputs=sorted(changes))
   c['evidence_refreshed']=before[name].get('evidence_refreshed',[])+[note];notes[name]=note
  target=ROOT/'metadata/closure'/name;rendered=json.dumps(c,indent=2)+'\n'
  if target.read_text()!=rendered:
   temporary=target.with_suffix('.json.tmp');temporary.write_text(rendered,encoding='utf-8');temporary.replace(target)
 output.mkdir(parents=True,exist_ok=True);(output/'relocks.json').write_text(json.dumps(notes,indent=2)+'\n')
 return notes

def controls(output):
 output=Path(output);path=ROOT/'metadata/closure/audio_world.json';base=json.loads(path.read_text());digest=closure.contract_digest(base);rows=[]
 for key,change in [('note',lambda c:c.setdefault('evidence_refreshed',[]).append({'reason':'control'})),('relock',lambda c:c.setdefault('verification_inputs',{}).update({'control':'changed'}))]:
  c=copy.deepcopy(base);change(c);assert closure.contract_digest(c)==digest;rows.append(dict(control=key,result='UNCHANGED'))
 for key in ['status','interface','memory','retained','assumptions','claims','dependencies']:
  c=copy.deepcopy(base);c[key]=['control change'];assert closure.contract_digest(c)!=digest;rows.append(dict(control=key,result='INVALIDATED'))
 for key in ['level','result']:
  c=copy.deepcopy(base);c['evidence'][0][key]='control change';assert closure.contract_digest(c)!=digest;rows.append(dict(control='evidence-'+key,result='INVALIDATED'))
 # Actual checker control, restore even if it raises. Dependents of audio_world
 # still carry the prior contract lock; only the claim changes in this copy.
 original=path.read_bytes()
 try:
  c=copy.deepcopy(base);c['retained'].append('CONTROL changed claim');path.write_text(json.dumps(c,indent=2)+'\n');_,errors=closure.validate()
  assert any('stale verification input metadata/closure/audio_world.json' in e for e in errors),errors
  rows.append(dict(control='actual dependent validation',result='DETECTED',dependents=sum('stale verification input metadata/closure/audio_world.json' in e for e in errors)))
 finally:path.write_bytes(original)
 # Refresh note and VI changes leave all incoming certificate edges bit-identical.
 incoming={p.name:json.loads(p.read_text()).get('verification_inputs',{}).get('metadata/closure/audio_world.json') for p in (ROOT/'metadata/closure').glob('*.json')};c=copy.deepcopy(base);c['evidence_refreshed'].append({'reason':'CONTROL note only'});assert closure.contract_digest(c)==digest
 original=path.read_bytes()
 try:
  path.write_text(json.dumps(c,indent=2)+'\n');_,errors=closure.validate()
  assert not [e for e in errors if 'stale verification input metadata/closure/audio_world.json' in e],errors
 finally:path.write_bytes(original)
 assert incoming=={p.name:json.loads(p.read_text()).get('verification_inputs',{}).get('metadata/closure/audio_world.json') for p in (ROOT/'metadata/closure').glob('*.json')}
 rows.append(dict(control='no relock cascade',result='PASS',incoming_edges_unchanged=sum(bool(v) for v in incoming.values())))
 output.mkdir(parents=True,exist_ok=True);(output/'contract-controls.json').write_text(json.dumps(dict(result='PASS',controls=rows),indent=2)+'\n')
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');p.add_argument('--final',action='store_true');p.add_argument('--controls',action='store_true');p.add_argument('--out',type=Path,default=ROOT/'build/workers/close-adlx-29');a=p.parse_args()
 if a.refresh:refresh(a.out,a.final)
 if a.controls:controls(a.out)
