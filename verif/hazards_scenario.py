"""Additional Dino species witness; no gameplay state patches."""
import ctypes as C,json,sys
from pathlib import Path
from closure_support import ROOT,receipt,save
from hazards_build import OUT,build,NAMES
import contacts_reference
contacts_reference.OUT=OUT/'reference'
from contacts_reference import prepare_reference
sys.path.insert(0,str(ROOT/'tools'))
import wholegame as w,nbuild
from emu import NativeVga

def main():
    prepare_reference(local=True);dll=nbuild.load_l1(build());path=ROOT/'verif/hazards_dino.txt'
    s=w.scenario(path);folder=OUT/'dino';folder.mkdir(parents=True,exist_ok=True)
    accelerator=NativeVga(folder);w.VGA_ACCELERATOR=accelerator
    try:
        machine,initial=w.fixture(s);frames,coverage,_=w.original(s,machine,initial)
        machine,initial=w.fixture(s);failure=w.native(s,machine,initial,dll,frames)
    finally:accelerator.close();w.VGA_ACCELERATOR=None
    assert not failure,failure
    assert set(s['requires'])<=set(coverage['routines'])
    audit=list((C.c_uint32*64).in_dll(dll,'hazards_audit'))
    assert audit[NAMES.index('UpdateDinoForce')]>0 and not any(audit[32:]),audit
    save(folder/'reference.json',dict(frames=frames,coverage=coverage))
    save(folder/'result.json',receipt(['python','verif/hazards_scenario.py'],[Path(__file__),path,ROOT/'verif/hazards_build.py',ROOT/'tools/wholegame.py'],result='PASS',frames=len(frames),audit=audit))
    print('PASS Dino',len(frames),'boundaries; force steps',audit[NAMES.index('UpdateDinoForce')])
if __name__=='__main__':main()
