#include "pair.inc"
uint8_t ugh_mem[UGH_MEM_SIZE];
static uint8_t sound[2][65537],stack[2][8192];
static unsigned phase,stop_calls[2],swap_calls[2],stages[7];
static uint16_t replies[5];
uint8_t ugh_read(uint32_t address)
{
    uint32_t b=(uint32_t)SOUND_SEG*16u;
    if(address>=b && address<b+65537) return sound[phase][address-b];
    if(address>=0x60000 && address<=0x70000) return ugh_mem[address];
    CHECK(address>=0x80000 && address<0x82000,"stack read footprint");return stack[phase][address-0x80000];
}
void ugh_write(uint32_t address,uint8_t value)
{
    uint32_t b=(uint32_t)SOUND_SEG*16u;
    if(address>=b && address<b+65537) {sound[phase][address-b]=value;return;}
    CHECK(address>=0x80000 && address<0x82000,"stack write footprint");stack[phase][address-0x80000]=value;
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r)
{
    CHECK(bank==UGH_SEG_C,"callee bank");
    if(target==UGH_O_C_SwapDwordByteOrder) {swap_calls[phase]++;return c_SwapDwordByteOrder(r);}
    if(target==UGH_O_C_LoadAdlibTrackData) return phase ? c_LoadAdlibTrackData(r) : reference_LoadAdlibTrackData(r);
    CHECK(target==UGH_O_C_StopAdlibTrackChannel,"complete callee targets");
    stop_calls[phase]++;sound[phase][0]^=255;r->ax=replies[0];r->bx=replies[1];r->cx=replies[2];r->dx=replies[3];r->es=replies[4];
    return 0;
}
static void resource_tag(uint16_t offset,const char tag[4])
{for(unsigned i=0;i<4;i++) ugh_mem[0x60000u+(uint16_t)(offset+i)]=(uint8_t)tag[i];}
static void resource_size(uint16_t offset,uint16_t low,uint16_t high)
{
    uint8_t b[4]={(uint8_t)(high>>8),(uint8_t)high,(uint8_t)(low>>8),(uint8_t)low};
    for(unsigned i=0;i<4;i++) ugh_mem[0x60000u+(uint16_t)(offset+i)]=b[i];
}
static void one_case(unsigned operation)
{
    phase=0;for(unsigned i=0;i<65537;i++) sound[0][i]=N8();
    for(unsigned i=0;i<65537;i++) ugh_mem[0x60000u+i]=N8();
    uint16_t index=N16(),h=(uint16_t)(index+8),ah=N16()%2 ? 10 : N16(),im=N16()%2 ? 0 : N16();
    uint16_t map=(uint16_t)(h+8+ah),track=(uint16_t)(map+8+im),channel=(uint16_t)(8+N16()%5);
    resource_tag(index,"ADLX");resource_tag(h,"AHDR");resource_tag(map,"IMAP");resource_tag(track,"TRCK");
    resource_size((uint16_t)(index+4),N16(),N16());resource_size((uint16_t)(h+4),ah,N16());resource_size((uint16_t)(map+4),im,N16());
    if(N16()%4==0) ugh_mem[0x60000u+(uint16_t)((N16()%4==0 ? index : N16()%3==0 ? h : N16()%2==0 ? map : track)+N16()%4)]^=1;
    if(N16()%4==0) channel=N16();
    for(unsigned i=0;i<5;i++) replies[i]=N16();
    Regs left={0},right;left.cs=UGH_SEG_C;left.ss=0x8000;left.sp=0x1000;
    left.ax=N16();left.bx=N16();left.cx=N16();left.dx=N16();left.si=N16();left.di=N16();left.bp=N16();left.ds=N16();left.es=N16();left.flags=N16();
    if(operation==2 && (int16_t)channel<0) channel=8; /* raw negative aliases have L0 cases */
    wr16(left.ss,0x1004,channel);wr16(left.ss,0x1006,index);wr16(left.ss,0x1008,0x6000);wr16(left.ss,0x100a,N16());wr16(left.ss,0x100c,N16());
    if(channel>=8 && channel<=12) wr16(SOUND_SEG,S(SoundDeviceBits),(uint16_t)(N16()|1u));
    for(unsigned i=0;i<65537;i++) sound[1][i]=sound[0][i];
    for(unsigned i=0;i<8192;i++) stack[1][i]=stack[0][i];
    stop_calls[0]=stop_calls[1]=swap_calls[0]=swap_calls[1]=0;right=left;
    int a=operation==0 ? reference_LoadAdlibTrackData(&left) : operation==1 ? reference_LoadAdlibChannel(&left) : reference_ResetAdlibTrackChannelCursor(&left);
    phase=1;int b=operation==0 ? c_LoadAdlibTrackData(&right) : operation==1 ? c_LoadAdlibChannel(&right) : c_ResetAdlibTrackChannelCursor(&right);
    CHECK(a==b,"status");
    for(unsigned i=0;i<65537;i++) CHECK(sound[0][i]==sound[1][i],"byte-exact shared audio state and instrument map");
    for(unsigned i=0x1000;i<8192;i++) CHECK(stack[0][i]==stack[1][i],"caller frame and arguments");
    CHECK(left.ax==right.ax && left.bx==right.bx && left.cx==right.cx && left.dx==right.dx,"volatile ABI");
    CHECK(left.si==right.si && left.di==right.di && left.bp==right.bp && left.sp==right.sp,"preserved ABI");
    CHECK(left.ds==right.ds && left.es==right.es && left.flags==right.flags,"segment and flags");
    CHECK(stop_calls[0]==stop_calls[1],"STOP capability multiplicity");
}
int main(void)
{
    for(unsigned op=0;op<3;op++) {for(unsigned i=0;i<10000;i++) one_case(op);printf("operation%u PASS10000\n",op);}
    printf("parser stages");for(unsigned i=0;i<7;i++) printf(" %u",stages[i]);puts("");return 0;
}
