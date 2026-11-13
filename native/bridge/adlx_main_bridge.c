#include "platform.h"
#include "audio_projection.h"
#include "../adlx_main.h"

int l1_RunMainAdlxEvents(Regs *r);
int l1_HandleMainAdlxInstrument(Regs *r);

static void audio_bridge_delay(Regs *r,unsigned factor)
{
    unsigned product=factor*rd8(r->cs,S(SoundIoDelayMultiplier));
    flag(r,CF,product>255);flag(r,OF,product>255);
}
static uint16_t audio_bridge_inc(Regs *r,uint16_t value)
{
    uint16_t carry=r->flags&CF;
    value=add16(r,value,1,0);flag(r,CF,carry);return value;
}
static void audio_bridge_low_b(Regs *r,uint8_t value)
{
    r->bx=(uint16_t)((r->bx&65280u)|value);
}
static int audio_bridge_timer(Regs *r,const AudioState *state)
{
    uint16_t saved=r->cx;
    r->sp=(uint16_t)(r->sp-2);r->bx=state->timer_period;r->ax=state->playback_timer_handle;r->cx=0;
    r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,r->cs);
    r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,(uint16_t)(S(HandleMainAdlxTimerPeriod)+0x16));
    int status=ugh_dispatch(TIMER_SEG,T(SetTimerCallbackInterval),r);
    r->sp=(uint16_t)(r->sp+6);r->cx=saved;
    return status;
}

/* Preserve the temporary machine calling convention without a shadow semantic
 * interpreter: all persistent stores and OPL values come from audio_main_step.
 * Only scratch registers/defined flags and external TIMER calls live here. */
static int audio_bridge_event(Regs *r,AudioMainOperation operation)
{
    uint8_t code=(uint8_t)r->ax,bytes[12];
    uint16_t old_index=r->di;
    for(unsigned i=0;i<12;i++) bytes[i]=rd8(r->es,(uint16_t)(r->di+i));
    /* Word operands crossing FFFF read a contiguous second byte, whereas the
     * twelve individual instrument reads wrap their effective offsets. */
    if(operation==AUDIO_FREQUENCY || operation==AUDIO_TIMER_PERIOD) {
        uint16_t value=rd16(r->es,r->di);bytes[0]=(uint8_t)value;bytes[1]=(uint8_t)(value>>8);
    }
    if(operation==AUDIO_INSTRUMENT && (code&15)<9) {
        for(unsigned i=0;i<12;i++) {
            uint32_t address=lin(r->es,(uint16_t)(r->di+i));
            uint32_t begin=lin(r->cs,S(AdlibVoiceStates));
            if(address>=begin && address<begin+360) return l1_HandleMainAdlxInstrument(r);
        }
    }
    AudioState state;
    audio_bridge_project(r->cs,&state);
    AudioCursor cursor=audio_bridge_cursor(r->es,r->di);
    uint32_t old_deadline=state.channels[AUDIO_MAIN_CHANNEL].deadline;
    uint16_t old_repeats=state.channels[AUDIO_MAIN_CHANNEL].repeats;
    uint16_t old_control=state.channels[AUDIO_MAIN_CHANNEL].control;
    AudioMainResult result=audio_main_step(&state,operation,code,bytes,&cursor);
    AudioChannel *main=&state.channels[AUDIO_MAIN_CHANNEL];
    if(result.exit==AUDIO_WAIT) {
        wr32(r->cs,S(MainAdlxDeadlineLow),main->deadline);
        wr16(r->cs,S(MainAdlxCursor),main->cursor.index);
    } else if(result.exit==AUDIO_END) {
        if(!(old_control&2)) wr16(r->cs,S(MainAdlxRepeatCount),main->repeats);
        if(result.repeated) {
            wr16(r->cs,S(MainAdlxCursorSegment),audio_bridge_bank(main->cursor));
            wr16(r->cs,S(MainAdlxCursor),main->cursor.index);
            wr32(r->cs,S(MainAdlxDeadlineLow),main->deadline);
            wr32(r->cs,S(MainAdlxTimeOrigin),state.time_origin);
        } else wr16(r->cs,S(MainAdlxFlags),main->control);
    }
    uint8_t channel=result.channel;
    if(channel<9 && (operation==AUDIO_FREQUENCY || operation==AUDIO_KEY_OFF || operation==AUDIO_GAIN || operation==AUDIO_INSTRUMENT)) {
        /* Publishing retained cells is safe only in ordinary serialized RAM;
         * the contract excludes memory-mapped state and observing store hooks. */
        audio_bridge_publish_voice(r->cs,(uint16_t)(S(AdlibVoiceStates)+20*channel),&state.live[channel]);
        audio_bridge_publish_voice(r->cs,(uint16_t)(S(SavedAdlibVoiceStates)+20*channel),&state.displaced[channel]);
    }
    if(result.timer_request) wr16(r->cs,S(AdlxTimerPeriod),state.timer_period);
    for(unsigned i=0;i<result.write_count;i++) {
        platform_out(0x388,1,result.writes[i].reg);
        platform_out(0x389,1,result.writes[i].value);
    }
    r->di=cursor.index;
    uint8_t first=(uint8_t)(9-rd8(r->cs,S(ReservedAdlibChannelCount)));
    switch(operation) {
    case AUDIO_LONG_WAIT:
    case AUDIO_SHORT_WAIT: {
        if(operation==AUDIO_SHORT_WAIT) r->ax&=127u;
        uint16_t low=add16(r,(uint16_t)old_deadline,result.wait_delta,0);
        add16(r,(uint16_t)(old_deadline>>16),0,r->flags&CF);
        (void)low;break;
    }
    case AUDIO_FREQUENCY:
        set_al(r,channel);
        if(channel<9) {
            r->ax=(uint16_t)(bytes[0]+(unsigned)bytes[1]*256u);audio_bridge_low_b(r,first);
            if(result.displaced) r->ax=r->bx=(uint16_t)(channel*20);
            else {flag(r,IF,1);audio_bridge_delay(r,2);}
        }
        break;
    case AUDIO_KEY_OFF:
        set_al(r,channel);
        if(channel<9) {
            audio_bridge_low_b(r,first);
            if(result.displaced) r->ax=r->bx=(uint16_t)(channel*20);
            else audio_bridge_delay(r,2);
        }
        break;
    case AUDIO_GAIN:
        set_al(r,channel);
        if(channel<9) {
            audio_bridge_low_b(r,bytes[0]);r->ax=(uint16_t)(channel*20);
            if(state.current_channel>=12 && (state.reserved_voices&15)) audio_bridge_low_b(r,first);
            if(result.write_count) audio_bridge_delay(r,4);
        }
        r->di=audio_bridge_inc(r,old_index);break;
    case AUDIO_INSTRUMENT:
        set_al(r,channel);
        if(channel<9) {
            r->ax=(uint16_t)(channel*20);flag(r,DF,0);
            if(result.displaced) set_al(r,first);
            else {r->ax=state.current_channel;r->bx=(uint16_t)(channel*20);audio_bridge_delay(r,4);}
        }
        break;
    case AUDIO_TIMER_PERIOD: {
        int status=audio_bridge_timer(r,&state);
        r->di=audio_bridge_inc(r,audio_bridge_inc(r,old_index));
        if(status) return status;
        break;
    }
    case AUDIO_CONTROL:
        if(code==0x77) {
            if(!(old_control&2)) dec16(r,old_repeats);
            if(result.repeated) r->ax=(uint16_t)(state.ticks>>16);
        } else {
            set_ah(r,bytes[0]);audio_bridge_inc(r,old_index);set_al(r,code&15);
            if(code&15) r->ax=bytes[0];
        }
        break;
    case AUDIO_NO_OP:break;
    }
    return result.exit==AUDIO_CONTINUE ? -1 : UGH_OK;
}

EXPORT int c_RunMainAdlxEvents(Regs *r)
{
    /* Mutable dispatch tables are outside the recovered grammar. Keep the
     * independent literal path for a deliberately replaced table entry. */
    const uint16_t targets[16]={S(HandleMainAdlxLongWait),S(HandleMainAdlxFrequency),S(HandleMainAdlxKeyOff),
        S(HandleMainAdlxGain),S(HandleMainAdlxInstrument),S(HandleMainAdlxNoOp),S(HandleMainAdlxTimerPeriod),
        S(HandleMainAdlxControl),S(HandleMainAdlxShortWait),S(HandleMainAdlxShortWait),S(HandleMainAdlxShortWait),
        S(HandleMainAdlxShortWait),S(HandleMainAdlxShortWait),S(HandleMainAdlxShortWait),S(HandleMainAdlxShortWait),S(HandleMainAdlxShortWait)};
    for(unsigned i=0;i<16;i++) if(rd16(r->cs,(uint16_t)(S(MainAdlxDispatchTable)+2*i))!=targets[i]) return l1_RunMainAdlxEvents(r);
    for(unsigned count=0;count<1000000;count++) {
        set_al(r,rd8(r->es,r->di));r->di=audio_bridge_inc(r,r->di);
        set_ah(r,(uint8_t)logic(r,0,8));r->bx=r->ax;
        r->bx=logic(r,(r->bx>>3)&65534u,16);r->bx=add16(r,r->bx,S(MainAdlxDispatchTable),0);
        int status=audio_bridge_event(r,audio_main_operation((uint8_t)r->ax));
        if(status>=0) return status;
    }
    return UGH_BUDGET;
}
static int audio_bridge_entry(Regs *r,AudioMainOperation operation)
{
    int status=audio_bridge_event(r,operation);
    return status<0 ? c_RunMainAdlxEvents(r) : status;
}
EXPORT int c_HandleMainAdlxLongWait(Regs *r) {return audio_bridge_entry(r,AUDIO_LONG_WAIT);}
EXPORT int c_HandleMainAdlxShortWait(Regs *r) {return audio_bridge_entry(r,AUDIO_SHORT_WAIT);}
EXPORT int c_HandleMainAdlxFrequency(Regs *r) {return audio_bridge_entry(r,AUDIO_FREQUENCY);}
EXPORT int c_HandleMainAdlxKeyOff(Regs *r) {return audio_bridge_entry(r,AUDIO_KEY_OFF);}
EXPORT int c_HandleMainAdlxGain(Regs *r) {return audio_bridge_entry(r,AUDIO_GAIN);}
EXPORT int c_HandleMainAdlxInstrument(Regs *r) {return audio_bridge_entry(r,AUDIO_INSTRUMENT);}
EXPORT int c_HandleMainAdlxNoOp(Regs *r) {return audio_bridge_entry(r,AUDIO_NO_OP);}
EXPORT int c_HandleMainAdlxTimerPeriod(Regs *r) {return audio_bridge_entry(r,AUDIO_TIMER_PERIOD);}
EXPORT int c_HandleMainAdlxControl(Regs *r) {return audio_bridge_entry(r,AUDIO_CONTROL);}
