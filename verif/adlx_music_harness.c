#include "pair.inc"
uint8_t ugh_mem[UGH_MEM_SIZE];
static uint8_t sound[2][65537],stack[2][8192];
static uint16_t reply[20];static unsigned phase,io_count[2],peer_count[2],wait_count[2];
static uint32_t io[2][12000][3];static uint16_t peers[2][32][9];
static uint32_t random_seed=693791;
static uint16_t N16(void) {random_seed=random_seed*1664525u+1013904223u;return (uint16_t)(random_seed>>16);}
static uint8_t N8(void) {return (uint8_t)N16();}
uint8_t ugh_read(uint32_t address)
{
    unsigned b=(unsigned)SOUND_SEG*16u;
    if(address>=b && address<b+65537) return sound[phase][address-b];
    CHECK(address>=0x80000 && address<0x82000,"read footprint");return stack[phase][address-0x80000];
}
void ugh_write(uint32_t address,uint8_t value)
{
    unsigned b=(unsigned)SOUND_SEG*16u;
    if(address>=b && address<b+65537) {sound[phase][address-b]=value;return;}
    CHECK(address>=0x80000 && address<0x82000,"write footprint");stack[phase][address-0x80000]=value;
}
void platform_out(uint16_t port,unsigned size,uint32_t value)
{unsigned i=io_count[phase]++;CHECK(i<12000,"port bound");io[phase][i][0]=port;io[phase][i][1]=size;io[phase][i][2]=value;}
static int peer(Regs *r,uint16_t target,unsigned args)
{
    unsigned i=peer_count[phase]++;CHECK(i<32,"peer bound");uint16_t *p=peers[phase][i];
    p[0]=target;p[1]=r->ax;p[2]=r->bx;p[3]=r->cx;p[4]=r->dx;
    p[5]=rd16(SOUND_SEG,S(MainAdlxPlaying));p[6]=rd16(SOUND_SEG,S(CurrentAdlxSlot));
    p[7]=args ? arg16(r,0) : 0;p[8]=args>1 ? arg16(r,2) : 0;
    r->ax=reply[i%4];r->bx=reply[4];r->cx=reply[5];r->dx=reply[6];r->ds=reply[7];r->flags=reply[8];r->es=reply[16];
    wr16(SOUND_SEG,S(AdlxTickCount),reply[9]);wr16(SOUND_SEG,S(AdlxTickHighWord),reply[10]);
    wr16(SOUND_SEG,S(CurrentAdlxSlot),reply[11]);wr16(SOUND_SEG,S(MusicFadeTargetVolume),reply[12]);
    wr16(SOUND_SEG,S(MainAdlxPlaying),reply[13]%3);
    return (reply[14]&15u)==0 ? UGH_BUDGET : UGH_OK;
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r)
{
    uint16_t old=r->cs;r->cs=bank;int status=UGH_UNSUPPORTED;
    if(bank==UGH_SEG_C && target==UGH_O_C_SetMusicTrackVolume) status=phase ? c_SetMusicTrackVolume(r) : reference_SetMusicTrackVolume(r);
    else if(bank==UGH_SEG_C && (target==UGH_O_C_LoadAdlibTrackData || target==UGH_O_C_StartAdlibTrackChannel || target==UGH_O_C_StopAdlibTrackChannel)) status=peer(r,target,target==UGH_O_C_LoadAdlibTrackData ? 4 : target==UGH_O_C_StartAdlibTrackChannel ? 2 : 1);
    else if(bank==TIMER_SEG && (target==T(RegisterTimerCallback) || target==T(RemoveTimerCallback))) status=peer(r,target,0);
    else if(bank==SOUND_SEG) {
        if(target==S(CancelMusicFade)) status=phase ? c_CancelMusicFade(r) : reference_CancelMusicFade(r);
        else if(target==S(ScheduleMusicFade)) status=phase ? c_ScheduleMusicFade(r) : reference_ScheduleMusicFade(r);
        else if(target==S(SilenceAdlibOperators)) status=phase ? c_SilenceAdlibOperators(r) : reference_SilenceAdlibOperators(r);
        else if(target==S(SetAdlibChannelVolume)) status=c_SetAdlibChannelVolume(r);
        else if(target==S(TickAdlxPlayback)) status=c_TickAdlxPlayback(r);
    }
    CHECK(status==UGH_OK || status==UGH_BUDGET,"complete peer set");r->cs=old;return status;
}
int platform_service_point_at(ServicePoint point,uint16_t bank,uint16_t target,Regs *r)
{
    CHECK(point==SERVICE_TIMER_WAIT && bank==UGH_SEG_C && target==UGH_O_C_StopMusicTrack+0x95,"exact wait site");
    unsigned i=++wait_count[phase];
#ifdef BUDGET_PROFILE
    (void)i;(void)r;return UGH_OK;
#else
    wr16(SOUND_SEG,S(MusicFadeScheduled),i>reply[15]%5 ? 0 : 2);
    r->ax=reply[16];r->cx=reply[17];r->flags=reply[18];
    return (reply[19]&15u)==0 ? UGH_BUDGET : UGH_OK;
#endif
}
static void one(unsigned operation)
{
    phase=0;for(unsigned i=0;i<65537;i++) sound[0][i]=N8();for(unsigned i=0;i<20;i++) reply[i]=N16();
    const uint16_t counts[8]={0,1,8,9,10,256,265,65535};
    wr16(SOUND_SEG,S(MusicVoiceCount),counts[N16()%8]);wr16(SOUND_SEG,S(SoundDeviceBits),N16()%4);
    wr16(SOUND_SEG,S(MainAdlxPlaying),N16()%3);wr16(SOUND_SEG,S(MusicFadeScheduled),N16()%4);
    wr16(SOUND_SEG,S(MusicFadeStep),N16()%2 ? N16() : 65535);wr16(SOUND_SEG,S(MusicFadeDuration),N16()%2 ? N16() : 0);
    Regs a={0};a.cs=operation<3 ? UGH_SEG_C : SOUND_SEG;a.ss=0x8000;a.sp=0x1000;
    a.ax=N16();a.bx=N16();a.cx=N16();a.dx=N16();a.si=N16();a.di=N16();a.bp=N16();a.ds=N16();a.es=N16();a.flags=N16();
    wr16(a.ss,0x1004,N16()%2 ? N16() : 0);wr16(a.ss,0x1006,0x6000);wr16(a.ss,0x1008,N16()%2 ? N16() : 0);wr16(a.ss,0x100a,N16());
#ifdef BUDGET_PROFILE
    CHECK(operation==1,"stop budget profile");wr16(SOUND_SEG,S(SoundDeviceBits),1);wr16(SOUND_SEG,S(MainAdlxPlaying),1);
    wr16(SOUND_SEG,S(MusicFadeScheduled),0);wr16(a.ss,0x1004,1);reply[13]=1;reply[14]=1;
#endif
    for(unsigned i=0;i<65537;i++) sound[1][i]=sound[0][i];
    for(unsigned i=0;i<8192;i++) stack[1][i]=stack[0][i];
    io_count[0]=io_count[1]=peer_count[0]=peer_count[1]=wait_count[0]=wait_count[1]=0;Regs b=a;int x,y;
    int (*reference[8])(Regs *)={reference_StartMusicTrack,reference_StopMusicTrack,reference_SetMusicTrackVolume,reference_ScheduleMusicFade,reference_CancelMusicFade,reference_AdvanceMusicFade,reference_AdvanceGuardedSoundClock,reference_SilenceAdlibOperators};
    int (*native[8])(Regs *)={c_StartMusicTrack,c_StopMusicTrack,c_SetMusicTrackVolume,c_ScheduleMusicFade,c_CancelMusicFade,c_AdvanceMusicFade,c_AdvanceGuardedSoundClock,c_SilenceAdlibOperators};
    x=reference[operation](&a);phase=1;y=native[operation](&b);CHECK(x==y,"status");
#ifdef BUDGET_PROFILE
    CHECK(x==UGH_BUDGET && wait_count[0]==5000000,"actual wait budget exit");
#endif
    for(unsigned i=0;i<65537;i++) CHECK(sound[0][i]==sound[1][i],"full SOUND RAM");
    for(unsigned i=0x1000;i<8192;i++) CHECK(stack[0][i]==stack[1][i],"caller stack");
    CHECK(a.ax==b.ax && a.bx==b.bx && a.cx==b.cx && a.dx==b.dx && a.si==b.si && a.di==b.di && a.bp==b.bp && a.sp==b.sp,"all GP and partial-error stack");
    CHECK(a.ds==b.ds && a.es==b.es && a.flags==b.flags,"segments and all flags");
    CHECK(io_count[0]==io_count[1] && peer_count[0]==peer_count[1] && wait_count[0]==wait_count[1],"ordered effect counts");
    for(unsigned i=0;i<io_count[0];i++) for(unsigned j=0;j<3;j++) CHECK(io[0][i][j]==io[1][i][j],"ordered writes");
    for(unsigned i=0;i<peer_count[0];i++) for(unsigned j=0;j<9;j++) CHECK(peers[0][i][j]==peers[1][i][j],"ordered peer inputs");
}
int main(void) {
#ifdef BUDGET_PROFILE
    one(1);puts("PASS actual five-million-delivery wait bound");
#else
    for(unsigned operation=0;operation<8;operation++) {for(unsigned i=0;i<2000;i++) one(operation);printf("operation%u PASS2000\n",operation);}
#endif
    return 0;
}
