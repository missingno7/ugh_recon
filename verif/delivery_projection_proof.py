"""Actual complete matching-cut projection predicate and negative corruption.

This theorem is independent of any handler body. A stage's output and byte-frame
properties establish the full predicate's premise at its cut; its own theorem
then discharges the helper-summary seam used by the stage output profile.
"""
import argparse,json
from pathlib import Path
from closure_support import ROOT
from delivery_build import OUT,pair
from delivery_limits import cbmc,SMT

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['outputs','frame','dependencies','corruption']);p.add_argument('--field',type=int);p.add_argument('--timeout',type=int,default=120);a=p.parse_args()
    if a.mode=='corruption' and (a.field is None or not 0<=a.field<26):p.error('corruption requires --field 0..25')
    folder=OUT/'projection'/(a.mode+(str(a.field) if a.field is not None else ''));inputs=pair(folder)
    original=ROOT/'verif/delivery_harness.c';prefix=original.read_text().split('int ugh_dispatch(')[0]
    prefix=prefix.replace('if(!(bank==DATA_SEG && address>=D(FallingItemDescriptors) && address<D(FallingItemVerticalStep)+24u)) record(bank,address,value,0);','record(bank,address,value,0);')
    support=ROOT/'verif/delivery_scalar_support.c'
    code='#include "pair.inc"\n'+prefix+'\nstatic _Bool item_exhausted;static int sound_status;static Regs item_result,audio_result;static unsigned audio_calls;\n#define CONTACT_QUERY(r) l1_FindPlayerTouchingActor(r)\n'+support.read_text()
    code+='''int main(void) {
 DeliveryRam arbitrary;ram=arbitrary;DeliveryPlan plan;
 unsigned pair,wet,tag;__CPROVER_assume(pair<3 && wet<2 && tag<10);
 const ActorPhase phases[]={ACTOR_READ_JOURNEY,ACTOR_PLATFORM_WAIT,ACTOR_DESTINATION_REQUEST,ACTOR_QUESTION,ACTOR_APPROACH,ACTOR_CARRIED_PASSENGER,ACTOR_WALK_TO_EXIT,ACTOR_FLOATING_DESTINATION_REQUEST,ACTOR_FLOATING_QUESTION,ACTOR_FLOATING_APPROACH};
 ActorPhase phase=phases[tag];
 __CPROVER_assume(ram.player_count==1 || ram.player_count==2);__CPROVER_assume(ram.difficulty<3);
 if(phase==ACTOR_CARRIED_PASSENGER) __CPROVER_assume(ram.actor[4]==0 || (ram.actor[4]==2 && ram.player_count==2));
 seed_piece(&plan,phase,wet,pair);
 size_t count;_Bool written;__CPROVER_assume(count<=32);plan.result.count=plan.consumed=count;plan.phase_written=written;
 if(written) ram.actor[3]=delivery_phase((uint16_t)phase);
 Regs r={0};r.ds=DATA_SEG;r.cs=GAME_SEG;r.bx=0;
 store_count=0;modern_calls=0;
'''
    if a.mode=='outputs':code+='CHECK(delivery_projection(&plan,&r),"complete active projection accepts matching cut");\n'
    elif a.mode=='frame':
        code+='''unsigned probe;__CPROVER_assume(probe<sizeof(plan));uint8_t *cell=(uint8_t *)&plan+probe;uint8_t before=*cell;
 delivery_projection(&plan,&r);CHECK(*cell==before && store_count==0,"projection changes no native byte and writes no RAM");
'''
    elif a.mode=='dependencies':
        code+='''DeliveryPlan other=plan;PassengerStoneSlot unrelated;ActorRenderHistory history;PassengerDeliveryResult result;
 other.slot.journey=unrelated.journey;other.slot.vertical_motion=unrelated.vertical_motion;
 unsigned mask=actor_phase_aliases(phase);
 if(!(mask&ACTOR_ALIAS_WAITING_POSE)) other.slot.waiting_pose=unrelated.waiting_pose;
 if(!(mask&ACTOR_ALIAS_REQUEST_TICKS)) other.slot.request_ticks=unrelated.request_ticks;
 if(!(mask&ACTOR_ALIAS_CARRIER)) other.slot.carrier=unrelated.carrier;
 other.slot.journey_wait=unrelated.journey_wait;other.slot.horizontal_step=unrelated.horizontal_step;other.slot.floating_ticks=unrelated.floating_ticks;
 other.render.previous_x=history.previous_x;other.render.previous_y=history.previous_y;other.render.erase_sprite=history.erase_sprite;other.render.erase_overlay_sprite=history.erase_overlay_sprite;
 other.result=result;other.result.count=count;other.slot.type=&other.types[0];other.world.platforms=other.platforms;
 CHECK(delivery_projection(&plan,&r)==delivery_projection(&other,&r),"inactive aliases, retained unborrowed histories and journal payload do not affect projection");
'''
    else:
        cells=['slot.position.x32','slot.position.y32','slot.sprite','slot.overlay_sprite','slot.source_platform','slot.destination_platform','slot.quick_delivery_ticks','slot.animation.byte_offset','slot.animation.countdown','world.score','world.hud_clear','world.player_count','world.player_slots','world.water_pixel_y','world.multiplier','render.pixel_x','render.pixel_y']
        cells += ['world.craft[i].'+field for field in ['position.x32','position.y32','pixel_x','platform','fare','minimum_fare','carried_kind','destination_icon']]
        cells += ['slot.carrier']
        code+='unsigned choice='+str(a.field)+',byte,i;__CPROVER_assume(i<2);\n'
        if a.field==25:code+='__CPROVER_assume(phase==ACTOR_CARRIED_PASSENGER);\n'
        code+='switch(choice) {\n'
        for j,name in enumerate(cells):code+=f'case {j}:__CPROVER_assume(byte<sizeof(plan.{name}));plan.{name}^=(uint64_t)1<<(8u*byte);break;\n'
        code+='''}
 CHECK(!delivery_projection(&plan,&r),"every checked scalar byte corruption is rejected, including full-width carrier/count representation");
'''
    code+='return 0;}\n';source=folder/'harness.c';source.write_text(code)
    result=cbmc(source,folder,[*inputs,original,support,Path(__file__)],unwind=40,timeout=a.timeout,defines=['-D__CPROVER__','-DACTOR_VERIFY','-DUINT16_MAX=65535u'],extra=SMT)
    print(a.mode,json.dumps({k:result[k] for k in ['result','seconds','peak_private_bytes','failures']}),flush=True);assert result['result']=='PASS'
if __name__=='__main__':main()
