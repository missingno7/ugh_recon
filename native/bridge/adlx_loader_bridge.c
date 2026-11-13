#include "platform.h"
#include "../adlx_loader.h"

int l1_LoadAdlibTrackData(Regs *r);
typedef struct LoaderFrame {uint16_t sp,bp,si,di,ds;} LoaderFrame;
static AudioCursor loader_cursor(uint16_t bank,uint16_t offset)
{AudioCursor cursor={ugh_mem+(uint32_t)bank*16u,offset};return cursor;}
static uint16_t loader_bank(AudioCursor cursor)
{return (uint16_t)((cursor.window-ugh_mem)/16);}
static AudioCursor loader_pointer(uint16_t offset)
{return loader_cursor(rd16(SOUND_SEG,(uint16_t)(offset+2)),rd16(SOUND_SEG,offset));}
static void loader_push(Regs *r,uint16_t value)
{r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,value);}
static LoaderFrame loader_enter(Regs *r,unsigned locals,unsigned saves)
{
    LoaderFrame frame={r->sp,r->bp,r->si,r->di,r->ds};
    loader_push(r,r->bp);r->bp=r->sp;r->sp=(uint16_t)(r->sp-locals);
    if(saves&1) loader_push(r,r->si);
    if(saves&2) loader_push(r,r->di);
    loader_push(r,r->ds);r->ds=UGH_S_C_SoundSystemInitialized;return frame;
}
static int loader_leave(Regs *r,LoaderFrame frame,int status)
{r->sp=frame.sp;r->bp=frame.bp;r->si=frame.si;r->di=frame.di;r->ds=frame.ds;return status;}
static int loader_overlap(uint32_t first,uint32_t end,uint32_t other,uint32_t limit)
{return first<limit && other<end;}
static int loader_ordinary(Regs *r,uint16_t bank)
{
    uint32_t first=(uint32_t)bank*16u,end=first+65537u;
    return !loader_overlap(first,end,(uint32_t)SOUND_SEG*16u,(uint32_t)SOUND_SEG*16u+65537u) &&
        !loader_overlap(first,end,(uint32_t)r->ss*16u,(uint32_t)r->ss*16u+65537u) &&
        !loader_overlap(first,end,0xa0000u,0xc0000u);
}
EXPORT int c_LoadAdlibTrackData(Regs *r)
{
    uint16_t channel=arg16(r,0),bank=arg16(r,4);
    if((rd16(SOUND_SEG,S(SoundDeviceBits))&1u) && channel>=8 && channel<=12 && !loader_ordinary(r,bank)) return l1_LoadAdlibTrackData(r);
    LoaderFrame frame=loader_enter(r,16,3);
    /* This writer's read projection is only reservations. All other machine
     * fields are retained in place; publish only the loader's explicit stores. */
    AudioState state={0};state.reserved_voices=rd16(SOUND_SEG,S(ReservedAdlibChannelCount));
    AudioCursor input=loader_cursor(bank,rd16(r->ss,(uint16_t)(frame.sp+6)));
    AudioAdlxLoadResult result=audio_adlx_load(&state,channel,&input,
        rd16(r->ss,(uint16_t)(frame.sp+10)),rd16(SOUND_SEG,S(SoundDeviceBits)));
    if(result.stage!=AUDIO_ADLX_GATE) wr16(r->ss,(uint16_t)(frame.sp+6),input.index);
    if(result.main_map) {
        wr16(SOUND_SEG,(uint16_t)(S(AdlibInstrumentMap)+2),loader_bank(result.instrument_map));
        wr16(SOUND_SEG,S(AdlibInstrumentMap),result.instrument_map.index);
        wr16(SOUND_SEG,S(MusicTicksPerUnit),state.ticks_per_unit);
    }
    if(result.stage==AUDIO_ADLX_LOADED) {
        const AudioChannel *track=&state.channels[channel];uint16_t p=(uint16_t)(S(AudioChannelStates)+channel*42);
        wr16(SOUND_SEG,(uint16_t)(p+38),track->step_q8);wr16(SOUND_SEG,(uint16_t)(p+10),track->length);
        wr16(SOUND_SEG,(uint16_t)(p+34),track->voice_count);
        wr16(SOUND_SEG,(uint16_t)(p+18),loader_bank(track->cursor));wr16(SOUND_SEG,(uint16_t)(p+16),track->cursor.index);
        wr16(SOUND_SEG,(uint16_t)(p+8),loader_bank(track->start));wr16(SOUND_SEG,(uint16_t)(p+6),track->start.index);
        wr16(SOUND_SEG,(uint16_t)(p+40),track->control);
        if(rd16(r->ss,(uint16_t)(frame.sp+10))) wr16(SOUND_SEG,(uint16_t)(p+4),track->repeats);
    }
    r->ax=result.value;
    if(result.swaps) r->dx=result.swap_high;
    r->es=result.stage>=AUDIO_ADLX_ROOT_TAG && result.stage<=AUDIO_ADLX_TRACK_TAG ? bank : SOUND_SEG;
    return loader_leave(r,frame,UGH_OK);
}
static int loader_call(Regs *r,uint16_t target,uint16_t resume,const uint16_t *arguments,unsigned count)
{
    uint16_t sp=r->sp;
    for(unsigned i=count;i;i--) loader_push(r,arguments[i-1]);
    loader_push(r,r->cs);loader_push(r,resume);
    int status=ugh_dispatch(UGH_SEG_C,target,r);if(status!=UGH_CONTROL_TRANSFER) r->sp=sp;return status;
}
EXPORT int c_LoadAdlibChannel(Regs *r)
{
    LoaderFrame frame=loader_enter(r,0,1);uint16_t channel=rd16(r->ss,(uint16_t)(frame.sp+4));r->ax=65535;
    if(channel<8) return loader_leave(r,frame,UGH_OK);
    int status=loader_call(r,UGH_O_C_StopAdlibTrackChannel,(uint16_t)(UGH_O_C_LoadAdlibChannel+0x1d),&channel,1);
    if(status) return status==UGH_CONTROL_TRANSFER ? status : loader_leave(r,frame,status);
    uint16_t arguments[4]={channel,rd16(r->ss,(uint16_t)(frame.sp+6)),rd16(r->ss,(uint16_t)(frame.sp+8)),rd16(r->ss,(uint16_t)(frame.sp+12))};
    status=loader_call(r,UGH_O_C_LoadAdlibTrackData,(uint16_t)(UGH_O_C_LoadAdlibChannel+0x2d),arguments,4);
    if(status) return status==UGH_CONTROL_TRANSFER ? status : loader_leave(r,frame,status);
    uint16_t p=(uint16_t)(S(AudioChannelStates)+42u*channel);AudioChannel track={0};
    track.volume=rd16(SOUND_SEG,(uint16_t)(p+28));
    uint16_t value=audio_adlx_loaded_volume(&track,rd16(r->ss,(uint16_t)(frame.sp+10)),r->ax);
    if(r->ax) {r->es=SOUND_SEG;wr16(SOUND_SEG,(uint16_t)(p+28),track.volume);}
    r->ax=value;return loader_leave(r,frame,UGH_OK);
}
EXPORT int c_ResetAdlibTrackChannelCursor(Regs *r)
{
    uint16_t channel=arg16(r,0);
    if((int16_t)channel>12) {r->ax=65535;return UGH_OK;}
    uint16_t p=(uint16_t)(S(AudioChannelStates)+42u*channel);r->es=SOUND_SEG;
    AudioChannel track={0};track.control=rd16(SOUND_SEG,(uint16_t)(p+40));
    if(track.control&4u) track.start=loader_pointer((uint16_t)(p+6));
    r->ax=audio_adlx_reset(&track);
    if(r->ax==1) {wr16(SOUND_SEG,(uint16_t)(p+18),loader_bank(track.cursor));wr16(SOUND_SEG,(uint16_t)(p+16),track.cursor.index);}
    return UGH_OK;
}
