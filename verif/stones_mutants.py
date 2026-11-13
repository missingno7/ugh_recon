"""Seed defects in private copies and require the maintained cases to reject."""
import subprocess
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save
from stones_build import OUT,pair
def main():
    raw=(ROOT/'native/stones.c').read_text();rows=[]
    mutations=[('action-high-byte','action_word&128u','action_word&32768u'),
        ('gravity','slot->vertical_motion+2u','slot->vertical_motion+3u'),
        ('old-surface-equality','stone_signed(old_bottom)>stone_signed(platform->surface_y)','stone_signed(old_bottom)>=stone_signed(platform->surface_y)'),
        ('alternate-identity','slot->type->id==ACTOR_STONE &&','slot->type->id>=ACTOR_STONE &&')]
    for tag,old,new in mutations:
        assert raw.count(old)==1
        folder=OUT/'mutants'/tag;inputs=pair(folder);mutant=folder/'stones.c';mutant.write_text(raw.replace(old,new))
        inc=folder/'pair.inc';inc.write_text(inc.read_text().replace((ROOT/'native/stones.c').as_posix(),mutant.as_posix()))
        source=ROOT/'verif/stones_harness.c';harness=folder/'harness.c';harness.write_text('#include "pair.inc"\n'+source.read_text())
        exe=folder/'enumerate.exe';built=compile_c([harness],exe,[ROOT/'native',ROOT/'native/bridge',ROOT/'c'])
        run=subprocess.run([str(exe)],capture_output=True,text=True);row=receipt(built['command'],[*inputs,source,mutant,Path(__file__)],
            result='DETECTED' if run.returncode==23 else 'MISSED',execution=[str(exe)],stdout=run.stdout,stderr=run.stderr)
        save(folder/'result.json',row);rows.append(dict(mutant=tag,result=row['result'],stderr=run.stderr));print(rows[-1],flush=True)
        assert row['result']=='DETECTED'
    save(OUT/'mutants.json',rows)
if __name__=='__main__':main()
