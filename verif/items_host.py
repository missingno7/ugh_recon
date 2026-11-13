"""Host review build with falling_items selected as if promoted to migrated.

Only the supervisor promotes certificate.status. This read-only overlay tests
that future selection without modifying its administrative status or c/.
"""
import json,re,subprocess,sys
from closure_support import ROOT,receipt,save
from items_build import OUT
sys.path.insert(0,str(ROOT/'tools'))
import hostbuild

def main():
    def selection(literal=False):
        if literal:return []
        units=[]
        for path in sorted((ROOT/'metadata/closure').glob('*.json')):
            cert=json.loads(path.read_text());status='migrated' if path.stem=='falling_items' else cert['status']
            if status not in hostbuild.STATUS_ORDER or hostbuild.STATUS_ORDER.index(status)<3:continue
            files=cert['native']['files']
            native=[ROOT/f for f in files if f.startswith('native/') and '/bridge/' not in f and f.endswith('.c')]
            bridges=[ROOT/f for f in files if f.startswith('native/bridge/') and f.endswith('.c')]
            assert len(native)==len(bridges)==1
            bridge=bridges[0]
            exports=sorted(set(re.findall(r'\bEXPORT\s+int\s+(c_[A-Za-z0-9_]+)\s*\(',bridge.read_text())))
            # level_view is a library dependency, not an L1 endpoint replacement.
            # Current hostbuild rejects empty exports; the read-only overlay
            # includes both sources and simply performs no endpoint renaming.
            units.append(dict(component=cert['component'],status=status,native=native[0],bridge=bridge,exports=exports))
        return units
    hostbuild.selected_units=selection
    # The maintained L1/generated headers are already tested and read_symbols
    # validates their rebuilt coordinates. Never regenerate protected c/.
    hostbuild.cgen.generate=lambda:None
    hostbuild.build()
    command=[sys.executable,str(ROOT/'host/check.py'),'--variant','native']
    run=subprocess.run(command,text=True)
    assert run.returncode==0
    result=json.loads((ROOT/'build/workers/host-native/host-check-native.json').read_text())
    pickups=[]
    for kind in ['multiplier','timer']:
        script=OUT/f'items-{kind}.txt'
        reference=json.loads((OUT/f'pickup-{kind}/reference.json').read_text())['frames']
        command=[str(ROOT/'build/host/ugh.exe'),'--headless',str(len(reference)),'--script',str(script),'--timeout','90']
        run=subprocess.run(command,capture_output=True,text=True,timeout=95,cwd=ROOT)
        frames=[json.loads(line) for line in run.stdout.splitlines()]
        assert run.returncode==0 and frames==reference,(kind,run.stderr)
        pickups.append(dict(kind=kind,frames=len(frames),result='PASS'))
        print('PASS host pickup',kind,len(frames),'frames',flush=True)
    save(OUT/'host.json',receipt(['python','verif/items_host.py'],[__file__,ROOT/'tools/hostbuild.py',ROOT/'host/check.py',ROOT/'metadata/closure/falling_items.json'],
        result='PASS',selection='read-only migrated overlay plus projection-library support; administrative certificate unchanged',
        build=json.loads((ROOT/'build/host/hostbuild.json').read_text()),check=result,pickups=pickups))

if __name__=='__main__':main()
