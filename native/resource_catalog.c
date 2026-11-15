#include "resource_catalog.h"
static NativeResourceCatalog catalog;
static uint8_t codec[RESOURCE_CODEC_BYTES];
void resource_provider_load_codec(const uint8_t bytes[RESOURCE_CODEC_BYTES]){for(unsigned i=0;i<RESOURCE_CODEC_BYTES;i++)codec[i]=bytes[i];}
NativeResourceCatalog *native_resource_catalog(void){return &catalog;}
int resource_token_valid(ResourceToken token){
 switch(token.kind){case RESOURCE_SPRITE_RECORD:return token.index<RESOURCE_SPRITE_RECORDS;
 case RESOURCE_CODEC_TABLE:return token.index<5;case RESOURCE_DEMO_EFFECT:return token.index<3;default:return 0;}
}
ResourceStatus resource_sprite(ResourceToken token,ResourceSpriteRecord *view){
 if(token.kind!=RESOURCE_SPRITE_RECORD || !resource_token_valid(token))return RESOURCE_INVALID;
 *view=catalog.sprites[token.index];return RESOURCE_OK;
}
ResourceStatus resource_table(ResourceToken token,ResourceTableView *view){
 static const uint8_t offset[5]={0,40,45,50,54},length[5]={60,5,5,3,6};
 if(token.kind!=RESOURCE_CODEC_TABLE || !resource_token_valid(token))return RESOURCE_INVALID;
 *view=(ResourceTableView){codec+offset[token.index],length[token.index],token.index?-1:0,token.index==4?2:1};return RESOURCE_OK;
}
ResourceStatus resource_effect(ResourceToken token,DemoMotionEffect *effect){
 if(token.kind!=RESOURCE_DEMO_EFFECT || !resource_token_valid(token))return RESOURCE_INVALID;
 static const DemoMotionEffect effects[3]={DEMO_EFFECT_NONE,DEMO_EFFECT_FADE_ON_HIDDEN,DEMO_EFFECT_REVEAL_WIDTH};
 *effect=effects[token.index];return RESOURCE_OK;
}
static uint8_t resource_sprite_byte(const ResourceSpriteRecord *sprite,unsigned lane){
 uint16_t word=lane<2?sprite->source_offset:sprite->dimensions;return (uint8_t)(word>>((lane&1)*8));
}
static void resource_sprite_put(ResourceSpriteRecord *sprite,unsigned lane,uint8_t value){
 uint16_t *word=lane<2?&sprite->source_offset:&sprite->dimensions;unsigned shift=(lane&1)*8;
 *word=(uint16_t)((*word&~(255u<<shift))|((unsigned)value<<shift));
}
ResourceStatus resource_read(ResourceToken token,unsigned lane,uint8_t *value){
 if(!resource_token_valid(token))return RESOURCE_INVALID;
 if(token.kind==RESOURCE_SPRITE_RECORD){
  if(lane>=4)return RESOURCE_INVALID;
  *value=resource_sprite_byte(&catalog.sprites[token.index],lane);return RESOURCE_OK;
 }
 if(token.kind==RESOURCE_CODEC_TABLE){ResourceTableView view;resource_table(token,&view);if(lane>=view.size)return RESOURCE_INVALID;*value=view.bytes[lane];return RESOURCE_OK;}
 return RESOURCE_INVALID;
}
ResourceStatus resource_store(ResourceToken token,unsigned lane,uint8_t value){
 if(!resource_token_valid(token))return RESOURCE_INVALID;
 if(token.kind==RESOURCE_CODEC_TABLE){ResourceTableView view;resource_table(token,&view);return lane<view.size?RESOURCE_IMMUTABLE:RESOURCE_INVALID;}
 if(token.kind!=RESOURCE_SPRITE_RECORD || lane>=4)return RESOURCE_INVALID;
 resource_sprite_put(&catalog.sprites[token.index],lane,value);return RESOURCE_OK;
}
