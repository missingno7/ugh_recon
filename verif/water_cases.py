"""Compiled actual-C finite water boundaries and generated states."""
import json,subprocess,time
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save
from water_build import OUT,pair
def main():
    folder=OUT/'cases';inputs=pair(folder);original=ROOT/'verif/water_harness.c';source=folder/'harness.c';source.write_text('#include "pair.inc"\n'+original.read_text());exe=folder/'cases.exe'
    built=compile_c([source],exe,[ROOT/'c',ROOT/'native',ROOT/'native/bridge'],['-DACTOR_VERIFY','-Wno-unused-function','-Wno-misleading-indentation']);start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
    save(folder/'result.json',receipt(built['command'],[*inputs,original,Path(__file__)],result='PASS' if not run.returncode else 'FAIL',seconds=time.perf_counter()-start,stdout=run.stdout,stderr=run.stderr));print(run.stdout+run.stderr,flush=True);assert not run.returncode
if __name__=='__main__':main()
