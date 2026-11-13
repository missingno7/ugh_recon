"""Record the missing game-input section path without fabricating a witness."""
import json,sys
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_sections_build import OUT
def main():
    model=json.loads((ROOT/'metadata/program-model.json').read_text())
    scan=model['routines']['C:ScanMusicEvents'];flag=model['variables']['MainAdlxSectionLoopEnabled']
    integration=json.loads((OUT/'integration.json').read_text());rows={r['scenario']:r for r in integration['section_scenarios']};observed=[]
    for name in ['adlib','gameplay-adlib']:
        row=rows[name];reference=json.loads((OUT/'whole'/f'{name}.ref.json').read_text());routines=reference['coverage']['routines']
        assert row['counts'][0]==row['counts'][1]==row['counts'][8]==0
        assert row['counts'][2]>0
        assert 'C:ScanMusicEvents' not in routines and 'C:ApplyScannedMusicEvents' not in routines
        observed.append(dict(scenario=name,scan=row['counts'][0],apply=row['counts'][1],tick=row['counts'][2],scheduler_apply=row['counts'][8]))
    assert scan['callers']==[]
    result=receipt([sys.executable,'verif/adlx_sections_reachability.py'],[Path(__file__),ROOT/'metadata/program-model.json',ROOT/'c/sound_api.c',ROOT/'c/adlib.c',ROOT/'src/asm/SOUND.ASM',ROOT/'tests/scenarios/adlib.txt',ROOT/'tests/scenarios/gameplay-adlib.txt',OUT/'integration.json'],
        result='GAP_RECORDED',known_scan_callers=scan['callers'],known_flag_writers=flag['writers'],writer_analysis_complete=flag['complete'],observed=observed,
        limitation='No justified normal game-input path to the sole known section-enabling API. The model is not a mathematical whole-program alias/unreachability proof. No input-only positive witness is claimed or fabricated.')
    save(OUT/'reachability.json',result);print(json.dumps(result['observed']),flush=True)
if __name__=='__main__':main()
