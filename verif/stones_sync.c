#include <stdio.h>
#include "stones.h"
#include "hazards.h"
#define CHECK(c) do {if(!(c)) {fprintf(stderr,"sync failure line %d\n",__LINE__);return 23;}} while(0)
static void borrow(HazardWorld *world,PassengerStoneSlot slots[3]) {
    world->stone_count=3;
    for(unsigned i=0;i<3;i++) {
        world->stones[i].contact=stone_contact_view(&slots[i]);world->stones[i].sprite=slots[i].sprite;
        uint16_t horizontal=0;
        if(slots[i].phase==ACTOR_THROWN_STONE) actor_alias_value(&slots[i],ACTOR_ALIAS_HORIZONTAL_STEP,&horizontal);
        world->stones[i].horizontal_step=horizontal;
    }
}
static int apply(PassengerStoneSlot slots[3],const HazardResult *result) {
    for(size_t i=0;i<result->count;i++) {
        HazardWrite write=result->writes[i];
        if(write.field==HW_STONE_VERTICAL) {
            if(write.index!=1) return 0;
            slots[write.index].vertical_motion=write.value;
        } else if(write.field==HW_STONE_SPRITE) slots[write.index].sprite=write.value;
    }
    return 1;
}
int main(void) {
    ActorType primary={0},alternate={0};primary.id=ACTOR_STONE;alternate.id=ACTOR_STONE_ALTERNATE;
    PassengerStoneSlot slots[3]={{0}};
    for(unsigned i=0;i<3;i++) {slots[i].type=i?&primary:&alternate;slots[i].phase=ACTOR_THROWN_STONE;slots[i].position=(ObjectPosition){1000,1000};slots[i].sprite=545;}
    /* Actor updates precede hazards. Both primary stones overlap the same
     * target; physical slot one must win over slot two and alternate zero. */
    for(unsigned i=0;i<3;i++) CHECK(stone_flight(&slots[i],0,0).exit==STONE_STILL);
    HazardWorld world={0};world.player_count=1;world.players[0].position=(ObjectPosition){6000,6000};
    HazardSlot enemy={0};enemy.position=(ObjectPosition){1000,1000};enemy.animation_countdown=2;
    HazardType type={0};type.handlers[10]=H_TRIO_STUN;
    borrow(&world,slots);HazardResult first=hazard_step(H_TRIO_PATROL,&enemy,&type,&world,-1);
    CHECK(first.has_tail && first.tail==H_TRIO_STUN && apply(slots,&first));
    CHECK(slots[0].vertical_motion==2 && slots[1].vertical_motion==65534u && slots[2].vertical_motion==2 && slots[1].sprite==546);
    /* A second hazard in this frame must see the bounce immediately and
     * select slot two. Demonstrate actual native hazard/contact code. */
    borrow(&world,slots);enemy.animation_countdown=2;
    HazardResult second=hazard_step(H_TRIO_PATROL,&enemy,&type,&world,-1);int selected=-1;
    for(size_t i=0;i<second.count;i++) if(second.writes[i].field==HW_STONE_VERTICAL) selected=second.writes[i].index;
    CHECK(selected==2);
    /* The following actor update sees -2 + gravity 2, not an old +2 copy. */
    uint16_t y=slots[1].position.y32;CHECK(stone_flight(&slots[1],0,0).exit==STONE_STILL);
    CHECK(slots[1].vertical_motion==0 && slots[1].position.y32==y);
    puts("PASS actual native stone -> hazard -> hazard -> stone, alternate identity and ascending slot order");return 0;
}
