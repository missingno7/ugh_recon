"""Static callers, shared writers, exact shipped records and Amiga meaning."""
import sys,json,hashlib
from pathlib import Path
from closure_support import ROOT,receipt,save
from high_scores_build import OUT,NAMES
sys.path.insert(0,str(ROOT/'tools'))
import contacts_reference,difftest
contacts_reference.OUT=OUT/'reference'
MENUS=['RunMainMenuAndAttractLoop','DrawMainMenu','DrawMenuHeaderSprites','SelectPlayerControls','DrawControlOptions','EditLevelPassword','CopyIndexedMenuString','DrawTextLine','DrawTextBlock','PrepareAttractMap0','PrepareAttractMap90','ShowLevelIntroduction','ShowCreditsPages']

def main():
 plain=contacts_reference.prepare_reference(local=True);m=difftest.Machine();model=json.loads((ROOT/'metadata/program-model.json').read_text());rows=[]
 for name in [*NAMES,*MENUS]:
  full='GAME:'+name;address=model['routines'][full]['address'];callers=sorted({owner for site in model['sites'].values() if not site.get('indirect') and [address,'call'] in site.get('edges',[]) for owner in site.get('owners',[])})
  rows.append(dict(name=full,address=address,static_callers=callers,indirect_sites=[k for k,v in model['indirect_sites'].items() if address in v.get('targets',[])]))
 passwords=[]
 for mode,count in [(0,69),(1,81)]:
  position=m.rw('DGROUP:PasswordListPointers',2*mode);start=position;items=[]
  for index in range(count):
   raw=bytearray()
   while True:
    byte=m.read(m.seg('DGROUP:PlayerCount'),position,1)[0];position=(position+1)&65535
    if not byte:break
    raw.append(byte)
   items.append(dict(index=index,level=index+1,password=raw.decode('ascii'),length=len(raw)))
  assert m.read(m.seg('DGROUP:PlayerCount'),position,1)==b'\xff'
  passwords.append(dict(players=mode+1,start=start,count=count,maximum=max(i['length'] for i in items),items=items))
 table=m.read(m.seg('DGROUP:PlayerCount'),m.off('DGROUP:HighScoreRows'),107);assert table[-2:]==bytes([0,255])
 scores=[dict(name=table[21*i:21*i+14].decode('ascii'),digits=table[21*i+14:21*i+20].decode('ascii'),separator=table[21*i+20]) for i in range(5)]
 fields=['PlayerOneControlMode','PlayerTwoControlMode','PlayerCount','PlayerArrayBytes','SelectedDifficulty','WaterYPixels','CurrentLevelIndex','PasswordEditBuffer','HighScoreRows','HighScoreFileHandle','HighScoreRowStride','DecimalDigitBuffer']
 ownership={name:model['variables'].get(name,{}) for name in fields};amiga=None;path=ROOT/'build/amiga/files/t'
 if path.exists():
  from amiga import Hunk
  raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()=='6826d1f7438e856367d2f78a6b546189517d1255e0f0ca526949d14e214355e7';data=bytes(Hunk(raw).hunks[8]['data']);comparisons=[]
  for mode,start,count in [(0,0x2fa,69),(1,0x716,81)]:
   position=start;strings=[]
   for index in range(count):
    end=data.index(0,position);assert data[end+1]==index+1;strings.append(bytes(b^42 for b in data[position:end]).decode('ascii'));position=end+2
   assert data[position]==255;comparisons.append(dict(players=mode+1,count=count,equal_to_DOS=strings==[i['password'] for i in passwords[mode]['items']],items=strings))
  amiga=dict(file_sha256=hashlib.sha256(raw).hexdigest(),hunk=8,encoding='Each non-NUL password byte XOR42, NUL then1-based ordinal; finalFF',lists=comparisons,meaning='Same per-player-mode ordered level passwords, different encoding. Static data meaning only; no DOS byte or code equivalence.')
 save(OUT/'inventory.json',receipt([sys.executable,'verif/front_end_inventory.py'],[Path(__file__),ROOT/'metadata/program-model.json',ROOT/'src/asm/GAME.ASM',ROOT/'src/data/DGDATA.ASM',ROOT/'c/menu.c',ROOT/'c/scene.c',plain,*([path,ROOT/'tools/amiga.py'] if amiga else [])],result='PASS',routines=rows,ownership=ownership,passwords=passwords,high_scores=dict(bytes=107,rows=scores,filename=m.read(m.seg('DGROUP:PlayerCount'),m.off('DGROUP:Data_0CF1'),8).hex()),amiga=amiga,notes=['No second owner: views reborrow input/session/water/score cells.','SelectPlayerControls has indexed writes to both modes; model base-symbol write list names only the first.','Password acceptance is in the external RunGameFromPassword service; this closure owns edit/dispatch and documents that service boundary.','Named source writer/readers are not an arbitrary-pointer alias theorem.']))
 print('PASS23 caller audits;150 passwords;107 score bytes;max password lengths',[p['maximum'] for p in passwords],'Amiga inspected',bool(amiga))
if __name__=='__main__':main()
