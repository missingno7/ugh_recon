/* Ordinary one-event memory binding. Instruction/copy source is a fixed
 *13-byte read footprint; the complete native word/window still exists. */
#include "pair.inc"
uint8_t ugh_mem[UGH_MEM_SIZE];
static uint8_t source[65537],stack[1024];
static uint16_t table_words[14];
static AudioState reference;
static AudioScanWork *reference_work;
AudioVoice nondet_voice(void);AudioState nondet_audio(void);
uint16_t nondet_u16(void);uint32_t nondet_u32(void);uint8_t nondet_u8(void);
static uint16_t scanned_word(unsigned p)
{
    CHECK(p<20 && !(p&1u),"selected scanned word footprint");AudioVoice *v=&reference.scanned[0];
    if(p<12) return (uint16_t)(v->instrument[p]|(unsigned)v->instrument[p+1]*256u);
    return p==12 ? v->volume : p==14 ? v->gain : p==16 ? v->owner : v->frequency;
}
static uint16_t word_read(uint16_t bank,uint16_t offset)
{
    if(bank==SOUND_SEG) {
        if(offset==S(MainAdlxStartPointer)) return reference.channels[12].start.index;
        if(offset==S(MusicEventStreamLength)) return reference.channels[12].length;
        CHECK(offset>=S(ScannedAdlibVoiceStates) && offset<S(ScannedAdlibVoiceStates)+20,"scanned read identity");
        return scanned_word(offset-S(ScannedAdlibVoiceStates));
    }
    uint32_t p=lin(bank,offset);return (uint16_t)(ugh_read(p)|(unsigned)ugh_read(p+1)*256u);
}
static void word_write(uint16_t bank,uint16_t offset,uint16_t value)
{
    if(bank==SOUND_SEG) {
        CHECK(offset>=S(ScannedAdlibVoiceStates) && offset<S(ScannedAdlibVoiceStates)+20,"scanned store identity");
        unsigned p=offset-S(ScannedAdlibVoiceStates);AudioVoice *v=&reference.scanned[0];
        if(p==14) v->gain=value;else if(p==16) v->owner=value;else {CHECK(p==18,"word store footprint");v->frequency=value;}return;
    }
    uint32_t p=lin(bank,offset);ugh_write(p,(uint8_t)value);ugh_write(p+1,(uint8_t)(value>>8));
}
uint8_t ugh_read(uint32_t p)
{
    if(p>=0x60000 && p<=0x70000) return source[p-0x60000];
    unsigned table=(unsigned)UGH_SEG_C*16u+C(ScanMusicEvents)+0x2c8;
    if(p>=table && p<table+28) {unsigned q=p-table;return (uint8_t)(table_words[q/2]>>(8*(q&1u)));}
    unsigned sound=(unsigned)SOUND_SEG*16u;
    if(p>=sound+S(ScannedAdlibVoiceStates) && p<sound+S(ScannedAdlibVoiceStates)+20) {
        unsigned q=p-sound-S(ScannedAdlibVoiceStates);return (uint8_t)(scanned_word(q&65534u)>>(8*(q&1u)));
    }
    CHECK(p>=0x80000 && p<0x80400,"stack read footprint");return stack[p-0x80000];
}
void ugh_write(uint32_t p,uint8_t value)
{
    unsigned sound=(unsigned)SOUND_SEG*16u+S(ScannedAdlibVoiceStates);
    if(p>=sound && p<sound+12) {reference.scanned[0].instrument[p-sound]=value;return;}
    CHECK(p>=0x80000 && p<0x80400,"stack store footprint");stack[p-0x80000]=value;
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r)
{CHECK(bank==GAME_SEG && target==G(CopyFarBytes),"scan copy target");reference_work->copied=1;return c_CopyFarBytes(r);}
static void equal_mutable(const AudioState *a,const AudioState *b)
{
#if ARM == 1 || ARM == 2
    CHECK(a->scanned[0].frequency==b->scanned[0].frequency,"scan frequency/key result");
#elif ARM == 3
    CHECK(a->scanned[0].gain==b->scanned[0].gain,"zero-extended gain word");
#elif ARM == 4
    for(unsigned i=0;i<12;i++) CHECK(a->scanned[0].instrument[i]==b->scanned[0].instrument[i],"instrument extra working byte");
    CHECK(a->scanned[0].owner==b->scanned[0].owner,"scan owner12");
#else
    (void)a;(void)b;
#endif
}
static int within(uint8_t *p,void *field,unsigned n) {return p>=(uint8_t *)field && p<(uint8_t *)field+n;}
int main(void)
{
    uint8_t code=nondet_u8(),pass=(uint8_t)(nondet_u8()&1u);
#if ARM >= 1 && ARM <= 4
    if(!pass) code&=240u; /* normalized pass-0 destination0; pass1 admits all */
#endif
    for(unsigned i=0;i<13;i++) source[0x100+i]=nondet_u8();source[0x100]=code;
    for(unsigned i=0;i<14;i++) table_words[i]=0xa500;
    AudioScanDispatch table[7];for(unsigned i=0;i<7;i++) {table[i].value=0xa500;table[i].action=AUDIO_SCAN_BAD;}
#if ARM != 7
    const uint16_t offsets[7]={0x11d,0x155,0x17d,0x19d,0x1c2,0x209,0x20c};
    table_words[0]=code&240u;table_words[7]=ARM==8 ? 0xffff : (uint16_t)(C(ScanMusicEvents)+offsets[ARM]);
    table[0].value=code&240u;table[0].action=(AudioScanAction)ARM;
#endif
    reference=(AudioState){0};reference.channels[12].start.index=nondet_u16();reference.channels[12].length=nondet_u16();reference.scanned[0]=nondet_voice();
    AudioScanWork work={0};work.cursor.window=source;work.cursor.index=0x100;work.total=nondet_u32();work.threshold=nondet_u32();work.pass=pass;work.budget=nondet_u32();
    __CPROVER_assume(work.total<work.threshold && work.budget>0);
#if MODE == 0
    AudioState native=reference;AudioScanWork expected=work;reference_work=&expected;
    Regs r={0};r.cs=UGH_SEG_C;r.ss=0x8000;r.sp=0x200;r.flags=(uint16_t)(nondet_u16()&~DF);
    reference_step(&r,&expected);
    audio_section_scan_step(&native,&work,table);
    equal_mutable(&reference,&native);
    CHECK(work.exit==expected.exit && work.cursor.index==expected.cursor.index && work.total==expected.total && work.budget==expected.budget && work.copied==expected.copied,"actual C one-event control state");
#elif MODE == 1
    AudioState native=nondet_audio();unsigned i=nondet_u16();__CPROVER_assume(i<sizeof(native));uint8_t *p=(uint8_t *)&native+i,old=*p;
    if(!pass) {
#if ARM == 1 || ARM == 2
        __CPROVER_assume(!within(p,&native.scanned[0].frequency,2));
#elif ARM == 3
        __CPROVER_assume(!within(p,&native.scanned[0].gain,2));
#elif ARM == 4
        __CPROVER_assume(!within(p,native.scanned[0].instrument,12) && !within(p,&native.scanned[0].owner,2));
#endif
    }
    audio_section_scan_step(&native,&work,table);CHECK(*p==old,"all other step state bytes unchanged");
#else
    AudioState a=nondet_audio(),b=nondet_audio();b.channels[12].start.index=a.channels[12].start.index;b.channels[12].length=a.channels[12].length;
#if ARM == 1 || ARM == 2
    b.scanned[0].frequency=a.scanned[0].frequency;
#elif ARM == 3
    b.scanned[0].gain=a.scanned[0].gain;
#elif ARM == 4
    for(unsigned i=0;i<12;i++) b.scanned[0].instrument[i]=a.scanned[0].instrument[i];b.scanned[0].owner=a.scanned[0].owner;
#endif
    AudioScanWork second=work;audio_section_scan_step(&a,&work,table);audio_section_scan_step(&b,&second,table);equal_mutable(&a,&b);
    CHECK(work.exit==second.exit && work.cursor.index==second.cursor.index && work.total==second.total && work.copied==second.copied && work.budget==second.budget,"no omitted one-event input state");
#endif
    return 0;
}
