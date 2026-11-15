#include "platform.h"
#include "enemy_world_bridge.h"
#include "actor_world_bridge.h"
#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
typedef struct EnemiesField {uint32_t address;size_t member;unsigned width,count,stride;} EnemiesField;
#define A(n) (((uint32_t)DATA_SEG<<4)+D(n))
#define WORD(n,m) {A(n),offsetof(NativeEnemyWorld,slot[0].m),2,5,sizeof(NativeEnemySlot)}
static const EnemiesField fields[]={
 WORD(EnemyDescriptors,descriptor_word),
 WORD(EnemyPlatformIndices,platform),
 WORD(EnemyX32,x32),
 WORD(EnemyY32,y32),
 WORD(EnemyAnimationOrDropLists,animation_or_drop_word),
 WORD(EnemyInitialDelays,initial_delay),
 WORD(EnemyHorizontalSpeeds,speed),
 WORD(EnemyStateCallbacks,callback_word),
 WORD(EnemyStateCounters,counter),
 WORD(EnemyDrawX,draw_x),
 WORD(EnemyPreviousDrawX,previous_x),
 WORD(EnemyDrawY,draw_y),
 WORD(EnemyPreviousDrawY,previous_y),
 WORD(EnemyAnimationByteOffsets,animation_offset),
 WORD(EnemyAnimationCountdowns,countdown),
 WORD(EnemySpriteIds,sprite),
 WORD(EnemyEraseSprite,erase_sprite),
 WORD(EnemyDirectionOrTargetPlayer,direction_or_target_word),
 WORD(EnemyFlightSoundHandles,sound_handle_word),

};
static unsigned active;
static int enemies_field(uint32_t address,unsigned *slot,unsigned *lane){
 uint32_t base=(uint32_t)DATA_SEG<<4;
 if(address<base || address-base<D(EnemyDescriptors) || address-base>=D(EnemyFlightSoundHandles)+10u)return 0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)if(address>=fields[i].address && address-fields[i].address<fields[i].width*fields[i].count){*slot=i;*lane=(unsigned)(address-fields[i].address);return 1;}
 return 0;
}
static uint8_t enemies_field_get(const EnemiesField *field,unsigned lane){
 const uint8_t *p=(const uint8_t*)native_enemy_world()+field->member;
 if(field->width==1)return p[lane];
 unsigned index=lane/field->width,shift=(lane%field->width)*8;uint32_t value=0;
 if(field->width==2){uint16_t word;memcpy(&word,p+index*field->stride,2);value=word;}
 else memcpy(&value,p+index*field->stride,4);

 return (uint8_t)(value>>shift);
}
static void enemies_field_put(const EnemiesField *field,unsigned lane,uint8_t value){
 uint8_t *p=(uint8_t*)native_enemy_world()+field->member;
 if(field->width==1){p[lane]=value;return;}
 unsigned index=lane/field->width,shift=(lane%field->width)*8;uint32_t word=0;
 if(field->width==2){uint16_t old;memcpy(&old,p+index*field->stride,2);word=old;}
 else memcpy(&word,p+index*field->stride,4);
 word=(word&~(255u<<shift))|((uint32_t)value<<shift);
 if(field->width==2){uint16_t half=(uint16_t)word;memcpy(p+index*field->stride,&half,2);}
 else memcpy(p+index*field->stride,&word,4);
}
int enemies_is_owned(uint32_t address){unsigned slot,lane;return active && enemies_field(address,&slot,&lane);}
int enemies_shared_read(uint32_t address,uint8_t *value){unsigned slot,lane;if(!active || !enemies_field(address,&slot,&lane))return 0;*value=enemies_field_get(fields+slot,lane);return 1;}
int enemies_shared_write(uint32_t address,uint8_t value){
 unsigned slot,lane;if(!active || !enemies_field(address,&slot,&lane))return 0;
#if ENEMIES_TEST_FAULT == 1
 if(address>=A(EnemyFlightSoundHandles) && address<A(EnemyFlightSoundHandles)+10u)return 1;
#elif ENEMIES_TEST_FAULT == 2
 if(lane>=2)lane-=2;
#elif ENEMIES_TEST_FAULT == 3
 if(!(lane&1))enemies_field_put(fields+slot,lane+1,0);
#endif
 enemies_field_put(fields+slot,lane,value);return 1;
}
unsigned enemies_owned_bytes(void){return active?190:0;}
void enemies_cold_import(uint8_t *memory){
 active=0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)enemies_field_put(fields+i,lane,memory[fields[i].address+lane]);
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)memset(memory+fields[i].address,0xa5,fields[i].width*fields[i].count);
 active=1;
}
void enemies_require_seal(const uint8_t *memory){
 if(!active)return;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)if(memory[fields[i].address+lane]!=0xa5){fputs("enemies: sealed RAM violation\n",stderr);exit(88);}
}
void enemies_serialize(uint8_t *output){
 if(!active)return;
 unsigned emitted=0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++){
#if ENEMIES_TEST_FAULT == 4
  if(!i && !lane)continue;
#endif
  output[fields[i].address+lane]=enemies_field_get(fields+i,lane);emitted++;
 }
 if(emitted!=enemies_owned_bytes()){fputs("enemies: missed serialization\n",stderr);exit(88);}
}
uint32_t enemies_check_serialization(const uint8_t *output){
 if(active)for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)if(output[fields[i].address+lane]!=enemies_field_get(fields+i,lane))return fields[i].address+lane;
 return UINT32_MAX;
}
uint8_t enemies_borrowed_byte(const uint8_t *window,uint32_t index){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE){uint8_t value;if(enemies_shared_read((uint32_t)(p-base+index),&value))return value;}
 return actors_borrowed_byte(window,index);
}
void enemies_borrowed_store(uint8_t *window,uint32_t index,uint8_t value){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE && enemies_shared_write((uint32_t)(p-base+index),value))return;
 actors_borrowed_store(window,index,value);
}
uint32_t enemies_borrow_read(EnemiesBorrower borrower,uint16_t bank,uint16_t position,unsigned width){
 if(borrower>=ENEMIES_BORROW_COUNT || (width!=1 && width!=2 && width!=4)){fputs("enemies: invalid borrower\n",stderr);exit(88);}
 uint32_t result=0,address=lin(bank,position);
 for(unsigned i=0;i<width;i++){uint8_t byte;if(!enemies_shared_read(address+i,&byte))byte=ugh_read(address+i);result|=(uint32_t)byte<<(8*i);}

 return result;
}
void enemies_borrow_write(EnemiesBorrower borrower,uint16_t bank,uint16_t position,unsigned width,uint32_t value){
 if(borrower>=ENEMIES_BORROW_COUNT || (width!=1 && width!=2 && width!=4)){fputs("enemies: invalid borrower\n",stderr);exit(88);}
 uint32_t address=lin(bank,position);
 for(unsigned i=0;i<width;i++)if(!enemies_shared_write(address+i,(uint8_t)(value>>(8*i))))ugh_write(address+i,(uint8_t)(value>>(8*i)));
}
