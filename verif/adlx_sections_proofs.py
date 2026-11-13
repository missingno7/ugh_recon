"""Small actual-C section properties; shared capped solver wrapper, no model."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from adlx_loader_solver import cbmc
from adlx_sections_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['dispatch','tick','tick-frame','tick-dependence']);p.add_argument('--negative',action='store_true');p.add_argument('--timeout',type=int,default=180);a=p.parse_args()
    assert 0<a.timeout<=600
    folder=OUT/f'proof-{a.mode}{"-negative" if a.negative else ""}';folder.mkdir(parents=True,exist_ok=True)
    native=(ROOT/'native/adlx_sections.c').read_text();bridge=(ROOT/'native/bridge/adlx_sections_bridge.c').read_text();literal=(ROOT/'c/adlib.c').read_text();api=(ROOT/'c/sound_api.c').read_text()
    code='''#include "ugh.h"
#include "adlx_sections.h"
#define C(n) UGH_O_C_##n
#define CHECK(c,m) __CPROVER_assert(c,m)
uint8_t ugh_mem[UGH_MEM_SIZE];
uint16_t nondet_u16(void);uint32_t nondet_u32(void);uint8_t nondet_u8(void);AudioState nondet_audio(void);
'''
    if a.mode=='dispatch':
        code+='''static uint16_t words[14];
uint8_t ugh_read(uint32_t address) {
 unsigned base=(unsigned)UGH_SEG_C*16u+C(ScanMusicEvents)+0x2c8;
 CHECK(address>=base && address<base+28,"table read footprint");
 unsigned p=address-base;return (uint8_t)(words[p/2]>>(8*(p&1u)));
}
void ugh_write(uint32_t p,uint8_t b) {(void)p;(void)b;CHECK(0,"classification read-only");}
'''
        code+=function(api,'scan_arm')+function(bridge,'section_table')
        f=function(native,'audio_section_classify')
        if a.negative:f=f.replace('i=0;i<7','i=1;i<7')
        code+=f+'''int main(void) {
 for(unsigned i=0;i<14;i++) words[i]=nondet_u16();
 uint8_t code=nondet_u8();Regs r={0};r.cs=UGH_SEG_C;AudioScanDispatch table[7];section_table(&r,table);
 int expected=scan_arm(r.cs,(uint8_t)(code&240u));AudioScanAction result=audio_section_classify(table,code);
 CHECK((result==AUDIO_SCAN_BAD ? -1 : (int)result)==expected,"modified table target and first-match classification");return 0;
}
'''
    else:
        code+='''static AudioState reference;
uint8_t ugh_read(uint32_t address) {
 unsigned p=address-(unsigned)SOUND_SEG*16u;uint16_t value=0;
 if((p&65534u)==S(AdlxTickCount)) value=(uint16_t)reference.ticks;
 else if((p&65534u)==S(AdlxTickHighWord)) value=(uint16_t)(reference.ticks>>16);
 else if((p&65534u)==S(AdlxPlaybackGuard)) value=reference.playback_guard;
 else if((p&65534u)==S(CurrentAdlxSlot)) value=reference.current_channel;
 else if((p&65534u)==S(MainAdlxPlaying)) value=reference.playing;
 else if((p&65534u)==S(MainAdlxDeadlineLow)) value=(uint16_t)reference.channels[12].deadline;
 else if((p&65534u)==S(MainAdlxDeadlineHigh)) value=(uint16_t)(reference.channels[12].deadline>>16);
 else if((p&65534u)==S(MainAdlxSectionLoopEnabled)) value=reference.section_loop_enabled;
 else if((p&65534u)==S(MainAdlxSectionEnd)) value=reference.section_end.index;
 else if((p&65534u)==S(AudioChannelStates)+8*42+40) value=reference.channels[8].control;
 else if((p&65534u)==S(AudioChannelStates)+8*42+30) value=(uint16_t)reference.channels[8].deadline;
 else if((p&65534u)==S(AudioChannelStates)+8*42+32) value=(uint16_t)(reference.channels[8].deadline>>16);
 else CHECK(0,"scheduler read footprint");return (uint8_t)(value>>(8*(p&1u)));
}
void ugh_write(uint32_t address,uint8_t value) {
 unsigned p=address-(unsigned)SOUND_SEG*16u;
 if((p&65534u)==S(AdlxPlaybackGuard)) {unsigned shift=8*(p&1u);reference.playback_guard=(uint16_t)((reference.playback_guard&~(255u<<shift))|((unsigned)value<<shift));return;}
 if((p&65534u)==S(CurrentAdlxSlot)) {unsigned shift=8*(p&1u);reference.current_channel=(uint16_t)((reference.current_channel&~(255u<<shift))|((unsigned)value<<shift));return;}
 CHECK(p>=S(AdlxTickCount) && p<S(AdlxTickCount)+4,"scheduler clock store footprint");
 unsigned shift=(p-S(AdlxTickCount))*8;reference.ticks=(reference.ticks&~((uint32_t)255<<shift))|((uint32_t)value<<shift);
}
'''
        code+=''.join(function(native,n) for n in ['audio_section_tick_begin','audio_section_main_due','audio_section_apply_due','audio_section_effect_due','audio_section_main_context','audio_section_effects_begin','audio_section_effect_next','audio_section_tick_end'])
        if a.mode=='tick':
            code+=function(literal,'inc')+function(literal,'clock_tick')
            body=function(literal,'c_TickAdlxPlayback')
            main_context='wr16(r->cs,S(CurrentAdlxSlot),12);'
            effects_context='wr16(r->cs,S(CurrentAdlxSlot),8);'
            next_context='wr16(r->cs,S(CurrentAdlxSlot),inc(r,rd16(r->cs,S(CurrentAdlxSlot))));'
            for name,statement in [('main_context',main_context),('effects_context',effects_context),('next_context',next_context)]:
                assert statement in body
                code+='static void reference_'+name+'(Regs *r) {'+statement+'}\n'
            begin=body[body.index('    clock_tick(r);'):body.index('    uint16_t ax=r->ax')]
            code+='static int reference_begin(Regs *r) {\n'+begin+'return 1;}\n'
            main=body[body.index('        r->dx=rd16'):body.index('        if(due) {')]
            code+='static int reference_main(Regs *r) {if(!(rd16(r->cs,S(MainAdlxPlaying))&1)) return 0;\n'+main+'return due;}\n'
            expr=body[body.index('            if((rd16'):body.index(' {\n                rc=call',body.index('            if((rd16'))]
            code+='static int reference_apply(Regs *r) {\n'+expr+' return 1;return 0;}\n'
            effect=body[body.index('                r->ax=rd16'):body.index('                if(due) {')]
            code+='static int reference_effect(Regs *r) {r->bx=(uint16_t)(S(AudioChannelStates)+8*42);if((rd8(r->cs,(uint16_t)(r->bx+0x28))&5)!=5) return 0;\n'+effect+'return due;}\n'
            code+='''int main(void) {
 reference=nondet_audio();AudioState native=reference;Regs r={0};r.cs=SOUND_SEG;r.flags=nondet_u16();
 int expected=reference_begin(&r),actual=audio_section_tick_begin(&native);
 CHECK(expected==actual && reference.ticks==native.ticks && reference.playback_guard==native.playback_guard,"clock and guard entry");
 CHECK(reference_main(&r)==audio_section_main_due(&reference),"unsigned main deadline decision");
 r.di=reference.channels[12].cursor.index;
 CHECK(reference_apply(&r)==audio_section_apply_due(&reference),"offset-only section handoff decision");
 CHECK(reference_effect(&r)==audio_section_effect_due(&reference,8),"active effect and unsigned deadline decision");
 reference_next_context(&r);audio_section_effect_next(&native);
 CHECK(reference.current_channel==native.current_channel,"increments raw owner after callbacks, including wrap");
 reference_main_context(&r);audio_section_main_context(&native);
 CHECK(reference.current_channel==native.current_channel,"main owner context");
 reference_effects_context(&r);audio_section_effects_begin(&native);
 CHECK(reference.current_channel==native.current_channel,"initial effect owner context");
 audio_section_tick_end(&native);CHECK(native.playback_guard==0,"end clears whole guard word");return 0;}
'''
        elif a.mode=='tick-frame':
            code+='''int main(void) {
 AudioState state=nondet_audio();unsigned i=nondet_u16();__CPROVER_assume(i<sizeof(state));
 uint8_t *p=(uint8_t *)&state+i,*t=(uint8_t *)&state.ticks,*g=(uint8_t *)&state.playback_guard,*c=(uint8_t *)&state.current_channel;
 __CPROVER_assume((p<t || p>=t+4) && (p<g || p>=g+2) && (p<c || p>=c+2));uint8_t old=*p;
 audio_section_tick_begin(&state);audio_section_main_context(&state);audio_section_effects_begin(&state);audio_section_effect_next(&state);audio_section_tick_end(&state);CHECK(*p==old,"all other tick state bytes unchanged");return 0;}
'''
        else:
            code+='''int main(void) {
 AudioState a=nondet_audio(),b=nondet_audio();b.ticks=a.ticks;b.playback_guard=a.playback_guard;b.current_channel=a.current_channel;
 b.playing=a.playing;b.channels[12].deadline=a.channels[12].deadline;
 b.channels[12].cursor.index=a.channels[12].cursor.index;b.section_end.index=a.section_end.index;b.section_loop_enabled=a.section_loop_enabled;
 b.channels[8].control=a.channels[8].control;b.channels[8].deadline=a.channels[8].deadline;
 CHECK(audio_section_tick_begin(&a)==audio_section_tick_begin(&b),"entry dependence");
 CHECK(a.ticks==b.ticks && a.playback_guard==b.playback_guard,"clock/guard dependence");
 CHECK(audio_section_main_due(&a)==audio_section_main_due(&b) && audio_section_apply_due(&a)==audio_section_apply_due(&b) && audio_section_effect_due(&a,8)==audio_section_effect_due(&b,8),"no omitted decision state");
 audio_section_effect_next(&a);audio_section_effect_next(&b);CHECK(a.current_channel==b.current_channel,"raw owner dependence");return 0;}
'''
    harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'native/adlx_sections.c',ROOT/'native/adlx_sections.h',ROOT/'native/bridge/adlx_sections_bridge.c',ROOT/'native/audio.h',ROOT/'c/adlib.c',ROOT/'c/sound_api.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=15,timeout=a.timeout,
        extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
    print(a.mode,result['result'],result['seconds'],result['failures'],flush=True);assert result['result']==('FAIL' if a.negative else 'PASS')
if __name__=='__main__':main()
