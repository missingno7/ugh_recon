"""Static sample callers and dynamic proof of the pre-probe broken hook."""
import json,sys,ctypes as C
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_samples_build import OUT,build
sys.path.insert(0,str(ROOT/'tools'))
import difftest,nbuild
from emu import SoundBlaster
def main():
    import contacts_reference
    contacts_reference.OUT=OUT/'reference';contacts_reference.prepare_reference(local=True)
    model=json.loads((ROOT/'metadata/program-model.json').read_text());rows=[]
    for name in ['C:LoadIffSample','SOUND:ResetSampleVoiceCursor','SOUND:MixSampleVoicePairs']:
        address=model['routines'][name]['address'];callers=sorted({owner for site in model['sites'].values() if not site.get('indirect') and [address,'call'] in site.get('edges',[]) for owner in site.get('owners',[])})
        indirect=[n for n,v in model['indirect_sites'].items() if address in v.get('targets',[])];rows.append(dict(name=name,address=address,static_callers=callers,indirect_sites=indirect,API_only=not callers and not indirect))
    m=difftest.Machine();m.device.sb=SoundBlaster();m.device.sb.install(m.device)
    initial=m.prepare('SOUND:ProbeSoundBlasterDmaIrq',dict(DX=0x22e),kind='far',flags=0x202)
    try:m.run(10000);raise AssertionError('broken hook unexpectedly returned')
    except RuntimeError as error:diagnostic=str(error)
    assert m.reg('CS')==m.seg('GAME:loc_001F') and m.reg('IP') in (0x1f19,0x1f1a),(diagnostic,m.reg('CS'),m.reg('IP'))
    assert not any(event[0] in (1,2) and 0x200<=event[1]<=0x26f for event in m.device.log)
    save(OUT/'inventory.json',receipt([sys.executable,'verif/adlx_samples_inventory.py'],[Path(__file__),ROOT/'metadata/program-model.json',ROOT/'src/asm/GAME.ASM',ROOT/'src/asm/SOUND.ASM',ROOT/'c/dsp.c',ROOT/'tools/emu.py'],result='PASS',routines=rows,audio_owned_after_proposal=57,audio_remaining=18,barrier=dict(diagnostic=diagnostic,landing=f'{m.reg("CS"):04x}:{m.reg("IP"):04x}',pre_DSP_ports=True,scope='Direct original API entry on an SB-equipped fixture; no RET rewrite, fallback or game-state repair.'),shipped_startup='GAME:InitializeAdLibSound always PUSH1 before InitializeSoundSystem; no DSP configuration input exists in shipped startup.',resource_barrier='No embedded FORM/8SVX. External bank hooks001C/001D are also near RET with a far caller.'))
    print(json.dumps(rows,indent=2));print('PASS original probe stops before any DSP port at broken GAME landing',diagnostic)
if __name__=='__main__':main()
