"""Remaining18 audio entries: static/indirect callers and maintained scenario reach."""
import sys,json,re
from pathlib import Path
from closure_support import ROOT,receipt,save
OUT=ROOT/'build/workers/close-adlx-10'
REMAINING=['C:InitializeSoundSystem','C:ShutdownSoundSystem','C:StartSoundOutputs','C:StopSoundChannel','C:LoadSoundBankResource','C:LoadBankSoundByIndex','C:GetMusicTrackDuration','SOUND:WriteSoundBlasterDsp','SOUND:ResetSoundBlasterDsp','SOUND:SetDspSampleRate','SOUND:ProbeSoundBlasterDmaIrq','SOUND:HandleDspProbeInterrupt','SOUND:InitializeDspPlayback','SOUND:ShutdownDspPlayback','SOUND:LocateDmaMixBuffers','SOUND:StartDmaSampleBlock','SOUND:PrimeSampleDmaPlayback','SOUND:HandleSampleDmaInterrupt']
def main():
    OUT.mkdir(parents=True,exist_ok=True);model=json.loads((ROOT/'metadata/program-model.json').read_text());rows=[]
    reference_folder=OUT/'whole' if len(list((OUT/'whole').glob('*.ref.json')))==20 else ROOT/'build/whole'
    references=[p for p in reference_folder.glob('*.ref.json') if (ROOT/'tests/scenarios'/f'{p.name.split(".")[0]}.txt').exists()]
    assert len(references)==20
    for name in REMAINING:
        address=model['routines'][name]['address'];callers=sorted({owner for site in model['sites'].values() if not site.get('indirect') and [address,'call'] in site.get('edges',[]) for owner in site.get('owners',[])})
        indirect=[n for n,v in model['indirect_sites'].items() if address in v.get('targets',[])]
        scenarios=[p.name.split('.')[0] for p in references if name in json.loads(p.read_text())['coverage']['routines']]
        api=not callers and not indirect
        group='facade' if name in ['C:InitializeSoundSystem','C:ShutdownSoundSystem','C:StartSoundOutputs','C:GetMusicTrackDuration'] else 'digital'
        rows.append(dict(name=name,address=address,static_callers=callers,indirect_sites=indirect,scenarios=scenarios,API_only=api,installed_interrupt_identity=name in ['SOUND:HandleDspProbeInterrupt','SOUND:HandleSampleDmaInterrupt'],group=group))
    audio=set(model['components']['audio']['routines']);covered=set();certificates={}
    for certificate in (ROOT/'metadata/closure').glob('*.json'):
        original=json.dumps(json.loads(certificate.read_text())['original']);entries={n for n in audio if re.search(r'(?<!\w)'+re.escape(n)+r'(?!\w)',original)}
        if entries:certificates[certificate.stem]=len(entries);covered|=entries
    save(OUT/'inventory.json',receipt([sys.executable,'verif/adlx_facade_inventory.py'],[Path(__file__),ROOT/'metadata/program-model.json',*references],result='PASS',audio_component_count=len(audio),covered_audio_entries=len(covered),missing_audio_entries=sorted(audio-covered),certificate_entries=certificates,routines=rows,facade_count=sum(r['group']=='facade' for r in rows),digital_count=sum(r['group']=='digital' for r in rows),barriers=['InitializeAdLibSound always requests1','No shipped sample resource or implemented bank hook','DSP probe far CALL returns through lone near RET']))
    for row in rows:print(row['name'],row['group'],'API',row['API_only'],'callers',row['static_callers'],'scenarios',row['scenarios'])
if __name__=='__main__':main()
