#include "ugh.h"
#include "platform.h"
uint8_t ugh_mem[UGH_MEM_SIZE];
EXPORT uint8_t *ugh_memory(void) { return ugh_mem; }
uint16_t ugh_load16(uint16_t s,uint16_t o) { return rd16(s,o); }
uint32_t ugh_load32(uint16_t s,uint16_t o) { return rd32(s,o); }
void ugh_store16(uint16_t s,uint16_t o,uint16_t v) { wr16(s,o,v); }
void ugh_store32(uint16_t s,uint16_t o,uint32_t v) { wr32(s,o,v); }
uint8_t ugh_read(uint32_t a) {
    if (a>=0xa0000u && a<0xb0000u) {
        uint16_t o=(uint16_t)a;
        for(unsigned p=0;p<4;p++) ugh_devices.latch[p]=ugh_devices.plane[p][o];
        if(ugh_devices.gc[5]&8) {
            uint8_t result=255;
            for(unsigned p=0;p<4;p++) if(ugh_devices.gc[7]&(1u<<p))
                result&=ugh_devices.latch[p] ^ (ugh_devices.gc[2]&(1u<<p)?0:255);
            return result;
        }
        return ugh_devices.latch[ugh_devices.read_map&3u];
    }
    return ugh_mem[a];
}
void ugh_write(uint32_t a, uint8_t v) {
    if (a>=0xa0000u && a<0xb0000u) {
        unsigned rotate=ugh_devices.gc[3]&7,mode=ugh_devices.gc[5]&3;
        unsigned op=(ugh_devices.gc[3]>>3)&3;
        uint8_t rotated=(uint8_t)((v>>rotate)|(v<<(8-rotate)));
        for(unsigned p=0;p<4;p++) if(ugh_devices.map_mask&(1u<<p)) {
            uint8_t latch=ugh_devices.latch[p],mask=ugh_devices.gc[8],source,result;
            if(mode==1) result=latch;
            else {
                if(mode==0) source=ugh_devices.gc[1]&(1u<<p)?(ugh_devices.gc[0]&(1u<<p)?255:0):rotated;
                else if(mode==2) source=v&(1u<<p)?255:0;
                else { source=ugh_devices.gc[0]&(1u<<p)?255:0; mask&=rotated; }
                if(op==1) source&=latch;
                else if(op==2) source|=latch;
                else if(op==3) source^=latch;
                result=(uint8_t)((source&mask)|(latch&~mask));
            }
            ugh_devices.plane[p][(uint16_t)a]=result;
        }
    } else ugh_mem[a]=v;
}
