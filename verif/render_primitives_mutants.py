"""Private-native mutants must be rejected by the consuming real bridge."""
import argparse,json,subprocess,sys
from closure_support import ROOT,hashes,save
from render_primitives_shells import OUT

MUTANTS=[
 ('placement','p.destination=(uint16_t)((p.fixed_page?fixed_page:draw_page)+render_quarter(x)+(uint16_t)(p.y*96u));','p.destination=(uint16_t)((p.fixed_page?fixed_page:draw_page)+render_quarter(x)+(uint16_t)(p.y*96u)+1u);','DrawTransparentSprite','render_primitives'),
 ('source-direction','c->backward?-1:1','1','DrawTransparentSprite','render_primitives'),
 ('water-tint','e.value|=0x40u','e.value|=0x20u','DrawTransparentSprite','render_primitives'),
 ('plane-rollover','if(!c->plane)','if(0)','DrawTransparentSprite','render_primitives'),
 ('rectangle-width','r.width=(uint16_t)((uint16_t)((uint16_t)((x&3u)+width)+3u)>>2);','r.width=(uint16_t)(((uint16_t)((uint16_t)((x&3u)+width)+3u)>>2)+1u);','RestoreBackgroundRectangle','render_primitives'),
 ('save-endpoint','r.source_end=(uint16_t)(source+(backward?-(int)count:(int)count));','r.source_end=(uint16_t)(source+(backward?-(int)count:(int)count)+1u);','SaveDrawPageBackground','render_primitives'),
 ('map-tile-x','r.x=(uint16_t)((packed_coordinates&255u)*16u);','r.x=(uint16_t)((packed_coordinates&255u)*16u+16u);','DrawMapTile','render'),
 ('animation-rate-sign','(int16_t)p.rate>90','p.rate>90','AnimateAndDrawPlayer','render'),
 ('visibility-equality','(int16_t)x>-32','(int16_t)x>=-32','RestorePlayerBackground','render'),
 ('cache-value','cache->sprite=value;','cache->sprite=(uint16_t)(value+1u);','CachePlayerDrawState','render_primitives'),
 ('unconsumed-restore','r.draw=render_player_visible(cache.x,cache.y);','r.draw=(uint8_t)!render_player_visible(cache.x,cache.y);','RestorePlayerBackground','render'),
 ('directory-index','return (uint16_t)(sprite*4u);','return (uint16_t)(sprite*4u+1u);','RestoreSpriteBackground','render'),
]

def probe(dll,target,suite):
    import sys
    sys.path.insert(0,str(ROOT/'tools'))
    import difftest,nbuild,contacts_reference
    contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True)
    machine=difftest.Machine();loaded=nbuild.load_l1(dll);count=0
    for c in difftest.load_suite(suite).CASES:
        if c.routine!='GAME:'+target:continue
        count+=1;difftest.run(c,machine,loaded,False)
    print('UNDETECTED',count,flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--probe',nargs=3);a=ap.parse_args()
    if a.probe:probe(*a.probe);return
    build=json.loads((OUT/'build.json').read_text());source=(ROOT/'native/render_primitives.c').read_text();rows=[]
    for name,old,new,target,suite in MUTANTS:
        assert source.count(old)==1,(name,source.count(old))
        folder=OUT/'mutants'/name;folder.mkdir(parents=True,exist_ok=True)
        mutated=folder/'render_primitives.c';mutated.write_text(source.replace(old,new).replace('#include "render_primitives.h"','#include "'+(ROOT/'native/render_primitives.h').as_posix()+'"'));dll=folder/'mutant.dll'
        abort=folder/'reject.c';abort.write_text('#include <stdio.h>\n#include <stdlib.h>\nvoid rp_test_abort(void){fputs("DETECTED_BY_BRIDGE\\n",stderr);_Exit(97);}\n')
        command=[str(dll) if arg==build['command'][build['command'].index('-o')+1] else str(mutated) if arg==str(ROOT/'native/render_primitives.c') else arg for arg in build['command']]
        command+=['-Dabort=rp_test_abort',str(abort)]
        p=subprocess.run(command,capture_output=True,text=True);(folder/'compile.log').write_text(p.stdout+p.stderr)
        assert p.returncode==0,(name,p.stdout+p.stderr)
        probe_command=[sys.executable,'verif/render_primitives_mutants.py','--probe',str(dll),target,suite]
        p=subprocess.run(probe_command,cwd=ROOT,capture_output=True,text=True,timeout=120)
        row=dict(name=name,result='DETECTED_BY_BRIDGE' if p.returncode==97 and 'DETECTED_BY_BRIDGE' in p.stderr else 'UNDETECTED',mutation=[old,new],command=probe_command,compile_command=command,inputs=hashes([ROOT/'native/render_primitives.c',ROOT/'native/bridge/render_primitives_bridge.c',ROOT/'native/bridge/render_primitives_support.h',ROOT/'verif/render_primitives_mutants.py',ROOT/'tests'/f'{suite}.py']),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
        rows.append(row);save(OUT/'mutants.json',rows);print(name,row['result'],flush=True)
    assert all(r['result']=='DETECTED_BY_BRIDGE' for r in rows)
if __name__=='__main__':main()
