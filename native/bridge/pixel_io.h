#ifndef PIXEL_IO_H
#define PIXEL_IO_H
#include "platform.h"
#ifdef UGH_NATIVE_PIXEL
#include "pixel_world_bridge.h"
static inline PixelControlRoute pixel_route(uint16_t port){
 switch(port){case 0x3c4:return PIXEL_SEQ_INDEX;case 0x3c5:return PIXEL_SEQ_DATA;
 case 0x3ce:return PIXEL_GC_INDEX;case 0x3cf:return PIXEL_GC_DATA;default:return PIXEL_INVALID_CONTROL;}
}
static inline void pixel_out(uint16_t port,unsigned width,uint32_t value){
 PixelControlRoute route=pixel_route(port);
 if(width==1 && route!=PIXEL_INVALID_CONTROL)pixel_service_control_write(route,(uint8_t)value);
 else pixel_service_compatibility_write((PixelExternalControlBinding){port},width,value);
}
static inline uint32_t pixel_in(uint16_t port,unsigned width){return pixel_service_control_read(width==1?pixel_route(port):PIXEL_INVALID_CONTROL).value;}
static inline uint8_t pixel_read(uint16_t bank,uint16_t position){return pixel_service_read((VideoCellAddress){{bank},position},PIXEL_SOURCE);}
static inline void pixel_store(uint16_t bank,uint16_t position,uint8_t value){pixel_service_store((VideoCellAddress){{bank},position},value);}
static inline uint8_t pixel_copy(uint16_t from_bank,uint16_t from,uint16_t to_bank,uint16_t to){return pixel_service_copy((VideoCellAddress){{from_bank},from},(VideoCellAddress){{to_bank},to});}
static inline uint8_t pixel_mark(uint16_t bank,uint16_t position){return pixel_service_water_mark((VideoCellAddress){{bank},position});}
#define PIXEL_CALL(n,ret) pixel_peer(PIXEL_PEER_##n,ret,r)
#define PIXEL_TAIL(target) pixel_tail(target,r)
#else
static inline void pixel_out(uint16_t port,unsigned width,uint32_t value){platform_out(port,width,value);}
static inline uint32_t pixel_in(uint16_t port,unsigned width){return platform_in(port,width);}
static inline uint8_t pixel_read(uint16_t bank,uint16_t position){return rd8(bank,position);}
static inline void pixel_store(uint16_t bank,uint16_t position,uint8_t value){wr8(bank,position,value);}
static inline uint8_t pixel_copy(uint16_t from_bank,uint16_t from,uint16_t to_bank,uint16_t to){uint8_t value=rd8(from_bank,from);wr8(to_bank,to,value);return value;}
static inline uint8_t pixel_mark(uint16_t bank,uint16_t position){uint8_t value=rd8(bank,position);wr8(bank,position,0x40);return value;}
#define PIXEL_CALL(n,ret) ugh_call_near(G(n),ret,r)
#define PIXEL_TAIL(target) ugh_dispatch(r->cs,target,r)
#endif
#endif
