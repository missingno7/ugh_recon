#include "backend.h"
#include <string.h>
void gs_video_init(GSSdlVideo *v) {
    memset(v,0,sizeof *v);v->map_mask=v->seq[2]=15;v->gc[8]=255;
}
static GSStatus control_write(void *ctx,GSVideoRoute route,uint8_t byte) {
    GSSdlVideo *v=ctx;
    switch(route) {
    case GS_SEQ_INDEX:v->seq_index=byte;break;
    case GS_SEQ_DATA:
        if(v->seq_index>=5)return GS_UNSUPPORTED;
        v->seq[v->seq_index]=byte;if(v->seq_index==2)v->map_mask=byte&15;break;
    case GS_GC_INDEX:v->gc_index=byte;break;
    case GS_GC_DATA:
        if(v->gc_index>=9)return GS_UNSUPPORTED;
        v->gc[v->gc_index]=byte;if(v->gc_index==4)v->read_plane=byte&3;break;
    case GS_CRTC_INDEX:v->crtc_index=byte;break;
    case GS_CRTC_DATA:if(v->crtc_index>=25)return GS_UNSUPPORTED;v->crtc[v->crtc_index]=byte;break;
    case GS_ATTRIBUTE_WRITE:
        if(!v->attribute_phase)v->attribute_index=byte&31;
        else {if(v->attribute_index>=21)return GS_UNSUPPORTED;v->attribute[v->attribute_index]=byte;}
        v->attribute_phase^=1;break;
    default:return GS_UNSUPPORTED;
    }return GS_OK;
}
static GSStatus control_read(void *ctx,GSVideoRoute route,uint8_t *byte) {
    GSSdlVideo *v=ctx;if(!byte)return GS_INVALID;
    switch(route) {
    case GS_SEQ_DATA:if(v->seq_index>=5)return GS_UNSUPPORTED;*byte=v->seq[v->seq_index];break;
    case GS_GC_DATA:if(v->gc_index>=9)return GS_UNSUPPORTED;*byte=v->gc[v->gc_index];break;
    case GS_CRTC_DATA:if(v->crtc_index>=25)return GS_UNSUPPORTED;*byte=v->crtc[v->crtc_index];break;
    case GS_ATTRIBUTE_READ:if(v->attribute_index>=21)return GS_UNSUPPORTED;*byte=v->attribute[v->attribute_index];break;
    default:return GS_UNSUPPORTED;
    }return GS_OK;
}
static GSStatus read_cell(void *ctx,uint16_t cell,GSReadRole role,uint8_t *byte) {
    GSSdlVideo *v=ctx;if(!byte||(unsigned)role>GS_COLLISION_READ)return GS_INVALID;
    for(unsigned p=0;p<4;p++)v->latches[p]=v->planes[p][cell];
    if(v->gc[5]&8) {
        uint8_t result=255;
        for(unsigned p=0;p<4;p++)if(v->gc[7]&(1u<<p))
            result&=v->latches[p]^(v->gc[2]&(1u<<p)?0:255);
        *byte=result;
    } else *byte=v->latches[v->read_plane&3];
    return GS_OK;
}
static GSStatus store(void *ctx,uint16_t cell,uint8_t byte) {
    GSSdlVideo *v=ctx;unsigned rotate=v->gc[3]&7,mode=v->gc[5]&3,op=(v->gc[3]>>3)&3;
    uint8_t rotated=(uint8_t)((byte>>rotate)|(byte<<(8-rotate)));
    for(unsigned p=0;p<4;p++)if(v->map_mask&(1u<<p)) {
        uint8_t latch=v->latches[p],mask=v->gc[8],source,result;
        if(mode==1)result=latch;
        else {
            if(mode==0)source=v->gc[1]&(1u<<p)?(v->gc[0]&(1u<<p)?255:0):rotated;
            else if(mode==2)source=byte&(1u<<p)?255:0;
            else {source=v->gc[0]&(1u<<p)?255:0;mask&=rotated;}
            if(op==1)source&=latch;else if(op==2)source|=latch;else if(op==3)source^=latch;
            result=(uint8_t)((source&mask)|(latch&~mask));
        }v->planes[p][cell]=result;
    }return GS_OK;
}
static GSStatus copy(void *ctx,uint16_t source,uint16_t destination,uint8_t *reply) {
    GSStatus status=read_cell(ctx,source,GS_SOURCE_READ,reply);
    return status==GS_OK?store(ctx,destination,*reply):status;
}
static GSStatus store_word(void *ctx,uint16_t cell,uint16_t value) {
    GSStatus status=store(ctx,cell,(uint8_t)value);if(status!=GS_OK)return status;
    /* The high byte is contiguous, not wrapped. Crossing the hardware store has
     * no shipped provider binding; retain the low-store prefix and fail closed. */
    if(cell==UINT16_MAX)return GS_UNSUPPORTED;
    return store(ctx,(uint16_t)(cell+1),(uint8_t)(value>>8));
}
static GSStatus water_mark(void *ctx,uint16_t address,uint8_t *reply) {
    GSStatus status=read_cell(ctx,address,GS_SOURCE_READ,reply);
    return status==GS_OK?store(ctx,address,0x40):status;
}
static GSStatus dac(void *ctx,GSDacWrite write) {
    GSSdlVideo *v=ctx;
    if(write.kind==GS_DAC_SELECT){v->dac_index=write.value;v->dac_component=0;}
    else if(write.kind==GS_DAC_COMPONENT){
        v->dac[3*v->dac_index+v->dac_component]=write.value&63;
        if(++v->dac_component==3){v->dac_component=0;v->dac_index++;}
    }else return GS_INVALID;
    return GS_OK;
}
static GSStatus retrace(void *ctx,uint8_t *level) {
    GSSdlVideo *v=ctx;if(!level)return GS_INVALID;
    v->attribute_phase=0;*level=v->retrace?8:0;return GS_OK;
}
static uint8_t expand6(uint8_t byte){return (uint8_t)((byte<<2)|(byte>>4));}
void gs_video_rgb(const GSSdlVideo *v,uint32_t out[320*200]) {
    uint32_t colors[256];for(unsigned i=0;i<256;i++)colors[i]=0xff000000u|
        ((uint32_t)expand6(v->dac[3*i])<<16)|((uint32_t)expand6(v->dac[3*i+1])<<8)|expand6(v->dac[3*i+2]);
    unsigned start=v->crtc[12]*256u+v->crtc[13],pitch=v->crtc[19]*2u;if(!pitch)pitch=80;
    unsigned compare=v->crtc[24]|((v->crtc[7]&16)<<4)|((v->crtc[9]&64)<<3),split=(compare+1)/2;
    for(unsigned y=0;y<200;y++) {
        unsigned base=y>=split?(y-split)*pitch:start+y*pitch;
        for(unsigned x=0;x<320;x++)out[y*320+x]=colors[v->planes[x&3][(uint16_t)(base+x/4)]];
    }
}
GSStatus gs_video_window(GSSdlVideo *v,int scale) {
    if(scale<1)return GS_INVALID;
    v->window=SDL_CreateWindow("Ugh!",320*scale,200*scale,SDL_WINDOW_RESIZABLE);
    if(!v->window)return GS_IO_ERROR;
    v->renderer=SDL_CreateRenderer(v->window,NULL);if(!v->renderer)return GS_IO_ERROR;
    if(!SDL_SetRenderLogicalPresentation(v->renderer,320,200,SDL_LOGICAL_PRESENTATION_LETTERBOX))return GS_IO_ERROR;
    v->texture=SDL_CreateTexture(v->renderer,SDL_PIXELFORMAT_XRGB8888,SDL_TEXTUREACCESS_STREAMING,320,200);
    if(!v->texture)return GS_IO_ERROR;
    return SDL_SetTextureScaleMode(v->texture,SDL_SCALEMODE_NEAREST)?GS_OK:GS_IO_ERROR;
}
static GSStatus present(void *ctx) {
    GSSdlVideo *v=ctx;uint32_t pixels[320*200];gs_video_rgb(v,pixels);
    if(!v->renderer)return GS_OK;
    /* A failed present (window closing, display lost) skips this frame; it is
     * presentation only and never ends the game. */
    if(!(SDL_UpdateTexture(v->texture,NULL,pixels,320*4)&&SDL_SetRenderDrawColor(v->renderer,0,0,0,255)&&
        SDL_RenderClear(v->renderer)&&SDL_RenderTexture(v->renderer,v->texture,NULL,NULL)&&SDL_RenderPresent(v->renderer))) {
        static int reported;if(!reported++)SDL_Log("present failed, frame skipped: %s",SDL_GetError());
    }
    return GS_OK;
}
void gs_video_close(GSSdlVideo *v){SDL_DestroyTexture(v->texture);SDL_DestroyRenderer(v->renderer);SDL_DestroyWindow(v->window);v->texture=NULL;v->renderer=NULL;v->window=NULL;}
static GSStatus compatibility(void *ctx){(void)ctx;return GS_UNSUPPORTED;}
GSVideoOps gs_video_operations(void){return (GSVideoOps){control_write,control_read,read_cell,store,store_word,copy,water_mark,dac,retrace,present,compatibility};}
