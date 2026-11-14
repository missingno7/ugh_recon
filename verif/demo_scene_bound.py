"""An under-unwound actual native branch walk must fail, not truncate."""
from closure_support import ROOT
from demo_scene_build import OUT
from demo_scene_kernel import make
from demo_scene_limits import cbmc
def main():
    folder=OUT/'negative-bound';folder.mkdir(parents=True,exist_ok=True);code,inputs=make('dependence',folder);source=folder/'harness.c';source.write_text(code)
    result=cbmc(source,folder,inputs,unwind=1,timeout=120,defines=['-D__CPROVER__','-DACTOR_VERIFY'],extra=['--no-array-field-sensitivity'])
    print(result['result'],result['failures']);assert result['result']=='FAIL' and any('demo_presentation_next' in n and 'unwind' in n for n,m in result['failures'])
if __name__=='__main__':main()
