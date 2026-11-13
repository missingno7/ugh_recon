/* Real C pair, one arbitrary physical slot, immutable finite resources and
 * ten platform rows. No model substitutes for either transition algorithm.
 * The RAM shim asserts the complete read/write footprint. */
#ifdef __CPROVER__
void __CPROVER_assert(_Bool,const char *);void __CPROVER_assume(_Bool);
#define CHECK(c,m) __CPROVER_assert((c),(m))
#else
#include <stdio.h>
#include <stdlib.h>
#define CHECK(c,m) do {if(!(c)) {fprintf(stderr,"%s line %d op=%u case=%llu\n",m,__LINE__,operation,comparisons);exit(23);}} while(0)
#endif
typedef struct ItRam {
    uint16_t actor[24],descriptor[37],platforms[3][10],animation[4][3],journey[7];
    uint16_t remaining,completion,fade_rate,fade_level,fraction;
} ItRam;
typedef struct ItStore {uint16_t bank,address,value;int byte;} ItStore;
static ItRam ram;static ItStore stores[32];static unsigned store_count;
static uint16_t stack_words[8],actor_index;static unsigned operation,journey_count;
static int modern_calls;
#if defined(__CPROVER__) && MODE==6
static unsigned dispatch_depth;
#endif
#ifndef __CPROVER__
static unsigned long long comparisons;
#endif
static const uint16_t platform_bases[3]={D(PlatformHeights),D(PlatformArrivalPointsX),D(PlatformActorOccupants)};
static const uint16_t vector_bases[4]={0x0e32,0x0e46,0x0e5a,0x0e6e};
uint16_t it_read(uint16_t bank,uint16_t address) {
    if(bank==1) {CHECK(address>=36848u && address<36864u && !(address&1u),"stack read footprint");return stack_words[(address-36848u)/2u];}
    CHECK(bank==DATA_SEG,"normalized ordinary data bank");
    if(address>=D(ActorDescriptors) && address<D(ActorDescriptors)+768u) {
        unsigned delta=address-D(ActorDescriptors);CHECK(delta%32u==actor_index,"only selected actor read");return ram.actor[delta/32u];
    }
    uint16_t descriptor=ram.actor[0];
    if(address>=descriptor && address<descriptor+74u) {CHECK(!((address-descriptor)&1u),"aligned descriptor");return ram.descriptor[(address-descriptor)/2u];}
    for(unsigned i=0;i<3;i++) if(address>=platform_bases[i] && address<platform_bases[i]+20u) {
        CHECK(!((address-platform_bases[i])&1u),"aligned platform");return ram.platforms[i][(address-platform_bases[i])/2u];
    }
    for(unsigned i=0;i<4;i++) if(address>=vector_bases[i] && address<vector_bases[i]+6u) {
        CHECK(!((address-vector_bases[i])&1u),"aligned animation window");return ram.animation[i][(address-vector_bases[i])/2u];
    }
    if(address>=0x6200u && address<0x620eu) {CHECK(!((address-0x6200u)&1u),"aligned journey");return ram.journey[(address-0x6200u)/2u];}
    if(address==D(RemainingPassengerJourneys)) return ram.remaining;
    if(address==D(LevelCompletionMarker)) return ram.completion;
    if(address==D(ScreenFadeStep)) return ram.fade_rate;
    if(address==D(ScreenFadeLevel)) return ram.fade_level;
    if(address==D(CoordinateScaleScratch)) return ram.fraction;
    CHECK(0,"read inside declared footprint");return 0;
}
static void record(uint16_t bank,uint16_t address,uint16_t value,int byte) {
    CHECK(store_count<32,"finite ordered store journal");stores[store_count++]=(ItStore){bank,address,value,byte};
}
void it_write(uint16_t bank,uint16_t address,uint16_t value) {
    record(bank,address,value,0);
    if(bank==1) {CHECK(address>=36848u && address<36864u && !(address&1u),"stack write footprint");stack_words[(address-36848u)/2u]=value;return;}
    CHECK(bank==DATA_SEG,"ordinary write bank");
    if(address>=D(ActorDescriptors) && address<D(ActorDescriptors)+768u) {
        unsigned delta=address-D(ActorDescriptors);CHECK(delta%32u==actor_index,"only selected actor write");ram.actor[delta/32u]=value;return;
    }
    if(address>=D(PlatformActorOccupants) && address<D(PlatformActorOccupants)+20u) {CHECK(!((address-D(PlatformActorOccupants))&1u),"aligned occupant write");ram.platforms[2][(address-D(PlatformActorOccupants))/2u]=value;return;}
    if(address==D(ScreenFadeStep)) {ram.fade_rate=value;return;}
    if(address==D(ScreenFadeLevel)) {ram.fade_level=value;return;}
    if(address==D(CoordinateScaleScratch)) {ram.fraction=value;return;}
    CHECK(0,"write inside declared effects");
}
uint8_t it_byte(uint16_t bank,uint16_t address) {return (uint8_t)it_read(bank,address);}
void it_byte_write(uint16_t bank,uint16_t address,uint8_t value) {
    CHECK(bank==DATA_SEG,"byte write bank");record(bank,address,value,1);
    if(address==D(RemainingPassengerJourneys)) {ram.remaining=(uint16_t)((ram.remaining&65280u)|value);return;}
    CHECK(address==D(LevelCompletionMarker),"only objective and completion byte writes");ram.completion=(uint16_t)((ram.completion&65280u)|value);
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r) {
    CHECK(bank==GAME_SEG,"closed near dispatch bank");
#ifdef __CPROVER__
    /* Checked per-entry call graph, avoiding impossible recursive expansion.
     * No callee target/depth is assumed. All real callee C bodies remain. */
#if MODE==0
    if(target==G(ScaleLevelSpeedToThreeHalves)) return l1_ScaleLevelSpeedToThreeHalves(r);
    CHECK(target==G(IgnoreActorState),"read tail is exact no-op");
    return modern_calls?c_IgnoreActorState(r):l1_IgnoreActorState(r);
#elif MODE==1
    CHECK(target==G(PlacePassengerOnPlatform),"wait tail is placement");
    return modern_calls?c_PlacePassengerOnPlatform(r):l1_PlacePassengerOnPlatform(r);
#elif MODE==3
    CHECK(target==G(BeginPassengerPlatformWait),"arrival tail stays unit-five L1");return l1_BeginPassengerPlatformWait(r);
#elif MODE==4
    CHECK(target==G(BeginPassengerDeparture),"walk tail begins departure");
    return modern_calls?c_BeginPassengerDeparture(r):l1_BeginPassengerDeparture(r);
#elif MODE==6
    if(!dispatch_depth) {
        CHECK(target==G(ReadPassengerJourneyLeg),"departure tail reads next leg");dispatch_depth++;
        int status=modern_calls?c_ReadPassengerJourneyLeg(r):l1_ReadPassengerJourneyLeg(r);dispatch_depth--;return status;
    }
    CHECK(dispatch_depth==1,"one immediate journey tail");
    if(target==G(ScaleLevelSpeedToThreeHalves)) return l1_ScaleLevelSpeedToThreeHalves(r);
    CHECK(target==G(IgnoreActorState),"exhausted departure journey retires");return modern_calls?c_IgnoreActorState(r):l1_IgnoreActorState(r);
#else
    (void)target;(void)r;CHECK(0,"no callee for this entry");return UGH_BAD_CALLBACK;
#endif
#else
    if(target==G(ScaleLevelSpeedToThreeHalves)) return l1_ScaleLevelSpeedToThreeHalves(r);
    if(target==G(IgnoreActorState)) return modern_calls?c_IgnoreActorState(r):l1_IgnoreActorState(r);
    if(target==G(BeginPassengerPlatformWait)) return l1_BeginPassengerPlatformWait(r); /* unit five stays L1 */
    if(target==G(PlacePassengerOnPlatform)) return modern_calls?c_PlacePassengerOnPlatform(r):l1_PlacePassengerOnPlatform(r);
    if(target==G(BeginPassengerDeparture)) return modern_calls?c_BeginPassengerDeparture(r):l1_BeginPassengerDeparture(r);
    if(target==G(ReadPassengerJourneyLeg)) return modern_calls?c_ReadPassengerJourneyLeg(r):l1_ReadPassengerJourneyLeg(r);
    CHECK(0,"exact descriptor tail target set");return UGH_BAD_CALLBACK;
#endif
}
int ugh_call_near(uint16_t target,uint16_t return_ip,Regs *r) {
    r->sp=(uint16_t)(r->sp-2);it_write(r->ss,r->sp,return_ip);
    int status=ugh_dispatch(r->cs,target,r);if(!status) r->sp=(uint16_t)(r->sp+2);return status;
}
static int execute(unsigned mode,Regs *r,int modern) {
    modern_calls=modern;
    switch(mode) {
    case 0:return modern?c_ReadPassengerJourneyLeg(r):l1_ReadPassengerJourneyLeg(r);
    case 1:return modern?c_WaitForPassengerPlatform(r):l1_WaitForPassengerPlatform(r);
    case 2:return modern?c_PlacePassengerOnPlatform(r):l1_PlacePassengerOnPlatform(r);
    case 3:return modern?c_AnimatePassengerArrival(r):l1_AnimatePassengerArrival(r);
    case 4:return modern?c_WalkPassengerToExit(r):l1_WalkPassengerToExit(r);
    case 5:return modern?c_BeginPassengerDeparture(r):l1_BeginPassengerDeparture(r);
    case 6:return modern?c_AnimatePassengerDeparture(r):l1_AnimatePassengerDeparture(r);
    default:return modern?c_IgnoreActorState(r):l1_IgnoreActorState(r);
    }
}
static void configure(void) {
    ram.descriptor[4]=G(ReadPassengerJourneyLeg);ram.descriptor[5]=G(WaitForPassengerPlatform);
    ram.descriptor[6]=G(PlacePassengerOnPlatform);ram.descriptor[7]=G(AnimatePassengerArrival);ram.descriptor[8]=G(BeginPassengerPlatformWait);
    ram.descriptor[9]=G(UpdatePassengerPlatformWait);ram.descriptor[19]=G(WalkPassengerToExit);
    ram.descriptor[20]=G(BeginPassengerDeparture);ram.descriptor[21]=G(AnimatePassengerDeparture);ram.descriptor[22]=G(IgnoreActorState);
    for(unsigned i=0;i<4;i++) {ram.descriptor[25+i]=vector_bases[i];ram.animation[i][2]=65535u;}
    ram.journey[2u*journey_count]=65535u;
}
static void compare(unsigned mode,Regs incoming) {
    operation=mode;ItRam initial=ram;Regs reference=incoming,bridge=incoming;
    store_count=0;int expected_status=execute(mode,&reference,0);ItRam expected=ram;
    unsigned expected_count=store_count;ItStore expected_stores[32];
    for(unsigned i=0;i<expected_count;i++) expected_stores[i]=stores[i];
    ram=initial;store_count=it_fallback=0;int actual_status=execute(mode,&bridge,1);
    CHECK(it_fallback==0,"all admitted calls use native implementation");
    CHECK(expected_status==actual_status && actual_status==UGH_OK,"both real C executions complete");
    for(unsigned i=0;i<24;i++) CHECK(expected.actor[i]==ram.actor[i],"every persistent actor word including render history");
    for(unsigned i=0;i<3;i++) for(unsigned j=0;j<10;j++) CHECK(expected.platforms[i][j]==ram.platforms[i][j],"platform contents and occupancy");
    CHECK(expected.remaining==ram.remaining && expected.completion==ram.completion && expected.fade_rate==ram.fade_rate && expected.fade_level==ram.fade_level && expected.fraction==ram.fraction,"objectives, byte neighbors, fade and real scale scratch");
    CHECK(expected_count==store_count,"same ordered store count");
    for(unsigned i=0;i<expected_count;i++) CHECK(expected_stores[i].bank==stores[i].bank && expected_stores[i].address==stores[i].address && expected_stores[i].value==stores[i].value && expected_stores[i].byte==stores[i].byte,"same ordered word/byte/stack stores, including pre-tail writes");
    CHECK(reference.ax==bridge.ax && reference.bx==bridge.bx && reference.cx==bridge.cx && reference.dx==bridge.dx && reference.si==bridge.si && reference.di==bridge.di && reference.bp==bridge.bp,"full working register shell");
    CHECK(reference.cs==bridge.cs && reference.ds==bridge.ds && reference.es==bridge.es && reference.ss==bridge.ss && reference.sp==bridge.sp && reference.ip==bridge.ip && reference.flags==bridge.flags,"full flags and continuation shell");
#ifndef __CPROVER__
    comparisons++;
#endif
}
#ifdef __CPROVER__
int main(void) {
    ItRam arbitrary;ram=arbitrary;Regs incoming;uint16_t slot;_Bool exhausted;
    __CPROVER_assume(slot<16);actor_index=(uint16_t)(2u*slot);
    ram.actor[0]=D(Data_7720);ram.actor[2]=0x6200;
    journey_count=MODE==0 && exhausted?1:MODE==6 && exhausted?2:3;
    for(unsigned i=0;i<3;i++) __CPROVER_assume(ram.journey[2*i]!=65535u);
    for(unsigned i=0;i<4;i++) for(unsigned j=0;j<2;j++) __CPROVER_assume(ram.animation[i][j]!=65535u);
#if MODE==1 || MODE==2
    __CPROVER_assume(ram.actor[5]<10);ram.actor[7]=(uint16_t)(2u*ram.actor[5]);
#endif
#if MODE==4
    __CPROVER_assume(ram.actor[6]<10);ram.actor[8]=(uint16_t)(2u*ram.actor[6]);
#endif
#if MODE==3 || MODE==4 || MODE==6
    if(ram.actor[17]==1) {
        __CPROVER_assume(ram.actor[16]==65534u || ram.actor[16]==0
#if MODE!=6
            || ram.actor[16]==2
#endif
        );
    }
#endif
    configure();
#if MODE!=7
    incoming.ds=DATA_SEG;incoming.cs=GAME_SEG;incoming.ss=1;incoming.sp=36864u;incoming.bx=actor_index;
#endif
    compare(MODE,incoming);return 0;
}
#else
static uint32_t rng=2654435769u;
static uint16_t word(void) {rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return (uint16_t)rng;}
static Regs seed(void) {
    ram=(ItRam){0};journey_count=3;actor_index=0;ram.actor[0]=D(Data_7720);ram.actor[2]=0x6200;
    ram.actor[5]=0;ram.actor[6]=1;ram.actor[7]=0;ram.actor[8]=2;
    ram.actor[10]=3200;ram.actor[11]=3200;ram.actor[12]=100;ram.actor[14]=100;
    ram.actor[16]=65534u;ram.actor[17]=1;ram.descriptor[0]=8;ram.descriptor[1]=16;ram.descriptor[31]=7;
    ram.remaining=2;ram.completion=0x9a53;ram.fade_level=100;
    for(unsigned i=0;i<3;i++) {ram.journey[2*i]=(uint16_t)i;ram.journey[2*i+1]=21;}
    for(unsigned i=0;i<10;i++) {ram.platforms[0][i]=100;ram.platforms[1][i]=108;ram.platforms[2][i]=65535u;}
    for(unsigned i=0;i<4;i++) {ram.animation[i][0]=(uint16_t)(100+i);ram.animation[i][1]=(uint16_t)(200+i);}
    configure();Regs r={0};r.ds=DATA_SEG;r.cs=GAME_SEG;r.ss=1;r.sp=36864u;r.flags=0xad5;return r;
}
int main(void) {
    static const uint16_t edges[]={0,1,2,32767,32768,65534,65535};Regs r;
    for(unsigned value=0;value<65536u;value++) {
        r=seed();ram.actor[9]=(uint16_t)value;compare(1,r);
        r=seed();ram.actor[9]=(uint16_t)value;ram.platforms[2][0]=0;compare(1,r);
        for(unsigned mode=3;mode<=6;mode++) if(mode!=5) {r=seed();ram.actor[17]=(uint16_t)value;compare(mode,r);}
        r=seed();ram.descriptor[31]=(uint16_t)value;compare(3,r);
        r=seed();ram.journey[1]=(uint16_t)value;compare(0,r);
        r=seed();ram.actor[12]=(uint16_t)value;compare(4,r);
        r=seed();ram.actor[16]=(uint16_t)value;ram.actor[17]=2;compare(3,r);
    }
    for(unsigned remaining=0;remaining<256;remaining++) for(unsigned edge=0;edge<7;edge++) {
        r=seed();journey_count=1;configure();ram.remaining=(uint16_t)(0x5a00u|remaining);ram.fade_level=edges[edge];compare(0,r);
    }
    /* Current arrival sentinel, departure lookahead, animation wrap, signed
     * cached X equality, and last-leg retirement after a departure tail. */
    for(unsigned cursor=0;cursor<3;cursor++) {
        r=seed();ram.actor[16]=cursor==0?65534u:(uint16_t)(2u*(cursor-1));compare(3,r);compare(4,r);
    }
    r=seed();ram.actor[16]=0;journey_count=2;configure();compare(6,r);
    r=seed();ram.actor[16]=0;journey_count=2;ram.remaining=1;configure();compare(6,r);
    CHECK((uint8_t)ram.completion==254 && ram.actor[18]==65535u,"departure exhaustion completes and hides in same call");
    r=seed();ram.animation[2][0]=65535u;compare(3,r); /* empty arrival current sentinel */
    r=seed();ram.descriptor[31]=0;compare(3,r);compare(3,r);
    CHECK(ram.actor[17]==65535u,"zero period predecrements through word wrap");
    for(unsigned order=0;order<2;order++) {
        r=seed();ram.actor[3]=G(WaitForPassengerPlatform);ram.actor[9]=0;ItRam second=ram;
        actor_index=order?30:0;r.bx=actor_index;uint16_t first_index=actor_index;compare(1,r);
        CHECK(ram.actor[3]==G(AnimatePassengerArrival) && ram.platforms[2][0]==first_index,"first eligible slot claims platform immediately");
        for(unsigned i=0;i<24;i++) ram.actor[i]=second.actor[i];
        actor_index=order?0:30;r.bx=actor_index;compare(1,r);
        CHECK(ram.actor[3]==G(WaitForPassengerPlatform) && ram.platforms[2][0]==first_index,"later slot sees occupancy in same dispatch");
    }
    for(unsigned test=0;test<8000;test++) {
        r=seed();for(unsigned i=1;i<24;i++) ram.actor[i]=word();
        ram.actor[2]=0x6200;ram.actor[5]=(uint16_t)(word()%10);ram.actor[6]=(uint16_t)(word()%10);
        ram.actor[7]=(uint16_t)(2u*ram.actor[5]);ram.actor[8]=(uint16_t)(2u*ram.actor[6]);
        ram.actor[16]=(test%3)==0?65534u:0;ram.actor[17]=(test%3)==0?1:(test%3)==1?0:word();
        ram.actor[0]=test%3==0?D(Data_7720):test%3==1?D(Data_77B4):D(Data_7848);
        actor_index=(uint16_t)(2u*(test%16));r.bx=actor_index;
        for(unsigned i=0;i<2;i++) ram.descriptor[i]=word();
        ram.descriptor[31]=word();
        for(unsigned i=0;i<4;i++) for(unsigned j=0;j<2;j++) ram.animation[i][j]=(uint16_t)(word()%65535u);
        for(unsigned i=0;i<3;i++) {ram.journey[2*i]=(uint16_t)(word()%65535u);ram.journey[2*i+1]=word();}
        for(unsigned i=0;i<3;i++) for(unsigned j=0;j<10;j++) ram.platforms[i][j]=word();
        ram.remaining=word();ram.completion=word();ram.fade_level=word();ram.fade_rate=word();ram.fraction=word();configure();
        r.ax=word();r.cx=word();r.dx=word();r.si=word();r.di=word();r.bp=word();r.flags=word();r.ip=word();r.es=word();
        for(unsigned mode=0;mode<8;mode++) {ItRam initial=ram;compare(mode,r);ram=initial;}
    }
    puts("PASS actual-L1/native journal, all persistent state, full registers/flags and ordered stores");
    printf("%llu comparisons: exhaustive word slices, all objective bytes and 8000 generated states x eight entries\n",comparisons);return 0;
}
#endif
