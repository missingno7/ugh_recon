"""Actual pass-completion statements versus the native section transition."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from adlx_loader_solver import cbmc
from adlx_sections_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['outputs','frame','dependence']);p.add_argument('--timeout',type=int,default=180);p.add_argument('--word-memory',action='store_true');a=p.parse_args()
    folder=OUT/('proof-finish-'+a.mode+('-word' if a.word_memory else ''));folder.mkdir(parents=True,exist_ok=True)
    api=(ROOT/'c/sound_api.c').read_text();native=(ROOT/'native/adlx_sections.c').read_text()
    body=function(api,'c_ScanMusicEvents');start=body.index('        uint16_t dest=pass?');end=body.index('\n    }\n    r->es=SOUND_SEG;',start);fragment=body[start:end]
    code='''#include "ugh.h"
#include "adlx_sections.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
uint8_t ugh_mem[UGH_MEM_SIZE];
AudioState nondet_audio(void);uint16_t nondet_u16(void);uint32_t nondet_u32(void);uint8_t nondet_u8(void);
static AudioState reference;static uint8_t stack[16];
static uint16_t read_word(uint16_t,uint16_t);static void write_word(uint16_t,uint16_t,uint16_t);
#define rd16 read_word
#define wr16 write_word
'''+api[:api.index('/* Word device mask;')]
    code+='''static uint16_t read_word(uint16_t bank,uint16_t p) {
 if(bank==SOUND_SEG) {CHECK(p==S(MusicTicksPerUnit),"finish scalar read");return reference.ticks_per_unit;}
 uint32_t a=lin(bank,p);return (uint16_t)(ugh_read(a)|(unsigned)ugh_read(a+1)*256u);
}
static void write_word(uint16_t bank,uint16_t p,uint16_t value) {
 CHECK(bank==SOUND_SEG,"finish scalar store bank");
 if(p==S(FirstScannedEvent)) reference.section_start.index=value;
 else if(p==S(FirstScannedEvent)+2) reference.section_start.window=ugh_mem+(unsigned)value*16u;
 else if(p==S(MainAdlxSectionEnd)) reference.section_end.index=value;
 else {CHECK(p==S(MainAdlxSectionEnd)+2,"finish pointer store");reference.section_end.window=ugh_mem+(unsigned)value*16u;}
}
uint8_t ugh_read(uint32_t a) {
 unsigned b=(unsigned)SOUND_SEG*16u+S(ScannedMusicClockTicks);
 if(a>=b && a<b+4) return (uint8_t)(reference.scanned_ticks>>(8*(a-b)));
 CHECK(a>=0x80000 && a<0x80010,"finish stack read");return stack[a-0x80000];
}
void ugh_write(uint32_t a,uint8_t value) {
 unsigned b=(unsigned)SOUND_SEG*16u+S(ScannedMusicClockTicks);
 if(a>=b && a<b+4) {unsigned s=8*(a-b);reference.scanned_ticks=(reference.scanned_ticks&~((uint32_t)255<<s))|((uint32_t)value<<s);return;}
 CHECK(a>=0x80000 && a<0x80010,"finish stack write");stack[a-0x80000]=value;
}
'''+function(native,'audio_section_scan_finish')
    code+='''static void reference_finish(Regs *r,AudioScanWork *work) {
 Frame f={0,r->bp,r->si,r->di,r->ds};unsigned pass=work->pass;uint32_t total=work->total,threshold=work->threshold;
 uint16_t p=work->cursor.index,s=0x6000;
'''+fragment+'''
 work->pass++;if(work->pass==2) {reference.section_loop_enabled=1;work->exit=AUDIO_SCAN_DONE;}
 else {reference.scanned_ticks=total;work->threshold=threshold;}
}
static void equal(const AudioState *a,const AudioState *b,const AudioScanWork *x,const AudioScanWork *y) {
 CHECK(a->scanned_ticks==b->scanned_ticks && a->section_loop_enabled==b->section_loop_enabled,"pass clocks/enable word");
 CHECK(a->section_start.window==b->section_start.window && a->section_start.index==b->section_start.index && a->section_end.window==b->section_end.window && a->section_end.index==b->section_end.index,"both section pointers");
 CHECK(x->pass==y->pass && x->exit==y->exit && (x->exit==AUDIO_SCAN_DONE || x->threshold==y->threshold),"next pass or terminal phase");
}
static int within(uint8_t *p,void *v,unsigned n) {return p>=(uint8_t *)v && p<(uint8_t *)v+n;}
int main(void) {
 AudioScanWork work={0};work.pass=(uint8_t)(nondet_u8()&1u);work.total=nondet_u32();work.threshold=nondet_u32();work.next_units=nondet_u16();work.cursor.index=nondet_u16();work.cursor.window=ugh_mem+0x60000;
 reference=(AudioState){0};reference.scanned_ticks=nondet_u32();reference.ticks_per_unit=nondet_u16();reference.section_loop_enabled=nondet_u16();
 reference.section_start.window=reference.section_end.window=ugh_mem;reference.section_start.index=nondet_u16();reference.section_end.index=nondet_u16();
 AudioState native=reference;
'''
    if a.mode=='outputs':
        code+='''Regs r={0};r.ss=0x8000;stack[6]=(uint8_t)work.next_units;stack[7]=(uint8_t)(work.next_units>>8);
 AudioScanWork expected=work;reference_finish(&r,&expected);audio_section_scan_finish(&native,&work);equal(&reference,&native,&expected,&work);
'''
    elif a.mode=='frame':
        code+='''native=nondet_audio();unsigned i=nondet_u16();__CPROVER_assume(i<sizeof(native));uint8_t *p=(uint8_t *)&native+i,old=*p;
 __CPROVER_assume(!within(p,&native.scanned_ticks,4));
 if(work.pass==0) __CPROVER_assume(!within(p,&native.section_start,sizeof(native.section_start)));
 else __CPROVER_assume(!within(p,&native.section_end,sizeof(native.section_end)) && !within(p,&native.section_loop_enabled,2));
 audio_section_scan_finish(&native,&work);CHECK(*p==old,"all other pass completion bytes unchanged");
'''
    else:
        code+='''native=nondet_audio();AudioState other=nondet_audio();other.scanned_ticks=native.scanned_ticks;other.ticks_per_unit=native.ticks_per_unit;
 other.section_start=native.section_start;other.section_end=native.section_end;other.section_loop_enabled=native.section_loop_enabled;
 AudioScanWork second=work;audio_section_scan_finish(&native,&work);audio_section_scan_finish(&other,&second);equal(&native,&other,&work,&second);
'''
    code+='return 0;}\n'
    if a.word_memory:
        declarations='''static uint32_t read_dword(uint16_t bank,uint16_t offset);
static void write_dword(uint16_t bank,uint16_t offset,uint32_t value);
static uint16_t argument_units;
#define rd32 read_dword
#define wr32 write_dword
'''
        code=code.replace('#define rd16 read_word',declarations+'#define rd16 read_word',1)
        code=code.replace('uint32_t a=lin(bank,p);return', 'if(bank==0x8000 && p==6) return argument_units;\n uint32_t a=lin(bank,p);return',1)
        pos=code.index('static void reference_finish(')
        code=code[:pos]+'''static uint32_t read_dword(uint16_t bank,uint16_t offset) {
 CHECK(bank==SOUND_SEG && offset==S(ScannedMusicClockTicks),"aligned clock read binding");return reference.scanned_ticks;
}
static void write_dword(uint16_t bank,uint16_t offset,uint32_t value) {
 CHECK(bank==SOUND_SEG && offset==S(ScannedMusicClockTicks),"aligned clock store binding");reference.scanned_ticks=value;
}
'''+code[pos:]
        code=code.replace('AudioScanWork expected=work;','argument_units=work.next_units;AudioScanWork expected=work;',1)
    harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'native/adlx_sections.c',ROOT/'native/adlx_sections.h',ROOT/'native/audio.h',ROOT/'c/sound_api.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=15,timeout=a.timeout,
        extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
    print(a.mode,result['result'],result['seconds'],result['failures'],flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
