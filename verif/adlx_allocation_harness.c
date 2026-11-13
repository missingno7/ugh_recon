/* Actual extracted L1 C and maintained native bridge. Ordinary SOUND/stack
 * memory is disjoint; arithmetic flags and all volatile registers are checked. */
#include "pair.inc"
uint8_t ugh_mem[UGH_MEM_SIZE];
static uint8_t memory[2][4608],stack[2][8192];
static unsigned phase,io_count[2];
static uint32_t io[2][1024][3];
uint8_t ugh_read(uint32_t address)
{
    unsigned base=(unsigned)SOUND_SEG*16;
    if(address>=base && address<base+4608) return memory[phase][address-base];
    CHECK(address>=0x70000 && address<0x72000,"read footprint");return stack[phase][address-0x70000];
}
void ugh_write(uint32_t address,uint8_t value)
{
    unsigned base=(unsigned)SOUND_SEG*16;
    if(address>=base && address<base+4608) {memory[phase][address-base]=value;return;}
    CHECK(address>=0x70000 && address<0x72000,"write footprint");stack[phase][address-0x70000]=value;
}
void platform_out(uint16_t port,unsigned size,uint32_t value)
{
    CHECK(io_count[phase]<1024,"write list capacity");
    unsigned i=io_count[phase]++;io[phase][i][0]=port;io[phase][i][1]=size;io[phase][i][2]=value;
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r)
{
    uint16_t saved=r->cs;r->cs=bank;int status=UGH_UNSUPPORTED;
    if(bank==SOUND_SEG) {
        if(target==S(KeyOffAdlibChannel)) status=c_KeyOffAdlibChannel(r);
        else if(target==S(SetAdlibFrequency)) status=c_SetAdlibFrequency(r);
        else if(target==S(LoadAdlibInstrument)) status=c_LoadAdlibInstrument(r);
        else if(target==S(SetAdlibChannelVolume)) status=c_SetAdlibChannelVolume(r);
    } else if(bank==GAME_SEG && target==G(CopyFarBytes)) status=c_CopyFarBytes(r);
    else if(bank==UGH_SEG_C) {
        if(target==UGH_O_C_StopAdlibTrackChannel) status=phase ? c_StopAdlibTrackChannel(r) : reference_StopAdlibTrackChannel(r);
        else if(target==UGH_O_C_RestoreAdlibVoiceAllocation) status=phase ? c_RestoreAdlibVoiceAllocation(r) : reference_RestoreAdlibVoiceAllocation(r);
        else if(target==UGH_O_C_StartAdlibTrackChannel) status=phase ? c_StartAdlibTrackChannel(r) : reference_StartAdlibTrackChannel(r);
    }
    CHECK(status==0,"complete call target set");r->cs=saved;return status;
}
static void one_case(unsigned operation)
{
    for(unsigned i=0;i<4608;i++) memory[0][i]=N8();
    phase=0;uint16_t channel=(uint16_t)(8+N16()%4),count=(uint16_t)(N16()%10),reserved=(uint16_t)(count+N16()%(10-count));
    uint16_t first=(uint16_t)(9-reserved+N16()%(reserved-count+1));
    if(operation==2) {channel=(uint16_t)(8+N16()%5);reserved=(uint16_t)(N16()%10);first=0;}
    uint16_t record=(uint16_t)(S(AudioChannelStates)+42*channel);
    wr16(SOUND_SEG,S(ReservedAdlibChannelCount),reserved);
    wr16(SOUND_SEG,(uint16_t)(record+34),count);wr16(SOUND_SEG,(uint16_t)(record+36),first);
    wr16(SOUND_SEG,(uint16_t)(record+40),(uint16_t)((N16()&65528u)|(operation==2 ? 4 : 5)));
    wr16(SOUND_SEG,S(SoundDeviceBits),(uint16_t)(N16()|1u));
    if(N16()%4==0) wr16(SOUND_SEG,(uint16_t)(record+40),N16());
    if(operation!=1 && N16()%8==0) channel=N16();
    if(operation==1 && (channel<8 || channel>11)) channel=8;
    Regs left={0},right;
    left.ax=N16();left.bx=N16();left.cx=N16();left.dx=N16();left.si=N16();left.di=N16();
    left.bp=N16();left.ds=N16();left.es=N16();left.flags=N16();left.cs=UGH_SEG_C;left.ss=0x7000;left.sp=0x1000;
    wr16(left.ss,(uint16_t)(left.sp+4),channel);wr16(left.ss,(uint16_t)(left.sp+6),N16());
    for(unsigned i=0;i<4608;i++) memory[1][i]=memory[0][i];
    for(unsigned i=0;i<8192;i++) stack[1][i]=stack[0][i];
    io_count[0]=io_count[1]=0;right=left;
    int a=operation==0 ? reference_StopAdlibTrackChannel(&left) : operation==1 ? reference_RestoreAdlibVoiceAllocation(&left) : reference_StartAdlibTrackChannel(&left);
    phase=1;int b=operation==0 ? c_StopAdlibTrackChannel(&right) : operation==1 ? c_RestoreAdlibVoiceAllocation(&right) : c_StartAdlibTrackChannel(&right);
    CHECK(a==b,"status");
    for(unsigned i=0;i<4608;i++) CHECK(memory[0][i]==memory[1][i],"persistent audio bytes");
    for(unsigned i=0x1000;i<8192;i++) CHECK(stack[0][i]==stack[1][i],"caller arguments and stack above frame");
    CHECK(left.ax==right.ax && left.bx==right.bx && left.cx==right.cx && left.dx==right.dx,"volatile ABI");
    CHECK(left.si==right.si && left.di==right.di && left.bp==right.bp && left.sp==right.sp,"preserved ABI");
    CHECK(left.ds==right.ds && left.es==right.es && left.ss==right.ss && left.cs==right.cs && left.flags==right.flags,"segments and flags");
    CHECK(io_count[0]==io_count[1],"ordered write count");
    for(unsigned i=0;i<io_count[0];i++) for(unsigned j=0;j<3;j++) CHECK(io[0][i][j]==io[1][i][j],"ordered port list");
}
int main(void)
{
    for(unsigned operation=0;operation<3;operation++) {
        for(unsigned i=0;i<30000;i++) one_case(operation);
        printf("operation%u PASS30000 native%u literal%u\n",operation,native_counts[operation],literal_counts[operation]);
    }
    return 0;
}
