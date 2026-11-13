#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint8_t ram[65568];
uint8_t ugh_read(uint32_t address) { if(address>=sizeof ram) abort();return ram[address]; }
void ugh_write(uint32_t address,uint8_t value) { if(address>=sizeof ram) abort();ram[address]=value; }
static void position(uint16_t x,uint16_t y,unsigned index,ObjectPosition value) {
    wr16(0,(uint16_t)(x+index),value.x32);wr16(0,(uint16_t)(y+index),value.y32);
}
static int reference(Regs *r,unsigned kind) {
    if(kind==0) return l1_FindPlayerTouchingFallingItem(r);
    if(kind==1) return l1_FindPlayerTouchingActor(r);
    if(kind==2) return l1_FindPlayerTouchingEnemy(r);
    return l1_FindThrownStoneHittingEnemy(r);
}
static int modern(Regs *r,unsigned kind) {
    if(kind==0) return c_FindPlayerTouchingFallingItem(r);
    if(kind==1) return c_FindPlayerTouchingActor(r);
    if(kind==2) return c_FindPlayerTouchingEnemy(r);
    return c_FindThrownStoneHittingEnemy(r);
}
static unsigned long long checks;
static void compare(unsigned kind,unsigned value) {
    Regs a={0x1234,0,0x5678,0x9abc,256,0xdead,0x4567,0x8000,0x13b,0,0x7654,0x5432,0x4567,(uint16_t)value};
    Regs b=a;int x=reference(&a,kind),y=modern(&b,kind);
    if(x!=y || memcmp(&a,&b,sizeof a)) {
        fprintf(stderr,"kind=%u value=%u AX=%04x/%04x DI=%04x/%04x flags=%04x/%04x\n",kind,value,a.ax,b.ax,a.di,b.di,a.flags,b.flags);exit(23);
    }
    checks++;
}
static void setup(unsigned kind,ObjectGeometry g,ObjectPosition object) {
    uint16_t xb=kind==0?D(FallingItemX):kind==1?D(ActorX32):D(EnemyX32);
    uint16_t yb=kind==0?D(FallingItemY):kind==1?D(ActorY32):D(EnemyY32);
    position(xb,yb,0,object);
    wr16(0,256,g.anchor_x);wr16(0,258,g.anchor_y);wr16(0,260,g.extent_x);wr16(0,262,g.extent_y);
    wr16(0,D(PlayerPlatformIndices),0xffff);wr16(0,D(PlayerPlatformIndices)+2,0x8000);
    wr16(0,D(PlayerCount),1);
}
int main(void) {
    static const ObjectGeometry geometries[]={
        {8,11,4,5},{16,22,9,10},{0,0,0,0},{65535,32768,65535,32768},
        {1024,1024,1024,1024},{32767,32767,32767,32767}};
    static const ObjectPosition objects[]={{1024,2048},{0,0},{32767,32768},{65535,65535},{32768,32767},{65504,32}};
    for(unsigned kind=0;kind<3;kind++) {
        for(unsigned k=0;k<6;k++) {
            ObjectGeometry g=geometries[k];ObjectPosition object=objects[k];setup(kind,g,object);
            if(kind==0) { g.extent_x=3;g.extent_y=3; }
            /* Hold the other coordinate on the inclusive upper edge. Full
             * word domain per axis; wrapped/reversed intervals stay reversed. */
            ObjectPosition p={(uint16_t)((g.anchor_x+g.extent_x)*32u+object.x32-160u),
                              (uint16_t)(g.anchor_y*32u+object.y32)};
            for(unsigned axis=0;axis<2;axis++) {
                for(unsigned v=0;v<65536u;v++) {
                    ObjectPosition probe=p;if(axis) probe.y32=(uint16_t)v;else probe.x32=(uint16_t)v;
                    position(D(PlayerX32),D(PlayerY32),0,probe);compare(kind,v);
                }
            }
        }
        /* Every count bit pattern: first misses, second hits. This catches the
         * equality retry and verifies all incoming flags using count as seed. */
        setup(kind,geometries[0],objects[0]);
        position(D(PlayerX32),D(PlayerY32),0,(ObjectPosition){30000,30000});
        position(D(PlayerX32),D(PlayerY32),2,(ObjectPosition){1024,2048});
        for(unsigned v=0;v<65536u;v++) { wr16(0,D(PlayerCount),(uint16_t)v);compare(kind,v); }
    }
    /* Stone eligibility, scan priority/sentinel, signed vertical-step endpoints,
     * and coordinate sweeps of every word against fixed enemy geometry. */
    for(unsigned axis=0;axis<2;axis++) {
        wr16(0,D(ActorDescriptors),D(Data_78DC));wr16(0,D(ActorDescriptors)+2,65535);
        wr16(0,D(ActorUpdateOrScriptCursor),G(UpdateThrownStone));wr16(0,D(ActorVerticalOrDemoPeriod),0);
        position(D(EnemyX32),D(EnemyY32),0,(ObjectPosition){1000,2000});
        for(unsigned v=0;v<65536u;v++) {
            position(D(ActorX32),D(ActorY32),0,(ObjectPosition){axis?1000:(uint16_t)v,axis?(uint16_t)v:2000});compare(3,v);
        }
    }
    for(unsigned v=0;v<65536u;v++) {
        position(D(ActorX32),D(ActorY32),0,(ObjectPosition){1000,2000});
        wr16(0,D(ActorVerticalOrDemoPeriod),(uint16_t)v);compare(3,v);
    }
    for(unsigned i=0;i<16;i++) {
        wr16(0,D(ActorDescriptors)+2*i,D(Data_78DC));wr16(0,D(ActorDescriptors)+2*i+2,65535);
        wr16(0,D(ActorUpdateOrScriptCursor)+2*i,G(UpdateThrownStone));wr16(0,D(ActorVerticalOrDemoPeriod)+2*i,0);
        position(D(ActorX32),D(ActorY32),2*i,(ObjectPosition){1000,2000});compare(3,i);
        wr16(0,D(ActorUpdateOrScriptCursor)+2*i,0);compare(3,i);
    }
#if PAIRS
    /* Complete Cartesian word-coordinate domain, all other inputs fixed.
     * Real compiled L1 vs native core (bridge shell covered above); no samples,
     * rectangle factorization, model replacement or skipped iterations. */
    ObjectGeometry pair_geometry=geometries[PAIR_CASE?3:0];
    ObjectPosition pair_object=objects[PAIR_CASE?2:0];
    if(PAIR_KIND==3) {
        wr16(0,D(ActorDescriptors),D(Data_78DC));wr16(0,D(ActorDescriptors)+2,65535u);
        wr16(0,D(ActorUpdateOrScriptCursor),G(UpdateThrownStone));wr16(0,D(ActorVerticalOrDemoPeriod),0);
        position(D(ActorX32),D(ActorY32),0,pair_object);
    } else {
        setup(PAIR_KIND,pair_geometry,pair_object);
        if(PAIR_KIND==0) { pair_geometry.extent_x=3;pair_geometry.extent_y=3; }
    }
    for(unsigned y=0;y<65536u;y++) {
        wr16(0,PAIR_KIND==3?D(EnemyY32):D(PlayerY32),(uint16_t)y);
        for(unsigned x=0;x<65536u;x++) {
            wr16(0,PAIR_KIND==3?D(EnemyX32):D(PlayerX32),(uint16_t)x);
            Regs r={0};r.si=256;
            int status=reference(&r,PAIR_KIND);
            ObjectPosition point={(uint16_t)x,(uint16_t)y};
            ContactProbe p=PAIR_KIND==3?contact_stone(pair_object,point):contact_player(pair_object,pair_geometry,point);
            /* Stone miss scratch is the final sentinel; actor hit scratch is
             * the selected platform, other player entries return boundary. */
            uint16_t expected=PAIR_KIND==3 && !p.touching?65535u:PAIR_KIND==1 && p.touching?65535u:p.boundary;
            if(status || (r.di==0)!=p.touching || r.ax!=expected) { fprintf(stderr,"pair %u,%u\n",x,y);return 23; }
            checks++;
        }
        if(y%8192u==0) { fprintf(stderr,"pairs row %u/65536\n",y);fflush(stderr); }
    }
#endif
    printf("{\"checks\":%llu,\"pairs\":%d}\n",checks,PAIRS);return 0;
}
