"""Actual full matching-cut predicate: output/frame/dependence and corruptions."""
import argparse,json
from pathlib import Path
from closure_support import ROOT
from water_build import OUT,pair
from water_limits import cbmc,SMT
FIELDS=['slot.phase','slot.source_platform','slot.destination_platform','slot.position.x32','slot.position.y32','slot.sprite','slot.overlay_sprite','slot.animation.byte_offset','slot.animation.countdown','slot.vertical_motion','slot.quick_delivery_ticks','render.pixel_x','render.pixel_y','world.surface_y','world.player_count','world.platform_count']+['world.craft[i].'+n for n in ['pixel_x','pixel_y','vertical_velocity','carried_kind']]+['slot.floating_ticks','slot.request_ticks']
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['outputs','frame','dependencies','corruption']);p.add_argument('--field',type=int);p.add_argument('--timeout',type=int,default=600);a=p.parse_args()
    if a.mode=='corruption' and (a.field is None or not 0<=a.field<len(FIELDS)):p.error('corruption field required')
    folder=OUT/'projection'/(a.mode+(str(a.field) if a.field is not None else ''));inputs=pair(folder)
    code='#define PIECE\n#include "pair.inc"\n'+(ROOT/'verif/water_harness.c').read_text().split('#ifndef PIECE')[0]
    code+='''int main(void) {
 WaterRam arbitrary;ram=arbitrary;unsigned pair,tag;__CPROVER_assume(pair<3 && tag<8);actor_index=0;configure(pair);
 __CPROVER_assume(ram.players==1 || ram.players==2);
 const ActorPhase phases[]={ACTOR_READ_JOURNEY,ACTOR_RESURFACING,ACTOR_SINKING,ACTOR_FLOATING,ACTOR_FLOATING_DESTINATION_REQUEST,ACTOR_FLOATING_QUESTION,ACTOR_FLOATING_APPROACH,ACTOR_RETIRED};
 ActorPhase phase=phases[tag];WaterPlan plan;seed_view(&plan,phase);
 size_t count;_Bool written;__CPROVER_assume(count<=32);plan.result.count=plan.consumed=count;plan.phase_written=written;
 if(written) ram.actor[3]=water_phase(phase);
 Regs r={0};r.ds=DATA_SEG;r.cs=GAME_SEG;r.bx=0;store_count=0;
'''
    if a.mode=='outputs':code+='CHECK(water_projection(&plan,&r),"actual full active projection accepts every matching cut");\n'
    elif a.mode=='frame':code+='unsigned byte;__CPROVER_assume(byte<sizeof(plan));uint8_t *cell=(uint8_t *)&plan+byte;uint8_t before=*cell;water_projection(&plan,&r);CHECK(*cell==before && !store_count,"projection changes no native byte or RAM");\n'
    elif a.mode=='dependencies':code+='''WaterPlan other=plan;PassengerStoneSlot unseen;ActorRenderHistory history;PassengerWaterResult result;
 other.slot.journey=unseen.journey;other.slot.waiting_pose=unseen.waiting_pose;other.slot.carrier=unseen.carrier;other.slot.journey_wait=unseen.journey_wait;other.slot.horizontal_step=unseen.horizontal_step;
 unsigned mask=actor_phase_aliases(phase);if(!(mask&ACTOR_ALIAS_FLOATING_TICKS)) other.slot.floating_ticks=unseen.floating_ticks;if(!(mask&ACTOR_ALIAS_REQUEST_TICKS)) other.slot.request_ticks=unseen.request_ticks;
 other.render.previous_x=history.previous_x;other.render.previous_y=history.previous_y;other.render.erase_sprite=history.erase_sprite;other.render.erase_overlay_sprite=history.erase_overlay_sprite;
 other.result=result;other.result.count=count;other.slot.type=&other.type;
 CHECK(water_projection(&plan,&r)==water_projection(&other,&r),"inactive aliases, retained history and journal payload do not affect full projection");
'''
    else:
        name=FIELDS[a.field];code+='unsigned byte,i;__CPROVER_assume(i<2);\n'
        if a.field==20:code+='__CPROVER_assume(phase==ACTOR_FLOATING);\n'
        if a.field==21:code+='__CPROVER_assume(phase==ACTOR_FLOATING_DESTINATION_REQUEST || phase==ACTOR_FLOATING_QUESTION);\n'
        code+=f'__CPROVER_assume(byte<sizeof(plan.{name}));plan.{name}^=(uint64_t)1<<(8u*byte);\nCHECK(!water_projection(&plan,&r),"every selected scalar byte corruption is rejected");\n'
    code+='return 0;}\n';source=folder/'harness.c';source.write_text(code)
    result=cbmc(source,folder,[*inputs,ROOT/'verif/water_harness.c',Path(__file__)],unwind=40,timeout=a.timeout,defines=['-D__CPROVER__','-DACTOR_VERIFY','-DUINT16_MAX=65535u'],extra=[*SMT,'--no-array-field-sensitivity'])
    print(json.dumps({k:result[k] for k in ['result','seconds','peak_private_bytes','failures']}),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
