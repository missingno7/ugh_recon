"""Actual-C alternating histories, demo seeds and loader history frame."""
import argparse,json
from closure_support import ROOT,function
from render_history_build import OUT,pair
from render_history_limits import cbmc,SMT

def make(mode,folder):
    inputs=pair(folder);code='#include "pair.inc"\n'+(ROOT/'verif/render_history_harness.c').read_text()
    if mode=='pages':
        code+='''
int main(void) {
 uint16_t initial[10],x[4],y[4];Regs r,a,b;
 for(unsigned i=0;i<10;i++) ram[i]=initial[i];
 service_after[0]=a;service_after[1]=b;service_status[0]=service_status[1]=0;actor_index=0;
 compare(5,r);ram[2]=65535u;
 for(unsigned frame=0;frame<4;frame++) {
  if(frame>=2) {
   CHECK(ram[6]==(uint16_t)((x[frame-2]>>5)|((x[frame-2]&32768u)?63488u:0)),"erase X belongs to same page two draws earlier");
   CHECK(ram[7]==(uint16_t)(y[frame-2]>>5),"erase Y belongs to same page two draws earlier");
  }
  uint16_t cached_x=ram[4],cached_y=ram[5];compare(0,r);
  CHECK(ram[4]==cached_x && ram[5]==cached_y,"pre-update pixel inputs survive erase");
  __CPROVER_assume(y[frame]<6144u);ram[0]=x[frame];ram[1]=y[frame];ram[2]=31;
  compare(1,r);compare(2,r);
 }
 return 0;
}
'''
    elif mode=='seeds':
        scene=(ROOT/'c/scene.c').read_text();body=function(scene,'c_InitializeDemoScripts');a=body.index('        r->ax=rd16(r->ds,r->di);');b=body.index('        r->ax=rd16(r->ds,(uint16_t)(r->di+4));',a);fragment=body[a:b]
        code+='''
#include "'''+(ROOT/'native/demo_core.c').as_posix()+'''"
static uint16_t seed_x,seed_y;
static uint16_t seed_read(uint16_t bank,uint16_t address) {CHECK(bank==DATA_SEG,"seed bank");if(address==4096)return seed_x;CHECK(address==4098,"two header words");return seed_y;}
static void seed_write(uint16_t bank,uint16_t address,uint16_t value) {
 CHECK(bank==DATA_SEG,"seed store bank");
 for(unsigned i=0;i<10;i++) if(address==(uint16_t)(bases[i]+actor_index)) {CHECK(i==0 || i==1 || (i>=4 && i<=7),"explicit seed footprint");ram[i]=value;return;}
 CHECK(0,"no other seed store");
}
#undef rd16
#undef wr16
#define rd16 seed_read
#define wr16 seed_write
static void reference_seed(Regs *r) {'''+fragment+'''}
#undef rd16
#undef wr16
int main(void) {
 uint16_t words[10];Regs r,a,b;ActorRenderStorage storage={0};ActorRenderHistory before;
 DemoMotionScene demo={0};DemoMotionScript script={0};const DemoMotionScript *scripts[1]={&script};
 for(unsigned i=0;i<10;i++) ram[i]=words[i];actor_index=0;r.ds=DATA_SEG;r.bx=0;r.di=4096;
 uint16_t header_x,header_y;seed_x=header_x;seed_y=header_y;
 script.initial_pixel_x=seed_x;script.initial_pixel_y=seed_y;
 before.pixel_x=ram[4];before.pixel_y=ram[5];before.previous_x=ram[6];before.previous_y=ram[7];before.erase_sprite=ram[8];before.erase_overlay_sprite=ram[9];storage.slots[0]=before;
 reference_seed(&r);demo_initialize(&demo,&storage,scripts,1);
 CHECK(storage.slots[0].pixel_x==ram[4] && storage.slots[0].pixel_y==ram[5] && storage.slots[0].previous_x==ram[6] && storage.slots[0].previous_y==ram[7],"actual native demo initializer matches explicit L1 seeds");
 CHECK(demo.slots[0].position.x32==ram[0] && demo.slots[0].position.y32==ram[1],"raw shifted seed positions");
 CHECK(storage.slots[0].erase_overlay_sprite==before.erase_overlay_sprite,"demo/reset preserve overlay history");
 service_after[0]=a;service_after[1]=b;service_status[0]=service_status[1]=0;
 compare(5,r);CHECK(ram[4]==seed_x && ram[5]==seed_y && ram[6]==seed_x && ram[7]==seed_y,"reset does not clear either seeded history");
 /* A stone placement owns fixed position, not pixel seeds. The separate
  * loader-frame theorem discharges this seam; stone update owns sprite. */
 uint16_t stone_x,stone_y;ram[0]=stone_x;ram[1]=stone_y;ram[2]=544;
 compare(1,r);
 CHECK(ram[6]==seed_x && ram[7]==seed_y,"first gameplay draw consumes demo caches before replacement");
 CHECK(ram[4]==(uint16_t)((stone_x>>5)|((stone_x&32768u)?63488u:0)) && ram[5]==(uint16_t)((stone_y>>5)|((stone_y&32768u)?63488u:0)),"new fixed position replaces only current cache");
 return 0;
}
'''
        inputs += [ROOT/'native/demo_core.c',ROOT/'native/demo_core.h']
    elif mode=='initialize-frame':
        code+='''
#include "'''+(ROOT/'native/demo_core.c').as_posix()+'''"
int main(void) {
 ActorRenderStorage storage={0};ActorRenderHistory before;DemoMotionScene demo={0};
 DemoMotionScript scripts[16];const DemoMotionScript *vector[16];uint16_t x[16],y[16];
 size_t count,slot;__CPROVER_assume(count<=15 && slot<16);storage.slots[slot]=before;
 for(unsigned i=0;i<16;i++) {scripts[i]=(DemoMotionScript){0};scripts[i].initial_pixel_x=x[i];scripts[i].initial_pixel_y=y[i];vector[i]=&scripts[i];}
 demo_initialize(&demo,&storage,vector,count);ActorRenderHistory actual=storage.slots[slot];
 CHECK(actual.pixel_x==(slot<count?x[slot]:before.pixel_x) && actual.previous_x==(slot<count?x[slot]:before.previous_x),"all active X seeds, inactive X histories retained");
 CHECK(actual.pixel_y==(slot<count?y[slot]:before.pixel_y) && actual.previous_y==(slot<count?y[slot]:before.previous_y),"all active Y seeds, inactive Y histories retained");
 CHECK(actual.erase_overlay_sprite==before.erase_overlay_sprite,"every overlay history survives native demo initialization");
 CHECK(actual.erase_sprite==65535u && demo.slots[slot].sprite==65535u,"all physical slots reset regardless of active prefix");
 return 0;
}
'''
        inputs += [ROOT/'native/demo_core.c',ROOT/'native/demo_core.h']
    else:
        raw=(ROOT/'c/render.c').read_text();body=function(raw,'c_LoadCurrentLevelState');a=body.index('        lodsw(r); WI(ActorDescriptors');b=body.index('        r->di=(uint16_t)(r->di+2);',a)+len('        r->di=(uint16_t)(r->di+2);');fragment=body[a:b]
        # Every load returns an arbitrary word: an overapproximation of all
        # immutable resource contents and consistent RAM maps, for frame only.
        code='''#include "'''+(ROOT/'c/ugh.h').as_posix()+'''"
void __CPROVER_assert(_Bool,const char *);void __CPROVER_assume(_Bool);
#define CHECK(c,m) __CPROVER_assert((c),(m))
static uint16_t watch_offset;static uint8_t watch;
static uint16_t loader_read(uint16_t bank,uint16_t address) {(void)bank;(void)address;uint16_t value;return value;}
static void loader_write(uint16_t bank,uint16_t address,uint16_t value) {
 CHECK(bank==DATA_SEG,"loader data bank");
 if(address==watch_offset)watch=(uint8_t)value;
 if((uint16_t)(address+1u)==watch_offset)watch=(uint8_t)(value>>8);
}
#define rd16 loader_read
#define wr16 loader_write
'''+ '\n'.join(line for line in raw.splitlines() if line.startswith('#define '))+'\n'+function(raw,'lodsw')+'''static void loader_actor(Regs *r) {for(unsigned once=0;once<1;once++) {'''+fragment+'''}}
int main(void) {
 Regs r;unsigned field,slot,byte;uint8_t initial;
 __CPROVER_assume(field<6 && slot<16 && byte<2);r.ds=DATA_SEG;
 unsigned physical;__CPROVER_assume(physical<16);r.di=(uint16_t)(physical*2);
 const uint16_t bases[]={D(ActorPixelX),D(ActorPixelY),D(ActorPreviousDrawX),D(ActorPreviousDrawY),D(ActorEraseSprite),D(ActorEraseOverlaySprite)};
 watch_offset=(uint16_t)(bases[field]+2*slot+byte);watch=initial;loader_actor(&r);
 if(field<4 || slot!=physical) CHECK(watch==initial,"loader actor contribution preserves every current/prior pixel byte and all other physical histories");
 return 0;
}
'''
        inputs += [ROOT/'c/render.c']
    return code,[*inputs,ROOT/'verif/render_history_harness.c',ROOT/'verif/render_history_sequences.py']
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['pages','seeds','initialize-frame','loader-frame']);p.add_argument('--timeout',type=int,default=600);a=p.parse_args();folder=OUT/'sequences'/a.mode;folder.mkdir(parents=True,exist_ok=True)
    code,inputs=make(a.mode,folder);source=folder/'harness.c';source.write_text(code)
    result=cbmc(source,folder,inputs,unwind=18,timeout=a.timeout,defines=['-D__CPROVER__','-DACTOR_VERIFY','-DUINT16_MAX=65535u'],extra=SMT)
    print(json.dumps({k:result[k] for k in ['result','seconds','peak_private_bytes','failures']}),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
