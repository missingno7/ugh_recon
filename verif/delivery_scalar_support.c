/* Word-normalized RAM, one selected slot, and matching-cut input projection.
 * Included after the actual C pair and the existing checked RAM accessor.
 * Unmapped reads/writes still fail; no other actors are allocated as arrays. */
static unsigned tail_calls,near_calls;static uint16_t tail_target;
static Regs service_arguments;
static void child_registers(Regs *r,const Regs *output) {
    r->ax=output->ax;r->cx=output->cx;r->dx=output->dx;r->si=output->si;
    r->di=output->di;r->bp=output->bp;r->es=output->es;r->ip=output->ip;r->flags=output->flags;
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r) {
    if(bank==UGH_S_C_PlayAdlibEffect && target==UGH_O_C_PlayAdlibEffect) {
        audio_calls++;
        CHECK(dl_read(r->ss,(uint16_t)(r->sp+4))==UGH_O_B3274_ext_3274 && dl_read(r->ss,(uint16_t)(r->sp+6))==UGH_S_B3274_ext_3274,"actual bonus audio resource at the service seam");
        child_registers(r,&audio_result);r->bx=audio_result.bx;return sound_status;
    }
    CHECK(bank==GAME_SEG,"piece near bank");
    if(target==G(FindPlayerTouchingActor)) return CONTACT_QUERY(r);
    if(target==G(SpawnFallingItem)) {
        near_calls++;service_arguments=*r;uint16_t actor=r->bx;
        dl_write(r->ss,(uint16_t)(r->sp-2),actor); /* real item bridge's saved BX */
        child_registers(r,&item_result);
        if(item_exhausted) {r->bx=65534u;r->ip=actor;return modern_calls?UGH_CONTROL_TRANSFER:UGH_BAD_CALLBACK;}
        r->bx=actor;return UGH_OK;
    }
    CHECK(target==G(BeginPassengerPlatformWait) || target==G(BeginPassengerDestinationDisplay) ||
          target==G(BeginPassengerQuestionDisplay) || target==G(BeginPassengerApproach) ||
          target==G(BoardPassenger) || target==G(DeliverPassenger) || target==G(BeginPassengerResurfacing),"complete piece tail target set");
    tail_calls++;tail_target=target;return UGH_CONTROL_TRANSFER;
}
int ugh_call_near(uint16_t target,uint16_t return_ip,Regs *r) {
    r->sp=(uint16_t)(r->sp-2);dl_write(r->ss,r->sp,return_ip);
    int status=ugh_dispatch(r->cs,target,r);if(!status) r->sp=(uint16_t)(r->sp+2);return status;
}
static void seed_piece(DeliveryPlan *plan,ActorPhase phase,unsigned wet,unsigned pair) {
    actor_index=0;land_base=(uint16_t)(D(Data_7720)+148u*pair);
    const uint16_t targets[]={G(BeginPassengerPlatformWait),G(UpdatePassengerPlatformWait),G(BeginPassengerDestinationDisplay),G(UpdatePassengerDestinationDisplay),
        G(BeginPassengerQuestionDisplay),G(UpdatePassengerQuestionDisplay),G(BeginPassengerApproach),G(UpdatePassengerApproach),G(BoardPassenger),G(UpdateCarriedPassenger),G(DeliverPassenger),G(WalkPassengerToExit)};
    for(unsigned i=0;i<12;i++) ram.types[0][8+i]=targets[i];
    ram.types[0][36]=(uint16_t)(land_base+74u);ram.types[1][36]=land_base;
    ram.types[1][4]=G(BeginPassengerResurfacing);ram.types[1][11]=G(UpdateFloatingDestinationDisplay);
    ram.types[1][13]=G(UpdateFloatingQuestionDisplay);ram.types[1][15]=G(UpdateFloatingPassengerApproach);
    ram.actor[0]=(uint16_t)(land_base+74u*wet);
    ram.player_bytes=(uint16_t)(2u*ram.player_count);ram.item_type[2]=G(SpawnFallingItem);
    for(unsigned i=0;i<4;i++) {
        ram.types[0][23+i]=ram.types[1][23+i]=vector_bases[i];ram.animation[i][2]=65535u;
    }
    for(unsigned i=0;i<2;i++) {
        unsigned t=i^wet;ActorType unknown;plan->types[i]=unknown;
        plan->types[i].id=(ActorTypeId)(2u*pair+t);plan->types[i].paired_type=&plan->types[1-i];
        plan->types[i].geometry=(ObjectGeometry){ram.types[t][0],ram.types[t][1],ram.types[t][2],ram.types[t][3]};
        plan->types[i].animation_period=ram.types[t][31];plan->types[i].initial_fare=ram.types[t][32];
        plan->types[i].minimum_fare=ram.types[t][33];plan->types[i].carried_kind=ram.types[t][35];
        for(unsigned j=0;j<4;j++) {plan->types[i].animations[j].sprites=ram.animation[j];plan->types[i].animations[j].count=2;}
    }
    PassengerStoneSlot unknown_slot;plan->slot=unknown_slot;plan->slot.type=&plan->types[0];
    CHECK(actor_bridge_alias_project(DATA_SEG,0,phase,&plan->slot),"input alias seam");
    plan->slot.source_platform=ram.actor[5];plan->slot.destination_platform=ram.actor[6];
    plan->slot.position=(ObjectPosition){ram.actor[10],ram.actor[11]};
    plan->slot.sprite=ram.actor[18];plan->slot.overlay_sprite=ram.actor[20];
    plan->slot.animation=(ActorAnimationState){ram.actor[16],ram.actor[17]};plan->slot.quick_delivery_ticks=ram.actor[23];
    ActorRenderHistory unknown_render;plan->render=unknown_render;plan->render.pixel_x=ram.actor[12];plan->render.pixel_y=ram.actor[14];
    for(unsigned i=0;i<2;i++) {
        plan->world.craft[i]=(PassengerCraft){{ram.players[0][i],ram.players[1][i]},ram.players[2][i],ram.players[3][i],ram.players[4][i],ram.players[5][i],ram.players[6][i],ram.players[7][i]};
    }
    plan->world.player_count=ram.player_count;plan->world.player_slots=ram.player_count;
    plan->world.platform_count=10;plan->world.platforms=plan->platforms;
    plan->world.water_pixel_y=ram.water;plan->world.multiplier=ram.multiplier;plan->world.multiplier_limit=ram.limit;
    plan->world.score=(uint32_t)ram.score_low|((uint32_t)ram.score_high<<16);plan->world.hud_clear=(uint8_t)ram.hud;
    for(unsigned i=0;i<10;i++) {
        LevelPlatform unknown;plan->platforms[i]=unknown;
        plan->platforms[i].surface_y=ram.platforms[0][i];plan->platforms[i].waiting_x=ram.platforms[1][i];plan->platforms[i].destination_icon=ram.platforms[2][i];
    }
    plan->result=(PassengerDeliveryResult){0};plan->result.selected=-1;
    plan->consumed=0;plan->bad=plan->tail_seen=plan->spawn_seen=plan->sound_seen=0;
    plan->input_phase=plan->published_phase=phase;plan->phase_written=0;plan->actor_index=0;plan->entry=PD_DELIVER;
}
static uint16_t result_target(PassengerDeliveryNext next) {
    switch(next) {
    case PD_NEXT_NONE:return 0;case PD_NEXT_WAIT:return G(BeginPassengerPlatformWait);
    case PD_NEXT_DESTINATION:return G(BeginPassengerDestinationDisplay);case PD_NEXT_QUESTION:return G(BeginPassengerQuestionDisplay);
    case PD_NEXT_APPROACH:return G(BeginPassengerApproach);case PD_NEXT_BOARD:return G(BoardPassenger);
    case PD_NEXT_DELIVER:return G(DeliverPassenger);case PD_NEXT_WATER:return G(BeginPassengerResurfacing);
    }
    CHECK(0,"native next is a defined semantic target");return 0;
}
