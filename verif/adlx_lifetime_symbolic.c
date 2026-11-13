/* Appended to extracted real L1 bodies, native module and its actual bridge. */
uint8_t ugh_mem[UGH_MEM_SIZE];Devices ugh_devices;
Regs nondet_regs(void);uint16_t nondet_u16(void);uint8_t nondet_u8(void);unsigned nondet_uint(void);
static unsigned phase,counts[2],input_count[2],service_count[2],polls[2][2];
static uint16_t words[2][6],initial_words[6],status_bytes[2],timer_value[4],timer_salt,progress_bias;
static uint8_t ops[9],calibration,stack[2][128],initial_stack[128];
/* An arbitrary event position represents every member of the ordered list.
 * Counts and capacity are checked separately; this avoids whole-list SSA. */
static uint16_t trace[2][3];static unsigned trace_position,which_fail,begin_skip,finish_skip;
static unsigned witness;static uint8_t witness_initial,witness_value[2];
static unsigned word_offset(unsigned i)
{return i==0 ? S(PreviousCalibrationTimerVector) : i==1 ? S(PreviousCalibrationTimerSegment) : i==2 ? S(CalibrationLoopRemainder) : i==3 ? S(SoundIoDelayMultiplier) : i==4 ? S(AdlxPlaybackTimerHandle) : S(AdlibInitAttempted);}
static void record(unsigned kind,uint16_t number,uint16_t value)
{unsigned i=counts[phase]++;CHECK(i<96,"service event bound");if(i==trace_position) {trace[phase][0]=(uint16_t)kind;trace[phase][1]=number;trace[phase][2]=value;}}
static int word_index(unsigned p)
{
    for(unsigned i=0;i<5;i++) if(p>=word_offset(i) && p<word_offset(i)+2) return (int)i;
    if(p==S(AdlibInitAttempted)) return 5;
    return -1;
}
uint8_t ugh_read(uint32_t address)
{
    unsigned base=(unsigned)SOUND_SEG*16u,p=address-base;
    if(RESETTING) {CHECK(address>=base && address<base+65537,"reset reads owner only");return nondet_u8();}
    int i=word_index(p);
    if(i>=0) return (uint8_t)(words[phase][i]>>(8*(p-word_offset((unsigned)i))));
    if(p>=S(AdlibOperatorOffsets) && p<S(AdlibOperatorOffsets)+9) return ops[p-S(AdlibOperatorOffsets)];
    if(address>=0x80000 && address<0x80080) return stack[phase][address-0x80000];
    CHECK(0,"no omitted memory input");return 0;
}
void ugh_write(uint32_t address,uint8_t value)
{
    if(address==witness) witness_value[phase]=value;
    unsigned base=(unsigned)SOUND_SEG*16u,p=address-base;
    if(RESETTING) {CHECK(address>=base+12 && address<base+12+0x488,"reset write frame");CHECK(value==0,"every reset store is zero");return;}
    int i=word_index(p);
    if(i>=0) {unsigned shift=8*(p-word_offset((unsigned)i));words[phase][i]=(uint16_t)((words[phase][i]&~(255u<<shift))|((unsigned)value<<shift));return;}
    if(address>=0x80000 && address<0x80080) {stack[phase][address-0x80000]=value;return;}
    if(address>=0x20 && address<0x24) return; /* External IVT service storage. */
    CHECK(0,"write frame excludes all other RAM");
}
void platform_out(uint16_t port,unsigned size,uint32_t value)
{CHECK(size==1,"byte port width");record(1,port,(uint16_t)value);}
uint32_t platform_in(uint16_t port,unsigned size)
{CHECK(size==1 && port==0x388,"OPL status interface");unsigned i=input_count[phase]++;CHECK(i<2,"status read count");record(2,port,status_bytes[i]);return status_bytes[i];}
int platform_interrupt(uint8_t number,Regs *r)
{
    CHECK(number==0x21 && (r->ax==0x3508 || r->ax==0x2508),"DOS vector service interface");
    record(3,r->ax,r->dx);unsigned i=++service_count[phase];
    if(r->ax==0x3508) {r->bx=timer_value[0];r->es=timer_value[1];}
    else if(r->dx==S(BeginSoundDelayMeasurement)) r->dx=progress_bias;
    return i==which_fail ? UGH_UNSUPPORTED : UGH_OK;
}
int lifetime_silence_contract(Regs *r)
{
    for(unsigned i=0;i<9;i++) record(7,(uint16_t)i,rd8(r->cs,(uint16_t)(S(AdlibOperatorOffsets)+i)));
    uint8_t delay=rd8(r->cs,S(SoundIoDelayMultiplier));record(8,0,delay);
    r->bx=timer_value[3];r->cx=0;flag(r,CF,4u*delay>255);flag(r,OF,4u*delay>255);return 0;
}
int ugh_dispatch(uint16_t bank,uint16_t target,Regs *r)
{
    if(bank==SOUND_SEG && target==S(CalibrateSoundDelay)) {
        /* Separately checked measurement service: arbitrary shared normal
         * flags/result words; preserves caller registers and stack. */
        record(4,target,0);r->flags=timer_value[2];words[phase][2]=timer_value[0];words[phase][3]=timer_value[1];
        return ++service_count[phase]==which_fail ? UGH_UNSUPPORTED : UGH_OK;
    }
    CHECK(bank==TIMER_SEG,"external TIMER service");
    CHECK(target==T(InstallTimerInterrupt) || target==T(RegisterTimerCallback) || target==T(RemoveTimerCallback) || target==T(RestoreTimerInterrupt),"TIMER target set");
    record(4,target,r->ax);record(5,r->bx,r->cx);record(6,r->dx,r->ds);
    r->ax=timer_value[3];r->ds=timer_salt;r->bx^=timer_salt;r->cx^=timer_salt;r->dx=(uint16_t)(r->dx+timer_salt);r->flags^=timer_salt;
    return ++service_count[phase]==which_fail ? UGH_UNSUPPORTED : UGH_OK;
}
int platform_service_point_at(ServicePoint point,uint16_t bank,uint16_t offset,Regs *r)
{
    CHECK(point==SERVICE_TIMER_WAIT && bank==SOUND_SEG,"explicit calibration wait");
    unsigned which=offset==S(loc_116B);CHECK(which || offset==S(loc_1163),"poll point set");
    unsigned visit=polls[phase][which]++;CHECK(visit<2,"delivery within two visits per phase");
    if(visit==(which ? finish_skip : begin_skip)) {
        uint16_t flags=r->flags;
        int result=which ? (phase ? c_FinishSoundDelayMeasurement(r) : reference_FinishSoundDelayMeasurement(r)) : (phase ? c_BeginSoundDelayMeasurement(r) : reference_BeginSoundDelayMeasurement(r));
        r->flags=flags;return result;
    }
    return 0;
}
int main(void)
{
    Regs a=nondet_regs();a.cs=SOUND_SEG;a.ss=0x8000;a.sp=0x60;Regs b=a;
    for(unsigned i=0;i<6;i++) {initial_words[i]=nondet_u16();words[0][i]=initial_words[i];words[1][i]=initial_words[i];}
    /* Attempted is a BYTE even if its following resident cell is stale. */
    words[0][5]&=255;words[1][5]&=255;
    for(unsigned i=0;i<128;i++) {initial_stack[i]=nondet_u8();stack[0][i]=initial_stack[i];stack[1][i]=initial_stack[i];}
    for(unsigned i=0;i<9;i++) ops[i]=nondet_u8();
    for(unsigned i=0;i<2;i++) status_bytes[i]=nondet_u8();
    for(unsigned i=0;i<4;i++) timer_value[i]=nondet_u16();
    timer_salt=nondet_u16();calibration=nondet_u8();progress_bias=nondet_u16();
    begin_skip=nondet_uint();finish_skip=nondet_uint();__CPROVER_assume(begin_skip<2 && finish_skip<2);
    which_fail=nondet_uint();__CPROVER_assume(which_fail<6);
    trace_position=nondet_uint();__CPROVER_assume(trace_position<96);
    witness=nondet_uint();__CPROVER_assume(witness<UGH_MEM_SIZE);witness_initial=nondet_u8();witness_value[0]=witness_value[1]=witness_initial;
    /* The arbitrary RAM witness and typed bindings describe one memory. In
     * particular an already-zero attempted byte must also start zero here. */
    if(!RESETTING) {
        unsigned p=witness-(unsigned)SOUND_SEG*16u;int i=word_index(p);
        if(i>=0) witness_initial=(uint8_t)(words[0][i]>>(8*(p-word_offset((unsigned)i))));
        else if(witness>=0x80000 && witness<0x80080) witness_initial=initial_stack[witness-0x80000];
        witness_value[0]=witness_value[1]=witness_initial;
    }
    int left=ENTRY_REFERENCE(&a);phase=1;int right=ENTRY_NATIVE(&b);
    if(OUTPUTS) {
        CHECK(left==right,"same status and failed service prefix");
        CHECK(a.ax==b.ax && a.bx==b.bx && a.cx==b.cx && a.dx==b.dx && a.si==b.si && a.di==b.di && a.bp==b.bp && a.sp==b.sp && a.ds==b.ds && a.es==b.es && a.flags==b.flags,"all register/flag outputs");
        for(unsigned i=0;i<6;i++) CHECK(words[0][i]==words[1][i],"every owned word and attempted byte");
        CHECK(counts[0]==counts[1] && input_count[0]==input_count[1] && service_count[0]==service_count[1],"event/read/service counts");
        for(unsigned j=0;j<3;j++) CHECK(trace[0][j]==trace[1][j],"arbitrary ordered port/service position");
        for(unsigned i=0;i<2;i++) CHECK(polls[0][i]==polls[1][i],"wait instruction visits");
        CHECK(witness_value[0]==witness_value[1],"arbitrary full RAM output byte");
    }
    if(FRAME) {
        CHECK(a.cs==b.cs && a.ss==b.ss && a.ip==b.ip,"control frame");
        unsigned i=nondet_uint();__CPROVER_assume(i<128);CHECK(stack[0][i]==stack[1][i],"arbitrary caller/save/return stack byte");
        CHECK(witness_value[0]==witness_value[1],"arbitrary whole RAM frame byte");
    }
    /* The read/write mappers above assert the entire dependency/frame set on
     * every executed operation. No unbound read returns a convenient zero. */
    if(DEPENDENCE) CHECK(left==right,"declared-read/service-only result");
    return 0;
}
