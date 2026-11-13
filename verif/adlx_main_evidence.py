"""Actual-C one-event equivalence, arbitrary audio bytes, with a tail cut.

The only algorithm abstraction is the terminating CPU delay's state contract;
TIMER is an observing external capability. Their exact boundaries are explicit.
"""
import argparse,json,subprocess,time
from pathlib import Path
from closure_support import ROOT,function,compile_c,receipt,save,cbmc
from adlx_main_build import OUT

OPERATIONS=['LongWait','Frequency','KeyOff','Gain','Instrument','NoOp','TimerPeriod','Control','ShortWait']

def pair(folder,operation,negative=False):
    folder.mkdir(parents=True,exist_ok=True)
    adlib=(ROOT/'c/adlib.c').read_text();engine=(ROOT/'c/sound_engine.c').read_text()
    bridge=(ROOT/'native/bridge/adlx_main_bridge.c').read_text().split('EXPORT int c_RunMainAdlxEvents')[0]
    bridge=bridge.replace('#include "audio_projection.h"','#include "'+(ROOT/'native/bridge/audio_projection.h').as_posix()+'"')
    bridge=bridge.replace('#include "../adlx_main.h"','#include "'+(ROOT/'native/adlx_main.h').as_posix()+'"')
    prefix=adlib.split('/* TRANSLATES SOUND:CancelMusicFade */')[0]
    # Strip the preceding comment, which belongs to Cancel rather than drivers.
    prefix=prefix[:prefix.rfind('/* No stack args.')]
    for name in ['bh','delay']:prefix=prefix.replace(function(prefix,name),'')
    delay=function(engine,'c_DelaySoundIo')
    loop='    uint16_t remaining=product;\n    do { remaining=(uint16_t)(remaining-1); } while(remaining);\n'
    assert loop in delay
    delay=delay.replace(loop,'    /* State-only delay contract: the finite busy loop has no effects. */\n')
    functions=[]
    for name in OPERATIONS:
        source=engine if name in ('LongWait','ShortWait') else adlib
        functions.append(function(source,'c_HandleMainAdlx'+name))
    extension=function(adlib,'extension')
    prologue='''#include "platform.h"
#ifdef __CPROVER__
uint8_t nondet_u8(void);uint16_t nondet_u16(void);
#define N8 nondet_u8
#define N16 nondet_u16
#define CHECK(c,m) __CPROVER_assert(c,m)
#else
#include <assert.h>
static uint32_t random_state=134159;
static uint16_t N16(void) {random_state=random_state*1664525u+1013904223u;return (uint16_t)(random_state>>16);}
static uint8_t N8(void) {return (uint8_t)N16();}
#define CHECK(c,m) assert(c)
#endif
static void initialize(void);
static void compare_memory(void);
'''
    native='#include "'+(ROOT/'native/adlx_main.c').as_posix()+'"\n'
    if negative:
        mutated=(ROOT/'native/adlx_main.c').read_text().replace('state->displaced[channel].frequency&=65503u;','state->displaced[channel].frequency&=57343u;')
        mutant=folder/'mutant.c';mutant.write_text(mutated.replace('#include "adlx_main.h"','#include "'+(ROOT/'native/adlx_main.h').as_posix()+'"'))
        native='#include "'+mutant.as_posix()+'"\n'
    code=prologue+prefix+delay+extension+''.join(functions)+bridge+native
    code+='static int reference_event(Regs *r) {return c_HandleMainAdlx'+OPERATIONS[operation]+'(r);}\n'
    (folder/'pair.inc').write_text(code)
    source=(ROOT/'verif/adlx_main_harness.c').read_text()
    init=['static void initialize(void) {',
          'for(unsigned i=0;i<2;i++) {io_count[i]=0;timer_count[i]=0;for(unsigned j=0;j<28;j++) for(unsigned k=0;k<3;k++) io[i][j][k]=0;for(unsigned j=0;j<3;j++) timer[i][j]=0;}',
          '#ifdef __CPROVER__\nsound[0]=nondet_sound();sound[1]=sound[0];\n#else',
          *[f'sound[0].bytes[{i}]=N8();sound[1].bytes[{i}]=sound[0].bytes[{i}];' for i in range(1280)],
          '#endif',
          'for(unsigned i=0;i<9;i++) {operators[i]=N8();}\nfor(unsigned i=0;i<10;i++) {auxiliary[i]=N8();}\nfor(unsigned i=0;i<12;i++) {operands[i]=N8();}','}']
    compare=['static void compare_memory(void) {',
        '#ifdef __CPROVER__\nuint16_t probe=N16();__CPROVER_assume(probe<1280);\nCHECK(sound[0].bytes[probe]==sound[1].bytes[probe],"every persistent audio byte");\n#else',
        *[f'CHECK(sound[0].bytes[{i}]==sound[1].bytes[{i}],"persistent audio byte {i}");' for i in range(1280)],'#endif','}']
    harness=folder/'harness.c';harness.write_text(source+'\n'+'\n'.join(init+compare)+'\n')
    return harness,[Path(__file__),ROOT/'verif/adlx_main_harness.c',ROOT/'c/adlib.c',ROOT/'c/sound_engine.c',
        ROOT/'native/adlx_main.c',ROOT/'native/adlx_main.h',ROOT/'native/audio.h',ROOT/'native/bridge/adlx_main_bridge.c',
        ROOT/'native/bridge/audio_projection.h',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',ROOT/'c/platform.h']

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['samples','prove']);p.add_argument('--op',type=int,choices=range(9));p.add_argument('--timeout',type=int,default=60);p.add_argument('--negative',action='store_true');p.add_argument('--channels',action='store_true');a=p.parse_args()
    rows=[]
    for op in range(9) if a.op is None else [a.op]:
      for channel in range(16) if a.channels else [-1]:
        folder=OUT/f'{a.mode}_{op}_struct_sat_c{channel}{"_negative" if a.negative else ""}';harness,inputs=pair(folder,op,a.negative)
        if a.mode=='samples':
            exe=folder/'harness.exe';built=compile_c([harness],exe,[ROOT/'c',ROOT/'native'],[f'-DOP={op}',f'-DCHANNEL={channel}'])
            start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
            result=receipt(built['command'],inputs,result='PASS' if run.returncode==0 else 'FAIL',cases=20000,
                execution=[str(exe)],compiler_sha256=built['compiler_sha256'],seconds=time.perf_counter()-start,stdout=run.stdout,stderr=run.stderr)
            save(folder/'result.json',result)
        else:
            result=cbmc(harness,folder,inputs,unwind=30,timeout=a.timeout,defines=['-D__CPROVER__',f'-DOP={op}',f'-DCHANNEL={channel}'],extra=['--arrays-uf-never'])
        print(OPERATIONS[op],channel,result['result'],result['seconds'],result.get('failures',[]),flush=True);rows.append(result)
        if not a.negative:assert result['result']=='PASS',result.get('stderr','')
        else:assert result['result']=='FAIL'
    return rows
if __name__=='__main__':main()
