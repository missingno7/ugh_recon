#include "adlx_sections.h"

AudioScanAction audio_section_classify(const AudioScanDispatch table[7],uint8_t code)
{
    for(unsigned i=0;i<7;i++) if(table[i].value==(code&240u)) return table[i].action;
    return AUDIO_SCAN_DEFAULT;
}
static uint16_t audio_section_word(AudioCursor cursor)
{return (uint16_t)(cursor.window[cursor.index]+(unsigned)cursor.window[(unsigned)cursor.index+1]*256u);}
static void audio_section_scan_finish(AudioState *state,AudioScanWork *work)
{
    if(work->pass==0) state->section_start=work->cursor;else state->section_end=work->cursor;
    state->scanned_ticks=work->total-state->scanned_ticks;
    work->pass++;
    if(work->pass==2) {state->section_loop_enabled=1;work->exit=AUDIO_SCAN_DONE;return;}
    work->threshold=(uint32_t)work->next_units*state->ticks_per_unit;
    state->scanned_ticks=work->total;
}
AudioScanWork audio_section_scan_begin(AudioState *state,uint16_t first,uint16_t second,uint16_t devices)
{
    AudioScanWork work={0};work.exit=AUDIO_SCAN_END;
    if(!(devices&1u) || !state->playing) return work;
    if(state->channels[12].voice_count>9) {work.exit=AUDIO_SCAN_BOUNDARY;return work;}
    work.entered=1;work.exit=AUDIO_SCAN_MORE;work.cursor=state->channels[12].start;
    work.threshold=(uint32_t)first*state->ticks_per_unit;work.next_units=second;work.budget=5000000;
    for(unsigned i=0;i<9;i++) {AudioVoice zero={0};state->scanned[i]=zero;}
    for(unsigned i=0;i<state->channels[12].voice_count;i++) state->scanned[i].volume=state->track_volume;
    state->scanned_ticks=0;return work;
}
AudioScanExit audio_section_scan_step(AudioState *state,AudioScanWork *work,const AudioScanDispatch table[7])
{
    if(work->exit!=AUDIO_SCAN_MORE) return work->exit;
    if(work->total>=work->threshold) {audio_section_scan_finish(state,work);return work->exit;}
    if(!work->budget) {work->exit=AUDIO_SCAN_BUDGET;return work->exit;}
    work->budget--;
    uint8_t code=work->cursor.window[work->cursor.index];work->cursor.index=(uint16_t)(work->cursor.index+1);
    uint16_t end=(uint16_t)(state->channels[12].start.index+state->channels[12].length);
    /* Retained post-fetch OFFSET-only test, before inspecting any payload. */
    if(work->cursor.index>=end) {work->exit=AUDIO_SCAN_END;return work->exit;}
    AudioScanAction action=audio_section_classify(table,code);unsigned channel=code&15u;
    if(!work->pass && channel>=9 && action>=AUDIO_SCAN_FREQUENCY && action<=AUDIO_SCAN_INSTRUMENT) {
        work->exit=AUDIO_SCAN_BOUNDARY;return work->exit;
    }
    switch(action) {
    case AUDIO_SCAN_LONG:
        /* The ENTIRE opcode participates, with no16-bit truncation. A
         * modified table can classify a nonzero high nibble as long wait. */
        work->total+=(((uint32_t)code<<8)+work->cursor.window[work->cursor.index])<<7;
        work->cursor.index=(uint16_t)(work->cursor.index+1);break;
    case AUDIO_SCAN_FREQUENCY:
        if(!work->pass) state->scanned[channel].frequency=audio_section_word(work->cursor);
        work->cursor.index=(uint16_t)(work->cursor.index+2);break;
    case AUDIO_SCAN_KEY_OFF:if(!work->pass) state->scanned[channel].frequency&=57343u;break;
    case AUDIO_SCAN_GAIN:
        if(!work->pass) state->scanned[channel].gain=work->cursor.window[work->cursor.index];
        work->cursor.index=(uint16_t)(work->cursor.index+1);break;
    case AUDIO_SCAN_INSTRUMENT:
        if(!work->pass) {
            for(unsigned i=0;i<12;i++) state->scanned[channel].instrument[i]=work->cursor.window[(uint16_t)(work->cursor.index+i)];
            state->scanned[channel].owner=12;work->copied=1;
        }
        work->cursor.index=(uint16_t)(work->cursor.index+11);break;
    case AUDIO_SCAN_TIMER:work->cursor.index=(uint16_t)(work->cursor.index+2);break;
    case AUDIO_SCAN_EXTENSION:work->cursor.index=(uint16_t)(work->cursor.index+work->cursor.window[work->cursor.index]+1);break;
    case AUDIO_SCAN_DEFAULT:work->total+=code&127u;break;
    case AUDIO_SCAN_BAD:work->exit=AUDIO_SCAN_CALLBACK;break;
    }
    return work->exit;
}
AudioScanWork audio_section_scan(AudioState *state,uint16_t first,uint16_t second,uint16_t devices,const AudioScanDispatch table[7])
{
    AudioScanWork work=audio_section_scan_begin(state,first,second,devices);
    while(work.exit==AUDIO_SCAN_MORE) audio_section_scan_step(state,&work,table);
    return work;
}
static AudioSectionAction *audio_section_action(AudioState *state,AudioSectionApply *result,AudioSectionActionKind kind,unsigned channel)
{
    AudioSectionAction *action=&result->actions[result->action_count++];action->kind=kind;action->channel=(uint16_t)channel;
    action->current_channel=state->current_channel;action->first_reserved=(uint8_t)(9-(uint8_t)state->reserved_voices);return action;
}
static void audio_section_voice(AudioState *state,AudioSectionApply *result,AudioSectionActionKind kind,unsigned channel)
{
    AudioSectionAction *action=audio_section_action(state,result,kind,channel);
    uint8_t bytes[12];for(unsigned i=0;i<12;i++) bytes[i]=state->live[channel].instrument[i];
    uint16_t reserved=state->reserved_voices;
    AudioMainOperation operation=kind==AUDIO_SECTION_INSTRUMENT ? AUDIO_INSTRUMENT : AUDIO_FREQUENCY;
    if(operation==AUDIO_FREQUENCY) {
        uint16_t frequency=state->live[channel].frequency;bytes[0]=(uint8_t)frequency;bytes[1]=(uint8_t)(frequency>>8);state->reserved_voices=0;
    }
    AudioCursor cursor={0};AudioMainResult voice=audio_main_step(state,operation,(uint8_t)channel,bytes,&cursor);
    state->reserved_voices=reserved;action->write_count=voice.write_count;action->displaced=voice.displaced;
    for(unsigned i=0;i<voice.write_count;i++) result->writes[result->write_count++]=voice.writes[i];
}
static uint8_t audio_section_level(uint8_t level,uint8_t gain,uint8_t volume)
{unsigned scaled=(((63u-(level&63u))*gain)>>8)*volume;return (uint8_t)((63u-(scaled>>8))|(level&192u));}
static void audio_section_volume(AudioState *state,AudioSectionApply *result,unsigned channel)
{
    AudioSectionAction *action=audio_section_action(state,result,AUDIO_SECTION_VOLUME,channel);
    /* Retained: the argument is read from LIVE after either copy/driver path. */
    uint8_t volume=(uint8_t)state->live[channel].volume;
    if((state->playing&1u) && state->current_channel>=12 && (state->reserved_voices&15u) && channel>=action->first_reserved) {
        state->displaced[channel].volume=(uint16_t)((state->displaced[channel].volume&65280u)|volume);action->displaced=1;return;
    }
    AudioVoice *voice=&state->live[channel];voice->volume=(uint16_t)((voice->volume&65280u)|volume);
    uint8_t op=state->operator_index[channel];
    AudioRegisterWrite carrier={(uint8_t)(op+67),audio_section_level(voice->instrument[6],(uint8_t)voice->gain,volume)};
    result->writes[result->write_count++]=carrier;action->write_count++;
    if(voice->instrument[10]&1u) {
        AudioRegisterWrite modulator={(uint8_t)(op+64),audio_section_level(voice->instrument[1],(uint8_t)voice->gain,volume)};
        result->writes[result->write_count++]=modulator;action->write_count++;
    }
}
AudioSectionApply audio_section_apply(AudioState *state,uint16_t devices)
{
    AudioSectionApply result={0};
    if(!(devices&1u)) return result;
    state->channels[12].cursor=state->section_start;state->time_origin+=state->scanned_ticks;
    for(unsigned i=0;i<state->channels[12].voice_count;i++) {
        audio_section_action(state,&result,AUDIO_SECTION_COPY,i);
        if(i<(uint16_t)(9-state->reserved_voices)) {
            state->live[i]=state->scanned[i];
            audio_section_voice(state,&result,AUDIO_SECTION_INSTRUMENT,i);
            audio_section_voice(state,&result,AUDIO_SECTION_FREQUENCY,i);
        } else state->displaced[i]=state->scanned[i];
        audio_section_volume(state,&result,i);
    }
    return result;
}
int audio_section_tick_begin(AudioState *state)
{state->ticks++;if(state->playback_guard&1u) return 0;state->playback_guard=1;return 1;}
int audio_section_main_due(const AudioState *state)
{return (state->playing&1u) && state->ticks>=state->channels[12].deadline;}
int audio_section_apply_due(const AudioState *state)
{return (state->section_loop_enabled&1u) && state->channels[12].cursor.index>=state->section_end.index;}
int audio_section_effect_due(const AudioState *state,unsigned index)
{return (state->channels[index].control&5u)==5u && state->ticks>=state->channels[index].deadline;}
void audio_section_main_context(AudioState *state) {state->current_channel=AUDIO_MAIN_CHANNEL;}
void audio_section_effects_begin(AudioState *state) {state->current_channel=AUDIO_FIRST_EFFECT_CHANNEL;}
void audio_section_effect_next(AudioState *state)
{
    /* Retained: callbacks can leave12 (or another raw owner). Increment that
     * word; the independent effect-record iterator does not replace it. */
    state->current_channel=(uint16_t)(state->current_channel+1u);
}
void audio_section_tick_end(AudioState *state) {state->playback_guard=0;}
