#include "game_object_data.h"
typedef struct GameObjectData {ObjectResourceIdentity identity;SessionDataView data;} GameObjectData;
typedef struct GameObjectPosition {uint16_t view,position;} GameObjectPosition;
#include "gameplay_data.h"
static const GameObjectData *admitted(ObjectResourceIdentity id){
    for(size_t i=0;i<sizeof object_data/sizeof *object_data;i++){
        const GameObjectData *d=object_data+i;
        if(d->identity.kind!=id.kind||d->identity.view.index!=id.view.index)continue;
        for(size_t j=0;j<sizeof object_positions/sizeof *object_positions;j++)
            if(object_positions[j].view==id.view.index&&object_positions[j].position==id.position)return d;
        return 0;
    }return 0;
}
GSStatus game_object_resource(GameServices *s,ObjectResourceIdentity id,GSBytes *out){
    if(!s||!out)return GS_INVALID;
    const GameObjectData *d=admitted(id);if(!d)return GS_UNSUPPORTED;
    GSBytes b;GSStatus status=session_data_view(s,d->data,&b);if(status!=GS_OK)return status;
    if(id.position>b.size)return GS_UNSUPPORTED;
    *out=(GSBytes){b.data+id.position,b.size-id.position};return GS_OK;
}
GSStatus game_object_word(GameServices *s,ObjectResourceIdentity id,uint16_t offset,uint16_t *value){
    if(!value)return GS_INVALID;
    GSBytes b;GSStatus status=game_object_resource(s,id,&b);if(status!=GS_OK)return status;
    if(offset>=b.size||b.size-offset<2)return GS_UNSUPPORTED;
    *value=(uint16_t)(b.data[offset]|(uint16_t)b.data[offset+1]<<8);return GS_OK;
}
GSStatus game_object_link(ObjectResourceIdentity id,uint16_t member,ObjectGraphLink *out){
    if(!out)return GS_INVALID;
    if(!admitted(id))return GS_UNSUPPORTED;
    size_t position=(size_t)id.position+member;
    for(size_t i=0;i<sizeof object_links/sizeof *object_links;i++){
        const ObjectGraphLink *l=object_links+i;
        if(l->source.index==id.view.index&&l->member==position){*out=*l;return GS_OK;}
    }return GS_UNSUPPORTED;
}
GSStatus game_object_actor_type(ActorTypeId type,ObjectResourceIdentity *out){
    if(!out)return GS_INVALID;
    if((unsigned)type>=sizeof actor_types/sizeof *actor_types)return GS_UNSUPPORTED;
    *out=actor_types[type];return GS_OK;
}
GSStatus game_object_actor_id(ObjectResourceIdentity id,ActorTypeId *out){
    if(!out)return GS_INVALID;
    if(id.kind!=OBJECT_ACTOR_DESCRIPTOR||id.position)return GS_UNSUPPORTED;
    for(size_t i=0;i<sizeof actor_types/sizeof *actor_types;i++)
        if(actor_types[i].view.index==id.view.index){*out=(ActorTypeId)i;return GS_OK;}
    return GS_UNSUPPORTED;
}
ObjectResourceIdentity game_object_bonus(void){return delivery_bonus;}
GSResourceId game_object_stone_effect(void){return stone_effect;}
GSResourceId game_object_bonus_effect(void){return bonus_effect;}
GSStatus game_object_multiplier_limit(GameServices *s,uint16_t difficulty,uint16_t *out){
    if(!out)return GS_INVALID;
    if(difficulty>2)return GS_UNSUPPORTED;
    GSBytes b;GSStatus status=session_data_view(s,multiplier_limits,&b);if(status!=GS_OK)return status;
    *out=(uint16_t)(b.data[2*difficulty]|(uint16_t)b.data[2*difficulty+1]<<8);return GS_OK;
}
