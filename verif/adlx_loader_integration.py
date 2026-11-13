"""Reuse the independent L0 audio/scenario gate with this combined DLL."""
import sys,ctypes as C,json
from pathlib import Path
from closure_support import receipt,save
import adlx_effects_integration as integration
from adlx_loader_build import OUT,build
import adlx_effects_cases,adlx_allocation_cases,adlx_loader_cases
adlx_effects_cases.CASES=[*adlx_effects_cases.CASES,*adlx_allocation_cases.CASES,*adlx_loader_cases.CASES]
integration.OUT=OUT;integration.build=build;integration.contacts_reference.OUT=OUT/'reference'
def main():
    loaded=[];original=integration.nbuild.load_l1
    def tracked(*args,**kwargs):
        dll=original(*args,**kwargs);loaded.append(dll);return dll
    integration.nbuild.load_l1=tracked
    status=integration.main()
    result=json.loads((OUT/'integration.json').read_text())
    result['allocation_audit']=list((C.c_uint32*16).in_dll(loaded[0],'adlx_allocation_audit'))
    result['loader_audit']=list((C.c_uint32*16).in_dll(loaded[0],'adlx_loader_audit'))
    result['allocation_inputs']=receipt([sys.executable,'verif/adlx_loader_integration.py',*sys.argv[1:]],
        [Path(__file__),Path(adlx_allocation_cases.__file__),Path(adlx_loader_cases.__file__)])
    save(OUT/'integration.json',result);print('allocation audit:',result['allocation_audit'],flush=True);print('loader audit:',result['loader_audit'],flush=True)
    return status
if __name__=='__main__':raise SystemExit(main())
