"""Require consumption of the native selected craft in the machine composition.

The mutation changes only the selected result AFTER approach has decided to
board. The original complete machine-comparison harness should detect this once
the production bridge binds that output at the immediate tail. An EXPECTED_MISS
is a recorded blocker and makes this command fail.
"""
import subprocess
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save
from delivery_build import OUT,pair

def main():
    folder=OUT/'selection-gap';inputs=pair(folder);source=ROOT/'native/passenger_delivery.c';raw=source.read_text()
    old='if(center==target) {result->next=PD_NEXT_BOARD;return;}';assert raw.count(old)==1
    mutant=folder/source.name;mutant.write_text(raw.replace(old,'if(center==target) {result->next=PD_NEXT_BOARD;result->selected^=1;return;}'))
    inc=folder/'pair.inc';inc.write_text(inc.read_text().replace(source.as_posix(),mutant.as_posix()))
    original=ROOT/'verif/delivery_harness.c';harness=folder/'harness.c';harness.write_text('#include "pair.inc"\n'+original.read_text())
    exe=folder/'gap.exe';built=compile_c([harness],exe,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-DACTOR_VERIFY'])
    run=subprocess.run([str(exe)],capture_output=True,text=True)
    result='EXPECTED_MISS' if run.returncode==0 else 'DETECTED_BY_BRIDGE' if run.returncode==23 else 'ERROR'
    save(folder/'result.json',receipt(built['command'],[*inputs,original,mutant,Path(__file__)],result=result,stdout=run.stdout,stderr=run.stderr))
    print(result+' '+run.stdout+run.stderr,flush=True);assert result=='DETECTED_BY_BRIDGE'
if __name__=='__main__':main()
