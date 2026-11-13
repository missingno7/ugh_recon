#include "ugh.h"
#include "../contacts.h"
#include "level_projection.h"
int l1_FindThrownStoneHittingEnemy(Regs *r);
static ObjectPosition contact_position(uint16_t segment,uint16_t x,uint16_t y,uint16_t index) {
    ObjectPosition result={rd16(segment,(uint16_t)(x+index)),rd16(segment,(uint16_t)(y+index))};
    return result;
}
static int player_bridge(Regs *r,uint16_t x,uint16_t y,int item,int actor) {
    ObjectPosition players[2];
    for(unsigned i=0;i<2;i++) players[i]=contact_position(r->ds,D(PlayerX32),D(PlayerY32),(uint16_t)(i*2));
    ObjectGeometry geometry=level_bridge_geometry(r->ds,r->si,item);
    ObjectPosition object=contact_position(r->ds,x,y,r->bx);
    uint16_t count=rd16(r->ds,D(PlayerCount));
    ContactSelection result=contact_players(object,geometry,players,count);
    r->ax=result.boundary;
    if(result.index>=0) {
        r->di=(uint16_t)(result.index*2);
        sub16(r,result.boundary,players[result.index].x32,0);
    } else {
        sub16(r,count==2?4:2,count,0);r->di=65535u;
    }
    logic(r,r->di,16);
    /* MOV after TEST preserves its flags, including SF from DI, not platform. */
    if(actor && result.index>=0) r->ax=rd16(r->ds,(uint16_t)(D(PlayerPlatformIndices)+r->di));
    return UGH_OK;
}
EXPORT int c_FindPlayerTouchingFallingItem(Regs *r) {
    return player_bridge(r,D(FallingItemX),D(FallingItemY),1,0);
}
EXPORT int c_FindPlayerTouchingActor(Regs *r) {
    return player_bridge(r,D(ActorX32),D(ActorY32),0,1);
}
EXPORT int c_FindPlayerTouchingEnemy(Regs *r) {
    return player_bridge(r,D(EnemyX32),D(EnemyY32),0,0);
}
EXPORT int c_FindThrownStoneHittingEnemy(Regs *r) {
    StoneContactView stones[16];size_t count=0;
    for(;;) {
        uint16_t index=(uint16_t)(count*2);
        uint16_t descriptor=rd16(r->ds,(uint16_t)(D(ActorDescriptors)+index));
        if(descriptor==65535u) break;
        /* Unbounded/corrupt sentinel walks remain explicit L1 compatibility. */
        if(count==16) return l1_FindThrownStoneHittingEnemy(r);
        stones[count].position=contact_position(r->ds,D(ActorX32),D(ActorY32),index);
        stones[count].thrown_stone=descriptor==D(Data_78DC) &&
            rd16(r->ds,(uint16_t)(D(ActorUpdateOrScriptCursor)+index))==G(UpdateThrownStone);
        stones[count].vertical_step=rd16(r->ds,(uint16_t)(D(ActorVerticalOrDemoPeriod)+index));
        count++;
    }
    ObjectPosition enemy=contact_position(r->ds,D(EnemyX32),D(EnemyY32),r->bx);
    ContactSelection result=contact_stones(stones,count,enemy);
    r->ax=result.boundary;
    r->di=result.index<0?65535u:(uint16_t)(result.index*2);
    sub16(r,result.index<0?65535u:result.boundary,result.index<0?65535u:enemy.x32,0);
    logic(r,r->di,16);return UGH_OK;
}
