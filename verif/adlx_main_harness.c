/* Normalized, disjoint ordinary RAM. Every byte of the audio owner is arbitrary.
 * No instruction-level IRQ or source/destination alias is assumed. TIMER is an
 * observing contract (request ABI only); delays have their state-only contract.
 * The actual extracted L1 handlers and voice drivers are in pair.inc. */
#include "pair.inc"

uint8_t ugh_mem[UGH_MEM_SIZE];
typedef struct SoundRam {uint8_t bytes[1280];} SoundRam;
static SoundRam sound[2];
static uint8_t operators[9],auxiliary[10],operands[12],stack_bytes[128];
#ifdef __CPROVER__
SoundRam nondet_sound(void);
#endif
static unsigned phase;
static uint16_t payload_index;
static uint32_t io[2][28][3],io_count[2],timer[2][3],timer_count[2];

uint8_t ugh_read(uint32_t address)
{
    uint32_t base=(uint32_t)SOUND_SEG*16u;
    if(address>=base && address<base+1280) return sound[phase].bytes[address-base];
    if(address>=base+S(AdlibOperatorOffsets) && address<base+S(AdlibOperatorOffsets)+9)
        return operators[address-base-S(AdlibOperatorOffsets)];
    if(address>=base+S(AdlxPlaybackTimerHandle) && address<base+S(AdlxPlaybackTimerHandle)+10)
        return auxiliary[address-base-S(AdlxPlaybackTimerHandle)];
    if(address>=0x90000u && address<=0xa0000u) {
        uint16_t index=(uint16_t)((uint16_t)(address-0x90000u)-payload_index);
        CHECK(index<12,"operand footprint");return operands[index];
    }
    CHECK(address>=0x70f80u && address<0x71000u,"stack read footprint");
    return stack_bytes[address-0x70f80u];
}
void ugh_write(uint32_t address,uint8_t value)
{
    uint32_t base=(uint32_t)SOUND_SEG*16u;
    if(address>=base && address<base+1280) {sound[phase].bytes[address-base]=value;return;}
    CHECK(address>=0x70f80u && address<0x71000u,"stack write footprint");
    stack_bytes[address-0x70f80u]=value;
}
void platform_out(uint16_t port,unsigned size,uint32_t value)
{
    CHECK(io_count[phase]<28,"ordered write capacity");
    io[phase][io_count[phase]][0]=port;io[phase][io_count[phase]][1]=size;io[phase][io_count[phase]][2]=value;
    io_count[phase]++;
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
    CHECK(segment==TIMER_SEG && offset==T(SetTimerCallbackInterval),"complete external target set");
    timer_count[phase]++;timer[phase][0]=r->ax;timer[phase][1]=r->bx;timer[phase][2]=r->cx;
    return UGH_OK;
}
/* One-step cut: the tail is exactly the next interpreter step. Wait/END do
 * not reach it. The tested step includes all actual real voice callees. */
int c_RunMainAdlxEvents(Regs *r) {(void)r;return 0;}
int c_RunEffectAdlxEvents(Regs *r) {(void)r;return 0;}
int l1_HandleMainAdlxInstrument(Regs *r) {(void)r;CHECK(0,"excluded source alias fallback");return 1;}

static void one_case(void)
{
    initialize();
    Regs left={0},right;
    left.ax=N16();left.bx=N16();left.cx=N16();left.dx=N16();left.si=N16();left.di=N16();
    left.bp=N16();left.ds=N16();left.flags=N16();left.cs=SOUND_SEG;left.es=0x9000;
    left.ss=0x7000;left.sp=0x1000;payload_index=left.di;
    left.ax=OP<8 ? (uint16_t)((left.ax&0xff0fu)|OP*16) : (uint16_t)((left.ax&0xff7fu)|128);
#if CHANNEL >= 0
    left.ax=(uint16_t)((left.ax&0xfff0u)|CHANNEL);
#endif
    right=left;phase=0;
    int result=reference_event(&left);
    CHECK(result==0,"reference normal step");
    phase=1;result=audio_bridge_event(&right,(AudioMainOperation)OP);
    CHECK(result==0 || result==-1,"native normal step");
    compare_memory();
    CHECK(left.ax==right.ax,"AX shell");CHECK(left.bx==right.bx,"BX shell");
    CHECK(left.cx==right.cx,"CX shell");CHECK(left.dx==right.dx,"DX shell");
    CHECK(left.si==right.si,"SI shell");CHECK(left.di==right.di,"cursor advance");
    CHECK(left.bp==right.bp && left.sp==right.sp,"stack shell");
    CHECK(left.ds==right.ds && left.es==right.es && left.cs==right.cs && left.ss==right.ss,"segments");
    CHECK(left.flags==right.flags,"defined L1 flags shell");
    CHECK(io_count[0]==io_count[1],"ordered write count");
    for(unsigned i=0;i<28;i++) for(unsigned j=0;j<3;j++) CHECK(io[0][i][j]==io[1][i][j],"ordered OPL writes");
    CHECK(timer_count[0]==timer_count[1],"timer request count");
    for(unsigned i=0;i<3;i++) CHECK(timer[0][i]==timer[1][i],"timer request ABI");
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
