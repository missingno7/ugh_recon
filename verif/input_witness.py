"""Input-only two-player/two-joystick L0/native witness; unchanged harness."""
import sys,ctypes as C,tempfile,json
from pathlib import Path
from closure_support import ROOT,receipt,save
from input_build import OUT,build
sys.path.insert(0,str(ROOT/'tools'))
import contacts_reference,difftest,nbuild,wholegame
from emu import NativeVga
contacts_reference.OUT=OUT/'reference'

def main():
 plain=contacts_reference.prepare_reference(local=True);dll=nbuild.load_l1(build());counters=(C.c_uint32*16).in_dll(dll,'input_audit');s=wholegame.scenario(ROOT/'verif/input_two_joysticks.txt');folder=OUT/'witness';folder.mkdir(exist_ok=True)
 ledger=OUT/'witness-prior-edges.json';ledger.write_text('[]\n')
 class ReadRoot(type(ROOT)):
  def __truediv__(self,value):
   if str(value)=='build/link/plain/UGH.EXE':return plain
   if str(value)=='build/workers/c-close/call-edges.json':return ledger
   return super().__truediv__(value)
 wholegame.ROOT=ReadRoot(ROOT)
 with tempfile.TemporaryDirectory(prefix='vga-',dir=folder) as temp:
  accelerator=NativeVga(Path(temp));wholegame.VGA_ACCELERATOR=accelerator
  try:
   original,initial=wholegame.fixture(s);frames,coverage,_=wholegame.original(s,original,initial);assert set(s['requires'])<=set(coverage['routines']);candidate,initial=wholegame.fixture(s);failure=wholegame.native(s,candidate,initial,dll,frames);assert not failure,failure
  finally:accelerator.close();wholegame.VGA_ACCELERATOR=None
 assert counters[9] and counters[13],list(counters)
 state=dll.ugh_memory().contents;m=difftest.Machine();at=m.seg('DGROUP:PlayerCount')*16+m.off('DGROUP:PlayerCount');assert int.from_bytes(bytes(state[at:at+2]),'little')==2
 save(OUT/'witness.json',receipt([sys.executable,'verif/input_witness.py'],[Path(__file__),ROOT/'verif/input_two_joysticks.txt',ROOT/'verif/input_build.py',ROOT/'native/input.c',ROOT/'native/input.h',ROOT/'native/bridge/input_bridge.c',ROOT/'tools/wholegame.py',ROOT/'tools/emu.py',plain],result='PASS',frames=len(frames),counts=list(counters),coverage=coverage,scope='Input-only witness; no state/executable/asset patch. Not a maintained tests scenario.'))
 print('PASS two physical joystick mappings',len(frames),'frames',list(counters),flush=True)
if __name__=='__main__':main()
