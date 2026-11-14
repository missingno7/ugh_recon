"""Actual mixer single-voice cuts: output, complete native frame, dependence."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from adlx_samples_limits import cbmc
from adlx_samples_build import OUT
from adlx_lifetime_proofs import SOLVER
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('role',choices=['select','accumulate']);p.add_argument('mode',choices=['outputs','frame','dependence']);a=p.parse_args()
    folder=OUT/f'proof-voice-{a.role}-{a.mode}-offset-contract';folder.mkdir(parents=True,exist_ok=True)
    engine=(ROOT/'c/sound_engine.c').read_text();native=(ROOT/'native/adlx_samples.c').read_text();body=function(engine,'c_MixSampleVoicePairs')
    first=body.index('            if(!(rd8');middle=body.index('            uint16_t samples=');end=body.index('        }\n        int16_t divisor=')
    prefix=body[first:middle].replace('continue;','return 0;').replace('goto finished;','return 2;')
    begin=prefix.index('            uint16_t sample_offset=');end_offset=prefix.index(';',begin)+1
    prefix=prefix[:begin]+'uint16_t sample_offset=offset_contract(cursor,rd16(r->cs,(uint16_t)(S(SampleVoiceStepQ8)+voice)));'+prefix[end_offset:]
    suffix=body[middle:end].replace('uint16_t samples=rd16(bank,(uint16_t)(base+sample_offset));','uint16_t samples=supplied;')
    code='''#include "ugh.h"
#include "adlx_samples.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
uint16_t nondet_u16(void);unsigned nondet_uint(void);AudioState nondet_audio(void);
static AudioState reference;static AudioSampleView ref;static uint16_t source_offset;static uint8_t resource[1];
static unsigned offsets[13]={S(SampleVoiceRepeatCount),S(SampleVoiceDataPointer),S(SampleVoiceDataPointer)+2,S(SampleVoiceByteLength),S(SampleVoicePairCursor),S(SampleVoiceVolume),S(SampleVoiceStepQ8),S(SampleVoiceFlags),S(ActiveSampleVoiceCount),S(ActiveSampleVoiceMask),S(SampleMixFirstSum),S(SampleMixSecondSum),S(SampleMixPairsRemaining)};
static uint16_t get(unsigned i) {AudioChannel *v=&reference.channels[0];switch(i) {case 0:return v->repeats;case 1:return v->start.index;case 2:return 0x7100;case 3:return v->length;case 4:return v->cursor.index;case 5:return v->volume;case 6:return v->step_q8;case 7:return v->control;case 8:return ref.count;case 9:return ref.mask;case 10:return ref.first_sum;case 11:return ref.second_sum;default:return ref.remaining;}}
uint8_t ugh_read(uint32_t address) {unsigned p=address-(unsigned)SOUND_SEG*16u;for(unsigned i=0;i<13;i++) if(p>=offsets[i] && p<offsets[i]+2) return (uint8_t)(get(i)>>(8*(p-offsets[i])));CHECK(0,"declared voice reads only");return 0;}
void ugh_write(uint32_t address,uint8_t value) {unsigned p=address-(unsigned)SOUND_SEG*16u;for(unsigned i=0;i<13;i++) if(p>=offsets[i] && p<offsets[i]+2) {unsigned shift=8*(p-offsets[i]);uint16_t v=(uint16_t)((get(i)&~(255u<<shift))|((unsigned)value<<shift));switch(i) {case 0:reference.channels[0].repeats=v;return;case 4:reference.channels[0].cursor.index=v;return;case 8:ref.count=v;return;case 9:ref.mask=v;return;case 10:ref.first_sum=v;return;case 11:ref.second_sum=v;return;default:CHECK(0,"voice write frame");return;}}CHECK(0,"unbound voice write");}
'''+function(engine,'scaled_sample')
    code+='static uint16_t contract_offset,contract_cursor,contract_scale;static unsigned contract_calls;\nstatic uint16_t offset_contract(uint16_t cursor,uint16_t scale) {if(!contract_calls++) {contract_cursor=cursor;contract_scale=scale;}else CHECK(cursor==contract_cursor && scale==contract_scale,"same actual resampling arguments");return contract_offset;}\n'
    helper=function(native,'sample_offset');native=native.replace(helper,'static uint16_t sample_offset(uint16_t cursor,uint16_t scale) {return offset_contract(cursor,scale);}\n')
    code+=native
    if a.role=='select':code+='static unsigned reference_cut(Regs *r) {uint16_t voice=0;unsigned bit=1;\n'+prefix+'source_offset=(uint16_t)(base+sample_offset);return 1;}\n'
    else:code+='static void reference_cut(Regs *r,uint16_t supplied) {uint16_t voice=0,cursor;\n'+suffix+'}\n'
    code+='''static int within(uint8_t *p,void *field,unsigned n) {return p>=(uint8_t *)field && p<(uint8_t *)field+n;}
int main(void) {
reference=nondet_audio();reference.channels[0].start.window=resource;ref=(AudioSampleView){reference.channels,nondet_u16(),nondet_u16(),nondet_u16(),nondet_u16(),nondet_u16(),nondet_u16()};
AudioState state=reference;AudioSampleView view=ref;view.voices=state.channels;AudioSampleMixWork work={0};AudioSampleRequest request={0};uint16_t supplied=nondet_u16();Regs r={0};r.cs=SOUND_SEG;contract_offset=nondet_u16();
'''
    if a.mode=='frame':code+='''unsigned position=nondet_uint();__CPROVER_assume(position<sizeof state);uint8_t *w=(uint8_t *)&state+position;__CPROVER_assume(!within(w,&state.channels[0].repeats,2) && !within(w,&state.channels[0].cursor.index,2));uint8_t old=*w;
'''
    if a.role=='select':code+='unsigned left=reference_cut(&r),right=sample_voice(&view,&work,&request);\n'
    else:code+='reference_cut(&r,supplied);sample_accumulate(&view,&work,supplied);\n'
    if a.mode=='outputs':
        code+='''CHECK(ref.count==view.count && ref.mask==view.mask && ref.first_sum==view.first_sum && ref.second_sum==view.second_sum && reference.channels[0].repeats==state.channels[0].repeats && reference.channels[0].cursor.index==state.channels[0].cursor.index,"all voice/cell outputs");'''
        if a.role=='select':code+='CHECK(left==right,"retire/read/skip policy");if(right==1) CHECK(request.source.index==source_offset && request.source.window==resource,"wrapped resampling/source request");'
    elif a.mode=='frame':code+='CHECK(*w==old && view.busy==ref.busy && view.remaining==ref.remaining,"every other owner byte and control cell preserved");'
    else:
        code+='''AudioState other=nondet_audio();other.channels[0]=reference.channels[0];AudioSampleView second=ref;second.voices=other.channels;AudioSampleMixWork second_work={0};AudioSampleRequest second_request={0};
'''
        # Use the original common inputs, not the updated reference poststate.
        code=code.replace('AudioState state=reference;','AudioState before=reference;AudioSampleView inputs=ref;AudioState state=reference;').replace('other.channels[0]=reference.channels[0];AudioSampleView second=ref;','other.channels[0]=before.channels[0];AudioSampleView second=inputs;')
        if a.role=='select':code+='unsigned second_action=sample_voice(&second,&second_work,&second_request);CHECK(right==second_action,"no other owner input selects voice action");if(right==1) CHECK(request.source.index==second_request.source.index,"no other input in source request");'
        else:code+='sample_accumulate(&second,&second_work,supplied);'
        code+='CHECK(view.count==second.count && view.mask==second.mask && view.first_sum==second.first_sum && view.second_sum==second.second_sum && state.channels[0].repeats==other.channels[0].repeats && state.channels[0].cursor.index==other.channels[0].cursor.index,"no omitted owner input affects voice outputs");'
    code+='return 0;}\n';harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'native/adlx_samples.c',ROOT/'native/adlx_samples.h',ROOT/'native/audio.h',ROOT/'c/sound_engine.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=15,timeout=180,extra=SOLVER)
    print(a.role,a.mode,result['result'],result['seconds'],result['failures'],flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
