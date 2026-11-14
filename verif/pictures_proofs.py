"""Split actual-C picture contracts; no replacement model of the reference."""
import argparse
from pathlib import Path
from closure_support import ROOT,function
from pictures_build import OUT
from pictures_limits import cbmc
from adlx_lifetime_proofs import SOLVER

def main():
 p=argparse.ArgumentParser();p.add_argument('entry',choices=['palette-prefix','palette-step','input','show','startup']);p.add_argument('--negative',action='store_true');a=p.parse_args()
 folder=OUT/f'proof-{a.entry}{"-negative" if a.negative else ""}';folder.mkdir(parents=True,exist_ok=True)
 native=(ROOT/'native/pictures.c').read_text();bridge=(ROOT/'native/bridge/pictures_bridge.c').read_text();video=(ROOT/'c/video.c').read_text();scene=(ROOT/'c/scene.c').read_text()
 if a.negative:
  old,new={'palette-prefix':('PICTURE_PALETTE_BYTES/2','PICTURE_PALETTE_BYTES/2-1'),'palette-step':('copy->source+2*','copy->source+3*'),'input':('scan==1 ? 1','scan==2 ? 1'),'show':('PICTURE_UPLOAD,PICTURE_SWAP','PICTURE_SWAP,PICTURE_UPLOAD'),'startup':('{PICTURE_PRESENT,140}','{PICTURE_PRESENT,141}')}[a.entry];assert old in native;native=native.replace(old,new)
 code='#include "platform.h"\n#include "pictures.h"\n#define CHECK(c,m) __CPROVER_assert(c,m)\nuint8_t nondet_u8(void);uint16_t nondet_u16(void);Regs nondet_regs(void);\n'+native
 code+='''static unsigned side;
static void equal(Regs a,Regs b) {CHECK(a.ax==b.ax && a.bx==b.bx && a.cx==b.cx && a.dx==b.dx && a.si==b.si && a.di==b.di && a.bp==b.bp && a.sp==b.sp && a.cs==b.cs && a.ds==b.ds && a.es==b.es && a.ss==b.ss && a.ip==b.ip && a.flags==b.flags,"complete outputs and frame");}
typedef struct Access {uint32_t address;uint8_t value;} Access;
static Access read_events[2][32],write_events[2][32];static unsigned nr[2],nw[2];static uint8_t delivered[32];
uint8_t ugh_read(uint32_t address) {unsigned n=nr[side]++;CHECK(n<32,"read log bound");read_events[side][n]=(Access){address,delivered[n]};return delivered[n];}
void ugh_write(uint32_t address,uint8_t value) {unsigned n=nw[side]++;CHECK(n<32,"write log bound");write_events[side][n]=(Access){address,value};}
static void accesses(void) {CHECK(nr[0]==nr[1] && nw[0]==nw[1],"access counts");for(unsigned i=0;i<nr[0];i++) CHECK(read_events[0][i].address==read_events[1][i].address && read_events[0][i].value==read_events[1][i].value,"ordered read footprint");for(unsigned i=0;i<nw[0];i++) CHECK(write_events[0][i].address==write_events[1][i].address && write_events[0][i].value==write_events[1][i].value,"ordered byte writes");}
static Regs responses[6],calls[2][8];static uint16_t targets[2][8],return_ips[2][8];static unsigned count[2];static uint8_t failures[6];
int ugh_call_near(uint16_t target,uint16_t ret,Regs *r) {unsigned i=count[side]++;CHECK(i<6,"service bound");calls[side][i]=*r;targets[side][i]=target;return_ips[side][i]=ret;*r=responses[i];return failures[i];}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r) {unsigned i=count[side]++;CHECK(i<8,"tail log bound");calls[side][i]=*r;targets[side][i]=target;return_ips[side][i]=bank;return 7;}
static void services(void) {CHECK(count[0]==count[1],"service prefix count");for(unsigned i=0;i<count[0];i++) {equal(calls[0][i],calls[1][i]);CHECK(targets[0][i]==targets[1][i] && return_ips[0][i]==return_ips[1][i],"ordered service identities and frames");}}
'''
 # Original local helpers, not hand translations of their effects.
 code+=function(video,'push')+function(video,'pop')+function(video,'call')
 code+='#define CALL(name,ret) do {int st=ugh_call_near(G(name),ret,r);if(st) return st;} while(0)\n#define PCALL(name,ret) CALL(name,ret)\n'
 if a.entry=='input':
  ref=function(scene,'c_ShowPackedPictureAndWait');ref=ref[ref.index('    set_al(r,'):ref.rindex('}')]
  actual=function(bridge,'c_ShowPackedPictureAndWait');actual=actual[actual.index('set_al(r,'):actual.index('\n }\n}')]
  code+='static int reference(Regs *r) {'+ref+'}\nstatic int actual(Regs *r) {'+actual+'}\n'
  code+='int main(void) {Regs r=nondet_regs(),s=r;CHECK(reference(&r)==actual(&s),"status");equal(r,s);return 0;}'
 elif a.entry=='palette-step':
  ref=function(video,'c_UnpackPictureAndCopyPalette');ref=ref[ref.index('        uint16_t v='):ref.index('    } while')]
  actual=function(bridge,'c_UnpackPictureAndCopyPalette');actual=actual[actual.index('  uint16_t value='):actual.index(' } while')]
  code+='static void reference(Regs *r) {'+ref+'}\nstatic void actual(Regs *r) {PicturePaletteCopy copy={r->si,r->di,r->cx,(int8_t)((r->flags&DF) ? -1 : 1)};'+actual+'CHECK(copy.source==r->si && copy.destination==r->di && copy.remaining==r->cx,"next native cursor agrees with live loop state");}\n'
  code+='int main(void) {for(unsigned i=0;i<32;i++) delivered[i]=nondet_u8();Regs r=nondet_regs();__CPROVER_assume(r.cx>=1 && r.cx<=384);Regs s=r;side=0;reference(&r);side=1;actual(&s);equal(r,s);accesses();return 0;}'
 elif a.entry=='palette-prefix':
  ref=function(video,'c_UnpackPictureAndCopyPalette');ref=ref[ref.index('{')+1:ref.index('    do {')]
  actual=function(bridge,'c_UnpackPictureAndCopyPalette');actual=actual[actual.index('{')+1:actual.index(' do {')]
  code+='static int reference(Regs *r) {'+ref+'return 0;}\nstatic int actual(Regs *r) {'+actual+'return 0;}\n'
  code+='int main(void) {for(unsigned i=0;i<32;i++) delivered[i]=nondet_u8();responses[0]=nondet_regs();failures[0]=nondet_u8()&1;Regs r=nondet_regs(),s=r;side=0;int first=reference(&r);side=1;int second=actual(&s);CHECK(first==second,"error prefix");equal(r,s);accesses();services();return 0;}'
 else:
  name='ShowPackedPictureAndWait' if a.entry=='show' else 'ShowStartupPictures'
  if a.entry=='startup':code+=function(bridge,'resource_segment')
  code+=function(scene,'c_'+name).replace('c_'+name+'(','reference(')+function(bridge,'c_'+name).replace('c_'+name+'(','actual(')
  code+='int main(void) {for(unsigned i=0;i<32;i++) delivered[i]=nondet_u8();for(unsigned i=0;i<6;i++) {responses[i]=nondet_regs();failures[i]=nondet_u8()&1;}Regs r=nondet_regs(),s=r;side=0;int first=reference(&r);side=1;int second=actual(&s);CHECK(first==second,"full entry status or terminal tail");equal(r,s);accesses();services();return 0;}'
 harness=folder/'harness.c';harness.write_text(code)
 result=cbmc(harness,folder,[Path(__file__),ROOT/'native/pictures.c',ROOT/'native/pictures.h',ROOT/'native/bridge/pictures_bridge.c',ROOT/'c/video.c',ROOT/'c/scene.c'],unwind=33,timeout=60,extra=SOLVER)
 print(a.entry,result['result'],result['seconds'],result['failures'][:3],flush=True);assert result['result']==('FAIL' if a.negative else 'PASS'),result['result']
if __name__=='__main__':main()
