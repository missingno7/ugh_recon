#include "platform.h"
#include <string.h>
Devices ugh_devices;
EXPORT Devices *ugh_device_state(void) { return &ugh_devices; }
EXPORT uint32_t ugh_device_size(void) { return sizeof(Devices); }
EXPORT void ugh_devices_reset(void) {
    memset(&ugh_devices,0,sizeof ugh_devices); ugh_devices.map_mask=15;
}
static void log_event(unsigned kind,uint16_t port,unsigned size,uint32_t value) {
    if(ugh_devices.count>=270000u) { ugh_devices.error=1; return; }
    IoEvent *e=&ugh_devices.log[ugh_devices.count++];
    e->kind=kind; e->port=port; e->size=size; e->value=value;
}
static void out_byte(uint16_t port,uint8_t value) {
    switch(port) {
    case 0x3c4: ugh_devices.seq_index=value; break;
    case 0x3c5:
        if(ugh_devices.seq_index==2) ugh_devices.map_mask=value&15;
        else ugh_devices.error=1;
        break;
    case 0x20: case 0x40: case 0x43: break; /* ordered PIC/PIT transactions */
    default: ugh_devices.error=1; break;
    }
}
void platform_out(uint16_t port,unsigned size,uint32_t value) {
    log_event(LOG_OUT,port,size,value);
    for(unsigned i=0;i<size;i++) out_byte((uint16_t)(port+i),(uint8_t)(value>>(8*i)));
}
uint32_t platform_in(uint16_t port,unsigned size) {
    log_event(LOG_IN,port,size,0); ugh_devices.error=1; return 0;
}
int platform_interrupt(uint8_t n,Regs *r) {
    log_event(LOG_DOS,n,0,r->ax); ugh_devices.error=1; return UGH_UNSUPPORTED;
}
int platform_service_point(ServicePoint point,Regs *r) {
    (void)point; (void)r; return UGH_UNSUPPORTED;
}
