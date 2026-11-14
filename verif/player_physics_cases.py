"""Compile and execute actual full L1 against the real consuming bridge."""
import subprocess
from closure_support import ROOT,compile_c,receipt,save
from player_physics_build import OUT
from player_physics_pair import pair
def run(folder,native_mutant=None,bridge_mutant=None):
    inputs=pair(folder);source=folder/'harness.c'
    inc=folder/'pair.inc';text=inc.read_text()
    if native_mutant:
        original=(ROOT/'native/player_physics.c').read_text();old,new=native_mutant;assert old in original
        mutant=folder/'mutant.c';mutant.write_text(original.replace(old,new,1));text=text.replace((ROOT/'native/player_physics.c').as_posix(),mutant.as_posix());inputs.append(mutant)
    if bridge_mutant:
        old,new=bridge_mutant;assert old in text;text=text.replace(old,new,1)
    inc.write_text(text)
    source.write_text((ROOT/'verif/player_physics_harness.c').read_text())
    exe=folder/'cases.exe';built=compile_c([source],exe,[ROOT/'c',ROOT/'native'],['-DACTOR_VERIFY','-Wno-misleading-indentation'])
    result=subprocess.run([str(exe)],capture_output=True,text=True)
    record=receipt(built['command'],[*inputs,ROOT/'verif/player_physics_harness.c',ROOT/'verif/player_physics_cases.py'],result='PASS' if not result.returncode else 'FAIL',stdout=result.stdout,stderr=result.stderr,returncode=result.returncode)
    save(folder/'result.json',record);return result,record
def main():
    result,_=run(OUT/'cases')
    print(result.stdout+result.stderr,flush=True);assert not result.returncode
if __name__=='__main__':main()
