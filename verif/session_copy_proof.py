"""Actual 26-byte backward record copy, all relative offsets including overlap."""
import argparse
from closure_support import ROOT,function
from sequencing_build import OUT
from sequencing_limits import cbmc
def fragment(path):
    b=function(path.read_text(),'c_LoadCurrentLevelState');a=b.index('    r->si=24;');return b[a:b.index('    wr16(r->cs,G(RendererScratchWord)',a)]
def source(mode):
    s='#include "ugh.h"\n#include "'+(ROOT/'native/session.c').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert((c),(m))\n'
    s+='''typedef struct HeaderMemory {uint8_t destination[26],source[26],other;uint16_t source_base;} HeaderMemory;
static HeaderMemory memory;
static uint8_t read_byte(uint16_t at){if(at<26)return memory.destination[at];uint16_t offset=(uint16_t)(at-memory.source_base);CHECK(offset<26,"complete sparse source window");return memory.source[offset];}
static uint16_t read_word(uint16_t segment,uint16_t at){(void)segment;return (uint16_t)(read_byte(at)|((uint16_t)read_byte((uint16_t)(at+1u))<<8));}
static void store_word(uint16_t at,uint16_t value){CHECK(at<25,"only destination contribution");memory.destination[at]=(uint8_t)value;memory.destination[at+1]=(uint8_t)(value>>8);}
static uint16_t sq_word(uint16_t a,uint16_t b){CHECK(a==b,"copy cursor seam");return a;}
static int sq_bool(int a,int b){CHECK(!!a==!!b,"copy signed continuation seam");return !!a;}
#define rd16 read_word
#define WI(n,i,v) store_word((i),(v))
'''
    s+='static void original(Regs *r){'+fragment(ROOT/'c/render.c')+'}\n'
    s+='static void modern(Regs *r){'+fragment(ROOT/'native/bridge/session_bridge.c')+'}\n'
    s+='int main(void){HeaderMemory initial;memory=initial;Regs before;before.bx=initial.source_base;Regs r=before;original(&r);HeaderMemory expected=memory;Regs expected_regs=r;memory=initial;r=before;modern(&r);'
    if mode=='output':
        s+='unsigned watch;__CPROVER_assume(watch<26);CHECK(memory.destination[watch]==expected.destination[watch],"every header byte, all relative offsets and wrap overlap");'
        for f in ['ax','bx','cx','dx','si','di','bp','sp','cs','ds','es','ss','ip','flags']:s+='CHECK(r.'+f+'==expected_regs.'+f+',"copy ABI and flags");'
    elif mode=='frame':
        s+='unsigned watch;__CPROVER_assume(watch<26);CHECK(memory.source[watch]==initial.source[watch] && memory.source_base==initial.source_base && memory.other==initial.other,"all bytes outside the destination are framed, alias bytes select destination storage");'
    else:
        s+='uint8_t other;memory=initial;memory.other=other;r=before;modern(&r);unsigned watch;__CPROVER_assume(watch<26);CHECK(memory.destination[watch]==expected.destination[watch],"no arbitrary-other-byte dependence");'
    return s+'return 0;}'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['output','frame','dependence']);ap.add_argument('--reachability',action='store_true');a=ap.parse_args()
    folder=OUT/('copy-reach' if a.reachability else 'copy-proofs')/a.mode;folder.mkdir(parents=True,exist_ok=True);code=source(a.mode)
    if a.reachability:at=code.rindex('return 0;}');code=code[:at]+'CHECK(0,"REACHED_FINAL_COMPARISON");'+code[at:]
    h=folder/'harness.c';h.write_text(code);r=cbmc(h,folder,[__file__,ROOT/'native/session.c',ROOT/'native/session.h',ROOT/'native/bridge/session_bridge.c',ROOT/'c/render.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=14,timeout=600)
    print('header-copy',a.mode,r['result'],r['seconds'],flush=True)
    if a.reachability:assert r['result']=='FAIL' and r['failures'] and all('REACHED_FINAL_COMPARISON' in str(f) for f in r['failures'])
    else:assert r['result']=='PASS',r.get('failures')
if __name__=='__main__':main()
