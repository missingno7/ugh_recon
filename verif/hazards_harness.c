/* Actual L1 and native C. One operation, arbitrary admitted prior slot state.
 * Immutable resources; disjoint ordinary normalized data and stack; no MMIO.
 * Tails are observed rather than recursively executed, so every transition is
 * proved separately. Native contacts use independent actual L1 contact bodies. */
#ifdef __CPROVER__
void __CPROVER_assert(_Bool,const char *);
void __CPROVER_assume(_Bool);
#define CHECK(c,m) __CPROVER_assert((c),(m))
#define ASSUME(c) __CPROVER_assume(c)
#else
#include <stdio.h>
#include <stdlib.h>
#define CHECK(c,m) do { if(!(c)) { fprintf(stderr,"%s line %d entry %d case %lu\n",m,__LINE__,operation,comparisons);exit(23); } } while(0)
#define ASSUME(c) CHECK(c,"enumeration relation")
static unsigned long comparisons;
#endif

static HazardSlot slot;
static HazardWorld world;
static HazardType type;
static LevelPlatform platforms[10];
typedef struct HazardResources { uint16_t first[13],next[13]; } HazardResources;
static HazardResources resource_store;
static uint16_t sampled_cursor;
static uint16_t stack_words[128];
static uint16_t list_word;
static HazardResult observed;
static uint16_t reference_state,reference_tail;
static HazardEntry operation;
static int near_context;
static int dispatcher_mode;
static unsigned dispatcher_count,visit_count;
static uint16_t visits[5];
#ifdef CONTACT_CONTRACT
static int selected_stone,selected_player;
static int stone_query,player_query;
static ObjectPosition queried_stone_position,queried_player_position,queried_players[2];
static ObjectGeometry queried_geometry;
static StoneContactView queried_stones[16];
static uint16_t queried_count;
/* These are relational callee contracts, NOT implementations of contacts.
 * They allow any selected slot/miss and assert identical query arguments.
 * Full sixteen-entry contact selection remains its separately stated C link. */
ContactSelection contract_stones(const StoneContactView *stones,size_t count,ObjectPosition object) {
    CHECK(stone_query,"reference makes the same stone query");stone_query=0;
    CHECK(count==world.stone_count && object.x32==queried_stone_position.x32 && object.y32==queried_stone_position.y32,"same stone query position/count");
    for(size_t i=0;i<count;i++) CHECK(stones[i].position.x32==queried_stones[i].position.x32 && stones[i].position.y32==queried_stones[i].position.y32 &&
        stones[i].thrown_stone==queried_stones[i].thrown_stone && stones[i].vertical_step==queried_stones[i].vertical_step,"same complete borrowed stone view");
    ContactSelection result={selected_stone,0};return result;
}
ContactSelection contract_players(ObjectPosition object,ObjectGeometry geometry,const ObjectPosition players[2],uint16_t count) {
    CHECK(player_query,"reference makes the same player query");player_query=0;
    CHECK(object.x32==queried_player_position.x32 && object.y32==queried_player_position.y32 && count==queried_count,"same player query position/count");
    CHECK(geometry.anchor_x==queried_geometry.anchor_x && geometry.anchor_y==queried_geometry.anchor_y &&
        geometry.extent_x==queried_geometry.extent_x && geometry.extent_y==queried_geometry.extent_y,"same complete contact geometry");
    for(unsigned i=0;i<2;i++) CHECK(players[i].x32==queried_players[i].x32 && players[i].y32==queried_players[i].y32,"same borrowed player positions");
    ContactSelection result={selected_player,0};return result;
}
#endif
enum { DESCRIPTOR=256, SEQUENCES=1024, FLIGHT=4096, REWARDS=5000, ITEM_TYPE=6000 };

static void observe(HazardField field,unsigned index,uint16_t value) {
    CHECK(observed.count<16,"bounded semantic write log");
    observed.writes[observed.count++]=(HazardWrite){field,(uint16_t)index,value};
}
uint16_t hz_read(uint16_t segment,uint16_t address) {
    if(segment==1) { CHECK(address>=36500u && address<36756u && !(address&1u),"stack footprint");return stack_words[(address-36500u)/2]; }
    CHECK(segment==0,"ordinary data bank");
    if(dispatcher_mode && address>=D(EnemyDescriptors) && address<=D(EnemyDescriptors)+10u)
        return (address-D(EnemyDescriptors))/2<dispatcher_count?DESCRIPTOR:65535u;
    if(dispatcher_mode && address>=D(EnemyStateCallbacks) && address<D(EnemyStateCallbacks)+10u) return G(IgnoreActorState);
    if(address==D(EnemyDescriptors)) return DESCRIPTOR;
    if(address==D(EnemyPlatformIndices)) return slot.platform;
    if(address==D(EnemyX32)) return slot.position.x32;
    if(address==D(EnemyY32)) return slot.position.y32;
    if(address==D(EnemyAnimationOrDropLists)) return list_word;
    if(address==D(EnemyInitialDelays)) return slot.initial_delay;
    if(address==D(EnemyHorizontalSpeeds)) return slot.speed;
    if(address==D(EnemyStateCallbacks)) return code(slot.state);
    if(address==D(EnemyStateCounters)) return slot.counter;
    if(address==D(EnemyDrawX)) return slot.draw_x;
    if(address==D(EnemyDrawY)) return slot.draw_y;
    if(address==D(EnemyAnimationByteOffsets)) return slot.animation_cursor;
    if(address==D(EnemyAnimationCountdowns)) return slot.animation_countdown;
    if(address==D(EnemySpriteIds)) return slot.sprite;
    if(address==D(EnemyDirectionOrTargetPlayer)) return slot.direction;
    if(address==D(EnemyFlightSoundHandles)) return slot.flight_sound;
    if(address>=D(PlayerX32) && address<D(PlayerX32)+4u) return world.players[(address-D(PlayerX32))/2].position.x32;
    if(address>=D(PlayerY32) && address<D(PlayerY32)+4u) return world.players[(address-D(PlayerY32))/2].position.y32;
    if(address>=D(PlayerPlatformIndices) && address<D(PlayerPlatformIndices)+4u) return world.players[(address-D(PlayerPlatformIndices))/2].platform;
    if(address>=D(PlayerHorizontalVelocities) && address<D(PlayerHorizontalVelocities)+4u) return world.players[(address-D(PlayerHorizontalVelocities))/2].horizontal_velocity;
    if(address>=D(PlayerVerticalVelocities) && address<D(PlayerVerticalVelocities)+4u) return world.players[(address-D(PlayerVerticalVelocities))/2].vertical_velocity;
    if(address==D(PlayerCount)) return world.player_count;
    if(address==D(PlayerArrayBytes)) return (uint16_t)(world.player_slots*2);
    if(address==D(WaterY32)) return world.water_y32;
    if(address==D(ScreenFadeStep)) return world.fade_step;
    if(address==D(ScreenFadeLevel)) return world.fade_level;
    if(address==D(ScoreLowWord)) return (uint16_t)world.score;
    if(address==D(ScoreHighWord)) return (uint16_t)(world.score>>16);
    if(address>=D(ActorDescriptors) && address<=D(ActorDescriptors)+32u) {
        unsigned i=(address-D(ActorDescriptors))/2;
        if(i>=world.stone_count) return 65535u;
        return world.stones[i].contact.thrown_stone?D(Data_78DC):1;
    }
    if(address>=D(ActorUpdateOrScriptCursor) && address<D(ActorUpdateOrScriptCursor)+32u) return G(UpdateThrownStone);
    if(address>=D(ActorX32) && address<D(ActorX32)+32u) return world.stones[(address-D(ActorX32))/2].contact.position.x32;
    if(address>=D(ActorY32) && address<D(ActorY32)+32u) return world.stones[(address-D(ActorY32))/2].contact.position.y32;
    if(address>=D(ActorVerticalOrDemoPeriod) && address<D(ActorVerticalOrDemoPeriod)+32u) return world.stones[(address-D(ActorVerticalOrDemoPeriod))/2].contact.vertical_step;
    if(address>=D(ActorMotionWaitOrDemoRepeats) && address<D(ActorMotionWaitOrDemoRepeats)+32u) return world.stones[(address-D(ActorMotionWaitOrDemoRepeats))/2].horizontal_step;
    if(address>=D(ActorSpriteIds) && address<D(ActorSpriteIds)+32u) return world.stones[(address-D(ActorSpriteIds))/2].sprite;
    if(address>=D(PlatformLeftEdges) && address<D(PlatformLeftEdges)+20u) return platforms[(address-D(PlatformLeftEdges))/2].left;
    if(address>=D(PlatformRightEdges) && address<D(PlatformRightEdges)+20u) return platforms[(address-D(PlatformRightEdges))/2].right;
    if(address==DESCRIPTOR) return type.geometry.anchor_x;
    if(address==DESCRIPTOR+2) return type.geometry.anchor_y;
    if(address==DESCRIPTOR+4) return type.geometry.extent_x;
    if(address==DESCRIPTOR+6) return type.geometry.extent_y;
    if(address>=DESCRIPTOR+8 && address<DESCRIPTOR+34) return code(type.handlers[(address-DESCRIPTOR-8)/2]);
    if(address>=DESCRIPTOR+34 && address<DESCRIPTOR+58) return (uint16_t)(SEQUENCES+64*((address-DESCRIPTOR-34)/2));
    if(address==DESCRIPTOR+58) return type.score;
    if(address==REWARDS) return type.rewards_exhausted?65535u:ITEM_TYPE;
    if(address==ITEM_TYPE+4) return G(SpawnFallingItem);
    for(unsigned i=0;i<13;i++) {
        uint16_t base=i==12?FLIGHT:(uint16_t)(SEQUENCES+64*i);
        if(address==base) return resource_store.first[i];
    }
    for(unsigned i=0;i<13;i++) {
        uint16_t base=i==12?FLIGHT:(uint16_t)(SEQUENCES+64*i);
        if(address==(uint16_t)(base+sampled_cursor+2u)) return resource_store.next[i];
    }
    CHECK(0,"immutable animation window footprint");return 0;
}
void hz_write(uint16_t segment,uint16_t address,uint16_t value) {
    if(segment==1) { CHECK(address>=36500u && address<36756u && !(address&1u),"stack write footprint");stack_words[(address-36500u)/2]=value;return; }
    CHECK(segment==0,"ordinary write bank");
    if(address==D(EnemyStateCallbacks)) {
        reference_state=value;observe(HW_STATE,0,value);return;
    }
    if(address==D(EnemyX32)) { slot.position.x32=value;observe(HW_X,0,value);return; }
    if(address==D(EnemyY32)) { slot.position.y32=value;observe(HW_Y,0,value);return; }
    if(address==D(EnemyHorizontalSpeeds)) { slot.speed=value;observe(HW_SPEED,0,value);return; }
    if(address==D(EnemyStateCounters)) { slot.counter=value;observe(HW_COUNTER,0,value);return; }
    if(address==D(EnemyAnimationByteOffsets)) { slot.animation_cursor=value;observe(HW_CURSOR,0,value);return; }
    if(address==D(EnemyAnimationCountdowns)) { slot.animation_countdown=value;observe(HW_TICK,0,value);return; }
    if(address==D(EnemySpriteIds)) { slot.sprite=value;observe(HW_SPRITE,0,value);return; }
    if(address==D(EnemyDirectionOrTargetPlayer)) { slot.direction=value;observe(HW_DIRECTION,0,value);return; }
    if(address==D(EnemyDrawX)) { slot.draw_x=value;observe(HW_DRAW_X,0,value);return; }
    if(address==D(EnemyDrawY)) { slot.draw_y=value;observe(HW_DRAW_Y,0,value);return; }
    if(address==D(EnemyFlightSoundHandles)) { slot.flight_sound=value;return; }
    if(address==D(EnemyAnimationOrDropLists)) {
        unsigned event=operation==H_TREE_RELEASE?2:value==SEQUENCES?0:1;
        if(event==2) slot.reward_cursor++;
        else slot.flight_side=(HazardFlightSide)event;
        list_word=value;observe(HW_LIST,0,(uint16_t)event);return;
    }
    if(address==D(ScoreLowWord)) { world.score=(world.score&4294901760u)|value;observe(HW_SCORE_LOW,0,value);return; }
    if(address==D(ScoreHighWord)) { world.score=(world.score&65535u)|((uint32_t)value<<16);observe(HW_SCORE_HIGH,0,value);return; }
    if(address==D(ScreenFadeStep)) { world.fade_step=value;observe(HW_FADE_STEP,0,value);return; }
    if(address==D(ScreenFadeLevel)) { world.fade_level=value;observe(HW_FADE_LEVEL,0,value);return; }
    if(address>=D(ActorVerticalOrDemoPeriod) && address<D(ActorVerticalOrDemoPeriod)+32u) {
        unsigned i=(address-D(ActorVerticalOrDemoPeriod))/2;world.stones[i].contact.vertical_step=value;observe(HW_STONE_VERTICAL,i,value);return;
    }
    if(address>=D(ActorSpriteIds) && address<D(ActorSpriteIds)+32u) {
        unsigned i=(address-D(ActorSpriteIds))/2;world.stones[i].sprite=value;observe(HW_STONE_SPRITE,i,value);return;
    }
    if(address>=D(PlayerY32) && address<D(PlayerY32)+4u) {
        unsigned i=(address-D(PlayerY32))/2;world.players[i].position.y32=value;observe(HW_PLAYER_Y,i,value);return;
    }
    if(address>=D(PlayerHorizontalVelocities) && address<D(PlayerHorizontalVelocities)+4u) {
        unsigned i=(address-D(PlayerHorizontalVelocities))/2;world.players[i].horizontal_velocity=value;observe(HW_PLAYER_HORIZONTAL,i,value);return;
    }
    if(address>=D(PlayerVerticalVelocities) && address<D(PlayerVerticalVelocities)+4u) {
        unsigned i=(address-D(PlayerVerticalVelocities))/2;world.players[i].vertical_velocity=value;observe(HW_PLAYER_VERTICAL,i,value);return;
    }
    if(address>=D(PlayerPlatformIndices) && address<D(PlayerPlatformIndices)+4u) {
        unsigned i=(address-D(PlayerPlatformIndices))/2;world.players[i].platform=value;observe(HW_PLAYER_PLATFORM,i,value);return;
    }
    CHECK(0,"complete declared write footprint");
}
int ugh_dispatch(uint16_t segment,uint16_t target,Regs *r) {
    if(dispatcher_mode) { CHECK(visit_count<5,"dispatcher capacity");visits[visit_count++]=r->bx;return 0; }
    if(segment==UGH_S_C_PlayAdlibEffect && target==UGH_O_C_PlayAdlibEffect) {
        uint16_t sound=hz_read(1,(uint16_t)(r->sp+6));
        observed.audio=sound==UGH_S_B325B_ext_325B?HA_WARNING:sound==UGH_S_B3260_ext_3260?HA_FLIGHT:sound==UGH_S_B3265_ext_3265?HA_DINO:HA_REWARD;
        r->ax=0;return 0;
    }
    if(segment==UGH_S_C_StopAdlibTrackChannel && target==UGH_O_C_StopAdlibTrackChannel) { observed.audio=HA_STOP;observed.audio_handle=hz_read(1,(uint16_t)(r->sp+4));return 0; }
    if(near_context && target==G(FindThrownStoneHittingEnemy)) {
#ifdef CONTACT_CONTRACT
        CHECK(!stone_query,"at most one outstanding stone query");stone_query=1;queried_stone_position=slot.position;
        for(size_t i=0;i<world.stone_count;i++) queried_stones[i]=world.stones[i].contact;
        r->di=selected_stone<0?65535u:(uint16_t)(selected_stone*2);logic(r,r->di,16);return 0;
#else
        return reference_FindThrownStoneHittingEnemy(r);
#endif
    }
    if(near_context && target==G(FindPlayerTouchingEnemy)) {
#ifdef CONTACT_CONTRACT
        CHECK(!player_query,"at most one outstanding player query");player_query=1;queried_player_position=slot.position;queried_geometry=type.geometry;queried_count=world.player_count;
        for(unsigned i=0;i<2;i++) queried_players[i]=world.players[i].position;
        r->di=selected_player<0?65535u:(uint16_t)(selected_player*2);logic(r,r->di,16);return 0;
#else
        return reference_FindPlayerTouchingEnemy(r);
#endif
    }
    if(near_context && target==G(StopBirdFlightSound)) { observed.audio=HA_STOP;observed.audio_handle=slot.flight_sound;return 0; }
    if(near_context && target==G(SpawnFallingItem)) {
        observed.spawn_item=1;observed.spawn_reward=slot.reward_cursor;observed.launch=(ObjectPosition){r->ax,r->bp};
        observed.launch_horizontal=r->cx;observed.launch_term=r->dx;return 0;
    }
    observed.has_tail=1;reference_tail=target;return 0;
}
int ugh_call_near(uint16_t target,uint16_t ret,Regs *r) {
    r->sp=(uint16_t)(r->sp-2);hz_write(1,r->sp,ret);
    near_context=1;int status=ugh_dispatch(r->cs,target,r);near_context=0;
    r->sp=(uint16_t)(r->sp+2);return status;
}
static void compare(void) {
    HazardSlot native_slot=slot;HazardWorld native_world=world;
    observed=(HazardResult){0};
    reference_state=code(slot.state);
    Regs incoming={0};incoming.ds=0;incoming.ss=1;incoming.cs=GAME_SEG;
    incoming.sp=36756u;incoming.si=DESCRIPTOR;incoming.di=0;
    CHECK(reference_step(operation,&incoming)==0,"reference completes one step");
    HazardResult result=hazard_step(operation,&native_slot,&type,&native_world,0);
#ifdef CONTACT_CONTRACT
    CHECK(!stone_query && !player_query,"native consumes the same contact query sequence");
#endif
    CHECK(result.count==observed.count,"same number of semantic stores");
#ifndef SEMANTIC_ONLY
    for(size_t i=0;i<observed.count;i++) {
        CHECK(result.writes[i].field==observed.writes[i].field,"same write owner and order");
        CHECK(result.writes[i].index==observed.writes[i].index,"same selected slot");
        CHECK((result.writes[i].field==HW_STATE?code((HazardEntry)result.writes[i].value):result.writes[i].value)==observed.writes[i].value,"same persistent value");
    }
#endif
    CHECK(result.has_tail==observed.has_tail && (!result.has_tail || code(result.tail)==reference_tail),"same transition target");
    CHECK(result.audio==observed.audio,"same audio request");
    if(result.audio==HA_STOP) CHECK(result.audio_handle==observed.audio_handle,"same opaque flight sound handle");
    CHECK(result.spawn_item==observed.spawn_item,"same item request");
    if(result.spawn_item) CHECK(result.spawn_reward==observed.spawn_reward && result.launch.x32==observed.launch.x32 && result.launch.y32==observed.launch.y32 &&
        result.launch_horizontal==observed.launch_horizontal && result.launch_term==observed.launch_term,"same native items API arguments");
    CHECK(native_slot.position.x32==slot.position.x32 && native_slot.position.y32==slot.position.y32 &&
        code(native_slot.state)==reference_state && native_slot.speed==slot.speed && native_slot.counter==slot.counter &&
        native_slot.animation_cursor==slot.animation_cursor && native_slot.animation_countdown==slot.animation_countdown &&
        native_slot.sprite==slot.sprite && native_slot.direction==slot.direction && native_slot.draw_x==slot.draw_x && native_slot.draw_y==slot.draw_y &&
        native_slot.flight_side==slot.flight_side && native_slot.reward_cursor==slot.reward_cursor,"native record agrees with ordered projection");
    CHECK(native_world.score==world.score && native_world.fade_step==world.fade_step && native_world.fade_level==world.fade_level,"shared score and fade projection");
    for(unsigned i=0;i<2;i++) CHECK(native_world.players[i].position.x32==world.players[i].position.x32 &&
        native_world.players[i].position.y32==world.players[i].position.y32 && native_world.players[i].platform==world.players[i].platform &&
        native_world.players[i].horizontal_velocity==world.players[i].horizontal_velocity &&
        native_world.players[i].vertical_velocity==world.players[i].vertical_velocity,"complete shared craft state");
    for(unsigned i=0;i<16;i++) CHECK(native_world.stones[i].contact.vertical_step==world.stones[i].contact.vertical_step &&
        native_world.stones[i].sprite==world.stones[i].sprite,"complete shared stone outputs");
#ifndef __CPROVER__
    comparisons++;
#endif
}
static void samples(void) {
    sampled_cursor=slot.animation_cursor;
    for(unsigned i=0;i<12;i++) {
        type.animations[i].first=hz_read(0,(uint16_t)(SEQUENCES+64*i));
        type.animations[i].next=hz_read(0,(uint16_t)(SEQUENCES+64*i+slot.animation_cursor+2u));
        ASSUME(type.animations[i].first!=65535u);
    }
    type.flight.first=hz_read(0,FLIGHT);type.flight.next=hz_read(0,(uint16_t)(FLIGHT+slot.animation_cursor+2u));
    ASSUME(type.flight.first!=65535u);
}
static void compare_dispatch(unsigned count) {
    dispatcher_mode=1;dispatcher_count=count;visit_count=0;
    Regs incoming={0};incoming.ds=0;incoming.ss=1;incoming.cs=GAME_SEG;incoming.sp=36756u;
    CHECK(reference_DispatchEnemyStates(&incoming)==0,"dispatcher completes");
    size_t cursor=0;
    for(unsigned i=0;i<count;i++) CHECK(hazards_next(count,&cursor)==visits[i]/2,"same ascending handler order");
    CHECK(visit_count==count && hazards_next(count,&cursor)==-1 && incoming.bx==2*count,"descriptor sentinel and termination");
    dispatcher_mode=0;
}
#ifdef __CPROVER__
int main(void) {
#ifdef DISPATCH_PROOF
    unsigned count;ASSUME(count<=5);compare_dispatch(count);return 0;
#else
    HazardSlot any_slot;HazardWorld any_world;HazardType any_type;
    HazardResources any_resources;LevelPlatform any_platforms[10];
    slot=any_slot;world=any_world;type=any_type;
    resource_store=any_resources;
    for(unsigned i=0;i<10;i++) platforms[i]=any_platforms[i];
    operation=OPERATION;
    ASSUME(slot.state>=H_ZERO && slot.state<=H_TREE_EMPTY);
    if(operation==H_BIRD_LAUNCH) ASSUME(slot.direction==0 || slot.direction==1);
    if(operation==H_TRIO_PATROL || operation==H_TRIO_ALERT || operation==H_TRIO_CHARGE || operation==H_TRIO_RECOVER ||
       operation==H_TRIO_IMPACT || operation==H_TRIO_STUNNED) ASSUME(slot.direction==0 || slot.direction==2);
    ASSUME(world.player_count<=2);ASSUME(world.player_slots==1 || world.player_slots==2);
    world.stone_count=STONES;world.platforms=platforms;world.platform_count=10;
#ifdef CONTACT_CONTRACT
    int any_stone,any_player;selected_stone=any_stone;selected_player=any_player;
    ASSUME(selected_stone>=-1 && selected_stone<STONES);
    ASSUME(selected_player>=-1 && selected_player<(world.player_count==2?2:1));
#endif
    ASSUME(slot.platform<10);
#ifndef WIDE_CURSOR
    ASSUME(slot.animation_cursor==65534u || (slot.animation_cursor<=30u && !(slot.animation_cursor&1u)));
#endif
    /* Any word cursor, including odd and wrapped values. Immutable sampled
     * operands cannot overlap the mutable output footprint. The read function
     * preserves collisions between sampled addresses instead of assuming all
     * samples independent. Descriptor operands remain stable and may alias. */
    for(unsigned i=0;i<13;i++) {
        uint16_t base=i==12?FLIGHT:(uint16_t)(SEQUENCES+64*i);
        uint16_t address=(uint16_t)(base+slot.animation_cursor+2u);
        ASSUME(address<D(ScoreLowWord) || address>D(FallingItemDescriptors)+144u);
    }
    for(unsigned i=0;i<13;i++) ASSUME(type.handlers[i]>=H_ZERO && type.handlers[i]<=H_TREE_EMPTY);
    list_word=operation==H_TREE_RELEASE || operation==H_TREE_COOLDOWN?REWARDS:FLIGHT;
    if(operation==H_TREE_RELEASE) ASSUME(!type.rewards_exhausted);
    samples();compare();return 0;
#endif
}
#else
static uint32_t random_state=2654435769u;
static uint16_t random_word(void) { random_state^=random_state<<13;random_state^=random_state>>17;random_state^=random_state<<5;return (uint16_t)random_state; }
int main(void) {
    for(unsigned i=0;i<13;i++) { resource_store.first[i]=(uint16_t)(i+100);resource_store.next[i]=(uint16_t)(i+200); }
    for(unsigned entry=H_BIRD_DELAY;entry<=H_TREE_EMPTY;entry++) {
        operation=(HazardEntry)entry;
        for(unsigned n=0;n<1000;n++) {
            slot=(HazardSlot){0};world=(HazardWorld){0};type=(HazardType){0};
            slot.position=(ObjectPosition){random_word(),random_word()};slot.speed=random_word();slot.counter=random_word();
            slot.animation_countdown=n%3?random_word():1;slot.animation_cursor=n%5?0:65534u;
            slot.direction=operation==H_BIRD_LAUNCH?n%2:(uint16_t)(2*(n%2));slot.initial_delay=random_word();
            slot.draw_x=random_word();slot.draw_y=random_word();slot.sprite=random_word();
            world.player_count=(uint16_t)(n%3);world.player_slots=(uint16_t)(1+n%2);
            world.stone_count=n%4;world.platforms=platforms;world.platform_count=10;
            world.score=((uint32_t)random_word()<<16)|random_word();world.fade_step=random_word();world.fade_level=random_word();world.water_y32=random_word();
            for(unsigned i=0;i<2;i++) {
                world.players[i].position=n%3?slot.position:(ObjectPosition){random_word(),random_word()};
                world.players[i].platform=n%2?slot.platform:65535u;world.players[i].horizontal_velocity=random_word();
            }
            for(unsigned i=0;i<16;i++) {
                world.stones[i].contact.position=n%2?slot.position:(ObjectPosition){random_word(),random_word()};
                world.stones[i].contact.vertical_step=random_word();world.stones[i].horizontal_step=random_word();world.stones[i].contact.thrown_stone=n%3==0;
            }
            for(unsigned i=0;i<13;i++) type.handlers[i]=(HazardEntry)i;
            type.geometry=(ObjectGeometry){random_word(),random_word(),random_word(),random_word()};type.score=random_word();
            list_word=operation==H_TREE_RELEASE || operation==H_TREE_COOLDOWN?REWARDS:FLIGHT;
            samples();compare();
        }
    }
    const HazardEntry timers[5]={H_BIRD_WAIT,H_BIRD_WARN_WAIT,H_DINO_STUNNED,H_TREE_COOLDOWN,H_TRIO_STUNNED};
    for(unsigned kind=0;kind<5;kind++) for(unsigned value=0;value<65536u;value++) {
        operation=timers[kind];slot=(HazardSlot){0};world=(HazardWorld){0};type=(HazardType){0};
        slot.counter=(uint16_t)value;slot.animation_countdown=1;slot.animation_cursor=65534u;
        for(unsigned i=0;i<13;i++) type.handlers[i]=(HazardEntry)i;
        list_word=operation==H_TREE_COOLDOWN?REWARDS:FLIGHT;
        type.rewards_exhausted=(int)(value&1u);samples();compare();
    }
    for(unsigned kind=0;kind<3;kind++) for(unsigned value=0;value<65536u;value++) {
        operation=kind==0?H_BIRD_STUN:kind==1?H_TRIO_STUN:H_DINO_STUN;
        slot=(HazardSlot){0};world=(HazardWorld){0};type=(HazardType){0};
        world.score=4294901760u|value;type.score=kind==0?2500:kind==1?1400:800;
        for(unsigned i=0;i<13;i++) type.handlers[i]=(HazardEntry)i;
        list_word=FLIGHT;samples();compare();
    }
    /* Complete animation-phase word domain with both craft inside the force
     * rectangle, including the signed 8000 boundary. Random geometry alone
     * missed this force path in the first seeded-defect experiment. */
    for(unsigned value=0;value<65536u;value++) {
        operation=H_DINO_FORCE;slot=(HazardSlot){0};world=(HazardWorld){0};type=(HazardType){0};
        slot.animation_cursor=(uint16_t)value;slot.animation_countdown=2;
        world.player_count=2;type.geometry=(ObjectGeometry){104,30,0,0};
        for(unsigned i=0;i<13;i++) type.handlers[i]=(HazardEntry)i;
        list_word=FLIGHT;samples();compare();
    }
    for(unsigned count=0;count<=5;count++) compare_dispatch(count);
    printf("PASS %lu generated actual-C transitions\n",comparisons);return 0;
}
#endif
