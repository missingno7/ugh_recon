#include "platform.h"
#include "audio_projection.h"
#include "../adlx_sections.h"
int l1_ScanMusicEvents(Regs *r);
int l1_ApplyScannedMusicEvents(Regs *r);
typedef struct SectionFrame {uint16_t sp,bp,si,di,ds;} SectionFrame;
static void section_push(Regs *r,uint16_t value) {r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,value);}
static SectionFrame section_enter(Regs *r,unsigned locals,unsigned saves)
{
    SectionFrame f={r->sp,r->bp,r->si,r->di,r->ds};section_push(r,r->bp);r->bp=r->sp;r->sp=(uint16_t)(r->sp-locals);
    if(saves&1) section_push(r,r->si);
    if(saves&2) section_push(r,r->di);
    section_push(r,r->ds);r->ds=UGH_S_C_SoundSystemInitialized;return f;
}
static int section_leave(Regs *r,SectionFrame f,int status)
{r->sp=f.sp;r->bp=f.bp;r->si=f.si;r->di=f.di;r->ds=f.ds;return status;}
static int section_call(Regs *r,uint16_t bank,uint16_t target,uint16_t resume)
{section_push(r,r->cs);section_push(r,resume);int status=ugh_dispatch(bank,target,r);r->sp=(uint16_t)(r->sp+4);return status;}
static int section_overlap(uint32_t first,uint32_t last,uint32_t other,uint32_t end)
{return first<end && other<last;}
static int section_source(Regs *r,uint16_t bank)
{
    uint32_t first=(uint32_t)bank*16u,last=first+65537;
    return !section_overlap(first,last,(uint32_t)SOUND_SEG*16u,(uint32_t)SOUND_SEG*16u+65537) &&
        !section_overlap(first,last,(uint32_t)r->ss*16u,(uint32_t)r->ss*16u+65537) && !section_overlap(first,last,0xa0000,0xc0000);
}
static void section_table(Regs *r,AudioScanDispatch table[7])
{
    const uint16_t offsets[7]={0x11d,0x155,0x17d,0x19d,0x1c2,0x209,0x20c};
    uint16_t at=(uint16_t)(UGH_O_C_ScanMusicEvents+0x2c8);
    for(unsigned i=0;i<7;i++) {
        table[i].value=rd16(r->cs,(uint16_t)(at+2*i));table[i].action=AUDIO_SCAN_BAD;
        uint16_t target=rd16(r->cs,(uint16_t)(at+14+2*i));
        for(unsigned j=0;j<7;j++) if(target==(uint16_t)(UGH_O_C_ScanMusicEvents+offsets[j])) table[i].action=(AudioScanAction)j;
    }
}
EXPORT int c_ScanMusicEvents(Regs *r)
{
    AudioState state;audio_bridge_project(SOUND_SEG,&state);uint16_t devices=rd16(SOUND_SEG,S(SoundDeviceBits));
    if((devices&1u) && state.playing && !section_source(r,audio_bridge_bank(state.channels[12].start))) return l1_ScanMusicEvents(r);
    AudioScanDispatch table[7];section_table(r,table);
    AudioScanWork work=audio_section_scan(&state,arg16(r,0),arg16(r,2),devices,table);
    if(work.exit==AUDIO_SCAN_BOUNDARY) return l1_ScanMusicEvents(r);
    SectionFrame f=section_enter(r,24,3);r->es=SOUND_SEG;r->ax=work.exit==AUDIO_SCAN_DONE ? 1 : 65535;
    if(work.entered) {
        flag(r,DF,0);if(work.copied) r->cx=0;
        for(unsigned i=0;i<9;i++) audio_bridge_publish_voice(SOUND_SEG,(uint16_t)(S(ScannedAdlibVoiceStates)+20*i),&state.scanned[i]);
        wr32(SOUND_SEG,S(ScannedMusicClockTicks),state.scanned_ticks);
        wr16(SOUND_SEG,(uint16_t)(S(FirstScannedEvent)+2),audio_bridge_bank(state.section_start));wr16(SOUND_SEG,S(FirstScannedEvent),state.section_start.index);
        wr16(SOUND_SEG,(uint16_t)(S(MainAdlxSectionEnd)+2),audio_bridge_bank(state.section_end));wr16(SOUND_SEG,S(MainAdlxSectionEnd),state.section_end.index);
        wr16(SOUND_SEG,S(MainAdlxSectionLoopEnabled),state.section_loop_enabled);
    }
    return section_leave(r,f,work.exit==AUDIO_SCAN_BUDGET ? UGH_BUDGET : work.exit==AUDIO_SCAN_CALLBACK ? UGH_BAD_CALLBACK : UGH_OK);
}
static void section_delay(Regs *r,unsigned factor)
{unsigned product=factor*rd8(SOUND_SEG,S(SoundIoDelayMultiplier));flag(r,CF,product>255);flag(r,OF,product>255);}
EXPORT int c_ApplyScannedMusicEvents(Regs *r)
{
    AudioState state;audio_bridge_project(SOUND_SEG,&state);uint16_t devices=rd16(SOUND_SEG,S(SoundDeviceBits));
    if((devices&1u) && (state.channels[12].voice_count>9 || ((r->flags&DF) && state.channels[12].voice_count))) return l1_ApplyScannedMusicEvents(r);
    AudioSectionApply result=audio_section_apply(&state,devices);
    SectionFrame f=section_enter(r,0,1);r->es=SOUND_SEG;
    if(devices&1u) {
        wr32(SOUND_SEG,S(MainAdlxCursor),(uint32_t)audio_bridge_bank(state.channels[12].cursor)*65536u+state.channels[12].cursor.index);
        wr32(SOUND_SEG,S(MainAdlxTimeOrigin),state.time_origin);
        for(unsigned i=0;i<9;i++) {
            audio_bridge_publish_voice(SOUND_SEG,(uint16_t)(S(AdlibVoiceStates)+20*i),&state.live[i]);
            audio_bridge_publish_voice(SOUND_SEG,(uint16_t)(S(SavedAdlibVoiceStates)+20*i),&state.displaced[i]);
        }
    }
    unsigned next=0;
    for(unsigned i=0;i<result.action_count;i++) {
        const AudioSectionAction *a=&result.actions[i];
        if(a->kind==AUDIO_SECTION_COPY) r->cx=0;
        else if(a->kind==AUDIO_SECTION_INSTRUMENT) {
            flag(r,DF,0);r->ax=(uint16_t)(a->channel*20);
            if(a->displaced) set_al(r,(uint8_t)a->first_reserved);
            else {r->ax=a->current_channel;r->bx=(uint16_t)(a->channel*20);section_delay(r,4);}
        } else if(a->kind==AUDIO_SECTION_FREQUENCY) {flag(r,IF,1);section_delay(r,2);}
        else if(a->write_count) section_delay(r,4);
        for(unsigned j=0;j<a->write_count;j++) {platform_out(0x388,1,result.writes[next].reg);platform_out(0x389,1,result.writes[next].value);next++;}
    }
    return section_leave(r,f,UGH_OK);
}
static uint16_t section_inc(Regs *r,uint16_t value)
{uint16_t carry=r->flags&CF;value=add16(r,value,1,0);flag(r,CF,carry);return value;}
/* Callback composition reprojects after every call. In particular the raw
 * current slot is incremented after effect restoration, never replaced with
 * a precomputed ordinal. AdvanceGuardedSoundClock/fades remain separate. */
EXPORT int c_TickAdlxPlayback(Regs *r)
{
    AudioState state;audio_bridge_project(r->cs,&state);uint32_t old=state.ticks;
    int entered=audio_section_tick_begin(&state);
    section_inc(r,(uint16_t)old);if(!(uint16_t)state.ticks) section_inc(r,(uint16_t)(old>>16));
    wr32(r->cs,S(AdlxTickCount),state.ticks);
    if(!entered) return UGH_OK;
    wr16(r->cs,S(AdlxPlaybackGuard),state.playback_guard);
    uint16_t ax=r->ax,bx=r->bx,dx=r->dx;r->sp=(uint16_t)(r->sp-6);int status=0;
    if(state.playing&1u) {
        r->dx=(uint16_t)(state.ticks>>16);
        if(r->dx==(uint16_t)(state.channels[12].deadline>>16)) r->ax=(uint16_t)state.ticks;
        if(audio_section_main_due(&state)) {
            wr16(r->cs,S(CurrentAdlxRecordOffset),(uint16_t)(S(AudioChannelStates)+12*42));
            audio_section_main_context(&state);wr16(r->cs,S(CurrentAdlxSlot),state.current_channel);
            uint16_t es=r->es,di=r->di,workbx=r->bx;r->sp=(uint16_t)(r->sp-6);
            r->di=state.channels[12].cursor.index;r->es=audio_bridge_bank(state.channels[12].cursor);
            if(audio_section_apply_due(&state)) {
                status=section_call(r,UGH_SEG_C,UGH_O_C_ApplyScannedMusicEvents,(uint16_t)(S(TickAdlxPlayback)+0x84));if(status) return status;
                r->di=rd16(r->cs,S(MainAdlxCursor));r->es=rd16(r->cs,S(MainAdlxCursorSegment));
            }
            status=section_call(r,r->cs,S(RunMainAdlxEvents),(uint16_t)(S(TickAdlxPlayback)+0x8d));
            r->sp=(uint16_t)(r->sp+6);r->bx=workbx;r->di=di;r->es=es;if(status) return status;
        }
    }
    audio_bridge_project(r->cs,&state);
    if(state.reserved_voices&15u) {
        r->bx=(uint16_t)(S(AudioChannelStates)+8*42);audio_section_effects_begin(&state);wr16(r->cs,S(CurrentAdlxSlot),state.current_channel);
        for(unsigned i=AUDIO_FIRST_EFFECT_CHANNEL;i<AUDIO_MAIN_CHANNEL;i++) {
            audio_bridge_project(r->cs,&state);set_al(r,(uint8_t)(state.channels[i].control&5u));
            if((uint8_t)r->ax==5) {
                r->ax=(uint16_t)(state.ticks>>16);
                if(r->ax==(uint16_t)(state.channels[i].deadline>>16)) r->ax=(uint16_t)state.ticks;
                if(audio_section_effect_due(&state,i)) {
                    wr16(r->cs,S(CurrentAdlxRecordOffset),r->bx);
                    uint16_t es=r->es,di=r->di,workbx=r->bx;r->sp=(uint16_t)(r->sp-6);
                    r->di=state.channels[i].cursor.index;r->es=audio_bridge_bank(state.channels[i].cursor);
                    status=section_call(r,r->cs,S(RunEffectAdlxEvents),(uint16_t)(S(TickAdlxPlayback)+0xe2));
                    r->sp=(uint16_t)(r->sp+6);r->es=es;r->di=di;r->bx=workbx;if(status) return status;
                }
            }
            uint16_t old_current=rd16(r->cs,S(CurrentAdlxSlot));state.current_channel=old_current;
            audio_section_effect_next(&state);wr16(r->cs,S(CurrentAdlxSlot),state.current_channel);
            section_inc(r,old_current);r->bx=(uint16_t)(r->bx+42);
        }
    }
    audio_section_tick_end(&state);wr16(r->cs,S(AdlxPlaybackGuard),state.playback_guard);
    r->sp=(uint16_t)(r->sp+6);r->ax=ax;r->bx=bx;r->dx=dx;return UGH_OK;
}
