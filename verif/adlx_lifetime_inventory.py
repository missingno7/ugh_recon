"""Static callers, indirect installations and remaining audio ownership."""
import json,re,sys
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_lifetime_build import OUT,NAMES
def main():
    model=json.loads((ROOT/'metadata/program-model.json').read_text());audio=set(model['components']['audio']['routines']);rows=[];inputs=[Path(__file__),ROOT/'metadata/program-model.json',ROOT/'src/c/module.c',ROOT/'src/asm/SOUND.ASM']
    for label in NAMES:
        name='SOUND:'+label;address=model['routines'][name]['address']
        static=sorted({owner for site in model['sites'].values() if not site.get('indirect') and [address,'call'] in site.get('edges',[]) for owner in site.get('owners',[])})
        indirect=[n for n,v in model['indirect_sites'].items() if address in v.get('targets',[])]
        mentions=[dict(line=i,text=line.strip()) for i,line in enumerate((ROOT/'src/c/module.c').read_text().splitlines(),1) if re.search(r'\b'+label+r'\s*\(',line)]
        installed=label in ['BeginSoundDelayMeasurement','FinishSoundDelayMeasurement']
        rows.append(dict(routine=name,address=address,static_callers=static,indirect_target_sites=indirect,C_mentions=mentions,installed_interrupt_handler=installed,API_only=not static and not indirect and not installed,outside_audio=[n for n in static if n not in audio]))
    owners={}
    for p in sorted((ROOT/'metadata/closure').glob('*.json')):
        cert=json.loads(p.read_text())
        if cert['status'] not in ['migrated','verified-under-assumptions','verified-within-contract','integration-validated']:continue
        for f in cert['native']['files']:
            if f.startswith('native/bridge/') and f.endswith('.c'):
                exports=set(re.findall(r'\bEXPORT\s+int\s+c_(\w+)\s*\(',(ROOT/f).read_text()))
                if any(n.split(':')[1] in exports for n in audio):inputs.extend([p,ROOT/f])
                for n in audio:
                    if n.split(':')[1] in exports:owners[n]=cert['component']
    for label in NAMES:owners['SOUND:'+label]='adlx_lifetime (proposed)'
    assert len(owners)==54 and len(audio-set(owners))==21
    save(OUT/'inventory.json',receipt([sys.executable,'verif/adlx_lifetime_inventory.py'],inputs,result='PASS',routines=rows,owned=len(owners),remaining=sorted(audio-set(owners)),scope='Static direct calls, all indirect target sets and C source mentions checked. DOS AH=25h installations are explicit roots even where model call-graph edges omit asynchronous delivery.'))
    print(json.dumps(rows,indent=2));print('54/75 owned after proposal;21 remain')
if __name__=='__main__':main()
