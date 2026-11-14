#include "platform.h"
#include "audio_projection.h"
#include "../adlx_samples.h"

static AudioSampleView samples_view(uint16_t bank,AudioState *state)
{
    (void)audio_bridge_publish_voice;
    audio_bridge_project(bank,state);
    AudioSampleView view={state->channels,rd16(bank,S(SampleMixerBusy)),rd16(bank,S(ActiveSampleVoiceCount)),rd16(bank,S(ActiveSampleVoiceMask)),rd16(bank,S(SampleMixPairsRemaining)),rd16(bank,S(SampleMixFirstSum)),rd16(bank,S(SampleMixSecondSum))};return view;
}
static void samples_publish(uint16_t bank,const AudioSampleView *view)
{
    for(unsigned i=0;i<8;i++) {
        uint16_t p=(uint16_t)(S(AudioChannelStates)+42u*i);
        wr16(bank,(uint16_t)(p+4),view->voices[i].repeats);wr16(bank,(uint16_t)(p+16),view->voices[i].cursor.index);
    }
    wr16(bank,S(SampleMixerBusy),view->busy);wr16(bank,S(ActiveSampleVoiceCount),view->count);
    wr16(bank,S(ActiveSampleVoiceMask),view->mask);wr16(bank,S(SampleMixPairsRemaining),view->remaining);
    wr16(bank,S(SampleMixFirstSum),view->first_sum);wr16(bank,S(SampleMixSecondSum),view->second_sum);
}
EXPORT int c_ResetSampleVoiceCursor(Regs *r)
{
    AudioSampleReset result=audio_sample_reset(r->ax);r->ax=result.displacement;
    flag(r,CF,result.overflow);flag(r,OF,result.overflow);
    wr16(r->cs,(uint16_t)(S(SampleVoicePairCursor)+result.displacement),0);return UGH_OK;
}
EXPORT int c_MixSampleVoicePairs(Regs *r)
{
    r->ax=0;AudioState state;AudioSampleView view=samples_view(r->cs,&state);
    sub16(r,view.count,0,0);if(!view.count) return UGH_OK;
    AudioSampleMixWork work=audio_sample_mix_begin(&view,r->bx,r->dx);
    samples_publish(r->cs,&view);uint16_t reply=0;
    for(;;) {
        AudioSampleRequest request=audio_sample_mix_next(&view,&work,reply);samples_publish(r->cs,&view);
        if(request.action==AUDIO_SAMPLE_DONE) {
            r->ax=sub16(r,work.requested,view.remaining,0);
            return UGH_OK;
        }
        if(request.action==AUDIO_SAMPLE_FAULT) return UGH_UNSUPPORTED;
        if(request.action==AUDIO_SAMPLE_BOUND) return UGH_BUDGET;
        if(request.action==AUDIO_SAMPLE_READ) reply=rd16(audio_bridge_bank(request.source),request.source.index);
        else wr8(r->cs,request.destination,request.value);
        /* Output and sources may alias any sound state cell. Rebind after
         * every actual read/write; never overwrite a fresh alias with cache. */
        view=samples_view(r->cs,&state);
    }
}

typedef struct SampleFrame {uint16_t sp,bp,si,di,ds;} SampleFrame;
static void samples_push(Regs *r,uint16_t value) {r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,value);}
static SampleFrame samples_enter(Regs *r)
{
    SampleFrame f={r->sp,r->bp,r->si,r->di,r->ds};samples_push(r,r->bp);r->bp=r->sp;r->sp=(uint16_t)(r->sp-10);
    samples_push(r,r->si);samples_push(r,r->di);samples_push(r,r->ds);r->ds=UGH_S_C_SoundSystemInitialized;return f;
}
static int samples_leave(Regs *r,SampleFrame f,int status)
{if(status==UGH_CONTROL_TRANSFER) return status;r->sp=f.sp;r->bp=f.bp;r->si=f.si;r->di=f.di;r->ds=f.ds;return status;}
static void samples_pointer(Regs *r,SampleFrame f,uint32_t position)
{wr16(r->ss,(uint16_t)(f.sp+6),(uint16_t)(position&15u));wr16(r->ss,(uint16_t)(f.sp+8),(uint16_t)(position>>4));}
static int samples_stop(Regs *r,uint16_t slot)
{
    uint16_t sp=r->sp;samples_push(r,slot);samples_push(r,r->cs);samples_push(r,(uint16_t)(UGH_O_C_LoadIffSample+0x3a5));
    int status=ugh_dispatch(UGH_SEG_C,UGH_O_C_StopSoundChannel,r);if(status!=UGH_CONTROL_TRANSFER) r->sp=sp;return status;
}
static void samples_loaded(uint16_t slot,const AudioChannel *voice)
{
    uint16_t p=(uint16_t)(S(AudioChannelStates)+42u*slot);
    wr16(SOUND_SEG,(uint16_t)(p+40),voice->control);wr16(SOUND_SEG,(uint16_t)(p+4),voice->repeats);
    wr16(SOUND_SEG,(uint16_t)(p+28),voice->volume);
    wr16(SOUND_SEG,(uint16_t)(p+8),audio_bridge_bank(voice->start));wr16(SOUND_SEG,(uint16_t)(p+6),voice->start.index);
    wr16(SOUND_SEG,(uint16_t)(p+18),audio_bridge_bank(voice->cursor));wr16(SOUND_SEG,(uint16_t)(p+16),voice->cursor.index);
    wr16(SOUND_SEG,(uint16_t)(p+10),voice->length);wr16(SOUND_SEG,(uint16_t)(p+12),voice->sample_mode);
    wr16(SOUND_SEG,(uint16_t)(p+24),voice->sample_selector);wr16(SOUND_SEG,(uint16_t)(p+38),voice->step_q8);
    wr16(SOUND_SEG,(uint16_t)(p+20),voice->sample_half_length);wr16(SOUND_SEG,(uint16_t)(p+26),voice->sample_accumulator);wr16(SOUND_SEG,(uint16_t)(p+14),voice->sample_rate);
}
EXPORT int c_LoadIffSample(Regs *r)
{
    uint16_t slot=arg16(r,0),offset=arg16(r,2),bank=arg16(r,4),volume=arg16(r,6),repeats=arg16(r,8),scale=arg16(r,10);
    SampleFrame f=samples_enter(r);r->es=SOUND_SEG;r->ax=65535;
    AudioSampleImportWork work=audio_sample_import_begin(rd16(SOUND_SEG,S(SoundDeviceBits)),slot,lin(bank,offset),volume,repeats,scale);
    uint16_t reply=0;
    for(;;) {
        AudioSampleImportRequest request=audio_sample_import_next(&work,reply);int status;
        switch(request.action) {
        case AUDIO_SAMPLE_IMPORT_DONE:r->ax=work.result;return samples_leave(r,f,UGH_OK);
        case AUDIO_SAMPLE_IMPORT_BOUND:return samples_leave(r,f,UGH_BUDGET);
        case AUDIO_SAMPLE_IMPORT_READ: {
            uint16_t source_bank=request.original_form ? bank : (uint16_t)(request.position>>4);
            uint16_t source_offset=request.original_form ? offset : (uint16_t)(request.position&15u);
            if(request.publication==1) samples_pointer(r,f,request.next);
            r->es=source_bank;reply=rd8(source_bank,source_offset);
            if(request.publication==2) {samples_pointer(r,f,request.next);r->es=r->ss;}
            break;
        }
        case AUDIO_SAMPLE_IMPORT_STOP:status=samples_stop(r,slot);if(status) return samples_leave(r,f,status);break;
        case AUDIO_SAMPLE_IMPORT_APPLY: {
            AudioState state;audio_bridge_project(SOUND_SEG,&state);AudioCursor data=audio_bridge_cursor((uint16_t)(work.position>>4),(uint16_t)(work.position&15u));
            audio_sample_import_apply(&state.channels[slot],&work,data);r->es=SOUND_SEG;samples_loaded(slot,&state.channels[slot]);break;
        }
        case AUDIO_SAMPLE_IMPORT_WAIT:
            status=platform_service_point_at(SERVICE_TIMER_WAIT,UGH_SEG_C,(uint16_t)(UGH_O_C_LoadIffSample+0x4e7),r);
            if(status) return samples_leave(r,f,status);
            reply=rd16(SOUND_SEG,S(SampleMixerBusy));break;
        case AUDIO_SAMPLE_IMPORT_ACTIVATE: {
            AudioState state;AudioSampleView view=samples_view(SOUND_SEG,&state);audio_sample_activate(&view,slot);
            wr16(SOUND_SEG,S(ActiveSampleVoiceCount),view.count);wr16(SOUND_SEG,S(ActiveSampleVoiceMask),view.mask);break;
        }
        default:return samples_leave(r,f,UGH_UNSUPPORTED);
        }
    }
}
