/* Deterministic fixtures. No device service owns original game state. */
#ifndef UGH_PLATFORM_H
#define UGH_PLATFORM_H
#include "ugh.h"
enum { LOG_OUT=1,LOG_IN=2,LOG_DOS=3,LOG_IRQ=4 };
typedef struct IoEvent { uint32_t kind,port,size,value; } IoEvent;
typedef struct ScriptRun { uint32_t value,repeat; } ScriptRun;
typedef struct InputScript {
    uint32_t port,count,cursor,used; ScriptRun runs[128];
    uint32_t cycles,cycles_left;
} InputScript;
typedef struct IrqEvent { uint32_t segment,offset,skip,irq,clocks; } IrqEvent;
typedef struct DosFile { uint8_t name[64],data[8192]; uint32_t exists,length; } DosFile;
typedef struct DosHandle { uint32_t active,file,position,mode; } DosHandle;
typedef struct Devices {
    uint8_t plane[4][65536],latch[4];
    uint8_t seq_index,map_mask,gc_index,read_map;
    uint8_t gc[9],seq[5],crtc[25],attr[21],dac[768];
    uint8_t crtc_index,attr_index,attr_phase,dac_index,dac_component,opl_index;
    uint8_t opl[256],pic_mask,dma_flip,dma_mode,dma_mask,dma_page;
    uint16_t dma_address,dma_count,pit_divisor;
    uint8_t pit_phase,pit_command,video_mode,video_page,video_columns,exit_code,exited;
    uint32_t clocks,script_count; InputScript scripts[16];
    uint32_t irq_count,irq_cursor; IrqEvent irqs[64];
    DosFile files[8]; DosHandle handles[32];
    uint32_t io_limit,dos_error,dos_error_skip;
    uint32_t count,error; IoEvent log[1080000];
} Devices;
extern Devices ugh_devices;
EXPORT void platform_out(uint16_t port,unsigned size,uint32_t value);
EXPORT uint32_t platform_in(uint16_t port,unsigned size);
EXPORT int platform_interrupt(uint8_t number,Regs *r);
/* Read-only differential observer; a nonzero result is a diagnostic stop. */
typedef int (*FrameObserver)(Regs *r);
EXPORT void ugh_set_frame_observer(FrameObserver observer);
int platform_frame_boundary(Regs *r);
typedef enum ServicePoint { SERVICE_RETRACE,SERVICE_TIMER_WAIT,SERVICE_IO } ServicePoint;
int platform_service_point(ServicePoint point,Regs *r);
EXPORT int platform_service_point_at(ServicePoint point,uint16_t segment,uint16_t offset,Regs *r);
#endif
