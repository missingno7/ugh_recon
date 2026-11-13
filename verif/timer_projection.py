"""Compile actual bridge projection/fragment functions and check their domains."""
import json,subprocess,time
from pathlib import Path
from closure_support import ROOT,function,compile_c,receipt,save
OUT=ROOT/'build/workers/close-timer/projection'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    bridge=ROOT/'native/bridge/timer_bridge.c';native=ROOT/'native/timer.c'
    text='#include "'+(ROOT/'c/ugh.h').as_posix()+'"\n'
    text+='#include "'+native.as_posix()+'"\n'
    text+=''.join(function(bridge.read_text(),name) for name in
                  ['timer_word_token','timer_token_word','timer_project','timer_publish'])
    text+='''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t address) { return ugh_mem[address]; }
void ugh_write(uint32_t address,uint8_t value) { ugh_mem[address]=value; }
#define CHECK(c) do { if(!(c)) { printf("failure line %d\\n",__LINE__);exit(23); } } while(0)
static uint32_t random_state=719;
static uint16_t random_word(void) {
    random_state^=random_state<<13; random_state^=random_state>>17; random_state^=random_state<<5;
    return (uint16_t)random_state;
}
int main(void) {
    uint16_t open[32];
    for(unsigned position=0;position<32;position++) for(unsigned word=0;word<65536;word++) {
        open[position]=(uint16_t)word;
        CHECK(timer_token_word(timer_word_token((uint16_t)word,position),open)==word);
    }
    for(unsigned callback=1;callback<=TIMER_FIXTURE_IRQ;callback++) {
        TimerTarget target=timer_target((TimerCallback)callback);
        TimerTarget projected={timer_word_token(timer_token_word(target.first,open),0),
                               timer_word_token(timer_token_word(target.second,open),1)};
        CHECK(timer_callback(projected)==(TimerCallback)callback);
    }
    for(unsigned sample=0;sample<2048;sample++) {
        for(unsigned address=D(LastActiveTimerSlotOffset);address<=D(ProgrammedPitDivisor);address+=2)
            wr16(DATA_SEG,(uint16_t)address,random_word());
        wr16(DATA_SEG,D(LastActiveTimerSlotOffset),(uint16_t)((sample%16)*2));
        wr16(TIMER_SEG,T(TimerInterruptInstalled),random_word());
        uint8_t before[304];memcpy(before,ugh_mem+lin(DATA_SEG,D(LastActiveTimerSlotOffset)),304);
        uint16_t installed=rd16(TIMER_SEG,T(TimerInterruptInstalled));
        TimerState state;CHECK(timer_project(&state,open));
        CHECK(state.installed==installed);
        timer_publish(&state,open);
        CHECK(!memcmp(before,ugh_mem+lin(DATA_SEG,D(LastActiveTimerSlotOffset)),304));
        CHECK(rd16(TIMER_SEG,T(TimerInterruptInstalled))==installed);
    }
    puts("{\\"word_roundtrips\\":2097152,\\"typed_callbacks\\":5,\\"state_roundtrips\\":2048}");
    return 0;
}
'''
    source=OUT/'projection.c';source.write_text(text);exe=OUT/'projection.exe'
    result=compile_c([source],exe,[ROOT/'native',ROOT/'c'])
    start=time.perf_counter();run=subprocess.run([str(exe)],capture_output=True,text=True)
    if run.returncode:raise RuntimeError(run.stdout+run.stderr)
    result.update(receipt(result['command'],[bridge,native,ROOT/'native/timer.h',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h',Path(__file__)],
        result='PASS',execution=[str(exe)],seconds=time.perf_counter()-start,counts=json.loads(run.stdout)))
    save(OUT/'result.json',result);print(run.stdout)

if __name__=='__main__':main()
