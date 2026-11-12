#include "ugh.h"
#include "platform.h"
uint8_t ugh_mem[UGH_MEM_SIZE];
EXPORT uint8_t *ugh_memory(void) { return ugh_mem; }
uint8_t ugh_read(uint32_t a) {
    if (a>=0xa0000u && a<0xb0000u) {
        uint16_t o=(uint16_t)a;
        for(unsigned p=0;p<4;p++) ugh_devices.latch[p]=ugh_devices.plane[p][o];
        return ugh_devices.latch[ugh_devices.read_map&3u];
    }
    return ugh_mem[a];
}
void ugh_write(uint32_t a, uint8_t v) {
    if (a>=0xa0000u && a<0xb0000u) {
        for(unsigned p=0;p<4;p++)
            if (ugh_devices.map_mask&(1u<<p)) ugh_devices.plane[p][(uint16_t)a]=v;
    } else ugh_mem[a]=v;
}
