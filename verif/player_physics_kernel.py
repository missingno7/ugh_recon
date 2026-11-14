"""Actual bridge projection, arbitrary-prefix consumption and completion checks."""
import argparse
from closure_support import ROOT,function
from player_physics_build import OUT,FILES
from player_physics_stage import make
from player_physics_limits import cbmc
FIELDS=['position.x32','position.y32','pixel_x','pixel_y','platform','velocity_x','velocity_y','impact','thrust','left','right','up','down']
def source(key,folder):
    harness,inputs=make('initial',folder);text=harness.read_text();text=text.replace(function(text,'main'),'')
    if key=='complete':
        inc=folder/'pair.inc';body=inc.read_text();old=function(body,'physics_require')
        body=body.replace(old,'static unsigned rejections;static void physics_require(int c){if(!c)rejections++;}\n');inc.write_text(body)
    text+='''int main(void) {
 PhysicsRam arbitrary;ram=arbitrary;actor_index=0;ram.platform[9][0]=65535;__CPROVER_assume(ram.difficulty<3);
 Regs r;r.cs=GAME_SEG;r.ds=DATA_SEG;r.bx=0;r.ss=0x9000;r.sp=0x8000;
 PhysicsPlan p;physics_open(&r,&p);CHECK(p.active,"actual constructor admits valid physical slot/prefix");
'''
    if key=='open':
        for i,f in enumerate(FIELDS):text+=f'CHECK(p.player.{f}==ram.player[{i}],"actual selected player projection");\n'
        for f,g in [('timer','timer'),('water_y','water'),('fade_rate','fade_rate'),('fade_level','fade_level')]:text+=f'CHECK(p.world.{f}==ram.{g},"actual world projection");\n'
        text+='''CHECK(p.world.rain==(uint8_t)ram.rain && p.world.impact_limit==ram.limits[ram.difficulty],"borrowed weather and difficulty limit");
 CHECK(p.world.platform_count>0 && p.world.platform_count<=10 && p.world.platforms==p.platforms,"one borrowed platform prefix");
 size_t i;__CPROVER_assume(i<p.world.platform_count);
 CHECK(p.platforms[i].left==ram.platform[i][0] && p.platforms[i].right==ram.platform[i][1] && p.platforms[i].surface_y==ram.platform[i][2],"arbitrary projected physical platform");
 CHECK((int16_t)p.platforms[p.world.platform_count-1].left<0,"negative sentinel is retained");
 if(i+1<p.world.platform_count)CHECK((int16_t)p.platforms[i].left>=0,"first negative sentinel, no silently skipped platform");
 CHECK(p.process.player==&p.player && p.process.world==&p.world && p.process.stage==PP_INITIAL && p.process.count==0 && p.process.consumed==0,"single working owner and native constructor");
 CHECK(physics_projection(&r,&p),"real verification predicate accepts complete projection");
'''
    elif key=='projection':
        text+='PlayerPhysicsView arbitrary_player;PlayerPhysicsWorld arbitrary_world;p.player=arbitrary_player;p.world=arbitrary_world;\nint expected=1;\n'
        for i,f in enumerate(FIELDS):text+=f'expected=expected && p.player.{f}==ram.player[{i}];\n'
        for f,g in [('timer','timer'),('water_y','water'),('fade_rate','fade_rate'),('fade_level','fade_level')]:text+=f'expected=expected && p.world.{f}==ram.{g};\n'
        text+='CHECK(physics_projection(&r,&p)==expected,"actual complete working-state equality predicate iff all declared fields agree");\n'
    elif key in ['write','out','complete']:
        text+='''size_t prefix;__CPROVER_assume(prefix<32);
 p.process.stage=PP_FINISHED;p.process.count=prefix+1;p.process.consumed=prefix;p.process.failed=p.process.awaiting_reply=0;
 epoch=observations=modern=0;watch=0;
'''
        if key=='write':
            text+='''unsigned field;__CPROVER_assume(field<12);uint16_t value;
 p.process.journal[prefix]=(PlayerPhysicsEvent){.kind=PP_WRITE,.field=(PlayerPhysicsField)field,.value=value};
 uint16_t address=physics_field(&p,(PlayerPhysicsField)field);physics_write(&r,&p,address,value);
 CHECK(p.process.consumed==prefix+1 && observations==1 && px_read(DATA_SEG,address)==value,"arbitrary-prefix native value/address consumption and sole selected RAM write");
 CHECK(expected[0].kind==0 && expected[0].address==(((uint32_t)DATA_SEG<<16)|address) && expected[0].value==value,"exact published write observation");
'''
        elif key=='out':
            text+='''_Bool select;uint16_t value;__CPROVER_assume(value<4);if(select)value=4;
 p.process.journal[prefix]=(PlayerPhysicsEvent){.kind=select?PP_SELECT_PLANE_REGISTER:PP_READ_PLANE,.value=value};
 uint16_t port=select?0x3ce:0x3cf;physics_out(&r,&p,port,1,value);
 CHECK(p.process.consumed==prefix+1 && observations==1 && expected[0].kind==1 && expected[0].address==port && expected[0].value==(65536u|value),"arbitrary-prefix exact port/width/native-plane binding");
'''
        else:
            text+='''_Bool leftover,awaiting,failed;p.process.count=prefix+(leftover?1u:0u);p.process.awaiting_reply=awaiting;p.process.failed=failed;
 p.process.journal[prefix]=(PlayerPhysicsEvent){.kind=PP_WRITE,.field=PF_TIMER};
 physics_complete(&r,&p);CHECK((rejections!=0)==(leftover || awaiting || failed),"actual normal completion rejects every unconsumed request and outstanding sample/failure");
'''
    elif key=='append':
        text+='''size_t prefix;__CPROVER_assume(prefix<=32);p.process.count=prefix;PlayerPhysicsEvent event;
 PlayerPhysicsProcess before=p.process;pp_append(&p.process,event);
 if(prefix<32) {CHECK(p.process.count==prefix+1,"actual append prefix bound");PlayerPhysicsEvent a=p.process.journal[prefix];CHECK(a.kind==event.kind && a.field==event.field && a.value==event.value && a.probe.pixel_x==event.probe.pixel_x && a.probe.pixel_y==event.probe.pixel_y && a.probe.columns==event.probe.columns && a.probe.rows==event.probe.rows,"actual appended event");}
 else CHECK(p.process.failed && p.process.count==32,"append capacity rejection");
 size_t at;__CPROVER_assume(at<sizeof(p.process));
 size_t count_begin=(size_t)((unsigned char *)&p.process.count-(unsigned char *)&p.process),failed_begin=(size_t)((unsigned char *)&p.process.failed-(unsigned char *)&p.process);
 size_t event_begin=(size_t)((unsigned char *)&p.process.journal-(unsigned char *)&p.process)+prefix*sizeof(event);
 if(!(at>=count_begin && at<count_begin+sizeof(p.process.count)) && !(at>=failed_begin && at<failed_begin+sizeof(p.process.failed)) && !(prefix<32 && at>=event_begin && at<event_begin+sizeof(event)))
 CHECK(((unsigned char *)&before)[at]==((unsigned char *)&p.process)[at],"arbitrary process byte frame outside appended cell/count/failure");
'''
    elif key=='poll-reply':
        text+='''p.process.stage=PP_FINISHED;p.process.count=1;p.process.consumed=0;
 p.process.journal[0]=(PlayerPhysicsEvent){.kind=PP_SAMPLE};PlayerPhysicsEvent event=player_physics_poll(&p.process);
 CHECK(event.kind==PP_SAMPLE && p.process.awaiting_reply && p.process.consumed==1,"actual poll publishes one pending sample");
 uint8_t reply;player_physics_reply(&p.process,reply);CHECK(!p.process.awaiting_reply && !p.process.failed && p.process.sample==reply,"exact reply consumption");
 event=player_physics_poll(&p.process);CHECK(event.kind==PP_DONE && !p.process.failed,"exhausted sequence terminates");
 player_physics_reply(&p.process,reply);CHECK(p.process.failed,"unsolicited reply rejected");
'''
    text+='return 0;}\n';harness.write_text(text);return harness,inputs
def main():
    ap=argparse.ArgumentParser();ap.add_argument('key',choices=['open','projection','write','out','complete','append','poll-reply']);ap.add_argument('--timeout',type=int,default=120);a=ap.parse_args()
    folder=OUT/'kernel'/a.key;folder.mkdir(parents=True,exist_ok=True);harness,inputs=source(a.key,folder)
    result=cbmc(harness,folder,[*inputs,ROOT/'verif/player_physics_kernel.py'],unwind=40,timeout=a.timeout,defines=['-DACTOR_VERIFY'],extra=['--no-array-field-sensitivity'])
    print(a.key,result['result'],round(result['seconds'],3),result.get('peak_private_bytes'),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
