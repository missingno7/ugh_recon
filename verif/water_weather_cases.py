import subprocess
from closure_support import ROOT,compile_c,receipt,save
from water_weather_build import OUT
from water_weather_pair import pair
def run(folder,mutation=None):
    inputs=pair(folder,contract_pixels=True);source=folder/'harness.c';source.write_text((ROOT/'verif/water_weather_harness.c').read_text())
    if mutation:
        old,new=mutation;native=(ROOT/'native/water_weather.c').read_text();assert old in native
        changed=folder/'mutant.c';changed.write_text(native.replace(old,new,1));inputs.append(changed)
        inc=folder/'pair.inc';inc.write_text(inc.read_text().replace((ROOT/'native/water_weather.c').as_posix(),changed.as_posix()))
    built=compile_c([source],folder/'cases.exe',[ROOT/'c',ROOT/'native'],['-DACTOR_VERIFY','-Wno-misleading-indentation','-Wno-unused-function','-Wno-unused-variable'])
    run=subprocess.run([str(folder/'cases.exe')],capture_output=True,text=True,timeout=600)
    record=receipt(built['command'],[*inputs,ROOT/'verif/water_weather_harness.c',ROOT/'verif/water_weather_cases.py'],result='PASS' if not run.returncode else 'FAIL',stdout=run.stdout,stderr=run.stderr,returncode=run.returncode);save(folder/'result.json',record);return run,record
def main():
    result,_=run(OUT/'cases');print(result.stdout+result.stderr,flush=True);assert not result.returncode
if __name__=='__main__':main()
