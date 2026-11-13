/* Disjoint ordinary RAM; actual L1 handlers/drivers, maintained native and
 * bridge. Next fetch is cut. TIMER/STOP are observing capability contracts.
 * STOP additionally mutates a canary and volatile outputs: stale publication
 * after the external call must not erase them. Real C stop runs in DLL tests. */
#include "pair.inc"
uint8_t ugh_mem[UGH_MEM_SIZE];
typedef struct SoundRam {uint8_t bytes[1280];} SoundRam;
static SoundRam sound[2];
static SoundRam before_stop;
static uint8_t operators[9],auxiliary[10],operands[12],stack_bytes[128];
static uint16_t selected_record;
#ifdef __CPROVER__
SoundRam nondet_sound(void);
#endif
static unsigned phase;
static uint16_t payload_index,stop_reply[4];
static uint32_t io[2][28][3],io_count[2],timer[2][3],timer_count[2],stop_count[2],stop_slot[2];

uint8_t ugh_read(uint32_t address)
{
    uint32_t base=(uint32_t)SOUND_SEG*16u;
    if(address>=base && address<base+1280) return sound[phase].bytes[address-base];
    if(address>=base+S(CurrentAdlxRecordOffset) && address<base+S(CurrentAdlxRecordOffset)+2)
        return (uint8_t)(selected_record>>(8u*(address-base-S(CurrentAdlxRecordOffset))));
    if(address>=base+S(AdlibOperatorOffsets) && address<base+S(AdlibOperatorOffsets)+9)
        return operators[address-base-S(AdlibOperatorOffsets)];
    if(address>=base+S(AdlxPlaybackTimerHandle) && address<base+S(AdlxPlaybackTimerHandle)+10)
        return auxiliary[address-base-S(AdlxPlaybackTimerHandle)];
    if(address>=0x60000u && address<=0x70000u) {
        uint16_t index=(uint16_t)((uint16_t)(address-0x60000u)-payload_index);
        CHECK(index<12,"operand footprint");return operands[index];
    }
    CHECK(address>=0x70f80u && address<0x71000u,"stack read footprint");
    return stack_bytes[address-0x70f80u];
}
void ugh_write(uint32_t address,uint8_t value)
{
    uint32_t base=(uint32_t)SOUND_SEG*16u;
    if(address>=base && address<base+1280) {sound[phase].bytes[address-base]=value;return;}
    if(address>=base+S(CurrentAdlxRecordOffset) && address<base+S(CurrentAdlxRecordOffset)+2) {
        CHECK(value==(uint8_t)(selected_record>>(8u*(address-base-S(CurrentAdlxRecordOffset)))),"read-only selector binding");return;
    }
    CHECK(address>=0x70f80u && address<0x71000u,"stack write footprint");stack_bytes[address-0x70f80u]=value;
}
void platform_out(uint16_t port,unsigned size,uint32_t value)
{
    CHECK(io_count[phase]<28,"ordered write capacity");
    io[phase][io_count[phase]][0]=port;io[phase][io_count[phase]][1]=size;io[phase][io_count[phase]][2]=value;io_count[phase]++;
}
int ugh_dispatch(uint16_t segment,uint16_t offset,Regs *r)
{
    if(segment==SOUND_SEG) {
        if(offset==S(SetAdlibFrequency)) return c_SetAdlibFrequency(r);
        if(offset==S(KeyOffAdlibChannel)) return c_KeyOffAdlibChannel(r);
        if(offset==S(SetAdlibChannelGain)) return c_SetAdlibChannelGain(r);
        if(offset==S(SetAdlibChannelVolume)) return c_SetAdlibChannelVolume(r);
        if(offset==S(LoadAdlibInstrument)) return c_LoadAdlibInstrument(r);
    }
    if(segment==UGH_SEG_C && offset==UGH_O_C_StopAdlibTrackChannel) {
        stop_count[phase]++;stop_slot[phase]=arg16(r,0);
        before_stop=sound[phase];
        sound[phase].bytes[0]^=255u;
        r->ax=stop_reply[0];r->cx=stop_reply[1];r->dx=stop_reply[2];r->es=stop_reply[3];
        return UGH_OK;
    }
    CHECK(segment==TIMER_SEG && offset==T(SetTimerCallbackInterval),"complete external target set");
    timer_count[phase]++;timer[phase][0]=r->ax;timer[phase][1]=r->bx;timer[phase][2]=r->cx;
    return UGH_OK;
}
int c_RunMainAdlxEvents(Regs *r) {(void)r;return 0;}
int c_RunEffectAdlxEvents(Regs *r) {(void)r;return 0;}
int l1_HandleEffectAdlxLongWait(Regs *r) {(void)r;CHECK(0,"excluded fallback");return 1;}
int l1_HandleEffectAdlxShortWait(Regs *r) {(void)r;CHECK(0,"excluded fallback");return 1;}
int l1_HandleEffectAdlxFrequency(Regs *r) {(void)r;CHECK(0,"excluded fallback");return 1;}
int l1_HandleEffectAdlxKeyOff(Regs *r) {(void)r;CHECK(0,"excluded fallback");return 1;}
int l1_HandleEffectAdlxGain(Regs *r) {(void)r;CHECK(0,"excluded fallback");return 1;}
int l1_HandleEffectAdlxInstrument(Regs *r) {(void)r;CHECK(0,"excluded fallback");return 1;}
int l1_HandleEffectAdlxNoOp(Regs *r) {(void)r;CHECK(0,"excluded fallback");return 1;}
int l1_HandleEffectAdlxTimerPeriod(Regs *r) {(void)r;CHECK(0,"excluded fallback");return 1;}
int l1_HandleEffectAdlxControl(Regs *r) {(void)r;CHECK(0,"excluded fallback");return 1;}

#ifdef SEMANTIC
static void compare_voice(const AudioVoice *a,const AudioVoice *b)
{
    for(unsigned i=0;i<12;i++) CHECK(a->instrument[i]==b->instrument[i],"instrument bytes");
    CHECK(a->volume==b->volume && a->gain==b->gain && a->owner==b->owner && a->frequency==b->frequency,"voice future state");
}
static void compare_state(const AudioState *a,const AudioState *b)
{
    for(unsigned i=0;i<13;i++) {
        const AudioChannel *x=&a->channels[i],*y=&b->channels[i];
        CHECK(x->age==y->age && x->repeats==y->repeats,"channel age/repeat");
        CHECK(x->start.window==y->start.window && x->start.index==y->start.index,"start resource");
        CHECK(x->cursor.window==y->cursor.window && x->cursor.index==y->cursor.index,"event cursor");
        CHECK(x->length==y->length && x->sample_mode==y->sample_mode && x->sample_rate==y->sample_rate,"retained phase fields");
        CHECK(x->sample_half_length==y->sample_half_length && x->reserved_word==y->reserved_word && x->sample_selector==y->sample_selector && x->sample_accumulator==y->sample_accumulator,"opaque phase words");
        CHECK(x->volume==y->volume && x->deadline==y->deadline && x->voice_count==y->voice_count && x->first_voice==y->first_voice && x->step_q8==y->step_q8 && x->control==y->control,"channel future state");
    }
    for(unsigned i=0;i<9;i++) {
        compare_voice(&a->live[i],&b->live[i]);compare_voice(&a->displaced[i],&b->displaced[i]);compare_voice(&a->scanned[i],&b->scanned[i]);
        CHECK(a->operator_index[i]==b->operator_index[i],"operator mapping");
    }
    CHECK(a->playback_guard==b->playback_guard && a->ticks_per_unit==b->ticks_per_unit && a->playing==b->playing && a->section_loop_enabled==b->section_loop_enabled,"control words");
    CHECK(a->ticks==b->ticks && a->time_origin==b->time_origin && a->scanned_ticks==b->scanned_ticks,"clocks");
    CHECK(a->section_start.window==b->section_start.window && a->section_start.index==b->section_start.index && a->section_end.window==b->section_end.window && a->section_end.index==b->section_end.index,"section cursors");
    CHECK(a->fade.step_count==b->fade.step_count && a->fade.duration==b->fade.duration && a->fade.start_volume==b->fade.start_volume && a->fade.target_volume==b->fade.target_volume && a->fade.scheduled==b->fade.scheduled && a->fade.timer_handle==b->fade.timer_handle,"fade state");
    CHECK(a->timer_period==b->timer_period && a->playback_timer_handle==b->playback_timer_handle && a->reserved_voices==b->reserved_voices && a->current_channel==b->current_channel && a->track_volume==b->track_volume,"allocation/timer state");
}
#endif

static void one_case(void)
{
    initialize();
    Regs left={0},right;
    left.ax=N16();left.bx=N16();left.cx=N16();left.dx=N16();left.si=N16();left.di=N16();
    left.bp=N16();left.ds=N16();left.flags=N16();left.cs=SOUND_SEG;left.es=0x6000;
    left.ss=0x7000;left.sp=0x1000;payload_index=left.di;
    left.ax=OP<8 ? (uint16_t)((left.ax&0xff0fu)|OP*16) : (uint16_t)((left.ax&0xff7fu)|128);
    uint16_t selected=(uint16_t)(8+(N16()&3u));
#if RECORD >= 0
    selected=RECORD;
#endif
    uint16_t record=(uint16_t)(S(AudioChannelStates)+selected*42u);
    selected_record=record;
    for(phase=0;phase<2;phase++) {
        wr16(SOUND_SEG,S(CurrentAdlxRecordOffset),record);
#if CHANNEL >= 0 && CHANNEL < 10
        wr8(SOUND_SEG,(uint16_t)(record+0x24),(uint8_t)(CHANNEL-(left.ax&15u)));
#elif CHANNEL == 10
        uint8_t effective=(uint8_t)((left.ax&15u)+rd8(SOUND_SEG,(uint16_t)(record+0x24)));
#ifdef __CPROVER__
        __CPROVER_assume(effective>=10);
#else
        if(effective<10) wr8(SOUND_SEG,(uint16_t)(record+0x24),(uint8_t)(10-(left.ax&15u)));
#endif
#endif
    }
    right=left;
#ifdef SEMANTIC
    phase=1;AudioState native;audio_bridge_project(SOUND_SEG,&native);
    AudioCursor cursor=audio_bridge_cursor(left.es,left.di);
    AudioEffectsResult output=audio_effects_step(&native,&native.channels[selected],(AudioMainOperation)OP,(uint8_t)left.ax,operands,&cursor);
    phase=0;int expected=reference_event(&left);
    if(stop_count[0]) sound[0]=before_stop; /* Compare the native pre-call boundary. */
    AudioState after;audio_bridge_project(SOUND_SEG,&after);compare_state(&native,&after);
    CHECK(expected==(output.exit==AUDIO_EFFECTS_DIVIDE_FAULT ? UGH_UNSUPPORTED : UGH_OK),"semantic status");
    CHECK(left.di==cursor.index,"semantic consumption");
    phase=1;
    for(unsigned i=0;i<output.write_count;i++) {
        platform_out(0x388,1,output.writes[i].reg);platform_out(0x389,1,output.writes[i].value);
    }
    CHECK(timer_count[0]==output.timer_request,"semantic timer count");
    if(output.timer_request) CHECK(timer[0][0]==native.playback_timer_handle && timer[0][1]==output.requested_period && timer[0][2]==0,"semantic timer request");
    CHECK(stop_count[0]==output.stop_request,"semantic stop count");
    if(output.stop_request) CHECK(stop_slot[0]==native.current_channel,"semantic stop identity");
#else
    phase=0;int expected=reference_event(&left);
    phase=1;int got=effects_bridge_event(&right,(AudioMainOperation)OP);
    CHECK(expected==(got<0 ? 0 : got),"step status including divide fault");
    compare_memory();
    CHECK(left.ax==right.ax,"AX shell");CHECK(left.bx==right.bx,"BX shell");
    CHECK(left.cx==right.cx,"CX shell");CHECK(left.dx==right.dx,"DX shell");
    CHECK(left.si==right.si,"SI shell");CHECK(left.di==right.di,"cursor advance");
    CHECK(left.bp==right.bp && left.sp==right.sp,"stack including fault shell");
    CHECK(left.ds==right.ds && left.es==right.es && left.cs==right.cs && left.ss==right.ss,"segments");
    CHECK(left.flags==right.flags,"L1 flags shell");
    CHECK(io_count[0]==io_count[1],"ordered write count");
    for(unsigned i=0;i<28;i++) for(unsigned j=0;j<3;j++) CHECK(io[0][i][j]==io[1][i][j],"ordered OPL writes");
    CHECK(timer_count[0]==timer_count[1],"timer request count");
    for(unsigned i=0;i<3;i++) CHECK(timer[0][i]==timer[1][i],"timer request ABI");
    CHECK(stop_count[0]==stop_count[1],"stop request count");
    if(stop_count[0]) CHECK(stop_slot[0]==stop_slot[1],"raw stop identity");
#endif
#ifdef SEMANTIC
    CHECK(io_count[0]==io_count[1],"ordered write count");
    for(unsigned i=0;i<28;i++) for(unsigned j=0;j<3;j++) CHECK(io[0][i][j]==io[1][i][j],"ordered OPL writes");
#endif
}
int main(void)
{
#ifdef __CPROVER__
    one_case();
#else
    for(unsigned iteration=0;iteration<20000;iteration++) one_case();
#endif
    return 0;
}
