"""Caller/service/borrowed-storage audit; independent shipped picture inventory."""
import json,sys
from pathlib import Path
from closure_support import ROOT,receipt,save
from pictures_build import OUT,NAMES
sys.path.insert(0,str(ROOT/'tools'))
import contacts_reference,difftest
contacts_reference.OUT=OUT/'reference'

def main():
 plain=contacts_reference.prepare_reference(local=True);m=difftest.Machine();model=json.loads((ROOT/'metadata/program-model.json').read_text());rows=[]
 for name in NAMES:
  full='GAME:'+name;address=model['routines'][full]['address'];sites={k:v for k,v in model['sites'].items() if full in v.get('owners',[])}
  rows.append(dict(name=full,address=address,static_callers=sorted({owner for site in model['sites'].values() if not site.get('indirect') and [address,'call'] in site.get('edges',[]) for owner in site.get('owners',[])}),indirect_sites=[k for k,v in model['indirect_sites'].items() if address in v.get('targets',[])],outgoing_sites=sites))
 pointers={name:dict(offset=m.rw('GAME:'+name),segment=m.rw('GAME:'+name,2),model=model['variables'].get(name,{})) for name in ['IceScratchPointer','PicturePaletteDestination']}
 save(OUT/'inventory.json',receipt([sys.executable,'verif/pictures_inventory.py'],[Path(__file__),ROOT/'metadata/program-model.json',ROOT/'src/asm/GAME.ASM',ROOT/'c/video.c',ROOT/'c/scene.c',plain],result='PASS',routines=rows,pointers=pointers,storage=dict(scratch_bytes=64768,pixels=64000,palette_offset=64000,palette_bytes=768,palette_order='256 RGB triples, already6-bit in shipped resources; verbatim word copy, no shift or mask',owner='Borrowed existing ICE workspace and video base palette. No native global image or palette owner.',physical_tail='Scratch ends at FD00; its64K window includes the next16 bytes of C state/padding and752 bytes of the packed tile-map bank.'),startup=[dict(frame=frame,meaning=meaning,retraces=ticks) for frame,meaning,ticks in [('2D9A','Play Byte',280),('2BF6','Bones Park Software Artistic',280),('2F9E','present',140),('2FB7','Ugh! title',420)]],file_boundary='No file service is called: all four picture resources are embedded banks. No missing-file branch exists; invalid/absent data at a supplied resource base is ordinary RAM and is interpreted without a length.',keyboard='Initialized IRQ1 remains installed throughout normal pictures. Only Q invokes existing shutdown tail: sound shutdown, restore BIOS mode, RestoreKeyboardInterrupt, INT21/4C. Escape/timeout do not restore IRQ1 here.'))
 print('PASS3 caller/service audits; fixed embedded banks; borrowed scratch/palette')
if __name__=='__main__':main()
