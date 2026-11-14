"""Actual compiled-C mutation controls; compilation failure is not detection."""
from pathlib import Path
from closure_support import ROOT,receipt,save
from sequencing_build import OUT
from sequencing_proof import common,body
from session_record_proof import source
from sequencing_limits import cbmc
MUTANTS=[
 ('life-adlib-mask','lifecycle','life-order','r.argument=1;','r.argument=3;'),
 ('life-mode-high-bit','lifecycle','life-order','value&127u','value&255u'),
 ('fade-unsigned','session','session-step','(int16_t)w.fade_level<0','w.fade_level==0xffff'),
 ('move-loop-inequality','session','session-step','e.index==w.player_count','e.index!=w.player_count'),
 ('lives-word-decrement','session','session-step','e.value=(uint8_t)(w.lives-1u)','e.value=(uint16_t)(w.lives-1u)'),
 ('water-cap-off-one','session','loader-scalar','scaled>0x17e0u?0x17e0u:scaled','scaled>0x17dfu?0x17dfu:scaled'),
 ('score-reduce-equality','session','display-score','v>1000000u','v>=1000000u'),
 ('request-overwrite','session','protocol','p->failed || p->pending','p->failed'),
 ('frame-skips-enemy-update','session','session-order','case SESSION_UPDATE_ACTORS:p->phase=SP_UPDATE_ENEMIES','case SESSION_UPDATE_ACTORS:p->phase=SP_UPDATE_ITEMS'),
 ('frame-budget-crosses-level','session','session-step','case SESSION_INITIALIZE_LEVEL:p->completed_frames=0;','case SESSION_INITIALIZE_LEVEL:'),
 ('stone-alternate-callback','session','record:actor','r->record_class==LOAD_STONE?16:8','r->record_class==LOAD_STONE?8:8'),
 ('private-callback-role','session','record:bird','e.value=(uint16_t)r->record_class','e.value=(uint16_t)LOAD_TREE'),
 ('private-platform-selection','session','record:tree','(uint16_t)(r->platform*2u)','(uint16_t)(r->platform*2u+2u)'),
 ('record-slot-selection','session','record:actor','LOAD_VALUE,r->slot,0,0','LOAD_VALUE,(uint16_t)(r->slot+2u),0,0'),
 ('retained-live-reread','session','record:trio','quarter-repeated','quarter-v'),
]
def main():
    rows=[]
    for name,unit,key,before,after in MUTANTS:
        folder=OUT/'mutants'/name;folder.mkdir(parents=True,exist_ok=True);path=ROOT/'native'/f'{unit}.c';original=path.read_text();assert before in original,(name,before)
        mutant=folder/'mutant.c';mutant.write_text(original.replace(before,after,1));code=source(key.split(':')[1],'output') if key.startswith('record:') else common()+body(key)
        code=code.replace('#include "'+path.as_posix()+'"','#include "'+mutant.as_posix()+'"');h=folder/'harness.c';h.write_text(code)
        r=cbmc(h,folder,[path,mutant,ROOT/'native/session.h',ROOT/'native/lifecycle.h',ROOT/'verif/sequencing_mutants.py',ROOT/'verif/sequencing_proof.py',ROOT/'verif/session_record_proof.py',ROOT/'verif/session_loader.py'],unwind=48 if key=='session-order' else 32,timeout=600)
        assert r['result']=='FAIL' and r['failures'] and any('unwind' not in n for n,m in r['failures']) and all('unwind' not in n for n,m in r['failures']),(name,r['result'],r['failures'])
        bridge=any('BRIDGE_REJECTED' in m or 'consumed by bridge' in m for n,m in r['failures']);result='DETECTED_BY_BRIDGE' if bridge else 'DETECTED_BY_PROPERTY';rows.append(dict(mutant=name,result=result,failures=r['failures'],seconds=r['seconds']));print(name,result,flush=True)
    save(OUT/'mutants.json',receipt(['python','verif/sequencing_mutants.py'],[__file__,ROOT/'native/session.c',ROOT/'native/lifecycle.c',ROOT/'native/session.h',ROOT/'native/lifecycle.h',ROOT/'verif/session_record_proof.py',ROOT/'verif/sequencing_proof.py'],result='PASS',rows=rows))
if __name__=='__main__':main()
