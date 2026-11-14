"""Input callers, shared writers, shipped matcher grammar and Amiga meaning check."""
import sys,json,hashlib
from pathlib import Path
from closure_support import ROOT,receipt,save
from input_build import OUT,NAMES
sys.path.insert(0,str(ROOT/'tools'))
import contacts_reference,difftest
contacts_reference.OUT=OUT/'reference'

def main():
 plain=contacts_reference.prepare_reference(local=True);m=difftest.Machine();model=json.loads((ROOT/'metadata/program-model.json').read_text());rows=[];refs=list((OUT/'whole').glob('*.ref.json')) or list((ROOT/'build/whole').glob('*.ref.json'))
 for name in NAMES:
  full='GAME:'+name;address=model['routines'][full]['address'];callers=sorted({owner for site in model['sites'].values() if not site.get('indirect') and [address,'call'] in site.get('edges',[]) for owner in site.get('owners',[])});indirect=[k for k,v in model['indirect_sites'].items() if address in v.get('targets',[])];rows.append(dict(name=full,address=address,static_callers=callers,indirect_sites=indirect,scenarios=[p.name.split('.')[0] for p in refs if full in json.loads(p.read_text())['coverage']['routines']]))
 offset=m.off('DGROUP:KeyboardSequenceRecords');records=[]
 for i in range(34):
  raw=m.read(m.seg('DGROUP:PlayerCount'),offset+6*i,6);scan=list(raw[:raw.index(255)]);assert len(scan) in [1,2];assert len(scan)==1 or scan[0]==0xe0;assert scan!=[0xe0];records.append(dict(record=i,scans=[f'{v:02x}' for v in scan],destination=raw[3],value=raw[4],candidate=raw[5]))
 assert m.read(m.seg('DGROUP:PlayerCount'),offset+204,1)==b'\xff';assert {r['destination'] for r in records}<={0,2,4,6,8,10,12,14,16,18,20};assert {r['value'] for r in records}<={0,255}
 writers={}
 for field in model['components']['input']['written_only_here']+model['components']['input']['shared_written_state']+['PlayerCount','KeyboardHandlerVector']:
  for writer in model['variables'].get(field,{}).get('writers',[]):writers.setdefault(writer,[]).append(field)
 amiga_path=ROOT/'build/amiga/files/t';amiga=None
 if amiga_path.exists():
  import amiga as decoder
  raw=amiga_path.read_bytes();assert hashlib.sha256(raw).hexdigest()=='6826d1f7438e856367d2f78a6b546189517d1255e0f0ca526949d14e214355e7';hunk=decoder.Hunk(raw);code=bytes(hunk.hunks[0]['data']);import capstone
  md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000);listing=[dict(offset=f'{i.address:05x}',mnemonic=i.mnemonic,operands=i.op_str) for i in md.disasm(code[0x5192:0x5240],0x5192)]
  amiga=dict(file_sha256=hashlib.sha256(raw).hexdigest(),range='h0:05192..0523E',listing=listing,meaning='CIA keyboard ISR reads BFEC01, acknowledges CIA, inverts/shifts the code and sets/clears key state. It uses keyboard translation and joystick state separately; no DOS six-byte matcher equivalence or cheat effect is inferred.')
 save(OUT/'inventory.json',receipt([sys.executable,'verif/input_inventory.py'],[Path(__file__),ROOT/'metadata/program-model.json',ROOT/'src/asm/GAME.ASM',ROOT/'src/data/DGDATA.ASM',ROOT/'c/menu.c',plain,*([amiga_path,ROOT/'tools/amiga.py'] if amiga else [])],result='PASS',routines=rows,records=records,matcher_states=['reset: index0/all candidates0','after E0: index1/only E0-leading records active'],writers=writers,indexed_writer_note='SelectPlayerControls writes both PlayerOneControlMode and PlayerTwoControlMode through PlayerOneControlMode+BX (BX0/2), despite the base-symbol writer model naming only the first. PlayerCount belongs to front-end/session configuration, borrowed by InputState.',amiga=amiga))
 print('PASS8 input entries;34 control records; reachable matcher has2 states; Amiga inspected:',bool(amiga))
if __name__=='__main__':main()
