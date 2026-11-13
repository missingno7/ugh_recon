"""Compile actual retained C and native code; exhaustive slices and C corpus."""
import subprocess
from closure_support import ROOT,compile_c,receipt,save
from render_history_build import OUT,pair
def run(folder,mutant=None,bridge_mutant=None):
    inputs=pair(folder)
    if mutant or bridge_mutant:
        path=folder/'pair.inc';text=path.read_text()
        if mutant:text=text.replace((ROOT/'native/actor_render.c').as_posix(),mutant.as_posix())
        if bridge_mutant:
            old,new=bridge_mutant;assert old in text;text=text.replace(old,new)
        path.write_text(text)
    source=folder/'harness.c';source.write_text('#include "pair.inc"\n'+(ROOT/'verif/render_history_harness.c').read_text())
    exe=folder/'cases.exe';built=compile_c([source],exe,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-DACTOR_VERIFY','-Wno-unused-function'])
    value=subprocess.run([str(exe)],capture_output=True,text=True)
    result=receipt(built['command'],[*inputs,ROOT/'verif/render_history_harness.c',ROOT/'verif/render_history_cases.py']+([mutant] if mutant else []),result='PASS' if not value.returncode else 'FAIL',stdout=value.stdout,stderr=value.stderr,returncode=value.returncode)
    return value,result
def main():
    value,result=run(OUT/'cases');save(OUT/'cases/result.json',result);print(value.stdout+value.stderr);assert not value.returncode
if __name__=='__main__':main()
