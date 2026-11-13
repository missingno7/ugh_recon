/* Nuked-OPL3 is pinned externally; only hardware register events enter it.
 * Game SOUND/TIMER callbacks remain literal translated code on the game thread.
 * SDL owns the consumer thread; it never touches game RAM or OPL state. */
#include "host.h"
#include "opl3.h"
#include <string.h>
static opl3_chip chip;
static SDL_AudioStream *stream;
static uint64_t remainder,samples,nonzero,registers;
static FILE *wav;
int host_audio_init(int enabled,const char *path) {
    OPL3_Reset(&chip,48000);
    if(path) { wav=fopen(path,"wb"); if(!wav) host_fail("cannot open WAV"); uint8_t h[44]={0}; fwrite(h,1,44,wav); }
    if(enabled) {
        SDL_AudioSpec spec={SDL_AUDIO_S16,2,48000};
        stream=SDL_OpenAudioDeviceStream(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK,&spec,NULL,NULL);
        if(!stream) return 0;
        if(!SDL_ResumeAudioStreamDevice(stream)) return 0;
    }
    return 1;
}
void host_audio_out(uint16_t port,unsigned size,uint32_t value) {
    for(unsigned i=0;i<size;i++) if(port+i==0x389) {
        OPL3_WriteRegBuffered(&chip,ugh_devices.opl_index,(uint8_t)(value>>(i*8))); registers++;
    }
}
void host_audio_advance(uint64_t ns) {
    uint64_t count=(ns*48000+remainder)/1000000000ull;
    remainder=(ns*48000+remainder)%1000000000ull;
    while(count) {
        int16_t buffer[2048]; unsigned n=count>1024?1024:(unsigned)count;
        OPL3_GenerateStream(&chip,buffer,n);
        for(unsigned i=0;i<n*2;i++) nonzero+=buffer[i]!=0;
        if(wav && fwrite(buffer,4,n,wav)!=n) host_fail("WAV write failed");
        if(stream && !SDL_PutAudioStreamData(stream,buffer,(int)n*4)) host_fail("SDL audio queue failed");
        samples+=n; count-=n;
    }
}
void host_audio_close(void) {
    if(wav) {
        uint8_t h[44]={0}; uint32_t size=(uint32_t)(samples*4),total=size+36,rate=48000,bytes=192000;
        memcpy(h,"RIFF",4); memcpy(h+4,&total,4); memcpy(h+8,"WAVEfmt ",8);
        h[16]=16; h[20]=1; h[22]=2; memcpy(h+24,&rate,4); memcpy(h+28,&bytes,4);
        h[32]=4; h[34]=16; memcpy(h+36,"data",4); memcpy(h+40,&size,4);
        fseek(wav,0,SEEK_SET); fwrite(h,1,44,wav); fclose(wav);
    }
    fprintf(stderr,"audio: %llu register writes, %llu stereo frames, %llu nonzero samples\n",
        (unsigned long long)registers,(unsigned long long)samples,(unsigned long long)nonzero);
    SDL_DestroyAudioStream(stream);
}
