/* Actual L1/native/bridge functions. The shim is precisely eight state bytes
 * plus two guard bytes on either side, ordinary serialized RAM; no stack alias. */
void __CPROVER_assert(_Bool,const char *);
void __CPROVER_assume(_Bool);
extern uint8_t nondet_byte(void);
extern uint16_t nondet_word(void);
extern int nondet_int(void);
static uint8_t memory[12], initial[12], expected[12];
static uint16_t selected_segment;
static Regs time_response;
static int time_status;
static unsigned service_calls;
uint8_t ugh_read(uint32_t address) {
    uint32_t start=lin(selected_segment,G(RandomStateWord0))-2;
    __CPROVER_assert(address>=start+2 && address<start+10,"read only RNG state");
    return memory[address-start];
}
void ugh_write(uint32_t address,uint8_t value) {
    uint32_t start=lin(selected_segment,G(RandomStateWord0))-2;
    __CPROVER_assert(address>=start+2 && address<start+10,"write only RNG state");
    memory[address-start]=value;
}
int platform_interrupt(uint8_t number,Regs *r) {
    __CPROVER_assert(number==0x21 && (r->ax>>8)==0x2c,"DOS time service AH=2C");
    service_calls++;
    *r=time_response;
    return time_status;
}
static void same_shell(Regs a,Regs b) {
    __CPROVER_assert(a.ax==b.ax && a.bx==b.bx && a.cx==b.cx && a.dx==b.dx &&
        a.si==b.si && a.di==b.di && a.bp==b.bp && a.sp==b.sp && a.cs==b.cs &&
        a.ds==b.ds && a.es==b.es && a.ss==b.ss && a.ip==b.ip && a.flags==b.flags,
        "complete L1 register and flag shell");
}
int main(void) {
    Regs old; Regs modern=old;
    for(unsigned i=0;i<12;i++) initial[i]=memory[i]=nondet_byte();
    selected_segment=old.cs;
    RandomState state=random_project(&old);
#if RANDOM_SEED
    Regs response;response.cs=old.cs;time_response=response;
    time_status=nondet_int();
    selected_segment=time_response.cs;
    RandomDosTime time={(uint8_t)(time_response.cx>>8),(uint8_t)time_response.cx,
                       (uint8_t)(time_response.dx>>8),(uint8_t)time_response.dx};
    random_seed(&state,time);
    __CPROVER_assert(state.word[0]==(uint16_t)((initial[2])+(uint16_t)time.seconds*256u),"partial reseed value");
    for(unsigned i=1;i<4;i++)
        __CPROVER_assert(state.word[i]==(uint16_t)(initial[2+2*i]+(uint16_t)initial[3+2*i]*256u),"native seed preserves other words");
    int a=l1_SeedRandomFromDosSeconds(&old);
#else
    selected_segment=old.cs;
    uint16_t bound=old.ax;
    uint16_t result=random_next_below(&state,bound);
#if RANDOM_RANGE
    __CPROVER_assert(!bound ? result==0 : result<bound,"exclusive output range including zero/one");
#endif
    int a=l1_NextRandomBelowAx(&old);
    __CPROVER_assert(result==old.ax,"native/L1 multiply-high result, all 80 input bits");
#endif
    for(unsigned i=0;i<12;i++) expected[i]=memory[i];
#if RANDOM_SEED
    if(!time_status) {
        __CPROVER_assert(expected[3]==(uint8_t)(state.word[0]>>8),"native/L1 seed byte");
        for(unsigned i=0;i<12;i++) if(i!=3) __CPROVER_assert(expected[i]==initial[i],"seed preserves other eleven bytes");
    } else for(unsigned i=0;i<12;i++) __CPROVER_assert(expected[i]==initial[i],"failed service preserves all state");
#else
    for(unsigned i=0;i<4;i++)
        __CPROVER_assert(state.word[i]==(uint16_t)(expected[2+2*i]+(uint16_t)expected[3+2*i]*256u),"native/L1 all four state words");
#endif
    for(unsigned i=0;i<12;i++) memory[i]=initial[i];
#if RANDOM_SEED
    int b=c_SeedRandomFromDosSeconds(&modern);
    __CPROVER_assert(service_calls==2,"one DOS service per seed");
#else
    int b=c_NextRandomBelowAx(&modern);
#endif
    __CPROVER_assert(a==b,"identical status");
    same_shell(old,modern);
    for(unsigned i=0;i<12;i++) __CPROVER_assert(memory[i]==expected[i],"all state and guard bytes");
    return 0;
}
