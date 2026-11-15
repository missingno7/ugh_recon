#include "platform.h"
#include "video_pages_bridge.h"
#include "input_world_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned active;
static int video_pages_index(uint32_t address,unsigned *index){
 uint32_t base=lin(GAME_SEG,G(PlayfieldHeight));
 if(address<base || address-base>=20)return 0;
 *index=(unsigned)(address-base);return 1;
}
static uint16_t video_pages_get_word(unsigned index){
 NativeVideoPages *p=native_video_pages();
 switch(index){
 case 0:return p->height;case 1:return p->copy_count;
 case 2:return p->fixed.position;case 3:return p->fixed.bank.value;
 case 4:return p->displayed.position;case 5:return p->displayed.bank.value;
 case 6:return p->draw.position;case 7:return p->draw.bank.value;
 case 8:return p->background.position;default:return p->background.bank.value;
 }
}
static void video_pages_put_word(unsigned index,uint16_t value){
 NativeVideoPages *p=native_video_pages();
 switch(index){
 case 0:p->height=value;break;case 1:p->copy_count=value;break;
 case 2:p->fixed.position=value;break;case 3:p->fixed.bank.value=value;break;
 case 4:p->displayed.position=value;break;case 5:p->displayed.bank.value=value;break;
 case 6:p->draw.position=value;break;case 7:p->draw.bank.value=value;break;
 case 8:p->background.position=value;break;default:p->background.bank.value=value;break;
 }
}
int video_pages_is_owned(uint32_t address){unsigned i;return active && video_pages_index(address,&i);}
int video_pages_shared_read(uint32_t address,uint8_t *value){unsigned i;if(!active || !video_pages_index(address,&i))return 0;*value=(uint8_t)(video_pages_get_word(i/2)>>((i&1)*8));return 1;}
int video_pages_shared_write(uint32_t address,uint8_t value){
 unsigned i;if(!active || !video_pages_index(address,&i))return 0;
 unsigned shift=(i&1)*8;uint16_t word=video_pages_get_word(i/2);
 video_pages_put_word(i/2,(uint16_t)((word&~(255u<<shift))|((unsigned)value<<shift)));return 1;
}
unsigned video_pages_owned_bytes(void){return active?20:0;}
void video_pages_cold_import(uint8_t *memory){
 active=0;uint32_t base=lin(GAME_SEG,G(PlayfieldHeight));
 for(unsigned i=0;i<10;i++)video_pages_put_word(i,(uint16_t)(memory[base+i*2]|memory[base+i*2+1]*256u));
 for(unsigned i=0;i<20;i++)memory[base+i]=0xa5;
 active=1;
}
void video_pages_require_seal(const uint8_t *memory){
 if(!active)return;
 uint32_t base=lin(GAME_SEG,G(PlayfieldHeight));
 for(unsigned i=0;i<20;i++)if(memory[base+i]!=0xa5){fputs("video pages: sealed RAM violation\n",stderr);abort();}
}
void video_pages_serialize(uint8_t *output){
 if(!active)return;
 uint32_t base=lin(GAME_SEG,G(PlayfieldHeight));unsigned emitted=0;
 for(unsigned i=0;i<20;i++){
#if VIDEO_TEST_FAULT == 6
  if(!i)continue;
#endif
  output[base+i]=(uint8_t)(video_pages_get_word(i/2)>>((i&1)*8));emitted++;
 }
 if(emitted!=video_pages_owned_bytes()){fputs("video pages: missed serialization\n",stderr);exit(88);}
}
uint32_t video_pages_check_serialization(const uint8_t *output){
 if(active){uint32_t base=lin(GAME_SEG,G(PlayfieldHeight));for(unsigned i=0;i<20;i++)if(output[base+i]!=(uint8_t)(video_pages_get_word(i/2)>>((i&1)*8)))return base+i;}
 return UINT32_MAX;
}
uint8_t video_pages_borrowed_byte(const uint8_t *window,uint32_t index){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE){uint8_t value;if(video_pages_shared_read((uint32_t)(p-base+index),&value))return value;}
 return input_borrowed_byte(window,index);
}
void video_pages_borrowed_store(uint8_t *window,uint32_t index,uint8_t value){
 size_t p=(size_t)window,base=(size_t)ugh_mem;
 if(p>=base && p-base+index<UGH_MEM_SIZE && video_pages_shared_write((uint32_t)(p-base+index),value))return;
 input_borrowed_store(window,index,value);
}
int video_pages_peer(VideoPeerRole role,uint16_t return_identity,Regs *r){
 if(r->cs!=GAME_SEG)return UGH_BAD_CALLBACK;
 r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,return_identity);int status;
 switch(role){
 case VIDEO_PEER_BlackenVgaPalette:status=c_BlackenVgaPalette(r);break;
 case VIDEO_PEER_EnableAllVgaWritePlanes:status=c_EnableAllVgaWritePlanes(r);break;
 case VIDEO_PEER_ClearAllVgaPlanes:status=c_ClearAllVgaPlanes(r);break;
 case VIDEO_PEER_WaitNextVerticalRetrace:status=c_WaitNextVerticalRetrace(r);break;
 case VIDEO_PEER_WaitVerticalRetraceActive:status=c_WaitVerticalRetraceActive(r);break;
 case VIDEO_PEER_WaitVerticalRetraceInactive:status=c_WaitVerticalRetraceInactive(r);break;
 case VIDEO_PEER_PollKeyboardScanChange:status=c_PollKeyboardScanChange(r);break;
 case VIDEO_PEER_SampleJoystickAxesAndButtons:status=c_SampleJoystickAxesAndButtons(r);break;
 default:return UGH_BAD_CALLBACK;
 }
 if(status)return status;
 r->sp=(uint16_t)(r->sp+2);return UGH_OK;
}
