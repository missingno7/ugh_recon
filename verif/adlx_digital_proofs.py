"""Cheap actual-C digital scalar cuts; 15-second,8GB jobs only."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from adlx_facade_limits import cbmc
from adlx_digital_build import OUT
from adlx_lifetime_proofs import SOLVER

def main():
 p=argparse.ArgumentParser();p.add_argument('entry',choices=['block','poll','bank','locate']);p.add_argument('--negative',action='store_true');a=p.parse_args();folder=OUT/('proof-digital-'+a.entry+('-negative' if a.negative else ''));folder.mkdir(parents=True,exist_ok=True)
 code='#include "platform.h"\n#include "adlx_digital.h"\n#define CHECK(c,m) __CPROVER_assert(c,m)\nuint16_t nondet_u16(void);uint32_t nondet_u32(void);uint8_t nondet_u8(void);Regs nondet_regs(void);uint8_t ugh_mem[UGH_MEM_SIZE];\n'+(ROOT/'native/adlx_digital.c').read_text()
 if a.negative:code=code.replace('{20,(uint8_t)encoded','{21,(uint8_t)encoded')
 if a.entry=='block':
  literal=function((ROOT/'c/dsp.c').read_text(),'c_StartDmaSampleBlock');literal=literal[:literal.index('    set_al(r,0x14);')]+'    return UGH_OK;\n}\n';literal=literal.replace('push_word(r,r->cx);','')
  code+='''static unsigned used;static AudioDigitalWrite writes[9];
void platform_out(uint16_t port,unsigned size,uint32_t value) {CHECK(size==1 && used<9,"nine ordered byte DMA transactions");writes[used].port=port;writes[used++].value=(uint8_t)value;}
'''+literal+'''int main(void) {Regs before=nondet_regs(),r=before;CHECK(c_StartDmaSampleBlock(&r)==0,"normal prefix");AudioDmaBlock block=audio_dma_block(before.bx,before.dx,(uint8_t)(before.cx>>8));CHECK(used==9 && block.encoded_count==r.bx,"all word counts including zero");for(unsigned i=0;i<9;i++) CHECK(block.writes[i].port==writes[i].port && block.writes[i].value==writes[i].value,"actual prefix register write order and bytes");CHECK(block.commands[0]==0x14 && block.commands[1]==(uint8_t)r.bx && block.commands[2]==(uint8_t)(r.bx>>8),"DSP block opcode then low/high encoded count");return 0;}'''
 elif a.entry=='poll':
  body=function((ROOT/'c/sound_engine.c').read_text(),'c_WriteSoundBlasterDsp');cut=body[body.index('        logic(r,'):body.index('\n    set_al(r,(uint8_t)(r->ax>>8))')];cut=cut.replace('    } while(r->cx && (r->ax&0x80));','    return r->cx && (r->ax&0x80);')
  code+='static int reference(Regs *r) {'+cut+'}\nint main(void) {Regs r=nondet_regs();uint16_t count=r.cx;uint8_t value=(uint8_t)r.ax;int expected=reference(&r);AudioDspPoll poll={count,0};int actual=audio_dsp_poll(&poll,value,1);CHECK(!!expected==!!actual && poll.remaining==r.cx,"busy poll and timeout write, arbitrary remaining word");CHECK(poll.busy==!!(value&128u),"declared status dependence");return 0;}'
 elif a.entry=='locate':
  code+='\n#undef SOUND_SEG\nstatic uint16_t relocated_storage;\n#define SOUND_SEG relocated_storage\nstatic uint8_t output[64];\nvoid ugh_write(uint32_t address,uint8_t value) {unsigned at=address-0x60000u;CHECK(at==16 || at==32 || at==33 || at==48 || at==49,"only page/address/offset stores");output[at]=value;}\n'+function((ROOT/'c/sound_engine.c').read_text(),'locate_buffer')+'int main(void) {relocated_storage=nondet_u16();uint16_t buffer=nondet_u16(),skip=nondet_u16();Regs before=nondet_regs(),r=before;r.cs=0x6000;locate_buffer(&r,16,32,48,buffer,skip);AudioDmaLocation result=audio_dma_locate(relocated_storage>>12,(uint16_t)(relocated_storage<<4),buffer,skip,(uint16_t)(S(DmaMixBufferTwoOffset)+2+0x40a));CHECK(output[16]==result.header.page && (uint16_t)(output[32]+256u*output[33])==result.header.address && (uint16_t)(output[48]+256u*output[49])==result.header.offset,"all relocated origins, page-end equality and byte page wrap");CHECK(r.ax==result.final_address && r.cx==((relocated_storage&255u)|((uint16_t)result.header.page<<8)),"location scratch results");CHECK(r.bx==before.bx && r.dx==before.dx && r.si==before.si && r.di==before.di && r.bp==before.bp && r.sp==before.sp && r.ds==before.ds && r.es==before.es && r.ss==before.ss && r.ip==before.ip,"location register frame");return 0;}'
 else:
  api=(ROOT/'c/sound_api.c').read_text();expr=function(api,'c_LoadBankSoundByIndex');expr=expr[expr.index('    Far p='):expr.index('\n    r->es=SOUND_SEG;')].replace('words32(base.s,base.o)','directory')
  code+='typedef struct {uint16_t s,o;} Far;\n'+function(api,'hadd')+'static Far reference(Far base,uint32_t directory,uint16_t index) {'+expr+'return p;}\nint main(void) {Far base={nondet_u16(),nondet_u16()};uint32_t directory=nondet_u32();uint16_t index=nondet_u16();Far expected=reference(base,directory,index);CHECK(audio_bank_entry(lin(base.s,base.o),directory,index)==lin(expected.s,expected.o),"actual huge arithmetic with word-truncated index times12");return 0;}'
 h=folder/'harness.c';h.write_text(code);r=cbmc(h,folder,[Path(__file__),ROOT/'native/adlx_digital.c',ROOT/'native/adlx_digital.h',ROOT/'c/dsp.c',ROOT/'c/sound_engine.c',ROOT/'c/sound_api.c'],unwind=10,timeout=15,extra=SOLVER);print(a.entry,r['result'],r['seconds'],r['failures']);assert r['result']==('FAIL' if a.negative else 'PASS')
if __name__=='__main__':main()
