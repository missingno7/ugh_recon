"""Seed three retained-quirk defects in scratch and require real-C detection."""
import json,subprocess
from closure_support import ROOT,compile_c,receipt,save
from items_build import OUT,pair

def main():
    rows=[]
    for name,relative,old,new in [
        ('timer-cap','native/items.c','sum>23099u?23099u:sum','sum>=23099u?23098u:sum'),
        ('expiry','native/items.c','if(!item->motion_or_lifetime)','if(item->motion_or_lifetime==1)'),
        ('safe-full-pool','native/bridge/items_bridge.c','r->ip=target;return UGH_CONTROL_TRANSFER;','return UGH_OK;')]:
        folder=OUT/'mutants'/name;inputs=pair(folder)
        maintained=ROOT/relative;text=maintained.read_text();assert text.count(old)==1
        mutant=folder/maintained.name
        text=text.replace(old,new)
        if 'bridge' in relative:text=text.replace('#include "../items.h"','#include "'+(ROOT/'native/items.h').as_posix()+'"')
        mutant.write_text(text)
        inc=folder/'pair.inc';inc.write_text(inc.read_text().replace(maintained.as_posix(),mutant.as_posix()))
        harness=folder/'harness.c';harness.write_text('#include "pair.inc"\n'+(ROOT/'verif/items_harness.c').read_text())
        exe=folder/'mutant.exe';built=compile_c([harness],exe,[ROOT/'c',ROOT/'native'])
        run=subprocess.run([str(exe)],capture_output=True,text=True)
        row=receipt(built['command'],[*inputs,maintained,mutant,ROOT/'verif/items_harness.c',__file__],
            mutation=name,result='DETECTED' if run.returncode==23 else 'MISSED',stdout=run.stdout,stderr=run.stderr)
        save(folder/'result.json',row);rows.append(row);assert run.returncode==23,row
        print(name,'DETECTED',run.stderr.strip(),flush=True)
    save(OUT/'mutants/result.json',dict(result='PASS',mutants=rows))

if __name__=='__main__':main()
