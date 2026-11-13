"""Negative control on the actual looping frame helper, not a model loop."""
from pathlib import Path
from closure_support import ROOT
from water_build import OUT
from water_scalar import make
from water_limits import cbmc,SMT
def main():
    folder=OUT/'negative-bound';folder.mkdir(parents=True,exist_ok=True);code,inputs=make('frame','outputs',folder);source=folder/'harness.c';source.write_text(code)
    result=cbmc(source,folder,[*inputs,Path(__file__)],unwind=40,timeout=180,defines=['-D__CPROVER__','-DACTOR_VERIFY','-DUINT16_MAX=65535u','-DGENERAL_FRAME'],extra=[*SMT,'--no-array-field-sensitivity','--unwindset','wa_ref_actor_frame.0:1,water_shell_actor_frame.0:1'])
    print(result['result'],result['seconds'],result['failures'],flush=True);assert result['result']=='FAIL' and any(n in ('wa_ref_actor_frame.unwind.0','water_shell_actor_frame.unwind.0') for n,m in result['failures'])
if __name__=='__main__':main()
