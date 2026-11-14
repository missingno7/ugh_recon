"""Actual C primitives and staged mixer division; capped split properties."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from adlx_samples_limits import cbmc
from adlx_samples_build import OUT
from adlx_lifetime_proofs import SOLVER
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('entry',choices=['reset','scale','division','import','offset']);p.add_argument('mode',choices=['outputs','frame','dependence']);p.add_argument('--bounded-divisor',action='store_true');p.add_argument('--negative',action='store_true');a=p.parse_args()
    folder=OUT/f'proof-{a.entry}-{a.mode}{"-bounded" if a.bounded_divisor else ""}{"-negative" if a.negative else ""}';folder.mkdir(parents=True,exist_ok=True)
    native=(ROOT/'native/adlx_samples.c').read_text();literal=(ROOT/'c/sound_engine.c').read_text()
    if a.negative:
        old,new={'reset':('index*42u','index*40u'),'scale':('volume>>1','volume>>2'),'division':('quotient+127','quotient+128'),'import':('work->length>64000u','work->length>=64000u')}[a.entry]
        changed=native.replace(old,new);assert changed!=native;native=changed
    code='''#include "platform.h"
#include "adlx_samples.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
uint8_t ugh_mem[UGH_MEM_SIZE];uint16_t nondet_u16(void);uint8_t nondet_u8(void);unsigned nondet_uint(void);Regs nondet_regs(void);AudioSampleMixWork nondet_mix(void);AudioSampleImportWork nondet_import(void);
'''+native
    if a.entry=='offset':
        body=function(literal,'c_MixSampleVoicePairs');begin=body.index('            uint16_t sample_offset=');end=body.index(';',begin)+1
        declaration=body[begin:end].replace('rd16(r->cs,(uint16_t)(S(SampleVoiceStepQ8)+voice))','scale')
        code+='static uint16_t reference_offset(uint16_t cursor,uint16_t scale) {'+declaration+'return sample_offset;}\nint main(void) {uint16_t cursor=nondet_u16(),scale=nondet_u16();CHECK(reference_offset(cursor,scale)==sample_offset(cursor,scale),"all32 product bits then word truncation of Q8 source offset");return 0;}'
    elif a.entry=='scale':
        code+=function(literal,'scaled_sample')+'''int main(void) {uint8_t sample=nondet_u8(),volume=nondet_u8();CHECK((uint16_t)audio_sample_scale(sample,volume)==scaled_sample(sample,volume),"all signed sample/volume products");return 0;}'''
    elif a.entry=='reset':
        code+='''static unsigned count;static uint32_t addresses[2];static uint8_t values[2];
uint8_t ugh_read(uint32_t address) {(void)address;CHECK(0,"reset reads no memory");return 0;}
void ugh_write(uint32_t address,uint8_t value) {CHECK(count<2,"only two bytes written");addresses[count]=address;values[count++]=value;}
'''+function(literal,'c_ResetSampleVoiceCursor')+'''int main(void) {Regs before=nondet_regs(),r=before;CHECK(c_ResetSampleVoiceCursor(&r)==0,"normal reset");AudioSampleReset result=audio_sample_reset(before.ax);CHECK(r.ax==result.displacement && !!(r.flags&CF)==result.overflow && !!(r.flags&OF)==result.overflow,"all indices product/overflow");CHECK(count==2 && addresses[0]==(uint32_t)r.cs*16u+(uint16_t)(S(SampleVoicePairCursor)+result.displacement) && addresses[1]==addresses[0]+1 && values[0]==0 && values[1]==0,"unchecked wrapping word target; contiguous operand high byte");r.ax=before.ax;r.flags=(uint16_t)((r.flags&~(CF|OF))|(before.flags&(CF|OF)));CHECK(r.ax==before.ax && r.bx==before.bx && r.cx==before.cx && r.dx==before.dx && r.si==before.si && r.di==before.di && r.bp==before.bp && r.sp==before.sp && r.cs==before.cs && r.ds==before.ds && r.es==before.es && r.ss==before.ss && r.ip==before.ip && r.flags==before.flags,"complete reset frame");return 0;}'''
    elif a.entry=='division':
        body=function(literal,'c_MixSampleVoicePairs');start=body.index('        int16_t divisor=');stop=body.index('        uint16_t remaining=');cut=body[start:stop]
        code+='''static uint16_t divisor_word,sum1,sum2;static uint8_t output[2];static unsigned written;
uint8_t ugh_read(uint32_t address) {unsigned p=address-(unsigned)SOUND_SEG*16u;unsigned at=p>=S(SampleMixSecondSum) && p<S(SampleMixSecondSum)+2 ? S(SampleMixSecondSum) : p>=S(SampleMixFirstSum) && p<S(SampleMixFirstSum)+2 ? S(SampleMixFirstSum) : S(ActiveSampleVoiceCount);uint16_t v=at==S(ActiveSampleVoiceCount) ? divisor_word : at==S(SampleMixFirstSum) ? sum1 : sum2;CHECK(p>=at && p<at+2,"division reads declared words");return (uint8_t)(v>>(8*(p-at)));}
void ugh_write(uint32_t address,uint8_t value) {CHECK(address==(unsigned)SOUND_SEG*16u+0x600+written && written<2,"ordered division output frame");output[written++]=value;}
static int reference_division(Regs *r) {uint16_t destination=0x600;
'''+cut+'''return 0;}
int main(void) {
divisor_word=nondet_u16();sum1=nondet_u16();sum2=nondet_u16();Regs r={0};r.cs=SOUND_SEG;int status=reference_division(&r);
AudioChannel voices[8]={0};AudioSampleView view={voices,1,divisor_word,0,1,sum1,sum2};AudioSampleMixWork work={2,0x600,8,0,0,2};unsigned actual=0;int fault=0;
for(unsigned i=0;i<2;i++) {AudioSampleRequest request=audio_sample_mix_next(&view,&work,0);if(request.action==AUDIO_SAMPLE_FAULT) {fault=1;break;}CHECK(request.action==AUDIO_SAMPLE_WRITE && request.destination==0x600+actual,"native division output order");CHECK(actual<written && request.value==output[actual],"truncation toward zero and wrapping unsigned output");actual++;}
CHECK((status==UGH_UNSUPPORTED)==fault && actual==written,"zero/overflow fault before partial output");CHECK(view.count==divisor_word && view.first_sum==sum1 && view.second_sum==sum2 && view.busy==1 && view.remaining==1,"division native frame");return 0;}'''
    else:
        # Actual length rejection/store cut versus maintained state transition.
        literal_import=function((ROOT/'c/sound_api.c').read_text(),'c_LoadIffSample')
        expression=literal_import[literal_import.index('    if(length>64000u)'):literal_import.index('    CALL(CSEG',literal_import.index('    if(length>64000u)'))]
        expression=expression.replace('return leave(r,f,0);','return 0;')
        code+='''static int reference_capacity(uint32_t length) {
'''+expression+'''return 1;}
int main(void) {AudioSampleImportWork work=nondet_import();work.stage=13;work.character=3;work.length&=16777215u;uint8_t byte=nondet_u8();uint32_t length=(work.length<<8)+byte;AudioSampleImportRequest request=audio_sample_import_next(&work,byte);CHECK((request.action==AUDIO_SAMPLE_IMPORT_STOP)==reference_capacity(length),"all BODY widths/capacity boundary");if(request.action==AUDIO_SAMPLE_IMPORT_STOP) CHECK(work.length==(length&65534u),"BODY rounds down even");else CHECK(work.result==65535 || request.action==AUDIO_SAMPLE_IMPORT_DONE,"rejected parser result frame");return 0;}'''
        # Rejected result is retained, not normalised: arbitrary work.result is
        # not admitted at this cut, since a fresh parser initializes FFFF.
        code=code.replace('work.stage=13;','work.result=65535;work.stage=13;')
    if a.bounded_divisor:code=code.replace('divisor_word=nondet_u16();','divisor_word=nondet_u16();__CPROVER_assume(divisor_word<=8 || divisor_word==65535);')
    harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'native/adlx_samples.c',ROOT/'native/adlx_samples.h',ROOT/'native/audio.h',ROOT/'c/sound_engine.c',ROOT/'c/sound_api.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=5,timeout=180,extra=SOLVER)
    print(a.entry,a.mode,result['result'],result['seconds'],result['failures'],flush=True);assert result['result']==('FAIL' if a.negative else 'PASS')
if __name__=='__main__':main()
