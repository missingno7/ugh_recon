/* Included after pair.inc. Actual maintained L1, native and bridge code.
 * Normalized ordinary word RAM, immutable descriptor and up to ten platforms.
 * No mutable descriptor aliases, MMIO or stack/data aliases are admitted. */
#ifdef __CPROVER__
void __CPROVER_assert(_Bool,const char *);
void __CPROVER_assume(_Bool);
#define CHECK(c,m) __CPROVER_assert((c),(m))
#else
#include <stdio.h>
#include <stdlib.h>
#define CHECK(c,m) do { if(!(c)) { fprintf(stderr,"%s at %d mode=%u case=%llu\n",m,__LINE__,operation,comparisons);exit(23); } } while(0)
#endif
typedef struct ItemRam {
    uint16_t fields[7][12], descriptor[10];
    uint16_t left[11],right[10],height[10];
    ObjectPosition players[2];
    uint16_t player_count,timer,multiplier,limit,difficulty;
    uint8_t lives;
} ItemRam;
static ItemRam ram;
static uint16_t stack_words[4];
static unsigned operation;
static int modern_calls;
static unsigned visit_count;
static uint16_t visits[12];
#ifndef __CPROVER__
static unsigned long long comparisons;
#endif
static unsigned platform_count;
static const uint16_t item_bases[7]={D(FallingItemDescriptors),D(FallingItemCallbacks),D(FallingItemSprites),
    D(FallingItemX),D(FallingItemY),D(FallingItemVerticalStep),D(FallingItemMotionOrLifetime)};
uint16_t items_rd16(uint16_t segment,uint16_t address) {
    if(segment==1 && address>=36856u && address<36864u) return stack_words[(address-36856u)/2];
    CHECK(segment==0,"data bank normalized");
#if defined(__CPROVER__) && MODE==5
    if(address>=D(FallingItemSprites) && address<D(FallingItemSprites)+24u) return ram.fields[2][(address-D(FallingItemSprites))/2];
    CHECK(address>=D(FallingItemCallbacks) && address<D(FallingItemCallbacks)+24u,"dispatcher footprint");
    return ram.fields[1][(address-D(FallingItemCallbacks))/2];
#else
    for(unsigned f=0;f<7;f++) if(address>=item_bases[f] && address<item_bases[f]+24u) {
        CHECK(!((address-item_bases[f])&1u),"aligned array operand");
        return ram.fields[f][(address-item_bases[f])/2];
    }
    if(address>=256 && address<276) return ram.descriptor[(address-256)/2];
    if(address>=D(PlatformLeftEdges) && address<D(PlatformLeftEdges)+22u) return ram.left[(address-D(PlatformLeftEdges))/2];
    if(address>=D(PlatformRightEdges) && address<D(PlatformRightEdges)+20u) return ram.right[(address-D(PlatformRightEdges))/2];
    if(address>=D(PlatformHeights) && address<D(PlatformHeights)+20u) return ram.height[(address-D(PlatformHeights))/2];
    if(address>=D(PlayerX32) && address<D(PlayerX32)+4u) return ram.players[(address-D(PlayerX32))/2].x32;
    if(address>=D(PlayerY32) && address<D(PlayerY32)+4u) return ram.players[(address-D(PlayerY32))/2].y32;
    if(address==D(PlayerCount)) return ram.player_count;
    if(address==D(LevelTimer)) return ram.timer;
    if(address==D(ScoreMultiplier)) return ram.multiplier;
    if(address==D(SelectedDifficulty)) return ram.difficulty;
    if(address==(uint16_t)(D(MultiplierLimitsByDifficulty)+(uint16_t)(ram.difficulty*2u))) return ram.limit;
    CHECK(0,"read inside declared footprint");return 0;
#endif
}
void items_wr16(uint16_t segment,uint16_t address,uint16_t value) {
    if(segment==1 && address>=36856u && address<36864u) { stack_words[(address-36856u)/2]=value;return; }
    CHECK(segment==0,"write data bank normalized");
    for(unsigned f=0;f<7;f++) if(address>=item_bases[f] && address<item_bases[f]+24u) {
        CHECK(!((address-item_bases[f])&1u),"aligned write operand");
        ram.fields[f][(address-item_bases[f])/2]=value;return;
    }
    if(address==D(LevelTimer)) { ram.timer=value;return; }
    CHECK(0,"write inside owned footprint");
}
uint8_t items_rd8(uint16_t segment,uint16_t address) {
    CHECK(segment==0 && address==D(LivesRemaining),"byte read is life count");return ram.lives;
}
void items_wr8(uint16_t segment,uint16_t address,uint8_t value) {
    CHECK(segment==0,"byte write bank");
    if(address==D(LivesRemaining)) { ram.lives=value;return; }
    CHECK(address==D(ScoreMultiplier),"only multiplier low byte otherwise");
    ram.multiplier=(uint16_t)((ram.multiplier&65280u)|value);
}
int ugh_dispatch(uint16_t segment,uint16_t target,Regs *r) {
    (void)segment;
#if defined(__CPROVER__) && MODE==5
    (void)target;
    CHECK(visit_count<12,"dispatcher visits at most twelve slots");
    visits[visit_count++]=r->bx;return 0;
#else
    if(target==G(LandFallingItem)) return modern_calls?c_LandFallingItem(r):l1_LandFallingItem(r);
    if(target==G(FindPlayerTouchingFallingItem)) return c_FindPlayerTouchingFallingItem(r);
    if(target==G(AdvanceFallingItem)) return modern_calls?c_AdvanceFallingItem(r):l1_AdvanceFallingItem(r);
    if(target==G(ExpireOrCollectFallingItem)) return modern_calls?c_ExpireOrCollectFallingItem(r):l1_ExpireOrCollectFallingItem(r);
    CHECK(0,"closed stored handler set");return 3;
#endif
}
int ugh_call_near(uint16_t target,uint16_t return_ip,Regs *r) {
    r->sp=(uint16_t)(r->sp-2);items_wr16(r->ss,r->sp,return_ip);
    int status=ugh_dispatch(r->cs,target,r);if(!status) r->sp=(uint16_t)(r->sp+2);return status;
}
static int execute(unsigned mode,Regs *r,int modern) {
    modern_calls=modern;
    if(mode==0) return modern?c_SpawnFallingItem(r):l1_SpawnFallingItem(r);
    if(mode==1) return modern?c_AdvanceFallingItem(r):l1_AdvanceFallingItem(r);
    if(mode==2) return modern?c_LandFallingItem(r):l1_LandFallingItem(r);
    if(mode==3) return modern?c_ExpireOrCollectFallingItem(r):l1_ExpireOrCollectFallingItem(r);
    return modern?c_DispatchFallingItems(r):l1_DispatchFallingItems(r);
}
static void compare(unsigned mode,Regs incoming) {
    ItemRam initial=ram;Regs old=incoming,bridge=incoming;
    visit_count=0;
    int status=execute(mode,&old,0);ItemRam expected=ram;
    unsigned expected_count=visit_count;uint16_t expected_visits[12];
    for(unsigned i=0;i<expected_count;i++) expected_visits[i]=visits[i];
    visit_count=0;
#ifndef __CPROVER__
    if(mode==4) {
        ram=initial;FallingItem native[12];LevelPlatform platforms[10];
        for(unsigned i=0;i<12;i++) native[i]=item_project(&incoming,(uint16_t)(i*2));
        for(unsigned i=0;i<platform_count;i++) {
            platforms[i].left=items_rd16(0,(uint16_t)(D(PlatformLeftEdges)+2*i));
            platforms[i].right=items_rd16(0,(uint16_t)(D(PlatformRightEdges)+2*i));
            platforms[i].surface_y=items_rd16(0,(uint16_t)(D(PlatformHeights)+2*i));
        }
        ItemBenefits benefits={ram.timer,ram.multiplier,ram.limit,ram.lives};
        items_dispatch(native,platforms,platform_count,ram.players,ram.player_count,&benefits);
        for(unsigned i=0;i<12;i++) {
            item_publish(&incoming,(uint16_t)(i*2),&native[i]);
            ram.fields[1][i]=native[i].phase==ITEM_FLIGHT?G(AdvanceFallingItem):G(ExpireOrCollectFallingItem);
        }
        for(unsigned f=0;f<7;f++) for(unsigned i=0;i<12;i++)
            CHECK(expected.fields[f][i]==ram.fields[f][i],"ordinary enum dispatcher persistent state");
        CHECK(expected.timer==benefits.timer && expected.multiplier==benefits.multiplier && expected.lives==benefits.lives,"ordinary enum dispatcher benefits");
    }
#endif
    ram=initial;int actual=execute(mode,&bridge,1);
    /* L1 diagnoses the unresolved saved-BX target with BAD_CALLBACK. The new
     * bridge exposes the same pending CS:IP/SP using the ABI control-transfer
     * outcome, like the established far-call/near-RET hooks. */
    CHECK(status==actual || (mode==0 && status==UGH_BAD_CALLBACK && actual==UGH_CONTROL_TRANSFER),"same completion or explicit abnormal transfer");
    CHECK(expected_count==visit_count,"same callback count");
    for(unsigned i=0;i<expected_count;i++) CHECK(expected_visits[i]==visits[i],"same callback order");
    for(unsigned f=0;f<7;f++) for(unsigned i=0;i<12;i++)
        CHECK(expected.fields[f][i]==ram.fields[f][i],"project step compare: every persistent slot word");
    CHECK(expected.timer==ram.timer && expected.multiplier==ram.multiplier && expected.lives==ram.lives,"benefits including byte-store high byte");
    CHECK(old.ax==bridge.ax && old.bx==bridge.bx && old.cx==bridge.cx && old.dx==bridge.dx && old.si==bridge.si && old.di==bridge.di && old.bp==bridge.bp,"bridge complete register shell");
    CHECK(old.flags==bridge.flags && old.sp==bridge.sp && old.ip==bridge.ip && old.cs==bridge.cs && old.ds==bridge.ds && old.es==bridge.es && old.ss==bridge.ss,"flags and abnormal continuation preserved");
#ifndef __CPROVER__
    comparisons++;
#endif
}
static void configure(void) {
    ram.descriptor[2]=G(SpawnFallingItem);ram.descriptor[3]=G(AdvanceFallingItem);
    ram.descriptor[4]=G(LandFallingItem);ram.descriptor[5]=G(ExpireOrCollectFallingItem);
    for(unsigned i=0;i<12;i++) ram.fields[0][i]=256;
    /* Difficulty itself is normalized to zero: the table VALUE remains any
     * word, not merely one of the three shipped caps. Avoid mutable table aliases. */
    ram.difficulty=0;
    if(platform_count<10) ram.left[10]=ram.right[0]; /* physical adjacent-array alias */
    for(unsigned i=0;i<platform_count;i++) ram.left[i]&=32767u;
    ram.left[platform_count]=65535u;
}
#ifdef __CPROVER__
int main(void) {
    ItemRam arbitrary;ram=arbitrary;
    platform_count=PLATFORMS;configure();
    Regs arbitrary_regs;Regs incoming=arbitrary_regs;
    incoming.ds=0;incoming.ss=1;incoming.cs=GAME_SEG;incoming.sp=36864u;incoming.si=256;
    if(MODE!=0) incoming.bx=0;
    for(unsigned i=0;i<12;i++) {
        uint16_t handler=ram.fields[1][i];
        __CPROVER_assume(handler==G(AdvanceFallingItem) || handler==G(ExpireOrCollectFallingItem));
    }
    compare(MODE,incoming);return 0;
}
#else
static uint32_t random_word=2654435769u;
static uint16_t word(void) { random_word^=random_word<<13;random_word^=random_word>>17;random_word^=random_word<<5;return (uint16_t)random_word; }
static Regs seed(void) {
    ram=(ItemRam){0};platform_count=0;
    ram.descriptor[0]=8;ram.descriptor[1]=16;ram.descriptor[6]=57;ram.descriptor[7]=3000;ram.descriptor[8]=285;
    for(unsigned i=0;i<12;i++) {
        ram.fields[1][i]=G(ExpireOrCollectFallingItem);ram.fields[2][i]=65535u;
        ram.fields[3][i]=1000;ram.fields[4][i]=1000;ram.fields[6][i]=560;
    }
    ram.players[0].x32=500;ram.players[0].y32=1000;ram.players[1]=ram.players[0];
    ram.player_count=2;ram.limit=9;configure();
    Regs r={0};r.ds=0;r.ss=1;r.cs=GAME_SEG;r.sp=36864u;r.si=256;r.flags=1539;
    return r;
}
int main(void) {
    for(unsigned target=0;target<3;target++) {
        Regs r=seed();r.bx=target==0?0:target==1?G(IgnoreExhaustedTree):65535u;
        for(unsigned i=0;i<12;i++) ram.fields[2][i]=285;
        operation=0;compare(0,r);
    }
    for(unsigned mask=0;mask<4096;mask++) for(unsigned marker=0;marker<3;marker++) {
        Regs r=seed();r.ax=1000;r.bp=2000;r.bx=G(IgnoreExhaustedTree);
        for(unsigned i=0;i<12;i++) ram.fields[2][i]=(mask&(1u<<i))?(marker==0?65535u:marker==1?65534u:32768u):285;
        operation=0;compare(0,r);
        r=seed();for(unsigned i=0;i<12;i++) ram.fields[2][i]=(mask&(1u<<i))?65535u:65534u;
        operation=4;compare(4,r);
    }
    for(unsigned value=0;value<65536u;value++) {
        for(unsigned kind=0;kind<3;kind++) {
            Regs r=seed();ram.descriptor[9]=(uint16_t)kind;ram.fields[6][0]=(uint16_t)value;
            operation=3;compare(3,r); /* Every lifetime word, with contact. */
            r=seed();ram.descriptor[9]=(uint16_t)kind;ram.timer=(uint16_t)value;ram.multiplier=(uint16_t)value;
            ram.lives=(uint8_t)value;compare(3,r); /* Fixed reward, every shared word. */
        }
        Regs r=seed();ram.lives=(uint8_t)value;ram.descriptor[7]=(uint16_t)(value>>8);ram.descriptor[9]=1;
        operation=3;compare(3,r); /* Complete byte-add input pairs. */
        r=seed();ram.fields[6][0]=(uint16_t)value;operation=2;compare(2,r);
        for(unsigned field=3;field<7;field++) {
            r=seed();ram.fields[field][0]=(uint16_t)value;ram.fields[1][0]=G(AdvanceFallingItem);
            operation=1;compare(1,r);
        }
    }
    for(unsigned sample=0;sample<100000;sample++) {
        Regs r=seed();platform_count=sample%11;
        for(unsigned j=0;j<10;j++) { ram.left[j]=(uint16_t)(word()%320);ram.right[j]=word();ram.height[j]=word(); }
        for(unsigned j=0;j<10;j++) ram.descriptor[j]=word();
        for(unsigned f=1;f<7;f++) for(unsigned i=0;i<12;i++) ram.fields[f][i]=word();
        for(unsigned i=0;i<2;i++) { ram.players[i].x32=word();ram.players[i].y32=word(); }
        ram.player_count=word();ram.timer=word();ram.multiplier=word();ram.limit=word();ram.lives=(uint8_t)word();
        configure();r.flags=word();r.ax=word();r.bp=word();r.dx=word();r.cx=word();
        operation=sample%4;compare(operation,r);
        if(sample<10000) {
            for(unsigned i=0;i<12;i++) ram.fields[1][i]=(word()&1u)?G(AdvanceFallingItem):G(ExpireOrCollectFallingItem);
            operation=4;r.bx=0;compare(4,r);
        }
    }
    printf("PASS %llu actual-C comparisons\n",comparisons);return 0;
}
#endif
