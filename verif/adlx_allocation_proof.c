/* Ordinary typed word binding for actual C APIs, with arbitrary shared
 * service replies. This is not a byte/segment-alias or instruction IRQ proof. */
#include "pair.inc"
uint8_t ugh_mem[UGH_MEM_SIZE];
static AudioState state[2];
static uint16_t devices;
static unsigned phase;
typedef struct ProofStack {uint8_t bytes[256];} ProofStack;
static ProofStack stack_bytes[2];
static unsigned calls[2];
typedef struct Reply {uint16_t ax,bx,cx,dx,es,flags,control[4];} Reply;
typedef struct Call {uint16_t target,count,args[5];} Call;
static Reply replies[3];static Call observations[2][3];
AudioState nondet_audio(void);Reply nondet_reply(void);
uint16_t nondet_u16(void);uint8_t nondet_u8(void);
static uint16_t sound_word(uint16_t offset)
{
    if(offset==S(SoundDeviceBits)) return devices;
    if(offset==S(AdlxPlaybackGuard)) return state[phase].playback_guard;
    if(offset==S(ReservedAdlibChannelCount)) return state[phase].reserved_voices;
    if(offset==S(CurrentAdlxSlot)) return state[phase].current_channel;
    if(offset==S(AdlxTickCount)) return (uint16_t)state[phase].ticks;
    if(offset==S(AdlxTickCount)+2) return (uint16_t)(state[phase].ticks>>16);
    CHECK(offset>=S(AudioChannelStates) && offset<S(AudioChannelStates)+13*42,"channel read footprint");
    unsigned delta=offset-S(AudioChannelStates),index=delta/42,field=delta%42;
    AudioChannel *c=&state[phase].channels[index];
    switch(field) {
    case 0:return (uint16_t)c->age;case 2:return (uint16_t)(c->age>>16);
    case 6:return c->start.index;case 8:return (uint16_t)((c->start.window-ugh_mem)/16);
    case 16:return c->cursor.index;case 18:return (uint16_t)((c->cursor.window-ugh_mem)/16);
    case 28:return c->volume;case 34:return c->voice_count;case 36:return c->first_voice;case 40:return c->control;
    }
    CHECK(0,"channel word read set");return 0;
}
static void sound_store(uint16_t offset,uint16_t value)
{
    if(offset==S(AdlxPlaybackGuard)) {state[phase].playback_guard=value;return;}
    if(offset==S(ReservedAdlibChannelCount)) {state[phase].reserved_voices=value;return;}
    if(offset==S(CurrentAdlxSlot)) {state[phase].current_channel=value;return;}
    CHECK(offset>=S(AudioChannelStates) && offset<S(AudioChannelStates)+13*42,"channel store footprint");
    unsigned delta=offset-S(AudioChannelStates),index=delta/42,field=delta%42;
    AudioChannel *c=&state[phase].channels[index];
    switch(field) {
    case 16:c->cursor.index=value;return;case 18:c->cursor.window=ugh_mem+(uint32_t)value*16;return;
    case 28:c->volume=value;return;case 36:c->first_voice=value;return;case 40:c->control=value;return;
    }
    CHECK(0,"channel word store set");
}
uint8_t ugh_read(uint32_t address)
{
    uint32_t base=(uint32_t)SOUND_SEG*16;
    if(address>=base && address<base+65536u) {
        unsigned offset=address-base;return (uint8_t)(sound_word((uint16_t)(offset&65534u))>>(8*(offset&1u)));
    }
    CHECK(address>=0x70f80 && address<0x71080,"stack read footprint");return stack_bytes[phase].bytes[address-0x70f80];
}
void ugh_write(uint32_t address,uint8_t value)
{
    CHECK(address>=0x70f80 && address<0x71080,"stack byte store footprint");stack_bytes[phase].bytes[address-0x70f80]=value;
}
static uint16_t word_read(uint16_t bank,uint16_t offset)
{
    if(bank==SOUND_SEG) return sound_word(offset);
    uint32_t p=lin(bank,offset);return (uint16_t)(ugh_read(p)|(unsigned)ugh_read(p+1)*256u);
}
static void word_write(uint16_t bank,uint16_t offset,uint16_t value)
{
    if(bank==SOUND_SEG) {sound_store(offset,value);return;}
    uint32_t p=lin(bank,offset);ugh_write(p,(uint8_t)value);ugh_write(p+1,(uint8_t)(value>>8));
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r)
{
    CHECK(bank==UGH_SEG_C,"external service bank");
    unsigned n=calls[phase]++;CHECK(n<3,"service list capacity");
    Call *call=&observations[phase][n];call->target=target;
    call->count=target==UGH_O_C_LoadAdlibChannel ? 5 : target==UGH_O_C_StartAdlibTrackChannel ? 2 : 1;
    for(unsigned i=0;i<call->count;i++) call->args[i]=arg16(r,(uint16_t)(i*2));
#if PROFILE != 0
    CHECK(target==UGH_O_C_StopAdlibTrackChannel,"start stop capability");
    /* A loaded, inactive selected track makes this real stop a no-op. */
    CHECK((state[phase].channels[call->args[0]].control&1u)==0,"inactive start stop call");
    r->ax=SOUND_SEG;r->es=SOUND_SEG;
#else
    CHECK(target==UGH_O_C_StopAdlibTrackChannel || target==UGH_O_C_LoadAdlibChannel || target==UGH_O_C_StartAdlibTrackChannel,"complete external target set");
    Reply *reply=&replies[n];r->ax=reply->ax;r->bx=reply->bx;r->cx=reply->cx;r->dx=reply->dx;r->es=reply->es;r->flags=reply->flags;
    for(unsigned i=0;i<4;i++) state[phase].channels[8+i].control=reply->control[i];
#endif
    return 0;
}
static void audio_bridge_project(uint16_t bank,AudioState *dest)
{CHECK(bank==SOUND_SEG,"projection bank");*dest=state[phase];}
AudioMainResult audio_main_step(AudioState *s,AudioMainOperation o,uint8_t c,const uint8_t b[12],AudioCursor *p)
{
    (void)s;(void)o;(void)c;(void)b;(void)p;CHECK(0,"excluded voice domain");AudioMainResult result={0};return result;
}
/* COMPARE */
int main(void)
{
    state[0]=nondet_audio();devices=nondet_u16();
    for(unsigned i=0;i<13;i++) {
        state[0].channels[i].start.window=ugh_mem+(uint32_t)nondet_u16()*16u;
        state[0].channels[i].cursor.window=ugh_mem+(uint32_t)nondet_u16()*16u;
    }
    state[0].section_start.window=state[0].section_end.window=ugh_mem;
    uint16_t channel=nondet_u16(),volume=nondet_u16();
#if PROFILE == 1
    /* Complete stop-rejection domain, no guard or cursor mutation. */
    __CPROVER_assume(!(devices&1u) || channel<8 || channel>=12 || (state[0].channels[channel].control&5u)!=5u);
#elif PROFILE == 2
    /* Start rejection and capacity failure: all operand words arbitrary. */
    if((devices&1u) && channel>=8 && channel<=12 && (state[0].channels[channel].control&4u) && !(state[0].channels[channel].control&1u)) {
        __CPROVER_assume(channel<12);
        __CPROVER_assume((uint16_t)(state[0].reserved_voices+state[0].channels[channel].voice_count)>9);
    }
#elif PROFILE == 3
    channel=(uint16_t)(8+(channel&3u));
    state[0].channels[channel].voice_count=0;
    __CPROVER_assume(state[0].reserved_voices<=9);
    __CPROVER_assume(state[0].channels[channel].first_voice<=9-state[0].reserved_voices);
#endif
    state[1]=state[0];for(unsigned i=0;i<3;i++) replies[i]=nondet_reply();
    Regs left={0},right;left.ax=nondet_u16();left.bx=nondet_u16();left.cx=nondet_u16();left.dx=nondet_u16();
    left.si=nondet_u16();left.di=nondet_u16();left.ds=nondet_u16();left.es=nondet_u16();left.bp=nondet_u16();left.flags=nondet_u16();
    left.cs=UGH_SEG_C;left.ss=0x7000;left.sp=0x1000;right=left;
    phase=0;word_write(left.ss,0x1004,channel);word_write(left.ss,0x1006,volume);
    word_write(left.ss,0x1008,nondet_u16());word_write(left.ss,0x100a,nondet_u16());
    stack_bytes[1]=stack_bytes[0];
#if PROFILE == 0
    int a=reference_PlayAdlibEffect(&left);phase=1;int b=c_PlayAdlibEffect(&right);
#else
    int a=PROFILE==1 ? reference_StopAdlibTrackChannel(&left) : PROFILE==2 ? reference_StartAdlibTrackChannel(&left) : reference_RestoreAdlibVoiceAllocation(&left);
    phase=1;
    AudioAllocationOperation op=PROFILE==1 ? AUDIO_ALLOCATION_STOP : PROFILE==2 ? AUDIO_ALLOCATION_START : AUDIO_ALLOCATION_RESTORE;
    CHECK(audio_allocation_supported(&state[1],op,channel,devices),"native domain admission");
    AudioAllocationResult result=audio_allocation_run(&state[1],op,channel,volume,devices);int b=0;
    CHECK(result.action_count==0 && result.write_count==0,"no subordinate voice calls");
    if(PROFILE==2 && result.clamped) word_write(right.ss,0x1006,result.volume);
    if(PROFILE==2) CHECK(result.value==left.ax,"start failure return value");
#endif
    CHECK(a==b,"return status");compare_state(&state[0],&state[1]);
    unsigned probe=nondet_u8();__CPROVER_assume(probe>=128);
    CHECK(stack_bytes[0].bytes[probe]==stack_bytes[1].bytes[probe],"caller storage");
#if PROFILE == 0
    CHECK(calls[0]==calls[1],"service count");
    for(unsigned i=0;i<calls[0];i++) {
        CHECK(observations[0][i].target==observations[1][i].target && observations[0][i].count==observations[1][i].count,"service target/order/arity");
        for(unsigned j=0;j<observations[0][i].count;j++) CHECK(observations[0][i].args[j]==observations[1][i].args[j],"service argument values");
    }
    CHECK(left.ax==right.ax && left.bx==right.bx && left.cx==right.cx && left.dx==right.dx && left.flags==right.flags && left.es==right.es,"observable service outputs");
#endif
    return 0;
}
