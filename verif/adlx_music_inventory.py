"""Known static incoming calls and all indirect target sets for this unit."""
import json,re,sys
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_music_build import OUT
NAMES=['C:StartMusicTrack','C:StopMusicTrack','C:SetMusicTrackVolume','SOUND:ScheduleMusicFade','SOUND:AdvanceMusicFade','SOUND:CancelMusicFade','SOUND:AdvanceGuardedSoundClock','SOUND:SilenceAdlibOperators']
def main():
    model=json.loads((ROOT/'metadata/program-model.json').read_text());source=(ROOT/'src/c/module.c').read_text();rows=[]
    for name in NAMES:
        r=model['routines'][name];address=r['address'];label=name.split(':')[1]
        direct=sorted({owner for site in model['sites'].values() if not site.get('indirect') and [address,'call'] in site.get('edges',[]) for owner in site.get('owners',[])})
        indirect=[n for n,v in model['indirect_sites'].items() if address in v.get('targets',[])]
        mentions=[dict(line=i,text=line.strip()) for i,line in enumerate(source.splitlines(),1) if re.search(r'\b'+label+r'\s*\(',line)]
        rows.append(dict(routine=name,address=address,static_callers=direct,model_callers=r['callers'],indirect_target_sites=indirect,src_C_mentions=mentions,API_only=not direct and not indirect))
    unused=[r['routine'] for r in rows if r['API_only']];assert unused==['SOUND:AdvanceGuardedSoundClock']
    assert not next(r for r in rows if r['API_only'])['src_C_mentions']
    save(OUT/'inventory.json',receipt([sys.executable,'verif/adlx_music_inventory.py'],[Path(__file__),ROOT/'metadata/program-model.json',ROOT/'src/c/module.c'],result='PASS',routines=rows,API_only=unused))
    for r in rows:print(r['routine'],'static',r['static_callers'],'indirect',r['indirect_target_sites'],'API_only',r['API_only'])
if __name__=='__main__':main()
