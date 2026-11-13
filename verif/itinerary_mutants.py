"""Seed retained-quirk defects in private native copies; require detection."""
import subprocess
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save
from itinerary_build import OUT,pair
def main():
    path=ROOT/'native/passenger_itinerary.c';raw=path.read_text();rows=[]
    mutations=[('objective-sign','remaining<128u','remaining!=255u'),('completion-byte','world->completion=254','world->completion=0'),
        ('departure-lookahead','if(index+1==animation->count)','if(index==animation->count)'),
        ('cached-pixel','render->pixel_x+slot->type->geometry.anchor_x','itinerary_sar(slot->position.x32)+slot->type->geometry.anchor_x'),
        ('zero-delay','if(delay) {','if(1) {')]
    for tag,old,new in mutations:
        assert raw.count(old)==1
        folder=OUT/'mutants'/tag;inputs=pair(folder);mutant=folder/'passenger_itinerary.c';mutant.write_text(raw.replace(old,new))
        inc=folder/'pair.inc';inc.write_text(inc.read_text().replace(path.as_posix(),mutant.as_posix()))
        source=ROOT/'verif/itinerary_harness.c';harness=folder/'harness.c';harness.write_text('#include "pair.inc"\n'+source.read_text())
        exe=folder/'enumerate.exe';built=compile_c([harness],exe,[ROOT/'native',ROOT/'native/bridge',ROOT/'c'])
        run=subprocess.run([str(exe)],capture_output=True,text=True);row=receipt(built['command'],[*inputs,source,mutant,Path(__file__)],
            result='DETECTED' if run.returncode==23 else 'MISSED',execution=[str(exe)],stdout=run.stdout,stderr=run.stderr)
        save(folder/'result.json',row);rows.append(dict(mutant=tag,result=row['result'],stderr=run.stderr));print(rows[-1],flush=True)
        assert row['result']=='DETECTED'
    save(OUT/'mutants.json',rows)
if __name__=='__main__':main()
