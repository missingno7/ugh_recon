"""Compiled actual-C scalar slices; no static decoder supplies expectations."""
import sys,ctypes as C
from pathlib import Path
from closure_support import ROOT,function,compile_c,receipt,save
from video_dos_build import OUT

def scale_span():
    body=function((ROOT/'c/video.c').read_text(),'c_ScaleAndUploadFadedPalette')
    return body[body.index('        set_al'):body.index('        r->bx=dec16')]

def main():
    negative='--negative' in sys.argv;folder=OUT/('enumerate-negative' if negative else 'enumerate');folder.mkdir(parents=True,exist_ok=True)
    native=(ROOT/'native/video_dos.c').read_text()
    if negative:native=native.replace('(uint8_t)(product>>8)','(uint8_t)(product>>7)')
    source='#include "platform.h"\n#include "video_dos.h"\n'+native+'''
static uint8_t incoming,written;
uint8_t ugh_read(uint32_t address) {(void)address;return incoming;}
void ugh_write(uint32_t address,uint8_t value) {(void)address;written=value;}
static void reference(Regs *r) {'''+scale_span()+'''}
EXPORT uint32_t enumerate_scale(void) {
 uint32_t count=0;Regs r={0};
 for(unsigned factor=0;factor<65536;factor++) for(unsigned value=0;value<256;value++) {
  incoming=(uint8_t)value;r.cx=(uint16_t)factor;r.flags=0xed7;reference(&r);VideoScaled actual=video_palette_scale(incoming,r.cx);
  if(actual.low!=r.ax || actual.high!=r.dx || actual.value!=written || !!(r.flags&CF)!=(actual.high!=0) || !!(r.flags&OF)!=(actual.high!=0)) return count;
  count++;
 }
 return count;
}
'''
    helper=folder/'enumerate.c';helper.write_text(source);dllpath=folder/'enumerate.dll';build=compile_c([helper],dllpath,[ROOT/'c',ROOT/'native'],['-shared']);dll=C.CDLL(str(dllpath));dll.enumerate_scale.restype=C.c_uint32;count=dll.enumerate_scale();expected=65536*256
    assert (count<expected) if negative else count==expected,(count,expected)
    save(folder/'result.json',receipt([sys.executable,'verif/video_dos_enumerate.py',*sys.argv[1:]],[Path(__file__),ROOT/'c/video.c',ROOT/'native/video_dos.c',ROOT/'native/video_dos.h'],result='PASS',comparisons=count,domain='All256 component bytes x all65536 factors; actual L1 MUL/store span, product words, stored AH and CF/OF',negative_detected=negative,build=build))
    print('PASS',count,'scale comparisons; negative detected',negative,flush=True)
if __name__=='__main__':main()
