"""Require private native retained-quirk defects to fail the real-C harness."""
import subprocess
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save
from delivery_build import OUT,pair

def main():
    source=ROOT/'native/passenger_delivery.c';raw=source.read_text();rows=[]
    mutations=[('request-141','slot->request_ticks=140;pd_emit(&result,PD_REQUEST,0,140);','slot->request_ticks=141;pd_emit(&result,PD_REQUEST,0,141);'),
        ('approach-derived-X','render->pixel_x+slot->type->geometry.anchor_x-16u','(slot->position.x32>>5)+slot->type->geometry.anchor_x-16u'),
        ('signed-fare-floor','craft->fare>craft->minimum_fare','pd_signed(craft->fare)>pd_signed(craft->minimum_fare)'),
        ('unsigned-quick','pd_signed(slot->quick_delivery_ticks)>0','slot->quick_delivery_ticks>0'),
        ('positive-only-bonus','if(slot->quick_delivery_ticks &&','if(pd_signed(slot->quick_delivery_ticks)>0 &&'),
        ('rescue-land-fare','pd_emit(&result,PD_FARE,incoming_craft,slot->type->initial_fare);','if(entry==PD_RESCUE) slot->type=slot->type->paired_type;\n        pd_emit(&result,PD_FARE,incoming_craft,slot->type->initial_fare);'),
        ('premature-finish','result.spawn_bonus=result.bonus_sound=result.finish_pending=1;','pd_finish(&result,slot,world);result.spawn_bonus=result.bonus_sound=result.finish_pending=1;')]
    for tag,old,new in mutations:
        assert raw.count(old)>=1,tag
        folder=OUT/'mutants'/tag;inputs=pair(folder);mutant=folder/source.name;mutant.write_text(raw.replace(old,new))
        inc=folder/'pair.inc';inc.write_text(inc.read_text().replace(source.as_posix(),mutant.as_posix()))
        harness=folder/'harness.c';harness.write_text('#include "pair.inc"\n'+(ROOT/'verif/delivery_harness.c').read_text())
        exe=folder/'enumerate.exe';built=compile_c([harness],exe,[ROOT/'native',ROOT/'native/bridge',ROOT/'c'])
        run=subprocess.run([str(exe)],capture_output=True,text=True)
        row=receipt(built['command'],[*inputs,ROOT/'verif/delivery_harness.c',mutant,Path(__file__)],result='DETECTED' if run.returncode==23 else 'MISSED',stdout=run.stdout,stderr=run.stderr)
        save(folder/'result.json',row);rows.append(dict(mutant=tag,result=row['result'],stderr=run.stderr));print(rows[-1],flush=True);assert row['result']=='DETECTED'
    save(OUT/'mutants.json',rows)
if __name__=='__main__':main()
