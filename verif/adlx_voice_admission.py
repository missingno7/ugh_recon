"""All invalid channel words: actual C/bridge/core control prefixes, no voice reads."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from adlx_loader_solver import cbmc
from adlx_voice_build import OUT
NAMES=['SetAdlibChannelVolume','SetAdlibChannelGain','KeyOffAdlibChannel','SetAdlibFrequency','LoadAdlibInstrument']
def cut_c(text,name):
    if name in ['SetAdlibChannelGain','LoadAdlibInstrument']:
        end=text.index('    if(ch>=9) return UGH_OK;')+len('    if(ch>=9) return UGH_OK;')
        return text[:end]+'CHECK(0,"invalid C channel must exit before voice work");return 0;}\n'
    at=text.index('if(channel<9)' if name=='SetAdlibChannelVolume' else 'if(ch<9)');start=text.index('{',at);depth=1;end=start+1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[:start]+'{CHECK(0,"invalid C channel cannot enter voice block");}'+text[end:]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--negative',action='store_true');p.add_argument('--timeout',type=int,default=180);a=p.parse_args();assert 0<a.timeout<=600
    folder=OUT/('proof-admission-negative' if a.negative else 'proof-admission');folder.mkdir(parents=True,exist_ok=True)
    literal=(ROOT/'c/adlib.c').read_text();bridge=(ROOT/'native/bridge/adlx_voice_bridge.c').read_text();native=(ROOT/'native/adlx_voice.c').read_text()
    code='''#include "ugh.h"
#include "adlx_voice.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
uint8_t ugh_mem[UGH_MEM_SIZE];Regs nondet_regs(void);uint16_t nondet_u16(void);uint8_t nondet_u8(void);static uint8_t stack[1024];static unsigned executing;
uint8_t ugh_read(uint32_t p) {CHECK(p>=0x80204 && p<0x8020a,"invalid entry reads only caller arguments");return stack[p-0x80000];}
void ugh_write(uint32_t p,uint8_t value) {CHECK(!executing && p>=0x80204 && p<0x8020a,"invalid entry stores no RAM");stack[p-0x80000]=value;}
'''
    for name in NAMES:code+=cut_c(function(literal,'c_'+name),name)
    prefix=function(bridge,'voice_entry');prefix=prefix[:prefix.index('    AudioInstrumentSource source=')]+'CHECK(0,"invalid bridge must exit before projection/source reads");return 0;}\n';code+=prefix
    core=function(native,'audio_voice_step');core=core[:core.index('    result.first_reserved=')]+'CHECK(0,"invalid native must exit before state/source reads");return result;}\n'
    if a.negative:core=core.replace('if(result.channel>=9)','if(result.channel>9)')
    code+=core
    code+='''static void same(Regs a,Regs b) {CHECK(a.ax==b.ax && a.bx==b.bx && a.cx==b.cx && a.dx==b.dx && a.si==b.si && a.di==b.di && a.bp==b.bp && a.sp==b.sp && a.cs==b.cs && a.ds==b.ds && a.es==b.es && a.ss==b.ss && a.ip==b.ip && a.flags==b.flags,"invalid entry full frame preserved");}
int main(void) {
 Regs before=nondet_regs();before.cs=SOUND_SEG;before.ss=0x8000;before.sp=0x200;Regs r=before;
 uint16_t channel=nondet_u16();__CPROVER_assume((uint8_t)channel>=9);wr16(r.ss,0x204,channel);wr16(r.ss,0x206,nondet_u16());wr16(r.ss,0x208,nondet_u16());executing=1;
 AudioVoiceOperation op=(AudioVoiceOperation)nondet_u8();__CPROVER_assume(op<=AUDIO_VOICE_INSTRUMENT);
 int rc;
 switch(op) {
 case AUDIO_VOICE_VOLUME:rc=c_SetAdlibChannelVolume(&r);break;
 case AUDIO_VOICE_GAIN:rc=c_SetAdlibChannelGain(&r);break;
 case AUDIO_VOICE_KEY_OFF:rc=c_KeyOffAdlibChannel(&r);break;
 case AUDIO_VOICE_FREQUENCY:rc=c_SetAdlibFrequency(&r);break;
 default:rc=c_LoadAdlibInstrument(&r);break;
 }
 CHECK(!rc,"invalid C normal return");same(r,before);r=before;CHECK(!voice_entry(&r,op),"invalid bridge normal return");same(r,before);
 AudioVoiceResult result=audio_voice_step(0,op,channel,0,0);CHECK(result.channel==(uint8_t)channel && !result.write_count && !result.displaced && !result.reservation_checked && !result.first_reserved,"invalid native early result without any borrowed pointer read");return 0;}
'''
    harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'native/adlx_voice.c',ROOT/'native/adlx_voice.h',ROOT/'native/bridge/adlx_voice_bridge.c',ROOT/'native/audio.h',ROOT/'c/adlib.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=4,timeout=a.timeout,extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
    print('admission',result['result'],result['seconds'],result['failures'],flush=True);assert result['result']==('FAIL' if a.negative else 'PASS')
if __name__=='__main__':main()
