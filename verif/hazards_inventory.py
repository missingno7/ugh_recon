"""Audit every descriptor entry against the independent program model."""
import json,sys
from pathlib import Path
from closure_support import ROOT,receipt,save
from hazards_build import OUT,ENTRIES
sys.path.insert(0,str(ROOT/'tools'))
from common import MZ
import contacts_reference

def main():
    contacts_reference.OUT=OUT/'reference'
    path=contacts_reference.expanded_image(local=True)
    image=MZ(path.read_bytes()).image
    model=json.loads((ROOT/'metadata/program-model.json').read_text())
    site=model['indirect_sites']['013B:236F'];words=site['origin_words'];actual=[];species={}
    lookup={r['address']:'GAME:'+name for name in ENTRIES for r in [model['routines']['GAME:'+name]]}
    lookup['013B:0000']='ZERO';lookup['013B:1C0E']='GAME:IgnoreActorState'
    for label,address in [('bird',0x7630),('triopterus',0x766c),('dino',0x76a8),('tree',0x76e4)]:
        entries=[]
        for index in range(13):
            at=address+8+index*2;value=int.from_bytes(image[0x5c090+at:0x5c090+at+2],'little')
            target=f'013B:{value:04X}';assert target in lookup,target
            actual.append(dict(cell=f'5C09:{at:04X}',target=target))
            entries.append(dict(field=f'+{8+2*index:02X}',target=target,entry=lookup[target]))
        species[label]=entries
    assert actual==words
    assert set(row['target'] for row in actual)==set(site['targets'])
    save(OUT/'inventory.json',receipt(['python','verif/hazards_inventory.py'],[Path(__file__),path,ROOT/'metadata/program-model.json'],
        result='PASS',descriptors=species,target_count=len(site['targets']),words=52,zero_entries=sum(x['target']=='013B:0000' for x in actual)))
    print('PASS all 52 descriptor fields; complete',len(site['targets']),'target set; zero entries remain explicit')
if __name__=='__main__':main()
