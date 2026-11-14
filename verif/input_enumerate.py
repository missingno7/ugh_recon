"""Real compiled whole-IRQ finite slices and threshold arithmetic enumeration."""
import ctypes as C,sys,json
from pathlib import Path
from closure_support import ROOT,function,save,receipt
import input_build
OUT=input_build.OUT

def main():
 source='''#include "platform.h"
#include "input.h"
#include <string.h>
extern int l1_HandleKeyboardScanInterrupt(Regs *);
static uint8_t before[UGH_MEM_SIZE],expected[UGH_MEM_SIZE];
EXPORT uint32_t input_batch_failure[8];
static void script(uint8_t scan) {ugh_devices.count=0;ugh_devices.error=0;ugh_devices.script_count=1;InputScript *s=&ugh_devices.scripts[0];s->port=0x60;s->count=1;s->cursor=s->used=0;s->cycles=s->cycles_left=1;s->runs[0].value=scan;s->runs[0].repeat=1;}
EXPORT uint32_t input_batch_scans(unsigned kind) {
 memcpy(before,ugh_mem,UGH_MEM_SIZE);uint32_t cases=0;
 for(unsigned state=0;state<(kind==0 ? 2u : kind==1 ? 3u : 34u*2u);state++) {
  for(unsigned index=0;index<(kind==0 ? 256u : 1u);index++) for(unsigned scan=0;scan<256;scan++) {
   memcpy(ugh_mem,before,UGH_MEM_SIZE);
   if(kind==0) {const uint8_t row[]={0xe0,0x48,255,0,255,0,255};for(unsigned i=0;i<7;i++) wr8(DATA_SEG,(uint16_t)(D(KeyboardSequenceRecords)+i),row[i]);wr8(DATA_SEG,D(KeyboardSequenceCandidateState),state ? 255 : 0);wr8(DATA_SEG,D(KeyboardSequenceIndex),(uint8_t)index);}
   else {for(unsigned i=0;i<34;i++) wr8(DATA_SEG,(uint16_t)(D(KeyboardSequenceCandidateState)+6u*i),kind==2 ? (i==state/2u ? (state&1u ? 255 : 0) : 255) : state==2 ? 255 : 0);wr8(DATA_SEG,D(KeyboardSequenceIndex),kind==1 && state==1 ? 1 : 0);}
   wr16(DATA_SEG,D(PlayerOneControlMode),65535);wr16(DATA_SEG,D(PlayerTwoControlMode),65535);
   if(kind==1 && state==1) {wr8(DATA_SEG,D(KeyboardSequenceIndex),0);Regs prefix={0};prefix.cs=GAME_SEG;script(0xe0);if(l1_HandleKeyboardScanInterrupt(&prefix)) return 0;}
   /* Other than index/candidates, the shipped record bytes stay the oracle. */
   uint8_t initial[256];memcpy(initial,ugh_mem+(uint32_t)DATA_SEG*16u+D(KeyboardSequenceRecords),256);
   uint8_t initial_index=rd8(DATA_SEG,D(KeyboardSequenceIndex));
   Regs r={0xa55a,0x6996,0x9669,0x3cc3,0x7e81,0x817e,0x5aa5,0x1000,GAME_SEG,DATA_SEG,0x7400,0x8000,0xf00d,0xed7},native=r;
   script((uint8_t)scan);int status=l1_HandleKeyboardScanInterrupt(&r);memcpy(expected,ugh_mem,UGH_MEM_SIZE);uint32_t count=ugh_devices.count,error=ugh_devices.error;IoEvent events[4];if(count>4) return 0;memcpy(events,ugh_devices.log,count*sizeof(IoEvent));
   memcpy(ugh_mem,before,UGH_MEM_SIZE);memcpy(ugh_mem+(uint32_t)DATA_SEG*16u+D(KeyboardSequenceRecords),initial,256);wr8(DATA_SEG,D(KeyboardSequenceIndex),initial_index);wr16(DATA_SEG,D(PlayerOneControlMode),65535);wr16(DATA_SEG,D(PlayerTwoControlMode),65535);
   script((uint8_t)scan);int actual=c_HandleKeyboardScanInterrupt(&native);
   if(actual!=status || memcmp(&r,&native,sizeof r) || memcmp(expected,ugh_mem,UGH_MEM_SIZE) || count!=ugh_devices.count || error!=ugh_devices.error || memcmp(events,ugh_devices.log,count*sizeof(IoEvent))) {input_batch_failure[0]=kind;input_batch_failure[1]=state;input_batch_failure[2]=index;input_batch_failure[3]=scan;for(unsigned i=0;i<UGH_MEM_SIZE;i++) if(expected[i]!=ugh_mem[i]) {input_batch_failure[4]=i;break;}return 0;}
   cases++;
  }
 }
 memcpy(ugh_mem,before,UGH_MEM_SIZE);return cases;
}
'''
 source+='extern void ugh_devices_reset(void);\nextern int l1_PollKeyboardScanChange(Regs *);\nEXPORT uint32_t input_batch_changes(void) {\n memcpy(before,ugh_mem,UGH_MEM_SIZE);ugh_devices_reset();uint32_t cases=0;\n for(unsigned old=0;old<256;old++) for(unsigned scan=0;scan<256;scan++) {\n  memcpy(ugh_mem,before,UGH_MEM_SIZE);wr8(DATA_SEG,D(CurrentKeyboardScanCode),(uint8_t)old);wr8(GAME_SEG,G(LatestInterruptScanCode),(uint8_t)scan);\n  Regs r={0xa55a,0x6996,0x9669,0x3cc3,0x7e81,0x817e,0x5aa5,0x1000,GAME_SEG,DATA_SEG,0x7400,0x8000,0xf00d,0xed7},native=r;\n  int status=l1_PollKeyboardScanChange(&r);memcpy(expected,ugh_mem,UGH_MEM_SIZE);memcpy(ugh_mem,before,UGH_MEM_SIZE);wr8(DATA_SEG,D(CurrentKeyboardScanCode),(uint8_t)old);wr8(GAME_SEG,G(LatestInterruptScanCode),(uint8_t)scan);\n  int actual=c_PollKeyboardScanChange(&native);if(actual!=status || memcmp(&r,&native,sizeof r) || memcmp(expected,ugh_mem,UGH_MEM_SIZE) || ugh_devices.count || ugh_devices.error) return 0;cases++;\n }\n memcpy(ugh_mem,before,UGH_MEM_SIZE);return cases;\n}\n'
 source+=function((ROOT/'c/video.c').read_text(),'thresholds')
 source+='''EXPORT uint32_t input_batch_thresholds(void) {
 Regs r={0};r.ds=DATA_SEG;uint32_t count=0;
 for(unsigned measured=0;measured<65536;measured++) {wr16(DATA_SEG,D(FirstJoystickXCount),(uint16_t)measured);thresholds(&r,D(FirstJoystickXCount),D(JoystickLeftThresholds),D(JoystickRightThresholds));InputThresholds result=input_thresholds((uint16_t)measured);if(result.low!=rd16(DATA_SEG,D(JoystickLeftThresholds)) || result.high!=rd16(DATA_SEG,D(JoystickRightThresholds)) || result.doubled!=(uint16_t)(measured*2u)) return 0;count++;}return count;
}
'''
 folder=OUT/'batch';folder.mkdir(exist_ok=True);helper=folder/'batch.c';helper.write_text(source)
 compile_previous=input_build.compile_c
 def compile_with_batch(sources,output,includes,options):return compile_previous([*sources,helper],output,includes,options)
 input_build.compile_c=compile_with_batch
 sys.path.insert(0,str(ROOT/'tools'));import contacts_reference,difftest,nbuild
 contacts_reference.OUT=OUT/'reference';plain=contacts_reference.prepare_reference(local=True);dll=nbuild.load_l1(input_build.build());m=difftest.Machine();
 for slot in [0,2]:
  for name in ['PlayerUpInput','PlayerDownInput','PlayerLeftInput','PlayerRightInput','PlayerActionInput']:m.ww('DGROUP:'+name,0xa580+slot,slot)
 C.memmove(dll.ugh_memory().contents,m.snapshot(),difftest.MEM_SIZE);dll.ugh_devices_reset();rows=[]
 for kind in [0,1,2]:
  f=dll.input_batch_scans;f.argtypes=[C.c_uint];f.restype=C.c_uint32;count=f(kind);print('scan slice',kind,count,flush=True);assert count,[* (C.c_uint32*8).in_dll(dll,'input_batch_failure')];rows.append(dict(kind=kind,cases=count))
 count=dll.input_batch_thresholds();assert count==65536
 changes=dll.input_batch_changes();assert changes==65536;print('scan-change byte pairs',changes,flush=True)
 save(OUT/'enumeration.json',receipt([sys.executable,'verif/input_enumerate.py'],[Path(__file__),ROOT/'verif/input_build.py',ROOT/'native/input.c',ROOT/'native/input.h',ROOT/'native/bridge/input_bridge.c',ROOT/'c/dos_input.c',ROOT/'c/video.c',helper,plain],result='PASS',scan_slices=rows,threshold_words=count,scan_change_pairs=changes,scope='Whole IRQ, full RAM including stack, all registers/flags and exact ordered ports. Single-record all256 indices x all256 scans x enabled/rejected; shipped table reset/reachable-E0-prefix/rejected and each of34 candidate records enabled/rejected at index0. No claim for all2^34 candidate combinations.'))
if __name__=='__main__':main()
