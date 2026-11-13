#include "platform.h"
#include "audio_projection.h"
#include "../adlx_allocation.h"

int l1_StopAdlibTrackChannel(Regs *r);
int l1_RestoreAdlibVoiceAllocation(Regs *r);
int l1_StartAdlibTrackChannel(Regs *r);

typedef struct AllocationFrame {uint16_t sp,bp,si,di,ds;} AllocationFrame;
static void allocation_push(Regs *r,uint16_t value)
{r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,value);}
static AllocationFrame allocation_enter(Regs *r,unsigned locals)
{
    AllocationFrame frame={r->sp,r->bp,r->si,r->di,r->ds};
    allocation_push(r,r->bp);r->bp=r->sp;r->sp=(uint16_t)(r->sp-locals);
    allocation_push(r,r->si);allocation_push(r,r->di);allocation_push(r,r->ds);
    r->ds=UGH_S_C_SoundSystemInitialized;return frame;
}
static int allocation_leave(Regs *r,AllocationFrame frame,int status)
{
    r->sp=frame.sp;r->bp=frame.bp;r->si=frame.si;r->di=frame.di;r->ds=frame.ds;return status;
}
static int allocation_call(Regs *r,uint16_t target,uint16_t resume,const uint16_t *arguments,unsigned count)
{
    uint16_t sp=r->sp;
    for(unsigned i=count;i;i--) allocation_push(r,arguments[i-1]);
    allocation_push(r,r->cs);allocation_push(r,resume);
    int status=ugh_dispatch(UGH_SEG_C,target,r);
    if(status!=UGH_CONTROL_TRANSFER) r->sp=sp;
    return status;
}
static void allocation_publish(const AudioState *state)
{
    for(unsigned i=8;i<13;i++) {
        const AudioChannel *track=&state->channels[i];uint16_t p=(uint16_t)(S(AudioChannelStates)+42*i);
        wr16(SOUND_SEG,(uint16_t)(p+16),track->cursor.index);
        wr16(SOUND_SEG,(uint16_t)(p+18),audio_bridge_bank(track->cursor));
        wr16(SOUND_SEG,(uint16_t)(p+28),track->volume);wr32(SOUND_SEG,(uint16_t)(p+30),track->deadline);
        wr16(SOUND_SEG,(uint16_t)(p+36),track->first_voice);wr16(SOUND_SEG,(uint16_t)(p+40),track->control);
    }
    for(unsigned i=0;i<9;i++) {
        audio_bridge_publish_voice(SOUND_SEG,(uint16_t)(S(AdlibVoiceStates)+20*i),&state->live[i]);
        audio_bridge_publish_voice(SOUND_SEG,(uint16_t)(S(SavedAdlibVoiceStates)+20*i),&state->displaced[i]);
    }
    wr16(SOUND_SEG,S(AdlxPlaybackGuard),state->playback_guard);
    wr16(SOUND_SEG,S(CurrentAdlxSlot),state->current_channel);
    wr16(SOUND_SEG,S(ReservedAdlibChannelCount),state->reserved_voices);
}
static void allocation_delay(Regs *r,unsigned factor)
{
    unsigned product=factor*rd8(SOUND_SEG,S(SoundIoDelayMultiplier));
    flag(r,CF,product>255);flag(r,OF,product>255);
}
/* All decisions, copies, routes and write values come from native code. This
 * journal traversal retains only machine outputs of the old subordinate ABI. */
static void allocation_deliver(Regs *r,const AudioAllocationResult *result)
{
    unsigned next=0;
    for(unsigned i=0;i<result->action_count;i++) {
        const AudioAllocationAction *action=&result->actions[i];
        switch(action->kind) {
        case AUDIO_ALLOCATION_COPY:r->cx=0;break;
        case AUDIO_ALLOCATION_INSTRUMENT:
            r->ax=(uint16_t)(action->channel*20);flag(r,DF,0);
            if(action->displaced) set_al(r,(uint8_t)action->first_reserved);
            else {r->ax=action->current_channel;r->bx=(uint16_t)(action->channel*20);allocation_delay(r,4);}
            break;
        case AUDIO_ALLOCATION_FREQUENCY:flag(r,IF,1);allocation_delay(r,2);break;
        case AUDIO_ALLOCATION_KEY_OFF:allocation_delay(r,2);break;
        case AUDIO_ALLOCATION_VOLUME:if(action->write_count) allocation_delay(r,4);break;
        case AUDIO_ALLOCATION_MUSIC_RESULT:r->bx=(uint16_t)(action->channel*20);r->ax=SOUND_SEG;break;
        case AUDIO_ALLOCATION_EMPTY_RESULT:r->cx=action->channel;break;
        }
        for(unsigned j=0;j<action->write_count;j++) {
            platform_out(0x388,1,result->writes[next].reg);platform_out(0x389,1,result->writes[next].value);next++;
        }
    }
}
static int allocation_literal(Regs *r,AudioAllocationOperation operation)
{
    if(operation==AUDIO_ALLOCATION_STOP) return l1_StopAdlibTrackChannel(r);
    if(operation==AUDIO_ALLOCATION_START) return l1_StartAdlibTrackChannel(r);
    return l1_RestoreAdlibVoiceAllocation(r);
}
static int allocation_entry(Regs *r,AudioAllocationOperation operation)
{
    uint16_t channel=arg16(r,0),volume=operation==AUDIO_ALLOCATION_START ? arg16(r,2) : 0;
    uint16_t devices=rd16(SOUND_SEG,S(SoundDeviceBits));
    AudioState state;audio_bridge_project(SOUND_SEG,&state);
    if(!audio_allocation_supported(&state,operation,channel,devices)) return allocation_literal(r,operation);
    AudioAllocationResult result=audio_allocation_run(&state,operation,channel,volume,devices);
    if(r->flags&DF) for(unsigned i=0;i<result.action_count;i++)
        if(result.actions[i].kind==AUDIO_ALLOCATION_COPY) return allocation_literal(r,operation);
    AllocationFrame frame=allocation_enter(r,operation==AUDIO_ALLOCATION_RESTORE ? 8 : 2);
    r->es=SOUND_SEG;r->ax=operation==AUDIO_ALLOCATION_START ? 65535 : SOUND_SEG;
    if(result.clamped) wr16(r->ss,(uint16_t)(frame.sp+6),result.volume);
    allocation_publish(&state);
    if(operation==AUDIO_ALLOCATION_RESTORE || (operation==AUDIO_ALLOCATION_STOP && result.performed)) {
        r->bx=(uint16_t)(channel*42);r->ax=result.first_voice;
    }
    allocation_deliver(r,&result);
    if(operation==AUDIO_ALLOCATION_STOP && result.performed) {r->cx=channel;r->ax=SOUND_SEG;r->dx=result.old_guard;}
    if(operation==AUDIO_ALLOCATION_START) {
        if(result.performed) {r->cx=(uint16_t)state.channels[channel].deadline;r->bx=(uint16_t)(channel*42);r->dx=result.old_guard;}
        r->ax=result.value;
    }
    return allocation_leave(r,frame,UGH_OK);
}
EXPORT int c_StopAdlibTrackChannel(Regs *r) {return allocation_entry(r,AUDIO_ALLOCATION_STOP);}
EXPORT int c_RestoreAdlibVoiceAllocation(Regs *r) {return allocation_entry(r,AUDIO_ALLOCATION_RESTORE);}
EXPORT int c_StartAdlibTrackChannel(Regs *r) {return allocation_entry(r,AUDIO_ALLOCATION_START);}

/* Parsing remains a synchronous L1 service. Selection/stealing and all voice
 * allocation lifecycle endpoints resolve to this native unit. Reproject after
 * each service; never publish a stale state snapshot over its loader stores. */
EXPORT int c_PlayAdlibEffect(Regs *r)
{
    AllocationFrame frame=allocation_enter(r,2);uint16_t args[5];
    args[1]=rd16(r->ss,(uint16_t)(frame.sp+4));args[2]=rd16(r->ss,(uint16_t)(frame.sp+6));
    args[3]=rd16(r->ss,(uint16_t)(frame.sp+8));args[4]=rd16(r->ss,(uint16_t)(frame.sp+10));
    r->es=SOUND_SEG;r->ax=65535;
    if(!(rd16(SOUND_SEG,S(SoundDeviceBits))&1u)) return allocation_leave(r,frame,UGH_OK);
    AudioState state;audio_bridge_project(SOUND_SEG,&state);AudioEffectSelection choice=audio_effect_select(&state);
    args[0]=choice.channel;int status;
    if(choice.replace) {
        status=allocation_call(r,UGH_O_C_StopAdlibTrackChannel,(uint16_t)(UGH_O_C_PlayAdlibEffect+0xad),args,1);
        if(status) return allocation_leave(r,frame,status);
        if(rd16(SOUND_SEG,(uint16_t)(S(AudioChannelStates)+42*choice.channel+40))&1u) {r->ax=65535;return allocation_leave(r,frame,UGH_OK);}
    }
    status=allocation_call(r,UGH_O_C_LoadAdlibChannel,(uint16_t)(UGH_O_C_PlayAdlibEffect+(choice.replace ? 0xd0 : 0x4f)),args,5);
    if(status) return allocation_leave(r,frame,status);
    if((int16_t)r->ax>=0) {
        uint16_t start_args[2]={choice.channel,args[3]};
        status=allocation_call(r,UGH_O_C_StartAdlibTrackChannel,(uint16_t)(UGH_O_C_PlayAdlibEffect+(choice.replace ? 0xdd : 0x5c)),start_args,2);
        if(status) return allocation_leave(r,frame,status);
        if(choice.replace && (int16_t)r->ax<0) return allocation_leave(r,frame,UGH_OK);
    } else if(choice.replace) {r->ax=65535;return allocation_leave(r,frame,UGH_OK);}
    r->ax=choice.channel;return allocation_leave(r,frame,UGH_OK);
}
