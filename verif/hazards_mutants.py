"""Seed timer/routing/force defects in scratch native sources only."""
import subprocess
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save
from hazards_pair import pair
from hazards_build import OUT

def main():
    native=ROOT/'native/hazards.c';base=native.read_text();rows=[]
    defects=[('warning71','hazard_counter(&result,slot,70)','hazard_counter(&result,slot,71)'),
        ('impact-routing','entry==H_TRIO_CHARGE_BEGIN||entry==H_DINO_BEGIN?5:7','entry==H_TRIO_CHARGE_BEGIN||entry==H_DINO_BEGIN?5:entry==H_TRIO_IMPACT_BEGIN?9:7'),
        ('dino-force40','?41u:65495u','?40u:65495u')]
    for name,old,new in defects:
        assert old in base,name
        folder=OUT/('mutant-'+name);inputs=pair(folder)
        mutant=folder/'hazards.c';mutant.write_text(base.replace(old,new))
        include=folder/'pair.inc';include.write_text(include.read_text().replace(native.as_posix(),mutant.as_posix()))
        harness=folder/'harness.c';harness.write_text('#include "pair.inc"\n'+(ROOT/'verif/hazards_harness.c').read_text())
        exe=folder/'mutant.exe';compile_c([harness],exe,[ROOT/'c',ROOT/'native'])
        run=subprocess.run([str(exe)],capture_output=True,text=True)
        assert run.returncode==23,(name,run.stdout,run.stderr)
        rows.append(dict(name=name,result='DETECTED',stderr=run.stderr));print(name,'DETECTED',flush=True)
    save(OUT/'mutants.json',receipt(['python','verif/hazards_mutants.py'],[Path(__file__),native,ROOT/'verif/hazards_harness.c'],result='PASS',mutants=rows))
if __name__=='__main__':main()
