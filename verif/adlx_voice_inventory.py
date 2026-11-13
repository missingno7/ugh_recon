"""After-facade audio inventory, static/indirect callers and remaining L1 bodies."""
import json,re,sys
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_voice_build import OUT
NAMES=['SetAdlibChannelVolume','SetAdlibChannelGain','KeyOffAdlibChannel','SetAdlibFrequency','LoadAdlibInstrument','WriteAdlibRegister','DelaySoundIo']
GROUPS={
 'AdLib lifetime/reset/calibration': ['SOUND:ClearSoundState','SOUND:InitializeAdlibPlayback','SOUND:ShutdownAdlibPlayback','SOUND:CalibrateSoundDelay','SOUND:BeginSoundDelayMeasurement','SOUND:FinishSoundDelayMeasurement'],
 'Top sound facade/bank/duration': ['C:InitializeSoundSystem','C:ShutdownSoundSystem','C:StartSoundOutputs','C:StopSoundChannel','C:LoadSoundBankResource','C:LoadBankSoundByIndex','C:GetMusicTrackDuration'],
 'Sample import': ['C:LoadIffSample'],
 'DSP protocol/probe/lifetime': ['SOUND:WriteSoundBlasterDsp','SOUND:ResetSoundBlasterDsp','SOUND:SetDspSampleRate','SOUND:ProbeSoundBlasterDmaIrq','SOUND:HandleDspProbeInterrupt','SOUND:InitializeDspPlayback','SOUND:ShutdownDspPlayback'],
 'Sample/mixer/DMA': ['SOUND:ResetSampleVoiceCursor','SOUND:MixSampleVoicePairs','SOUND:LocateDmaMixBuffers','SOUND:StartDmaSampleBlock','SOUND:PrimeSampleDmaPlayback','SOUND:HandleSampleDmaInterrupt']}
def main():
    model=json.loads((ROOT/'metadata/program-model.json').read_text());audio=set(model['components']['audio']['routines']);owners={};inputs=[Path(__file__),ROOT/'metadata/program-model.json',ROOT/'src/c/module.c']
    statuses={'migrated','verified-under-assumptions','verified-within-contract','integration-validated'}
    for p in sorted((ROOT/'metadata/closure').glob('*.json')):
        c=json.loads(p.read_text())
        if c['status'] not in statuses:continue
        for f in c['native']['files']:
            if f.startswith('native/bridge/') and f.endswith('.c'):
                exports=set(re.findall(r'\bEXPORT\s+int\s+c_(\w+)\s*\(',(ROOT/f).read_text()))
                if any(n.split(':')[1] in exports for n in audio):inputs.extend([p,ROOT/f])
                for n in audio:
                    if n.split(':')[1] in exports:owners[n]=c['component']
    for n in NAMES:owners['SOUND:'+n]='adlx_voice (proposed)'
    inputs.append(ROOT/'native/bridge/adlx_voice_bridge.c')
    remaining=sorted(audio-set(owners));grouped=[n for names in GROUPS.values() for n in names]
    assert len(audio)==75 and len(owners)==48 and len(remaining)==27 and set(remaining)==set(grouped) and len(grouped)==len(set(grouped))
    source=(ROOT/'src/c/module.c').read_text();rows=[]
    for label in NAMES:
        name='SOUND:'+label;address=model['routines'][name]['address']
        static=sorted({owner for site in model['sites'].values() if not site.get('indirect') and [address,'call'] in site.get('edges',[]) for owner in site.get('owners',[])})
        indirect=[n for n,v in model['indirect_sites'].items() if address in v.get('targets',[])]
        rows.append(dict(routine=name,address=address,static_callers=static,indirect_target_sites=indirect,model_callers=model['routines'][name]['callers'],outside_audio=[n for n in static if n not in audio],still_L1_callers=[n for n in static if n not in owners],API_only=not static and not indirect,source_C_mentions=[dict(line=i,text=line.strip()) for i,line in enumerate(source.splitlines(),1) if re.search(r'\b'+label+r'\s*\(',line)]))
    assert not any(r['outside_audio'] or r['API_only'] for r in rows)
    save(OUT/'inventory.json',receipt([sys.executable,'verif/adlx_voice_inventory.py'],inputs,result='PASS',audio_count=75,proposed_native_entries=48,remaining_count=27,owners=owners,routines=rows,groups={k:dict(count=len(v),routines=v) for k,v in GROUPS.items()},scope='Canonical entries with migrated ownership, not deletion of retained compatibility bodies. Direct callers exclude indirect sites; all indirect target sets checked. TIMER/DOS/external hooks outside audio75 are not counted.'))
    print('Audio75:48 owned after proposal,27 remaining')
    for r in rows:print(r['routine'],'outside_audio',r['outside_audio'],'still L1',r['still_L1_callers'],'API_only',r['API_only'])
if __name__=='__main__':main()
