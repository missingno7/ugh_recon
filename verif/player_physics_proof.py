"""Small actual-C craft properties; each solver is independently capped."""
import argparse,json
from closure_support import ROOT,function
from player_physics_build import OUT,FILES
from player_physics_limits import cbmc

STAGES={'initial':'pp_initial','horizontal':'pp_horizontal','horizontal-scan':'pp_horizontal_scan',
 'horizontal-hit':'pp_horizontal_hit','horizontal-end':'pp_horizontal_end','vertical':'pp_vertical',
 'vertical-scan':'pp_vertical_scan','vertical-hit':'pp_vertical_hit','vertical-end':'pp_vertical_end'}
VOUT={'initial':['impact','thrust'],'horizontal':['velocity_x','velocity_y','thrust'],
 'horizontal-scan':[],'horizontal-hit':['velocity_x','impact'],'horizontal-end':['position.x32','pixel_x'],
 'vertical':['velocity_y','platform','thrust'],'vertical-scan':[],'vertical-hit':['velocity_y','velocity_x','impact','platform'],
 'vertical-end':['position.y32','pixel_y']}
WOUT={'initial':['timer'],'horizontal':[],'horizontal-scan':[],'horizontal-hit':[],'horizontal-end':[],
 'vertical':['timer'],'vertical-scan':[],'vertical-hit':[],'vertical-end':['fade_rate','fade_level']}
VIN={'initial':['pixel_y','platform'],'horizontal':['position.x32','pixel_x','velocity_x','velocity_y','thrust','left','right'],
 'horizontal-scan':['pixel_x','pixel_y'],'horizontal-hit':['velocity_x'],'horizontal-end':[],
 'vertical':['velocity_y','platform','thrust','position.y32','pixel_x','pixel_y','down','up'],
 'vertical-scan':['pixel_x','pixel_y'],'vertical-hit':['velocity_x','velocity_y','impact','platform','pixel_x'],
 'vertical-end':['impact']}
WIN={'initial':['timer','water_y'],'horizontal':['rain'],'horizontal-scan':[],'horizontal-hit':[],'horizontal-end':[],
 'vertical':['timer','water_y'],'vertical-scan':[],'vertical-hit':['impact_limit','platform_count','platforms'],
 'vertical-end':['fade_rate','fade_level','impact_limit']}
ALLV=['position.x32','position.y32','pixel_x','pixel_y','platform','velocity_x','velocity_y','impact','thrust','left','right','up','down']
ALLW=['timer','water_y','impact_limit','fade_rate','fade_level','rain','platform_count','platforms']
def header():
    return '#include "ugh.h"\n#include "'+(ROOT/'native/player_physics.c').as_posix()+'"\n#define CHECK(c,m) __CPROVER_assert((c),(m))\n'
def primitive(key,mode):
    scene=(ROOT/'c/scene.c').read_text();source=header()
    source+='static uint16_t ram;static uint8_t samples[10];static unsigned reads;static uint16_t origin,segment;\n'
    source+='''static uint16_t model_read(uint16_t s,uint16_t o){(void)s;(void)o;return ram;}
static void model_write(uint16_t s,uint16_t o,uint16_t v){(void)s;(void)o;ram=v;}
static uint8_t model_read8(uint16_t s,uint16_t o) {
 static const uint16_t delta[]={0,3,5,0x720,0x723,0x725,0x240,0x245,0x480,0x485};
 CHECK(reads<10,"ten sample bound");CHECK(s==segment && o==(uint16_t)(origin+delta[reads]),"complete ordered read footprint");
 return samples[reads++];
}
#define rd16 model_read
#define wr16 model_write
#define rd8 model_read8
'''
    for name in ['sar','limit_velocity','reflect_velocity']:
        body=function(scene,name).replace(name+'(', 'reference_'+name+'(',1)
        if name=='reflect_velocity':body=body.replace('sar(', 'reference_sar(')
        source+=body
    samples=(ROOT/'c/demo_scripts.c').read_text();body=function(samples,'c_SamplePlayerCollisionPixels').replace('c_SamplePlayerCollisionPixels','reference_sample')
    source+=body+function((ROOT/'native/bridge/player_physics_bridge.c').read_text(),'c_SamplePlayerCollisionPixels')
    source+='int main(void) {uint16_t value;Regs r;\n'
    if key=='sar':source+='unsigned count;__CPROVER_assume(count>0 && count<16);CHECK(player_physics_sar(value,count)==reference_sar(value,count),"all word SAR and count slice");\n'
    elif key=='limit':source+='CHECK(player_physics_limit(value)==reference_limit_velocity(value),"full word signed clamps");\n'
    elif key=='reflect':source+='ram=value;uint16_t speed=value;uint16_t impact=player_physics_reflect(&speed);reference_reflect_velocity(&r,0);CHECK(ram==speed && r.ax==impact,"full word reflection and reflected-component magnitude");\n'
    elif key=='sample':
        source+='uint8_t any[10];for(unsigned i=0;i<10;i++)samples[i]=any[i];origin=r.si;segment=r.es;Regs a=r,b=r;\n'
        source+='reads=0;int left=reference_sample(&a);CHECK(reads==10,"reference ten reads");reads=0;int right=c_SamplePlayerCollisionPixels(&b);CHECK(reads==10 && left==right,"native ten reads and status");\n'
        if mode=='outputs':source+='for(unsigned i=0;i<sizeof(Regs);i++)CHECK(((unsigned char *)&a)[i]==((unsigned char *)&b)[i],"full registers and flags");\n'
        elif mode=='frame':source+='for(unsigned i=0;i<10;i++)CHECK(samples[i]==any[i],"sample input frame");for(unsigned i=2;i<26;i++)CHECK(((unsigned char *)&b)[i]==((unsigned char *)&r)[i],"register frame outside AL and flags");CHECK((b.ax&0xff00u)==(r.ax&0xff00u),"AH frame");\n'
        else:source+='uint8_t second[10];for(unsigned i=0;i<10;i++)second[i]=any[i];CHECK(player_collision_sample(second)==(uint8_t)b.ax,"result depends on exactly ten supplied bytes");\n'
    source+='return 0;}\n';return source
def native(key,mode):
    source=header()+'''int main(void) {
 PlayerPhysicsView v;PlayerPhysicsWorld w;LevelPlatform platforms[10];PlayerPhysicsProcess p;
 w.platforms=platforms;__CPROVER_assume(w.platform_count<=10);platforms[9].left=65535;
 p.player=&v;p.world=&w;p.count=p.consumed=0;p.failed=p.awaiting_reply=0;
 __CPROVER_assume(p.positive==0 || p.positive==1);
 PlayerPhysicsView before=v;PlayerPhysicsWorld world_before=w;
'''
    if mode=='frame':
        source+='unsigned domain;size_t watched;__CPROVER_assume(domain<3);\n'
        allowed=[]
        for d,typ,fields in [(0,'PlayerPhysicsView',VOUT[key]),(1,'PlayerPhysicsWorld',WOUT[key])]:
            for field in fields:
                obj='v' if d==0 else 'w'
                allowed.append(f'(domain=={d} && watched>=(size_t)((unsigned char *)&{obj}.{field}-(unsigned char *)&{obj}) && watched<(size_t)((unsigned char *)&{obj}.{field}-(unsigned char *)&{obj})+sizeof({obj}.{field}))')
        source+='__CPROVER_assume(watched<(domain==0?sizeof(v):domain==1?sizeof(w):sizeof(platforms)));\n'
        source+='unsigned char *base=domain==0?(unsigned char *)&v:domain==1?(unsigned char *)&w:(unsigned char *)platforms;unsigned char original=base[watched];\n'
        source+=STAGES[key]+'(&p);CHECK(p.count<=32 && !p.failed,"bounded complete stage journal");\n'
        source+='if(!('+' || '.join(allowed or ['0'])+'))CHECK(base[watched]==original,"arbitrary other native/resource byte frame");\n'
    else:
        source+='PlayerPhysicsView other;PlayerPhysicsWorld other_world;PlayerPhysicsProcess q=p;\n'
        # Inactive words vary independently; retained outputs are not compared.
        for f in VIN[key]:source+=f'other.{f}=v.{f};\n'
        for f in WIN[key]:source+=f'other_world.{f}=w.{f};\n'
        source+='other_world.platforms=platforms;__CPROVER_assume(other_world.platform_count<=10);q.player=&other;q.world=&other_world;\n'
        source+=STAGES[key]+'(&p);'+STAGES[key]+'(&q);CHECK(p.count==q.count && p.failed==q.failed,"event count and failure dependence");\n'
        source+='size_t at;if(at<p.count){PlayerPhysicsEvent a=p.journal[at],b=q.journal[at];CHECK(a.kind==b.kind && a.field==b.field && a.value==b.value && a.probe.pixel_x==b.probe.pixel_x && a.probe.pixel_y==b.probe.pixel_y && a.probe.columns==b.probe.columns && a.probe.rows==b.probe.rows,"arbitrary journal event dependence");}\n'
        for f in VOUT[key]:
            # Conditional writes can retain initial outputs, so retained values
            # are explicit dependence inputs as well as writes.
            source=source.replace('q.player=&other;',f'other.{f}=v.{f};q.player=&other;')
            source+=f'CHECK(v.{f}==other.{f},"working player output dependence");\n'
        for f in WOUT[key]:
            source=source.replace('q.world=&other_world;',f'other_world.{f}=w.{f};q.world=&other_world;')
            source+=f'CHECK(w.{f}==other_world.{f},"working world output dependence");\n'
        for f in ['stage','candidate','cursor','plane','columns','rows','water_state','positive','awaiting_reply']:
            source+=f'CHECK(p.{f}==q.{f},"control seam dependence");\n'
    source+='return 0;}\n';return source
def main():
    ap=argparse.ArgumentParser();ap.add_argument('key',choices=['sar','limit','reflect','sample',*STAGES]);ap.add_argument('mode',choices=['outputs','frame','dependence'],default='outputs',nargs='?');ap.add_argument('--timeout',type=int,default=120);a=ap.parse_args()
    folder=OUT/'proofs'/(a.key+'-'+a.mode);folder.mkdir(parents=True,exist_ok=True);harness=folder/'harness.c'
    harness.write_text(native(a.key,a.mode) if a.key in STAGES else primitive(a.key,a.mode))
    result=cbmc(harness,folder,[*FILES,ROOT/'verif/player_physics_proof.py',ROOT/'c/scene.c',ROOT/'c/demo_scripts.c',ROOT/'c/ugh.h',ROOT/'c/ugh_sym.h'],unwind=35,timeout=a.timeout,extra=['--no-array-field-sensitivity'])
    print(a.key,a.mode,result['result'],round(result['seconds'],3),result.get('peak_private_bytes'),flush=True)
    assert result['result']=='PASS'
if __name__=='__main__':main()
