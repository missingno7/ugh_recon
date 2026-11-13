#include "pair.inc"
uint8_t ugh_mem[UGH_MEM_SIZE];Devices ugh_devices;
static uint8_t memory[2][UGH_MEM_SIZE];
static uint32_t events[2][128][4],count[2],visits[2][2],phase,service_count[2];
static uint32_t random_seed=831907;
static uint16_t N16(void) {random_seed=random_seed*1664525u+1013904223u;return (uint16_t)(random_seed>>16);}
static uint16_t status_bytes[2],vector_offset,vector_bank,timer_reply,service_salt,bias;
static uint32_t first_skip,second_skip,fail_service,reads[2];static unsigned mutate_bias;
uint8_t ugh_read(uint32_t address) {CHECK(address<UGH_MEM_SIZE,"read bounds");return memory[phase][address];}
void ugh_write(uint32_t address,uint8_t value) {CHECK(address<UGH_MEM_SIZE,"write bounds");memory[phase][address]=value;}
static void event(unsigned kind,uint16_t port,unsigned size,uint32_t value)
{unsigned i=count[phase]++;CHECK(i<128,"event capacity");events[phase][i][0]=kind;events[phase][i][1]=port;events[phase][i][2]=size;events[phase][i][3]=value;}
void platform_out(uint16_t port,unsigned size,uint32_t value) {event(1,port,size,value);}
uint32_t platform_in(uint16_t port,unsigned size)
{unsigned i=reads[phase]++;event(2,port,size,status_bytes[i<2 ? i : 1]);return status_bytes[i<2 ? i : 1];}
int platform_interrupt(uint8_t number,Regs *r)
{
    event(3,number,0,r->ax);unsigned fail=(++service_count[phase]==fail_service);
    if(r->ax==0x3508) {r->bx=vector_offset;r->es=vector_bank;}
    else {CHECK(r->ax==0x2508,"DOS service set complete");wr16(0,0x20,r->dx);wr16(0,0x22,r->ds);
        if(mutate_bias && r->dx==S(BeginSoundDelayMeasurement)) r->dx=bias;}
    return fail ? UGH_UNSUPPORTED : UGH_OK;
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r)
{
    if(bank==SOUND_SEG && target==S(CalibrateSoundDelay)) {
#ifdef EXHAUSTIVE_PROBE
        /* Separate measurement contract, exercised in the 12000-pair run. */
        return UGH_OK;
#else
        return phase ? c_CalibrateSoundDelay(r) : reference_CalibrateSoundDelay(r);
#endif
    }
    CHECK(bank==TIMER_SEG,"only TIMER peer entries");event(4,target,0,r->ax);
    CHECK(target==T(InstallTimerInterrupt) || target==T(RegisterTimerCallback) || target==T(RemoveTimerCallback) || target==T(RestoreTimerInterrupt),"complete TIMER service set");
    unsigned fail=(++service_count[phase]==fail_service);
    r->ax=timer_reply;r->ds=service_salt;r->cx^=service_salt;r->dx=(uint16_t)(r->dx+service_salt);r->bx^=timer_reply;r->flags^=0x895;
    wr16(SOUND_SEG,S(CurrentAdlxSlot),service_salt);return fail ? UGH_UNSUPPORTED : UGH_OK;
}
int platform_service_point_at(ServicePoint point,uint16_t bank,uint16_t offset,Regs *r)
{
    CHECK(point==SERVICE_TIMER_WAIT && bank==SOUND_SEG,"calibration service domain");
    unsigned which=offset==S(loc_116B);CHECK(which || offset==S(loc_1163),"poll instruction set");
    uint32_t i=visits[phase][which]++;uint32_t trigger=which ? second_skip : first_skip;
    if(i==trigger) {
        uint16_t flags=r->flags;
        int status=which ? (phase ? c_FinishSoundDelayMeasurement(r) : reference_FinishSoundDelayMeasurement(r)) : (phase ? c_BeginSoundDelayMeasurement(r) : reference_BeginSoundDelayMeasurement(r));
        r->flags=flags;return status;
    }
    return UGH_OK;
}
static void pair(unsigned which)
{
    operation=which;phase=0;
    for(unsigned i=0;i<65537;i++) memory[0][(unsigned)SOUND_SEG*16u+i]=(uint8_t)N16();
    for(unsigned i=0;i<8192;i++) memory[0][0x80000+i]=(uint8_t)N16();
    Regs a={0};a.cs=SOUND_SEG;a.ss=0x8000;a.sp=0x1000;
    a.ax=N16();a.bx=N16();a.cx=N16();a.dx=N16();a.si=N16();a.di=N16();a.bp=N16();a.ds=N16();a.es=N16();a.flags=N16();
    vector_offset=N16();vector_bank=N16();timer_reply=N16();service_salt=N16();bias=N16();mutate_bias=(case_number%5==0);
    first_skip=N16()%5;second_skip=(case_number%97==0) ? 1000001u : (uint32_t)(N16()%3)*65536u+(N16()%19);
    fail_service=(case_number%7==0) ? N16()%9+1u : 0;
    status_bytes[0]=N16()&31u;status_bytes[1]=N16();
    if(case_number%4==0) status_bytes[0]=N16();
    wr8(SOUND_SEG,S(AdlibInitAttempted),case_number%4==0 ? (uint8_t)N16() : 0);
#ifdef EXHAUSTIVE_PROBE
    fail_service=0;status_bytes[0]=(uint16_t)(case_number>>8);status_bytes[1]=(uint16_t)(case_number&255u);
    wr8(SOUND_SEG,S(AdlibInitAttempted),0);
#endif
    /* Low-level multiply and operator table remain arbitrary, including wraps. */
    memcpy(memory[1],memory[0],UGH_MEM_SIZE);Regs b=a;
    memset(events,0,sizeof events);memset(count,0,sizeof count);memset(visits,0,sizeof visits);memset(reads,0,sizeof reads);memset(service_count,0,sizeof service_count);
    int (*ref[6])(Regs *)={reference_ClearSoundState,reference_InitializeAdlibPlayback,reference_ShutdownAdlibPlayback,reference_CalibrateSoundDelay,reference_BeginSoundDelayMeasurement,reference_FinishSoundDelayMeasurement};
    int (*native[6])(Regs *)={c_ClearSoundState,c_InitializeAdlibPlayback,c_ShutdownAdlibPlayback,c_CalibrateSoundDelay,c_BeginSoundDelayMeasurement,c_FinishSoundDelayMeasurement};
    ugh_devices.error=case_number%101==0;int x=ref[which](&a);phase=1;ugh_devices.error=case_number%101==0;int y=native[which](&b);
    CHECK(x==y,"return/failure status");
    CHECK(!memcmp(memory[0],memory[1],UGH_MEM_SIZE),"full RAM including caller stack, IVT and resident PCM");
    CHECK(!memcmp(&a,&b,sizeof a),"all registers and all L1 flags including error prefixes");
    CHECK(count[0]==count[1] && !memcmp(events[0],events[1],sizeof events[0]),"all ordered ports/DOS/TIMER calls");
    CHECK(!memcmp(visits[0],visits[1],sizeof visits[0]),"exact service polling visit counts");
    CHECK(reads[0]==reads[1] && service_count[0]==service_count[1],"service counts");
}
int main(void)
{
    for(unsigned i=0;i<UGH_MEM_SIZE;i++) memory[0][i]=(uint8_t)N16();
#ifdef EXHAUSTIVE_PROBE
    for(case_number=0;case_number<65536;case_number++) pair(1);
    puts("PASS all 65536 OPL status-byte pairs under successful calibration/TIMER contracts; full RAM/registers and ordered I/O compared");return 0;
#else
    for(unsigned which=0;which<6;which++) for(case_number=0;case_number<2000;case_number++) pair(which);
    puts("PASS 12000 compiled pairs: full RAM, all registers/flags, ordered ports/DOS/TIMER services, exact polling counts; service errors and missing delivery included");return 0;
#endif
}
