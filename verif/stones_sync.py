"""Check actual native stone/hazard borrowing and same-frame publication."""
import subprocess
from pathlib import Path
from closure_support import ROOT,compile_c,receipt,save
from stones_build import OUT
def main():
    folder=OUT/'sync';folder.mkdir(parents=True,exist_ok=True);exe=folder/'sync.exe'
    inputs=[ROOT/'verif/stones_sync.c',*[ROOT/'native'/name for name in ['stones.c','hazards.c','contacts.c','actor_resources.c','level_view.c']]]
    built=compile_c(inputs,exe,[ROOT/'native']);run=subprocess.run([str(exe)],capture_output=True,text=True)
    save(folder/'result.json',receipt(built['command'],[*inputs,Path(__file__),*sorted((ROOT/'native').glob('*.h'))],
        result='PASS' if not run.returncode else 'FAIL',execution=[str(exe)],stdout=run.stdout,stderr=run.stderr))
    print(run.stdout+run.stderr,flush=True);assert not run.returncode
if __name__=='__main__':main()
