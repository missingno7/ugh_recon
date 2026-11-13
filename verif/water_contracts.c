/* Relational tick/frame seams. Primitive actual-C theorems discharge these
 * arbitrary shared results. Inputs and multiplicity are asserted here. */
typedef struct WaterContract {uint16_t dec,reload,cursor,sprite,ax,di,flags;_Bool due,reset;} WaterContract;
static WaterContract contract;static unsigned nt,nf,rt,rf,bt,bf;
static uint16_t count_in,cursor_in,period_in,frame_cursor,frame_kind;
static int pw_tick(PassengerWaterResult *out,PassengerStoneSlot *slot) {
 CHECK(++nt==1,"one native tick seam");count_in=slot->animation.countdown;cursor_in=slot->animation.byte_offset;period_in=slot->type->animation_period;
 slot->animation.countdown=contract.dec;pw_emit(out,PW_TICK,0,contract.dec);
 if(!contract.due) return 0;
 slot->animation.countdown=contract.reload;pw_emit(out,PW_TICK,0,contract.reload);slot->animation.byte_offset=contract.cursor;pw_emit(out,PW_CURSOR,0,contract.cursor);return 1;
}
static int pw_frame(PassengerWaterResult *out,PassengerStoneSlot *slot,ActorAnimationKind kind) {
 CHECK(++nf==1,"one native frame seam");frame_cursor=slot->animation.byte_offset;frame_kind=(uint16_t)kind;
 if(contract.reset) {slot->animation.byte_offset=contract.cursor;pw_emit(out,PW_CURSOR,0,contract.cursor);}
 slot->sprite=contract.sprite;pw_emit(out,PW_SPRITE,0,contract.sprite);return 1;
}
static int contract_tick(Regs *r,WaterPlan *plan) {
 if(plan) CHECK(++bt==1,"one bridge tick");else CHECK(++rt==1,"one reference tick");
 CHECK(nt==1 && wa_read(r->ds,D(ActorAnimationCountdowns))==count_in && wa_read(r->ds,D(ActorAnimationByteOffsets))==cursor_in && wa_read(r->ds,(uint16_t)(r->si+62))==period_in,"tick input equality at seam");
 if(plan) water_write(plan,r,D(ActorAnimationCountdowns),contract.dec);else wa_write(r->ds,D(ActorAnimationCountdowns),contract.dec);
 if(contract.due) {
  if(plan) {water_write(plan,r,D(ActorAnimationCountdowns),contract.reload);water_write(plan,r,D(ActorAnimationByteOffsets),contract.cursor);}
  else {wa_write(r->ds,D(ActorAnimationCountdowns),contract.reload);wa_write(r->ds,D(ActorAnimationByteOffsets),contract.cursor);}
 }
 r->ax=contract.ax;r->flags=contract.flags;return contract.due;
}
static int contract_frame(Regs *r,WaterPlan *plan,unsigned field) {
 if(plan) CHECK(++bf==1,"one bridge frame");else CHECK(++rf==1,"one reference frame");
 CHECK(nf==1 && field==46u+2u*frame_kind && wa_read(r->ds,D(ActorAnimationByteOffsets))==frame_cursor,"frame cursor/vector equality at seam");
 if(contract.reset) {if(plan) water_write(plan,r,D(ActorAnimationByteOffsets),contract.cursor);else wa_write(r->ds,D(ActorAnimationByteOffsets),contract.cursor);}
 if(plan) water_write(plan,r,D(ActorSpriteIds),contract.sprite);else wa_write(r->ds,D(ActorSpriteIds),contract.sprite);
 r->ax=contract.sprite;r->di=contract.di;r->flags=contract.flags;return UGH_OK;
}
static int wa_ref_actor_tick(Regs *r) {return contract_tick(r,0);}
static int water_shell_actor_tick(Regs *r,WaterPlan *plan) {return contract_tick(r,plan);}
static int wa_ref_actor_frame(Regs *r,unsigned field) {return contract_frame(r,0,field);}
static int water_shell_actor_frame(Regs *r,WaterPlan *plan,unsigned field) {return contract_frame(r,plan,field);}
