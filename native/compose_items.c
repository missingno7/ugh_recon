#include "compose_objects.h"
#include "game_object_data.h"
#define TRY(call) do{GSStatus status=(call);if(status!=GS_OK)return status;}while(0)
static GSStatus item_type(GameServices *s,ObjectResourceIdentity id,FallingItemType *type){
    if(id.kind!=OBJECT_ITEM_DESCRIPTOR||id.position)return GS_UNSUPPORTED;
    uint16_t kind;
    TRY(game_object_word(s,id,0,&type->geometry.anchor_x));
    TRY(game_object_word(s,id,2,&type->geometry.anchor_y));
    type->geometry.extent_x=type->geometry.extent_y=3;
    TRY(game_object_word(s,id,12,&type->launch_impulse));
    TRY(game_object_word(s,id,14,&type->amount));
    TRY(game_object_word(s,id,16,&type->sprite));
    TRY(game_object_word(s,id,18,&kind));
    type->benefit=kind==0?ITEM_TIMER:kind==1?ITEM_LIVES:ITEM_MULTIPLIER;return GS_OK;
}
static GSStatus callback(GameWorld *w,size_t n,uint16_t member){
    ObjectGraphLink l;TRY(game_object_link(w->session.item_descriptor[n],member,&l));
    if(l.kind!=OBJECT_LINK_CALLBACK||l.callback.kind!=OBJECT_CALLBACK_ITEM)return GS_UNSUPPORTED;
    w->session.item_callback[n]=l.callback;return GS_OK;
}
static GSStatus platforms(GameWorld *w,LevelPlatform p[10],size_t *count){
    *count=0;
    for(size_t i=0;i<10;i++){
        NativePlatform *a=w->session.platforms.slot+i;
        if(a->left&32768u)return GS_OK;
        p[i]=(LevelPlatform){.left=a->left,.right=a->right,.surface_y=a->height};++*count;
    }return GS_UNSUPPORTED;
}
static void publish(NativeItemSlot *a,const FallingItem *v){
    a->sprite=v->sprite;a->x32=v->position.x32;a->y32=v->position.y32;
    a->vertical_step=v->vertical_step;a->motion_or_lifetime=v->motion_or_lifetime;
}
GameItemSpawn game_item_spawn(GameWorld *w,GameServices *s,ObjectResourceIdentity id,
    ObjectPosition launch,uint16_t horizontal,uint16_t term){
    GameItemSpawn result={GS_INVALID,{ITEM_POOL_FULL,-1}};
    if(!w||!s||!w->session.ready)return result;
    FallingItemType type;result.status=item_type(s,id,&type);if(result.status!=GS_OK)return result;
    FallingItem slots[12]={0};
    for(size_t i=0;i<12;i++)slots[i].sprite=w->items.slot[i].sprite;
    result.allocation=items_spawn(slots,type,launch,horizontal,term);result.status=GS_OK;
    /* Pool-full is an abnormal continuation, not a successful allocation.
     * The caller decides whether its return role admits that continuation. */
    if(result.allocation.status==ITEM_POOL_FULL)return result;
    size_t n=(size_t)result.allocation.slot;
    w->session.item_descriptor[n]=id;publish(w->items.slot+n,slots+n);
    result.status=callback(w,n,6);return result;
}
GSStatus game_item_call(GameWorld *w,GameServices *s,size_t n,ItemCallbackRole role){
    if(!w||!s||!w->session.ready)return GS_INVALID;
    if(n>=12)return GS_UNSUPPORTED;
    if(role!=ITEM_CALLBACK_ADVANCE&&role!=ITEM_CALLBACK_LAND&&role!=ITEM_CALLBACK_COLLECT)return GS_UNSUPPORTED;
    NativeItemSlot *a=w->items.slot+n;FallingItem item={0};
    TRY(item_type(s,w->session.item_descriptor[n],&item.type));
    item.sprite=a->sprite;item.position=(ObjectPosition){a->x32,a->y32};
    item.vertical_step=a->vertical_step;item.motion_or_lifetime=a->motion_or_lifetime;
    if(role==ITEM_CALLBACK_LAND){
        item_land(&item);TRY(callback(w,n,10));a->motion_or_lifetime=item.motion_or_lifetime;return GS_OK;
    }
    if(role==ITEM_CALLBACK_ADVANCE){
        LevelPlatform p[10];size_t count;TRY(platforms(w,p,&count));
        ItemFlightResult result=item_advance(&item,p,count);publish(a,&item);
        if(result.exit==ITEM_TOUCHDOWN)TRY(callback(w,n,10));
        return GS_OK;
    }
    uint16_t limit;TRY(game_object_multiplier_limit(s,w->run.configuration.difficulty,&limit));
    ItemBenefits benefits={w->run.timer,w->run.multiplier,limit,w->run.lives};
    ObjectPosition players[2];for(size_t i=0;i<2;i++)players[i]=(ObjectPosition){w->session.players.player[i].fixed_x,w->session.players.player[i].fixed_y};
    ItemCollectionResult result=item_collect(&item,players,w->run.configuration.players,&benefits);
    a->motion_or_lifetime=item.motion_or_lifetime;
    if(result.collected){
        if(item.type.benefit==ITEM_TIMER)w->run.timer=benefits.timer;
        else if(item.type.benefit==ITEM_LIVES)w->run.lives=benefits.lives;
        else w->run.multiplier=(uint8_t)benefits.multiplier;
    }
    a->sprite=item.sprite;return GS_OK;
}
GSStatus game_items_update(GameWorld *w,GameServices *s){
    if(!w||!s||!w->session.ready)return GS_INVALID;
    /* Never precompute an active set: each physical slot and role is live. */
    for(size_t n=12;n;){
        --n;if(w->items.slot[n].sprite==UINT16_MAX)continue;
        ObjectCallbackIdentity role=w->session.item_callback[n];
        if(role.kind!=OBJECT_CALLBACK_ITEM)return GS_UNSUPPORTED;
        TRY(game_item_call(w,s,n,role.item));
    }return GS_OK;
}
