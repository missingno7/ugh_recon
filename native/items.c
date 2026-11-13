#include "items.h"
static int32_t item_signed(uint16_t value) {
    return value<32768u ? (int32_t)value : (int32_t)value-65536;
}
static uint16_t item_pixels(uint16_t value) {
    return (uint16_t)((value>>5) | ((value&32768u)?63488u:0u));
}
ItemSpawnResult items_spawn(FallingItem items[12], FallingItemType type,
    ObjectPosition launch, uint16_t horizontal, uint16_t launch_term) {
    ItemSpawnResult result={ITEM_POOL_FULL,-1};
    for(int i=11;i>=0;i--) {
        /* Retained allocator/dispatcher disagreement on negative sprite IDs. */
        if(!(items[i].sprite&32768u)) continue;
        FallingItem *item=&items[i];
        item->type=type; item->phase=ITEM_FLIGHT;
        item->position.x32=(uint16_t)(launch.x32-type.geometry.anchor_x*32u);
        /* Spawn height is half scale, deliberately unlike landing height. */
        item->position.y32=(uint16_t)(launch.y32-type.geometry.anchor_y*16u);
        item->motion_or_lifetime=horizontal;
        item->vertical_step=(uint16_t)(0u-(uint16_t)(launch_term+type.launch_impulse));
        item->sprite=type.sprite;
        result.status=ITEM_SPAWNED;result.slot=i;return result;
    }
    return result; /* No normal DOS failure return is implied. */
}
void item_land(FallingItem *item) {
    item->phase=ITEM_LANDED;item->motion_or_lifetime=560;
}
ItemFlightResult item_advance(FallingItem *item,const LevelPlatform *platforms,size_t count) {
    ItemFlightResult result={ITEM_OUT_LEFT,0,-1,0};
    uint16_t x=(uint16_t)(item->position.x32+item->motion_or_lifetime);
    if(item_signed(x)<=-512) { item->sprite=65535u;return result; }
    result.exit=ITEM_OUT_RIGHT;
    if(item_signed(x)>=10240) { item->sprite=65535u;return result; }
    item->position.x32=x;
    item->vertical_step=(uint16_t)(item->vertical_step+3u);
    uint16_t old_y=item->position.y32;
    uint16_t y=(uint16_t)(old_y+item->vertical_step);
    result.exit=ITEM_RISING;
    if(item_signed(item->vertical_step)<0) { item->position.y32=y;return result; }
    result.exit=ITEM_OUT_BOTTOM;
    if(item_signed(y)>=6144) { item->sprite=65535u;return result; }
    item->position.y32=y;
    uint16_t bottom=(uint16_t)(item_pixels(y)+item->type.geometry.anchor_y);
    uint16_t old_bottom=(uint16_t)(item_pixels(old_y)+item->type.geometry.anchor_y);
    result.exit=ITEM_FLYING;result.platform=count;
    for(size_t i=0;i<count;i++) {
        const LevelPlatform *p=&platforms[i];
        if(item_signed(old_bottom)>=item_signed(p->surface_y) ||
           item_signed(bottom)<item_signed(p->surface_y)) continue;
        uint16_t center=(uint16_t)(item_pixels(x)+item->type.geometry.anchor_x);
        result.horizontal_platform=(int)i;result.right_tested=0;
        if(item_signed(center)<item_signed(p->left)) continue;
        center=(uint16_t)(center-1u);result.right_tested=1;
        if(item_signed(center)>item_signed(p->right)) continue;
        item->position.y32=(uint16_t)((uint16_t)(p->surface_y-item->type.geometry.anchor_y)*32u);
        item_land(item);result.exit=ITEM_TOUCHDOWN;result.platform=i;return result;
    }
    return result;
}
ItemCollectionResult item_collect(FallingItem *item,const ObjectPosition players[2],
    uint16_t player_count,ItemBenefits *benefits) {
    ItemCollectionResult result={0,0,{-1,0}};
    item->motion_or_lifetime=(uint16_t)(item->motion_or_lifetime-1u);
    if(!item->motion_or_lifetime) { result.expired=1;item->sprite=65535u;return result; }
    result.contact=contact_players(item->position,item->type.geometry,players,player_count);
    if(result.contact.index<0) return result;
    result.collected=1;
    if(item->type.benefit==ITEM_TIMER) {
        /* Retained wrap BEFORE unsigned cap. */
        uint16_t sum=(uint16_t)(benefits->timer+item->type.amount);
        benefits->timer=sum>23099u?23099u:sum;
    } else if(item->type.benefit==ITEM_LIVES) {
        uint8_t sum=(uint8_t)(benefits->lives+(uint8_t)item->type.amount);
        benefits->lives=sum>99u?99u:sum;
    } else if(benefits->multiplier<benefits->multiplier_limit) {
        /* Word comparison, byte increment/store, stale high byte retained. */
        benefits->multiplier=(uint16_t)((benefits->multiplier&65280u)|
            (uint8_t)((uint8_t)benefits->multiplier+1u));
    }
    item->sprite=65535u;return result;
}
int items_next(const FallingItem items[12],size_t *cursor) {
    while(*cursor) {
        --*cursor;
        if(items[*cursor].sprite!=65535u) return (int)*cursor;
    }
    return -1;
}
ItemUpdateResult item_update(FallingItem *item,const LevelPlatform *platforms,size_t count,
    const ObjectPosition players[2],uint16_t player_count,ItemBenefits *benefits) {
    ItemUpdateResult result={0};
    if(item->phase==ITEM_FLIGHT) result.flight=item_advance(item,platforms,count);
    else result.collection=item_collect(item,players,player_count,benefits);
    return result;
}
void items_dispatch(FallingItem items[12],const LevelPlatform *platforms,size_t count,
    const ObjectPosition players[2],uint16_t player_count,ItemBenefits *benefits) {
    size_t cursor=12;int selected;
    while((selected=items_next(items,&cursor))>=0)
        item_update(&items[selected],platforms,count,players,player_count,benefits);
}
