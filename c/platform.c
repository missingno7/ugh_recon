#include "platform.h"
#include <string.h>
Devices ugh_devices;
static FrameObserver frame_observer;
EXPORT void ugh_set_frame_observer(FrameObserver observer) { frame_observer=observer; }
int platform_frame_boundary(Regs *r) { return frame_observer?frame_observer(r):UGH_OK; }
EXPORT Devices *ugh_device_state(void) { return &ugh_devices; }
EXPORT uint32_t ugh_device_size(void) { return sizeof(Devices); }
EXPORT void ugh_devices_reset(void) {
    memset(&ugh_devices,0,sizeof ugh_devices);
    ugh_devices.map_mask=15; ugh_devices.seq[2]=15; ugh_devices.gc[8]=255;
    ugh_devices.video_mode=3; ugh_devices.video_columns=80;
}
static void log_event(unsigned kind,uint16_t port,unsigned size,uint32_t value) {
    if(ugh_devices.count>=1080000u) { ugh_devices.error=1; return; }
    IoEvent *e=&ugh_devices.log[ugh_devices.count++];
    e->kind=kind; e->port=port; e->size=size; e->value=value;
}
static InputScript *script(uint16_t port) {
    for(unsigned i=0;i<ugh_devices.script_count && i<16;i++)
        if(ugh_devices.scripts[i].port==port) return &ugh_devices.scripts[i];
    return 0;
}
static int scripted(uint16_t port,uint32_t *value,int peek) {
    InputScript *s=script(port);
    if(!s || !s->cycles_left || s->cursor>=s->count || s->cursor>=128) { ugh_devices.error=1; return UGH_UNSUPPORTED; }
    *value=s->runs[s->cursor].value;
    if(!peek && ++s->used==s->runs[s->cursor].repeat) {
        s->cursor++; s->used=0;
        if(s->cursor==s->count && s->cycles_left>1) { s->cycles_left--; s->cursor=0; }
    }
    return UGH_OK;
}
static void out_byte(uint16_t port,uint8_t v) {
    Devices *d=&ugh_devices;
    switch(port) {
    case 0x3c4: d->seq_index=v; break;
    case 0x3c5:
        if(d->seq_index<5) { d->seq[d->seq_index]=v; if(d->seq_index==2) d->map_mask=v&15; }
        else d->error=1;
        break;
    case 0x3ce: d->gc_index=v; break;
    case 0x3cf:
        if(d->gc_index<9) { d->gc[d->gc_index]=v; if(d->gc_index==4) d->read_map=v&3; }
        else d->error=1;
        break;
    case 0x3d4: d->crtc_index=v; break;
    case 0x3d5: if(d->crtc_index<25) d->crtc[d->crtc_index]=v; else d->error=1; break;
    case 0x3c0:
        if(!d->attr_phase) d->attr_index=v&31;
        else if(d->attr_index<21) d->attr[d->attr_index]=v; else d->error=1;
        d->attr_phase^=1; break;
    case 0x3c8: d->dac_index=v; d->dac_component=0; break;
    case 0x3c9:
        d->dac[3*d->dac_index+d->dac_component]=v&63;
        if(++d->dac_component==3) { d->dac_component=0; d->dac_index++; } break;
    case 0x388: d->opl_index=v; break;
    case 0x389: d->opl[d->opl_index]=v; break;
    case 0x20: if(v!=0x20) d->error=1; break;
    case 0x21: d->pic_mask=v; break;
    case 0x40:
        if(!d->pit_phase) d->pit_divisor=(uint16_t)((d->pit_divisor&0xff00)|v);
        else d->pit_divisor=(uint16_t)((d->pit_divisor&255)|((uint16_t)v<<8));
        d->pit_phase^=1; break;
    case 0x43: if(v!=0x36) d->error=1; else { d->pit_command=v; d->pit_phase=0; } break;
    case 0x02: case 0x03: {
        uint16_t *cell=port==2?&d->dma_address:&d->dma_count;
        *cell=d->dma_flip?(uint16_t)((*cell&255)|((uint16_t)v<<8)):(uint16_t)((*cell&0xff00)|v);
        d->dma_flip^=1; break;
    }
    case 0x0a: d->dma_mask=v; break;
    case 0x0b: d->dma_mode=v; break;
    case 0x0c: d->dma_flip=0; break;
    case 0x83: d->dma_page=v; break;
    case 0x201: { InputScript *s=script(port); if(!s) d->error=1;
        else { s->cursor=s->used=0; s->cycles_left=s->cycles; } break; }
    default:
        if(port>=0x206 && port<=0x26e && ((port&15)==6 || (port&15)==12) &&
           (script((uint16_t)((port&0xfff0)+12)) || script((uint16_t)((port&0xfff0)+14)))) break;
        d->error=1; break;
    }
}
void platform_out(uint16_t port,unsigned size,uint32_t value) {
    log_event(LOG_OUT,port,size,value);
    if(size!=1 && size!=2) { ugh_devices.error=1; return; }
    for(unsigned i=0;i<size;i++) out_byte((uint16_t)(port+i),(uint8_t)(value>>(8*i)));
}
uint32_t platform_in(uint16_t port,unsigned size) {
    Devices *d=&ugh_devices; uint32_t v=0;
    if(size!=1) d->error=1;
    else switch(port) {
    case 0x3c5: if(d->seq_index<5) v=d->seq[d->seq_index]; else d->error=1; break;
    case 0x3cf: if(d->gc_index<9) v=d->gc[d->gc_index]; else d->error=1; break;
    case 0x3d5: if(d->crtc_index<25) v=d->crtc[d->crtc_index]; else d->error=1; break;
    case 0x3c1: if(d->attr_index<21) v=d->attr[d->attr_index]; else d->error=1; break;
    case 0x21: v=d->pic_mask; break;
    default: scripted(port,&v,0); if(port==0x3da) d->attr_phase=0; break;
    }
    log_event(LOG_IN,port,size,v); return v;
}
static int dos_result(Regs *r,unsigned value,int error) { r->ax=(uint16_t)value; flag(r,CF,error); return UGH_OK; }
int platform_interrupt(uint8_t n,Regs *r) {
    Devices *d=&ugh_devices; uint16_t ax=r->ax; unsigned ah=ax>>8,al=ax&255,i; uint32_t v;
    log_event(LOG_DOS,n,0,ax);
    if(n==0x21 && ah==0x35) { r->bx=rd16(0,(uint16_t)(4*al)); r->es=rd16(0,(uint16_t)(4*al+2)); return UGH_OK; }
    if(n==0x21 && ah==0x25) { wr16(0,(uint16_t)(4*al),r->dx); wr16(0,(uint16_t)(4*al+2),r->ds); return UGH_OK; }
    if(n==0x21 && ah==0x2c) { if(scripted(0xfffe,&v,0)) return UGH_UNSUPPORTED; r->cx=(uint16_t)(v>>16); r->dx=(uint16_t)v; return UGH_OK; }
    if(n==0x21 && ah==0x4c) { d->exited=1; d->exit_code=(uint8_t)al; return UGH_OK; }
    if(n==0x10 && ah==0) { d->video_mode=(uint8_t)al; d->video_page=0; return UGH_OK; }
    if(n==0x10 && ah==15) { r->ax=(uint16_t)(d->video_mode+256*d->video_columns); r->bx=(uint16_t)((r->bx&255)+256*d->video_page); return UGH_OK; }
    if(n==0x16 && (ah==0 || ah==1)) {
        InputScript *s=script(0xffff);
        if(ah==1 && (!s || s->cursor==s->count)) { flag(r,ZF,1); return UGH_OK; }
        if(scripted(0xffff,&v,ah==1)) return UGH_UNSUPPORTED;
        r->ax=(uint16_t)v; if(ah==1) flag(r,ZF,0); return UGH_OK;
    }
    if(n==0x21 && ah>=0x3c && ah<=0x40) {
        if(d->dos_error) {
            if(d->dos_error_skip) d->dos_error_skip--;
            else { unsigned e=d->dos_error; d->dos_error=0; return dos_result(r,e,1); }
        }
        if(ah==0x3c || ah==0x3d) {
            uint8_t name[64]={0}; i=0;
            for(;i<63;i++) { name[i]=rd8(r->ds,(uint16_t)(r->dx+i)); if(!name[i]) break; }
            if(i==63) return dos_result(r,3,1);
            int f=-1,h=-1;
            for(i=0;i<8;i++) if(d->files[i].exists && !memcmp(d->files[i].name,name,64)) { f=(int)i; break; }
            if(f<0 && ah==0x3d) return dos_result(r,2,1);
            for(i=5;i<32;i++) if(!d->handles[i].active) { h=(int)i; break; }
            if(h<0) return dos_result(r,4,1);
            if(f<0) for(i=0;i<8;i++) if(!d->files[i].exists) { f=(int)i; break; }
            if(f<0) return dos_result(r,4,1);
            if(ah==0x3c) { memcpy(d->files[f].name,name,64); d->files[f].exists=1; d->files[f].length=0; }
            d->handles[h]=(DosHandle){1,(unsigned)f,0,ah==0x3c?2:al}; return dos_result(r,(unsigned)h,0);
        }
        if(r->bx>=32 || !d->handles[r->bx].active) return dos_result(r,6,1);
        DosHandle *h=&d->handles[r->bx]; DosFile *f=&d->files[h->file];
        if(ah==0x3e) { h->active=0; return dos_result(r,0,0); }
        unsigned len=r->cx; if(d->io_limit && len>d->io_limit) len=d->io_limit;
        if(ah==0x3f) {
            if(h->mode==1) return dos_result(r,5,1);
            unsigned available=f->length>h->position?f->length-h->position:0; if(len>available) len=available;
            for(i=0;i<len;i++) wr8(r->ds,(uint16_t)(r->dx+i),f->data[h->position+i]);
        } else {
            if(h->mode==0) return dos_result(r,5,1);
            if(h->position+len>8192) len=8192-h->position;
            for(i=0;i<len;i++) f->data[h->position+i]=rd8(r->ds,(uint16_t)(r->dx+i));
            if(!r->cx || h->position+len>f->length) f->length=h->position+len;
        }
        h->position+=len; return dos_result(r,len,0);
    }
    d->error=1; return UGH_UNSUPPORTED;
}
int platform_service_point_at(ServicePoint point,uint16_t segment,uint16_t offset,Regs *r) {
    Devices *d=&ugh_devices; (void)point;
    if(d->irq_cursor>=d->irq_count) return UGH_OK;
    IrqEvent *e=&d->irqs[d->irq_cursor];
    if(e->segment!=segment || e->offset!=offset) return UGH_OK;
    if(e->skip) { e->skip--; return UGH_OK; }
    if(!(r->flags&IF) || (d->pic_mask&(1u<<e->irq))) return UGH_OK;
    d->clocks+=e->clocks; d->irq_cursor++; log_event(LOG_IRQ,(uint16_t)e->irq,0,e->clocks);
    r->sp=(uint16_t)(r->sp-6); wr16(r->ss,r->sp,offset);
    wr16(r->ss,(uint16_t)(r->sp+2),segment); wr16(r->ss,(uint16_t)(r->sp+4),r->flags);
    r->flags&=(uint16_t)~0x300;
    uint16_t vector=(uint16_t)(4*(8+e->irq));
    return ugh_dispatch_interrupt(rd16(0,(uint16_t)(vector+2)),rd16(0,vector),r);
}
int platform_service_point(ServicePoint point,Regs *r) { return platform_service_point_at(point,r->cs,r->ip,r); }
