#include "platform.h"
#include "resource_catalog_bridge.h"
#include "player_world_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned active;
static uint32_t sprite_base(void){return (uint32_t)UGH_S_B5B63_ext_5B63*16u;}
static uint32_t codec_base(void){return lin(GAME_SEG,G(IceDecoderTables));}
int resource_sprite_from_legacy(uint16_t ordinal,ResourceToken *token){
 if(ordinal>=RESOURCE_SPRITE_RECORDS)return 0;
#if RESOURCE_TEST_FAULT == 2
 if(ordinal<2)ordinal^=1;
#endif
 *token=(ResourceToken){RESOURCE_SPRITE_RECORD,ordinal};return 1;
}
int resource_effect_from_legacy(uint16_t word,ResourceToken *token){
 const uint16_t words[3]={G(IgnoreActorState),G(StartDemoFadeWhenSpriteHidden),G(SetDemoRevealSpriteWidth)};
 for(unsigned i=0;i<3;i++)if(word==words[i]){*token=(ResourceToken){RESOURCE_DEMO_EFFECT,(uint16_t)i};return 1;}
 return 0;
}
int resource_table_from_legacy(uint16_t word,ResourceToken *token){
 const uint16_t words[5]={G(IceDecoderTables),G(IceMatchLengthBitCountsMinusOne),G(IceMatchLengthBiases),G(IceMatchOffsetBitCountsMinusOne),G(IceMatchOffsetBiases)};
 for(unsigned i=0;i<5;i++)if(word==words[i]){*token=(ResourceToken){RESOURCE_CODEC_TABLE,(uint16_t)i};return 1;}
 return 0;
}
int resource_token_to_legacy(ResourceToken token,uint16_t *word){
 if(!resource_token_valid(token))return 0;
 if(token.kind==RESOURCE_SPRITE_RECORD){*word=token.index;return 1;}
 if(token.kind==RESOURCE_DEMO_EFFECT){const uint16_t words[3]={G(IgnoreActorState),G(StartDemoFadeWhenSpriteHidden),G(SetDemoRevealSpriteWidth)};*word=words[token.index];return 1;}
 if(token.kind==RESOURCE_CODEC_TABLE){const uint16_t words[5]={G(IceDecoderTables),G(IceMatchLengthBitCountsMinusOne),G(IceMatchLengthBiases),G(IceMatchOffsetBitCountsMinusOne),G(IceMatchOffsetBiases)};*word=words[token.index];return 1;}
 return 0;
}
static int resources_field(uint32_t address,ResourceToken *token,unsigned *lane){
 uint32_t base=sprite_base();
 if(address>=base && address-base<RESOURCE_SPRITE_RECORDS*4u){unsigned n=(unsigned)(address-base);resource_sprite_from_legacy((uint16_t)(n/4),token);*lane=n%4;return 1;}
 base=codec_base();if(address>=base && address-base<RESOURCE_CODEC_BYTES){*token=(ResourceToken){RESOURCE_CODEC_TABLE,0};*lane=(unsigned)(address-base);return 1;}
 return 0;
}
int resources_is_owned(uint32_t address){ResourceToken token;unsigned lane;return active && resources_field(address,&token,&lane);}
int resources_shared_read(uint32_t address,uint8_t *value){ResourceToken token;unsigned lane;if(!active || !resources_field(address,&token,&lane))return 0;if(resource_read(token,lane,value)!=RESOURCE_OK)exit(89);return 1;}
int resources_shared_write(uint32_t address,uint8_t value){
 ResourceToken token;unsigned lane;if(!active || !resources_field(address,&token,&lane))return 0;
#if RESOURCE_TEST_FAULT == 1
 if(token.kind==RESOURCE_SPRITE_RECORD && token.index==214 && lane==2)return 1;
#endif
 ResourceStatus status=resource_store(token,lane,value);
 if(status!=RESOURCE_OK){fputs("resources: immutable or invalid store\n",stderr);exit(89);}return 1;
}
unsigned resources_owned_bytes(void){return active?2708:0;}
void resources_cold_import(uint8_t *memory){
 active=0;NativeResourceCatalog *c=native_resource_catalog();uint32_t base=sprite_base();
 for(unsigned i=0;i<RESOURCE_SPRITE_RECORDS;i++){unsigned a=base+i*4;c->sprites[i].source_offset=(uint16_t)(memory[a]|memory[a+1]*256u);c->sprites[i].dimensions=(uint16_t)(memory[a+2]|memory[a+3]*256u);}
 uint8_t bytes[RESOURCE_CODEC_BYTES];for(unsigned i=0;i<RESOURCE_CODEC_BYTES;i++)bytes[i]=memory[codec_base()+i];resource_provider_load_codec(bytes);
 for(unsigned i=0;i<RESOURCE_SPRITE_RECORDS*4u;i++)memory[base+i]=0xa5;
 for(unsigned i=0;i<RESOURCE_CODEC_BYTES;i++)memory[codec_base()+i]=0xa5;
 active=1;
}
void resources_require_seal(const uint8_t *memory){
 if(!active)return;
 for(unsigned a=0;a<RESOURCE_SPRITE_RECORDS*4u;a++)if(memory[sprite_base()+a]!=0xa5){fputs("resources: sealed RAM violation\n",stderr);exit(88);}
 for(unsigned a=0;a<RESOURCE_CODEC_BYTES;a++)if(memory[codec_base()+a]!=0xa5){fputs("resources: sealed RAM violation\n",stderr);exit(88);}
}
void resources_serialize(uint8_t *output){
 if(!active)return;
 unsigned count=0;
 for(unsigned i=0;i<RESOURCE_SPRITE_RECORDS*4u;i++){
#if RESOURCE_TEST_FAULT == 3
  if(i==858)continue;
#endif
  uint8_t value;resources_shared_read(sprite_base()+i,&value);output[sprite_base()+i]=value;count++;
 }
 for(unsigned i=0;i<RESOURCE_CODEC_BYTES;i++){uint8_t value;resources_shared_read(codec_base()+i,&value);output[codec_base()+i]=value;count++;}
 if(count!=resources_owned_bytes()){fputs("resources: missed serialization\n",stderr);exit(88);}
}
uint32_t resources_check_serialization(const uint8_t *output){
 if(active){for(unsigned i=0;i<RESOURCE_SPRITE_RECORDS*4u;i++){uint8_t value;resources_shared_read(sprite_base()+i,&value);if(output[sprite_base()+i]!=value)return sprite_base()+i;}
 for(unsigned i=0;i<RESOURCE_CODEC_BYTES;i++){uint8_t value;resources_shared_read(codec_base()+i,&value);if(output[codec_base()+i]!=value)return codec_base()+i;}}
 return UINT32_MAX;
}
uint8_t resources_borrowed_byte(const uint8_t *window,uint32_t index){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE){uint8_t value;if(resources_shared_read((uint32_t)(p-base+index),&value))return value;}
 return player_borrowed_byte(window,index);
}
void resources_borrowed_store(uint8_t *window,uint32_t index,uint8_t value){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE && resources_shared_write((uint32_t)(p-base+index),value))return;
 player_borrowed_store(window,index,value);
}
