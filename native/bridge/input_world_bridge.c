#include "platform.h"
#include "input_world_bridge.h"
#include "palette_world_bridge.h"
#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
typedef struct InputField {uint32_t address;size_t member;unsigned width,count;} InputField;
#define A(n) (((uint32_t)DATA_SEG<<4)+D(n))
#define MEMBER(m) ((size_t)&((NativeInputWorld*)0)->m)
#define B(n,m) {A(n),MEMBER(m),2,1}
#define J(i,n,m) B(n,joysticks[i].m)
static const InputField fields[]={
 {((uint32_t)GAME_SEG<<4)+G(LatestInterruptScanCode),MEMBER(latest),1,1},
 B(CurrentKeyboardScanCode,current_scan_storage),
 {A(PreviousPolledScanCode),MEMBER(previous),1,1},
 {A(KeyboardScanCodeChangeBits),MEMBER(change),1,1},
 {A(KeyboardSequenceIndex),MEMBER(index),1,1},
 B(JoystickEnabledAxisMask,enabled_axis_storage),
 B(JoystickSampleLoopLimit,loop_limit),
 J(0,JoystickPresentFlags,present),J(1,SecondJoystickPresent,present),
 J(0,FirstJoystickXCount,x),J(1,SecondJoystickXCount,x),
 J(0,FirstJoystickYCount,y),J(1,SecondJoystickYCount,y),
 J(0,JoystickButtonBits,buttons),J(1,SecondJoystickButtonBits,buttons),
 J(0,FirstJoystickXDoubleCenter,double_x),J(1,SecondJoystickXDoubleCenter,double_x),
 J(0,FirstJoystickYDoubleCenter,double_y),J(1,SecondJoystickYDoubleCenter,double_y),
 J(0,JoystickLeftThresholds,left),J(1,SecondJoystickXLowThreshold,left),
 J(0,JoystickRightThresholds,right),J(1,SecondJoystickXHighThreshold,right),
 J(0,JoystickUpThresholds,up),J(1,SecondJoystickYLowThreshold,up),
 J(0,JoystickDownThresholds,down),J(1,SecondJoystickYHighThreshold,down),
 {A(ds_3321),MEMBER(calibration_reset_words),2,4},
 {A(KeyboardSequenceRecords),MEMBER(sequence),1,205},
 B(PreviousKeyboardVector,saved_keyboard.first),B(PreviousKeyboardVectorSegment,saved_keyboard.second)
};
#undef J
#undef B
#undef A
static unsigned active;
static int input_field(uint32_t address,unsigned *slot,unsigned *lane){
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)if(address>=fields[i].address && address-fields[i].address<fields[i].width*fields[i].count){*slot=i;*lane=(unsigned)(address-fields[i].address);return 1;}
 return 0;
}
static uint8_t input_field_get(const InputField *field,unsigned lane){
 const uint8_t *p=(const uint8_t*)native_input_world()+field->member;
 if(field->width==1)return p[lane];
 uint16_t word;memcpy(&word,p+(lane/2)*2,2);return (uint8_t)(word>>((lane&1)*8));
}
static void input_field_put(const InputField *field,unsigned lane,uint8_t value){
 uint8_t *p=(uint8_t*)native_input_world()+field->member;
 if(field->width==1){p[lane]=value;return;}
 unsigned shift=(lane&1)*8;uint16_t word;memcpy(&word,p+(lane/2)*2,2);
 word=(uint16_t)((word&~(255u<<shift))|((unsigned)value<<shift));memcpy(p+(lane/2)*2,&word,2);
}
int input_is_owned(uint32_t address){unsigned slot,lane;return active && input_field(address,&slot,&lane);}
int input_shared_read(uint32_t address,uint8_t *value){unsigned slot,lane;if(!active || !input_field(address,&slot,&lane))return 0;*value=input_field_get(fields+slot,lane);return 1;}
int input_shared_write(uint32_t address,uint8_t value){unsigned slot,lane;if(!active || !input_field(address,&slot,&lane))return 0;input_field_put(fields+slot,lane,value);return 1;}
unsigned input_owned_bytes(void){return active?267:0;}
void input_cold_import(uint8_t *memory){
 active=0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)input_field_put(fields+i,lane,memory[fields[i].address+lane]);
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)memset(memory+fields[i].address,0xa5,fields[i].width*fields[i].count);
 active=1;
}
void input_require_seal(const uint8_t *memory){
 if(!active)return;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)if(memory[fields[i].address+lane]!=0xa5){fputs("input: sealed RAM violation\n",stderr);abort();}
}
void input_serialize(uint8_t *output){
 if(!active)return;
 unsigned emitted=0;
 for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++){
#if INPUT_TEST_FAULT == 5
  if(!i && !lane)continue;
#endif
  output[fields[i].address+lane]=input_field_get(fields+i,lane);emitted++;
 }
 if(emitted!=input_owned_bytes()){fputs("input: missed serialization\n",stderr);exit(88);}
}
uint32_t input_check_serialization(const uint8_t *output){
 if(active)for(unsigned i=0;i<sizeof fields/sizeof *fields;i++)for(unsigned lane=0;lane<fields[i].width*fields[i].count;lane++)if(output[fields[i].address+lane]!=input_field_get(fields+i,lane))return fields[i].address+lane;
 return UINT32_MAX;
}
uint8_t input_borrowed_byte(const uint8_t *window,uint32_t index){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE){uint8_t value;if(input_shared_read((uint32_t)(p-base+index),&value))return value;}
 return palette_borrowed_byte(window,index);
}
void input_borrowed_store(uint8_t *window,uint32_t index,uint8_t value){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE && input_shared_write((uint32_t)(p-base+index),value))return;
 palette_borrowed_store(window,index,value);
}
int input_peer_deliver(InputPeerRole role,uint16_t return_identity,Regs *r){
 if(r->cs!=GAME_SEG)return UGH_BAD_CALLBACK;
 r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,return_identity);int status;
 switch(role){
 case INPUT_PEER_PollKeyboardScanChange:status=c_PollKeyboardScanChange(r);break;
 case INPUT_PEER_SampleJoystickAxesAndButtons:status=c_SampleJoystickAxesAndButtons(r);break;
 case INPUT_PEER_WaitNextVerticalRetrace:status=c_WaitNextVerticalRetrace(r);break;
 default:return UGH_BAD_CALLBACK;
 }
 if(status)return status;
 r->sp=(uint16_t)(r->sp+2);return UGH_OK;
}
int input_editor_queue(Regs *r){
 if((r->ax>>8)>1)return UGH_UNSUPPORTED;
 InputQueueOperation operation=(r->ax>>8)?INPUT_QUEUE_PEEK:INPUT_QUEUE_TAKE;
 InputQueueReply reply=input_service_queue(operation,(InputServiceContext*)r);
 if(!reply.status){r->ax=reply.word;if(operation==INPUT_QUEUE_PEEK)flag(r,ZF,!reply.present);}
 return reply.status;
}
int input_capture_keyboard(Regs *r){
 InputVectorReply reply=input_service_vector(INPUT_VECTOR_CAPTURE,(InputKeyboardBinding){0,0},(InputServiceContext*)r);
 if(!reply.status){r->bx=reply.binding.first;r->es=reply.binding.second;}
 return reply.status;
}
