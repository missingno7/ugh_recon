/* Normalized disjoint actor arrays. A pixel service is observed before its
 * arbitrary shared post-registers; it preserves the real SI/DS/CS/SS:SP shell
 * and does not write actor history. Real blitters are exercised separately. */
#ifdef __CPROVER__
void __CPROVER_assert(_Bool,const char *);void __CPROVER_assume(_Bool);
#define CHECK(c,m) __CPROVER_assert((c),(m))
#else
#include <stdio.h>
#include <stdlib.h>
#define CHECK(c,m) do {if(!(c)) {fprintf(stderr,"%s line%d op%u case%llu\n",m,__LINE__,operation,comparisons);exit(23);}} while(0)
#endif
static uint16_t ram[10],actor_index;
static unsigned operation,modern,observations,expected_observations,calls;
static unsigned long long comparisons;
void rh_abort(void) {
    CHECK(0,"bridge rejection is a failed property, never an assumed path");
#ifdef __CPROVER__
    __CPROVER_assume(0);
#else
    exit(23);
#endif
}
typedef struct Observation {unsigned kind;uint16_t address,value,x,y,sprite,ret;} Observation;
static Observation expected[8];
static Regs service_after[2];static int service_status[2];
static uint16_t bases[10]={D(ActorX32),D(ActorY32),D(ActorSpriteIds),D(ActorOverlayOrScriptCallbacks),D(ActorPixelX),D(ActorPixelY),D(ActorPreviousDrawX),D(ActorPreviousDrawY),D(ActorEraseSprite),D(ActorEraseOverlaySprite)};
static void observe(Observation value) {
    CHECK(observations<8,"bounded ordered observations");
    if(modern) {
        CHECK(observations<expected_observations,"no extra observation");Observation old=expected[observations];
        CHECK(value.kind==old.kind && value.address==old.address && value.value==old.value && value.x==old.x && value.y==old.y && value.sprite==old.sprite && value.ret==old.ret,"ordered stores and pixel requests");
    } else expected[observations]=value;
    observations++;
}
uint16_t rh_read(uint16_t bank,uint16_t address) {
    CHECK(bank==DATA_SEG,"data bank");
    for(unsigned i=0;i<10;i++) if(address==(uint16_t)(bases[i]+actor_index)) return ram[i];
    CHECK(0,"complete input footprint");return 0;
}
void rh_write(uint16_t bank,uint16_t address,uint16_t value) {
    CHECK(bank==DATA_SEG,"store bank");
    for(unsigned i=2;i<10;i++) if(address==(uint16_t)(bases[i]+actor_index)) {
        CHECK(i!=3,"overlay simulation output is not owned");
        observe((Observation){0,address,value,0,0,0,0});ram[i]=value;return;
    }
    CHECK(0,"store footprint excludes all other bytes/slots");
}
int rh_call(uint16_t target,uint16_t ret,Regs *r) {
    int restore=target==G(RestoreSpriteBackground);
    CHECK(restore || target==G(DrawTransparentSprite),"complete pixel target set");
    CHECK(calls<2,"at most two pixel requests");
    observe((Observation){restore?1u:2u,0,0,restore?r->ax:r->bx,restore?r->bx:r->cx,restore?r->cx:r->ax,ret});
    Regs next=service_after[calls];next.si=r->si;next.ds=r->ds;next.cs=r->cs;next.ss=r->ss;next.sp=r->sp;
    *r=next;return service_status[calls++];
}
static int execute(unsigned op,Regs *r,int native) {
    switch(op) {
    case 0:return native?modern_GAME_ERASE(r):reference_GAME_ERASE(r);
    case 1:return native?modern_GAME_DRAW(r):reference_GAME_DRAW(r);
    case 2:return native?modern_GAME_OVERLAY(r):reference_GAME_OVERLAY(r);
    case 3:return native?modern_DEMO_ERASE(r):reference_DEMO_ERASE(r);
    case 4:return native?modern_DEMO_DRAW(r):reference_DEMO_DRAW(r);
    default:return native?modern_RESET(r):reference_RESET(r);
    }
}
static int regs_equal(Regs a,Regs b) {
    return a.ax==b.ax && a.bx==b.bx && a.cx==b.cx && a.dx==b.dx && a.si==b.si && a.di==b.di && a.bp==b.bp && a.sp==b.sp && a.cs==b.cs && a.ds==b.ds && a.es==b.es && a.ss==b.ss && a.ip==b.ip && a.flags==b.flags;
}
static void compare(unsigned op,Regs initial) {
    uint16_t before[10],after[10];for(unsigned i=0;i<10;i++) before[i]=ram[i];
    operation=op;initial.si=actor_index;initial.ds=DATA_SEG;initial.cs=GAME_SEG;
    /* Reset's enclosing actual shell has already installed this constant. */
    if(op==5) initial.ax=65535u;
    Regs left=initial,right=initial;modern=0;observations=calls=0;
    int a=execute(op,&left,0);expected_observations=observations;
    for(unsigned i=0;i<10;i++) {after[i]=ram[i];ram[i]=before[i];}
    modern=1;observations=calls=0;int b=execute(op,&right,1);
    CHECK(a==b,"same normal/abnormal return");CHECK(regs_equal(left,right),"all machine registers and flags");
    CHECK(observations==expected_observations,"no unconsumed event");
    for(unsigned i=0;i<10;i++) CHECK(ram[i]==after[i],"all current-slot words and histories");
    comparisons++;
}
#ifndef __CPROVER__
static unsigned random_word=0x736ce921u;
static uint16_t word(void) {random_word^=random_word<<13;random_word^=random_word>>17;random_word^=random_word<<5;return (uint16_t)random_word;}
static Regs seed(void) {
    Regs r={0};r.ax=word();r.bx=word();r.cx=word();r.dx=word();r.si=word();r.di=word();r.bp=word();r.sp=word();r.cs=GAME_SEG;r.ds=DATA_SEG;r.es=word();r.ss=word();r.ip=word();r.flags=word();
    for(unsigned i=0;i<10;i++) ram[i]=word();
    for(unsigned i=0;i<2;i++) {service_after[i]=r;service_after[i].ax=word();service_after[i].bx=word();service_after[i].cx=word();service_after[i].dx=word();service_after[i].flags=word();service_after[i].bp=word();service_after[i].di=word();service_status[i]=0;}
    actor_index=(uint16_t)(2*(word()%16));return r;
}
int main(void) {
    /* Every raw word in complete slices; not a full Cartesian enumeration. */
    for(unsigned slice=0;slice<8;slice++) for(unsigned v=0;v<65536;v++) {
        random_word=0x736ce921u+slice;
        Regs r=seed();ram[2]=31;ram[3]=63;ram[8]=31;ram[9]=63;
        ram[6]=100;ram[7]=106;
        unsigned op=slice<2?1:slice<4?4:slice<6?0:3;
        unsigned field=slice==0||slice==2?0:slice==1||slice==3?1:slice==4||slice==6?7:8;
        ram[field]=(uint16_t)v;compare(op,r);
    }
    const uint16_t edges[]={0,1,0xffff,0x7fff,0x8000,0xfff4,0xfff5,0xfff6,191,192,193,319,320,321};
    for(unsigned op=0;op<6;op++) for(unsigned sprite=0;sprite<4;sprite++) for(unsigned erase=0;erase<4;erase++) for(unsigned overlay=0;overlay<4;overlay++) for(unsigned x=0;x<14;x++) for(unsigned y=0;y<14;y++) {
        Regs r=seed();ram[2]=edges[sprite];ram[8]=edges[erase];ram[3]=ram[9]=edges[overlay];ram[0]=(uint16_t)(edges[x]*32u);ram[1]=(uint16_t)(edges[y]*32u);ram[4]=ram[6]=edges[x];ram[5]=ram[7]=edges[y];compare(op,r);
    }
    for(unsigned n=0;n<16000;n++) for(unsigned op=0;op<6;op++) {Regs r=seed();if(n&1u) service_status[0]=UGH_UNSUPPORTED;compare(op,r);}
    printf("PASS %llu slot comparisons\n",comparisons);return 0;
}
#endif
