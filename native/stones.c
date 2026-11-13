#include "stones.h"
static int32_t stone_signed(uint16_t value) {
    return value<32768u ? (int32_t)value : (int32_t)value-65536;
}
static uint16_t stone_sar(uint16_t value) {
    return (uint16_t)((value>>5)|((value&32768u)?63488u:0));
}
void stone_begin_wait(PassengerStoneSlot *slot) {
    slot->phase=ACTOR_STONE_WAIT;
    slot->animation.byte_offset=65534u;slot->animation.countdown=1;
}
StoneResult stone_pickup_wait(PassengerStoneSlot *slot,const StonePlayer players[2],uint16_t player_count) {
    ObjectPosition positions[2]={players[0].position,players[1].position};
    StoneResult result={STONE_STILL,0,{-1,0}};
    result.contact=contact_players(slot->position,slot->type->geometry,positions,player_count);
    if(result.contact.index>=0 && players[result.contact.index].carried_kind==0) result.exit=STONE_PICKUP;
    else slot->sprite=544;
    return result;
}
void stone_attach(PassengerStoneSlot *slot,StonePlayer players[2],size_t carrier) {
    slot->phase=ACTOR_CARRIED_STONE;slot->carrier=carrier;slot->sprite=ACTOR_HIDDEN_SPRITE;
    players[carrier].carried_kind=slot->type->carried_kind;players[carrier].destination_icon=7;
}
int stone_release_requested(const PassengerStoneSlot *slot,const StonePlayer players[2]) {
    uint16_t carrier;
    if(!actor_alias_value(slot,ACTOR_ALIAS_CARRIER,&carrier)) return 0;
    /* Retained byte TEST: the high action byte has no influence. */
    return (players[carrier].action_word&128u)!=0;
}
void stone_throw(PassengerStoneSlot *slot,StonePlayer players[2],size_t carrier) {
    StonePlayer *player=&players[carrier];
    player->carried_kind=0;player->destination_icon=0;
    slot->horizontal_step=stone_sar(player->horizontal_velocity);
    slot->vertical_motion=stone_sar(player->vertical_velocity);
    slot->position.x32=(uint16_t)(player->position.x32+512u-slot->type->geometry.anchor_x*32u);
    slot->position.y32=(uint16_t)(player->position.y32+320u-slot->type->geometry.anchor_y*16u);
    slot->sprite=545;slot->phase=ACTOR_THROWN_STONE;
}
StoneResult stone_flight(PassengerStoneSlot *slot,const LevelPlatform *platforms,size_t count) {
    StoneResult result={STONE_STILL,count,{-1,0}};uint16_t horizontal;
    if(!actor_alias_value(slot,ACTOR_ALIAS_HORIZONTAL_STEP,&horizontal)) return result;
    uint16_t x=(uint16_t)(slot->position.x32+horizontal);
    if(stone_signed(x)<=-512) {result.exit=STONE_OUT_LEFT;goto gone;}
    if(stone_signed(x)>=10240) {result.exit=STONE_OUT_RIGHT;goto gone;}
    slot->position.x32=x;
    slot->vertical_motion=(uint16_t)(slot->vertical_motion+2u);
    uint16_t previous_y=slot->position.y32;
    uint16_t y=(uint16_t)(previous_y+slot->vertical_motion);
    if(slot->vertical_motion&32768u) {
        slot->position.y32=y;result.exit=STONE_RISING;return result;
    }
    if(stone_signed(y)>=6144) {result.exit=STONE_OUT_BOTTOM;goto gone;}
    slot->position.y32=y;
    uint16_t bottom=(uint16_t)(stone_sar(y)+slot->type->geometry.anchor_y);
    uint16_t old_bottom=(uint16_t)(stone_sar(previous_y)+slot->type->geometry.anchor_y);
    for(size_t i=0;i<count;i++) {
        const LevelPlatform *platform=&platforms[i];
        /* Retained inclusive old/new surface crossing and both X edges.
         * Falling items have different rules; these are stone rules. */
        if(stone_signed(old_bottom)>stone_signed(platform->surface_y) ||
           stone_signed(bottom)<stone_signed(platform->surface_y)) continue;
        uint16_t center=(uint16_t)(stone_sar(x)+slot->type->geometry.anchor_x);
        if(stone_signed(center)<stone_signed(platform->left) ||
           stone_signed(center)>stone_signed(platform->right)) continue;
        slot->position.y32=(uint16_t)((platform->surface_y-slot->type->geometry.anchor_y)*32u);
        result.exit=STONE_LANDING;result.platform=i;return result;
    }
    return result;
gone:
    slot->sprite=ACTOR_HIDDEN_SPRITE;slot->phase=ACTOR_RETIRED;return result;
}
StoneContactView stone_contact_view(const PassengerStoneSlot *slot) {
    StoneContactView view={slot->position,slot->type->id==ACTOR_STONE && slot->phase==ACTOR_THROWN_STONE,slot->vertical_motion};
    return view;
}
