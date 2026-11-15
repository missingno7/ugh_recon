/* Appended to a generated c/platform.c only. The full compatibility Devices,
 * ordered I/O log and existing deterministic scheduling policy stay intact. */
#include "input_world_bridge.h"
InputByteReply input_service_scan(void){
 InputByteReply reply={(uint8_t)platform_in(0x60,1),UGH_OK};
 if(ugh_devices.error)reply.status=UGH_UNSUPPORTED;
#if INPUT_TEST_FAULT == 2
 if(reply.value!=0xe0)reply.value^=0x80;
#endif
#if INPUT_TEST_FAULT == 3
 if(reply.value==0xe0)reply.value=0;
#endif
 return reply;
}
void input_service_acknowledge_scan(void){platform_out(0x20,1,0x20);}
void input_service_joystick_start(uint8_t trigger){platform_out(0x201,1,trigger);}
InputByteReply input_service_joystick_presence(void){
 InputByteReply reply={(uint8_t)platform_in(0x201,1),UGH_OK};
 if(ugh_devices.error)reply.status=UGH_UNSUPPORTED;
 return reply;
}
InputButtonReply input_service_joystick_buttons(unsigned joystick){
 uint8_t delivered=(uint8_t)platform_in(0x201,1);
 InputButtonReply reply={input_button_bits(delivered,joystick)};return reply;
}
InputCountsReply input_service_joystick_counts(uint16_t limit,uint8_t enabled){
 InputAxisTimer work=input_axis_begin(limit,enabled);int status=UGH_OK;
 if(enabled)for(;;){
  uint8_t delivered=(uint8_t)platform_in(0x201,1);
  if(ugh_devices.error){status=UGH_UNSUPPORTED;break;}
  int again=input_axis_delivery(&work,delivered);
  if(again<0){status=UGH_BUDGET;break;}
  if(!again)break;
 }
 if(!status && ugh_devices.error)status=UGH_UNSUPPORTED;
 InputCountsReply reply={{0,0,0,0},{0,0,0,0},work.remaining,status};
 for(unsigned i=0;i<4;i++){reply.latched[i]=work.latched[i];reply.counts[i]=input_axis_count(limit,work.latched[i]);}
#if INPUT_TEST_FAULT == 4
 static unsigned have;static uint16_t stale[4];
 if(have)for(unsigned i=0;i<4;i++)reply.counts[i]=stale[i];
 else {for(unsigned i=0;i<4;i++)stale[i]=reply.counts[i];have=1;}
#endif
 return reply;
}
InputVectorReply input_service_vector(InputVectorOperation operation,InputKeyboardBinding binding,InputServiceContext *context){
 Regs local={0},*r=context?(Regs*)context:&local;
 if(operation==INPUT_VECTOR_CAPTURE)r->ax=0x3509;
 else if(operation==INPUT_VECTOR_INSTALL_HANDLER || operation==INPUT_VECTOR_RESTORE_SAVED){r->ax=0x2509;r->dx=binding.first;r->ds=binding.second;}
 else return (InputVectorReply){{0,0},UGH_UNSUPPORTED};
 int status=platform_interrupt(0x21,r);
 return (InputVectorReply){{r->bx,r->es},status};
}
uint16_t input_service_queue_flush(void){uint16_t tail=rd16(0x40,0x1c);wr16(0x40,0x1a,tail);return tail;}
InputQueueReply input_service_queue(InputQueueOperation operation,InputServiceContext *context){
 if(operation!=INPUT_QUEUE_PEEK && operation!=INPUT_QUEUE_TAKE)return (InputQueueReply){0,0,UGH_UNSUPPORTED};
 Regs local={0},*r=context?(Regs*)context:&local;
 set_ah(r,operation==INPUT_QUEUE_PEEK?1:0);int status=platform_interrupt(0x16,r);
 return (InputQueueReply){r->ax,(uint8_t)(operation==INPUT_QUEUE_PEEK?!(r->flags&ZF):!status),status};
}
int input_service_poll(InputPollCut cut,InputServiceContext *context){
 if(!context || (cut!=INPUT_POLL_SCAN && cut!=INPUT_POLL_WAIT))return UGH_UNSUPPORTED;
 Regs *r=(Regs*)context;
 return platform_service_point_at(SERVICE_IO,r->cs,cut==INPUT_POLL_SCAN?G(PollKeyboardScanChange):(uint16_t)(G(loc_44DE)+11),r);
}
