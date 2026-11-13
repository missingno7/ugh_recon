/* Temporary ABI shell, transcribed from the maintained L1 instruction
 * expressions. Arithmetic reconstructs registers/flags only. Persistent stores
 * consume the native semantic journal, and tails consume its typed target.
 * Journal mismatches fail explicitly; there is no shadow L1 execution or
 * post-step overwrite. The independent L1 remains in c/ for comparisons. */
#include "ugh.h"
#include "../hazards.h"
typedef struct HazardPlan {
    HazardResult result;
    uint16_t descriptor;
    size_t used;
    int invalid, audio_used;
} HazardPlan;
int l1_DispatchEnemyStates(Regs *r);
int l1_BeginBirdDelay(Regs *r);
int l1_WaitForBirdFlight(Regs *r);
int l1_BeginBirdWarning(Regs *r);
int l1_WaitForBirdWarning(Regs *r);
int l1_LaunchBirdTowardPlayer(Regs *r);
int l1_UpdateBirdFlight(Regs *r);
int l1_StunBirdAndAwardScore(Regs *r);
int l1_UpdateStunnedBird(Regs *r);
int l1_StopBirdFlightSound(Regs *r);
int l1_BeginTriopterusPatrol(Regs *r);
int l1_UpdateTriopterusPatrol(Regs *r);
int l1_BeginTriopterusAlert(Regs *r);
int l1_UpdateTriopterusAlert(Regs *r);
int l1_BeginTriopterusCharge(Regs *r);
int l1_UpdateTriopterusCharge(Regs *r);
int l1_BeginTriopterusRecovery(Regs *r);
int l1_AnimateTriopterusRecovery(Regs *r);
int l1_BeginTriopterusImpactRecovery(Regs *r);
int l1_AnimateTriopterusImpactRecovery(Regs *r);
int l1_StunTriopterusAndAwardScore(Regs *r);
int l1_UpdateStunnedTriopterus(Regs *r);
int l1_InitializeDinoAnimation(Regs *r);
int l1_UpdateDinoForce(Regs *r);
int l1_StunDinoAndAwardScore(Regs *r);
int l1_UpdateStunnedDino(Regs *r);
int l1_InitializeFruitTreeAnimation(Regs *r);
int l1_UpdateFruitTreeAnimation(Regs *r);
int l1_ReleaseTreeReward(Regs *r);
int l1_AdvanceTreeRewardCooldown(Regs *r);
int l1_IgnoreExhaustedTree(Regs *r);
static uint16_t hazard_target(HazardEntry entry) {
 switch(entry) {
 case H_ZERO:return 0;
 case H_IGNORE:return G(IgnoreActorState);
 case H_BIRD_DELAY:return G(BeginBirdDelay);
 case H_BIRD_WAIT:return G(WaitForBirdFlight);
 case H_BIRD_WARNING:return G(BeginBirdWarning);
 case H_BIRD_WARN_WAIT:return G(WaitForBirdWarning);
 case H_BIRD_LAUNCH:return G(LaunchBirdTowardPlayer);
 case H_BIRD_FLIGHT:return G(UpdateBirdFlight);
 case H_BIRD_STUN:return G(StunBirdAndAwardScore);
 case H_BIRD_FALL:return G(UpdateStunnedBird);
 case H_BIRD_STOP:return G(StopBirdFlightSound);
 case H_TRIO_PATROL_BEGIN:return G(BeginTriopterusPatrol);
 case H_TRIO_PATROL:return G(UpdateTriopterusPatrol);
 case H_TRIO_ALERT_BEGIN:return G(BeginTriopterusAlert);
 case H_TRIO_ALERT:return G(UpdateTriopterusAlert);
 case H_TRIO_CHARGE_BEGIN:return G(BeginTriopterusCharge);
 case H_TRIO_CHARGE:return G(UpdateTriopterusCharge);
 case H_TRIO_RECOVER_BEGIN:return G(BeginTriopterusRecovery);
 case H_TRIO_RECOVER:return G(AnimateTriopterusRecovery);
 case H_TRIO_IMPACT_BEGIN:return G(BeginTriopterusImpactRecovery);
 case H_TRIO_IMPACT:return G(AnimateTriopterusImpactRecovery);
 case H_TRIO_STUN:return G(StunTriopterusAndAwardScore);
 case H_TRIO_STUNNED:return G(UpdateStunnedTriopterus);
 case H_DINO_BEGIN:return G(InitializeDinoAnimation);
 case H_DINO_FORCE:return G(UpdateDinoForce);
 case H_DINO_STUN:return G(StunDinoAndAwardScore);
 case H_DINO_STUNNED:return G(UpdateStunnedDino);
 case H_TREE_BEGIN:return G(InitializeFruitTreeAnimation);
 case H_TREE_ANIMATE:return G(UpdateFruitTreeAnimation);
 case H_TREE_RELEASE:return G(ReleaseTreeReward);
 case H_TREE_COOLDOWN:return G(AdvanceTreeRewardCooldown);
 case H_TREE_EMPTY:return G(IgnoreExhaustedTree);
 default:return 0;
 }
}
static int hazard_entry(uint16_t target,HazardEntry *entry) {
 if(!target) { *entry=H_ZERO;return 1; }
 if(target==G(IgnoreActorState)) { *entry=H_IGNORE;return 1; }
 if(target==G(BeginBirdDelay)) { *entry=H_BIRD_DELAY;return 1; }
 if(target==G(WaitForBirdFlight)) { *entry=H_BIRD_WAIT;return 1; }
 if(target==G(BeginBirdWarning)) { *entry=H_BIRD_WARNING;return 1; }
 if(target==G(WaitForBirdWarning)) { *entry=H_BIRD_WARN_WAIT;return 1; }
 if(target==G(LaunchBirdTowardPlayer)) { *entry=H_BIRD_LAUNCH;return 1; }
 if(target==G(UpdateBirdFlight)) { *entry=H_BIRD_FLIGHT;return 1; }
 if(target==G(StunBirdAndAwardScore)) { *entry=H_BIRD_STUN;return 1; }
 if(target==G(UpdateStunnedBird)) { *entry=H_BIRD_FALL;return 1; }
 if(target==G(StopBirdFlightSound)) { *entry=H_BIRD_STOP;return 1; }
 if(target==G(BeginTriopterusPatrol)) { *entry=H_TRIO_PATROL_BEGIN;return 1; }
 if(target==G(UpdateTriopterusPatrol)) { *entry=H_TRIO_PATROL;return 1; }
 if(target==G(BeginTriopterusAlert)) { *entry=H_TRIO_ALERT_BEGIN;return 1; }
 if(target==G(UpdateTriopterusAlert)) { *entry=H_TRIO_ALERT;return 1; }
 if(target==G(BeginTriopterusCharge)) { *entry=H_TRIO_CHARGE_BEGIN;return 1; }
 if(target==G(UpdateTriopterusCharge)) { *entry=H_TRIO_CHARGE;return 1; }
 if(target==G(BeginTriopterusRecovery)) { *entry=H_TRIO_RECOVER_BEGIN;return 1; }
 if(target==G(AnimateTriopterusRecovery)) { *entry=H_TRIO_RECOVER;return 1; }
 if(target==G(BeginTriopterusImpactRecovery)) { *entry=H_TRIO_IMPACT_BEGIN;return 1; }
 if(target==G(AnimateTriopterusImpactRecovery)) { *entry=H_TRIO_IMPACT;return 1; }
 if(target==G(StunTriopterusAndAwardScore)) { *entry=H_TRIO_STUN;return 1; }
 if(target==G(UpdateStunnedTriopterus)) { *entry=H_TRIO_STUNNED;return 1; }
 if(target==G(InitializeDinoAnimation)) { *entry=H_DINO_BEGIN;return 1; }
 if(target==G(UpdateDinoForce)) { *entry=H_DINO_FORCE;return 1; }
 if(target==G(StunDinoAndAwardScore)) { *entry=H_DINO_STUN;return 1; }
 if(target==G(UpdateStunnedDino)) { *entry=H_DINO_STUNNED;return 1; }
 if(target==G(InitializeFruitTreeAnimation)) { *entry=H_TREE_BEGIN;return 1; }
 if(target==G(UpdateFruitTreeAnimation)) { *entry=H_TREE_ANIMATE;return 1; }
 if(target==G(ReleaseTreeReward)) { *entry=H_TREE_RELEASE;return 1; }
 if(target==G(AdvanceTreeRewardCooldown)) { *entry=H_TREE_COOLDOWN;return 1; }
 if(target==G(IgnoreExhaustedTree)) { *entry=H_TREE_EMPTY;return 1; }
 return 0;
}
static uint16_t hazard_word(Regs *r,uint16_t base,uint16_t index) {
    return rd16(r->ds,(uint16_t)(base+index));
}
static ObjectPosition hazard_position(Regs *r,uint16_t x,uint16_t y,uint16_t index) {
    ObjectPosition position={hazard_word(r,x,index),hazard_word(r,y,index)};return position;
}
static int hazard_project(Regs *r,HazardEntry entry,HazardPlan *plan) {
    if(r->bx>8 || (r->bx&1u)) return 0;
    if(lin(r->ds,0)<0xc0000u && lin(r->ds,65535u)>=0xa0000u) return 0;
    int uses_incoming=entry==H_TRIO_ALERT_BEGIN || entry==H_TRIO_CHARGE_BEGIN ||
        entry==H_TRIO_RECOVER_BEGIN || entry==H_TRIO_IMPACT_BEGIN ||
        entry==H_BIRD_STUN || entry==H_TRIO_STUN || entry==H_DINO_STUN || entry==H_TREE_RELEASE;
    uint16_t descriptor=uses_incoming?r->si:hazard_word(r,D(EnemyDescriptors),r->bx);
    /* Stable immutable resource operands, ordinary RAM, no output aliases.
     * Out-of-contract resource/array/stack aliases retain the independent L1. */
    if(descriptor>65475u || (descriptor>=D(ScoreLowWord)-60u && descriptor<D(FallingItemDescriptors)+144u)) return 0;
    HazardSlot slot={0};HazardType type={0};HazardWorld world={0};LevelPlatform platforms[10];
    slot.position=hazard_position(r,D(EnemyX32),D(EnemyY32),r->bx);
    slot.platform=hazard_word(r,D(EnemyPlatformIndices),r->bx);
    slot.initial_delay=hazard_word(r,D(EnemyInitialDelays),r->bx);
    slot.speed=hazard_word(r,D(EnemyHorizontalSpeeds),r->bx);
    slot.counter=hazard_word(r,D(EnemyStateCounters),r->bx);
    slot.animation_cursor=hazard_word(r,D(EnemyAnimationByteOffsets),r->bx);
    /* Every shipped animation has at most fourteen frames. The retained L1
     * handles malformed/odd cursors; the native boundary admits all even
     * cursors through the largest sequence's sentinel and the FFFE seed. */
    if(slot.animation_cursor!=65534u && (slot.animation_cursor>30u || (slot.animation_cursor&1u))) return 0;
    slot.animation_countdown=hazard_word(r,D(EnemyAnimationCountdowns),r->bx);
    slot.sprite=hazard_word(r,D(EnemySpriteIds),r->bx);
    slot.direction=hazard_word(r,D(EnemyDirectionOrTargetPlayer),r->bx);
    slot.draw_x=hazard_word(r,D(EnemyDrawX),r->bx);slot.draw_y=hazard_word(r,D(EnemyDrawY),r->bx);
    slot.flight_sound=hazard_word(r,D(EnemyFlightSoundHandles),r->bx);
    /* Every word not needed by an entry is still retained, never normalized. */
    if((entry==H_BIRD_LAUNCH && slot.direction>1) ||
       ((entry==H_TRIO_PATROL || entry==H_TRIO_ALERT || entry==H_TRIO_CHARGE ||
         entry==H_TRIO_RECOVER || entry==H_TRIO_IMPACT || entry==H_TRIO_STUNNED) && slot.direction!=0 && slot.direction!=2)) return 0;
    type.geometry.anchor_x=rd16(r->ds,descriptor);type.geometry.anchor_y=rd16(r->ds,(uint16_t)(descriptor+2));
    type.geometry.extent_x=rd16(r->ds,(uint16_t)(descriptor+4));type.geometry.extent_y=rd16(r->ds,(uint16_t)(descriptor+6));
    type.score=rd16(r->ds,(uint16_t)(descriptor+58));
    for(unsigned i=0;i<13;i++) if(!hazard_entry(rd16(r->ds,(uint16_t)(descriptor+8+2*i)),&type.handlers[i])) return 0;
    for(unsigned i=0;i<12;i++) {
        uint16_t sequence=rd16(r->ds,(uint16_t)(descriptor+34+2*i));
        uint16_t next=(uint16_t)(sequence+slot.animation_cursor+2u);
        if((sequence>=D(ScoreLowWord)-1u && sequence<D(FallingItemDescriptors)+144u) ||
           (next>=D(ScoreLowWord)-1u && next<D(FallingItemDescriptors)+144u)) return 0;
        type.animations[i].first=rd16(r->ds,sequence);type.animations[i].next=rd16(r->ds,next);
        if(type.animations[i].first==65535u) return 0;
    }
    uint16_t list=hazard_word(r,D(EnemyAnimationOrDropLists),r->bx);
    slot.flight_side=list==rd16(r->ds,(uint16_t)(descriptor+34))?H_FLIGHT_LEFT:
        list==rd16(r->ds,(uint16_t)(descriptor+36))?H_FLIGHT_RIGHT:H_FLIGHT_UNSELECTED;
    slot.reward_cursor=(uint16_t)((uint16_t)(list-D(Treerewardlist_3CB3))/2u);
    if((entry==H_TREE_RELEASE || entry==H_TREE_COOLDOWN) &&
       ((uint16_t)(list-D(Treerewardlist_3CB3))>18u || ((list-D(Treerewardlist_3CB3))&1u))) return 0;
    if(entry==H_BIRD_FLIGHT && slot.flight_side==H_FLIGHT_UNSELECTED) return 0;
    type.flight.first=rd16(r->ds,list);
    type.flight.next=rd16(r->ds,(uint16_t)(list+slot.animation_cursor+2u));
    type.rewards_exhausted=type.flight.first==65535u;
    if(entry==H_BIRD_FLIGHT && type.flight.first==65535u) return 0;
    world.player_count=hazard_word(r,D(PlayerCount),0);
    uint16_t bytes=hazard_word(r,D(PlayerArrayBytes),0);
    if(world.player_count>2 || (bytes!=2 && bytes!=4)) return 0;
    world.player_slots=bytes/2;
    world.water_y32=hazard_word(r,D(WaterY32),0);world.fade_step=hazard_word(r,D(ScreenFadeStep),0);
    world.fade_level=hazard_word(r,D(ScreenFadeLevel),0);
    world.score=hazard_word(r,D(ScoreLowWord),0)|((uint32_t)hazard_word(r,D(ScoreHighWord),0)<<16);
    for(unsigned i=0;i<2;i++) {
        world.players[i].position=hazard_position(r,D(PlayerX32),D(PlayerY32),(uint16_t)(2*i));
        world.players[i].platform=hazard_word(r,D(PlayerPlatformIndices),(uint16_t)(2*i));
        world.players[i].horizontal_velocity=hazard_word(r,D(PlayerHorizontalVelocities),(uint16_t)(2*i));
        world.players[i].vertical_velocity=hazard_word(r,D(PlayerVerticalVelocities),(uint16_t)(2*i));
    }
    world.stone_count=16;
    for(unsigned i=0;i<16;i++) {
        uint16_t index=(uint16_t)(2*i),actor=hazard_word(r,D(ActorDescriptors),index);
        if(actor==65535u && world.stone_count==16) world.stone_count=i;
        world.stones[i].contact.position=hazard_position(r,D(ActorX32),D(ActorY32),index);
        world.stones[i].contact.vertical_step=hazard_word(r,D(ActorVerticalOrDemoPeriod),index);
        world.stones[i].contact.thrown_stone=actor==D(Data_78DC) && hazard_word(r,D(ActorUpdateOrScriptCursor),index)==G(UpdateThrownStone);
        world.stones[i].horizontal_step=hazard_word(r,D(ActorMotionWaitOrDemoRepeats),index);
        world.stones[i].sprite=hazard_word(r,D(ActorSpriteIds),index);
    }
    if(world.stone_count==16 && hazard_word(r,D(ActorDescriptors),32)!=65535u) return 0;
    world.platform_count=10;
    for(unsigned i=0;i<10;i++) {
        platforms[i].left=hazard_word(r,D(PlatformLeftEdges),(uint16_t)(2*i));
        platforms[i].right=hazard_word(r,D(PlatformRightEdges),(uint16_t)(2*i));
        platforms[i].surface_y=hazard_word(r,D(PlatformHeights),(uint16_t)(2*i));
    }
    world.platforms=platforms;
    if(entry==H_TRIO_PATROL && slot.platform>=10) return 0;
    if(entry==H_TREE_RELEASE && (r->di>30 || (r->di&1u))) return 0;
    if(entry==H_TREE_RELEASE) {
        uint16_t item=rd16(r->ds,list);
        if(rd16(r->ds,(uint16_t)(item+4))!=G(SpawnFallingItem)) return 0;
    }
    plan->result=hazard_step(entry,&slot,&type,&world,r->di/2);
    plan->descriptor=descriptor;plan->used=0;plan->invalid=0;plan->audio_used=0;
    return 1;
}
static void hazard_write(Regs *r,HazardPlan *plan,uint16_t base,uint16_t index,uint16_t shell_value) {
    /* A returned audio channel is supplied by the open L1 audio interface. */
    if(base==D(EnemyFlightSoundHandles)) { wr16(r->ds,(uint16_t)(base+index),shell_value);return; }
    if(plan->used>=plan->result.count) { plan->invalid=1;return; }
    const HazardWrite *write=&plan->result.writes[plan->used++];
    HazardField field=HW_STATE;unsigned logical=0;int recognized=1;
    if(base==D(EnemyStateCallbacks)) field=HW_STATE;
    else if(base==D(EnemyX32)) field=HW_X;
    else if(base==D(EnemyY32)) field=HW_Y;
    else if(base==D(EnemyHorizontalSpeeds)) field=HW_SPEED;
    else if(base==D(EnemyStateCounters)) field=HW_COUNTER;
    else if(base==D(EnemyAnimationByteOffsets)) field=HW_CURSOR;
    else if(base==D(EnemyAnimationCountdowns)) field=HW_TICK;
    else if(base==D(EnemySpriteIds)) field=HW_SPRITE;
    else if(base==D(EnemyDirectionOrTargetPlayer)) field=HW_DIRECTION;
    else if(base==D(EnemyDrawX)) field=HW_DRAW_X;
    else if(base==D(EnemyDrawY)) field=HW_DRAW_Y;
    else if(base==D(EnemyAnimationOrDropLists)) field=HW_LIST;
    else if(base==D(ScoreLowWord)) field=HW_SCORE_LOW;
    else if(base==D(ScoreHighWord)) field=HW_SCORE_HIGH;
    else if(base==D(ScreenFadeStep)) field=HW_FADE_STEP;
    else if(base==D(ScreenFadeLevel)) field=HW_FADE_LEVEL;
    else if(base==D(ActorVerticalOrDemoPeriod)) { field=HW_STONE_VERTICAL;logical=index/2; }
    else if(base==D(ActorSpriteIds)) { field=HW_STONE_SPRITE;logical=index/2; }
    else if(base==D(PlayerY32)) { field=HW_PLAYER_Y;logical=index/2; }
    else if(base==D(PlayerHorizontalVelocities)) { field=HW_PLAYER_HORIZONTAL;logical=index/2; }
    else if(base==D(PlayerVerticalVelocities)) { field=HW_PLAYER_VERTICAL;logical=index/2; }
    else if(base==D(PlayerPlatformIndices)) { field=HW_PLAYER_PLATFORM;logical=index/2; }
    else recognized=0;
    if(!recognized || field!=write->field || logical!=write->index) { plan->invalid=1;return; }
    uint16_t value=write->value;
    if(field==HW_STATE) value=hazard_target((HazardEntry)value);
    if(field==HW_LIST) value=value==2?(uint16_t)(hazard_word(r,base,index)+2u):
        rd16(r->ds,(uint16_t)(plan->descriptor+34+2*value));
    wr16(r->ds,(uint16_t)(base+index),value);
}
static int hazard_finish(HazardPlan *plan,int status) {
    if(plan->invalid) return UGH_BAD_CALLBACK;
    if(status) return status;
    return plan->used!=plan->result.count || (plan->result.audio!=HA_NONE && !plan->audio_used) ? UGH_BAD_CALLBACK : UGH_OK;
}
static int hazard_tail_call(Regs *r,HazardPlan *plan,uint16_t shell_target) {
    if(!plan->result.has_tail || shell_target!=hazard_target(plan->result.tail) ||
       hazard_finish(plan,0)) return UGH_BAD_CALLBACK;
    return ugh_dispatch(r->cs,hazard_target(plan->result.tail),r);
}
static int hazard_near(Regs *r,HazardPlan *plan,uint16_t target,uint16_t ret) {
    if(target==G(SpawnFallingItem)) {
        if(!plan->result.spawn_item) return UGH_BAD_CALLBACK;
        r->ax=plan->result.launch.x32;r->bp=plan->result.launch.y32;
        r->cx=plan->result.launch_horizontal;r->dx=plan->result.launch_term;
    }
    if(target==G(StopBirdFlightSound)) {
        if(plan->result.audio!=HA_STOP || plan->result.audio_handle!=hazard_word(r,D(EnemyFlightSoundHandles),r->bx)) return UGH_BAD_CALLBACK;
        plan->audio_used=1;
    }
    return ugh_call_near(target,ret,r);
}
static int hazard_audio(Regs *r,HazardPlan *plan,uint16_t segment,uint16_t target) {
    if(plan->result.audio==HA_NONE) return UGH_BAD_CALLBACK;
    plan->audio_used=1;return ugh_dispatch(segment,target,r);
}
#define READ(n,i) hazard_word(r,D(n),(i))
#define WRITE(n,i,v) hazard_write(r,plan,D(n),(i),(v))
#define A(n) READ(n,r->bx)
#define W(n,v) WRITE(n,r->bx,v)
#define DESC(n) rd16(r->ds,(uint16_t)(r->si+(n)))
static int tail(Regs *r,HazardPlan *plan,unsigned field) { return hazard_tail_call(r,plan,DESC(field)); }
static uint16_t hs_0_shl(Regs *r,HazardPlan *plan,uint16_t v,unsigned n) { (void)plan;
    for(unsigned i=0;i<n;i++) { flag(r,CF,v&0x8000u); v=(uint16_t)(v<<1); }
    szp(r,v,16); if(n==1) flag(r,OF,!!(v&0x8000u)^!!(r->flags&CF));
    return v;
}

static uint16_t hs_0_inc(Regs *r,HazardPlan *plan,uint16_t v) { (void)plan;
    uint16_t cf=r->flags&CF; v=add16(r,v,1,0); flag(r,CF,cf); return v;
}

static int hs_0_less(const Regs *r,HazardPlan *plan) { (void)plan; return !!(r->flags&SF)!=!!(r->flags&OF); }

static void hs_0_enemy_init(Regs *r,HazardPlan *plan,unsigned field,int load_descriptor) { (void)plan;
    if(load_descriptor) r->si=A(EnemyDescriptors);
    r->ax=DESC(field); W(EnemyStateCallbacks,r->ax);
    W(EnemyAnimationByteOffsets,0xfffe); W(EnemyAnimationCountdowns,1);
}

static int hs_0_enemy_frame(Regs *r,HazardPlan *plan,unsigned field) { (void)plan;
    for(unsigned budget=0;budget<32768;budget++) {
        r->bp=A(EnemyDirectionOrTargetPlayer);
        r->di=rd16(r->ds,(uint16_t)(r->bp+r->si+field));
        r->di=add16(r,r->di,A(EnemyAnimationByteOffsets),0);
        r->ax=rd16(r->ds,r->di); sub16(r,r->ax,0xffff,0);
        if(r->ax!=0xffff) { W(EnemySpriteIds,r->ax); return UGH_OK; }
        W(EnemyAnimationByteOffsets,0);
    }
    return UGH_BUDGET;
}

static void hs_0_score(Regs *r,HazardPlan *plan) { (void)plan;
    r->ax=DESC(0x3a);
    WRITE(ScoreLowWord,0,add16(r,READ(ScoreLowWord,0),r->ax,0));
    WRITE(ScoreHighWord,0,add16(r,READ(ScoreHighWord,0),0,!!(r->flags&CF)));
}

static int hs_0_enemy_wait(Regs *r,HazardPlan *plan,unsigned field) { (void)plan;
    uint16_t count=dec16(r,A(EnemyStateCounters)); W(EnemyStateCounters,count);
    if(count) return UGH_OK;
    r->si=A(EnemyDescriptors); return tail(r,plan,field);
}

static int shell_BeginBirdDelay(Regs *r,HazardPlan *plan) { (void)plan;
    hs_0_enemy_init(r,plan,0x0a,1); W(EnemySpriteIds,0xffff); r->ax=A(EnemyInitialDelays); W(EnemyStateCounters,r->ax); return UGH_OK;
}

static int shell_WaitForBirdFlight(Regs *r,HazardPlan *plan) { (void)plan; return hs_0_enemy_wait(r,plan,0x0c); }

static int shell_WaitForBirdWarning(Regs *r,HazardPlan *plan) { (void)plan; return hs_0_enemy_wait(r,plan,0x10); }

static int shell_StunBirdAndAwardScore(Regs *r,HazardPlan *plan) { (void)plan;
    r->ax=DESC(0x1e); W(EnemyStateCallbacks,r->ax); hs_0_score(r,plan); W(EnemyStateCounters,0);
    logic(r,A(EnemyHorizontalSpeeds),16); r->si=DESC((r->flags&SF)?0x36:0x38);
    r->ax=rd16(r->ds,r->si); W(EnemySpriteIds,r->ax); return UGH_OK;
}

static int shell_UpdateStunnedBird(Regs *r,HazardPlan *plan) { (void)plan;
    r->ax=add16(r,A(EnemyHorizontalSpeeds),A(EnemyX32),0); sub16(r,r->ax,0xfc00,0);
    if(hs_0_less(r,plan)||(r->flags&ZF)) goto gone;
    sub16(r,r->ax,0x2800,0); if(!hs_0_less(r,plan)) goto gone;
    W(EnemyX32,r->ax); r->ax=A(EnemyStateCounters); sub16(r,r->ax,40,0);
    if(hs_0_less(r,plan)) { r->ax=hs_0_inc(r,plan,r->ax); W(EnemyStateCounters,r->ax); }
    r->ax=add16(r,r->ax,A(EnemyY32),0); sub16(r,r->ax,0x1800,0); if(!hs_0_less(r,plan)) goto gone;
    W(EnemyY32,r->ax); return UGH_OK;
gone: r->si=A(EnemyDescriptors); return tail(r,plan,8);
}

static int shell_BeginTriopterusPatrol(Regs *r,HazardPlan *plan) { (void)plan; hs_0_enemy_init(r,plan,0x0a,1); return UGH_OK; }

static int shell_BeginTriopterusAlert(Regs *r,HazardPlan *plan) { (void)plan; hs_0_enemy_init(r,plan,0x0e,0); W(EnemyStateCounters,140); return UGH_OK; }

static int shell_BeginTriopterusCharge(Regs *r,HazardPlan *plan) { (void)plan; hs_0_enemy_init(r,plan,0x12,0); W(EnemyStateCounters,0); return UGH_OK; }

static int shell_BeginTriopterusRecovery(Regs *r,HazardPlan *plan) { (void)plan; hs_0_enemy_init(r,plan,0x16,0); return UGH_OK; }

static int shell_BeginTriopterusImpactRecovery(Regs *r,HazardPlan *plan) { (void)plan;
    /* Original installs +16 (ordinary recovery), despite its +18 caller. */
    hs_0_enemy_init(r,plan,0x16,0); return UGH_OK;
}

static int shell_StunTriopterusAndAwardScore(Regs *r,HazardPlan *plan) { (void)plan;
    r->ax=DESC(0x1e); W(EnemyStateCallbacks,r->ax); hs_0_score(r,plan);
    W(EnemyAnimationByteOffsets,0xfffe); W(EnemyAnimationCountdowns,1); W(EnemyStateCounters,350); return UGH_OK;
}

static int shell_UpdateStunnedTriopterus(Regs *r,HazardPlan *plan) { (void)plan;
    r->si=A(EnemyDescriptors);
    uint16_t count=dec16(r,A(EnemyStateCounters)); W(EnemyStateCounters,count); if(!count) return tail(r,plan,8);
    count=dec16(r,A(EnemyAnimationCountdowns)); W(EnemyAnimationCountdowns,count); if(count) return UGH_OK;
    W(EnemyAnimationCountdowns,4); W(EnemyAnimationByteOffsets,add16(r,A(EnemyAnimationByteOffsets),2,0));
    return hs_0_enemy_frame(r,plan,0x36);
}

static int shell_InitializeDinoAnimation(Regs *r,HazardPlan *plan) { (void)plan; hs_0_enemy_init(r,plan,0x12,1); return UGH_OK; }

static int shell_StunDinoAndAwardScore(Regs *r,HazardPlan *plan) { (void)plan;
    r->ax=DESC(0x1e); W(EnemyStateCallbacks,r->ax); hs_0_score(r,plan); W(EnemyStateCounters,350);
    r->si=DESC(0x36); r->ax=rd16(r->ds,r->si); W(EnemySpriteIds,r->ax); return UGH_OK;
}

static int shell_UpdateStunnedDino(Regs *r,HazardPlan *plan) { (void)plan; return hs_0_enemy_wait(r,plan,0x10); }

static int shell_InitializeFruitTreeAnimation(Regs *r,HazardPlan *plan) { (void)plan;
    hs_0_enemy_init(r,plan,0x0a,1);
    /* Actual SHL, not SAR: retain the original cached-coordinate bug. */
    r->ax=hs_0_shl(r,plan,A(EnemyX32),5); W(EnemyDrawX,r->ax);
    r->ax=hs_0_shl(r,plan,A(EnemyY32),5); W(EnemyDrawY,r->ax); return UGH_OK;
}

#undef W
#undef W
#define R(n,i) READ(n,i)
#define W(n,i,v) WRITE(n,i,v)
#define B(n,v) WRITE(n,r->bx,v)
#define F(n) DESC(n)
static int hs_1_lt(const Regs *r,HazardPlan *plan) { (void)plan; return !!(r->flags&SF)!=!!(r->flags&OF); }

static int hs_1_gt(const Regs *r,HazardPlan *plan) { (void)plan; return !(r->flags&ZF)&&!hs_1_lt(r,plan); }

static uint16_t hs_1_shift(Regs *r,HazardPlan *plan,uint16_t v,unsigned n,int right) { (void)plan;
    for(unsigned i=0;i<n;i++) {
        flag(r,CF,right?(v&1):(v&0x8000));
        v=right?(uint16_t)((v>>1)|(v&0x8000)):(uint16_t)(v<<1);
    }
    szp(r,v,16); if(n==1) flag(r,OF,right?0:(!!(v&0x8000)^!!(r->flags&CF)));
    return v;
}

static void hs_1_push(Regs *r,HazardPlan *plan,uint16_t v) { (void)plan; r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,v); }

static uint16_t hs_1_pop(Regs *r,HazardPlan *plan) { (void)plan; uint16_t v=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return v; }

static int hs_1_effect(Regs *r,HazardPlan *plan,uint16_t segment,uint16_t offset,uint16_t ret) { (void)plan;
    hs_1_push(r,plan,1); hs_1_push(r,plan,255); hs_1_push(r,plan,segment); hs_1_push(r,plan,offset);
    hs_1_push(r,plan,r->cs); hs_1_push(r,plan,ret);
    int status=hazard_audio(r,plan,UGH_S_C_PlayAdlibEffect,UGH_O_C_PlayAdlibEffect);
    if(status) return status;
    r->sp=(uint16_t)(r->sp+4); r->sp=add16(r,r->sp,8,0); return UGH_OK;
}

static int hs_1_frame(Regs *r,HazardPlan *plan,int enemy,unsigned field,int directional) { (void)plan; (void)enemy;
    for(unsigned budget=0;budget<32768;budget++) {
        if(directional) r->bp=A(EnemyDirectionOrTargetPlayer);
        r->di=rd16(r->ds,(uint16_t)(r->si+field+(directional?r->bp:0)));
        r->di=add16(r,r->di,A(EnemyAnimationByteOffsets),0);
        r->ax=rd16(r->ds,r->di); sub16(r,r->ax,0xffff,0);
        if(r->ax!=0xffff) {
            B(EnemySpriteIds,r->ax);
            return UGH_OK;
        }
        B(EnemyAnimationByteOffsets,0);
    }
    return UGH_BUDGET;
}

static int hs_1_enemy_stone(Regs *r,HazardPlan *plan,uint16_t return_ip,int sprite) { (void)plan;
    int status=hazard_near(r,plan,G(FindThrownStoneHittingEnemy),return_ip); if(status) return status;
    if(r->flags&SF) return UGH_OK;
    W(ActorVerticalOrDemoPeriod,r->di,sub16(r,0,R(ActorVerticalOrDemoPeriod,r->di),0));
    if(sprite) W(ActorSpriteIds,r->di,0x222);
    return tail(r,plan,0x1c);
}

static int hs_1_enemy_player(Regs *r,HazardPlan *plan) { (void)plan;
    r->ax=A(EnemyPlatformIndices); r->di=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        sub16(r,r->ax,R(PlayerPlatformIndices,r->di),0); if(r->flags&ZF) return 1;
        r->di=add16(r,r->di,2,0); sub16(r,r->di,R(PlayerArrayBytes,0),0); if(r->flags&ZF) return 0;
    }
    return -1;
}

static void hs_1_face_player(Regs *r,HazardPlan *plan) { (void)plan;
    r->cx=A(EnemyHorizontalSpeeds); r->ax=A(EnemyX32); sub16(r,r->ax,R(PlayerX32,r->di),0);
    if(!hs_1_lt(r,plan)) { r->ax=logic(r,0,16); logic(r,r->cx,16); if(!(r->flags&SF)) r->cx=sub16(r,0,r->cx,0); }
    else { r->ax=2; logic(r,r->cx,16); if(r->flags&SF) r->cx=sub16(r,0,r->cx,0); }
    B(EnemyDirectionOrTargetPlayer,r->ax); B(EnemyHorizontalSpeeds,r->cx);
}

static int hs_1_enemy_tick(Regs *r,HazardPlan *plan,uint16_t period) { (void)plan;
    uint16_t count=dec16(r,A(EnemyAnimationCountdowns)); B(EnemyAnimationCountdowns,count); if(count) return 0;
    B(EnemyAnimationCountdowns,period); B(EnemyAnimationByteOffsets,add16(r,A(EnemyAnimationByteOffsets),2,0)); return 1;
}

static int hs_1_recover(Regs *r,HazardPlan *plan,int impact) { (void)plan;
    r->si=A(EnemyDescriptors);
    if(hs_1_enemy_tick(r,plan,4)) {
        r->bp=A(EnemyDirectionOrTargetPlayer); r->di=rd16(r->ds,(uint16_t)(r->bp+r->si+(impact?0x32:0x2a)));
        r->di=add16(r,r->di,A(EnemyAnimationByteOffsets),0); r->ax=rd16(r->ds,r->di); sub16(r,r->ax,0xffff,0);
        if(r->flags&ZF) return tail(r,plan,8);
        B(EnemySpriteIds,r->ax);
    }
    return hs_1_enemy_stone(r,plan,(uint16_t)(impact?G(AnimateTriopterusImpactRecovery)+0x38:G(AnimateTriopterusRecovery)+0x38),1);
}

static int shell_BeginBirdWarning(Regs *r,HazardPlan *plan) { (void)plan;
    r->si=A(EnemyDescriptors); r->ax=F(0xe); B(EnemyStateCallbacks,r->ax);
    B(EnemyStateCounters,70); hs_1_push(r,plan,r->bx); hs_1_push(r,plan,r->es);
    int st=hs_1_effect(r,plan,UGH_S_B325B_ext_325B,0,G(BeginBirdWarning)+0x23);
    if(st) return st;
    r->es=hs_1_pop(r,plan); r->bx=hs_1_pop(r,plan); return UGH_OK;
}

static int shell_LaunchBirdTowardPlayer(Regs *r,HazardPlan *plan) { (void)plan;
    r->si=A(EnemyDescriptors); r->di=logic(r,A(EnemyDirectionOrTargetPlayer)^1,16);
    sub16(r,r->di,R(PlayerCount,0),0); if(!hs_1_lt(r,plan)) r->di=logic(r,0,16);
    B(EnemyDirectionOrTargetPlayer,r->di); r->di=hs_1_shift(r,plan,r->di,1,0);
    sub16(r,R(PlayerX32,r->di),0x1400,0);
    if(hs_1_lt(r,plan)) {
        r->ax=logic(r,A(EnemyHorizontalSpeeds),16);
        if(!(r->flags&SF)) { r->ax=sub16(r,0,r->ax,0); B(EnemyHorizontalSpeeds,r->ax); }
        r->ax=0x27e0; r->cx=F(0x22);
    } else {
        r->ax=logic(r,A(EnemyHorizontalSpeeds),16);
        if(r->flags&SF) { r->ax=sub16(r,0,r->ax,0); B(EnemyHorizontalSpeeds,r->ax); }
        r->ax=0xfc20; r->cx=F(0x24);
    }
    B(EnemyX32,r->ax); B(EnemyAnimationOrDropLists,r->cx);
    r->ax=add16(r,R(PlayerY32,r->di),0x340,0); sub16(r,r->ax,R(WaterY32,0),0);
    if(hs_1_gt(r,plan)) r->ax=R(WaterY32,0);
    r->ax=sub16(r,r->ax,0x340,0); sub16(r,r->ax,0xff80,0);
    if(hs_1_lt(r,plan)) r->ax=0xff80;
    B(EnemyY32,r->ax); r->ax=F(0x12); B(EnemyStateCallbacks,r->ax);
    hs_1_push(r,plan,r->es); hs_1_push(r,plan,r->bx);
    hs_1_push(r,plan,0); hs_1_push(r,plan,255); hs_1_push(r,plan,UGH_S_B3260_ext_3260); hs_1_push(r,plan,0);
    hs_1_push(r,plan,r->cs); hs_1_push(r,plan,G(LaunchBirdTowardPlayer)+0x9f);
    int st=hazard_audio(r,plan,UGH_S_C_PlayAdlibEffect,UGH_O_C_PlayAdlibEffect);
    if(st) return st;
    r->sp=(uint16_t)(r->sp+4); r->sp=add16(r,r->sp,8,0);
    r->bx=hs_1_pop(r,plan); r->es=hs_1_pop(r,plan); B(EnemyFlightSoundHandles,r->ax); return UGH_OK;
}

static int shell_UpdateBirdFlight(Regs *r,HazardPlan *plan) { (void)plan;
    r->si=A(EnemyDescriptors); r->ax=add16(r,A(EnemyHorizontalSpeeds),A(EnemyX32),0);
    sub16(r,r->ax,0xfc00,0); int gone=hs_1_lt(r,plan)||(r->flags&ZF);
    if(!gone) { sub16(r,r->ax,0x2800,0); gone=!hs_1_lt(r,plan); }
    if(gone) {
        int status=hazard_near(r,plan,G(StopBirdFlightSound),(uint16_t)(G(UpdateBirdFlight)+0x1f)); if(status) return status; return tail(r,plan,8);
    }
    B(EnemyX32,r->ax); if(!hs_1_enemy_tick(r,plan,4)) return UGH_OK;
    /* Bird's sequence pointer is stored in its array, not the descriptor. */
    for(unsigned budget=0;;budget++) {
        if(budget==32768) return UGH_BUDGET;
        r->di=add16(r,A(EnemyAnimationOrDropLists),A(EnemyAnimationByteOffsets),0); r->ax=rd16(r->ds,r->di); sub16(r,r->ax,0xffff,0);
        if(r->ax!=0xffff) break;
        B(EnemyAnimationByteOffsets,0);
    }
    B(EnemySpriteIds,r->ax); int status=hazard_near(r,plan,G(FindThrownStoneHittingEnemy),(uint16_t)(G(UpdateBirdFlight)+0x5b)); if(status) return status;
    if(!(r->flags&SF)) {
        status=hazard_near(r,plan,G(StopBirdFlightSound),(uint16_t)(G(UpdateBirdFlight)+0x63)); if(status) return status;
        W(ActorVerticalOrDemoPeriod,r->di,sub16(r,0,R(ActorVerticalOrDemoPeriod,r->di),0)); W(ActorSpriteIds,r->di,0x222); return tail(r,plan,0x1c);
    }
    status=hazard_near(r,plan,G(FindPlayerTouchingEnemy),(uint16_t)(G(UpdateBirdFlight)+0x73)); if(status) return status; if(r->flags&SF) return UGH_OK;
    uint16_t old=r->di; r->di=(uint16_t)(old>>1); flag(r,CF,old&1); flag(r,OF,old&0x8000); szp(r,r->di,16);
    sub16(r,r->di,A(EnemyDirectionOrTargetPlayer),0); if(!(r->flags&ZF)) return UGH_OK;
    sub16(r,R(ScreenFadeStep,0),0,0); if(hs_1_lt(r,plan)) return UGH_OK;
    r->ax=0xfffe; W(ScreenFadeStep,0,r->ax); W(ScreenFadeLevel,0,add16(r,R(ScreenFadeLevel,0),r->ax,0)); return UGH_OK;
}

static int shell_StopBirdFlightSound(Regs *r,HazardPlan *plan) { (void)plan;
    hs_1_push(r,plan,r->bx); hs_1_push(r,plan,r->si); hs_1_push(r,plan,A(EnemyFlightSoundHandles));
    hs_1_push(r,plan,r->cs); hs_1_push(r,plan,G(StopBirdFlightSound)+11);
    int st=hazard_audio(r,plan,UGH_S_C_StopAdlibTrackChannel,UGH_O_C_StopAdlibTrackChannel);
    if(st) return st;
    r->sp=(uint16_t)(r->sp+4); r->sp=add16(r,r->sp,2,0);
    r->si=hs_1_pop(r,plan); r->bx=hs_1_pop(r,plan); return UGH_OK;
}

static int shell_UpdateTriopterusPatrol(Regs *r,HazardPlan *plan) { (void)plan;
    r->si=A(EnemyDescriptors);
    uint16_t count=dec16(r,A(EnemyAnimationCountdowns)); B(EnemyAnimationCountdowns,count);
    if(!count) {
        r->di=hs_1_shift(r,plan,A(EnemyPlatformIndices),1,0); r->ax=add16(r,A(EnemyHorizontalSpeeds),A(EnemyX32),0); B(EnemyX32,r->ax);
        r->ax=hs_1_shift(r,plan,r->ax,5,1); sub16(r,r->ax,R(PlatformLeftEdges,r->di),0); int turn=hs_1_lt(r,plan);
        if(!turn) { r->ax=add16(r,r->ax,32,0); sub16(r,r->ax,R(PlatformRightEdges,r->di),0); turn=!hs_1_lt(r,plan); }
        if(turn) { B(EnemyHorizontalSpeeds,sub16(r,0,A(EnemyHorizontalSpeeds),0)); B(EnemyDirectionOrTargetPlayer,logic(r,A(EnemyDirectionOrTargetPlayer)^2,16)); }
        B(EnemyAnimationCountdowns,4); B(EnemyAnimationByteOffsets,add16(r,A(EnemyAnimationByteOffsets),2,0));
        int status=hs_1_frame(r,plan,1,0x22,1); if(status) return status;
    }
    int found=hs_1_enemy_player(r,plan); if(found<0) return UGH_BUDGET; if(found) return tail(r,plan,0x0c);
    return hs_1_enemy_stone(r,plan,(uint16_t)(G(UpdateTriopterusPatrol)+0x8b),1);
}

static int shell_UpdateTriopterusAlert(Regs *r,HazardPlan *plan) { (void)plan;
    r->si=A(EnemyDescriptors); uint16_t count=dec16(r,A(EnemyStateCounters)); B(EnemyStateCounters,count); if(!count) return tail(r,plan,0x10);
    if(hs_1_enemy_tick(r,plan,5)) { int status=hs_1_frame(r,plan,1,0x2e,1); if(status) return status; }
    int status=hazard_near(r,plan,G(FindThrownStoneHittingEnemy),(uint16_t)(G(UpdateTriopterusAlert)+0x49)); if(status) return status;
    if(!(r->flags&SF)) { W(ActorVerticalOrDemoPeriod,r->di,sub16(r,0,R(ActorVerticalOrDemoPeriod,r->di),0)); W(ActorSpriteIds,r->di,0x222); return tail(r,plan,0x1c); }
    int found=hs_1_enemy_player(r,plan); if(found<0) return UGH_BUDGET; if(!found) return tail(r,plan,8);
    hs_1_face_player(r,plan); return UGH_OK;
}

static int shell_UpdateTriopterusCharge(Regs *r,HazardPlan *plan) { (void)plan;
    r->si=A(EnemyDescriptors); if(hs_1_enemy_tick(r,plan,4)) { int status=hs_1_frame(r,plan,1,0x26,1); if(status) return status; }
    int status=hazard_near(r,plan,G(FindThrownStoneHittingEnemy),(uint16_t)(G(UpdateTriopterusCharge)+0x3d)); if(status) return status;
    if(!(r->flags&SF)) { W(ActorVerticalOrDemoPeriod,r->di,sub16(r,0,R(ActorVerticalOrDemoPeriod,r->di),0)); W(ActorSpriteIds,r->di,0x222); return tail(r,plan,0x1c); }
    int found=hs_1_enemy_player(r,plan); if(found<0) return UGH_BUDGET; if(!found) return tail(r,plan,0x14);
    hs_1_face_player(r,plan); r->ax=dec16(r,A(EnemyDirectionOrTargetPlayer)); r->ax=add16(r,r->ax,A(EnemyStateCounters),0); B(EnemyStateCounters,r->ax);
    r->ax=add16(r,r->ax,A(EnemyHorizontalSpeeds),0); r->ax=add16(r,r->ax,A(EnemyX32),0); B(EnemyX32,r->ax);
    status=hazard_near(r,plan,G(FindPlayerTouchingEnemy),(uint16_t)(G(UpdateTriopterusCharge)+0xbc)); if(status) return status; if(r->flags&SF) return UGH_OK;
    W(PlayerY32,r->di,sub16(r,R(PlayerY32,r->di),32,0)); r->ax=add16(r,A(EnemyHorizontalSpeeds),A(EnemyStateCounters),0);
    hs_1_push(r,plan,r->ax); r->ax=hs_1_shift(r,plan,r->ax,5,0); W(PlayerHorizontalVelocities,r->di,r->ax); r->ax=hs_1_pop(r,plan);
    r->ax=hs_1_shift(r,plan,r->ax,4,0); W(PlayerVerticalVelocities,r->di,r->ax); W(PlayerPlatformIndices,r->di,0xffff); return tail(r,plan,0x18);
}

static int shell_AnimateTriopterusRecovery(Regs *r,HazardPlan *plan) { (void)plan; return hs_1_recover(r,plan,0); }

static int shell_AnimateTriopterusImpactRecovery(Regs *r,HazardPlan *plan) { (void)plan; return hs_1_recover(r,plan,1); }

static int shell_UpdateDinoForce(Regs *r,HazardPlan *plan) { (void)plan;
    r->si=A(EnemyDescriptors);
    if(hs_1_enemy_tick(r,plan,15)) {
        sub16(r,A(EnemyAnimationByteOffsets),6,0);
        if(r->flags&ZF) {
            hs_1_push(r,plan,r->bx); hs_1_push(r,plan,r->si); int status=hs_1_effect(r,plan,UGH_S_B3265_ext_3265,UGH_O_B3265_ext_3265,(uint16_t)(G(UpdateDinoForce)+0x34));
            if(status) return status;
            r->si=hs_1_pop(r,plan); r->bx=hs_1_pop(r,plan);
        }
        int status=hs_1_frame(r,plan,1,0x26,0); if(status) return status;
    }
    r->di=logic(r,0,16);
    for(unsigned budget=0;budget<32768;budget++) {
        r->ax=hs_1_shift(r,plan,sub16(r,F(2),9,0),5,0); r->ax=add16(r,r->ax,A(EnemyY32),0); sub16(r,r->ax,R(PlayerY32,r->di),0); if(hs_1_lt(r,plan)) goto next;
        r->ax=hs_1_shift(r,plan,sub16(r,F(2),30,0),5,0); r->ax=add16(r,r->ax,A(EnemyY32),0); sub16(r,r->ax,R(PlayerY32,r->di),0); if(hs_1_gt(r,plan)) goto next;
        r->ax=hs_1_shift(r,plan,sub16(r,F(0),16,0),5,0); r->ax=add16(r,r->ax,A(EnemyX32),0); sub16(r,r->ax,R(PlayerX32,r->di),0); if(hs_1_lt(r,plan)) goto next;
        r->ax=hs_1_shift(r,plan,sub16(r,F(0),104,0),5,0); r->ax=add16(r,r->ax,A(EnemyX32),0); r->ax=sub16(r,r->ax,0x340,0); sub16(r,r->ax,R(PlayerX32,r->di),0); if(hs_1_gt(r,plan)) goto next;
        sub16(r,A(EnemyAnimationByteOffsets),5,0); r->ax=hs_1_lt(r,plan)?41:0xffd7; W(PlayerHorizontalVelocities,r->di,add16(r,R(PlayerHorizontalVelocities,r->di),r->ax,0));
next:   r->di=add16(r,r->di,2,0); sub16(r,r->di,R(PlayerCount,0),0); if(!(r->flags&ZF)) break;
        if(budget==32767) return UGH_BUDGET;
    }
    return hs_1_enemy_stone(r,plan,(uint16_t)(G(UpdateDinoForce)+0xd3),0);
}

static int shell_UpdateFruitTreeAnimation(Regs *r,HazardPlan *plan) { (void)plan;
    uint16_t count=dec16(r,A(EnemyAnimationCountdowns)); B(EnemyAnimationCountdowns,count); if(count) return UGH_OK;
    r->si=A(EnemyDescriptors); B(EnemyAnimationCountdowns,6); B(EnemyAnimationByteOffsets,add16(r,A(EnemyAnimationByteOffsets),2,0));
    int status=hs_1_frame(r,plan,1,0x22,0); if(status) return status;
    status=hazard_near(r,plan,G(FindThrownStoneHittingEnemy),(uint16_t)(G(UpdateFruitTreeAnimation)+0x38)); if(status) return status;
    if(r->flags&SF) return UGH_OK;
    r->ax=sub16(r,0,R(ActorVerticalOrDemoPeriod,r->di),0); r->ax=hs_1_shift(r,plan,r->ax,1,1); W(ActorVerticalOrDemoPeriod,r->di,r->ax); W(ActorSpriteIds,r->di,0x222);
    r->si=A(EnemyDescriptors); return tail(r,plan,0x1c);
}

static int shell_ReleaseTreeReward(Regs *r,HazardPlan *plan) { (void)plan;
    r->ax=F(0x1e); B(EnemyStateCallbacks,r->ax); B(EnemyStateCounters,210); B(EnemySpriteIds,0xe8);
    r->ax=R(ActorX32,r->di); r->bp=R(ActorY32,r->di);
    r->cx=R(ActorMotionWaitOrDemoRepeats,r->di); r->dx=hs_1_shift(r,plan,sub16(r,0,R(ActorVerticalOrDemoPeriod,r->di),0),2,1);
    r->si=A(EnemyAnimationOrDropLists); r->si=rd16(r->ds,r->si);
    int st=hazard_near(r,plan,F(4),G(ReleaseTreeReward)+0x31); if(st) return st;
    B(EnemyAnimationOrDropLists,add16(r,A(EnemyAnimationOrDropLists),2,0));
    hs_1_push(r,plan,r->bx); st=hs_1_effect(r,plan,UGH_S_B3274_ext_3274,0,G(ReleaseTreeReward)+0x47);
    if(st) return st;
    r->bx=hs_1_pop(r,plan); return UGH_OK;
}

static uint16_t hs_2_cell(uint16_t base, uint16_t index) { return (uint16_t)(base+index); }

static int shell_AdvanceTreeRewardCooldown(Regs *r,HazardPlan *plan) { (void)plan;
    r->si=rd16(r->ds,hs_2_cell(D(EnemyDescriptors),r->bx));
    uint16_t count=dec16(r,rd16(r->ds,hs_2_cell(D(EnemyStateCounters),r->bx)));
    hazard_write(r,plan,D(EnemyStateCounters),r->bx,count);
    if(!count) {
        r->di=rd16(r->ds,hs_2_cell(D(EnemyAnimationOrDropLists),r->bx));
        uint16_t end=rd16(r->ds,r->di);
        sub16(r,end,65535,0);
        r->ax=rd16(r->ds,(uint16_t)(r->si+(end==65535 ? 0x20 : 0x0a)));
        hazard_write(r,plan,D(EnemyStateCallbacks),r->bx,r->ax);
    }
    return UGH_OK;
}



#undef A
#undef B
#undef R
#undef W
#undef F
#undef READ
#undef WRITE
#undef DESC
EXPORT int c_BeginBirdDelay(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_BIRD_DELAY,&plan)) return l1_BeginBirdDelay(r);
    int status=shell_BeginBirdDelay(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_WaitForBirdFlight(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_BIRD_WAIT,&plan)) return l1_WaitForBirdFlight(r);
    int status=shell_WaitForBirdFlight(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_BeginBirdWarning(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_BIRD_WARNING,&plan)) return l1_BeginBirdWarning(r);
    int status=shell_BeginBirdWarning(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_WaitForBirdWarning(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_BIRD_WARN_WAIT,&plan)) return l1_WaitForBirdWarning(r);
    int status=shell_WaitForBirdWarning(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_LaunchBirdTowardPlayer(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_BIRD_LAUNCH,&plan)) return l1_LaunchBirdTowardPlayer(r);
    int status=shell_LaunchBirdTowardPlayer(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_UpdateBirdFlight(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_BIRD_FLIGHT,&plan)) return l1_UpdateBirdFlight(r);
    int status=shell_UpdateBirdFlight(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_StunBirdAndAwardScore(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_BIRD_STUN,&plan)) return l1_StunBirdAndAwardScore(r);
    int status=shell_StunBirdAndAwardScore(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_UpdateStunnedBird(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_BIRD_FALL,&plan)) return l1_UpdateStunnedBird(r);
    int status=shell_UpdateStunnedBird(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_StopBirdFlightSound(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_BIRD_STOP,&plan)) return l1_StopBirdFlightSound(r);
    int status=shell_StopBirdFlightSound(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_BeginTriopterusPatrol(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TRIO_PATROL_BEGIN,&plan)) return l1_BeginTriopterusPatrol(r);
    int status=shell_BeginTriopterusPatrol(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_UpdateTriopterusPatrol(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TRIO_PATROL,&plan)) return l1_UpdateTriopterusPatrol(r);
    int status=shell_UpdateTriopterusPatrol(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_BeginTriopterusAlert(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TRIO_ALERT_BEGIN,&plan)) return l1_BeginTriopterusAlert(r);
    int status=shell_BeginTriopterusAlert(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_UpdateTriopterusAlert(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TRIO_ALERT,&plan)) return l1_UpdateTriopterusAlert(r);
    int status=shell_UpdateTriopterusAlert(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_BeginTriopterusCharge(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TRIO_CHARGE_BEGIN,&plan)) return l1_BeginTriopterusCharge(r);
    int status=shell_BeginTriopterusCharge(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_UpdateTriopterusCharge(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TRIO_CHARGE,&plan)) return l1_UpdateTriopterusCharge(r);
    int status=shell_UpdateTriopterusCharge(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_BeginTriopterusRecovery(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TRIO_RECOVER_BEGIN,&plan)) return l1_BeginTriopterusRecovery(r);
    int status=shell_BeginTriopterusRecovery(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_AnimateTriopterusRecovery(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TRIO_RECOVER,&plan)) return l1_AnimateTriopterusRecovery(r);
    int status=shell_AnimateTriopterusRecovery(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_BeginTriopterusImpactRecovery(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TRIO_IMPACT_BEGIN,&plan)) return l1_BeginTriopterusImpactRecovery(r);
    int status=shell_BeginTriopterusImpactRecovery(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_AnimateTriopterusImpactRecovery(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TRIO_IMPACT,&plan)) return l1_AnimateTriopterusImpactRecovery(r);
    int status=shell_AnimateTriopterusImpactRecovery(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_StunTriopterusAndAwardScore(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TRIO_STUN,&plan)) return l1_StunTriopterusAndAwardScore(r);
    int status=shell_StunTriopterusAndAwardScore(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_UpdateStunnedTriopterus(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TRIO_STUNNED,&plan)) return l1_UpdateStunnedTriopterus(r);
    int status=shell_UpdateStunnedTriopterus(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_InitializeDinoAnimation(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_DINO_BEGIN,&plan)) return l1_InitializeDinoAnimation(r);
    int status=shell_InitializeDinoAnimation(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_UpdateDinoForce(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_DINO_FORCE,&plan)) return l1_UpdateDinoForce(r);
    int status=shell_UpdateDinoForce(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_StunDinoAndAwardScore(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_DINO_STUN,&plan)) return l1_StunDinoAndAwardScore(r);
    int status=shell_StunDinoAndAwardScore(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_UpdateStunnedDino(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_DINO_STUNNED,&plan)) return l1_UpdateStunnedDino(r);
    int status=shell_UpdateStunnedDino(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_InitializeFruitTreeAnimation(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TREE_BEGIN,&plan)) return l1_InitializeFruitTreeAnimation(r);
    int status=shell_InitializeFruitTreeAnimation(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_UpdateFruitTreeAnimation(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TREE_ANIMATE,&plan)) return l1_UpdateFruitTreeAnimation(r);
    int status=shell_UpdateFruitTreeAnimation(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_ReleaseTreeReward(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TREE_RELEASE,&plan)) return l1_ReleaseTreeReward(r);
    int status=shell_ReleaseTreeReward(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_AdvanceTreeRewardCooldown(Regs *r) {
    HazardPlan plan;
    if(!hazard_project(r,H_TREE_COOLDOWN,&plan)) return l1_AdvanceTreeRewardCooldown(r);
    int status=shell_AdvanceTreeRewardCooldown(r,&plan);
    return hazard_finish(&plan,status);
}
EXPORT int c_IgnoreExhaustedTree(Regs *r) { (void)r;return UGH_OK; }
EXPORT int c_DispatchEnemyStates(Regs *r) {
    size_t count=0;
    while(count<5 && hazard_word(r,D(EnemyDescriptors),(uint16_t)(2*count))!=65535u) count++;
    if(count==5 && hazard_word(r,D(EnemyDescriptors),10)!=65535u) return l1_DispatchEnemyStates(r);
    r->bx=logic(r,0,16);size_t cursor=0;
    for(;;) {
        sub16(r,hazard_word(r,D(EnemyDescriptors),r->bx),65535u,0);
        int selected=hazards_next(count,&cursor);if(selected<0) return UGH_OK;
        int status=ugh_call_near(hazard_word(r,D(EnemyStateCallbacks),r->bx),G(DispatchEnemyStates)+16,r);
        if(status) return status;
        r->bx=add16(r,r->bx,2,0);
    }
}
