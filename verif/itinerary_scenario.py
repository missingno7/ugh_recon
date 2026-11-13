"""Extend the existing input-only passenger trace to witness departure in L0."""
import ctypes as C,json,sys
from pathlib import Path
from closure_support import ROOT,receipt,save
from itinerary_build import OUT,build,NAMES
import contacts_reference
contacts_reference.OUT=OUT/'reference'
sys.path.insert(0,str(ROOT/'tools'))
import wholegame as w,nbuild
from emu import NativeVga
def main():
    plain=contacts_reference.prepare_reference(local=True);dll=nbuild.load_l1(build());path=ROOT/'verif/itinerary_departure.txt'
    s=w.scenario(path);folder=OUT/'departure';folder.mkdir(parents=True,exist_ok=True)
    accelerator=NativeVga(folder);w.VGA_ACCELERATOR=accelerator
    try:
        machine,initial=w.fixture(s);key=w.identity(path,machine);ref=folder/'reference.json'
        saved=json.loads(ref.read_text()) if ref.exists() else {}
        if saved.get('key')==key:frames,coverage=saved['frames'],saved['coverage']
        else:
            frames,coverage,_=w.original(s,machine,initial)
            save(ref,dict(key=key,frames=frames,coverage=coverage))
        assert set(s['requires'])<=set(coverage['routines']),set(s['requires'])-set(coverage['routines'])
        machine,initial=w.fixture(s);failure=w.native(s,machine,initial,dll,frames)
    finally:accelerator.close();w.VGA_ACCELERATOR=None
    assert not failure,failure
    audit=list((C.c_uint32*16).in_dll(dll,'itinerary_audit'))
    assert audit[NAMES.index('BeginPassengerDeparture')]>0 and audit[NAMES.index('AnimatePassengerDeparture')]>0 and not any(audit[8:]),audit
    save(folder/'result.json',receipt(['python','verif/itinerary_scenario.py'],[Path(__file__),path,ROOT/'verif/itinerary_build.py',ROOT/'tools/wholegame.py',plain],
        result='PASS',frames=len(frames),audit=audit))
    print('PASS departure',len(frames),'boundaries; audit',audit,flush=True)
if __name__=='__main__':main()
