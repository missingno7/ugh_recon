"""A real under-unwound history sequence must fail its unwind assertion."""
from closure_support import ROOT
from render_history_build import OUT
from render_history_sequences import make
from render_history_limits import cbmc,SMT
def main():
    folder=OUT/'negative-bound';folder.mkdir(parents=True,exist_ok=True);code,inputs=make('pages',folder);source=folder/'harness.c';source.write_text(code)
    result=cbmc(source,folder,inputs,unwind=1,timeout=120,defines=['-D__CPROVER__','-DACTOR_VERIFY','-DUINT16_MAX=65535u'],extra=SMT)
    print(result['result'],result['failures']);assert result['result']=='FAIL' and any('unwind' in n for n,m in result['failures'])
if __name__=='__main__':main()
