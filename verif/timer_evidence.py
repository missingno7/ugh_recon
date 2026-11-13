"""Actual-C timer operation proofs and finite enumeration; no algorithm model."""
import argparse,json,re,subprocess,time
from pathlib import Path
from closure_support import ROOT,function,compile_c,cbmc,receipt,save
OUT=ROOT/'build/workers/close-timer'

def pair(folder):
    folder.mkdir(parents=True,exist_ok=True)
    first=(ROOT/'c/timer.c').read_text();system=(ROOT/'c/timer_system.c').read_text()
    body=function(system,'scan_timer_minimum')
    for raw,names in [(first,['RegisterTimerCallback']),(system,['RemoveTimerCallback','SetTimerCallbackInterval'])]:
        for name in names:body+=function(raw,'c_'+name).replace('c_'+name,'l1_'+name)
    # Verbatim accounting phase of the actual L1 ISR. Stack saves, calls and I/O
    # belong to the independently exercised bridge/platform shell, not this lemma.
    raw=function(first,'c_HandleTimerInterrupt')
    start=raw.index('    uint16_t slot=');end=raw.index('    slot=rd16(DATA_SEG,D(LastActiveTimerSlotOffset));',start)
    body+='int l1_account(Regs *r) {\nRegs saved=*r;\n'+raw[start:end]+'return UGH_OK;\n}\n'
    text='#include "'+(ROOT/'c/ugh.h').as_posix()+'"\n'
    text+='''/* Normalized aligned timer RAM only; NOT a full-machine alias proof. */
static uint16_t words[152];
static uint16_t timer_read_word(uint16_t segment,uint16_t offset) {
    CHECK(segment==DATA_SEG && offset>=D(LastActiveTimerSlotOffset) &&
          offset<=D(ProgrammedPitDivisor) && !(offset&1),"timer read footprint");
    return words[(offset-D(LastActiveTimerSlotOffset))/2];
}
static void timer_write_word(uint16_t segment,uint16_t offset,uint16_t value) {
    CHECK(segment==DATA_SEG && offset>=D(LastActiveTimerSlotOffset) &&
          offset<=D(ProgrammedPitDivisor) && !(offset&1),"timer write footprint");
    words[(offset-D(LastActiveTimerSlotOffset))/2]=value;
}
static uint32_t timer_read_long(uint16_t segment,uint16_t offset) {
    return timer_read_word(segment,offset) | (uint32_t)timer_read_word(segment,offset+2)*65536u;
}
#define rd16 timer_read_word
#define wr16 timer_write_word
#define rd32 timer_read_long
'''+body+'#include "'+(ROOT/'native/timer.c').as_posix()+'"\n'
    text+='''static void project(TimerState *state) {
    state->count=rd16(DATA_SEG,D(LastActiveTimerSlotOffset))/2+1;
    state->earliest=rd32(DATA_SEG,D(EarliestTimerIntervalLow));
    state->quantum=rd32(DATA_SEG,D(NextPitQuantumLow));
    for(unsigned i=0;i<16;i++) {
        TimerSlot *slot=&state->slots[i];
        slot->interval=rd16(DATA_SEG,D(TimerIntervalLowBySlot)+i*2) |
            (uint32_t)rd16(DATA_SEG,D(TimerIntervalHighBySlot)+i*2)*65536u;
        slot->remaining=rd16(DATA_SEG,D(TimerRemainingLowBySlot)+i*2) |
            (uint32_t)rd16(DATA_SEG,D(TimerRemainingHighBySlot)+i*2)*65536u;
        slot->due=rd16(DATA_SEG,D(TimerCallbackDueBySlot)+i*2);
        slot->handle=rd16(DATA_SEG,D(TimerHandleBySlot)+i*2);
        state->by_handle[i]=rd16(DATA_SEG,D(TimerSlotOffsetByHandle)+i*2);
        /* Relational proof permits arbitrary symbolic callback WORDS as opaque
         * fragments: no address arithmetic or dispatch is performed by L2. */
        slot->target.first=rd16(DATA_SEG,D(TimerCallbackOffsetBySlot)+i*4);
        slot->target.second=rd16(DATA_SEG,D(TimerCallbackSegmentBySlot)+i*4);
    }
}
static void compare(const TimerState *state, int registration) {
    CHECK(rd16(DATA_SEG,D(LastActiveTimerSlotOffset))==(state->count-1)*2,"count");
    CHECK(rd32(DATA_SEG,D(EarliestTimerIntervalLow))==state->earliest,"minimum");
    CHECK(rd32(DATA_SEG,D(NextPitQuantumLow))==state->quantum,"next quantum");
    for(unsigned i=0;i<16;i++) {
        const TimerSlot *slot=&state->slots[i];
        CHECK(rd16(DATA_SEG,D(TimerIntervalLowBySlot)+i*2)==(uint16_t)slot->interval,"interval low");
        CHECK(rd16(DATA_SEG,D(TimerIntervalHighBySlot)+i*2)==slot->interval>>16,"interval high");
        CHECK(rd16(DATA_SEG,D(TimerRemainingLowBySlot)+i*2)==(uint16_t)slot->remaining,"remaining low");
        CHECK(rd16(DATA_SEG,D(TimerRemainingHighBySlot)+i*2)==slot->remaining>>16,"remaining high");
        CHECK(rd16(DATA_SEG,D(TimerCallbackDueBySlot)+i*2)==slot->due,"due");
        CHECK(rd16(DATA_SEG,D(TimerHandleBySlot)+i*2)==slot->handle,"slot handle");
        CHECK(rd16(DATA_SEG,D(TimerSlotOffsetByHandle)+i*2)==state->by_handle[i],"handle map");
        if(!registration || i!=state->count-1) {
            CHECK(rd16(DATA_SEG,D(TimerCallbackOffsetBySlot)+i*4)==slot->target.first,"callback first");
            CHECK(rd16(DATA_SEG,D(TimerCallbackSegmentBySlot)+i*4)==slot->target.second,"callback second");
        }
    }
}
'''
    (folder/'pair.inc').write_text(text)
    return [ROOT/'c/timer.c',ROOT/'c/timer_system.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',
            ROOT/'native/timer.c',ROOT/'native/timer.h',Path(__file__)]

def prove(operation,count,timeout,negative,handle=2,destination=1,symbolic=False):
    folder=OUT/f'cbmc_{operation}_{count}_h{handle}_s{destination}{"_symbolic" if symbolic else ""}{"_negative" if negative else ""}'
    inputs=pair(folder);harness=folder/'harness.c'
    harness.write_text('''void __CPROVER_assert(_Bool,const char *);
void __CPROVER_assume(_Bool);
void __CPROVER_havoc_object(void *);
#define CHECK __CPROVER_assert
#include "pair.inc"
int main(void) {
    __CPROVER_havoc_object(words);
    unsigned active=COUNT;
    if(SYMBOLIC) { unsigned arbitrary; __CPROVER_assume(arbitrary>=1 && arbitrary<=COUNT);active=arbitrary; }
    wr16(DATA_SEG,D(LastActiveTimerSlotOffset),(active-1)*2);
    if(!SYMBOLIC && (OPERATION==1 || OPERATION==2)) wr16(DATA_SEG,D(TimerSlotOffsetByHandle)+HANDLE,DESTINATION*2);
    if(!SYMBOLIC && OPERATION==0) {
        for(unsigned i=0;i<=COUNT;i++) wr16(DATA_SEG,D(TimerSlotOffsetByHandle)+i*2,0);
        wr16(DATA_SEG,D(TimerSlotOffsetByHandle)+HANDLE,32768);
    }
    TimerState state; project(&state);
    Regs old; old.ds=DATA_SEG;
    uint16_t handle=HANDLE;
    if(SYMBOLIC) { uint16_t arbitrary; __CPROVER_assume(arbitrary<32 && !(arbitrary&1));handle=arbitrary; }
    old.ax=handle;
    int selected=timer_handle_slot(&state,handle);
    unsigned operation=OPERATION;
    if(operation==0) {
        __CPROVER_assume(active<16);
        unsigned free_index=handle/2; __CPROVER_assume(free_index<=active);
        for(unsigned i=free_index+1;i<=active;i++) {
            __CPROVER_assume(!(state.by_handle[i]&32768));
        }
        __CPROVER_assume(state.by_handle[free_index]&32768);
        old.ax=S(TickAdlxPlayback);old.dx=SOUND_SEG;
        uint32_t interval=old.bx | (uint32_t)old.cx*65536u;
        int result=timer_register(&state,TIMER_ADLX_PLAYBACK,interval);
        CHECK(l1_RegisterTimerCallback(&old)==0,"registration status");
        CHECK(result==old.ax,"allocated handle");
        CHECK(rd16(DATA_SEG,D(TimerCallbackOffsetBySlot)+(active*4))==S(TickAdlxPlayback),"registered first");
        CHECK(rd16(DATA_SEG,D(TimerCallbackSegmentBySlot)+(active*4))==SOUND_SEG,"registered second");
    } else if(operation==1) {
        __CPROVER_assume(active>=2 && selected>=0);
        uint16_t result=timer_remove(&state,handle);
        CHECK(l1_RemoveTimerCallback(&old)==0,"remove status");
        CHECK(result==old.ax && old.bx==(uint16_t)state.earliest && old.cx==state.earliest>>16,"remove result");
    } else if(operation==2) {
        __CPROVER_assume(selected>=0);
        uint32_t interval=old.bx | (uint32_t)old.cx*65536u;
        timer_set_interval(&state,handle,interval);
        CHECK(l1_SetTimerCallbackInterval(&old)==0,"setter status");
        CHECK(old.bx==(uint16_t)state.earliest && old.cx==state.earliest>>16,"setter result");
    } else {
        TimerTickScratch scratch=timer_account_tick(&state);
        CHECK(l1_account(&old)==0,"tick status");
        CHECK(old.ax==scratch.low && old.dx==scratch.high,"callback input scratch");
    }
    compare(&state,operation==0);
    return 0;
}
''')
    result=cbmc(harness,folder,inputs,unwind=1 if negative else 18,timeout=timeout,
        defines=[f'-DSYMBOLIC={int(symbolic)}',f'-DCOUNT={count}',f'-DHANDLE={handle}',f'-DDESTINATION={destination}',f'-DOPERATION={dict(register=0,remove=1,set=2,tick=3)[operation]}'],
        extra=[])
    print(json.dumps({k:result[k] for k in ['result','seconds','failures']}),flush=True)
    if negative:
        if result['result']!='FAIL' or not any('unwind' in x[0] for x in result['failures']):raise RuntimeError('negative control')
    elif result['result']!='PASS':raise RuntimeError(result['result'])

def enumerate_cases():
    folder=OUT/'enumeration';inputs=pair(folder);source=folder/'enumeration.c'
    source.write_text('''#include <stdio.h>
#include <stdlib.h>
#define CHECK(c,m) do { if(!(c)) { puts(m); exit(23); } } while(0)
#include "pair.inc"
#include "'''+(ROOT/'verif/timer_enumeration.c').as_posix()+'''"
''')
    exe=folder/'enumeration.exe';result=compile_c([source],exe,[ROOT/'c',ROOT/'native'])
    start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
    if run.returncode:raise RuntimeError(run.stdout+run.stderr)
    result.update(receipt(result['command'],[*inputs,ROOT/'verif/timer_enumeration.c'],
        execution=[str(exe)],result='PASS',seconds=time.perf_counter()-start,counts=json.loads(run.stdout)))
    save(folder/'result.json',result);print(run.stdout,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation',choices=['enumerate','register','remove','set','tick'])
    p.add_argument('--count',type=int,choices=range(1,17),default=3)
    p.add_argument('--symbolic',action='store_true');p.add_argument('--handle',type=int,default=2);p.add_argument('--slot',type=int,default=1);
    p.add_argument('--timeout',type=int,default=45);p.add_argument('--negative',action='store_true')
    a=p.parse_args()
    if a.operation=='enumerate':enumerate_cases()
    else:prove(a.operation,a.count,a.timeout,a.negative,a.handle,a.slot,a.symbolic)
