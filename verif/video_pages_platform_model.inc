/* Verification provider, appended to generated c/platform.c. No game state. */
#include "video_pages_bridge.h"
static uint16_t video_control_port(VideoControlRoute route){
 switch(route){
 case VIDEO_SEQ_INDEX:return 0x3c4;case VIDEO_SEQ_DATA:return 0x3c5;
 case VIDEO_CRTC_INDEX:return 0x3d4;case VIDEO_CRTC_DATA:return 0x3d5;
 case VIDEO_ATTRIBUTE_WRITE:return 0x3c0;case VIDEO_ATTRIBUTE_READ:return 0x3c1;
 default:return 0;
 }
}
void video_service_control_write(VideoControlRoute route,uint8_t value){
 uint16_t port=video_control_port(route);
 if(!port || route==VIDEO_ATTRIBUTE_READ){ugh_devices.error=1;return;}
#if VIDEO_TEST_FAULT == 1
 if(route==VIDEO_SEQ_DATA && ugh_devices.seq_index==2)value^=1;
#endif
 platform_out(port,1,value);
}
VideoByteReply video_service_control_read(VideoControlRoute route){
 if(route!=VIDEO_SEQ_DATA && route!=VIDEO_CRTC_DATA && route!=VIDEO_ATTRIBUTE_READ){ugh_devices.error=1;return (VideoByteReply){0,UGH_UNSUPPORTED};}
 uint8_t value=(uint8_t)platform_in(video_control_port(route),1);
 return (VideoByteReply){value,ugh_devices.error?UGH_UNSUPPORTED:UGH_OK};
}
#if VIDEO_TEST_FAULT == 3
static uint8_t video_snapshot[4][65536];static unsigned video_snapshot_valid;
static void video_capture_snapshot(void){memcpy(video_snapshot,ugh_devices.plane,sizeof video_snapshot);video_snapshot_valid=1;}
#endif
uint8_t video_service_source_byte(VideoCellAddress address){
 uint32_t a=((uint32_t)address.bank.value<<4)+address.position;
#if VIDEO_TEST_FAULT == 2
 ugh_devices.read_map=0;
#endif
#if VIDEO_TEST_FAULT == 3
 if(!video_snapshot_valid)video_capture_snapshot();
 if(a>=0xa0000 && a<0xb0000){
  unsigned offset=(unsigned)(a-0xa0000);uint8_t live[4];
  for(unsigned p=0;p<4;p++){live[p]=ugh_devices.plane[p][offset];ugh_devices.plane[p][offset]=video_snapshot[p][offset];}
  uint8_t value=ugh_read(a);
  for(unsigned p=0;p<4;p++)ugh_devices.plane[p][offset]=live[p];
  return value;
 }
#endif
 return ugh_read(a);
}
void video_service_store_byte(VideoCellAddress address,uint8_t value){
 uint32_t a=((uint32_t)address.bank.value<<4)+address.position;
#if VIDEO_TEST_FAULT == 4
 if(a>=0xa0000 && a<0xb0000 && a-0xa0000>=0x3e80)return;
#endif
 ugh_write(a,value);
}
void video_service_store_word(VideoCellAddress address,uint16_t value){
 uint32_t a=((uint32_t)address.bank.value<<4)+address.position;
#if VIDEO_TEST_FAULT == 4
 if(a>=0xa0000 && a<0xb0000 && a-0xa0000>=0x3e80)return;
#endif
 ugh_write(a,(uint8_t)value);ugh_write(a+1,(uint8_t)(value>>8));
}
VideoByteReply video_service_retrace_level(void){
 uint8_t value=(uint8_t)platform_in(0x3da,1);
 return (VideoByteReply){value,ugh_devices.error?UGH_UNSUPPORTED:UGH_OK};
}
int video_service_cut(VideoServiceCut cut,VideoServiceContext *context){
 if(!context || (cut!=VIDEO_CUT_ACTIVE_RETRACE && cut!=VIDEO_CUT_INPUT_TIMEOUT))return UGH_UNSUPPORTED;
 Regs *r=(Regs*)context;
 return platform_service_point_at(cut==VIDEO_CUT_ACTIVE_RETRACE?SERVICE_RETRACE:SERVICE_IO,r->cs,cut==VIDEO_CUT_ACTIVE_RETRACE?G(WaitVerticalRetraceActive):G(loc_449B),r);
}
int video_service_frame_end(VideoServiceContext *context){
 if(!context)return UGH_UNSUPPORTED;
#if VIDEO_TEST_FAULT == 3
 video_capture_snapshot();
#endif
 return platform_frame_boundary((Regs*)context);
}
