#include "platform.h"
#include "front_end_world_bridge.h"
#include "enemy_world_bridge.h"
#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
typedef struct FrontEndField {uint32_t address;size_t member;unsigned width,count,stride;} FrontEndField;
#define A(n) (((uint32_t)DATA_SEG<<4)+D(n))
#define BYTES(n,m,w) {A(n),offsetof(NativeFrontEndWorld,m),1,w,1}
static const FrontEndField fields[]={
 BYTES(HighScoreRows,score_rows,107),
 BYTES(HighScoreNameEntry,name_entry,13),
 BYTES(PasswordEditBuffer,password,21),
 BYTES(LevelNumberTensCharacter,level_characters,2),
 BYTES(HighScoreRowStride,row_stride,1),
 BYTES(HighScoreFileHandle,file_handle_bytes,2),
 {A(Text_0AE4)+41,offsetof(NativeFrontEndWorld,difficulty_text),1,6,1},
 {A(Text_0AE4)+53,offsetof(NativeFrontEndWorld,players_text),1,10,1},
 {A(Text_0B64)+15,offsetof(NativeFrontEndWorld,control_text[0]),1,10,1},
 {A(Text_0B64)+41,offsetof(NativeFrontEndWorld,control_text[1]),1,10,1},
};
static unsigned active;
static int frontend_field(uint32_t address,unsigned *slot,unsigned *lane){
 uint32_t base=(uint32_t)DATA_SEG<<4;
 if(address<base || address-base>0xcf1)return 0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)if(address>=fields[i].address && address-fields[i].address<fields[i].width*fields[i].count){*slot=i;*lane=(unsigned)(address-fields[i].address);return 1;}
 return 0;
}
static uint8_t frontend_field_get(const FrontEndField *field,unsigned lane){
 const uint8_t *p=(const uint8_t*)native_front_end_world()+field->member;
 if(field->width==1)return p[lane];
 unsigned index=lane/field->width,shift=(lane%field->width)*8;uint32_t value=0;
 if(field->width==2){uint16_t word;memcpy(&word,p+index*field->stride,2);value=word;}
 else memcpy(&value,p+index*field->stride,4);

 return (uint8_t)(value>>shift);
}
static void frontend_field_put(const FrontEndField *field,unsigned lane,uint8_t value){
 uint8_t *p=(uint8_t*)native_front_end_world()+field->member;
 if(field->width==1){p[lane]=value;return;}
 unsigned index=lane/field->width,shift=(lane%field->width)*8;uint32_t word=0;
 if(field->width==2){uint16_t old;memcpy(&old,p+index*field->stride,2);word=old;}
 else memcpy(&word,p+index*field->stride,4);
 word=(word&~(255u<<shift))|((uint32_t)value<<shift);
 if(field->width==2){uint16_t half=(uint16_t)word;memcpy(p+index*field->stride,&half,2);}
 else memcpy(p+index*field->stride,&word,4);
}
int frontend_is_owned(uint32_t address){unsigned slot,lane;return active && frontend_field(address,&slot,&lane);}
int frontend_shared_read(uint32_t address,uint8_t *value){unsigned slot,lane;if(!active || !frontend_field(address,&slot,&lane))return 0;*value=frontend_field_get(fields+slot,lane);return 1;}
int frontend_shared_write(uint32_t address,uint8_t value){
 unsigned slot,lane;if(!active || !frontend_field(address,&slot,&lane))return 0;
#if FRONTEND_TEST_FAULT == 1
 if(slot==0 && lane>=100)return 1;
#elif FRONTEND_TEST_FAULT == 2
 if(slot==2 && lane>=2)lane-=2;
#elif FRONTEND_TEST_FAULT == 3
 if(slot==5 && !lane)frontend_field_put(fields+slot,1,0);
#endif
 frontend_field_put(fields+slot,lane,value);return 1;
}
unsigned frontend_owned_bytes(void){return active?182:0;}
void frontend_cold_import(uint8_t *memory){
 active=0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)frontend_field_put(fields+i,lane,memory[fields[i].address+lane]);
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)memset(memory+fields[i].address,0xa5,fields[i].width*fields[i].count);
 active=1;
}
void frontend_require_seal(const uint8_t *memory){
 if(!active)return;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)if(memory[fields[i].address+lane]!=0xa5){fputs("frontend: sealed RAM violation\n",stderr);exit(88);}
}
void frontend_serialize(uint8_t *output){
 if(!active)return;
 unsigned emitted=0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++){
#if FRONTEND_TEST_FAULT == 4
  if(!i && !lane)continue;
#endif
  output[fields[i].address+lane]=frontend_field_get(fields+i,lane);emitted++;
 }
 if(emitted!=frontend_owned_bytes()){fputs("frontend: missed serialization\n",stderr);exit(88);}
}
uint32_t frontend_check_serialization(const uint8_t *output){
 if(active)for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)if(output[fields[i].address+lane]!=frontend_field_get(fields+i,lane))return fields[i].address+lane;
 return UINT32_MAX;
}
uint8_t frontend_borrowed_byte(const uint8_t *window,uint32_t index){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE){uint8_t value;if(frontend_shared_read((uint32_t)(p-base+index),&value))return value;}
 return enemies_borrowed_byte(window,index);
}
void frontend_borrowed_store(uint8_t *window,uint32_t index,uint8_t value){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE && frontend_shared_write((uint32_t)(p-base+index),value))return;
 enemies_borrowed_store(window,index,value);
}
uint32_t frontend_borrow_read(FrontEndBorrower borrower,uint16_t bank,uint16_t position,unsigned width){
 if(borrower>=FRONTEND_BORROW_COUNT || (width!=1 && width!=2 && width!=4)){fputs("frontend: invalid borrower\n",stderr);exit(88);}
 uint32_t result=0,address=lin(bank,position);
 for(unsigned i=0;i<width;i++){uint8_t byte;if(!frontend_shared_read(address+i,&byte))byte=ugh_read(address+i);result|=(uint32_t)byte<<(8*i);}

 return result;
}
void frontend_borrow_write(FrontEndBorrower borrower,uint16_t bank,uint16_t position,unsigned width,uint32_t value){
 if(borrower>=FRONTEND_BORROW_COUNT || (width!=1 && width!=2 && width!=4)){fputs("frontend: invalid borrower\n",stderr);exit(88);}
 uint32_t address=lin(bank,position);
 for(unsigned i=0;i<width;i++)if(!frontend_shared_write(address+i,(uint8_t)(value>>(8*i))))ugh_write(address+i,(uint8_t)(value>>(8*i)));
}
