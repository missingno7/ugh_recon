"""Input-only gameplay witness with AdLib enabled; maintained gameplay is silent."""
import ctypes as C,sys
from pathlib import Path
from closure_support import ROOT,receipt,save
from adlx_effects_build import OUT,build
import contacts_reference
contacts_reference.OUT=OUT/'reference'
sys.path.insert(0,str(ROOT/'tools'))
import wholegame as w,nbuild
from emu import NativeVga

def main():
    plain=contacts_reference.prepare_reference(local=True);dll=nbuild.load_l1(build())
    path=ROOT/'verif/adlx_main_gameplay.txt';s=w.scenario(path)
    folder=OUT/'gameplay-adlib';folder.mkdir(parents=True,exist_ok=True)
    accelerator=NativeVga(folder);w.VGA_ACCELERATOR=accelerator
    try:
        machine,initial=w.fixture(s);frames,coverage,_=w.original(s,machine,initial)
        machine,initial=w.fixture(s);failure=w.native(s,machine,initial,dll,frames)
    finally:accelerator.close();w.VGA_ACCELERATOR=None
    assert not failure,failure
    assert set(s['requires'])<=set(coverage['routines'])
    audit=list((C.c_uint32*32).in_dll(dll,'adlx_effects_audit'))
    assert audit[16]>0 and not audit[17] and not audit[18]
    save(folder/'reference.json',dict(frames=frames,coverage=coverage))
    save(folder/'result.json',receipt(['python','verif/adlx_effects_scenario.py'],
        [Path(__file__),path,plain,ROOT/'verif/adlx_effects_build.py',ROOT/'tools/wholegame.py'],
        result='PASS',frames=len(frames),audit=audit))
    print('PASS gameplay AdLib:',len(frames),'boundaries;',audit[16],'native steps',flush=True)
if __name__=='__main__':main()
