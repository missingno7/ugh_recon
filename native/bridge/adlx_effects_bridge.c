#include "platform.h"
#include "audio_projection.h"
#include "../adlx_effects.h"

int l1_RunEffectAdlxEvents(Regs *r);
int l1_HandleEffectAdlxLongWait(Regs *r);
int l1_HandleEffectAdlxShortWait(Regs *r);
int l1_HandleEffectAdlxFrequency(Regs *r);
int l1_HandleEffectAdlxKeyOff(Regs *r);
int l1_HandleEffectAdlxGain(Regs *r);
int l1_HandleEffectAdlxInstrument(Regs *r);
int l1_HandleEffectAdlxNoOp(Regs *r);
int l1_HandleEffectAdlxTimerPeriod(Regs *r);
int l1_HandleEffectAdlxControl(Regs *r);

static int effects_bridge_literal(Regs *r,AudioMainOperation operation)
{
    switch(operation) {
    case AUDIO_LONG_WAIT:return l1_HandleEffectAdlxLongWait(r);
    case AUDIO_SHORT_WAIT:return l1_HandleEffectAdlxShortWait(r);
    case AUDIO_FREQUENCY:return l1_HandleEffectAdlxFrequency(r);
    case AUDIO_KEY_OFF:return l1_HandleEffectAdlxKeyOff(r);
    case AUDIO_GAIN:return l1_HandleEffectAdlxGain(r);
    case AUDIO_INSTRUMENT:return l1_HandleEffectAdlxInstrument(r);
    case AUDIO_NO_OP:return l1_HandleEffectAdlxNoOp(r);
    case AUDIO_TIMER_PERIOD:return l1_HandleEffectAdlxTimerPeriod(r);
    case AUDIO_CONTROL:return l1_HandleEffectAdlxControl(r);
    }
    return UGH_UNSUPPORTED;
}
static uint16_t effects_bridge_inc(Regs *r,uint16_t value)
{
    uint16_t carry=r->flags&CF;value=add16(r,value,1,0);flag(r,CF,carry);return value;
}
static void effects_bridge_delay(Regs *r,unsigned factor)
{
    unsigned product=factor*rd8(r->cs,S(SoundIoDelayMultiplier));
    flag(r,CF,product>255);flag(r,OF,product>255);
}
static int effects_bridge_call(Regs *r,uint16_t bank,uint16_t target,uint16_t resume)
{
    r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,r->cs);
    r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,resume);
    int status=ugh_dispatch(bank,target,r);r->sp=(uint16_t)(r->sp+4);return status;
}

/* The only semantic external calls are TIMER interval and C stop/restoration.
 * All native stores are published BEFORE a stop. No cached state is written
 * back after C, so its compaction, current-slot and voice updates survive. */
static int effects_bridge_event(Regs *r,AudioMainOperation operation)
{
    uint16_t record=rd16(r->cs,S(CurrentAdlxRecordOffset));
    uint16_t relative=(uint16_t)(record-S(AudioChannelStates));
    if(relative%42 || relative/42<AUDIO_FIRST_EFFECT_CHANNEL ||
       relative/42>=AUDIO_FIRST_EFFECT_CHANNEL+AUDIO_EFFECT_CHANNEL_COUNT) return effects_bridge_literal(r,operation);
    unsigned index=relative/42;
    uint8_t code=(uint8_t)r->ax,bytes[12];
    uint16_t old_index=r->di;
    uint8_t effective=(uint8_t)((code&15u)+rd8(r->cs,(uint16_t)(record+0x24)));
    if(operation==AUDIO_INSTRUMENT && effective<9) {
        for(unsigned i=0;i<12;i++) {
            uint32_t address=lin(r->es,(uint16_t)(r->di+i));
            uint32_t first=lin(r->cs,S(AdlibVoiceStates));
            if(address>=first && address<first+360) return effects_bridge_literal(r,operation);
        }
    }
    for(unsigned i=0;i<12;i++) bytes[i]=rd8(r->es,(uint16_t)(r->di+i));
    if(operation==AUDIO_FREQUENCY || operation==AUDIO_TIMER_PERIOD || operation==AUDIO_GAIN) {
        uint16_t value=rd16(r->es,r->di);bytes[0]=(uint8_t)value;bytes[1]=(uint8_t)(value>>8);
    }
    AudioState state;audio_bridge_project(r->cs,&state);
    AudioChannel *track=&state.channels[index];
    uint32_t old_deadline=track->deadline;
    uint16_t old_repeats=track->repeats,old_control=track->control;
    AudioCursor cursor=audio_bridge_cursor(r->es,r->di);
    AudioEffectsResult result=audio_effects_step(&state,track,operation,code,bytes,&cursor);
    if(result.exit==AUDIO_EFFECTS_WAIT) {
        wr32(r->cs,(uint16_t)(record+0x1e),track->deadline);
        wr16(r->cs,(uint16_t)(record+0x10),track->cursor.index);
    }
    if(operation==AUDIO_CONTROL && code==0x77) {
        if(!(old_control&2)) wr16(r->cs,(uint16_t)(record+4),track->repeats);
        if(result.repeated) {
            wr16(r->cs,(uint16_t)(record+0x12),audio_bridge_bank(track->cursor));
            wr16(r->cs,(uint16_t)(record+0x10),track->cursor.index);
        }
    }
    if(operation==AUDIO_TIMER_PERIOD && result.exit!=AUDIO_EFFECTS_DIVIDE_FAULT) {
        if(result.timer_request) wr16(r->cs,S(AdlxTimerPeriod),state.timer_period);
        else wr16(r->cs,(uint16_t)(record+0x26),track->step_q8);
    }
    if(effective<9 && operation>=AUDIO_FREQUENCY && operation<=AUDIO_INSTRUMENT) {
        audio_bridge_publish_voice(r->cs,(uint16_t)(S(AdlibVoiceStates)+20*effective),&state.live[effective]);
        audio_bridge_publish_voice(r->cs,(uint16_t)(S(SavedAdlibVoiceStates)+20*effective),&state.displaced[effective]);
    } else if(effective==9 && operation==AUDIO_INSTRUMENT)
        wr16(r->cs,(uint16_t)(S(SavedAdlibVoiceStates)+16),state.displaced[0].owner);
    for(unsigned i=0;i<result.write_count;i++) {
        platform_out(0x388,1,result.writes[i].reg);platform_out(0x389,1,result.writes[i].value);
    }
    r->di=cursor.index;
    switch(operation) {
    case AUDIO_LONG_WAIT:
    case AUDIO_SHORT_WAIT: {
        r->bx=record;r->ax=(uint16_t)result.wait_delta;
        add16(r,(uint16_t)old_deadline,(uint16_t)result.wait_delta,0);
        add16(r,(uint16_t)(old_deadline>>16),(uint16_t)(result.wait_delta>>16),r->flags&CF);
        break;
    }
    case AUDIO_FREQUENCY:
    case AUDIO_KEY_OFF:
        set_al(r,effective);r->bx=record;
        if(effective<9) {if(operation==AUDIO_FREQUENCY) flag(r,IF,1);effects_bridge_delay(r,2);}
        break;
    case AUDIO_GAIN:
        set_al(r,effective);r->bx=record;
        if(effective<9) {
            r->ax=(uint16_t)(effective*20);
            if(state.current_channel>=12 && (state.reserved_voices&15))
                r->bx=(uint16_t)((r->bx&65280u)|(uint8_t)(9-(uint8_t)state.reserved_voices));
            if(result.write_count) effects_bridge_delay(r,4);
        }
        r->di=effects_bridge_inc(r,old_index);break;
    case AUDIO_INSTRUMENT:
        set_al(r,effective);r->bx=record;
        if(effective<=9) r->bx=(uint16_t)(effective*20);
        if(effective<9) {
            r->ax=(uint16_t)(effective*20);flag(r,DF,0);
            if(result.displaced) set_al(r,(uint8_t)(9-(uint8_t)state.reserved_voices));
            else {r->ax=state.current_channel;effects_bridge_delay(r,4);}
        }
        break;
    case AUDIO_TIMER_PERIOD: {
        uint16_t saved_cx=r->cx,saved_dx=r->dx;r->sp=(uint16_t)(r->sp-4);
        if(result.exit==AUDIO_EFFECTS_DIVIDE_FAULT) {r->bx=state.timer_period;return UGH_UNSUPPORTED;}
        int status=UGH_OK;
        if(result.timer_request) {
            r->bx=state.timer_period;r->ax=state.playback_timer_handle;r->cx=0;
            r->di=old_index;
            status=effects_bridge_call(r,TIMER_SEG,T(SetTimerCallbackInterval),(uint16_t)(S(HandleEffectAdlxTimerPeriod)+0x2f));
        } else {r->ax=track->step_q8;r->bx=record;}
        r->di=effects_bridge_inc(r,effects_bridge_inc(r,old_index));r->cx=saved_cx;r->dx=saved_dx;
        r->sp=(uint16_t)(r->sp+4);if(status) return status;
        break;
    }
    case AUDIO_CONTROL:
        if(code==0x77) {
            r->bx=record;if(!(old_control&2)) dec16(r,old_repeats);
            if(result.stop_request) {
                r->sp=(uint16_t)(r->sp-2);wr16(r->ss,r->sp,state.current_channel);
                int status=effects_bridge_call(r,UGH_SEG_C,UGH_O_C_StopAdlibTrackChannel,(uint16_t)(S(HandleEffectAdlxControl)+0x46));
                r->sp=(uint16_t)(r->sp+2);return status;
            }
            r->ax=track->start.index;
        } else {
            set_ah(r,bytes[0]);effects_bridge_inc(r,old_index);set_al(r,code&15);
            if(code&15) r->ax=bytes[0];
        }
        break;
    case AUDIO_NO_OP:break;
    }
    return result.exit==AUDIO_EFFECTS_CONTINUE ? -1 : UGH_OK;
}

EXPORT int c_RunEffectAdlxEvents(Regs *r)
{
    const uint16_t targets[16]={S(HandleEffectAdlxLongWait),S(HandleEffectAdlxFrequency),S(HandleEffectAdlxKeyOff),
        S(HandleEffectAdlxGain),S(HandleEffectAdlxInstrument),S(HandleEffectAdlxNoOp),S(HandleEffectAdlxTimerPeriod),
        S(HandleEffectAdlxControl),S(HandleEffectAdlxShortWait),S(HandleEffectAdlxShortWait),S(HandleEffectAdlxShortWait),
        S(HandleEffectAdlxShortWait),S(HandleEffectAdlxShortWait),S(HandleEffectAdlxShortWait),S(HandleEffectAdlxShortWait),S(HandleEffectAdlxShortWait)};
    for(unsigned i=0;i<16;i++) if(rd16(r->cs,(uint16_t)(S(EffectAdlxDispatchTable)+2*i))!=targets[i]) return l1_RunEffectAdlxEvents(r);
    for(unsigned count=0;count<1000000;count++) {
        set_al(r,rd8(r->es,r->di));r->di=effects_bridge_inc(r,r->di);
        set_ah(r,(uint8_t)logic(r,0,8));r->bx=r->ax;
        r->bx=logic(r,(r->bx>>3)&65534u,16);r->bx=add16(r,r->bx,S(EffectAdlxDispatchTable),0);
        int status=effects_bridge_event(r,audio_main_operation((uint8_t)r->ax));if(status>=0) return status;
    }
    return UGH_BUDGET;
}
static int effects_bridge_entry(Regs *r,AudioMainOperation operation)
{
    int status=effects_bridge_event(r,operation);return status<0 ? c_RunEffectAdlxEvents(r) : status;
}
EXPORT int c_HandleEffectAdlxLongWait(Regs *r) {return effects_bridge_entry(r,AUDIO_LONG_WAIT);}
EXPORT int c_HandleEffectAdlxShortWait(Regs *r) {return effects_bridge_entry(r,AUDIO_SHORT_WAIT);}
EXPORT int c_HandleEffectAdlxFrequency(Regs *r) {return effects_bridge_entry(r,AUDIO_FREQUENCY);}
EXPORT int c_HandleEffectAdlxKeyOff(Regs *r) {return effects_bridge_entry(r,AUDIO_KEY_OFF);}
EXPORT int c_HandleEffectAdlxGain(Regs *r) {return effects_bridge_entry(r,AUDIO_GAIN);}
EXPORT int c_HandleEffectAdlxInstrument(Regs *r) {return effects_bridge_entry(r,AUDIO_INSTRUMENT);}
EXPORT int c_HandleEffectAdlxNoOp(Regs *r) {return effects_bridge_entry(r,AUDIO_NO_OP);}
EXPORT int c_HandleEffectAdlxTimerPeriod(Regs *r) {return effects_bridge_entry(r,AUDIO_TIMER_PERIOD);}
EXPORT int c_HandleEffectAdlxControl(Regs *r) {return effects_bridge_entry(r,AUDIO_CONTROL);}
