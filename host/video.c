/* Ugh uses unchained 256-colour VGA: byte-mode CRTC counter, four
 * interleaved pixels per address, pitch = 2*CRTC[13]. The line compare
 * restarts the counter at zero for the fixed eight-line HUD. */
#include "host.h"
#include <string.h>
static SDL_Window *window;
static SDL_Renderer *renderer;
static SDL_Texture *texture;
static uint32_t pixels[320*200];
static uint8_t expand6(uint8_t c) { return (uint8_t)((c<<2)|(c>>4)); }
void host_render(uint32_t out[320*200]) {
    Devices *d=&ugh_devices; uint32_t palette[256];
    for(unsigned i=0;i<256;i++) palette[i]=0xff000000u|((uint32_t)expand6(d->dac[3*i])<<16)|
        ((uint32_t)expand6(d->dac[3*i+1])<<8)|expand6(d->dac[3*i+2]);
    unsigned start=((unsigned)d->crtc[12]<<8)|d->crtc[13];
    unsigned pitch=d->crtc[19]*2; if(!pitch) pitch=80;
    unsigned compare=d->crtc[24]|((d->crtc[7]&16)<<4)|((d->crtc[9]&64)<<3);
    /* BIOS 13h has doubled scanlines; the game preserves that geometry. */
    unsigned split=(compare+1)/2;
    for(unsigned y=0;y<200;y++) {
        unsigned base=y>=split?(y-split)*pitch:start+y*pitch;
        for(unsigned x=0;x<320;x++) out[y*320+x]=palette[d->plane[x&3][(uint16_t)(base+x/4)]];
    }
}
int host_video_init(int scale) {
    window=SDL_CreateWindow("Ugh! - literal C / SDL3",320*scale,200*scale,SDL_WINDOW_RESIZABLE);
    if(!window) return 0;
    renderer=SDL_CreateRenderer(window,NULL); if(!renderer) return 0;
    SDL_SetRenderLogicalPresentation(renderer,320,200,SDL_LOGICAL_PRESENTATION_LETTERBOX);
    texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_XRGB8888,SDL_TEXTUREACCESS_STREAMING,320,200);
    if(!texture) return 0;
    SDL_SetTextureScaleMode(texture,SDL_SCALEMODE_NEAREST); return 1;
}
void host_present(void) {
    host_render(pixels);
    if(!renderer) return;
    SDL_UpdateTexture(texture,NULL,pixels,320*4); SDL_SetRenderDrawColor(renderer,0,0,0,255);
    SDL_RenderClear(renderer); SDL_RenderTexture(renderer,texture,NULL,NULL); SDL_RenderPresent(renderer);
}
void host_save_shot(const char *path) {
    host_render(pixels);
    SDL_Surface *s=SDL_CreateSurfaceFrom(320,200,SDL_PIXELFORMAT_XRGB8888,pixels,320*4);
    if(!s || !SDL_SaveBMP(s,path)) host_fail("cannot save screenshot");
    SDL_DestroySurface(s);
}
void host_video_close(void) {
    SDL_DestroyTexture(texture); SDL_DestroyRenderer(renderer); SDL_DestroyWindow(window);
}
