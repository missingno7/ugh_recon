"""Compiled actual-C scan domain and existing ICE control-byte/token domains."""
import ctypes as C,sys
from pathlib import Path
from closure_support import ROOT,function,compile_c,receipt,save
from pictures_build import OUT
import pictures_proofs

def main():
 negative='--negative' in sys.argv;folder=OUT/('enumeration-negative' if negative else 'enumeration');folder.mkdir(parents=True,exist_ok=True);rows={}
 def compile_property(harness,ignored,inputs,**options):
  code=harness.read_text().replace('#define CHECK(c,m) __CPROVER_assert(c,m)','#define CHECK(c,m) do {if(!(c)) failed=1;} while(0)')
  code=code.replace('uint8_t nondet_u8(void);','static int failed;uint8_t nondet_u8(void);',1);code=code.replace(function(code,'main').rstrip(),'')
  code+='EXPORT unsigned enumerate(void) {for(unsigned value=0;value<65536;value++) {Regs r={0};r.ax=(uint16_t)value;r.flags=0xed7;Regs s=r;CHECK(reference(&r)==actual(&s),"status");equal(r,s);if(failed) return value;}return 65536;}\n'
  path=folder/'input.c';path.write_text(code);dllpath=folder/'input.dll';built=compile_c([path],dllpath,[ROOT/'c',ROOT/'native'],['-shared','-Wno-unused-function']);dll=C.CDLL(str(dllpath));dll.enumerate.restype=C.c_uint;count=dll.enumerate();assert count<65536 if negative else count==65536
  rows['scan_and_stale_high_byte']=count;save(folder/'input.json',receipt([sys.executable,'verif/pictures_enumerate.py',*sys.argv[1:]],inputs,result='PASS',cases=count,negative_detected=negative,build=built));return dict(result='FAIL' if negative else 'PASS',seconds=0,failures=[])
 previous=pictures_proofs.cbmc;arguments=sys.argv;pictures_proofs.cbmc=compile_property;sys.argv=['pictures_proofs.py','input',*(['--negative'] if negative else [])]
 try:pictures_proofs.main()
 finally:pictures_proofs.cbmc=previous;sys.argv=arguments
 import contacts_reference
 contacts_reference.OUT=OUT/'reference';plain=contacts_reference.prepare_reference(local=True)
 import ice_evidence
 ice_evidence.OUT=folder/'ice';ice_evidence.OUT.mkdir(parents=True,exist_ok=True)
 if negative:
  original=(ROOT/'native/ice.c').read_text();changed=original.replace('return bases[kind]+take_bits(reader,widths[kind]);','return bases[kind]+1+take_bits(reader,widths[kind]);');assert changed!=original
  changed=changed.replace('#include "ice.h"',f'#include "{(ROOT/"native/ice.h").as_posix()}"');mutant=folder/'ice-length-mutant.c';mutant.write_text(changed);rows['ice_service_mutant']=ice_evidence.primitives(mutant);assert rows['ice_service_mutant']['detected']
 else:
  rows['ice_primitives']=ice_evidence.primitives();rows['ice_one_token_domain']=ice_evidence.bounded()
 save(OUT/('enumeration-negative.json' if negative else 'enumeration.json'),receipt([sys.executable,'verif/pictures_enumerate.py',*sys.argv[1:]],[Path(__file__),ROOT/'verif/pictures_proofs.py',ROOT/'native/pictures.c',ROOT/'native/pictures.h',ROOT/'native/ice.c',ROOT/'native/ice.h',ROOT/'c/ice.c',ROOT/'native/bridge/ice_bridge.c',ROOT/'verif/ice_evidence.py',ROOT/'verif/ice_primitives.c',plain],result='PASS',domains=rows,negative_detected=negative))
 print('PASS picture input and ICE enumeration',rows,flush=True)
if __name__=='__main__':main()
