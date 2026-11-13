"""Actual C raw OPL write/delay flags under the enumerated finite LOOP contract."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from adlx_loader_solver import cbmc
from adlx_voice_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['register','delay']);p.add_argument('--timeout',type=int,default=180);a=p.parse_args();assert 0<a.timeout<=600
    folder=OUT/f'proof-io-{a.mode}';folder.mkdir(parents=True,exist_ok=True)
    literal=(ROOT/'c/adlib.c').read_text();engine=(ROOT/'c/sound_engine.c').read_text();native=(ROOT/'native/adlx_voice.c').read_text()
    code='''#include "platform.h"
#include "adlx_voice.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
uint8_t ugh_mem[UGH_MEM_SIZE];Regs nondet_regs(void);uint8_t nondet_u8(void);
static uint8_t calibration;static uint16_t ports[2][2];static unsigned count;
uint8_t ugh_read(uint32_t address) {CHECK(address==(unsigned)SOUND_SEG*16u+S(SoundIoDelayMultiplier),"only calibration low byte read");return calibration;}
void ugh_write(uint32_t address,uint8_t value) {(void)address;(void)value;CHECK(0,"raw I/O writes no RAM");}
void platform_out(uint16_t port,unsigned size,uint32_t value) {CHECK(count<2 && size==1,"raw register output count");ports[count][0]=port;ports[count++][1]=(uint16_t)value;}
'''+function(literal,'al')+function(literal,'c_WriteAdlibRegister')
    delay=function(engine,'c_DelaySoundIo');loop='    uint16_t remaining=product;\n    do { remaining=(uint16_t)(remaining-1); } while(remaining);\n';assert loop in delay;code+=delay.replace(loop,'/* Actual LOOP counts exhaustively enumerated on compiled C. */\n')
    code+=function(native,'audio_voice_delay')+function(native,'audio_voice_register')
    code+='''int main(void) {Regs before=nondet_regs();before.cs=SOUND_SEG;Regs r=before;calibration=nondet_u8();AudioIoDelay d;
'''
    if a.mode=='register':code+='''CHECK(c_WriteAdlibRegister(&r)==0,"normal raw register return");AudioRegisterWrite write=audio_voice_register(before.bx);d=audio_voice_delay(4,calibration);CHECK(count==2 && ports[0][0]==0x388 && ports[1][0]==0x389 && ports[0][1]==write.reg && ports[1][1]==write.value,"all packed-word writes in order");
'''
    else:code+='CHECK(c_DelaySoundIo(&r)==0,"normal delay return");d=audio_voice_delay((uint8_t)before.ax,calibration);CHECK(!count,"delay has no I/O");\n'
    code+='''CHECK(!!(r.flags&CF)==d.overflow && !!(r.flags&OF)==d.overflow && ((r.flags^before.flags)&~(CF|OF))==0,"MUL flags and all other flags preserved");
 CHECK(r.ax==before.ax && r.bx==before.bx && r.cx==before.cx && r.dx==before.dx && r.si==before.si && r.di==before.di && r.bp==before.bp && r.sp==before.sp && r.cs==before.cs && r.ds==before.ds && r.es==before.es && r.ss==before.ss && r.ip==before.ip,"entire register frame preserved");return 0;}
'''
    harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'native/adlx_voice.c',ROOT/'native/adlx_voice.h',ROOT/'native/audio.h',ROOT/'c/adlib.c',ROOT/'c/sound_engine.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=4,timeout=a.timeout,extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
    print(a.mode,result['result'],result['seconds'],result['failures'],flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
