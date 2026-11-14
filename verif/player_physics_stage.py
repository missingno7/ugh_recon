"""Actual-C branch output properties with equality assertions at each seam."""
import argparse,json,re
from closure_support import ROOT,function
from player_physics_build import OUT,FILES
from player_physics_pair import pair
from player_physics_pieces import pieces,wrappers
from player_physics_proof import STAGES
from player_physics_children import platform_span
from player_physics_limits import cbmc,SMT

def make(key,folder):
    inputs=pair(folder)
    inc=folder/'pair.inc';code=inc.read_text()
    # The physical-address child theorem is separate. Both actual callers
    # receive identical arbitrary child outputs after equality of all inputs.
    code='#include "ugh.h"\nvoid px_address(Regs *);static uint16_t shared_base,shared_low,shared_high;\n'+code
    for name in ['reference_collision_address','collision_address']:
        old=function(code,name)
        code=code.replace(old,'static void '+name+'(Regs *r) {px_address(r);}\n')
    old=function(code,'physics_sample')
    a=old.index('        uint16_t x=');b=old.index('        physics_require(',a)
    contracted=old[:a]+'''        physics_require(probe.pixel_x==physics_read(r,D(PlayerPixelX)) && probe.pixel_y==physics_read(r,D(PlayerYPixels)));
        uint16_t segment=ram_segment();
        uint16_t location=(uint16_t)(shared_base+probe.columns+probe.rows*96u);
'''+old[b:]
    code='uint16_t ram_segment(void);\n'+code.replace(old,contracted)
    if key=='vertical-hit':
        native=(ROOT/'native/player_physics.c').read_text()
        old=function(native,'pp_find_platform')
        native=native.replace(old,'''static int pp_find_platform(const PlayerPhysicsWorld *w,uint16_t x,uint16_t cursor) {return landing_choice(w,x,cursor);}
''')
        declaration='#include "'+(ROOT/'native/player_physics.h').as_posix()+'"\nint landing_choice(const PlayerPhysicsWorld *,uint16_t,uint16_t);\n'
        code=declaration+code.replace('#include "'+(ROOT/'native/player_physics.c').as_posix()+'"',native)
    inc.write_text(code)
    support=(ROOT/'verif/player_physics_harness.c').read_text().split('#ifndef PLAYER_PHYSICS_NO_MAIN')[0]
    support=re.sub(r'#include <(?:stdio|stdlib|string)\.h>\n','',support)
    support=re.sub(r'#define CHECK[^\n]*', '#define CHECK(c,m) __CPROVER_assert((c),(m))',support)
    support=support.replace('#include "pair.inc"','int memcmp(const void *,const void *,size_t);void *memset(void *,int,size_t);\n#include "pair.inc"')
    support=support.replace('static Observation expected[50000];','static Observation expected[2];static unsigned epoch;static size_t watch;static int seen[2];')
    old=function(support,'observe')
    support=support.replace(old,'''static void observe(unsigned kind,uint32_t address,uint32_t value) {
 if(observations==watch){expected[epoch]=(Observation){kind,address,value};seen[epoch]=1;}
 observations++;
}
''')
    read=function(support,'px_read8')
    support=support.replace(read,'''static uint8_t pixel[10];
uint8_t px_read8(uint16_t bank,uint16_t address) {
 if(bank==DATA_SEG && address==D(LevelRainDirection))return (uint8_t)ram.rain;
 uint8_t value=pixel[read_number++%10u];observe(2,((uint32_t)bank<<16)|address,value);return value;
}
''')
    # No libc equality or summaries are used in a proof assertion.
    support='#include <stddef.h>\n'+support
    extra=''
    if key=='vertical-hit':extra='''static int choice,child_calls,reference_child_calls;
static uint16_t child_x,child_cursor,child_ax,child_cx,child_si;
int landing_choice(const PlayerPhysicsWorld *w,uint16_t x,uint16_t cursor) {
 CHECK(w->platform_count<=10 && w->platforms!=0,"landing child resource seam");
 child_calls++;child_x=x;child_cursor=cursor;return choice;
}
static void landing_contract(Regs *r,PhysicsPlan *plan) {
 CHECK(child_calls==1 && child_x==ram.player[2] && child_cursor==r->bp,"landing child exact input equality");reference_child_calls++;
 if(choice>=0) {
  if(plan) {physics_write(r,plan,D(PlayerPlatformIndices),(uint16_t)choice);physics_write(r,plan,D(PlayerHorizontalVelocities),0);physics_write(r,plan,D(PlayerVerticalVelocities),0);}
  else {px_write(r->ds,D(PlayerPlatformIndices),(uint16_t)choice);px_write(r->ds,D(PlayerHorizontalVelocities),0);px_write(r->ds,D(PlayerVerticalVelocities),0);}
 }
 r->ax=child_ax;r->cx=child_cx;r->si=child_si;
}
'''
    bodies=wrappers(key)
    if key=='vertical-hit':
        ref_search=platform_span().replace('sar(', 'reference_sar(')
        assert bodies.count(ref_search)==1 and bodies.count(platform_span())==1
        bodies=bodies.replace(ref_search,'landing_contract(r,0);',1).replace(platform_span(),'landing_contract(r,plan);',1)
    source=support+extra+'''uint16_t ram_segment(void){return ram.segment;}
void px_address(Regs *r) {
 CHECK(px_read(r->ds,(uint16_t)(D(PlayerPixelX)+r->bx))==ram.player[2] && px_read(r->ds,(uint16_t)(D(PlayerYPixels)+r->bx))==ram.player[3],"address child cached input equality");
 CHECK(px_read(r->ds,D(VgaRowStrideBytes))==ram.stride && px_read(r->cs,G(BackgroundPagePointer))==ram.page && px_read(r->cs,(uint16_t)(G(BackgroundPagePointer)+2))==ram.segment,"address child resource input equality");
 r->ax=shared_low;r->dx=shared_high;r->si=shared_base;r->es=ram.segment;
}
static int positive,continuation;
'''+bodies
    source+='''int main(void) {
 PhysicsRam arbitrary;ram=arbitrary;actor_index=0;ram.platform[9][0]=65535;
 size_t arbitrary_watch;watch=arbitrary_watch;
 uint8_t any_pixels[10];for(unsigned i=0;i<10;i++)pixel[i]=any_pixels[i];
 uint16_t arbitrary_base,arbitrary_low,arbitrary_high;shared_base=arbitrary_base;shared_low=arbitrary_low;shared_high=arbitrary_high;
 __CPROVER_assume(ram.difficulty<3);__CPROVER_assume((int16_t)ram.segment!=DATA_SEG);
 Regs r;r.cs=GAME_SEG;r.ds=DATA_SEG;r.ss=0x9000;r.sp=0x8000;r.bx=0;
 PhysicsPlan plan;physics_open(&r,&plan);CHECK(plan.active,"actual bridge projection accepts full scalar state and valid prefix");
 PlayerPhysicsProcess *process=&plan.process;
 process->water_state=(int8_t)(r.cx>>8);
 process->candidate=r.di;process->cursor=r.bp;
 int direction;__CPROVER_assume(direction==0 || direction==1);process->positive=positive=direction;
 process->plane=(uint8_t)r.cx;__CPROVER_assume(process->plane<4);
 uint16_t columns,rows;process->columns=columns;process->rows=rows;
 process->sample=(uint8_t)r.ax;CHECK(process->sample==(uint8_t)r.ax,"exact sampler result seam");
'''
    if key=='initial':source+='process->stage=PP_INITIAL;\n'
    if key in ['horizontal-scan','vertical-scan']:
        source+='''reference_collision_address(&r);r.es=ram.segment;
 r.si=(uint16_t)(r.si+columns+rows*96u);
 CHECK(r.si==(uint16_t)(shared_base+columns+rows*96u),"exact cached-origin/address seam");
'''
        if key=='horizontal-scan':source+='__CPROVER_assume(rows==0);r.dx=0x3cf;\n'
        else:source+='__CPROVER_assume(columns==0);\n'
        source+='r.cx=(uint16_t)((r.cx&0xff00u)|process->plane);\n'
    if key in ['horizontal-hit','vertical-hit']:
        source+='r.flags=(uint16_t)((r.flags&~SF)|(process->sample&128u));\n'
    if key=='horizontal-end':source+='r.sp=0x7ffe;__CPROVER_assume((int8_t)(ram.stack[3]>>8)==process->water_state);\n'
    if key=='vertical-hit':source+='int arbitrary_choice;__CPROVER_assume(arbitrary_choice>=-1 && arbitrary_choice<10);choice=arbitrary_choice;uint16_t aa,cc,ii;child_ax=aa;child_cx=cc;child_si=ii;\n'
    source+='''PhysicsRam initial=ram;Regs left=r,right=r;
 process->count=process->consumed=0;process->failed=0;
 PlayerPhysicsProcess old_process=*process;
'''
    source+=STAGES[key]+'(process);CHECK(!process->failed,"complete bounded branch journal");\n'
    source+='''PlayerPhysicsStage next=process->stage;process->stage=PP_FINISHED;
 unsigned plane_after=process->plane;uint16_t columns_after=process->columns,rows_after=process->rows;
 uint16_t cursor_after=process->cursor,candidate_after=process->candidate;int positive_after=process->positive;
 int water_after=process->water_state;
 epoch=modern=observations=read_number=0;continuation=-1;positive=direction;int a=reference_piece(&left);
 PhysicsRam final=ram;unsigned count=observations;int reference_next=continuation;
 ram=initial;epoch=modern=1;observations=read_number=0;continuation=-1;positive=direction;
 int b=bridge_piece(&right,&plan);
 CHECK(a==b && process->consumed==process->count && !process->failed,"all published events consumed exactly");
 CHECK(observations==count && seen[0]==seen[1],"complete observation length");
 if(seen[0])CHECK(expected[0].kind==expected[1].kind && expected[0].address==expected[1].address && expected[0].value==expected[1].value,"arbitrary ordered store/port/read observation");
 for(unsigned i=0;i<sizeof(Regs);i++)CHECK(((unsigned char *)&left)[i]==((unsigned char *)&right)[i],"complete retained register/flag ABI");
 size_t watched;__CPROVER_assume(watched<sizeof(ram));CHECK(((unsigned char *)&ram)[watched]==((unsigned char *)&final)[watched],"arbitrary full normalized RAM byte");
 CHECK(physics_projection(&right,&plan),"working player/world projection at matching cut");
 CHECK(process->player==old_process.player && process->world==old_process.world && !process->awaiting_reply,"working-owner identity and complete reply frame");
'''
    changed={'initial':{'water_state'},'horizontal':{'candidate','cursor','plane','columns','rows','positive'},
      'horizontal-scan':{'plane','columns','sample'},'horizontal-hit':{'cursor'},'horizontal-end':set(),
      'vertical':{'candidate','cursor','plane','columns','rows','positive'},'vertical-scan':{'rows','sample'},
      'vertical-hit':{'cursor'},'vertical-end':set()}
    for member in ['candidate','cursor','plane','columns','rows','water_state','positive','sample']:
        if member not in changed[key]:source+=f'CHECK(process->{member}==old_process.{member},"every retained private continuation scalar");\n'
    if key=='initial':source+='CHECK(water_after==(int8_t)(left.cx>>8) && next==reference_next,"water and attachment branch seam");\n'
    if key in ['horizontal','vertical']:
        source+='CHECK(candidate_after==left.di && cursor_after==left.bp && next==reference_next,"candidate/cursor and cache-equality seam");\n'
        source+='if(reference_next=='+('PP_HORIZONTAL_SCAN' if key=='horizontal' else 'PP_VERTICAL_SCAN')+')CHECK(positive_after==positive,"signed direction seam");\n'
        if key=='horizontal':source+='CHECK(plane_after==(uint8_t)left.cx && rows_after==0,"horizontal plane seam");\n'
        else:source+='CHECK(plane_after==((plan.player.pixel_x+37u)&3u) && columns_after==0,"vertical plane seam");\n'
        source+='CHECK(left.si==(uint16_t)(shared_base+columns_after+rows_after*96u),"cache-origin/displacement integration seam");\n'
    if key in ['horizontal-hit','vertical-hit']:
        source+='CHECK(cursor_after==left.bp && next==reference_next,"collision, reflection, platform and loop-backedge seam");\n'
    if key=='vertical-hit':source+='CHECK(reference_child_calls==2*child_calls,"both parents use exactly the same landing child");\n'
    if key=='horizontal-end':source+='CHECK(next==PP_VERTICAL && process->water_state==(int8_t)(left.cx>>8),"horizontal completion and saved water-state transition");\n'
    if key=='vertical-end':source+='CHECK(next==PP_FINISHED,"normal completion transition");\n'
    if key in ['horizontal-scan','vertical-scan']:
        source+='CHECK(next==reference_next && process->sample==(uint8_t)left.ax && !process->awaiting_reply,"service reply and transition seam");\n'
        source+='CHECK(cursor_after==left.bp && candidate_after==left.di,"complete cursor/candidate frame across sampling child");\n'
        if key=='horizontal-scan':source+='CHECK(plane_after==(uint8_t)left.cx,"plane scan continuation");\n'
    source+='return 0;}\n'
    path=folder/'harness.c';path.write_text(source)
    return path,[*inputs,ROOT/'verif/player_physics_harness.c',ROOT/'verif/player_physics_pieces.py',ROOT/'verif/player_physics_stage.py',ROOT/'verif/player_physics_children.py']
def main():
    ap=argparse.ArgumentParser();ap.add_argument('key',choices=list(STAGES));ap.add_argument('--timeout',type=int,default=120);ap.add_argument('--smt',action='store_true');a=ap.parse_args()
    folder=OUT/'stages'/a.key;folder.mkdir(parents=True,exist_ok=True);harness,inputs=make(a.key,folder)
    result=cbmc(harness,folder,inputs,unwind=40,timeout=a.timeout,defines=['-DACTOR_VERIFY'],extra=[*(SMT if a.smt else []),'--no-array-field-sensitivity'])
    print(a.key,result['result'],round(result['seconds'],3),result.get('peak_private_bytes'),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
