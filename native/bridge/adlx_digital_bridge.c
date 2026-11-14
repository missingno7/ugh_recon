/* CPU frames, flags, port delivery and the broken near-RET hook are platform
 * bindings. Ordinary DSP/DMA/bank policy is in adlx_digital.c. No L1 endpoint
 * fallback; the GAME RET boundary remains an explicit service. */
#include "platform.h"
#include "audio_projection.h"
#include "../adlx_digital.h"
#define CSEG UGH_SEG_C
#define CDATA UGH_S_C_SoundSystemInitialized
#define C(n) UGH_O_C_##n
#define SW(n) rd16(SOUND_SEG,S(n))
#define WW(n,v) wr16(SOUND_SEG,S(n),(uint16_t)(v))
static void push_word(Regs *r,uint16_t value) {
    r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,value);
}
static uint16_t pop_word(Regs *r) {
    uint16_t value=rd16(r->ss,r->sp); r->sp=(uint16_t)(r->sp+2); return value;
}
static int call_sound(Regs *r,uint16_t target,uint16_t return_ip) {
    push_word(r,r->cs); push_word(r,return_ip);
    int status=ugh_dispatch(r->cs,target,r);
    if(status!=UGH_CONTROL_TRANSFER) r->sp=(uint16_t)(r->sp+4);
    return status;
}
static uint16_t increment(Regs *r,uint16_t value) {
    uint16_t carry=r->flags&CF;
    value=add16(r,value,1,0); flag(r,CF,carry); return value;
}
static void compare_byte(Regs *r,uint8_t a,uint8_t b) {
    uint8_t value=(uint8_t)(a-b);
    flag(r,CF,a<b); flag(r,OF,((a^b)&(a^value)&0x80u)!=0);
    flag(r,AF,((a^b^value)&16u)!=0); szp(r,value,8);
}
typedef struct {uint16_t sp,bp,si,di,ds;} Frame;
static void push(Regs *r,uint16_t x) { r->sp=(uint16_t)(r->sp-2); wr16(r->ss,r->sp,x); }
static Frame enter(Regs *r,unsigned locals,unsigned saves) {
    Frame f={r->sp,r->bp,r->si,r->di,r->ds};
    push(r,r->bp); r->bp=r->sp; r->sp=(uint16_t)(r->sp-locals);
    if(saves&1) push(r,r->si);
    if(saves&2) push(r,r->di);
    push(r,r->ds); r->ds=CDATA; return f;
}
static int leave(Regs *r,Frame f,int status) {
    r->sp=f.sp; r->bp=f.bp; r->si=f.si; r->di=f.di; r->ds=f.ds; return status;
}
static uint16_t arg(Regs *r,Frame f,unsigned n) { return rd16(r->ss,(uint16_t)(f.sp+4+n)); }
static int call(Regs *r,uint16_t seg,uint16_t off,uint16_t ret,const uint16_t *a,unsigned n) {
    uint16_t sp=r->sp;
    for(unsigned i=n;i;i--) push(r,a[i-1]);
    push(r,r->cs); push(r,ret);
    int status=ugh_dispatch(seg,off,r); if(status!=UGH_CONTROL_TRANSFER) r->sp=sp; return status;
}
static uint32_t words32(uint16_t s,uint16_t o) { return rd16(s,o)|((uint32_t)rd16(s,(uint16_t)(o+2))<<16); }
#define CALL(seg,n,ret,...) do {const uint16_t a_[]={__VA_ARGS__};int st=call(r,seg,n,ret,a_,sizeof(a_)/2);if(st) return st==UGH_CONTROL_TRANSFER?st:leave(r,f,st);} while(0)
static AudioDigitalView digital_view(uint16_t bank,AudioState *state) {
    (void)audio_bridge_publish_voice;(void)audio_bridge_bank;audio_bridge_project(bank,state);
    AudioDigitalView v={state->channels,rd16(bank,S(SoundDeviceBits)),rd16(bank,S(SampleMixerBusy)),rd16(bank,S(ActiveSampleVoiceCount)),rd16(bank,S(ActiveSampleVoiceMask)),rd8(bank,S(DspIrqBusy)),rd8(bank,S(DmaMixBufferSelect)),rd8(bank,S(DspPicIrqMask))};return v;
}
EXPORT int c_ProbeSoundBlasterDmaIrq(Regs *r) {
    push_word(r,r->es); push_word(r,r->ds);
    int st=call_sound(r,S(LocateDmaMixBuffers),S(ProbeSoundBlasterDmaIrq)+6);
    if(st) return st;
    wr16(r->cs,S(DspInterruptVector),1); wr16(r->cs,S(DspBasePort),0x200);
    return ugh_call_near_ret_hook(r,G(loc_001F),S(ProbeSoundBlasterDmaIrq)+0x19);
}
EXPORT int c_InitializeDspPlayback(Regs *r) {
    push_word(r,r->ds); push_word(r,r->es);
    int st=call_sound(r,S(CalibrateSoundDelay),S(InitializeDspPlayback)+6); if(st) return st;
    return call_sound(r,S(ProbeSoundBlasterDmaIrq),S(InitializeDspPlayback)+10);
}
EXPORT int c_ShutdownDspPlayback(Regs *r) {
    push_word(r,r->ds); set_al(r,0xd3);
    int st=call_sound(r,S(WriteSoundBlasterDsp),S(ShutdownDspPlayback)+7); if(st) return st;
    return ugh_call_near_ret_hook(r,G(loc_001F),S(ShutdownDspPlayback)+12);
}
EXPORT int c_WriteSoundBlasterDsp(Regs *r) {
    uint16_t ax=r->ax,cx=r->cx,dx=r->dx;
    set_ah(r,(uint8_t)r->ax); r->dx=add16(r,rd16(r->cs,S(DspBasePort)),12,0); r->cx=logic(r,0,16);
    AudioDspPoll poll={0,0};
    do {
        set_al(r,(uint8_t)platform_in(r->dx,1)); if(ugh_devices.error) return UGH_UNSUPPORTED;
        logic(r,(uint8_t)r->ax&0x80,8); audio_dsp_poll(&poll,(uint8_t)r->ax,1);r->cx=poll.remaining;
    } while(poll.remaining && poll.busy);
    set_al(r,(uint8_t)(r->ax>>8)); platform_out(r->dx,1,(uint8_t)r->ax);
    r->ax=ax; r->cx=cx; r->dx=dx; return UGH_OK;
}
EXPORT int c_ResetSoundBlasterDsp(Regs *r) {
    r->dx=add16(r,rd16(r->cs,S(DspBasePort)),6,0);
    set_al(r,1); platform_out(r->dx,1,(uint8_t)r->ax); r->ax=3;
    int status=call_sound(r,S(DelaySoundIo),(uint16_t)(S(ResetSoundBlasterDsp)+0x12));
    if(status) return status;
    set_al(r,(uint8_t)logic(r,0,8)); platform_out(r->dx,1,(uint8_t)r->ax);
    r->dx=add16(r,r->dx,8,0); r->cx=100;AudioDspPoll poll={100,0};
    do {
        set_al(r,(uint8_t)platform_in(r->dx,1));
        if(ugh_devices.error) return UGH_UNSUPPORTED;
        logic(r,(uint8_t)r->ax&0x80u,8); audio_dsp_poll(&poll,(uint8_t)r->ax,0);r->cx=poll.remaining;
    } while(poll.remaining && !poll.busy);
    r->dx=sub16(r,r->dx,4,0); set_al(r,(uint8_t)platform_in(r->dx,1));
    if(ugh_devices.error) return UGH_UNSUPPORTED;
    compare_byte(r,(uint8_t)r->ax,0xaa); flag(r,CF,(uint8_t)r->ax!=0xaa);
    return UGH_OK;
}
EXPORT int c_SetDspSampleRate(Regs *r) {
    push_word(r,r->bp); r->bp=r->sp;
    push_word(r,r->ax); push_word(r,r->bx); push_word(r,r->dx);
    uint16_t devices=logic(r,rd16(r->cs,S(SoundDeviceBits))&2u,16);
    if(devices) {
        uint16_t rate=rd16(r->ss,(uint16_t)(r->bp+6)); sub16(r,rate,1000,0);
        if(audio_dsp_rate_enabled(devices,rate)) {
            r->ax=(uint16_t)(1000000u/rate); r->dx=(uint16_t)(1000000u%rate);
            sub16(r,0,r->ax,0);r->ax=audio_dsp_constant(rate);r->bx=r->ax; set_al(r,0x40);
            int status=call_sound(r,S(WriteSoundBlasterDsp),(uint16_t)(S(SetDspSampleRate)+0x30));
            if(status) return status;
            set_al(r,(uint8_t)r->bx);
            status=call_sound(r,S(WriteSoundBlasterDsp),(uint16_t)(S(SetDspSampleRate)+0x36));
            if(status) return status;
        }
    }
    r->dx=pop_word(r); r->bx=pop_word(r); r->ax=pop_word(r);
    r->sp=r->bp; r->bp=pop_word(r); return UGH_OK;
}
EXPORT int c_StartDmaSampleBlock(Regs *r) {
    AudioDmaBlock block=audio_dma_block(r->bx,r->dx,(uint8_t)(r->cx>>8));
    push_word(r,r->cx);r->bx=dec16(r,r->bx);
    for(unsigned i=0;i<9;i++) {set_al(r,block.writes[i].value);platform_out(block.writes[i].port,1,(uint8_t)r->ax);}
    const uint16_t resumes[]={S(StartDmaSampleBlock)+0xb3,S(StartDmaSampleBlock)+0xb9,S(StartDmaSampleBlock)+0xbf};
    for(unsigned i=0;i<3;i++) {set_al(r,block.commands[i]);int status=call_sound(r,S(WriteSoundBlasterDsp),resumes[i]);if(status) return status;}
    r->bx=increment(r,r->bx);r->cx=pop_word(r);return UGH_OK;
}
static void digital_locate(Regs *r,uint16_t page,uint16_t address,uint16_t offset,uint16_t buffer,uint16_t skip) {
    AudioDmaLocation result=audio_dma_locate(SOUND_SEG>>12,(uint16_t)(SOUND_SEG<<4),buffer,skip,(uint16_t)(S(DmaMixBufferTwoOffset)+2+0x40a));
    uint16_t initial=(uint16_t)((uint16_t)(SOUND_SEG<<4)+buffer);
    r->cx=SOUND_SEG;r->ax=initial;
    wr16(r->cs,address,initial);wr16(r->cs,offset,buffer);wr8(r->cs,page,result.initial_page);
    r->ax=add16(r,r->ax,0x400,0);
    if(result.fallback) {
        uint8_t old=result.initial_page,carry=result.carry,value=result.header.page;
        r->ax=result.final_address;flag(r,CF,(unsigned)old+carry>255u);flag(r,OF,old==127 && carry);flag(r,AF,((old^carry^value)&16u)!=0);szp(r,value,8);
        wr8(r->cs,page,value);wr16(r->cs,address,result.header.address);wr16(r->cs,offset,result.header.offset);
    }
    r->cx=(uint16_t)((r->cx&255u)|((uint16_t)result.header.page<<8));
}
EXPORT int c_LocateDmaMixBuffers(Regs *r) {
    digital_locate(r,S(DmaMixBufferOnePage),S(DmaMixBufferOneAddress),S(DmaMixBufferOneOffset),(uint16_t)(S(DmaMixBufferOneOffset)+2),0x814);
    digital_locate(r,S(DmaMixBufferTwoPage),S(DmaMixBufferTwoAddress),S(DmaMixBufferTwoOffset),(uint16_t)(S(DmaMixBufferTwoOffset)+2),0x40a);return UGH_OK;
}
EXPORT int c_HandleDspProbeInterrupt(Regs *r) {
    set_al(r,0x20); platform_out(0x20,1,0x20);
    wr8(r->cs,S(DspProbeIrqSeen),1);
    return UGH_OK;
}
static AudioDmaView digital_dma_view(uint16_t bank,AudioState *state) {
    AudioDmaView view;view.shared=digital_view(bank,state);
    for(unsigned i=0;i<2;i++) {uint16_t displacement=(uint16_t)(i*0x40a);AudioDmaHeader *header=&view.headers[i];header->count=rd16(bank,(uint16_t)(S(DmaMixBufferOneCount)+displacement));header->address=rd16(bank,(uint16_t)(S(DmaMixBufferOneAddress)+displacement));header->offset=rd16(bank,(uint16_t)(S(DmaMixBufferOneOffset)+displacement));header->page=rd8(bank,(uint16_t)(S(DmaMixBufferOnePage)+displacement));}return view;
}
EXPORT int c_HandleSampleDmaInterrupt(Regs *r) {
    push_word(r,r->ax);set_al(r,0x20);platform_out(0x20,1,(uint8_t)r->ax);r->ax=pop_word(r);
    AudioState state;AudioDmaView view=digital_dma_view(r->cs,&state);AudioDmaInterruptWork work={0,0};
    logic(r,view.shared.interrupt_busy&1u,8);AudioDmaRequest request=audio_dma_interrupt_next(&view,&work,0);
    if(request.action==AUDIO_DIGITAL_BUSY_RETURN) return UGH_OK;
    wr8(r->cs,S(DspIrqBusy),view.shared.interrupt_busy);
    Regs saved=*r;uint16_t pusha_sp=r->sp;
    push_word(r,r->ax);push_word(r,r->cx);push_word(r,r->dx);push_word(r,r->bx);push_word(r,pusha_sp);push_word(r,r->bp);push_word(r,r->si);push_word(r,r->di);push_word(r,r->es);push_word(r,r->ds);
    r->dx=add16(r,rd16(r->cs,S(DspBasePort)),14,0);set_al(r,(uint8_t)platform_in(r->dx,1));if(ugh_devices.error) return UGH_UNSUPPORTED;
    for(;;) {
        view=digital_dma_view(r->cs,&state);uint8_t stage=work.stage;request=audio_dma_interrupt_next(&view,&work,r->ax);
        if(stage==1) {
            r->si=logic(r,0,16);logic(r,rd8(r->cs,S(DmaMixBufferSelect))&1u,8);r->si=(uint16_t)(request.selected*0x40a);
            r->bx=request.header.count;sub16(r,r->bx,0x28,0);
        }
        if(request.action==AUDIO_DIGITAL_START_BLOCK) {
            wr8(r->cs,S(DmaMixBufferSelect),(uint8_t)logic(r,view.shared.selection,8));r->dx=request.header.address;
            r->cx=(uint16_t)((r->cx&255u)|(uint16_t)request.header.page*256u);
            int status=call_sound(r,S(StartDmaSampleBlock),S(HandleSampleDmaInterrupt)+0x55);if(status) return status;
        } else if(request.action==AUDIO_DIGITAL_MIX) {
            wr16(r->cs,(uint16_t)(S(DmaMixBufferOneCount)+r->si),0);r->si=sub16(r,0,r->si,0);
            r->dx=request.header.offset;r->bx=0x400;int status=call_sound(r,S(MixSampleVoicePairs),S(HandleSampleDmaInterrupt)+0x6a);if(status) return status;
        } else if(request.action==AUDIO_DIGITAL_MASK) {
            set_al(r,(uint8_t)platform_in(0x21,1));set_al(r,(uint8_t)logic(r,audio_digital_pic((uint8_t)r->ax,rd8(r->cs,S(DspPicIrqMask)),0),8));platform_out(0x21,1,(uint8_t)r->ax);
        } else {
            if(stage==3) wr16(r->cs,(uint16_t)(S(DmaMixBufferTwoCount)+r->si),view.headers[1u-work.selected].count);
            uint16_t flags=r->flags;*r=saved;r->flags=flags;wr8(r->cs,S(DspIrqBusy),view.shared.interrupt_busy);return UGH_OK;
        }
    }
}
EXPORT int c_PrimeSampleDmaPlayback(Regs *r) {
    AudioDmaPrimeWork work={0};AudioState state;unsigned budget=1000000;
    logic(r,rd16(r->cs,S(SoundDeviceBits))&2u,16);
    for(;;) {
        AudioDmaView view=digital_dma_view(r->cs,&state);AudioDmaPrimeRequest request=audio_dma_prime_next(&view,&work,r->ax);
        if(request.count_checked) sub16(r,view.shared.count,0,0);
        int status;
        switch(request.action) {
        case AUDIO_DIGITAL_DONE:return UGH_OK;
        case AUDIO_DIGITAL_WAIT:
            if(!budget--) return UGH_BUDGET;
            status=platform_service_point_at(SERVICE_TIMER_WAIT,r->cs,S(loc_1EA3),r);if(status) return status;
            logic(r,rd16(r->cs,S(SampleMixerBusy))&1u,16);break;
        case AUDIO_DIGITAL_DSP_COMMAND:
            set_al(r,request.command);status=call_sound(r,S(WriteSoundBlasterDsp),S(PrimeSampleDmaPlayback)+0x26);if(status) return status;break;
        case AUDIO_DIGITAL_MIX:
            r->dx=request.destination;r->bx=0x400;status=call_sound(r,S(MixSampleVoicePairs),S(PrimeSampleDmaPlayback)+0x32);if(status) return status;break;
        case AUDIO_DIGITAL_UNMASK:
            wr16(r->cs,S(DmaMixBufferOneCount),view.headers[0].count);wr8(r->cs,S(DmaMixBufferSelect),view.shared.selection);
            set_al(r,(uint8_t)platform_in(0x21,1));set_ah(r,(uint8_t)~rd8(r->cs,S(DspPicIrqMask)));set_al(r,(uint8_t)logic(r,(uint8_t)r->ax&(r->ax>>8),8));platform_out(0x21,1,(uint8_t)r->ax);break;
        case AUDIO_DIGITAL_INTERRUPT:
            push_word(r,r->flags);push_word(r,r->cs);push_word(r,S(PrimeSampleDmaPlayback)+0x5d);return ugh_dispatch_interrupt(r->cs,S(HandleSampleDmaInterrupt),r);
        default:return UGH_UNSUPPORTED;
        }
    }
}
EXPORT int c_StopSoundChannel(Regs *r) {
    Frame f=enter(r,0,0);uint16_t slot=arg(r,f,0);r->ax=65535;
    if(slot>12) return leave(r,f,0);
    r->es=SOUND_SEG;
    AudioState state;AudioDigitalView view=digital_view(SOUND_SEG,&state);
    AudioDigitalAction action=audio_digital_stop_begin(&view,slot);
    if(action==AUDIO_DIGITAL_REJECT) return leave(r,f,0);
    if(action==AUDIO_DIGITAL_WAIT) {
        wr16(SOUND_SEG,(uint16_t)(S(AudioChannelStates)+42u*slot+4),view.channels[slot].repeats);
        unsigned budget=5000000;
        for(;;) {if(!budget--) return leave(r,f,UGH_BUDGET);int status=platform_service_point_at(SERVICE_TIMER_WAIT,CSEG,C(StopSoundChannel)+0x53,r);if(status) return leave(r,f,status);if(!SW(SampleMixerBusy)) break;}
        view=digital_view(SOUND_SEG,&state);audio_digital_stop_finish(&view,slot);
        WW(ActiveSampleVoiceMask,view.mask);WW(ActiveSampleVoiceCount,view.count);
    } else if(action==AUDIO_DIGITAL_STOP_ADLIB) {CALL(CSEG,C(StopAdlibTrackChannel),C(StopSoundChannel)+0x9c,slot);}
    r->ax=1;return leave(r,f,0);
}
EXPORT int c_LoadSoundBankResource(Regs *r) {
    Frame f=enter(r,4,0); r->ax=CDATA;
    for(unsigned n=12;n;n-=2) push(r,arg(r,f,n-2));
    return ugh_call_near_ret_hook(r,G(loc_001D),C(LoadSoundBankResource)+0x21);
}
static uint32_t digital_words(uint32_t position) {return words32((uint16_t)(position>>4),(uint16_t)(position&15u));}
EXPORT int c_LoadBankSoundByIndex(Regs *r) {
    Frame f=enter(r,4,3);uint16_t slot=arg(r,f,0),index=arg(r,f,2);r->ax=65535;
    if(slot>=12) return leave(r,f,0);
    uint16_t bank=rd16(SOUND_SEG,(uint16_t)(S(SoundBankBase)+2)),offset=SW(SoundBankBase);
    uint32_t base=lin(bank,offset),directory=words32(bank,offset),entry=audio_bank_entry(base,directory,index);
    r->es=SOUND_SEG;if(!audio_bank_admit(slot,entry,base,rd32(SOUND_SEG,S(SoundBankLength)))) return leave(r,f,0);
    uint32_t source=audio_bank_add(base,digital_words(entry));
    AudioBankScan work={source,0,1,1};uint8_t reply=0;
    for(;;) {
        AudioBankRequest request=audio_bank_scan_next(&work,reply);
        if(request.action==AUDIO_BANK_READ) {r->es=(uint16_t)(request.position>>4);reply=rd8(r->es,(uint16_t)(request.position&15u));continue;}
        if(request.action==AUDIO_BANK_SAMPLE) {CALL(CSEG,C(LoadIffSample),C(LoadBankSoundByIndex)+0x192,slot,(uint16_t)(source&15u),(uint16_t)(source>>4),arg(r,f,4),arg(r,f,6),arg(r,f,8));}
        else if(request.action==AUDIO_BANK_ADLX) {CALL(CSEG,C(LoadAdlibChannel),C(LoadBankSoundByIndex)+0x277,slot,(uint16_t)(source&15u),(uint16_t)(source>>4),arg(r,f,4),arg(r,f,6));}
        else r->ax=65535;
        return leave(r,f,0);
    }
}
