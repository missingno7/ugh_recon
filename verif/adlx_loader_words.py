"""Actual endian primitive at every wrapping word offset, including FFFF."""
from pathlib import Path
import argparse
from closure_support import ROOT,function
from adlx_loader_solver import cbmc
from adlx_loader_build import OUT
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bind-index',action='store_true');p.add_argument('--offset',type=int,choices=[0,1,65534,65535]);a=p.parse_args()
    folder=OUT/(f'proof-words-{a.offset:04x}' if a.offset is not None else 'proof-words-bound' if a.bind_index else 'proof-words');folder.mkdir(parents=True,exist_ok=True)
    source=(ROOT/'native/adlx_loader.c').read_text()
    code='''#include "ugh.h"
#include "adlx_loader.h"
#define CHECK(c,m) __CPROVER_assert(c,m)
uint8_t ugh_mem[UGH_MEM_SIZE];
typedef struct Resource {uint8_t bytes[65537];} Resource;
Resource nondet_resource(void);uint16_t nondet_u16(void);uint8_t nondet_u8(void);
static Resource resource;static uint8_t stack[16];
uint8_t ugh_read(uint32_t address) {
 if(address>=0x60000 && address<=0x70000) return resource.bytes[address-0x60000];
 CHECK(address>=0x80000 && address<0x80010,"word proof stack read");return stack[address-0x80000];
}
void ugh_write(uint32_t address,uint8_t value) {
 CHECK(address>=0x80000 && address<0x80010,"word proof stack store");stack[address-0x80000]=value;
}
'''
    code+=function(source,'audio_adlx_word')+function(source,'audio_adlx_size')+function((ROOT/'c/music_clock.c').read_text(),'c_SwapDwordByteOrder')
    code+='''int main(void) {
 resource=nondet_resource();uint16_t offset=nondet_u16();AudioCursor cursor={resource.bytes,0};
 Regs r={0};r.ss=0x8000;
 wr16(r.ss,4,rd16(0x6000,offset));wr16(r.ss,6,rd16(0x6000,(uint16_t)(offset+2)));
 c_SwapDwordByteOrder(&r);uint32_t result=audio_adlx_size(cursor,offset);
 CHECK(result==((uint32_t)r.dx*65536u+r.ax),"complete BE32 word-pair result and high word");
 CHECK(audio_adlx_word(cursor,offset)==rd16(0x6000,offset),"unaligned LE16 including contiguous FFFF boundary");
 return 0;
}
'''
    if a.offset is not None:
        code=code.replace('resource=nondet_resource();uint16_t offset=nondet_u16();',f'''resource=(Resource){{0}};uint16_t offset={a.offset};
 resource.bytes[offset]=nondet_u8();resource.bytes[(unsigned)offset+1]=nondet_u8();
 resource.bytes[(uint16_t)(offset+2)]=nondet_u8();resource.bytes[(unsigned)(uint16_t)(offset+2)+1]=nondet_u8();''')
    if a.bind_index:
        code=code.replace('static Resource resource;','static Resource resource;static uint16_t source_index;static unsigned source_read;')
        code=code.replace('return resource.bytes[address-0x60000];','''{
 unsigned mapped=address-0x60000;
 unsigned expected=(source_read<2 ? source_index : (uint16_t)(source_index+2))+(source_read&1u);
 CHECK(source_read<4 && mapped==expected,"ordinary word-read address normalization");source_read++;
 mapped=expected;return resource.bytes[mapped];}''')
        code=code.replace('uint16_t offset=nondet_u16();','uint16_t offset=nondet_u16();source_index=offset;')
        code=code.replace('CHECK(audio_adlx_word(cursor,offset)==','source_read=0;CHECK(audio_adlx_word(cursor,offset)==')
    harness=folder/'harness.c';harness.write_text(code)
    result=cbmc(harness,folder,[Path(__file__),ROOT/'native/adlx_loader.c',ROOT/'native/adlx_loader.h',ROOT/'native/audio.h',ROOT/'c/music_clock.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=6,timeout=120,
        extra=['--smt2','--z3','--external-smt2-solver','C:/tools/z3-solver-5.4.1.0/z3_solver-5.4.1.0.data/data/bin/z3.exe'])
    print(result['result'],result['seconds'],result['failures'],flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
