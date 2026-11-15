#include "object_identities.h"
#include "object_identities.inc"
ObjectIdentityStatus object_callback_identity(ObjectCallbackIdentity role,ObjectCallbackIdentity *identity){
 if(!identity)return OBJECT_IDENTITY_UNSUPPORTED;
 *identity=(ObjectCallbackIdentity){OBJECT_CALLBACK_UNSUPPORTED,ACTOR_CALLBACK_UNSUPPORTED,H_ZERO,ITEM_CALLBACK_UNSUPPORTED,{RESOURCE_DEMO_EFFECT,0}};
 if(role.kind==OBJECT_CALLBACK_ACTOR && role.actor>ACTOR_CALLBACK_UNSUPPORTED && role.actor<ACTOR_CALLBACK_COUNT)identity->actor=role.actor;
 else if(role.kind==OBJECT_CALLBACK_ENEMY && (unsigned)role.enemy<=H_TREE_EMPTY)identity->enemy=role.enemy;
 else if(role.kind==OBJECT_CALLBACK_ITEM && role.item>ITEM_CALLBACK_UNSUPPORTED && role.item<=ITEM_CALLBACK_COLLECT)identity->item=role.item;
 else if(role.kind==OBJECT_CALLBACK_DEMO_EFFECT && role.effect.kind==RESOURCE_DEMO_EFFECT && role.effect.index<=DEMO_EFFECT_REVEAL_WIDTH)identity->effect=role.effect;
 else if(role.kind!=OBJECT_CALLBACK_EMPTY)return OBJECT_IDENTITY_UNSUPPORTED;
 identity->kind=role.kind;return OBJECT_IDENTITY_OK;
}
ObjectIdentityStatus object_resource_identity(ObjectResourceKind kind,ResourceWorldToken view,
 uint16_t position,ObjectResourceIdentity *identity){
 size_t lo=0,hi=sizeof object_resources/sizeof *object_resources;
 if(!identity)return OBJECT_IDENTITY_UNSUPPORTED;
 *identity=(ObjectResourceIdentity){OBJECT_RESOURCE_UNSUPPORTED,{0},0};
 while(lo<hi){
  size_t mid=lo+(hi-lo)/2;const ObjectResourceIdentity *entry=object_resources+mid;
  if(entry->view.index<view.index || (entry->view.index==view.index && entry->position<position))lo=mid+1;
  else hi=mid;
 }
 if(lo==sizeof object_resources/sizeof *object_resources)return OBJECT_IDENTITY_UNSUPPORTED;
 const ObjectResourceIdentity *entry=object_resources+lo;
 if(entry->view.index!=view.index || entry->position!=position || entry->kind!=kind)return OBJECT_IDENTITY_UNSUPPORTED;
 *identity=*entry;return OBJECT_IDENTITY_OK;
}
ObjectIdentityStatus object_resource_read(ObjectResourceIdentity identity,uint16_t displacement,uint16_t *value){
 ObjectResourceIdentity checked;uint8_t low,high;
 if(!value || object_resource_identity(identity.kind,identity.view,identity.position,&checked)!=OBJECT_IDENTITY_OK)return OBJECT_IDENTITY_UNSUPPORTED;
 uint32_t position=(uint32_t)checked.position+displacement;
 if(!resource_world_read(RESOURCE_BORROW_ACTORS,checked.view,position,&low) ||
    !resource_world_read(RESOURCE_BORROW_ACTORS,checked.view,position+1,&high))return OBJECT_IDENTITY_UNSUPPORTED;
 *value=(uint16_t)(low+256u*high);return OBJECT_IDENTITY_OK;
}
size_t object_graph_link_count(void){return sizeof object_links/sizeof *object_links;}
ObjectIdentityStatus object_graph_link_at(size_t index,ObjectGraphLink *link){
 if(!link || index>=object_graph_link_count())return OBJECT_IDENTITY_UNSUPPORTED;
 *link=object_links[index];return OBJECT_IDENTITY_OK;
}
ObjectIdentityStatus object_graph_link(ResourceWorldToken source,uint16_t member,ObjectGraphLink *link){
 size_t lo=0,hi=object_graph_link_count();
 while(lo<hi){
  size_t mid=lo+(hi-lo)/2;const ObjectGraphLink *entry=object_links+mid;
  if(entry->source.index<source.index || (entry->source.index==source.index && entry->member<member))lo=mid+1;
  else hi=mid;
 }
 if(lo==object_graph_link_count() || object_links[lo].source.index!=source.index || object_links[lo].member!=member)return OBJECT_IDENTITY_UNSUPPORTED;
 return object_graph_link_at(lo,link);
}
