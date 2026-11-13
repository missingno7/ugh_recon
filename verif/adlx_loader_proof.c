/* Actual parser C over an ordinary resource window and aligned SOUND word
 * binding. Output/frame/dependence are independent properties. */
#include "pair.inc"
uint8_t ugh_mem[UGH_MEM_SIZE];
typedef struct Resource {uint8_t bytes[65537];} Resource;
typedef struct ProofStack {uint8_t bytes[256];} ProofStack;
Resource nondet_resource(void);AudioState nondet_audio(void);
uint16_t nondet_u16(void);uint8_t nondet_u8(void);
static Resource resource;
static ProofStack stack;
static AudioState reference;
static AudioCursor map;
static uint16_t devices;
static unsigned swap_count;

static uint16_t window_id(AudioCursor c) {return c.window==resource.bytes ? 0x6000 : 0;}
static uint16_t sound_word(uint16_t offset)
{
    if(offset==S(SoundDeviceBits)) return devices;
    if(offset==S(ReservedAdlibChannelCount)) return reference.reserved_voices;
    if(offset==S(MusicTicksPerUnit)) return reference.ticks_per_unit;
    if(offset==S(AdlibInstrumentMap)) return map.index;
    if(offset==S(AdlibInstrumentMap)+2) return window_id(map);
    CHECK(offset>=S(AudioChannelStates)+SLOT*42 && offset<S(AudioChannelStates)+(SLOT+1)*42,"selected word read footprint");
    AudioChannel *c=&reference.channels[SLOT];unsigned f=offset-S(AudioChannelStates)-SLOT*42;
    switch(f) {
    case 4:return c->repeats;case 6:return c->start.index;case 8:return window_id(c->start);
    case 10:return c->length;case 16:return c->cursor.index;case 18:return window_id(c->cursor);
    case 34:return c->voice_count;case 38:return c->step_q8;case 40:return c->control;
    }
    CHECK(0,"channel read set");return 0;
}
static void sound_store(uint16_t offset,uint16_t value)
{
    if(offset==S(MusicTicksPerUnit)) {reference.ticks_per_unit=value;return;}
    if(offset==S(AdlibInstrumentMap)) {map.index=value;return;}
    if(offset==S(AdlibInstrumentMap)+2) {map.window=value==0x6000 ? resource.bytes : ugh_mem;return;}
    CHECK(offset>=S(AudioChannelStates)+SLOT*42 && offset<S(AudioChannelStates)+(SLOT+1)*42,"selected word store footprint");
    AudioChannel *c=&reference.channels[SLOT];unsigned f=offset-S(AudioChannelStates)-SLOT*42;
    switch(f) {
    case 4:c->repeats=value;return;case 6:c->start.index=value;return;
    case 8:c->start.window=value==0x6000 ? resource.bytes : ugh_mem;return;
    case 10:c->length=value;return;case 16:c->cursor.index=value;return;
    case 18:c->cursor.window=value==0x6000 ? resource.bytes : ugh_mem;return;
    case 34:c->voice_count=value;return;case 38:c->step_q8=value;return;case 40:c->control=value;return;
    }
    CHECK(0,"channel store set");
}
uint8_t ugh_read(uint32_t address)
{
    if(address>=0x60000 && address<=0x70000) return resource.bytes[address-0x60000];
    CHECK(address>=0x70f80 && address<0x71080,"stack read footprint");return stack.bytes[address-0x70f80];
}
void ugh_write(uint32_t address,uint8_t value)
{
    CHECK(address>=0x70f80 && address<0x71080,"stack write footprint");stack.bytes[address-0x70f80]=value;
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
    CHECK(bank==UGH_SEG_C && target==UGH_O_C_SwapDwordByteOrder,"complete parser callee set");
    swap_count++;return c_SwapDwordByteOrder(r);
}
static void equal_outputs(const AudioState *a,const AudioState *b)
{
    const AudioChannel *x=&a->channels[SLOT],*y=&b->channels[SLOT];
    CHECK(x->repeats==y->repeats && x->length==y->length && x->voice_count==y->voice_count && x->step_q8==y->step_q8 && x->control==y->control,"loaded scalar outputs");
    CHECK(x->start.window==y->start.window && x->start.index==y->start.index && x->cursor.window==y->cursor.window && x->cursor.index==y->cursor.index,"loaded resource cursors");
    CHECK(a->ticks_per_unit==b->ticks_per_unit,"main tick rate");
}
static int within(uint8_t *probe,void *field,unsigned length)
{return probe>=(uint8_t *)field && probe<(uint8_t *)field+length;}
int main(void)
{
    resource=nondet_resource();devices=nondet_u16();
    uint16_t channel=SLOT,repeats=nondet_u16(),index=nondet_u16();
    reference=(AudioState){0};reference.reserved_voices=nondet_u16();reference.ticks_per_unit=nondet_u16();
    reference.channels[SLOT].repeats=nondet_u16();reference.channels[SLOT].length=nondet_u16();
    reference.channels[SLOT].voice_count=nondet_u16();reference.channels[SLOT].step_q8=nondet_u16();reference.channels[SLOT].control=nondet_u16();
    reference.channels[SLOT].start.window=ugh_mem;reference.channels[SLOT].start.index=nondet_u16();
    reference.channels[SLOT].cursor.window=ugh_mem;reference.channels[SLOT].cursor.index=nondet_u16();
    map.window=ugh_mem;map.index=nondet_u16();
    AudioCursor input={resource.bytes,index};
#if MODE == 3
    channel=nondet_u16();__CPROVER_assume(!(devices&1u) || channel<8 || channel>12);
#endif
#if MODE == 0 || MODE == 3
    AudioState native=reference;AudioCursor new_map=map;
    Regs r={0};r.cs=UGH_SEG_C;r.ss=0x7000;r.sp=0x1000;r.dx=nondet_u16();uint16_t old_dx=r.dx;
    word_write(r.ss,0x1004,channel);word_write(r.ss,0x1006,index);word_write(r.ss,0x1008,0x6000);word_write(r.ss,0x100a,repeats);
    int status=c_LoadAdlibTrackData(&r);
    AudioAdlxLoadResult result=audio_adlx_load(&native,channel,&input,repeats,devices);
    if(result.main_map) new_map=result.instrument_map;
    CHECK(status==0 && r.ax==result.value,"parser result");
    CHECK(input.index==word_read(r.ss,0x1006),"partial input cursor mutation");
    CHECK(swap_count==result.swaps && r.dx==(result.swaps ? result.swap_high : old_dx),"byte-swap observations");
    CHECK(r.es==(result.stage>=AUDIO_ADLX_ROOT_TAG && result.stage<=AUDIO_ADLX_TRACK_TAG ? 0x6000 : SOUND_SEG),"parser segment output");
    equal_outputs(&reference,&native);
    CHECK(new_map.window==map.window && new_map.index==map.index,"byte-exact instrument map setup");
#elif MODE == 1
    AudioState native=nondet_audio();
    unsigned probe_index=nondet_u16();__CPROVER_assume(probe_index<sizeof(native));
    uint8_t *probe=(uint8_t *)&native+probe_index;uint8_t before=*probe;
    AudioChannel *c=&native.channels[SLOT];
    __CPROVER_assume(!within(probe,&c->length,sizeof(c->length)) && !within(probe,&c->voice_count,sizeof(c->voice_count)) && !within(probe,&c->step_q8,sizeof(c->step_q8)) && !within(probe,&c->control,sizeof(c->control)) && !within(probe,&c->start,sizeof(c->start)) && !within(probe,&c->cursor,sizeof(c->cursor)));
    if(repeats) __CPROVER_assume(!within(probe,&c->repeats,sizeof(c->repeats)));
    if(SLOT==12) __CPROVER_assume(!within(probe,&native.ticks_per_unit,sizeof(native.ticks_per_unit)));
    audio_adlx_load(&native,channel,&input,repeats,devices);
    CHECK(*probe==before,"every non-output native byte unchanged");
#elif MODE == 2
    AudioState a=nondet_audio(),b=nondet_audio();
    b.reserved_voices=a.reserved_voices;b.ticks_per_unit=a.ticks_per_unit;
    b.channels[SLOT].repeats=a.channels[SLOT].repeats;b.channels[SLOT].length=a.channels[SLOT].length;
    b.channels[SLOT].voice_count=a.channels[SLOT].voice_count;b.channels[SLOT].step_q8=a.channels[SLOT].step_q8;
    b.channels[SLOT].control=a.channels[SLOT].control;b.channels[SLOT].start=a.channels[SLOT].start;b.channels[SLOT].cursor=a.channels[SLOT].cursor;
    AudioCursor second=input;
    AudioAdlxLoadResult x=audio_adlx_load(&a,channel,&input,repeats,devices),y=audio_adlx_load(&b,channel,&second,repeats,devices);
    equal_outputs(&a,&b);
    CHECK(input.index==second.index && x.value==y.value && x.stage==y.stage && x.main_map==y.main_map && x.swaps==y.swaps && x.swap_high==y.swap_high,"remaining state irrelevant to loader outputs");
    CHECK(x.instrument_map.window==y.instrument_map.window && x.instrument_map.index==y.instrument_map.index,"map dependence");
#endif
    return 0;
}
