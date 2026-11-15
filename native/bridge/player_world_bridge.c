#include "platform.h"
#include "player_world_bridge.h"
#include "random_world_bridge.h"
#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
typedef struct PlayerField {uint32_t address;size_t member;unsigned width,count,stride;} PlayerField;
#define A(n) (((uint32_t)DATA_SEG<<4)+D(n))
#define WORD(n,m) {A(n),offsetof(NativePlayerWorld,player[0].m),2,2,sizeof(NativePlayer)}
static const PlayerField fields[]={
 WORD(PlayerUpInput,up),
 WORD(PlayerDownInput,down),
 WORD(PlayerLeftInput,left),
 WORD(PlayerRightInput,right),
 WORD(PlayerActionInput,action),
 WORD(PlayerX32,fixed_x),
 WORD(PlayerY32,fixed_y),
 WORD(PlayerPixelX,pixel_x),
 WORD(PlayerYPixels,pixel_y),
 WORD(PlayerCachedPixelX,cached_x),
 WORD(PlayerCachedPixelY,cached_y),
 WORD(PlayerSpriteIds,sprite),
 WORD(PlayerCachedSpriteIds,cached_sprite),
 WORD(PlayerAnimationCountdowns,animation),
 WORD(PlayerThrustAnimationRate,thrust),
 WORD(PlayerPlatformIndices,platform),
 WORD(PlayerCarriedKinds,carried),
 WORD(PlayerDestinationIcons,destination),
 WORD(PlayerPassengerFares,fare),
 WORD(PlayerMinimumFares,minimum_fare),
 WORD(PlayerHorizontalVelocities,velocity_x),
 WORD(PlayerVerticalVelocities,velocity_y),
 WORD(PlayerImpactMagnitude,impact),
};
static unsigned active;
static int player_field(uint32_t address,unsigned *slot,unsigned *lane){
 uint32_t base=(uint32_t)DATA_SEG<<4;
 if(address<base || address-base<D(PlayerUpInput) || address-base>=D(PlayerImpactMagnitude)+4u)return 0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)if(address>=fields[i].address && address-fields[i].address<fields[i].width*fields[i].count){*slot=i;*lane=(unsigned)(address-fields[i].address);return 1;}
 return 0;
}
static uint8_t player_field_get(const PlayerField *field,unsigned lane){
 const uint8_t *p=(const uint8_t*)native_player_world()+field->member;
 if(field->width==1)return p[lane];
 unsigned index=lane/field->width,shift=(lane%field->width)*8;uint32_t value=0;
 if(field->width==2){uint16_t word;memcpy(&word,p+index*field->stride,2);value=word;}
 else memcpy(&value,p+index*field->stride,4);
#if PLAYER_TEST_FAULT == 7
 if(field->member==offsetof(NativePlayerWorld,player[0].cached_x))value=native_player_world()->player[index].fixed_x>>5;
 if(field->member==offsetof(NativePlayerWorld,player[0].cached_y))value=native_player_world()->player[index].fixed_y>>5;
#endif
 return (uint8_t)(value>>shift);
}
static void player_field_put(const PlayerField *field,unsigned lane,uint8_t value){
 uint8_t *p=(uint8_t*)native_player_world()+field->member;
 if(field->width==1){p[lane]=value;return;}
 unsigned index=lane/field->width,shift=(lane%field->width)*8;uint32_t word=0;
 if(field->width==2){uint16_t old;memcpy(&old,p+index*field->stride,2);word=old;}
 else memcpy(&word,p+index*field->stride,4);
 word=(word&~(255u<<shift))|((uint32_t)value<<shift);
 if(field->width==2){uint16_t half=(uint16_t)word;memcpy(p+index*field->stride,&half,2);}
 else memcpy(p+index*field->stride,&word,4);
}
int player_is_owned(uint32_t address){unsigned slot,lane;return active && player_field(address,&slot,&lane);}
int player_shared_read(uint32_t address,uint8_t *value){unsigned slot,lane;if(!active || !player_field(address,&slot,&lane))return 0;*value=player_field_get(fields+slot,lane);return 1;}
int player_shared_write(uint32_t address,uint8_t value){
 unsigned slot,lane;if(!active || !player_field(address,&slot,&lane))return 0;
#if PLAYER_TEST_FAULT == 1
 /* Incorrect IRQ-byte normalization clears a retained command high byte. */
 if(address>=A(PlayerUpInput) && address<A(PlayerActionInput)+4u && !(lane&1))player_field_put(fields+slot,lane+1,0);
#elif PLAYER_TEST_FAULT == 2
 if(lane>=2)lane-=2; /* Incorrectly collapse player1 onto player0. */
#elif PLAYER_TEST_FAULT == 3
 if(address>=A(PlayerCachedPixelX) && address<A(PlayerCachedSpriteIds)+4u)return 1;
#elif PLAYER_TEST_FAULT == 4
 if(address>=A(PlayerCarriedKinds) && address<A(PlayerMinimumFares)+4u)return 1;
#elif PLAYER_TEST_FAULT == 5
 if(address>=A(PlayerHorizontalVelocities) && address<A(PlayerVerticalVelocities)+4u)return 1;
#endif
 player_field_put(fields+slot,lane,value);return 1;
}
unsigned player_owned_bytes(void){return active?92:0;}
void player_cold_import(uint8_t *memory){
 active=0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)player_field_put(fields+i,lane,memory[fields[i].address+lane]);
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)memset(memory+fields[i].address,0xa5,fields[i].width*fields[i].count);
 active=1;
}
void player_require_seal(const uint8_t *memory){
 if(!active)return;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)if(memory[fields[i].address+lane]!=0xa5){fputs("player: sealed RAM violation\n",stderr);exit(88);}
}
void player_serialize(uint8_t *output){
 if(!active)return;
 unsigned emitted=0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++){
#if PLAYER_TEST_FAULT == 6
  if(!i && !lane)continue;
#endif
  output[fields[i].address+lane]=player_field_get(fields+i,lane);emitted++;
 }
 if(emitted!=player_owned_bytes()){fputs("player: missed serialization\n",stderr);exit(88);}
}
uint32_t player_check_serialization(const uint8_t *output){
 if(active)for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)if(output[fields[i].address+lane]!=player_field_get(fields+i,lane))return fields[i].address+lane;
 return UINT32_MAX;
}
uint8_t player_borrowed_byte(const uint8_t *window,uint32_t index){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE){uint8_t value;if(player_shared_read((uint32_t)(p-base+index),&value))return value;}
 return rng_borrowed_byte(window,index);
}
void player_borrowed_store(uint8_t *window,uint32_t index,uint8_t value){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE && player_shared_write((uint32_t)(p-base+index),value))return;
 rng_borrowed_store(window,index,value);
}
uint32_t player_borrow_read(PlayerBorrower borrower,uint16_t bank,uint16_t position,unsigned width){
 if(borrower>=PLAYER_BORROW_COUNT || (width!=1 && width!=2 && width!=4)){fputs("player: invalid borrower\n",stderr);exit(88);}
 uint32_t result=0,address=lin(bank,position);
 for(unsigned i=0;i<width;i++){uint8_t byte;if(!player_shared_read(address+i,&byte))byte=ugh_read(address+i);result|=(uint32_t)byte<<(8*i);}

 return result;
}
void player_borrow_write(PlayerBorrower borrower,uint16_t bank,uint16_t position,unsigned width,uint32_t value){
 if(borrower>=PLAYER_BORROW_COUNT || (width!=1 && width!=2 && width!=4)){fputs("player: invalid borrower\n",stderr);exit(88);}
 uint32_t address=lin(bank,position);
 for(unsigned i=0;i<width;i++)if(!player_shared_write(address+i,(uint8_t)(value>>(8*i))))ugh_write(address+i,(uint8_t)(value>>(8*i)));
}
