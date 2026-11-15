#include "object_identities_bridge.h"
#include "object_identity_bindings.inc"
ObjectIdentityStatus object_resource_from_legacy(ObjectResourceKind kind,uint16_t word,ObjectResourceIdentity *identity){
 if(!identity)return OBJECT_IDENTITY_UNSUPPORTED;
 *identity=(ObjectResourceIdentity){OBJECT_RESOURCE_UNSUPPORTED,{0},0};
 for(unsigned i=0;i<sizeof object_legacy_resources/sizeof *object_legacy_resources;i++){
  const ObjectLegacyResource *row=object_legacy_resources+i;
  if(row->kind==kind && word>=row->word &&
     object_resource_identity(kind,row->view,(uint16_t)(word-row->word),identity)==OBJECT_IDENTITY_OK)return OBJECT_IDENTITY_OK;
 }
 return OBJECT_IDENTITY_UNSUPPORTED;
}
ObjectIdentityStatus object_resource_to_legacy(ObjectResourceIdentity identity,uint16_t *word){
 ObjectResourceIdentity checked;
 if(!word || object_resource_identity(identity.kind,identity.view,identity.position,&checked)!=OBJECT_IDENTITY_OK)return OBJECT_IDENTITY_UNSUPPORTED;
 for(unsigned i=0;i<sizeof object_legacy_resources/sizeof *object_legacy_resources;i++){
  const ObjectLegacyResource *row=object_legacy_resources+i;
  if(row->kind==checked.kind && row->view.index==checked.view.index){*word=(uint16_t)(row->word+checked.position);return OBJECT_IDENTITY_OK;}
 }
 return OBJECT_IDENTITY_UNSUPPORTED;
}
ObjectIdentityStatus object_callback_from_legacy(ObjectLegacyCallbackFamily family,uint16_t word,ObjectCallbackIdentity *identity){
 if(!identity)return OBJECT_IDENTITY_UNSUPPORTED;
 *identity=(ObjectCallbackIdentity){OBJECT_CALLBACK_UNSUPPORTED,ACTOR_CALLBACK_UNSUPPORTED,H_ZERO,ITEM_CALLBACK_UNSUPPORTED,{RESOURCE_DEMO_EFFECT,0}};
 for(unsigned i=0;i<sizeof object_legacy_callbacks/sizeof *object_legacy_callbacks;i++){
  const ObjectLegacyCallback *row=object_legacy_callbacks+i;
  if(row->family!=family || row->word!=word)continue;
  if(family==OBJECT_LEGACY_ACTOR){identity->kind=OBJECT_CALLBACK_ACTOR;identity->actor=(ActorCallback)row->role;}
  else if(family==OBJECT_LEGACY_ENEMY){identity->kind=OBJECT_CALLBACK_ENEMY;identity->enemy=(HazardEntry)row->role;}
  else if(family==OBJECT_LEGACY_ITEM){identity->kind=OBJECT_CALLBACK_ITEM;identity->item=(ItemCallbackRole)row->role;}
  else if(family==OBJECT_LEGACY_EFFECT){identity->kind=OBJECT_CALLBACK_DEMO_EFFECT;identity->effect.index=row->role;}
  else return OBJECT_IDENTITY_UNSUPPORTED;
  ObjectCallbackIdentity checked;
  if(object_callback_identity(*identity,&checked)!=OBJECT_IDENTITY_OK)return OBJECT_IDENTITY_UNSUPPORTED;
  *identity=checked;return OBJECT_IDENTITY_OK;
 }
 return OBJECT_IDENTITY_UNSUPPORTED;
}
ObjectIdentityStatus object_callback_to_legacy(ObjectCallbackIdentity identity,uint16_t *word){
 ObjectLegacyCallbackFamily family;unsigned role;
 ObjectCallbackIdentity checked;
 if(!word || object_callback_identity(identity,&checked)!=OBJECT_IDENTITY_OK)return OBJECT_IDENTITY_UNSUPPORTED;
 identity=checked;
 if(identity.kind==OBJECT_CALLBACK_ACTOR){family=OBJECT_LEGACY_ACTOR;role=identity.actor;}
 else if(identity.kind==OBJECT_CALLBACK_ENEMY){family=OBJECT_LEGACY_ENEMY;role=identity.enemy;}
 else if(identity.kind==OBJECT_CALLBACK_ITEM){family=OBJECT_LEGACY_ITEM;role=identity.item;}
 else if(identity.kind==OBJECT_CALLBACK_DEMO_EFFECT && identity.effect.kind==RESOURCE_DEMO_EFFECT && identity.effect.index<3){family=OBJECT_LEGACY_EFFECT;role=identity.effect.index;}
 else return OBJECT_IDENTITY_UNSUPPORTED;
 for(unsigned i=0;i<sizeof object_legacy_callbacks/sizeof *object_legacy_callbacks;i++){
  const ObjectLegacyCallback *row=object_legacy_callbacks+i;
  if(row->family==family && row->role==role){*word=row->word;return OBJECT_IDENTITY_OK;}
 }
 return OBJECT_IDENTITY_UNSUPPORTED;
}
ObjectIdentityStatus object_live_link(ResourceWorldToken source,uint16_t member,ObjectGraphLink *link){
 ObjectGraphLink schema;uint8_t low,high;
 if(!link || object_graph_link(source,member,&schema)!=OBJECT_IDENTITY_OK ||
    !resource_world_read(RESOURCE_BORROW_ACTORS,source,member,&low) ||
    !resource_world_read(RESOURCE_BORROW_ACTORS,source,(uint32_t)member+1,&high))return OBJECT_IDENTITY_UNSUPPORTED;
 uint16_t word=(uint16_t)(low+256u*high);*link=schema;
 if(schema.kind==OBJECT_LINK_RESOURCE){
  if(!word){link->kind=OBJECT_LINK_EMPTY;return OBJECT_IDENTITY_OK;}
  if(word==65535u){link->kind=OBJECT_LINK_END;return OBJECT_IDENTITY_OK;}
  return object_resource_from_legacy(schema.resource.kind,word,&link->resource);
 }
 if(schema.kind==OBJECT_LINK_CALLBACK){
  ObjectLegacyCallbackFamily family;
  if(schema.callback.kind==OBJECT_CALLBACK_ACTOR)family=OBJECT_LEGACY_ACTOR;
  else if(schema.callback.kind==OBJECT_CALLBACK_ENEMY)family=OBJECT_LEGACY_ENEMY;
  else if(schema.callback.kind==OBJECT_CALLBACK_ITEM)family=OBJECT_LEGACY_ITEM;
  else if(schema.callback.kind==OBJECT_CALLBACK_DEMO_EFFECT)family=OBJECT_LEGACY_EFFECT;
  else return !word?OBJECT_IDENTITY_OK:OBJECT_IDENTITY_UNSUPPORTED;
  return object_callback_from_legacy(family,word,&link->callback);
 }
 if(schema.kind==OBJECT_LINK_SPRITE){
  if(word==65535u){link->kind=OBJECT_LINK_END;return OBJECT_IDENTITY_OK;}
  link->sprite=(ResourceToken){RESOURCE_SPRITE_RECORD,word};
  return word<RESOURCE_SPRITE_RECORDS?OBJECT_IDENTITY_OK:OBJECT_IDENTITY_UNSUPPORTED;
 }
 /* Optional null and terminal members do not acquire a role from an unrelated
  * mutated word. The verification raw window still retains that word. */
 if(word!=0 && word!=65535u)return OBJECT_IDENTITY_UNSUPPORTED;
 link->kind=word?OBJECT_LINK_END:OBJECT_LINK_EMPTY;return OBJECT_IDENTITY_OK;
}
