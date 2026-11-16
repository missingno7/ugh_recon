#include "backend.h"
#include <string.h>
GSStatus gs_audio_init(GSSdlAudio *audio,int enabled) {
    memset(audio,0,sizeof *audio);OPL3_Reset(&audio->chip,48000);
    if(enabled) {
        SDL_AudioSpec spec={SDL_AUDIO_S16,2,48000};
        audio->stream=SDL_OpenAudioDeviceStream(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK,&spec,NULL,NULL);
        if(!audio->stream)return GS_IO_ERROR;
        if(!SDL_ResumeAudioStreamDevice(audio->stream)){gs_audio_close(audio);return GS_IO_ERROR;}
    }return GS_OK;
}
static GSStatus opl(void *ctx,GSRegisterWrite write) {
    GSSdlAudio *a=ctx;OPL3_WriteRegBuffered(&a->chip,write.reg,write.value);
    a->values[write.reg]=write.value;a->registers++;return GS_OK;
}
static GSStatus status(void *ctx,uint8_t *reply) {
    (void)ctx;if(!reply)return GS_INVALID;
    return GS_UNSUPPORTED; /* step 7: pending: capability/calibration prefix */
}
GSStatus gs_audio_generate(GSSdlAudio *a,int16_t *samples,unsigned frames) {
    if(!samples&&frames)return GS_INVALID;
    OPL3_GenerateStream(&a->chip,samples,frames);a->frames+=frames;
    /* Bound latency to about 0.2 s; a failed push drops these samples. Audio
     * output is presentation only and never ends the game. */
    if(a->stream&&SDL_GetAudioStreamQueued(a->stream)<48000*4/5&&!SDL_PutAudioStreamData(a->stream,samples,(int)(frames*4u))) {
        static int reported;if(!reported++)SDL_Log("audio push failed, samples dropped: %s",SDL_GetError());
    }
    return GS_OK;
}
static GSStatus advance(void *ctx,uint64_t ns) {
    GSSdlAudio *a=ctx;
    uint64_t frames=(ns/1000000000ull)*48000+(ns%1000000000ull*48000+a->remainder)/1000000000ull;
    a->remainder=(ns%1000000000ull*48000+a->remainder)%1000000000ull;
    while(frames){int16_t buffer[2048];unsigned n=frames>1024?1024:(unsigned)frames;GSStatus s=gs_audio_generate(a,buffer,n);if(s!=GS_OK)return s;frames-=n;}
    return GS_OK;
}
static GSStatus clock_delivery(void *ctx,GSClockDelivery kind){
    GSSdlAudio *a=ctx;if((unsigned)kind>GS_CLOCK_BIOS_CHAIN)return GS_INVALID;
    if(!a->clock_sink)return GS_UNSUPPORTED; /* step 7: pending engine receiver */
    return a->clock_sink(a->clock_context,kind);
}
void gs_audio_close(GSSdlAudio *a){SDL_DestroyAudioStream(a->stream);a->stream=NULL;}
static GSStatus calibration(void *ctx,GSCalibrationPhase phase,GSCalibrationReply *reply){(void)ctx;(void)phase;(void)reply;return GS_UNSUPPORTED;}
static GSStatus timer_lifetime(void *ctx,GSTimerLifetimeRequest request,GSBinding *reply){(void)ctx;(void)request;(void)reply;return GS_UNSUPPORTED;}
GSAudioOps gs_audio_operations(void){return (GSAudioOps){opl,status,advance,clock_delivery,calibration,timer_lifetime,NULL};}
