/* Verification provider appended only to generated c/platform.c. */
#include "pixel_world_bridge.h"
static uint16_t pixel_control_port(PixelControlRoute route){
 switch(route){case PIXEL_SEQ_INDEX:return 0x3c4;case PIXEL_SEQ_DATA:return 0x3c5;
 case PIXEL_GC_INDEX:return 0x3ce;case PIXEL_GC_DATA:return 0x3cf;default:return 0;}
}
void pixel_service_control_write(PixelControlRoute route,uint8_t value){
 uint16_t port=pixel_control_port(route);if(!port){ugh_devices.error=1;return;}
#if PIXEL_TEST_FAULT == 1
 if(route==PIXEL_SEQ_DATA && ugh_devices.seq_index==2)value^=1;
#endif
#if PIXEL_TEST_FAULT == 2
 if(route==PIXEL_GC_DATA && ugh_devices.gc_index==4)value=0;
#endif
 platform_out(port,1,value);
}
VideoByteReply pixel_service_control_read(PixelControlRoute route){
 if(route!=PIXEL_SEQ_DATA && route!=PIXEL_GC_DATA){ugh_devices.error=1;return (VideoByteReply){0,UGH_UNSUPPORTED};}
 uint8_t value=(uint8_t)platform_in(pixel_control_port(route),1);
 return (VideoByteReply){value,ugh_devices.error?UGH_UNSUPPORTED:UGH_OK};
}
#if PIXEL_TEST_FAULT == 3
static uint8_t pixel_snapshot[4][65536];static unsigned pixel_snapshot_valid;
void pixel_test_epoch(void){memcpy(pixel_snapshot,ugh_devices.plane,sizeof pixel_snapshot);pixel_snapshot_valid=1;}
#endif
uint8_t pixel_service_read(VideoCellAddress address,PixelReadRole role){
 uint32_t physical=((uint32_t)address.bank.value<<4)+address.position;
 (void)role;
#if PIXEL_TEST_FAULT == 7
 static unsigned collision_cursor;static uint8_t last_reply;
 if(role==PIXEL_COLLISION && collision_cursor++%10==4)return last_reply;
 uint8_t value=ugh_read(physical);last_reply=value;return value;
#else
 return ugh_read(physical);
#endif
}
void pixel_service_store(VideoCellAddress address,uint8_t value){
 uint32_t physical=((uint32_t)address.bank.value<<4)+address.position;
#if PIXEL_TEST_FAULT == 4
 if(physical>=0xa0000 && physical<0xb0000 && physical-0xa0000>=0x3e80)return;
#endif
 ugh_write(physical,value);
}
uint8_t pixel_service_copy(VideoCellAddress source,VideoCellAddress destination){
#if PIXEL_TEST_FAULT == 3
 if(!pixel_snapshot_valid)pixel_test_epoch();
 uint32_t physical=((uint32_t)source.bank.value<<4)+source.position;
 uint8_t live[4];unsigned offset=physical&65535u,aperture=physical>=0xa0000 && physical<0xb0000;
 if(aperture)for(unsigned p=0;p<4;p++){live[p]=ugh_devices.plane[p][offset];ugh_devices.plane[p][offset]=pixel_snapshot[p][offset];}
#endif
 uint8_t value=pixel_service_read(source,PIXEL_SOURCE);
#if PIXEL_TEST_FAULT == 3
 if(aperture)for(unsigned p=0;p<4;p++)ugh_devices.plane[p][offset]=live[p];
#endif
 pixel_service_store(destination,value);return value;
}
uint8_t pixel_service_water_mark(VideoCellAddress address){
 uint8_t value=pixel_service_read(address,PIXEL_SOURCE);
#if PIXEL_TEST_FAULT != 6
 pixel_service_store(address,0x40);
#endif
 return value;
}
int pixel_service_continuation(PixelContinuationKind kind,PixelExternalBinding binding,
 uint16_t return_identity,PixelServiceContext *context){
 if(!context)return UGH_BAD_CALLBACK;
 Regs *r=(Regs*)context;
 if(binding.first!=r->cs)return UGH_BAD_CALLBACK;
 if(kind==PIXEL_EXTERNAL_NEAR)return ugh_call_near(binding.second,return_identity,r);
 if(kind==PIXEL_EXTERNAL_TAIL)return ugh_dispatch(binding.first,binding.second,r);
 return UGH_BAD_CALLBACK;
}
void pixel_service_compatibility_write(PixelExternalControlBinding binding,unsigned width,uint32_t value){
 platform_out(binding.identity,width,value);
}
