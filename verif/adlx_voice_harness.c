#include "pair.inc"
uint8_t ugh_mem[UGH_MEM_SIZE];
static uint8_t sound[2][65537],stack[2][8192],external[65537];
static unsigned phase,ports[2],reads[2];static uint32_t io[2][32][3],mmio[2][64][2];
static uint32_t random_seed=750193;
static uint16_t N16(void) {random_seed=random_seed*1664525u+1013904223u;return (uint16_t)(random_seed>>16);}
static uint8_t N8(void) {return (uint8_t)N16();}
uint8_t ugh_read(uint32_t address)
{
    unsigned b=(unsigned)SOUND_SEG*16u;
    if(address>=b && address<b+65537) return sound[phase][address-b];
    if(address>=0x60000 && address<=0x70000) return external[address-0x60000];
    if(address>=0xa0000 && address<0xc0000) {
        unsigned i=reads[phase]++;CHECK(i<64,"MMIO read bound");uint8_t value=(uint8_t)(address^(i*17u));mmio[phase][i][0]=address;mmio[phase][i][1]=value;return value;
    }
    CHECK(address>=0x80000 && address<0x82000,"stack read footprint");return stack[phase][address-0x80000];
}
void ugh_write(uint32_t address,uint8_t value)
{
    unsigned b=(unsigned)SOUND_SEG*16u;
    if(address>=b && address<b+65537) {sound[phase][address-b]=value;return;}
    CHECK(address>=0x80000 && address<0x82000,"stack write footprint");stack[phase][address-0x80000]=value;
}
void platform_out(uint16_t port,unsigned size,uint32_t value)
{unsigned i=ports[phase]++;CHECK(i<32,"port bound");io[phase][i][0]=port;io[phase][i][1]=size;io[phase][i][2]=value;}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r)
{
    CHECK(bank==SOUND_SEG && target==S(SetAdlibChannelVolume),"complete standalone peer set");
    return phase ? c_SetAdlibChannelVolume(r) : reference_SetAdlibChannelVolume(r);
}
static void one(unsigned operation)
{
    phase=0;for(unsigned i=0;i<65537;i++) {sound[0][i]=N8();external[i]=N8();}
    for(unsigned i=0;i<8192;i++) stack[0][i]=N8();
    const uint16_t channels[]={0,8,9,255,256,264,265,0xffff};uint16_t channel=channels[N16()%8];
    const uint16_t owners[]={0,8,12,13,0xffff};const uint16_t reserved[]={0,2,9,16,0x101,0x109,0xffff};
    wr16(SOUND_SEG,S(CurrentAdlxSlot),owners[N16()%5]);wr16(SOUND_SEG,S(MainAdlxPlaying),N16()%3);wr16(SOUND_SEG,S(ReservedAdlibChannelCount),reserved[N16()%7]);
    Regs a={0};a.cs=SOUND_SEG;a.ss=0x8000;a.sp=0x1000;a.ax=N16();a.bx=N16();a.cx=N16();a.dx=N16();a.si=N16();a.di=N16();a.bp=N16();a.ds=N16();a.es=N16();a.flags=N16();
    wr16(a.ss,0x1004,channel);wr16(a.ss,0x1006,N16());wr16(a.ss,0x1008,0x6000);
    if(operation==4) {
        unsigned kind=N16()%8;uint16_t bank=0x6000,offset=N16();
        if(kind<4) {bank=SOUND_SEG;offset=(uint16_t)((kind&1 ? S(SavedAdlibVoiceStates) : S(AdlibVoiceStates))+20u*(uint8_t)channel+(N16()%41)-20);if(kind&2) {bank--;offset=(uint16_t)(offset+16);}}
        else if(kind==4) {bank=0xa000;offset=N16();}
        else if(kind==5) {bank=0x8000;offset=0x1800;}
        wr16(a.ss,0x1006,offset);wr16(a.ss,0x1008,bank);
    }
    for(unsigned i=0;i<65537;i++) sound[1][i]=sound[0][i];
    for(unsigned i=0;i<8192;i++) stack[1][i]=stack[0][i];
    ports[0]=ports[1]=reads[0]=reads[1]=0;Regs b=a;
    int (*reference[7])(Regs *)={reference_SetAdlibChannelVolume,reference_SetAdlibChannelGain,reference_KeyOffAdlibChannel,reference_SetAdlibFrequency,reference_LoadAdlibInstrument,reference_WriteAdlibRegister,reference_DelaySoundIo};
    int (*native[7])(Regs *)={c_SetAdlibChannelVolume,c_SetAdlibChannelGain,c_KeyOffAdlibChannel,c_SetAdlibFrequency,c_LoadAdlibInstrument,c_WriteAdlibRegister,c_DelaySoundIo};
    CHECK(reference[operation](&a)==0,"literal return");phase=1;CHECK(native[operation](&b)==0,"native return");
    for(unsigned i=0;i<65537;i++) CHECK(sound[0][i]==sound[1][i],"full persistent SOUND RAM");
    for(unsigned i=0x1000;i<8192;i++) CHECK(stack[0][i]==stack[1][i],"caller stack");
    CHECK(a.ax==b.ax && a.bx==b.bx && a.cx==b.cx && a.dx==b.dx && a.si==b.si && a.di==b.di && a.bp==b.bp && a.sp==b.sp,"all GP");
    CHECK(a.ds==b.ds && a.es==b.es && a.flags==b.flags,"segments and all L1 flags");
    CHECK(ports[0]==ports[1] && reads[0]==reads[1],"effect counts");
    for(unsigned i=0;i<ports[0];i++) for(unsigned j=0;j<3;j++) CHECK(io[0][i][j]==io[1][i][j],"ordered register writes");
    for(unsigned i=0;i<reads[0];i++) for(unsigned j=0;j<2;j++) CHECK(mmio[0][i][j]==mmio[1][i][j],"ordered MMIO source reads");
}
int main(void)
{
#ifdef EXHAUSTIVE_DELAY
    for(unsigned factor=0;factor<256;factor++) for(unsigned calibration=0;calibration<256;calibration++) {
        phase=0;wr16(SOUND_SEG,S(SoundIoDelayMultiplier),(uint16_t)(0xab00|calibration));Regs r={0};r.cs=SOUND_SEG;r.ax=(uint16_t)(0x5a00|factor);r.flags=0x6d5;
        reference_DelaySoundIo(&r);AudioIoDelay delay=audio_voice_delay((uint8_t)factor,(uint8_t)calibration);
        CHECK(!!(r.flags&CF)==delay.overflow && !!(r.flags&OF)==delay.overflow,"exhaustive actual MUL flags");
        CHECK(reference_iterations==delay.iterations,"exhaustive actual finite LOOP count");
    }
    puts("PASS65536 byte-pair delay outputs/iteration counts");
#else
    for(unsigned operation=0;operation<7;operation++) {for(unsigned i=0;i<10000;i++) one(operation);printf("operation%u PASS10000\n",operation);}
#endif
    return 0;
}
