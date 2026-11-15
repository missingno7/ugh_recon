#include "resource_catalog_bridge.h"
#include <stdio.h>
#include <string.h>
uint8_t ugh_mem[UGH_MEM_SIZE];
uint8_t ugh_read(uint32_t a){return ugh_mem[a];}
void ugh_write(uint32_t a,uint8_t v){ugh_mem[a]=v;}
uint8_t player_borrowed_byte(const uint8_t*p,uint32_t i){return p[i];}
void player_borrowed_store(uint8_t*p,uint32_t i,uint8_t v){p[i]=v;}
static uint8_t expected[UGH_MEM_SIZE],output[UGH_MEM_SIZE];
int main(int argc,char**argv){
 uint32_t base=(uint32_t)UGH_S_B5B63_ext_5B63*16u,ro=lin(GAME_SEG,G(IceDecoderTables));
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)ugh_mem[a]=(uint8_t)(a*193u+(a>>8)*73u);
 memcpy(expected,ugh_mem,sizeof expected);resources_cold_import(ugh_mem);if(resources_owned_bytes()!=2708)return 1;
 if(argc>1 && !strcmp(argv[1],"immutable")){resources_shared_write(ro+59,71);return 99;}
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(resources_is_owned(a)!=(int)((a>=base && a<base+2648)||(a>=ro && a<ro+60)))return 2;
 memcpy(output,ugh_mem,sizeof output);resources_serialize(output);if(memcmp(output,expected,sizeof output))return 3;
 NativeResourceCatalog*c=native_resource_catalog();
 for(unsigned i=0;i<662;i++)for(unsigned half=0;half<2;half++)for(unsigned v=0;v<65536;v++){
  unsigned a=base+i*4+half*2;resources_shared_write(a,(uint8_t)v);resources_borrowed_store(ugh_mem,a+1,(uint8_t)(v>>8));expected[a]=(uint8_t)v;expected[a+1]=(uint8_t)(v>>8);
  if((half?c->sprites[i].dimensions:c->sprites[i].source_offset)!=v)return 4;
 }
 for(unsigned i=0;i<2648;i++)for(unsigned v=0;v<256;v++){
  resources_shared_write(base+i,(uint8_t)v);expected[base+i]=(uint8_t)v;uint8_t now;
  if(!resources_shared_read(base+i,&now)||now!=v)return 5;
  memcpy(output,ugh_mem,sizeof output);resources_serialize(output);if(memcmp(output,expected,sizeof output))return 6;
 }
 for(unsigned kind=1;kind<=3;kind++)for(unsigned n=0;n<(kind==1?662:kind==2?5:3);n++){
  ResourceToken token={(ResourceKind)kind,(uint16_t)n},decoded={0,0};uint16_t old;if(!resource_token_to_legacy(token,&old))return 7;
  int ok=kind==1?resource_sprite_from_legacy(old,&decoded):kind==2?resource_table_from_legacy(old,&decoded):resource_effect_from_legacy(old,&decoded);
  if(!ok || decoded.kind!=token.kind || decoded.index!=token.index)return 8;
 }
 for(unsigned w=0;w<65536;w++){ResourceToken t;
  if(resource_sprite_from_legacy((uint16_t)w,&t)!=(w<662))return 9;
  unsigned ne=(w==G(IgnoreActorState)||w==G(StartDemoFadeWhenSpriteHidden)||w==G(SetDemoRevealSpriteWidth));
  if(resource_effect_from_legacy((uint16_t)w,&t)!=(int)ne)return 10;
 }
 for(unsigned table=0;table<5;table++){
  ResourceToken t={RESOURCE_CODEC_TABLE,(uint16_t)table};ResourceTableView view;if(resource_table(t,&view)!=RESOURCE_OK)return 11;
  static const unsigned starts[5]={0,40,45,50,54},sizes[5]={60,5,5,3,6};if(view.size!=sizes[table] || view.first_index!=(table?-1:0) || view.entry_width!=(table==4?2:1))return 12;
  for(unsigned i=0;i<view.size;i++)for(unsigned v=0;v<256;v++){
   if(view.bytes[i]!=expected[ro+starts[table]+i] || resource_store(t,i,(uint8_t)v)!=RESOURCE_IMMUTABLE)return 13;
   if(view.bytes[i]!=expected[ro+starts[table]+i])return 14;
  }
 }
 for(unsigned delta=0;delta<3;delta++){
  uint16_t bank=(uint16_t)(UGH_S_B5B63_ext_5B63+delta);uint8_t *window=ugh_mem+lin(bank,0);
  resources_borrowed_store(window,(unsigned)(858-delta*16),91);if((c->sprites[214].dimensions&255)!=91)return 15;expected[base+858]=91;
 }
 resources_require_seal(ugh_mem);resources_serialize(output);if(resources_check_serialization(output)!=UINT32_MAX)return 16;
 if(memcmp(output,expected,sizeof output))return 17;
 for(unsigned a=0;a<UGH_MEM_SIZE;a++)if(!resources_is_owned(a)){uint8_t v=49;if(resources_shared_read(a,&v)||resources_shared_write(a,17)||v!=49)return 18;}
 puts("{\"mutable_bytes\":2648,\"immutable_bytes\":60,\"word_roundtrips\":86769664,\"mutable_byte_values\":677888,\"tokens\":670,\"legacy_word_domain\":65536}");return 0;
}
