#include "platform.h"
#include "audio_projection.h"
#include "../adlx_lifetime.h"

static void lifetime_push(Regs *r,uint16_t value)
{r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,value);}
static int lifetime_call(Regs *r,uint16_t bank,uint16_t target,uint16_t resume)
{
    lifetime_push(r,r->cs);lifetime_push(r,resume);
    int status=ugh_dispatch(bank,target,r);r->sp=(uint16_t)(r->sp+4);return status;
}
static void lifetime_pointer(uint16_t offset,AudioCursor cursor)
{wr16(SOUND_SEG,offset,cursor.index);wr16(SOUND_SEG,(uint16_t)(offset+2),cursor.window ? audio_bridge_bank(cursor) : 0);}
static void lifetime_publish_reset(const AudioState *state,const AudioResetCells *cells)
{
    wr16(SOUND_SEG,S(AdlxTimerPeriod),state->timer_period);
    wr16(SOUND_SEG,S(SampleMixerBusy),cells->mixer_busy);wr16(SOUND_SEG,S(DspBasePort),cells->dsp_port);
    wr16(SOUND_SEG,S(DspInterruptVector),cells->interrupt_vector);
    for(unsigned i=0;i<AUDIO_CHANNEL_COUNT;i++) {
        const AudioChannel *c=&state->channels[i];uint16_t p=(uint16_t)(S(AudioChannelStates)+42u*i);
        wr32(SOUND_SEG,p,c->age);wr16(SOUND_SEG,(uint16_t)(p+4),c->repeats);lifetime_pointer((uint16_t)(p+6),c->start);
        wr16(SOUND_SEG,(uint16_t)(p+10),c->length);wr16(SOUND_SEG,(uint16_t)(p+12),c->sample_mode);wr16(SOUND_SEG,(uint16_t)(p+14),c->sample_rate);
        lifetime_pointer((uint16_t)(p+16),c->cursor);wr16(SOUND_SEG,(uint16_t)(p+20),c->sample_half_length);
        wr16(SOUND_SEG,(uint16_t)(p+22),c->reserved_word);wr16(SOUND_SEG,(uint16_t)(p+24),c->sample_selector);
        wr16(SOUND_SEG,(uint16_t)(p+26),c->sample_accumulator);wr16(SOUND_SEG,(uint16_t)(p+28),c->volume);
        wr32(SOUND_SEG,(uint16_t)(p+30),c->deadline);wr16(SOUND_SEG,(uint16_t)(p+34),c->voice_count);
        wr16(SOUND_SEG,(uint16_t)(p+36),c->first_voice);wr16(SOUND_SEG,(uint16_t)(p+38),c->step_q8);wr16(SOUND_SEG,(uint16_t)(p+40),c->control);
    }
    wr16(SOUND_SEG,S(AdlxPlaybackGuard),state->playback_guard);wr16(SOUND_SEG,S(MusicTicksPerUnit),state->ticks_per_unit);
    wr32(SOUND_SEG,S(AdlxTickCount),state->ticks);wr32(SOUND_SEG,S(MainAdlxTimeOrigin),state->time_origin);
    wr32(SOUND_SEG,S(ScannedMusicClockTicks),state->scanned_ticks);
    wr16(SOUND_SEG,S(MusicFadeStep),state->fade.step_count);wr16(SOUND_SEG,S(MusicFadeDuration),state->fade.duration);
    wr16(SOUND_SEG,S(MusicFadeStartVolume),state->fade.start_volume);wr16(SOUND_SEG,S(MusicFadeTargetVolume),state->fade.target_volume);
    lifetime_pointer(S(SoundBankBase),cells->bank);wr32(SOUND_SEG,S(SoundBankLength),cells->bank_length);
    wr16(SOUND_SEG,S(MainAdlxPlaying),state->playing);wr16(SOUND_SEG,S(MusicFadeScheduled),state->fade.scheduled);
    wr16(SOUND_SEG,S(MusicTrackVolume),state->track_volume);wr16(SOUND_SEG,S(MainAdlxSectionLoopEnabled),state->section_loop_enabled);
    lifetime_pointer(S(FirstScannedEvent),state->section_start);lifetime_pointer(S(MainAdlxSectionEnd),state->section_end);
    lifetime_pointer(S(AdlibInstrumentMap),cells->instrument_map);wr16(SOUND_SEG,S(SoundDeviceBits),cells->devices);
    wr16(SOUND_SEG,S(ReservedAdlibChannelCount),state->reserved_voices);wr16(SOUND_SEG,S(ActiveSampleVoiceCount),cells->sample_count);
    wr16(SOUND_SEG,S(ActiveSampleVoiceMask),cells->sample_mask);wr16(SOUND_SEG,(uint16_t)(S(ActiveSampleVoiceMask)+2),cells->spare[0]);
    wr16(SOUND_SEG,S(CurrentAdlxSlot),state->current_channel);wr16(SOUND_SEG,(uint16_t)(S(CurrentAdlxSlot)+2),cells->spare[1]);
    for(unsigned i=0;i<AUDIO_VOICE_COUNT;i++) {
        audio_bridge_publish_voice(SOUND_SEG,(uint16_t)(S(AdlibVoiceStates)+20u*i),&state->live[i]);
        audio_bridge_publish_voice(SOUND_SEG,(uint16_t)(S(SavedAdlibVoiceStates)+20u*i),&state->displaced[i]);
        audio_bridge_publish_voice(SOUND_SEG,(uint16_t)(S(ScannedAdlibVoiceStates)+20u*i),&state->scanned[i]);
    }
}
EXPORT int c_ClearSoundState(Regs *r)
{
    AudioState state;AudioResetCells cells;audio_bridge_project(SOUND_SEG,&state);
    audio_lifetime_reset(&state,&cells);lifetime_publish_reset(&state,&cells);
    r->ax=logic(r,0,16);r->cx=0;flag(r,DF,0);return UGH_OK;
}
EXPORT int c_BeginSoundDelayMeasurement(Regs *r)
{
    uint16_t ds=r->ds,dx=r->dx;set_al(r,0x20);platform_out(0x20,1,0x20);
    r->ax=SOUND_SEG;r->ds=r->ax;r->dx=S(FinishSoundDelayMeasurement);r->ax=0x2508;
    int status=platform_interrupt(0x21,r);r->ds=ds;r->dx=dx;
    r->ax=audio_calibration_started();logic(r,0,8);return status;
}
EXPORT int c_FinishSoundDelayMeasurement(Regs *r)
{
    uint16_t ds=r->ds,dx=r->dx;set_al(r,0x20);platform_out(0x20,1,0x20);
    r->dx=rd16(r->cs,S(PreviousCalibrationTimerVector));r->ds=rd16(r->cs,S(PreviousCalibrationTimerSegment));
    r->ax=0x2508;int status=platform_interrupt(0x21,r);
    AudioMeasurement measured=audio_calibration_finished(r->cx,dx);
    wr16(r->cs,S(CalibrationLoopRemainder),measured.remainder);r->dx=dx;
    wr16(r->cs,S(SoundIoDelayMultiplier),measured.multiplier);r->cx=1;set_al(r,1);r->ds=ds;return status;
}
EXPORT int c_CalibrateSoundDelay(Regs *r)
{
    Regs saved=*r;r->sp=(uint16_t)(r->sp-12);
    r->ax=0x3508;int status=platform_interrupt(0x21,r);if(status) return status;
    wr16(r->cs,S(PreviousCalibrationTimerVector),r->bx);wr16(r->cs,S(PreviousCalibrationTimerSegment),r->es);
    r->ax=SOUND_SEG;r->ds=r->ax;r->dx=S(BeginSoundDelayMeasurement);r->ax=0x2508;
    status=platform_interrupt(0x21,r);if(status) return status;r->ax=logic(r,0,16);
    AudioCalibrationWork work=audio_calibration_begin(r->dx);
    for(;;) {
        if(!work.budget) return UGH_BUDGET;
        AudioCalibrationAction before=work.action;
        status=platform_service_point_at(SERVICE_TIMER_WAIT,r->cs,before==AUDIO_CALIBRATION_WAIT_BEGIN ? S(loc_1163) : S(loc_116B),r);
        if(status) return status;
        work.marker=r->ax;work.remaining=r->cx;work.progress=r->dx;
        AudioCalibrationAction after=audio_calibration_resume(&work);
        if(before==AUDIO_CALIBRATION_WAIT_BEGIN) sub16(r,r->ax>>8,1,0);
        else if(!work.remaining) {
            uint16_t carry=r->flags&CF;add16(r,r->dx,1,0);flag(r,CF,carry);sub16(r,(uint8_t)r->ax,1,0);
        }
        r->cx=work.remaining;r->dx=work.progress;
        if(after==AUDIO_CALIBRATION_DONE) {uint16_t flags=r->flags;*r=saved;r->flags=flags;return UGH_OK;}
    }
}
static int lifetime_run(Regs *r,int stopping)
{
    uint16_t es=r->es,di=r->di,si=r->si,sp=r->sp,reply=0;
    if(!stopping) r->sp=(uint16_t)(sp-6);
    AudioLifetimeWork work=audio_lifetime_begin(stopping);
    for(;;) {
        uint8_t attempted=rd8(r->cs,S(AdlibInitAttempted)),previous=attempted;
        AudioLifetimeRequest request=audio_lifetime_next(&work,&attempted,rd16(r->cs,S(AdlxPlaybackTimerHandle)),reply);
        if(attempted!=previous) wr8(r->cs,S(AdlibInitAttempted),attempted);
        int status=UGH_OK;
        switch(request.action) {
        case AUDIO_LIFETIME_DONE:
            if(!stopping) {r->ax=work.result ? 1 : logic(r,0,16);r->es=es;r->di=di;r->si=si;r->sp=sp;}
            return UGH_OK;
        case AUDIO_LIFETIME_CALIBRATE:status=lifetime_call(r,r->cs,S(CalibrateSoundDelay),(uint16_t)(S(InitializeAdlibPlayback)+0x18));break;
        case AUDIO_LIFETIME_WRITE:r->bx=request.value;status=c_WriteAdlibRegister(r);break;
        case AUDIO_LIFETIME_DELAY:set_al(r,(uint8_t)request.value);status=c_DelaySoundIo(r);break;
        case AUDIO_LIFETIME_READ:
            r->dx=0x388;set_al(r,(uint8_t)platform_in(r->dx,1));if(ugh_devices.error) return UGH_UNSUPPORTED;reply=(uint8_t)r->ax;break;
        case AUDIO_LIFETIME_SILENCE:status=c_SilenceAdlibOperators(r);break;
        case AUDIO_LIFETIME_INSTALL:status=lifetime_call(r,TIMER_SEG,T(InstallTimerInterrupt),(uint16_t)(S(InitializeAdlibPlayback)+0x90));break;
        case AUDIO_LIFETIME_REGISTER:
            r->bx=request.value;r->cx=0;r->ax=S(TickAdlxPlayback);r->dx=SOUND_SEG;
            status=lifetime_call(r,TIMER_SEG,T(RegisterTimerCallback),(uint16_t)(S(InitializeAdlibPlayback)+0xa0));
            if(!status) wr16(r->cs,S(AdlxPlaybackTimerHandle),r->ax);
            break;
        case AUDIO_LIFETIME_REMOVE:
            r->ax=request.value;status=lifetime_call(r,TIMER_SEG,T(RemoveTimerCallback),(uint16_t)(S(ShutdownAdlibPlayback)+0x14));break;
        case AUDIO_LIFETIME_RESTORE:status=lifetime_call(r,TIMER_SEG,T(RestoreTimerInterrupt),(uint16_t)(S(ShutdownAdlibPlayback)+0x19));break;
        default:return UGH_UNSUPPORTED;
        }
        if(status) return status;
    }
}
EXPORT int c_InitializeAdlibPlayback(Regs *r) {return lifetime_run(r,0);}
EXPORT int c_ShutdownAdlibPlayback(Regs *r) {return lifetime_run(r,1);}
