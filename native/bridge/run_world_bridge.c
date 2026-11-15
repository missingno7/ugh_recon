#include "platform.h"
#include "run_world_bridge.h"
#include "presentation_world_bridge.h"
#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
typedef struct RunField {uint32_t address;size_t member;unsigned width,count;} RunField;
#define A(n) (((uint32_t)DATA_SEG<<4)+D(n))
#define MEMBER(m) offsetof(NativeRunWorld,m)
#define WORD(n,m) {A(n),MEMBER(m),2,1}
#define BYTE(n,m) {A(n),MEMBER(m),1,1}
static const RunField fields[]={
 WORD(PlayerCount,configuration.players),WORD(PlayerArrayBytes,configuration.player_bytes),
 {A(PlayerOneControlMode),MEMBER(configuration.control_mode),2,2},
 WORD(SelectedDifficulty,configuration.difficulty),WORD(CurrentLevelIndex,level),
 {A(ScoreLowWord),MEMBER(score),4,1},
 BYTE(LivesRemaining,lives),BYTE(ScoreMultiplier,multiplier),BYTE(LevelCompletionMarker,completion),
 WORD(LevelTimer,timer),WORD(ScreenFadeLevel,fade_level),WORD(ScreenFadeStep,fade_step),WORD(WaterYPixels,water_y),
 /* One live record; odd field boundaries are intentional. */
 WORD(CurrentLevelRecord,record.map.value),WORD(LevelPlatformList,record.platforms.value),
 WORD(LevelActorList,record.actors.value),WORD(LevelEnemyList,record.enemies.value),
 BYTE(RemainingPassengerJourneys,record.journeys),
 {A(CurrentLevelRecord)+9,MEMBER(record.reserved_before_text),1,1},
 WORD(LevelIntroTextPointer,record.introduction.value),BYTE(LevelRainDirection,record.rain),
 WORD(LevelPlayerOneStartX,record.player_start[0][0]),WORD(LevelPlayerOneStartY,record.player_start[0][1]),
 WORD(LevelPlayerTwoStartX,record.player_start[1][0]),WORD(LevelPlayerTwoStartY,record.player_start[1][1]),
 WORD(WaterY32,record.water_fixed),WORD(WaterSurfaceStep,record.water_step),
 {A(CurrentLevelRecord)+25,MEMBER(record.reserved_tail),1,1},
 {A(Data_264C),MEMBER(tiles),1,320}
};
static unsigned active;
static int run_field(uint32_t address,unsigned *slot,unsigned *lane){
 uint32_t base=(uint32_t)DATA_SEG<<4;
 if(address<base || address-base<D(CurrentLevelIndex) || address-base>=D(WaterYPixels)+2u)return 0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)if(address>=fields[i].address && address-fields[i].address<fields[i].width*fields[i].count){*slot=i;*lane=(unsigned)(address-fields[i].address);return 1;}
 return 0;
}
static uint8_t run_field_get(const RunField *field,unsigned lane){
 const uint8_t *p=(const uint8_t*)native_run_world()+field->member;
 if(field->width==1)return p[lane];
 unsigned index=lane/field->width,shift=(lane%field->width)*8;uint32_t value=0;
 if(field->width==2){uint16_t word;memcpy(&word,p+index*2,2);value=word;}
 else memcpy(&value,p+index*4,4);
 return (uint8_t)(value>>shift);
}
static void run_field_put(const RunField *field,unsigned lane,uint8_t value){
 uint8_t *p=(uint8_t*)native_run_world()+field->member;
 if(field->width==1){p[lane]=value;return;}
 unsigned index=lane/field->width,shift=(lane%field->width)*8;uint32_t word=0;
 if(field->width==2){uint16_t old;memcpy(&old,p+index*2,2);word=old;}
 else memcpy(&word,p+index*4,4);
 word=(word&~(255u<<shift))|((uint32_t)value<<shift);
 if(field->width==2){uint16_t half=(uint16_t)word;memcpy(p+index*2,&half,2);}
 else memcpy(p+index*4,&word,4);
}
int run_is_owned(uint32_t address){unsigned slot,lane;return active && run_field(address,&slot,&lane);}
int run_shared_read(uint32_t address,uint8_t *value){unsigned slot,lane;if(!active || !run_field(address,&slot,&lane))return 0;*value=run_field_get(fields+slot,lane);return 1;}
int run_shared_write(uint32_t address,uint8_t value){
 unsigned slot,lane;if(!active || !run_field(address,&slot,&lane))return 0;
#if RUN_TEST_FAULT == 1
 if(address==A(ScoreLowWord))return 1;
#elif RUN_TEST_FAULT == 2
 if(address==A(ScoreLowWord))address=A(ScoreHighWord);
 else if(address==A(ScoreHighWord))address=A(ScoreLowWord);
 if(!run_field(address,&slot,&lane))return 0;
#elif RUN_TEST_FAULT == 3
 if(address==A(PlayerTwoControlMode))return 1;
#elif RUN_TEST_FAULT == 4
 if(address==A(PlayerArrayBytes))value=(uint8_t)(native_run_world()->configuration.players*2);
#elif RUN_TEST_FAULT == 5
 if(address==A(WaterYPixels))return 1;
#elif RUN_TEST_FAULT == 6
 if(address==A(RemainingPassengerJourneys))return 1;
#elif RUN_TEST_FAULT == 7
 if(address==A(CurrentLevelRecord)+9 || address==A(CurrentLevelRecord)+25)value=0;
#elif RUN_TEST_FAULT == 8
 if(address==A(WaterY32)+1)return 1;
#endif
 run_field_put(fields+slot,lane,value);return 1;
}
unsigned run_owned_bytes(void){return active?373:0;}
void run_cold_import(uint8_t *memory){
 active=0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)run_field_put(fields+i,lane,memory[fields[i].address+lane]);
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)memset(memory+fields[i].address,0xa5,fields[i].width*fields[i].count);
 active=1;
}
void run_require_seal(const uint8_t *memory){
 if(!active)return;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)if(memory[fields[i].address+lane]!=0xa5){fputs("run: sealed RAM violation\n",stderr);exit(88);}
}
void run_serialize(uint8_t *output){
 if(!active)return;
 unsigned emitted=0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++){
#if RUN_TEST_FAULT == 9
  if(!i && !lane)continue;
#endif
  output[fields[i].address+lane]=run_field_get(fields+i,lane);emitted++;
 }
 if(emitted!=run_owned_bytes()){fputs("run: missed serialization\n",stderr);exit(88);}
}
uint32_t run_check_serialization(const uint8_t *output){
 if(active)for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)if(output[fields[i].address+lane]!=run_field_get(fields+i,lane))return fields[i].address+lane;
 return UINT32_MAX;
}
uint8_t run_borrowed_byte(const uint8_t *window,uint32_t index){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE){uint8_t value;if(run_shared_read((uint32_t)(p-base+index),&value))return value;}
 return presentation_borrowed_byte(window,index);
}
void run_borrowed_store(uint8_t *window,uint32_t index,uint8_t value){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE && run_shared_write((uint32_t)(p-base+index),value))return;
 presentation_borrowed_store(window,index,value);
}
uint32_t run_borrow_read(RunBorrower borrower,uint16_t bank,uint16_t position,unsigned width){
 if(borrower>=RUN_BORROW_COUNT || (width!=1 && width!=2 && width!=4)){fputs("run: invalid borrower\n",stderr);exit(88);}
 uint32_t result=0,address=lin(bank,position);
 for(unsigned i=0;i<width;i++){uint8_t byte;if(!run_shared_read(address+i,&byte))byte=ugh_read(address+i);result|=(uint32_t)byte<<(8*i);}
#if RUN_TEST_FAULT == 10
 if(borrower==RUN_BORROW_INPUT && width==2 && address>=A(PlayerOneControlMode) && address<A(PlayerTwoControlMode)+2u)result&=255u;
#endif
 return result;
}
void run_borrow_write(RunBorrower borrower,uint16_t bank,uint16_t position,unsigned width,uint32_t value){
 if(borrower>=RUN_BORROW_COUNT || (width!=1 && width!=2 && width!=4)){fputs("run: invalid borrower\n",stderr);exit(88);}
 uint32_t address=lin(bank,position);
 for(unsigned i=0;i<width;i++)if(!run_shared_write(address+i,(uint8_t)(value>>(8*i))))ugh_write(address+i,(uint8_t)(value>>(8*i)));
}
