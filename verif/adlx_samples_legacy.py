"""Certify unchanged whole-game records against the pre-SB references."""
import json,sys
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_samples_build import OUT
def main():
    result=json.loads((ROOT/'build/whole/last-run.json').read_text());assert result['passed'] and len(result['scenarios'])==20
    rows=[];inputs=[Path(__file__),ROOT/'tools/wholegame.py',ROOT/'tools/emu.py',ROOT/'build/whole/last-run.json']
    for scenario in sorted((ROOT/'tests/scenarios').glob('*.txt')):
        old=OUT/'pre-sb-references'/f'{scenario.stem}.ref.json';new=ROOT/'build/whole'/old.name
        before=json.loads(old.read_text());after=json.loads(new.read_text());assert before['frames']==after['frames'],scenario.stem
        assert before['coverage']==after['coverage'],scenario.stem
        rows.append(dict(scenario=scenario.stem,boundaries=len(after['frames']),records_unchanged=True,coverage_unchanged=True));inputs.extend([old,new,scenario])
    save(OUT/'legacy.json',receipt([sys.executable,'tools/wholegame.py'],inputs,result='PASS',scenarios=rows,reference_identity='Tool source keys intentionally change; all frame/terminal observations and code coverage are byte-for-byte equal as JSON values. No scenario input was changed.'))
    print('PASS20 unchanged frame/terminal records and coverage inventories')
if __name__=='__main__':main()
