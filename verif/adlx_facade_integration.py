"""Direct L0 suites and all maintained scenarios through the combined audio DLL."""
import sys,ctypes as C,json
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_facade_build import OUT,build
import adlx_effects_integration as integration
import adlx_effects_cases,adlx_allocation_cases,adlx_loader_cases,adlx_sections_cases,adlx_music_cases,adlx_voice_cases,adlx_samples_cases
adlx_effects_cases.CASES=[*adlx_effects_cases.CASES,*adlx_allocation_cases.CASES,*adlx_loader_cases.CASES,*adlx_sections_cases.CASES,*adlx_music_cases.CASES,*adlx_voice_cases.CASES,*adlx_samples_cases.CASES]
integration.OUT=OUT;integration.build=build;integration.contacts_reference.OUT=OUT/'reference'
def main():
    import wholegame
    observed=[];previous=wholegame.native
    def native(*args,**kwargs):
        scenario,dll=args[0],args[3];audit=(C.c_uint32*16).in_dll(dll,'adlx_facade_audit');before=list(audit)
        result=previous(*args,**kwargs);observed.append(dict(scenario=scenario['name'],counts=[audit[i]-before[i] for i in range(16)]));return result
    wholegame.native=native
    status=integration.main();result=json.loads((OUT/'integration.json').read_text());result['facade_scenarios']=observed
    result['facade_inputs']=receipt([sys.executable,'verif/adlx_facade_integration.py',*sys.argv[1:]],[Path(__file__),ROOT/'verif/adlx_samples_cases.py',ROOT/'verif/adlx_facade_build.py'])
    save(OUT/'integration.json',result);save(OUT/'facade-integration.json',result)
    for row in observed:print(row,flush=True)
    return status
if __name__=='__main__':raise SystemExit(main())
