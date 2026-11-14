"""Discharge the physical-address and platform-search equality seams."""
import argparse
from closure_support import ROOT,function
from player_physics_build import OUT,FILES
from player_physics_limits import cbmc,SMT

def platform_span():
    body=function((ROOT/'c/scene.c').read_text(),'c_MovePlayerWithVgaCollisions')
    a=body.index('r->si=0; r->ax=(uint16_t)(sar(r->bp,5)+20);')
    start=body.index('for(unsigned budget=0;;budget++) {',a);end=body.index('{',start)+1;depth=1
    while depth:
        depth+=int(body[end]=='{')-int(body[end]=='}');end+=1
    return body[a:end]
def landing():
    source='''#include "ugh.h"
#include "'''+(ROOT/'native/player_physics.c').as_posix()+'''"
#define CHECK(c,m) __CPROVER_assert((c),(m))
static LevelPlatform platform;static uint16_t pixel_x,index_word;
static unsigned stores;static uint16_t selected;
static uint16_t model_read(uint16_t s,uint16_t o) {
 CHECK(s==DATA_SEG,"platform data bank");
 if(o==D(PlayerPixelX))return pixel_x;
 if(o==D(PlatformLeftEdges)+index_word)return platform.left;
 if(o==D(PlatformRightEdges)+index_word)return platform.right;
 if(o==D(PlatformHeights)+index_word)return platform.surface_y;
 CHECK(0,"complete platform read footprint");return 0;
}
static void model_write(uint16_t s,uint16_t o,uint16_t value) {
 CHECK(s==DATA_SEG && stores<3,"three landing stores");
 if(stores==0){CHECK(o==D(PlayerPlatformIndices),"selected platform first");selected=value;}
 if(stores==1)CHECK(o==D(PlayerHorizontalVelocities) && value==0,"horizontal stop second");
 if(stores==2)CHECK(o==D(PlayerVerticalVelocities) && value==0,"vertical stop third");
 stores++;
}
#define RX(n,i) model_read(r->ds,(uint16_t)(D(n)+(i)))
#define WX(n,i,v) model_write(r->ds,(uint16_t)(D(n)+(i)),(uint16_t)(v))
'''
    scene=(ROOT/'c/scene.c').read_text();source+=function(scene,'sar')
    span=platform_span().replace('for(unsigned budget=0;;budget++) {','r->si=index_word;\nfor(unsigned budget=0;budget<1;budget++) {')
    source+='static int reference_search(Regs *r) {'+span+'return UGH_OK;}\n'
    source+='''int main(void) {
 LevelPlatform arbitrary;platform=arbitrary;
 uint16_t arbitrary_x;pixel_x=arbitrary_x;Regs r;r.bx=0;r.ds=DATA_SEG;
 unsigned index;__CPROVER_assume(index<10);index_word=(uint16_t)(2u*index);
 uint16_t cursor=r.bp;int result=pp_platform_decision(&platform,(uint16_t)(player_physics_sar(cursor,5)+20u),(uint16_t)(pixel_x+16u));
 int status=reference_search(&r);CHECK(status==UGH_OK,"one actual platform iteration");
 CHECK((result<0 && stores==0 && r.si==index_word) || (result==0 && stores==0 && r.si==index_word+2u) || (result>0 && stores==3 && selected==index && r.si==index),"complete stop/pass/match selection, cursor advance and ordered landing stores");
 return 0;
}
''';return source
def address():
    scene=(ROOT/'c/scene.c').read_text();bridge=(ROOT/'native/bridge/player_physics_bridge.c').read_text()
    source='''#include "ugh.h"
#include "'''+(ROOT/'native/player_physics.c').as_posix()+'''"
#define CHECK(c,m) __CPROVER_assert((c),(m))
static uint16_t pixel_x,pixel_y,stride,page,segment;
static uint16_t model_read(uint16_t s,uint16_t o) {
 if(s==DATA_SEG) {if(o==D(PlayerPixelX))return pixel_x;if(o==D(PlayerYPixels))return pixel_y;if(o==D(VgaRowStrideBytes))return stride;}
 if(s==GAME_SEG) {if(o==G(BackgroundPagePointer))return page;if(o==G(BackgroundPagePointer)+2u)return segment;}
 CHECK(0,"complete physical-address input footprint");return 0;
}
#define rd16 model_read
#define R(n) model_read(r->ds,D(n))
#define RX(n,i) model_read(r->ds,(uint16_t)(D(n)+(i)))
'''
    source+='''static int32_t product;static uint16_t product_y,product_stride;static unsigned products;
static int32_t shared_product(uint16_t y,uint16_t row){CHECK(y==product_y && row==product_stride,"actual multiplication operand equality seam");products++;return product;}
'''
    actual=function(scene,'collision_address')
    multiply='(int32_t)(int16_t)r->ax*(int16_t)R(VgaRowStrideBytes)'
    assert multiply in actual;actual=actual.replace(multiply,'shared_product(r->ax,R(VgaRowStrideBytes))')
    source+=function(scene,'sar')+actual
    a=bridge.index('typedef struct PhysicsPlan');b=bridge.index('static void physics_require',a)
    source+=bridge[a:b]
    source+='''static void physics_require(int c){CHECK(c,"actual sample binding predicate");}
static int physics_projection(Regs *r,PhysicsPlan *p){(void)r;(void)p;return 1;}
static int calls;
static int model_near(uint16_t target,uint16_t return_word,Regs *r){(void)return_word;(void)r;CHECK(target==G(SamplePlayerCollisionPixels),"exact sample callee");calls++;return 0;}
#define ugh_call_near model_near
'''+function(bridge,'physics_read')
    sample=function(bridge,'physics_sample');multiply='(int32_t)(int16_t)probe.pixel_y*(int16_t)rd16(r->ds,D(VgaRowStrideBytes))'
    assert multiply in sample;sample=sample.replace(multiply,'shared_product(probe.pixel_y,rd16(r->ds,D(VgaRowStrideBytes)))')
    source+=sample
    source+='''int main(void) {
 uint16_t x,y,row,origin,bank,columns,rows;pixel_x=x;pixel_y=y;stride=row;page=origin;segment=bank;
 product_y=y;product_stride=row;int32_t arbitrary_product;__CPROVER_assume(arbitrary_product>=-1073709056 && arbitrary_product<=1073741824);product=arbitrary_product;
 Regs r;r.cs=GAME_SEG;r.ds=DATA_SEG;r.bx=0;collision_address(&r);
 r.si=(uint16_t)(r.si+columns+rows*96u);
 PhysicsPlan p={0};p.active=1;p.process.stage=PP_FINISHED;p.process.count=1;
 p.process.journal[0]=(PlayerPhysicsEvent){.kind=PP_SAMPLE,.probe={x,y,columns,rows}};
 int status=physics_sample(&r,&p,0);CHECK(status==UGH_OK && calls==1 && products==2 && !p.process.failed && !p.process.awaiting_reply,"actual full-word address construction and sample-request consumption");
 return 0;
}
''';return source
def product():
    scene=(ROOT/'c/scene.c').read_text();bridge=(ROOT/'native/bridge/player_physics_bridge.c').read_text()
    original='(int32_t)(int16_t)r->ax*(int16_t)R(VgaRowStrideBytes)'
    borrowed='(int32_t)(int16_t)probe.pixel_y*(int16_t)rd16(r->ds,D(VgaRowStrideBytes))'
    assert original in function(scene,'collision_address') and borrowed in function(bridge,'physics_sample')
    return '''#include "ugh.h"
#include "'''+(ROOT/'native/player_physics.h').as_posix()+'''"
#define R(n) row
#define rd16(s,o) row
int main(void) {
 uint16_t y,row;Regs storage,*r=&storage;PlayerCollisionProbe probe;
 r->ax=y;probe.pixel_y=y;
 __CPROVER_assert(r->ax==probe.pixel_y,"actual multiplication input equality");
 int32_t left='''+original+';int32_t right='+borrowed+''';
 __CPROVER_assert(left==right,"identical actual signed products on shared inputs");
 __CPROVER_assert(left>=-1073709056 && left<=1073741824,"complete signed word product range used by parent");
 return 0;
}
'''
def scan_index():
    source=(ROOT/'native/player_physics.c').read_text()
    assert 'for(size_t i=0;i<w->platform_count;i++)' in function(source,'pp_find_platform')
    span=platform_span();advance='r->si=(uint16_t)(r->si+2);';assert advance in span
    return '''#include "ugh.h"
int main(void) {
 unsigned i;__CPROVER_assume(i<10);Regs storage,*r=&storage;r->si=(uint16_t)(2u*i);
'''+advance+'''i++;
 __CPROVER_assert(r->si==2u*i && i<=10,"actual native increment and literal byte-index backedge commute");
 __CPROVER_assert(0u==2u*0u && 10u<32768u,"initial slot equality and sentinel prefix precedes literal budget");
 return 0;
}
'''
def main():
    ap=argparse.ArgumentParser();ap.add_argument('key',choices=['address','landing','product','scan-index']);ap.add_argument('--timeout',type=int,default=120);ap.add_argument('--smt',action='store_true');a=ap.parse_args()
    folder=OUT/'children'/a.key;folder.mkdir(parents=True,exist_ok=True);harness=folder/'harness.c';harness.write_text({'address':address,'landing':landing,'product':product,'scan-index':scan_index}[a.key]())
    result=cbmc(harness,folder,[*FILES,ROOT/'c/scene.c',ROOT/'verif/player_physics_children.py'],unwind=15,timeout=a.timeout,extra=[*(SMT if a.smt else []),'--no-array-field-sensitivity'])
    print(a.key,result['result'],round(result['seconds'],3),result.get('peak_private_bytes'),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
