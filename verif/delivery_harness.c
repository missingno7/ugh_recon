/* Actual maintained C on ordinary disjoint RAM/resources/stack. The selected
 * actor is any physical slot. All other-actor accesses fail the footprint.
 * Contacts and all twelve item slots use their real C implementations. */
#ifdef __CPROVER__
void __CPROVER_assert(_Bool,const char *);void __CPROVER_assume(_Bool);
#define CHECK(c,m) __CPROVER_assert((c),(m))
#else
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(c,m) do {if(!(c)) {fprintf(stderr,"%s line %d op=%u case=%llu\n",m,__LINE__,operation,comparisons);exit(23);}} while(0)
#endif
typedef struct DeliveryRam {
    uint16_t actor[24],types[2][37],players[8][2],platforms[4][10],animation[4][3];
    uint16_t item[7][12],item_type[10];
    uint16_t player_count,player_bytes,water,multiplier,limit,difficulty,score_low,score_high,hud;
} DeliveryRam;
typedef struct DeliveryStore {uint16_t bank,address,value;int byte;} DeliveryStore;
static DeliveryRam ram;static DeliveryStore stores[64];static unsigned store_count,sound_count,spawn_count;
static unsigned expected_store_count;
static uint16_t stack_words[8],actor_index,land_base;static unsigned operation,delivery_depth;
static int modern_calls;
#ifndef __CPROVER__
static unsigned long long comparisons;
#endif
static const uint16_t player_bases[8]={D(PlayerX32),D(PlayerY32),D(PlayerPixelX),D(PlayerPlatformIndices),D(PlayerCarriedKinds),D(PlayerDestinationIcons),D(PlayerPassengerFares),D(PlayerMinimumFares)};
static const uint16_t platform_bases[4]={D(PlatformHeights),D(PlatformWaitingPointsX),D(PlatformDestinationIcons),D(PlatformActorOccupants)};
static const uint16_t item_bases[7]={D(FallingItemDescriptors),D(FallingItemCallbacks),D(FallingItemSprites),D(FallingItemX),D(FallingItemY),D(FallingItemVerticalStep),D(FallingItemMotionOrLifetime)};
static const uint16_t vector_bases[4]={0x0e20,0x0e2a,0x0e32,0x0e46};
uint16_t dl_read(uint16_t bank,uint16_t address) {
    if(bank==1) {CHECK(address>=36848u && address<36864u && !(address&1u),"stack read footprint");return stack_words[(address-36848u)/2u];}
    CHECK(bank==DATA_SEG,"ordinary data bank");
    if(address>=D(ActorDescriptors) && address<D(ActorDescriptors)+768u) {
        unsigned delta=address-D(ActorDescriptors);CHECK(delta%32u==actor_index,"only selected actor read");return ram.actor[delta/32u];
    }
    if(address>=land_base && address<land_base+148u) {unsigned delta=address-land_base;CHECK(!(delta&1u),"aligned type");return ram.types[delta/74u][(delta%74u)/2u];}
    for(unsigned i=0;i<8;i++) if(address>=player_bases[i] && address<player_bases[i]+4u) {CHECK(!((address-player_bases[i])&1u),"aligned craft");return ram.players[i][(address-player_bases[i])/2u];}
    for(unsigned i=0;i<4;i++) if(address>=platform_bases[i] && address<platform_bases[i]+20u) {CHECK(!((address-platform_bases[i])&1u),"aligned platform");return ram.platforms[i][(address-platform_bases[i])/2u];}
    for(unsigned i=0;i<4;i++) if(address>=vector_bases[i] && address<vector_bases[i]+6u) {CHECK(!((address-vector_bases[i])&1u),"aligned animation");return ram.animation[i][(address-vector_bases[i])/2u];}
    for(unsigned i=0;i<7;i++) if(address>=item_bases[i] && address<item_bases[i]+24u) {CHECK(!((address-item_bases[i])&1u),"aligned item");return ram.item[i][(address-item_bases[i])/2u];}
    if(address>=D(FallingDescriptor_7A38) && address<D(FallingDescriptor_7A38)+20u) {CHECK(!((address-D(FallingDescriptor_7A38))&1u),"aligned item descriptor");return ram.item_type[(address-D(FallingDescriptor_7A38))/2u];}
    if(address==D(PlayerCount)) return ram.player_count;
    if(address==D(PlayerArrayBytes)) return ram.player_bytes;
    if(address==D(WaterYPixels)) return ram.water;
    if(address==D(ScoreMultiplier)) return ram.multiplier;
    if(address==D(SelectedDifficulty)) return ram.difficulty;
    if(address==(uint16_t)(D(MultiplierLimitsByDifficulty)+2u*ram.difficulty)) return ram.limit;
    if(address==D(ScoreLowWord)) return ram.score_low;
    if(address==D(ScoreHighWord)) return ram.score_high;
    if(address==D(HudFareClearPending)) return ram.hud;
    CHECK(0,"read in declared footprint");return 0;
}
static void record(uint16_t bank,uint16_t address,uint16_t value,int byte) {
    CHECK(store_count<64,"finite stores");
    if(modern_calls) {
        CHECK(store_count<expected_store_count,"no extra native store");
        DeliveryStore expected=stores[store_count];
        CHECK(expected.bank==bank && expected.address==address && expected.value==value && expected.byte==byte,"ordered passenger/global/stack stores");
    } else stores[store_count]=(DeliveryStore){bank,address,value,byte};
    store_count++;
}
void dl_write(uint16_t bank,uint16_t address,uint16_t value) {
    /* Item internals are a separately closed API. Observe all slot words and
     * calls, while recording only this caller's own stores and stack order. */
    if(!(bank==DATA_SEG && address>=D(FallingItemDescriptors) && address<D(FallingItemVerticalStep)+24u)) record(bank,address,value,0);
    if(bank==1) {CHECK(address>=36848u && address<36864u && !(address&1u),"stack write footprint");stack_words[(address-36848u)/2u]=value;return;}
    CHECK(bank==DATA_SEG,"ordinary write bank");
    if(address>=D(ActorDescriptors) && address<D(ActorDescriptors)+768u) {
        unsigned delta=address-D(ActorDescriptors);CHECK(delta%32u==actor_index,"only selected actor write");ram.actor[delta/32u]=value;return;
    }
    for(unsigned i=4;i<8;i++) if(address>=player_bases[i] && address<player_bases[i]+4u) {CHECK(!((address-player_bases[i])&1u),"aligned craft write");ram.players[i][(address-player_bases[i])/2u]=value;return;}
    if(address>=D(PlatformActorOccupants) && address<D(PlatformActorOccupants)+20u) {CHECK(!((address-D(PlatformActorOccupants))&1u),"aligned occupant write");ram.platforms[3][(address-D(PlatformActorOccupants))/2u]=value;return;}
    for(unsigned i=0;i<7;i++) if(address>=item_bases[i] && address<item_bases[i]+24u) {CHECK(!((address-item_bases[i])&1u),"aligned item write");ram.item[i][(address-item_bases[i])/2u]=value;return;}
    if(address==D(ScoreLowWord)) {ram.score_low=value;return;}if(address==D(ScoreHighWord)) {ram.score_high=value;return;}
    CHECK(0,"write in declared effects");
}
uint8_t dl_byte(uint16_t bank,uint16_t address) {CHECK(address==D(HudFareClearPending),"only HUD byte read");return (uint8_t)dl_read(bank,address);}
void dl_byte_write(uint16_t bank,uint16_t address,uint8_t value) {
    CHECK(bank==DATA_SEG && address==D(HudFareClearPending),"only HUD byte write");record(bank,address,value,1);ram.hud=(uint16_t)((ram.hud&65280u)|value);
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r) {
#if defined(__CPROVER__) && MODE!=10 && MODE!=11
    CHECK(bank==GAME_SEG,"this entry has only near calls");
#else
    if(bank==UGH_S_C_PlayAdlibEffect && target==UGH_O_C_PlayAdlibEffect) {
        sound_count++;CHECK(spawn_count==1,"sound follows successful item request");
        CHECK(dl_read(r->ss,(uint16_t)(r->sp+4))==UGH_O_B3274_ext_3274 && dl_read(r->ss,(uint16_t)(r->sp+6))==UGH_S_B3274_ext_3274,"actual bonus sound resource and far stack");return UGH_OK;
    }
    CHECK(bank==GAME_SEG,"near bank");
#endif
#ifdef __CPROVER__
    /* Assert each real entry's COMPLETE target set. These are properties,
     * never assumptions. Avoid symex recursively exploring unrelated entries
     * before it has simplified the symbolic descriptor read. */
#if MODE==1 || MODE==3 || MODE==5 || MODE==7
    if(target==G(FindPlayerTouchingActor)) return modern_calls?c_FindPlayerTouchingActor(r):l1_FindPlayerTouchingActor(r);
    if(target==G(BeginPassengerResurfacing)) return l1_BeginPassengerResurfacing(r);
#if MODE==1 || MODE==5
    if(target==G(BeginPassengerDestinationDisplay)) return modern_calls?c_BeginPassengerDestinationDisplay(r):l1_BeginPassengerDestinationDisplay(r);
#endif
#if MODE==3 || MODE==7
    if(target==G(BeginPassengerQuestionDisplay)) return modern_calls?c_BeginPassengerQuestionDisplay(r):l1_BeginPassengerQuestionDisplay(r);
#endif
#if MODE==3
    if(target==G(BeginPassengerApproach)) return modern_calls?c_BeginPassengerApproach(r):l1_BeginPassengerApproach(r);
#elif MODE==5
    if(target==G(BeginPassengerPlatformWait)) return modern_calls?c_BeginPassengerPlatformWait(r):l1_BeginPassengerPlatformWait(r);
#elif MODE==7
    if(target==G(BoardPassenger)) return modern_calls?c_BoardPassenger(r):l1_BoardPassenger(r);
#endif
#elif MODE==10 || MODE==11
    if(target==G(SpawnFallingItem)) {spawn_count++;return modern_calls?c_SpawnFallingItem(r):l1_SpawnFallingItem(r);}
#if MODE==10
    if(!delivery_depth && target==G(DeliverPassenger)) {
        delivery_depth++;int status=modern_calls?c_DeliverPassenger(r):l1_DeliverPassenger(r);delivery_depth--;return status;
    }
#endif
#else
    (void)target;(void)r;
#endif
#else
    if(target==G(FindPlayerTouchingActor)) return modern_calls?c_FindPlayerTouchingActor(r):l1_FindPlayerTouchingActor(r);
    if(target==G(SpawnFallingItem)) {spawn_count++;return modern_calls?c_SpawnFallingItem(r):l1_SpawnFallingItem(r);}
    if(target==G(BeginPassengerResurfacing)) return l1_BeginPassengerResurfacing(r); /* unit six stays L1 */
    if(target==G(BeginPassengerPlatformWait)) return modern_calls?c_BeginPassengerPlatformWait(r):l1_BeginPassengerPlatformWait(r);
    if(target==G(BeginPassengerDestinationDisplay)) return modern_calls?c_BeginPassengerDestinationDisplay(r):l1_BeginPassengerDestinationDisplay(r);
    if(target==G(BeginPassengerQuestionDisplay)) return modern_calls?c_BeginPassengerQuestionDisplay(r):l1_BeginPassengerQuestionDisplay(r);
    if(target==G(BeginPassengerApproach)) return modern_calls?c_BeginPassengerApproach(r):l1_BeginPassengerApproach(r);
    if(target==G(BoardPassenger)) return modern_calls?c_BoardPassenger(r):l1_BoardPassenger(r);
    if(target==G(DeliverPassenger)) {
        if(delivery_depth) {CHECK(0,"no recursive delivery");return UGH_BAD_CALLBACK;}
        delivery_depth++;int status=modern_calls?c_DeliverPassenger(r):l1_DeliverPassenger(r);delivery_depth--;return status;
    }
#endif
    CHECK(0,"closed target set");return UGH_BAD_CALLBACK;
}
int ugh_call_near(uint16_t target,uint16_t return_ip,Regs *r) {
    r->sp=(uint16_t)(r->sp-2);dl_write(r->ss,r->sp,return_ip);
    int status=ugh_dispatch(r->cs,target,r);if(!status) r->sp=(uint16_t)(r->sp+2);return status;
}
static int execute(unsigned mode,Regs *r,int modern) {
    modern_calls=modern;delivery_depth=mode==11;
    switch(mode) {
    case 0:return modern?c_BeginPassengerPlatformWait(r):l1_BeginPassengerPlatformWait(r);
    case 1:return modern?c_UpdatePassengerPlatformWait(r):l1_UpdatePassengerPlatformWait(r);
    case 2:return modern?c_BeginPassengerDestinationDisplay(r):l1_BeginPassengerDestinationDisplay(r);
    case 3:return modern?c_UpdatePassengerDestinationDisplay(r):l1_UpdatePassengerDestinationDisplay(r);
    case 4:return modern?c_BeginPassengerQuestionDisplay(r):l1_BeginPassengerQuestionDisplay(r);
    case 5:return modern?c_UpdatePassengerQuestionDisplay(r):l1_UpdatePassengerQuestionDisplay(r);
    case 6:return modern?c_BeginPassengerApproach(r):l1_BeginPassengerApproach(r);
    case 7:return modern?c_UpdatePassengerApproach(r):l1_UpdatePassengerApproach(r);
    case 8:return modern?c_BoardWaterbornePassenger(r):l1_BoardWaterbornePassenger(r);
    case 9:return modern?c_BoardPassenger(r):l1_BoardPassenger(r);
    case 10:return modern?c_UpdateCarriedPassenger(r):l1_UpdateCarriedPassenger(r);
    default:return modern?c_DeliverPassenger(r):l1_DeliverPassenger(r);
    }
}
static void configure(void) {
    const uint16_t targets[]={G(BeginPassengerPlatformWait),G(UpdatePassengerPlatformWait),G(BeginPassengerDestinationDisplay),G(UpdatePassengerDestinationDisplay),
        G(BeginPassengerQuestionDisplay),G(UpdatePassengerQuestionDisplay),G(BeginPassengerApproach),G(UpdatePassengerApproach),G(BoardPassenger),G(UpdateCarriedPassenger),G(DeliverPassenger),G(WalkPassengerToExit)};
    for(unsigned i=0;i<12;i++) ram.types[0][8+i]=targets[i];
    ram.types[0][36]=(uint16_t)(land_base+74u);ram.types[1][36]=land_base;
    ram.types[1][4]=G(BeginPassengerResurfacing);ram.types[1][5]=G(UpdatePassengerResurfacing);
    ram.types[1][11]=G(UpdateFloatingDestinationDisplay);ram.types[1][13]=G(UpdateFloatingQuestionDisplay);ram.types[1][15]=G(UpdateFloatingPassengerApproach);
    for(unsigned i=0;i<4;i++) {ram.types[0][23+i]=vector_bases[i];ram.types[1][23+i]=vector_bases[i];ram.animation[i][2]=65535u;}
    ram.item_type[2]=G(SpawnFallingItem);ram.item_type[3]=G(AdvanceFallingItem);ram.item_type[4]=G(LandFallingItem);ram.item_type[5]=G(ExpireOrCollectFallingItem);
}
static void compare(unsigned mode,Regs incoming) {
    operation=mode;DeliveryRam initial=ram;Regs reference=incoming,bridge=incoming;
    store_count=sound_count=spawn_count=native_item_calls=0;int expected_status=execute(mode,&reference,0);DeliveryRam expected=ram;
    unsigned expected_count=store_count,expected_sound=sound_count,expected_spawn=spawn_count;expected_store_count=expected_count;
    ram=initial;store_count=sound_count=spawn_count=dl_fallback=native_item_calls=0;int actual_status=execute(mode,&bridge,1);
    CHECK(dl_fallback==0,"admitted passenger path has no L1 fallback");
    CHECK(expected_status==actual_status || (expected_status==UGH_BAD_CALLBACK && actual_status==UGH_CONTROL_TRANSFER),"same ordinary completion or exact item abnormal-transfer refinement");
    for(unsigned i=0;i<24;i++) CHECK(expected.actor[i]==ram.actor[i],"all actor state/history words");
    for(unsigned i=0;i<8;i++) for(unsigned j=0;j<2;j++) CHECK(expected.players[i][j]==ram.players[i][j],"both craft records");
    for(unsigned i=0;i<4;i++) for(unsigned j=0;j<10;j++) CHECK(expected.platforms[i][j]==ram.platforms[i][j],"all platform words and occupancy");
    for(unsigned i=0;i<7;i++) for(unsigned j=0;j<12;j++) CHECK(expected.item[i][j]==ram.item[i][j],"actual twelve-slot item allocation");
    CHECK(expected.score_low==ram.score_low && expected.score_high==ram.score_high && expected.hud==ram.hud,"score and HUD high byte");
    CHECK(expected_count==store_count && expected_sound==sound_count && expected_spawn==spawn_count,"same stores, item and audio calls");
    CHECK(native_item_calls==spawn_count,"every allocation request calls actual native items_spawn");
    CHECK(reference.ax==bridge.ax && reference.bx==bridge.bx && reference.cx==bridge.cx && reference.dx==bridge.dx && reference.si==bridge.si && reference.di==bridge.di && reference.bp==bridge.bp,"full working registers");
    CHECK(reference.cs==bridge.cs && reference.ds==bridge.ds && reference.es==bridge.es && reference.ss==bridge.ss && reference.sp==bridge.sp && reference.ip==bridge.ip && reference.flags==bridge.flags,"full flags/continuation, including item full pool");
    if(actual_status==UGH_CONTROL_TRANSFER) CHECK(!sound_count && ram.actor[11]==initial.actor[11] && ram.hud==initial.hud && ram.actor[16]==initial.actor[16] && ram.actor[17]==initial.actor[17],"full pool prevents all post-service delivery stores");
#ifndef __CPROVER__
    comparisons++;
#endif
}
#ifdef __CPROVER__
int main(void) {
    DeliveryRam arbitrary;ram=arbitrary;Regs incoming;uint16_t physical;
    __CPROVER_assume(physical<16);actor_index=(uint16_t)(2u*physical);land_base=D(Data_7720);
    _Bool water_type;
    ram.actor[0]=MODE==8 || ((MODE==2 || MODE==4 || MODE==6) && water_type)?(uint16_t)(land_base+74):land_base;
    __CPROVER_assume(ram.player_count==1 || ram.player_count==2);ram.player_bytes=ram.player_count==2?4:2;ram.difficulty=0;
#if MODE==1 || MODE==3 || MODE==5 || MODE==7 || MODE==8 || MODE==9
    __CPROVER_assume(ram.actor[5]<10);ram.actor[7]=(uint16_t)(2u*ram.actor[5]);
#endif
#if MODE==7 || MODE==8 || MODE==9 || MODE==10 || MODE==11
    __CPROVER_assume(ram.actor[6]<10);ram.actor[8]=(uint16_t)(2u*ram.actor[6]);
#endif
#if MODE==10 || MODE==11
    __CPROVER_assume(ram.actor[4]==0 || (ram.actor[4]==2 && ram.player_count==2));
#endif
    for(unsigned i=0;i<4;i++) for(unsigned j=0;j<2;j++) __CPROVER_assume(ram.animation[i][j]!=65535u);
#if MODE==1 || MODE==3 || MODE==5 || MODE==7
    if(ram.actor[17]==1) __CPROVER_assume(ram.actor[16]==65534u || ram.actor[16]==0 || ram.actor[16]==2);
#if MODE==7
    else __CPROVER_assume(ram.actor[16]==0 || ram.actor[16]==2 || ram.actor[16]==4);
#endif
#endif
    configure();incoming.ds=DATA_SEG;incoming.cs=GAME_SEG;incoming.ss=1;incoming.sp=36864u;incoming.bx=actor_index;
#if MODE==8 || MODE==9 || MODE==11
    __CPROVER_assume(incoming.di==0 || (incoming.di==2 && ram.player_count==2));
#endif
    compare(MODE,incoming);return 0;
}
#else
static uint32_t rng=2654435769u;
static uint16_t word(void) {rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return (uint16_t)rng;}
static Regs seed(void) {
    ram=(DeliveryRam){0};land_base=D(Data_7720);actor_index=0;ram.actor[0]=land_base;
    ram.actor[5]=0;ram.actor[6]=1;ram.actor[7]=0;ram.actor[8]=2;ram.actor[9]=0;
    ram.actor[10]=3200;ram.actor[11]=3200;ram.actor[12]=100;ram.actor[14]=100;ram.actor[16]=0;ram.actor[17]=1;ram.actor[23]=200;
    ram.player_count=2;ram.player_bytes=4;ram.water=192;ram.multiplier=1;ram.limit=9;ram.hud=0xa500;
    for(unsigned t=0;t<2;t++) {ram.types[t][0]=8;ram.types[t][1]=16;ram.types[t][2]=8;ram.types[t][3]=16;ram.types[t][31]=7;ram.types[t][32]=(uint16_t)(300+400*t);ram.types[t][33]=(uint16_t)(100+100*t);ram.types[t][35]=1;}
    for(unsigned i=0;i<2;i++) {ram.players[0][i]=6000;ram.players[1][i]=100;ram.players[2][i]=92;ram.players[3][i]=0;ram.players[6][i]=300;ram.players[7][i]=100;}
    for(unsigned i=0;i<10;i++) {ram.platforms[0][i]=100;ram.platforms[1][i]=108;ram.platforms[2][i]=(uint16_t)i;ram.platforms[3][i]=0;}
    for(unsigned i=0;i<4;i++) {ram.animation[i][0]=(uint16_t)(100+i);ram.animation[i][1]=(uint16_t)(200+i);}
    ram.item_type[0]=8;ram.item_type[1]=16;ram.item_type[6]=57;ram.item_type[7]=1;ram.item_type[8]=297;ram.item_type[9]=2;
    for(unsigned i=0;i<12;i++) ram.item[2][i]=65535u;
    configure();Regs r={0};r.ds=DATA_SEG;r.cs=GAME_SEG;r.ss=1;r.sp=36864u;r.flags=0xad5;return r;
}
int main(void) {
    Regs r;
    for(unsigned value=0;value<65536u;value++) {
        r=seed();ram.actor[6]=(uint16_t)value;compare(2,r);
        r=seed();ram.actor[4]=(uint16_t)value;compare(3,r);
        r=seed();ram.actor[4]=(uint16_t)value;compare(5,r);
        r=seed();ram.players[6][0]=(uint16_t)value;ram.players[3][0]=65535u;compare(10,r);
        r=seed();ram.actor[23]=(uint16_t)value;ram.players[3][0]=65535u;compare(10,r);
        r=seed();ram.actor[12]=(uint16_t)value;compare(7,r);
        r=seed();ram.players[6][0]=(uint16_t)value;ram.multiplier=65535u;ram.limit=0;compare(11,r);
    }
    /* Complete unsigned fare/floor boundary pairs on both sides of 8000. */
    static const uint16_t edges[]={0,1,139,140,141,199,200,32767,32768,65534,65535};
    for(unsigned a=0;a<11;a++) for(unsigned b=0;b<11;b++) {
        r=seed();ram.players[6][0]=edges[a];ram.players[7][0]=edges[b];ram.players[3][0]=65535u;compare(10,r);
        r=seed();ram.actor[23]=edges[a];ram.multiplier=edges[b];ram.limit=65535u;compare(11,r);
    }
    for(unsigned type=0;type<3;type++) for(unsigned carrier=0;carrier<2;carrier++) {
        r=seed();land_base=(uint16_t)(D(Data_7720)+148u*type);ram.actor[0]=(uint16_t)(land_base+74u);ram.types[1][35]=4;configure();r.di=(uint16_t)(2u*carrier);compare(8,r);
        CHECK(ram.players[6][carrier]==700 && ram.players[7][carrier]==200 && ram.actor[0]==land_base,"rescue uses water fare before land pair");
        CHECK(ram.players[4][carrier]==1,"rescue carried kind uses paired land descriptor");
    }
    for(unsigned type=0;type<3;type++) for(unsigned wet=0;wet<2;wet++) for(unsigned mode=2;mode<=6;mode+=2) {
        r=seed();land_base=(uint16_t)(D(Data_7720)+148u*type);ram.actor[0]=(uint16_t)(land_base+74u*wet);configure();compare(mode,r);
    }
    r=seed();for(unsigned i=0;i<12;i++) ram.item[2][i]=0;compare(11,r);
    r=seed();actor_index=30;r.bx=actor_index;for(unsigned i=0;i<12;i++) ram.item[2][i]=32767u;compare(11,r);
    r=seed();ram.actor[3]=G(UpdatePassengerDestinationDisplay);ram.actor[4]=140;ram.actor[17]=100;
    for(unsigned tick=0;tick<139;tick++) compare(3,r);
    CHECK(ram.actor[4]==1 && ram.actor[3]==G(UpdatePassengerDestinationDisplay),"request waits exactly 139 pre-expiry calls");compare(3,r);
    CHECK(ram.actor[4]==0 && ram.actor[3]==G(UpdatePassengerApproach),"request transitions on call 140");
    r=seed();ram.players[4][0]=99;compare(3,r);
    CHECK(ram.actor[3]==G(UpdatePassengerQuestionDisplay),"destination rejects first busy match rather than using later empty craft");
    r=seed();ram.players[4][0]=99;compare(1,r);
    CHECK(ram.actor[3]==G(UpdatePassengerDestinationDisplay),"waiting scan skips first busy craft to find later empty craft");
    r=seed();ram.actor[10]=0;ram.actor[17]=2;ram.players[4][0]=99;compare(7,r);
    CHECK(ram.actor[3]==G(UpdateCarriedPassenger) && ram.players[4][0]==1,"exact cached-X boards first craft even between ticks and despite busy kind");
    r=seed();DeliveryPlan pending;CHECK(delivery_prepare(&r,PD_DELIVER,&pending),"prepare native pending delivery");
    CHECK(pending.result.finish_pending && pending.slot.position.y32==ram.actor[11] && pending.slot.animation.countdown==ram.actor[17] && pending.world.hud_clear==(uint8_t)ram.hud,"native logical state defers post-service mutations");
    FallingItem full[12];memset(full,0,sizeof full);FallingItemType bonus={0};
    CHECK(items_spawn(full,bonus,pending.result.launch,0,0).status==ITEM_POOL_FULL,"actual native pool can be full");
    for(unsigned test=0;test<6000;test++) {
        r=seed();land_base=(uint16_t)(D(Data_7720)+148u*(test%3));ram.actor[0]=land_base;
        actor_index=(uint16_t)(2u*(test%16));r.bx=actor_index;
        for(unsigned i=1;i<24;i++) ram.actor[i]=word();
        ram.actor[5]=(uint16_t)(word()%10);ram.actor[6]=(uint16_t)(word()%10);ram.actor[7]=(uint16_t)(2u*ram.actor[5]);ram.actor[8]=(uint16_t)(2u*ram.actor[6]);ram.actor[4]=(uint16_t)(2u*(test%2));
        ram.actor[16]=0;ram.actor[17]=test%3==0?1:test%3==1?0:word();
        for(unsigned t=0;t<2;t++) for(unsigned i=0;i<4;i++) ram.types[t][i]=word();
        for(unsigned t=0;t<2;t++) {ram.types[t][31]=word();ram.types[t][32]=word();ram.types[t][33]=word();ram.types[t][35]=word();}
        for(unsigned i=0;i<8;i++) for(unsigned j=0;j<2;j++) ram.players[i][j]=word();
        for(unsigned i=0;i<4;i++) for(unsigned j=0;j<2;j++) ram.animation[i][j]=(uint16_t)(word()%65535u);
        for(unsigned i=0;i<4;i++) for(unsigned j=0;j<10;j++) ram.platforms[i][j]=word();
        for(unsigned i=0;i<7;i++) for(unsigned j=0;j<12;j++) ram.item[i][j]=word();
        ram.multiplier=word();ram.limit=word();ram.score_low=word();ram.score_high=word();ram.water=word();ram.hud=word();configure();
        r.di=(uint16_t)(2u*(test%2));r.ax=word();r.cx=word();r.dx=word();r.si=word();r.bp=word();r.ip=word();r.es=word();r.flags=word();
        for(unsigned mode=0;mode<12;mode++) {DeliveryRam initial=ram;if(mode==8) ram.actor[0]=(uint16_t)(land_base+74u);compare(mode,r);ram=initial;}
    }
    printf("PASS %llu comparisons: seven complete word slices, boundary pairs, rescue pairs, full pool and 6000 x twelve generated states\n",comparisons);return 0;
}
#endif
