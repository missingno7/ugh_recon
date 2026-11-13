/* Actual-C relational harness: one arbitrary physical slot, all scalar words,
 * two craft records, immutable descriptor, bounded platform list. Ordinary
 * RAM/stack are disjoint; external sound is an observing, successful callback.
 * Unrelated actor words include all renderer history and remain arbitrary. */
#ifdef __CPROVER__
void __CPROVER_assert(_Bool,const char *);
void __CPROVER_assume(_Bool);
#define CHECK(c,m) __CPROVER_assert((c),(m))
#else
#include <stdio.h>
#include <stdlib.h>
#define CHECK(c,m) do {if(!(c)) {fprintf(stderr,"%s line %d operation=%u case=%llu\n",m,__LINE__,operation,comparisons);exit(23);}} while(0)
#endif
typedef struct StoneRam {
    uint16_t actor[24],descriptor[37],players[8][2],platform[30];
    uint16_t player_count;
} StoneRam;
typedef struct StoneStore { uint16_t bank,address,value; } StoneStore;
static StoneRam ram;
static StoneStore stores[32];static unsigned store_count;
static uint16_t stack_words[8];static uint16_t actor_index;
static unsigned platform_count,operation,sound_count;
static int modern_calls;
#ifndef __CPROVER__
static unsigned long long comparisons;
#endif
static const uint16_t player_bases[8]={D(PlayerX32),D(PlayerY32),D(PlayerHorizontalVelocities),D(PlayerVerticalVelocities),
    D(PlayerCarriedKinds),D(PlayerDestinationIcons),D(PlayerActionInput),D(PlayerPlatformIndices)};
uint16_t st_read(uint16_t bank,uint16_t address) {
    if(bank==1) {
        CHECK(address>=36848u && address<36864u && !(address&1u),"stack footprint");return stack_words[(address-36848u)/2u];
    }
    CHECK(bank==DATA_SEG,"ordinary data bank");
    if(address>=D(ActorDescriptors) && address<D(ActorDescriptors)+768u) {
        unsigned delta=address-D(ActorDescriptors);CHECK(delta%32u==actor_index,"only selected actor slot");return ram.actor[delta/32u];
    }
    uint16_t descriptor=ram.actor[0];
    if(address>=descriptor && address<descriptor+74u) {CHECK(!((address-descriptor)&1u),"aligned descriptor");return ram.descriptor[(address-descriptor)/2u];}
    for(unsigned i=0;i<8;i++) if(address>=player_bases[i] && address<player_bases[i]+4u) {
        CHECK(!((address-player_bases[i])&1u),"aligned player");return ram.players[i][(address-player_bases[i])/2u];
    }
    if(address==D(PlayerCount)) return ram.player_count;
    if(address>=D(PlatformLeftEdges) && address<D(PlatformLeftEdges)+60u) {
        CHECK(!((address-D(PlatformLeftEdges))&1u),"aligned platform");return ram.platform[(address-D(PlatformLeftEdges))/2u];
    }
    CHECK(0,"read within declared RAM footprint");return 0;
}
void st_write(uint16_t bank,uint16_t address,uint16_t value) {
    CHECK(store_count<32,"finite ordered stores");stores[store_count++]=(StoneStore){bank,address,value};
    if(bank==1) {CHECK(address>=36848u && address<36864u && !(address&1u),"stack write footprint");stack_words[(address-36848u)/2u]=value;return;}
    CHECK(bank==DATA_SEG,"ordinary write bank");
    if(address>=D(ActorDescriptors) && address<D(ActorDescriptors)+768u) {
        unsigned delta=address-D(ActorDescriptors);CHECK(delta%32u==actor_index,"only selected actor write");ram.actor[delta/32u]=value;return;
    }
    for(unsigned i=4;i<6;i++) if(address>=player_bases[i] && address<player_bases[i]+4u) {
        CHECK(!((address-player_bases[i])&1u),"aligned owned craft write");ram.players[i][(address-player_bases[i])/2u]=value;return;
    }
    CHECK(0,"write within declared effects");
}
uint8_t st_byte(uint16_t bank,uint16_t address) {
    CHECK(address==D(PlayerActionInput) || address==D(PlayerActionInput)+2u,"only low action byte read");return (uint8_t)st_read(bank,address);
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r) {
    if(bank==UGH_S_C_PlayAdlibEffect && target==UGH_O_C_PlayAdlibEffect) {
        sound_count++;CHECK(st_read(r->ss,r->sp)==G(ThrowCarriedStone)+0x68,"sound return continuation");
        CHECK(st_read(r->ss,(uint16_t)(r->sp+4))==0 && st_read(r->ss,(uint16_t)(r->sp+6))==UGH_S_B3632_ext_3632,"sound resource identity");
        CHECK(ram.actor[3]==G(UpdateThrownStone) && ram.actor[18]==545,"throw published before sound");return UGH_OK;
    }
    CHECK(bank==GAME_SEG,"near dispatch bank");
#ifdef __CPROVER__
    /* Per-entry exact target assertions remove impossible recursive dispatch
     * expansion. These are checked, never assumptions about a callback. */
#if MODE==1
    if(target==G(FindPlayerTouchingActor)) return l1_FindPlayerTouchingActor(r);
    CHECK(target==G(AttachStoneToPlayer),"pickup tail target");
    return modern_calls?c_AttachStoneToPlayer(r):l1_AttachStoneToPlayer(r);
#elif MODE==3
    CHECK(target==G(ThrowCarriedStone),"release tail target");
    return modern_calls?c_ThrowCarriedStone(r):l1_ThrowCarriedStone(r);
#elif MODE==5
    CHECK(target==G(BeginStonePickupWait),"landing tail target");
    return modern_calls?c_BeginStonePickupWait(r):l1_BeginStonePickupWait(r);
#else
    CHECK(0,"no near callee in this entry");return UGH_BAD_CALLBACK;
#endif
#else
    if(target==G(FindPlayerTouchingActor)) return l1_FindPlayerTouchingActor(r);
    if(target==G(BeginStonePickupWait)) return modern_calls?c_BeginStonePickupWait(r):l1_BeginStonePickupWait(r);
    if(target==G(AttachStoneToPlayer)) return modern_calls?c_AttachStoneToPlayer(r):l1_AttachStoneToPlayer(r);
    if(target==G(ThrowCarriedStone)) return modern_calls?c_ThrowCarriedStone(r):l1_ThrowCarriedStone(r);
    CHECK(0,"closed dispatch target set");return UGH_BAD_CALLBACK;
#endif
}
int ugh_call_near(uint16_t target,uint16_t return_ip,Regs *r) {
    r->sp=(uint16_t)(r->sp-2);st_write(r->ss,r->sp,return_ip);
    int status=ugh_dispatch(r->cs,target,r);if(!status) r->sp=(uint16_t)(r->sp+2);return status;
}
static int execute(unsigned mode,Regs *r,int modern) {
    modern_calls=modern;
    switch(mode) {
    case 0:return modern?c_BeginStonePickupWait(r):l1_BeginStonePickupWait(r);
    case 1:return modern?c_UpdateStonePickupWait(r):l1_UpdateStonePickupWait(r);
    case 2:return modern?c_AttachStoneToPlayer(r):l1_AttachStoneToPlayer(r);
    case 3:return modern?c_WaitForStoneRelease(r):l1_WaitForStoneRelease(r);
    case 4:return modern?c_ThrowCarriedStone(r):l1_ThrowCarriedStone(r);
    default:return modern?c_UpdateThrownStone(r):l1_UpdateThrownStone(r);
    }
}
static void configure(void) {
    ram.descriptor[8]=G(BeginStonePickupWait);ram.descriptor[9]=G(UpdateStonePickupWait);
    ram.descriptor[16]=G(AttachStoneToPlayer);ram.descriptor[17]=G(WaitForStoneRelease);
    ram.descriptor[18]=G(ThrowCarriedStone);ram.descriptor[19]=G(UpdateThrownStone);ram.descriptor[22]=G(IgnoreActorState);
    for(unsigned i=0;i<platform_count;i++) ram.platform[i]&=32767u;
    ram.platform[platform_count]=65535u; /* at ten, aliases first right edge */
}
#ifdef STONE_SEMANTIC
/* Semantic projection check, separate from the full adapter-shell profile.
 * All algorithms are maintained native functions; this adapter only moves
 * their typed outputs back into the relational observation. */
static int semantic_execute(unsigned mode,Regs *incoming) {
    PassengerStoneSlot slot;ActorType type;StonePlayer players[2];
    ActorPhase phase=mode==0?ACTOR_BEGIN_STONE_WAIT:mode==3 || mode==4?ACTOR_CARRIED_STONE:mode==5?ACTOR_THROWN_STONE:ACTOR_STONE_WAIT;
    CHECK(stone_project(incoming,phase,&slot,&type,players),"semantic projection admits state");
    int thrown=0,attached=0,waiting=0,retired=0;
    if(mode==0) {stone_begin_wait(&slot);waiting=1;}
    else if(mode==1) {
        StoneResult result=stone_pickup_wait(&slot,players,ram.player_count);
        if(result.exit==STONE_PICKUP) {stone_attach(&slot,players,(size_t)result.contact.index);attached=1;}
    } else if(mode==2) {stone_attach(&slot,players,incoming->di/2u);attached=1;}
    else if(mode==3) {
        if(stone_release_requested(&slot,players)) {
            uint16_t carrier;CHECK(actor_alias_value(&slot,ACTOR_ALIAS_CARRIER,&carrier),"release reads valid carrier");
            stone_throw(&slot,players,carrier);thrown=1;
        }
    } else if(mode==4) {stone_throw(&slot,players,incoming->di/2u);thrown=1;}
    else {
        LevelPlatform platforms[10];
        for(unsigned i=0;i<platform_count;i++) {
            platforms[i]=(LevelPlatform){0};platforms[i].left=ram.platform[i];platforms[i].right=ram.platform[10+i];platforms[i].surface_y=ram.platform[20+i];
        }
        StoneResult result=stone_flight(&slot,platforms,platform_count);
        if(result.exit==STONE_LANDING) {stone_begin_wait(&slot);waiting=1;}
        retired=slot.phase==ACTOR_RETIRED;
    }
    ram.actor[10]=slot.position.x32;ram.actor[11]=slot.position.y32;ram.actor[18]=slot.sprite;
    ram.actor[16]=slot.animation.byte_offset;ram.actor[17]=slot.animation.countdown;ram.actor[22]=slot.vertical_motion;
    if(waiting) ram.actor[3]=G(UpdateStonePickupWait);
    if(attached) {ram.actor[3]=G(WaitForStoneRelease);ram.actor[4]=(uint16_t)(2u*slot.carrier);}
    if(thrown) {ram.actor[3]=G(UpdateThrownStone);ram.actor[9]=slot.horizontal_step;sound_count++;}
    if(retired) ram.actor[3]=G(IgnoreActorState);
    for(unsigned i=0;i<2;i++) {ram.players[4][i]=players[i].carried_kind;ram.players[5][i]=players[i].destination_icon;}
    return UGH_OK;
}
#endif
static void compare(unsigned mode,Regs incoming) {
    operation=mode;StoneRam initial=ram;Regs reference=incoming,bridge=incoming;
    store_count=sound_count=0;int expected_status=execute(mode,&reference,0);StoneRam expected=ram;
    unsigned expected_count=store_count,expected_sound=sound_count;StoneStore expected_stores[32];
    for(unsigned i=0;i<expected_count;i++) expected_stores[i]=stores[i];
    ram=initial;store_count=sound_count=st_fallback=0;
#ifdef STONE_SEMANTIC
    int actual_status=semantic_execute(mode,&bridge);
#else
    int actual_status=execute(mode,&bridge,1);
#endif
    CHECK(st_fallback==0,"admitted states execute native code without fallback");
    CHECK(expected_status==actual_status && actual_status==UGH_OK,"both actual C entries complete");
    for(unsigned i=0;i<24;i++) CHECK(expected.actor[i]==ram.actor[i],"every actor word including persistent render history");
    for(unsigned i=0;i<8;i++) for(unsigned j=0;j<2;j++) CHECK(expected.players[i][j]==ram.players[i][j],"craft state including action high byte");
    CHECK(expected_sound==sound_count,"same synchronous sound requests");
#ifndef STONE_SEMANTIC
    CHECK(expected_count==store_count,"same store count");
    for(unsigned i=0;i<expected_count;i++) {
        CHECK(expected_stores[i].bank==stores[i].bank && expected_stores[i].address==stores[i].address && expected_stores[i].value==stores[i].value,"same ordered semantic and stack stores");
    }
    CHECK(reference.ax==bridge.ax && reference.bx==bridge.bx && reference.cx==bridge.cx && reference.dx==bridge.dx && reference.si==bridge.si && reference.di==bridge.di && reference.bp==bridge.bp,"complete working register shell");
    CHECK(reference.cs==bridge.cs && reference.ds==bridge.ds && reference.es==bridge.es && reference.ss==bridge.ss && reference.sp==bridge.sp && reference.ip==bridge.ip && reference.flags==bridge.flags,"complete continuation and flags");
#endif
#ifndef __CPROVER__
    comparisons++;
#endif
}
#ifdef __CPROVER__
int main(void) {
    StoneRam arbitrary;ram=arbitrary;Regs incoming;uint16_t index;
    __CPROVER_assume(index<16);actor_index=(uint16_t)(2u*index);incoming.bx=actor_index;
    incoming.ds=DATA_SEG;incoming.cs=GAME_SEG;incoming.ss=1;incoming.sp=36864u;
    _Bool alternate;ram.actor[0]=alternate?D(Data_7926):D(Data_78DC);
#if MODE==2 || MODE==4
    __CPROVER_assume(incoming.di==0 || (incoming.di==2 && ram.player_count==2));
#endif
#if MODE==3 || MODE==4
    __CPROVER_assume(ram.actor[4]==0 || (ram.actor[4]==2 && ram.player_count==2));
#endif
    platform_count=PLATFORMS;configure();compare(MODE,incoming);return 0;
}
#else
static uint32_t rng=2654435769u;
static uint16_t word(void) {rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return (uint16_t)rng;}
static Regs seed(void) {
    ram=(StoneRam){0};actor_index=0;platform_count=0;ram.actor[0]=D(Data_78DC);
    ram.actor[10]=1000;ram.actor[11]=1000;ram.descriptor[0]=8;ram.descriptor[1]=11;ram.descriptor[2]=8;ram.descriptor[3]=8;ram.descriptor[35]=4;
    ram.players[0][0]=500;ram.players[1][0]=1000;ram.players[0][1]=500;ram.players[1][1]=1000;ram.player_count=2;
    Regs r={0};r.ds=DATA_SEG;r.cs=GAME_SEG;r.ss=1;r.sp=36864u;r.flags=0xad5;configure();return r;
}
static void view_cases(void) {
    ActorType primary={0},alternate={0};primary.id=ACTOR_STONE;alternate.id=ACTOR_STONE_ALTERNATE;
    PassengerStoneSlot slots[3]={{0}};StoneContactView views[3];
    for(unsigned i=0;i<3;i++) {slots[i].type=&primary;slots[i].phase=ACTOR_THROWN_STONE;slots[i].position=(ObjectPosition){1000,1000};}
    for(unsigned i=0;i<3;i++) views[i]=stone_contact_view(&slots[i]);
    CHECK(contact_stones(views,3,(ObjectPosition){1000,1000}).index==0,"ascending first hit");
    slots[0].type=&alternate;
    for(unsigned i=0;i<3;i++) views[i]=stone_contact_view(&slots[i]);
    CHECK(contact_stones(views,3,(ObjectPosition){1000,1000}).index==1,"alternate identity excluded");
    slots[1].vertical_motion=65534u;slots[2].phase=ACTOR_RETIRED;
    for(unsigned i=0;i<3;i++) views[i]=stone_contact_view(&slots[i]);
    CHECK(contact_stones(views,3,(ObjectPosition){1000,1000}).index==-1,"bounce and retirement immediately visible");
    uint16_t out=123;slots[0].phase=ACTOR_STONE_WAIT;slots[0].carrier=1;slots[0].horizontal_step=5;
    CHECK(!actor_alias_value(&slots[0],ACTOR_ALIAS_CARRIER,&out) && out==123,"inactive carrier rejected");
    CHECK(!actor_alias_value(&slots[0],ACTOR_ALIAS_HORIZONTAL_STEP,&out) && out==123,"inactive motion alias rejected");
}
int main(void) {
    Regs r=seed();
    for(unsigned value=0;value<65536u;value++) {
        r=seed();ram.players[6][0]=(uint16_t)value;compare(3,r); /* complete action word */
        r=seed();ram.players[2][0]=(uint16_t)value;ram.players[3][0]=(uint16_t)value;compare(4,r); /* both complete velocity axes */
        r=seed();ram.actor[10]=(uint16_t)value;compare(5,r); /* complete X retirement domain */
        r=seed();ram.actor[22]=(uint16_t)value;compare(5,r); /* gravity/sign/wrap domain */
    }
    static const uint16_t edges[]={0,1,2,31,32,511,512,6143,6144,10239,10240,32767,32768,65023,65024,65025,65534,65535};
    /* Exact old-bottom equality, both X-edge equalities and first-platform
     * competition. A zero vertical word becomes +2 before the crossing. */
    for(unsigned side=0;side<2;side++) {
        r=seed();ram.actor[10]=(uint16_t)(side*32u);ram.actor[11]=0;ram.actor[22]=0;
        platform_count=2;ram.platform[0]=8;ram.platform[1]=8;
        ram.platform[10]=9;ram.platform[11]=9;ram.platform[20]=11;ram.platform[21]=11;configure();compare(5,r);
    }
    for(unsigned a=0;a<18;a++) for(unsigned b=0;b<18;b++) {
        r=seed();ram.actor[11]=edges[a];ram.actor[22]=edges[b];ram.platform[0]=0;ram.platform[10]=319;ram.platform[20]=42;platform_count=1;configure();compare(5,r);
    }
    for(unsigned test=0;test<12000;test++) {
        r=seed();for(unsigned i=1;i<24;i++) ram.actor[i]=word();
        for(unsigned i=0;i<8;i++) for(unsigned j=0;j<2;j++) ram.players[i][j]=word();
        for(unsigned i=0;i<4;i++) ram.descriptor[i]=word();
        ram.descriptor[35]=word();
        ram.actor[0]=(test&1)?D(Data_78DC):D(Data_7926);actor_index=(uint16_t)(2u*(test%16));r.bx=actor_index;
        ram.player_count=(test&1)?2:word();r.di=ram.player_count==2?(uint16_t)(2u*(test%2)):0;ram.actor[4]=r.di;
        platform_count=test%11;for(unsigned i=0;i<30;i++) ram.platform[i]=word();configure();
        r.ax=word();r.cx=word();r.dx=word();r.si=word();r.bp=word();r.flags=word();r.es=word();r.ip=word();
        for(unsigned mode=0;mode<6;mode++) {StoneRam initial=ram;compare(mode,r);ram=initial;}
    }
    view_cases();printf("PASS %llu comparisons; exhaustive action/velocity/X/vertical domains, signed edges, 12000 arbitrary states x six entries, immediate ordered hazard views\n",comparisons);return 0;
}
#endif
