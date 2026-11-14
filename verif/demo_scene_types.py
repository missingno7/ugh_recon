"""Supervisor-approved B evidence transfer, freshly replayed in this worker."""
import hashlib,json,sys
from datetime import date
from pathlib import Path
from closure_support import ROOT,save
from demo_scene_build import OUT
from demo_scene_limits import cbmc,SMT
from render_history_shells import OPS
import render_history_proof as slot_proof
import render_history_sequences as sequence
import render_history_projection as projection

def main():
    folder=OUT/'actor-types';folder.mkdir(parents=True,exist_ok=True);rows=[]
    def solve(source,directory,inputs,**kwargs):
        return cbmc(source,directory,[*inputs,Path(__file__)],**kwargs)
    for op in OPS:
        for mode in ['outputs','native-frame','dependencies']:
            path=folder/(op+'-'+mode);path.mkdir(exist_ok=True);code,inputs=slot_proof.make(OPS.index(op),mode,path);source=path/'harness.c';source.write_text(code)
            result=solve(source,path,inputs,unwind=18,timeout=600,defines=['-D__CPROVER__','-DACTOR_VERIFY','-DUINT16_MAX=65535u'],extra=SMT)
            assert result['result']=='PASS';rows.append((f'{op} {mode}',f'python verif/render_history_proof.py {op} {mode}',path/'result.json'));print('PASS',op,mode,flush=True)
    for mode in ['pages','seeds','initialize-frame','loader-frame']:
        path=folder/mode;path.mkdir(exist_ok=True);code,inputs=sequence.make(mode,path);source=path/'harness.c';source.write_text(code)
        result=solve(source,path,inputs,unwind=18,timeout=600,defines=['-D__CPROVER__','-DACTOR_VERIFY','-DUINT16_MAX=65535u'],extra=SMT)
        assert result['result']=='PASS';rows.append((mode,'python verif/render_history_sequences.py '+mode,path/'result.json'));print('PASS',mode,flush=True)
    projection.OUT=folder;projection.cbmc=solve;projection.main();rows.append(('all16 history projector','python verif/render_history_projection.py',folder/'projection/result.json'))
    cert_path=ROOT/'metadata/closure/actor_types.json';cert=json.loads(cert_path.read_text());old_locks=dict(cert['verification_inputs']);accepted=json.loads((ROOT/'metadata/closure/actor_render.json').read_text())
    for name,expected in old_locks.items():assert hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==expected,'stale old actor_types input '+name
    imported=[];profiles=[];new_locks={}
    assumptions=['Ordinary disjoint RAM, immutable registered resources, initialized native output storage and ordinary disjoint stack; no device alias, asynchronous mutation or self-modifying resources.','Valid physical slot indices below16, active prefixes at most15 with an in-array sentinel, and ordinary disjoint word-normalized addressing. Fixed-slot normalization has an arbitrary-other-slot byte frame; compiled integration separately varies all16 slots.','Normal initializer ownership: demo explicitly seeds both coordinate generations, passenger placement seeds current pixels, stone placement preserves caches, and no mode-entry/projection clear is invented.','Synchronous pixel services preserve actor arrays and SI/DS/CS/SS:SP at the declared cuts; their other register/flag/status outputs are arbitrary shared inputs. Actual blits remain independently C/D.','Only the local history obligation is raised to B. The L0-to-L1 link remains differential C/D; finite shipped-resource/alias A properties keep their original domains. No new A or unrestricted whole-session theorem is claimed.']
    for label,command,path in rows:
        proof=json.loads(path.read_text());maintained={};tools={}
        for name,raw in proof['inputs'].items():
            source=Path(name) if Path(name).is_absolute() else ROOT/name
            assert hashlib.sha256(source.read_bytes()).hexdigest()==raw,'stale profile '+name
            if source.is_relative_to(ROOT) and source.relative_to(ROOT).parts[0]!='build':
                relative=source.relative_to(ROOT).as_posix();maintained[relative]=hashlib.sha256(source.read_bytes().replace(b'\r\n',b'\n')).hexdigest();new_locks[relative]=maintained[relative]
            elif not source.is_relative_to(ROOT):tools[name]=raw
        profiles.append(dict(profile=label,command=command,replay='python verif/demo_scene_types.py',receipt=str(path.relative_to(ROOT)),result=proof['result'],seconds=proof['seconds'],peak_private_bytes=proof['peak_private_bytes'],unwind=proof['unwind'],preprocessed_sha256=proof['preprocessed_sha256'],source_inputs=maintained,tool_inputs=tools))
        imported.append(dict(property='Render persistence B: '+label,level='B',command=command+' (full replay: python verif/demo_scene_types.py)',result=f'PASS {proof["seconds"]:.3f}s; private peak {proof["peak_private_bytes"]} bytes',method='Actual C profile imported from accepted actor_render and freshly replayed in close-stones-7. Complete declared slot outputs/frame/dependence or explicit seed/initializer/loader/projector scope; assumptions and exact source/tool/profile locks are in render_persistence_profiles.',date=date.today().isoformat()))
    cert['evidence']=[r for r in cert['evidence'] if not r['property'].startswith('Render persistence B: ')];cert['evidence']+=imported
    cert['assumptions']=[*assumptions,*[r for r in cert['assumptions'] if r not in assumptions]]
    cert['status']=cert['proposed_status']='verified-under-assumptions';cert['status_reason']='Supervisor close-stones-7 decision approved the B renderer-persistence evidence transfer; no A claim.'
    cert['proposed_status_reason']='Finite resource/alias A domains remain unchanged; render persistence is B under explicit ordinary-memory, valid-slot/prefix, initializer and synchronous service-frame assumptions, freshly replayed on actual C.'
    cert['render_persistence_profiles']=profiles;cert['verification_inputs'].update(new_locks)
    cert['evidence_refreshed']=dict(date=date.today().isoformat(),command='python verif/demo_scene_types.py',imported_from='metadata/closure/actor_render.json',accepted_certificate_sha256=hashlib.sha256((ROOT/'metadata/closure/actor_render.json').read_bytes()).hexdigest(),existing_locks_revalidated=len(old_locks),existing_lock_values_changed=[],added_or_revalidated_profile_locks=len(new_locks),profiles=len(rows),note='Fresh actual-C replay under worker7 capped solver permits. Existing46 LF-normalized locks revalidated unchanged; B profile maintained-source LF locks and raw tool/generated-profile hashes imported explicitly. Status set only by the supervisor instruction; no new A.')
    save(cert_path,cert);save(folder/'transfer.json',dict(result='PASS',profiles=profiles,certificate_sha256=hashlib.sha256(cert_path.read_bytes()).hexdigest(),accepted_inventory=accepted['coverage_inventory']))
    print('PASS actor_types B transfer',len(rows),'profiles',flush=True)
if __name__=='__main__':main()
