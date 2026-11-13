#include "pair.inc"
uint8_t ugh_mem[UGH_MEM_SIZE];
static uint8_t sound[2][65537],stack[2][8192];
static uint16_t table_words[14],reply[16];
static unsigned phase,io_count[2],callback_count[2];
static uint32_t io[2][1024][3];static uint16_t callbacks[2][8][6];
uint8_t ugh_read(uint32_t address)
{
    unsigned b=(unsigned)SOUND_SEG*16u;
    if(address>=b && address<b+65537) return sound[phase][address-b];
    if(address>=0x60000 && address<=0x70000) return ugh_mem[address];
    CHECK(address>=0x80000 && address<0x82000,"read footprint");return stack[phase][address-0x80000];
}
void ugh_write(uint32_t address,uint8_t value)
{
    unsigned b=(unsigned)SOUND_SEG*16u;
    if(address>=b && address<b+65537) {sound[phase][address-b]=value;return;}
    CHECK(address>=0x80000 && address<0x82000,"write footprint");stack[phase][address-0x80000]=value;
}
void platform_out(uint16_t port,unsigned size,uint32_t value)
{
    unsigned n=io_count[phase]++;CHECK(n<1024,"port capacity");io[phase][n][0]=port;io[phase][n][1]=size;io[phase][n][2]=value;
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r)
{
    uint16_t saved=r->cs;r->cs=bank;int status=UGH_UNSUPPORTED;
    if(bank==GAME_SEG && target==G(CopyFarBytes)) status=c_CopyFarBytes(r);
    else if(bank==UGH_SEG_C && target==C(ApplyScannedMusicEvents)) status=phase ? c_ApplyScannedMusicEvents(r) : reference_ApplyScannedMusicEvents(r);
    else if(bank==SOUND_SEG) {
        if(target==S(LoadAdlibInstrument)) status=c_LoadAdlibInstrument(r);
        else if(target==S(SetAdlibFrequency)) status=c_SetAdlibFrequency(r);
        else if(target==S(SetAdlibChannelVolume)) status=c_SetAdlibChannelVolume(r);
        else {
            CHECK(target==S(RunMainAdlxEvents) || target==S(RunEffectAdlxEvents),"complete callback targets");
            unsigned n=callback_count[phase]++;CHECK(n<8,"callback count");uint16_t *log=callbacks[phase][n];
            log[0]=target;log[1]=rd16(SOUND_SEG,S(CurrentAdlxSlot));log[2]=rd16(SOUND_SEG,S(CurrentAdlxRecordOffset));log[3]=r->es;log[4]=r->di;log[5]=rd16(SOUND_SEG,S(AdlxPlaybackGuard));
            r->ax=reply[0];r->bx=reply[1];r->cx=reply[2];r->dx=reply[3];r->si=reply[4];r->di=reply[5];r->es=reply[6];r->ds=reply[7];r->flags=reply[8];
            wr16(SOUND_SEG,S(CurrentAdlxSlot),reply[9]);wr16(SOUND_SEG,S(AdlxTickCount),reply[10]);wr16(SOUND_SEG,S(AdlxTickHighWord),reply[11]);
            wr16(SOUND_SEG,S(ReservedAdlibChannelCount),reply[12]);
            status=(reply[13]&15u)==0 ? UGH_BUDGET : UGH_OK;
        }
    }
    CHECK(status==UGH_OK || status==UGH_BUDGET,"complete callee set");r->cs=saved;return status;
}
static void one_case(unsigned operation)
{
    phase=0;for(unsigned i=0;i<65537;i++) {sound[0][i]=N8();ugh_mem[0x60000+i]=N8();}
    const uint16_t values[7]={0,0x10,0x20,0x30,0x40,0x60,0x70},targets[7]={0x11d,0x155,0x17d,0x19d,0x1c2,0x209,0x20c};
    for(unsigned i=0;i<7;i++) {table_words[i]=values[i];table_words[7+i]=(uint16_t)(C(ScanMusicEvents)+targets[i]);}
    if(N16()%4==0) table_words[N16()%14]=N16();
    for(unsigned i=0;i<16;i++) reply[i]=N16();
    uint16_t count=(uint16_t)(N16()%10);
    wr16(SOUND_SEG,S(MusicVoiceCount),count);wr16(SOUND_SEG,S(MainAdlxStartPointer),0x100);wr16(SOUND_SEG,S(MainAdlxStartPointer)+2,0x6000);
    wr16(SOUND_SEG,S(MusicEventStreamLength),128);wr16(SOUND_SEG,S(SoundDeviceBits),(uint16_t)(N16()|1u));
    wr16(SOUND_SEG,S(MainAdlxPlaying),(uint16_t)(N16()%3));wr16(SOUND_SEG,S(MusicTicksPerUnit),1);
    wr16(SOUND_SEG,S(FirstScannedEvent),0x100);wr16(SOUND_SEG,S(FirstScannedEvent)+2,0x6000);
    wr16(SOUND_SEG,S(AdlxPlaybackGuard),(uint16_t)(N16()%4));
    if(operation==2) {
        wr16(SOUND_SEG,S(MainAdlxDeadlineHigh),(uint16_t)(N16()%2));wr16(SOUND_SEG,S(AdlxTickHighWord),1);
        wr16(SOUND_SEG,S(MainAdlxCursor),0x101);wr16(SOUND_SEG,S(MainAdlxCursorSegment),0x6000);
        wr16(SOUND_SEG,S(MainAdlxSectionEnd),0x100);wr16(SOUND_SEG,S(MainAdlxSectionLoopEnabled),(uint16_t)(N16()%3));
        wr16(SOUND_SEG,S(ReservedAdlibChannelCount),(uint16_t)(N16()%10));
        for(unsigned i=8;i<12;i++) wr16(SOUND_SEG,(uint16_t)(S(AudioChannelStates)+i*42+40),N16()%2 ? 5 : 0);
    }
    Regs left={0},right;left.cs=operation==2 ? SOUND_SEG : UGH_SEG_C;left.ss=0x8000;left.sp=0x1000;
    left.ax=N16();left.bx=N16();left.cx=N16();left.dx=N16();left.si=N16();left.di=N16();left.bp=N16();left.ds=N16();left.es=N16();left.flags=N16();
    wr16(left.ss,0x1004,(uint16_t)(N16()%100));wr16(left.ss,0x1006,(uint16_t)(N16()%100));
#ifdef BUDGET_PROFILE
    CHECK(operation==0,"budget scan only");
    for(unsigned i=0;i<65537;i++) ugh_mem[0x60000+i]=0x40;
    for(unsigned i=0;i<7;i++) {table_words[i]=values[i];table_words[7+i]=(uint16_t)(C(ScanMusicEvents)+targets[i]);}
    wr16(SOUND_SEG,S(MainAdlxPlaying),1);wr16(SOUND_SEG,S(MusicVoiceCount),9);wr16(SOUND_SEG,S(MusicTicksPerUnit),1);
    wr16(SOUND_SEG,S(MusicEventStreamLength),0xfeff);wr16(left.ss,0x1004,1);wr16(left.ss,0x1006,2);
#endif
#ifdef WRAP_PROFILE
    CHECK(operation==0,"wrap scan only");
    for(unsigned i=0;i<7;i++) {table_words[i]=values[i];table_words[7+i]=(uint16_t)(C(ScanMusicEvents)+targets[i]);}
    for(unsigned i=0;i<65537;i++) ugh_mem[0x60000+i]=0x20;
    ugh_mem[0x6fffc]=0x40;
    for(unsigned i=0;i<11;i++) ugh_mem[0x60000+(uint16_t)(0xfffd+i)]=(uint8_t)(i+1);
    ugh_mem[0x60008]=0x81;
    wr16(SOUND_SEG,S(MainAdlxPlaying),1);wr16(SOUND_SEG,S(MusicVoiceCount),9);wr16(SOUND_SEG,S(MusicTicksPerUnit),1);
    wr16(SOUND_SEG,S(MusicEventStreamLength),0xfeff);wr16(left.ss,0x1004,1);wr16(left.ss,0x1006,1);
#endif
#ifdef CLOCK_PROFILE
    CHECK(operation==0,"clock scan only");
    for(unsigned i=0;i<7;i++) {table_words[i]=values[i];table_words[7+i]=(uint16_t)(C(ScanMusicEvents)+targets[i]);}
    ugh_mem[0x60100]=0x0f;ugh_mem[0x60101]=0xff;ugh_mem[0x60102]=0x81;ugh_mem[0x60103]=0xff;
    wr16(SOUND_SEG,S(MainAdlxPlaying),1);wr16(SOUND_SEG,S(MusicVoiceCount),9);wr16(SOUND_SEG,S(MusicTicksPerUnit),1);
    wr16(left.ss,0x1004,1);wr16(left.ss,0x1006,65535);
#endif
    /* The full SOUND window physically includes the following C code/table.
     * Populate that alias, rather than shadowing it with a separate read map. */
    unsigned table_alias=(unsigned)(UGH_SEG_C-SOUND_SEG)*16u+C(ScanMusicEvents)+0x2c8;
    CHECK(table_alias+28<65537,"table lies in broad SOUND window");
    for(unsigned i=0;i<14;i++) {sound[0][table_alias+2*i]=(uint8_t)table_words[i];sound[0][table_alias+2*i+1]=(uint8_t)(table_words[i]>>8);}
    for(unsigned i=0;i<65537;i++) sound[1][i]=sound[0][i];
    for(unsigned i=0;i<8192;i++) stack[1][i]=stack[0][i];
    io_count[0]=io_count[1]=callback_count[0]=callback_count[1]=0;right=left;
    int a=operation==0 ? reference_ScanMusicEvents(&left) : operation==1 ? reference_ApplyScannedMusicEvents(&left) : reference_TickAdlxPlayback(&left);
    phase=1;int b=operation==0 ? c_ScanMusicEvents(&right) : operation==1 ? c_ApplyScannedMusicEvents(&right) : c_TickAdlxPlayback(&right);
    CHECK(a==b,"status");
#ifdef BUDGET_PROFILE
    CHECK(a==UGH_BUDGET,"actual five-million-event exit");
#endif
#ifdef WRAP_PROFILE
    CHECK(a==UGH_OK && left.ax==1 && sound[0][S(FirstScannedEvent)]==9 && sound[0][S(FirstScannedEvent)+1]==0,"wrapped payload completes at cursor9");
    CHECK(sound[0][S(ScannedAdlibVoiceStates)+11]==0x81 && sound[0][S(ScannedAdlibVoiceStates)+16]==12,"extra instrument byte and owner12 after wrap");
#endif
    for(unsigned i=0;i<65537;i++) CHECK(sound[0][i]==sound[1][i],"full persistent SOUND bytes");
    for(unsigned i=0x1000;i<8192;i++) CHECK(stack[0][i]==stack[1][i],"caller stack");
    CHECK(left.ax==right.ax && left.bx==right.bx && left.cx==right.cx && left.dx==right.dx,"volatile ABI");
    CHECK(left.si==right.si && left.di==right.di && left.bp==right.bp && left.sp==right.sp,"preserved/partial-error ABI");
    CHECK(left.ds==right.ds && left.es==right.es && left.flags==right.flags,"segments and flags");
    CHECK(io_count[0]==io_count[1] && callback_count[0]==callback_count[1],"ordered effect counts");
    for(unsigned i=0;i<io_count[0];i++) for(unsigned j=0;j<3;j++) CHECK(io[0][i][j]==io[1][i][j],"ordered register writes");
    for(unsigned i=0;i<callback_count[0];i++) for(unsigned j=0;j<6;j++) CHECK(callbacks[0][i][j]==callbacks[1][i][j],"ordered live callback inputs");
}
int main(void) {
#ifdef BUDGET_PROFILE
 one_case(0);puts("PASS five-million-event no-wait diagnostic bound");
#elif defined(CLOCK_PROFILE)
 one_case(0);puts("PASS long-wait clock case");
#elif defined(WRAP_PROFILE)
 one_case(0);puts("PASS wrapped twelve-byte instrument capture");
#else
 for(unsigned op=0;op<3;op++){for(unsigned i=0;i<10000;i++) one_case(op);printf("operation%u PASS10000\n",op);}
#endif
 return 0;}
