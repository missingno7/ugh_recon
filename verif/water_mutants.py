"""Seed retained-quirk, private-state and protocol defects in private copies."""
from pathlib import Path
from closure_support import ROOT,save
from water_build import OUT
from water_extra_cases import run
MUTATIONS=[
 ('logical-velocity-shift','pw_sar(velocity,6)','(velocity>>6)'),
 ('wrong-sar-scale','pw_sar(slot->vertical_motion,6)','pw_sar(slot->vertical_motion,5)'),
 ('signed-sink-threshold','if(y<6144u)','if(pw_signed(y)<6144)'),
 ('surface-equality-write','if(render->pixel_y==world->surface_y) return;','(void)render; /* lost exact equality */'),
 ('surface-cross-equality','if(pw_signed(top)>pw_signed(world->surface_y))','if(pw_signed(top)>=pw_signed(world->surface_y))'),
 ('lifetime-zero-saturate','(uint16_t)(value-1u);pw_emit(out,PW_LIFETIME','(uint16_t)(value?value-1u:0);pw_emit(out,PW_LIFETIME'),
 ('second-pair-rescue','if(slot->type->id==ACTOR_PASSENGER_TWO_WATER) return;','(void)slot; /* missing identity exception */'),
 ('approach-requires-stationary','if(!world->craft[i].carried_kind && pw_at_surface','if(!world->craft[i].vertical_velocity && !world->craft[i].carried_kind && pw_at_surface'),
 ('destination-rejects-busy','if(pw_at_surface(&world->craft[i],world)) return 0;','if(!world->craft[i].carried_kind && pw_at_surface(&world->craft[i],world)) return 0;'),
 ('selected-float-only','out->selected=(int)i;out->next=PW_NEXT_DESTINATION;','out->selected=(int)i^1;out->next=PW_NEXT_DESTINATION;'),
 ('selected-board-only','if(center==target) {out->next=PW_NEXT_BOARD;return;}','if(center==target) {out->selected^=1;out->next=PW_NEXT_BOARD;return;}'),
 ('private-velocity','slot->vertical_motion=velocity;pw_emit','/* private state omitted */ pw_emit'),
 ('private-phase','slot->phase=phase;pw_emit','/* private phase omitted */ pw_emit'),
 ('extra-next','case PW_BEGIN_SINK:\n','case PW_BEGIN_SINK:\n        out.next=PW_NEXT_FLOAT;\n'),
 ('wrong-alias-tag','pw_emit(out,PW_LIFETIME,0,slot->floating_ticks);','pw_emit(out,PW_REQUEST,0,slot->floating_ticks);'),
 ('high-occupant-index','pw_emit(&out,PW_OCCUPANT_CLEAR,slot->source_platform,65535u);','pw_emit(&out,PW_OCCUPANT_CLEAR,slot->source_platform+32768u,65535u);')]
def main():
    raw=(ROOT/'native/passenger_water.c').read_text();rows=[]
    for key,old,new in MUTATIONS:
        assert old in raw,key;folder=OUT/'mutants'/key;folder.mkdir(parents=True,exist_ok=True);mutant=folder/'passenger_water.c';mutant.write_text(raw.replace(old,new));value,result=run(folder,mutant);save(folder/'result.json',result);print(key,result['result'],value.stderr.strip(),flush=True);assert result['result']=='DETECTED';rows.append(dict(mutant=key,result=result['result']))
    save(OUT/'mutants.json',rows)
if __name__=='__main__':main()
