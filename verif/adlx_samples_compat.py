"""Actual legacy L0/L1 suites, with both clean and poisoned ABI inputs."""
import json,subprocess,sys,shutil
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_samples_build import OUT
def main():
    rows=[]
    for poison in [False,True]:
        command=[sys.executable,'tools/difftest.py',*(['--poison'] if poison else [])]
        run=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(OUT/f'compat-{int(poison)}.log').write_text(run.stdout+run.stderr);print(run.stdout+run.stderr,flush=True)
        assert not run.returncode
        data=json.loads((ROOT/'build/c/difftest.json').read_text());assert data['passed']==data['total'];shutil.copyfile(ROOT/'build/c/difftest.json',OUT/f'compat-{int(poison)}.json')
        rows.append(dict(command=command,total=data['total'],passed=data['passed'],poison=poison))
    save(OUT/'compat.json',receipt([sys.executable,'verif/adlx_samples_compat.py'],[Path(__file__),ROOT/'tools/emu.py',ROOT/'tools/wholegame.py',ROOT/'tools/difftest.py'],result='PASS',runs=rows))
if __name__=='__main__':main()
