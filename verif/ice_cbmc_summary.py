"""Validate accepted CBMC receipts and regenerate their C with current sources."""
import hashlib,json,subprocess
from pathlib import Path
import ice_cbmc
ROOT=ice_cbmc.ROOT;OUT=ice_cbmc.OUT
PROFILES=['final_whole_s16_o6_u17','final_whole_s32_o4_u17',
          'final_init_s16_o8_u17','final_step_s16_o8_u17',
          *[f'final_{name}_s8_o1_u17' for name in ('reader','bits','literal','length','offset')],
          'reach_whole_s16_o4_u17','negative_whole_s16_o2_u1']

def main():
    rows=[]
    for name in PROFILES:
        folder=OUT/name;receipt=json.loads((folder/'result.json').read_text())
        expected='WITNESSED' if name.startswith('reach') else 'FAIL' if name.startswith('negative') else 'PASS'
        assert receipt['result']==expected,(name,receipt['result'])
        if expected=='FAIL':assert any('unwind' in label for label,_ in receipt['failures'])
        replay=OUT/'replay'/name
        ice_cbmc.prepare(replay,mode=receipt['mode'])
        command=list(receipt['preprocess']);command[-3]=str(replay/'whole.c');command[-1]=str(replay/'whole.i')
        subprocess.run(command,check=True,capture_output=True)
        original=(folder/'whole.i').read_bytes();current=(replay/'whole.i').read_bytes()
        assert original==current,f'{name}: preprocessed C differs from current source'
        log=(folder/'cbmc.log').read_text()
        solver_times=ice_cbmc.re.findall(r'Runtime Solver: ([^\n]+)',log)
        decision_times=ice_cbmc.re.findall(r'Runtime decision procedure: ([^\n]+)',log)
        rows.append(dict(profile=name,result=expected,seconds=receipt['seconds'],
            solver_times=solver_times,decision_times=decision_times,command=receipt['command'],
            loop_unwinds=receipt['loop_unwinds'],stream=receipt['stream_size'],output=receipt['output_size'],
            iterations=receipt['token_bound'],preprocessed_sha256=hashlib.sha256(original).hexdigest(),current_C_identical=True))
    defects=json.loads((OUT/'defects.json').read_text())
    for name,row in defects.items():
        assert row['primitive']['result']=='FAIL'
        assert any('primitive' in desc for _,desc in row['primitive']['failures']),(name,'not an observation counterexample')
    summary=dict(profiles=rows,defects={k:dict(primitive=v['primitive']['result'],whole=v['whole']['result']) for k,v in defects.items()},
        tools=json.loads((ROOT/'metadata/verif-tools.json').read_text()))
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(f'{len(rows)} current-source receipts validated; five primitive counterexamples validated')
if __name__=='__main__':main()
