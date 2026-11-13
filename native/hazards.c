#include "hazards.h"

static int hazard_signed(uint16_t value) {
    return value < 32768u ? (int)value : (int)value - 65536;
}
static uint16_t hazard_sar(uint16_t value, unsigned bits) {
    return (uint16_t)((value >> bits) | ((value & 32768u) ? (65535u << (16-bits)) : 0));
}
static void hazard_store(HazardResult *result, HazardField field, unsigned index, uint16_t value) {
    HazardWrite *write = &result->writes[result->count++];
    write->field=field;write->index=(uint16_t)index;write->value=value;
}
static void hazard_state(HazardResult *result,HazardSlot *slot,HazardEntry state) {
    slot->state=state;hazard_store(result,HW_STATE,0,(uint16_t)state);
}
static void hazard_begin(HazardResult *result,HazardSlot *slot,HazardEntry state) {
    hazard_state(result,slot,state);
    slot->animation_cursor=65534u;hazard_store(result,HW_CURSOR,0,slot->animation_cursor);
    slot->animation_countdown=1;hazard_store(result,HW_TICK,0,1);
}
static void hazard_counter(HazardResult *result,HazardSlot *slot,uint16_t value) {
    slot->counter=value;hazard_store(result,HW_COUNTER,0,value);
}
static void hazard_tail(HazardResult *result,const HazardType *type,unsigned handler) {
    result->has_tail=1;result->tail=type->handlers[handler];
}
static int hazard_tick(HazardResult *result,HazardSlot *slot,uint16_t period) {
    slot->animation_countdown--;hazard_store(result,HW_TICK,0,slot->animation_countdown);
    if(slot->animation_countdown) return 0;
    slot->animation_countdown=period;hazard_store(result,HW_TICK,0,period);
    slot->animation_cursor=(uint16_t)(slot->animation_cursor+2u);
    hazard_store(result,HW_CURSOR,0,slot->animation_cursor);return 1;
}
static void hazard_frame(HazardResult *result,HazardSlot *slot,HazardAnimation animation) {
    uint16_t sprite=animation.next;
    if(sprite==65535u) {
        slot->animation_cursor=0;hazard_store(result,HW_CURSOR,0,0);sprite=animation.first;
    }
    slot->sprite=sprite;hazard_store(result,HW_SPRITE,0,sprite);
}
static void hazard_score(HazardResult *result,const HazardType *type,HazardWorld *world) {
    world->score+=type->score;
    hazard_store(result,HW_SCORE_LOW,0,(uint16_t)world->score);
    hazard_store(result,HW_SCORE_HIGH,0,(uint16_t)(world->score>>16));
}
static int hazard_platform_player(const HazardSlot *slot,const HazardWorld *world) {
    for(unsigned i=0;i<world->player_slots;i++) if(slot->platform==world->players[i].platform) return (int)i;
    return -1;
}
static void hazard_face(HazardResult *result,HazardSlot *slot,const HazardPlayer *player) {
    slot->direction=hazard_signed(slot->position.x32)<hazard_signed(player->position.x32)?2:0;
    if((slot->direction==2 && hazard_signed(slot->speed)<0) ||
       (!slot->direction && hazard_signed(slot->speed)>=0)) slot->speed=(uint16_t)(0u-slot->speed);
    hazard_store(result,HW_DIRECTION,0,slot->direction);hazard_store(result,HW_SPEED,0,slot->speed);
}
static int hazard_stone(HazardResult *result,HazardSlot *slot,const HazardType *type,HazardWorld *world,int sprite,int tree) {
    StoneContactView stones[16];
    for(size_t i=0;i<world->stone_count;i++) stones[i]=world->stones[i].contact;
    int index=contact_stones(stones,world->stone_count,slot->position).index;
    if(index<0) return -1;
    HazardStone *stone=&world->stones[index];
    stone->contact.vertical_step=(uint16_t)(0u-stone->contact.vertical_step);
    if(tree) stone->contact.vertical_step=hazard_sar(stone->contact.vertical_step,1);
    hazard_store(result,HW_STONE_VERTICAL,(unsigned)index,stone->contact.vertical_step);
    if(sprite) { stone->sprite=546;hazard_store(result,HW_STONE_SPRITE,(unsigned)index,stone->sprite); }
    hazard_tail(result,type,10);return index;
}
static int hazard_player(const HazardSlot *slot,const HazardType *type,const HazardWorld *world) {
    ObjectPosition players[2]={world->players[0].position,world->players[1].position};
    return contact_players(slot->position,type->geometry,players,world->player_count).index;
}
static int hazard_out(uint16_t x) { return hazard_signed(x)<=-1024 || hazard_signed(x)>=10240; }

HazardResult hazard_step(HazardEntry entry,HazardSlot *slot,const HazardType *type,HazardWorld *world,int incoming_stone) {
    HazardResult result={0};
    unsigned direction=slot->direction/2u;
    switch(entry) {
    /* A zero descriptor word requests the explicit noninstruction boundary;
     * it must never become a successful empty state in a native dispatcher. */
    case H_ZERO: result.has_tail=1;result.tail=H_ZERO;break;
    case H_IGNORE: case H_TREE_EMPTY: break;
    case H_BIRD_STOP: result.audio=HA_STOP;result.audio_handle=slot->flight_sound;break;
    case H_BIRD_DELAY:
        hazard_begin(&result,slot,type->handlers[1]);slot->sprite=65535u;
        hazard_store(&result,HW_SPRITE,0,slot->sprite);hazard_counter(&result,slot,slot->initial_delay);break;
    case H_BIRD_WAIT: case H_BIRD_WARN_WAIT: case H_DINO_STUNNED:
        hazard_counter(&result,slot,(uint16_t)(slot->counter-1u));
        if(!slot->counter) hazard_tail(&result,type,entry==H_BIRD_WAIT?2:entry==H_BIRD_WARN_WAIT?4:4);
        break;
    case H_BIRD_WARNING:
        hazard_state(&result,slot,type->handlers[3]);hazard_counter(&result,slot,70);result.audio=HA_WARNING;break;
    case H_BIRD_LAUNCH: {
        uint16_t target=(uint16_t)(slot->direction^1u);
        if(hazard_signed(target)>=hazard_signed(world->player_count)) target=0;
        slot->direction=target;hazard_store(&result,HW_DIRECTION,0,target);
        const HazardPlayer *player=&world->players[target];
        int left=hazard_signed(player->position.x32)<5120;
        if((left && hazard_signed(slot->speed)>=0) || (!left && hazard_signed(slot->speed)<0)) {
            slot->speed=(uint16_t)(0u-slot->speed);hazard_store(&result,HW_SPEED,0,slot->speed);
        }
        slot->position.x32=left?10208:64544;hazard_store(&result,HW_X,0,slot->position.x32);
        slot->flight_side=left?H_FLIGHT_LEFT:H_FLIGHT_RIGHT;
        hazard_store(&result,HW_LIST,0,(uint16_t)slot->flight_side);
        uint16_t y=(uint16_t)(player->position.y32+832u);
        if(hazard_signed(y)>hazard_signed(world->water_y32)) y=world->water_y32;
        y=(uint16_t)(y-832u);if(hazard_signed(y)<-128) y=65408;
        slot->position.y32=y;hazard_store(&result,HW_Y,0,y);
        hazard_state(&result,slot,type->handlers[5]);result.audio=HA_FLIGHT;break;
    }
    case H_BIRD_STUN:
        hazard_state(&result,slot,type->handlers[11]);hazard_score(&result,type,world);hazard_counter(&result,slot,0);
        slot->sprite=type->animations[hazard_signed(slot->speed)<0?10:11].first;
        hazard_store(&result,HW_SPRITE,0,slot->sprite);break;
    case H_BIRD_FALL: {
        uint16_t x=(uint16_t)(slot->position.x32+slot->speed);
        if(hazard_out(x)) { hazard_tail(&result,type,0);break; }
        slot->position.x32=x;hazard_store(&result,HW_X,0,x);
        if(hazard_signed(slot->counter)<40) hazard_counter(&result,slot,(uint16_t)(slot->counter+1u));
        uint16_t y=(uint16_t)(slot->position.y32+slot->counter);
        if(hazard_signed(y)>=6144) { hazard_tail(&result,type,0);break; }
        slot->position.y32=y;hazard_store(&result,HW_Y,0,y);break;
    }
    case H_BIRD_FLIGHT: {
        uint16_t x=(uint16_t)(slot->position.x32+slot->speed);
        if(hazard_out(x)) { result.audio=HA_STOP;result.audio_handle=slot->flight_sound;hazard_tail(&result,type,0);break; }
        slot->position.x32=x;hazard_store(&result,HW_X,0,x);
        if(!hazard_tick(&result,slot,4)) break;
        hazard_frame(&result,slot,type->flight);
        /* Stop the flight sound before reflecting the stone and selecting stun. */
        int stone=hazard_stone(&result,slot,type,world,1,0);
        if(stone>=0) { result.audio=HA_STOP;result.audio_handle=slot->flight_sound;break; }
        int player=hazard_player(slot,type,world);
        if(player>=0 && (unsigned)player==slot->direction && hazard_signed(world->fade_step)>=0) {
            world->fade_step=65534u;hazard_store(&result,HW_FADE_STEP,0,world->fade_step);
            world->fade_level=(uint16_t)(world->fade_level-2u);hazard_store(&result,HW_FADE_LEVEL,0,world->fade_level);
        }
        break;
    }
    case H_TRIO_PATROL_BEGIN: case H_TRIO_ALERT_BEGIN: case H_TRIO_CHARGE_BEGIN:
    case H_TRIO_RECOVER_BEGIN: case H_TRIO_IMPACT_BEGIN: case H_DINO_BEGIN: case H_TREE_BEGIN: {
        unsigned handler=entry==H_TRIO_PATROL_BEGIN||entry==H_TREE_BEGIN?1:entry==H_TRIO_ALERT_BEGIN?3:
            entry==H_TRIO_CHARGE_BEGIN||entry==H_DINO_BEGIN?5:7;
        /* DOS impact installs ordinary recovery (+16); never the nominal +1A. */
        hazard_begin(&result,slot,type->handlers[handler]);
        if(entry==H_TRIO_ALERT_BEGIN) hazard_counter(&result,slot,140);
        if(entry==H_TRIO_CHARGE_BEGIN) hazard_counter(&result,slot,0);
        if(entry==H_TREE_BEGIN) {
            slot->draw_x=(uint16_t)(slot->position.x32<<5);hazard_store(&result,HW_DRAW_X,0,slot->draw_x);
            slot->draw_y=(uint16_t)(slot->position.y32<<5);hazard_store(&result,HW_DRAW_Y,0,slot->draw_y);
        }
        break;
    }
    case H_TRIO_STUN:
        hazard_state(&result,slot,type->handlers[11]);hazard_score(&result,type,world);
        slot->animation_cursor=65534u;hazard_store(&result,HW_CURSOR,0,slot->animation_cursor);
        slot->animation_countdown=1;hazard_store(&result,HW_TICK,0,1);hazard_counter(&result,slot,350);break;
    case H_TRIO_STUNNED:
        hazard_counter(&result,slot,(uint16_t)(slot->counter-1u));
        if(!slot->counter) { hazard_tail(&result,type,0);break; }
        if(hazard_tick(&result,slot,4)) hazard_frame(&result,slot,type->animations[10+direction]);
        break;
    case H_DINO_STUN:
        hazard_state(&result,slot,type->handlers[11]);hazard_score(&result,type,world);hazard_counter(&result,slot,350);
        slot->sprite=type->animations[10].first;hazard_store(&result,HW_SPRITE,0,slot->sprite);break;
    case H_TRIO_PATROL: {
        slot->animation_countdown--;hazard_store(&result,HW_TICK,0,slot->animation_countdown);
        if(!slot->animation_countdown) {
            slot->position.x32=(uint16_t)(slot->position.x32+slot->speed);hazard_store(&result,HW_X,0,slot->position.x32);
            uint16_t pixel=hazard_sar(slot->position.x32,5);
            const LevelPlatform *platform=&world->platforms[slot->platform];
            if(hazard_signed(pixel)<hazard_signed(platform->left) || hazard_signed((uint16_t)(pixel+32u))>=hazard_signed(platform->right)) {
                slot->speed=(uint16_t)(0u-slot->speed);hazard_store(&result,HW_SPEED,0,slot->speed);
                slot->direction^=2u;hazard_store(&result,HW_DIRECTION,0,slot->direction);
            }
            slot->animation_countdown=4;hazard_store(&result,HW_TICK,0,4);
            slot->animation_cursor=(uint16_t)(slot->animation_cursor+2u);hazard_store(&result,HW_CURSOR,0,slot->animation_cursor);
            hazard_frame(&result,slot,type->animations[slot->direction/2u]);
        }
        if(hazard_platform_player(slot,world)>=0) hazard_tail(&result,type,2);
        else hazard_stone(&result,slot,type,world,1,0);
        break;
    }
    case H_TRIO_ALERT: case H_TRIO_CHARGE: {
        if(entry==H_TRIO_ALERT) {
            hazard_counter(&result,slot,(uint16_t)(slot->counter-1u));
            if(!slot->counter) { hazard_tail(&result,type,4);break; }
        }
        if(hazard_tick(&result,slot,entry==H_TRIO_ALERT?5:4))
            hazard_frame(&result,slot,type->animations[(entry==H_TRIO_ALERT?6:2)+direction]);
        if(hazard_stone(&result,slot,type,world,1,0)>=0) break;
        int player=hazard_platform_player(slot,world);
        if(player<0) { hazard_tail(&result,type,entry==H_TRIO_ALERT?0:6);break; }
        hazard_face(&result,slot,&world->players[player]);
        if(entry==H_TRIO_ALERT) break;
        hazard_counter(&result,slot,(uint16_t)(slot->counter+slot->direction-1u));
        slot->position.x32=(uint16_t)(slot->position.x32+slot->speed+slot->counter);
        hazard_store(&result,HW_X,0,slot->position.x32);
        player=hazard_player(slot,type,world);if(player<0) break;
        HazardPlayer *craft=&world->players[player];
        craft->position.y32=(uint16_t)(craft->position.y32-32u);hazard_store(&result,HW_PLAYER_Y,(unsigned)player,craft->position.y32);
        uint16_t kick=(uint16_t)(slot->speed+slot->counter);
        craft->horizontal_velocity=(uint16_t)(kick<<5);hazard_store(&result,HW_PLAYER_HORIZONTAL,(unsigned)player,craft->horizontal_velocity);
        craft->vertical_velocity=(uint16_t)(kick<<4);hazard_store(&result,HW_PLAYER_VERTICAL,(unsigned)player,craft->vertical_velocity);
        craft->platform=65535u;hazard_store(&result,HW_PLAYER_PLATFORM,(unsigned)player,craft->platform);
        hazard_tail(&result,type,8);break;
    }
    case H_TRIO_RECOVER: case H_TRIO_IMPACT:
        if(hazard_tick(&result,slot,4)) {
            uint16_t sprite=type->animations[(entry==H_TRIO_IMPACT?8:4)+direction].next;
            if(sprite==65535u) { hazard_tail(&result,type,0);break; }
            slot->sprite=sprite;hazard_store(&result,HW_SPRITE,0,sprite);
        }
        hazard_stone(&result,slot,type,world,1,0);break;
    case H_DINO_FORCE: {
        if(hazard_tick(&result,slot,15)) {
            if(slot->animation_cursor==6) result.audio=HA_DINO;
            hazard_frame(&result,slot,type->animations[2]);
        }
        /* DOS retries only when next byte index equals PlayerCount: one craft
         * for count=1, both for count=2. This is not PlayerArrayBytes. */
        for(unsigned i=0;i<(world->player_count==2?2u:1u);i++) {
            HazardPlayer *craft=&world->players[i];
            uint16_t top=(uint16_t)(slot->position.y32+((type->geometry.anchor_y-30u)<<5));
            uint16_t bottom=(uint16_t)(slot->position.y32+((type->geometry.anchor_y-9u)<<5));
            uint16_t right=(uint16_t)(slot->position.x32+((type->geometry.anchor_x-16u)<<5));
            uint16_t left=(uint16_t)(slot->position.x32+((type->geometry.anchor_x-104u)<<5)-832u);
            if(hazard_signed(bottom)<hazard_signed(craft->position.y32) || hazard_signed(top)>hazard_signed(craft->position.y32) ||
               hazard_signed(right)<hazard_signed(craft->position.x32) || hazard_signed(left)>hazard_signed(craft->position.x32)) continue;
            craft->horizontal_velocity=(uint16_t)(craft->horizontal_velocity+(hazard_signed(slot->animation_cursor)<5?41u:65495u));
            hazard_store(&result,HW_PLAYER_HORIZONTAL,i,craft->horizontal_velocity);
        }
        hazard_stone(&result,slot,type,world,0,0);break;
    }
    case H_TREE_ANIMATE:
        if(hazard_tick(&result,slot,6)) {
            hazard_frame(&result,slot,type->animations[0]);hazard_stone(&result,slot,type,world,1,1);
        }
        break;
    case H_TREE_RELEASE: {
        hazard_state(&result,slot,type->handlers[11]);hazard_counter(&result,slot,210);
        slot->sprite=232;hazard_store(&result,HW_SPRITE,0,slot->sprite);
        const HazardStone *stone=&world->stones[incoming_stone];
        result.spawn_item=1;result.spawn_reward=slot->reward_cursor;result.launch=stone->contact.position;result.launch_horizontal=stone->horizontal_step;
        result.launch_term=hazard_sar((uint16_t)(0u-stone->contact.vertical_step),2);
        slot->reward_cursor++;hazard_store(&result,HW_LIST,0,2);result.audio=HA_REWARD;break;
    }
    case H_TREE_COOLDOWN:
        hazard_counter(&result,slot,(uint16_t)(slot->counter-1u));
        if(!slot->counter) hazard_state(&result,slot,type->handlers[type->rewards_exhausted?12:1]);
        break;
    }
    return result;
}
int hazards_next(size_t count,size_t *cursor) {
    if(*cursor>=count) return -1;
    return (int)(*cursor)++;
}
