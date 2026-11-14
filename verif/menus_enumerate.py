"""Compile the actual-C property cuts and enumerate their small domains."""
import ctypes as C,sys
from pathlib import Path
from closure_support import ROOT,function,compile_c,receipt,save
from menus_build import OUT
import menus_proofs

def main():
 negative='--negative' in sys.argv;rows={};original_argv=sys.argv
 entries=['selector'] if negative else ['centering','mutators','control','selector','editor']
 for entry in entries:
  folder=OUT/f'menus-enumeration-{entry}{"-negative" if negative else ""}';folder.mkdir(parents=True,exist_ok=True)
  def compile_property(harness,ignored,inputs,**options):
   code=harness.read_text().replace('#define CHECK(c,m) __CPROVER_assert(c,m)','#define CHECK(c,m) do {if(!(c)) failed=1;} while(0)')
   code=code.replace('uint8_t nondet_u8(void);','static int failed;uint8_t nondet_u8(void);',1);main_body=function(code,'main');code=code.replace(main_body.rstrip(),'')
   if entry=='centering':
    expected=131072;body='for(unsigned value=0;value<65536;value++) for(unsigned kind=0;kind<2;kind++) {Regs r={0};r.bp=(uint16_t)value;r.flags=0xed7;Regs s=r;if(kind) {ref_line(&r);actual_line(&s);}else {ref_credits(&r);actual_credits(&s);}equal(r,s);if(failed) return count;count++;}'
   elif entry=='mutators':
    expected=131072;body='for(unsigned value=0;value<65536;value++) for(unsigned kind=0;kind<2;kind++) {memory[0].players=(uint16_t)value;memory[0].bytes=0xa55a;memory[0].difficulty=(uint16_t)value;memory[1]=memory[0];Regs r={0};r.flags=0xed7;Regs s=r;side=0;if(kind) ref_players(&r);else ref_difficulty(&r);side=1;if(kind) native_players(&s);else native_difficulty(&s);equal(r,s);CHECK(memory[0].players==memory[1].players && memory[0].bytes==memory[1].bytes && memory[0].difficulty==memory[1].difficulty,"fields");if(failed) return count;count++;}'
   elif entry=='control':
    expected=262144;body='for(unsigned mode=0;mode<65536;mode++) for(unsigned presence=0;presence<4;presence++) {Regs r={0};r.ax=(uint16_t)mode;r.flags=0xed7;Regs s=r;delivered=(uint16_t[]){0,32767,32768,65535}[presence];nr[0]=nr[1]=nw[0]=nw[1]=0;side=0;int first=reference(&r);side=1;int second=actual(&s);CHECK(first==second,"accept");equal(r,s);accesses();if(failed) return count;count++;}'
   elif entry=='selector':
    expected=65536;body='for(unsigned value=0;value<65536;value++) {Regs r={0};r.ax=(uint16_t)value;r.flags=0xed7;Regs s=r;MenusMainAction expected_action=reference(&r);logic(&s,s.ax>>8,8);if(s.ax>>8) main_key_trace(&s,(uint8_t)s.ax);MenusMain state={MENUS_MAIN_POLL,1,1};MenusMainReply reply={0,0,(uint8_t)!!(s.ax>>8),(uint8_t)s.ax,0,0};CHECK(expected_action==menus_main_next(&state,reply),"action");equal(r,s);if(failed) return count;count++;}'
   else:
    expected=16777216;body='for(unsigned position=0;position<65536;position++) for(unsigned ch=0;ch<256;ch++) {Regs r={0};r.si=(uint16_t)position;r.ax=(uint16_t)(0xa500u+ch);r.flags=0xed7;Regs s=r;nr[0]=nr[1]=nw[0]=nw[1]=0;side=0;int first=reference(&r);side=1;int second=actual(&s);CHECK(first==second,"outcome");equal(r,s);accesses();if(failed) return count;count++;}'
   code+='EXPORT uint32_t enumerate(void) {uint32_t count=0;'+body+'return count;}\n';path=folder/'enumerate.c';path.write_text(code);dllpath=folder/'enumerate.dll';built=compile_c([path],dllpath,[ROOT/'c',ROOT/'native'],['-shared']);dll=C.CDLL(str(dllpath));dll.enumerate.restype=C.c_uint32;count=dll.enumerate();assert count<expected if negative else count==expected,(entry,count,expected)
   rows[entry]=count;save(folder/'result.json',receipt([sys.executable,'verif/menus_enumerate.py',*original_argv[1:]],[Path(__file__),*inputs],result='PASS',cases=count,domain=entry,negative_detected=negative,build=built));print('ENUM',entry,count,flush=True)
   return dict(result='FAIL' if negative else 'PASS',seconds=0,failures=[])
  previous=menus_proofs.cbmc;menus_proofs.cbmc=compile_property;sys.argv=['menus_proofs.py',entry,*(['--negative'] if negative else [])]
  try:menus_proofs.main()
  finally:menus_proofs.cbmc=previous;sys.argv=original_argv
 save(OUT/('menus-enumeration-negative.json' if negative else 'menus-enumeration.json'),receipt([sys.executable,'verif/menus_enumerate.py',*original_argv[1:]],[Path(__file__),ROOT/'verif/menus_proofs.py',ROOT/'verif/menus_spans.py',ROOT/'native/menus.c',ROOT/'native/menus.h',ROOT/'native/high_scores.c',ROOT/'native/front_end.h',ROOT/'native/bridge/menus_bridge.c'],result='PASS',domains=rows,negative_detected=negative))
if __name__=='__main__':main()
