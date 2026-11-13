/* Relational capability contract for the already-accepted main voice step.
 * This checks the complete shared read footprint, operation and value arguments,
 * then gives both clients the same arbitrary allowed selected-voice result
 * and ordered event list. It is conditional B evidence, not a new proof of
 * the driver: the39 main profiles and real compiled effects traces own that.
 * Channel9 is rejected before this contract, preserving its separate stamp. */
static AudioState voice_input;
static AudioVoice voice_live_reply,voice_saved_reply;
static AudioMainResult voice_result;
static AudioMainOperation voice_operation;
static uint8_t voice_channel,voice_operands[12];
static unsigned native_voice_calls,reference_voice_calls;
#ifdef __CPROVER__
AudioVoice nondet_voice(void);
#endif

AudioMainResult audio_main_step(AudioState *state,AudioMainOperation operation,
    uint8_t code,const uint8_t bytes[12],AudioCursor *cursor)
{
    native_voice_calls++;voice_input=*state;voice_operation=operation;voice_channel=code;
    for(unsigned i=0;i<12;i++) voice_operands[i]=bytes[i];
    voice_live_reply=nondet_voice();voice_saved_reply=nondet_voice();
    voice_result=(AudioMainResult){0};voice_result.write_count=(uint16_t)(N16()%15u);
    for(unsigned i=0;i<14;i++) {voice_result.writes[i].reg=N8();voice_result.writes[i].value=N8();}
    voice_result.displaced=(uint8_t)(N8()&1u);
    voice_result.advance=(uint16_t)(operation==AUDIO_FREQUENCY ? 2 : operation==AUDIO_GAIN ? 1 : operation==AUDIO_INSTRUMENT ? 11 : 0);
    state->live[code]=voice_live_reply;state->displaced[code]=voice_saved_reply;
    cursor->index=(uint16_t)(cursor->index+voice_result.advance);return voice_result;
}
static int reference_voice(Regs *r,AudioMainOperation operation)
{
    uint8_t ch=(uint8_t)arg16(r,0);
    if(operation==AUDIO_INSTRUMENT && ch==9) return UGH_OK;
    CHECK(ch<9 && native_voice_calls==1,"valid shared voice call");reference_voice_calls++;
    CHECK(operation==voice_operation && ch==voice_channel,"voice operation and effective channel");
    if(operation==AUDIO_FREQUENCY) CHECK(arg16(r,2)==(uint16_t)(voice_operands[0]+(unsigned)voice_operands[1]*256u),"frequency argument");
    if(operation==AUDIO_GAIN) CHECK((uint8_t)arg16(r,2)==voice_operands[0],"gain argument byte");
    if(operation==AUDIO_INSTRUMENT) CHECK(arg16(r,2)==payload_index && arg16(r,4)==0x6000,"stable instrument resource");
    uint16_t reserved=reference_state.reserved_voices;
    if(operation==AUDIO_FREQUENCY || operation==AUDIO_KEY_OFF) reference_state.reserved_voices=0;
    /* These are the complete read footprint of the accepted voice cases;
     * track descriptors/clocks/fade/other voices are not driver inputs.
     * The contract's frame below preserves all unselected storage. */
    if(operation==AUDIO_INSTRUMENT) {
        CHECK(voice_input.live[ch].owner==reference_state.live[ch].owner,"pre-loader owner stamp lemma");
        reference_state.live[ch].owner=voice_input.live[ch].owner;
    }
    compare_voice(&voice_input.live[ch],&reference_state.live[ch]);
    compare_voice(&voice_input.displaced[ch],&reference_state.displaced[ch]);
    CHECK(voice_input.current_channel==reference_state.current_channel &&
        voice_input.reserved_voices==reference_state.reserved_voices &&
        voice_input.playing==reference_state.playing &&
        voice_input.operator_index[ch]==reference_state.operator_index[ch],"complete voice control inputs");
    reference_state.reserved_voices=reserved;
    reference_state.live[ch]=voice_live_reply;reference_state.displaced[ch]=voice_saved_reply;
    for(unsigned i=0;i<voice_result.write_count;i++) {
        platform_out(0x388,1,voice_result.writes[i].reg);platform_out(0x389,1,voice_result.writes[i].value);
    }
    return UGH_OK;
}
