"""Private-native mutants must be rejected by the consuming real bridge."""
import argparse,json,subprocess,sys
from closure_support import ROOT,hashes,save
from hud_shells import OUT

MUTANTS=[
 ('glyph','204u+digit','205u+digit','DrawHudDigit','render'),
 ('cursor','x+6u','x+7u','DrawHudDigitAndAdvance','render'),
 ('changed-comparison','current!=previous','current==previous','RedrawChangedFourDigitNumber','render'),
 ('sentinel','current==255','current==254','RedrawChangedFourDigitNumber','render'),
 ('score-cap','v.score_high>15','v.score_high>=15','RefreshHudAndTimerBar','render'),
 ('score-priority','hud_number(&r,HUD_NUMBER_SIX,v.score_low,v.cached_score_low,v.score_high,v.cached_score_high);r.next=HUD_TIMER;','hud_number(&r,HUD_NUMBER_SIX,v.score_low,v.cached_score_low,v.score_high,v.cached_score_high);r.next=HUD_JOURNEYS;','RefreshHudAndTimerBar','render'),
 ('fare-selection','if(v.icon_one)fare=v.fare_one;','if(v.icon_one)fare=v.fare_two;','RefreshHudAndTimerBar','render'),
 ('bar-signed','(int16_t)width>=(int16_t)previous','width>=previous','RefreshHudAndTimerBar','render'),
 ('bar-shrink-span','r.remaining=r.cumulative?(uint16_t)(r.cell-(previous>>2)):0;','r.remaining=r.cumulative?(uint16_t)(r.cell-(previous>>2)):1;','RefreshHudAndTimerBar','render'),
 ('mask-selection','r.mask_index=(uint8_t)(last&3u);','r.mask_index=(uint8_t)((last&3u)^1u);','RefreshHudAndTimerBar','render'),
 ('unconsumed-effect','HudResult r=hud_empty(HUD_SCORE);hud_store(&r,HF_CURSOR_Y,194);','HudResult r=hud_empty(HUD_SCORE);hud_store(&r,HF_CURSOR_Y,194);hud_store(&r,HF_CURSOR_Y,194);','RefreshHudAndTimerBar','render'),
 ('working-projection','v->cached_score_high=e.a;','v->cached_score_high=(uint16_t)(e.a+1u);','RefreshHudAndTimerBar','render'),
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
    build=json.loads((OUT/'build.json').read_text());source=(ROOT/'native/hud.c').read_text();rows=[]
    for name,old,new,target,suite in MUTANTS:
        assert source.count(old)==1,(name,source.count(old))
        folder=OUT/'mutants'/name;folder.mkdir(parents=True,exist_ok=True)
        mutated=folder/'hud.c';mutated.write_text(source.replace(old,new).replace('#include "hud.h"','#include "'+(ROOT/'native/hud.h').as_posix()+'"'));dll=folder/'mutant.dll'
        abort=folder/'reject.c';abort.write_text('#include <stdio.h>\n#include <stdlib.h>\nvoid rp_test_abort(void){fputs("DETECTED_BY_BRIDGE\\n",stderr);_Exit(97);}\n')
        command=[str(dll) if arg==build['command'][build['command'].index('-o')+1] else str(mutated) if arg==str(ROOT/'native/hud.c') else arg for arg in build['command']]
        command+=['-Dabort=rp_test_abort',str(abort)]
        p=subprocess.run(command,capture_output=True,text=True);(folder/'compile.log').write_text(p.stdout+p.stderr)
        assert p.returncode==0,(name,p.stdout+p.stderr)
        probe_command=[sys.executable,'verif/hud_mutants.py','--probe',str(dll),target,suite]
        p=subprocess.run(probe_command,cwd=ROOT,capture_output=True,text=True,timeout=120)
        row=dict(name=name,result='DETECTED_BY_BRIDGE' if p.returncode==97 and 'DETECTED_BY_BRIDGE' in p.stderr else 'UNDETECTED',mutation=[old,new],command=probe_command,compile_command=command,inputs=hashes([ROOT/'native/hud.c',ROOT/'native/bridge/hud_bridge.c',ROOT/'native/bridge/hud_support.h',ROOT/'verif/hud_mutants.py',ROOT/'tests'/f'{suite}.py']),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
        rows.append(row);save(OUT/'mutants.json',rows);print(name,row['result'],flush=True)
    assert all(r['result']=='DETECTED_BY_BRIDGE' for r in rows)
if __name__=='__main__':main()
