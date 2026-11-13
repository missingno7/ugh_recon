#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint8_t memory[12];
static RandomDosTime fixture;
uint8_t ugh_read(uint32_t address) {
    unsigned offset=address-G(RandomStateWord0)+2;
    if(offset<2 || offset>=10) abort();
    return memory[offset];
}
void ugh_write(uint32_t address,uint8_t value) {
    unsigned offset=address-G(RandomStateWord0)+2;
    if(offset<2 || offset>=10) abort();
    memory[offset]=value;
}
int platform_interrupt(uint8_t number,Regs *r) {
    if(number!=0x21 || (r->ax>>8)!=0x2c) abort();
    r->cx=(uint16_t)(fixture.hours*256u+fixture.minutes);
    r->dx=(uint16_t)(fixture.seconds*256u+fixture.hundredths);
    return UGH_OK;
}
static void fail(const char *message) { fprintf(stderr,"%s\n",message);exit(23); }
static void publish(RandomState state) {
    memset(memory,0xa7,sizeof memory);
    for(unsigned i=0;i<4;i++) wr16(0,(uint16_t)(G(RandomStateWord0)+2*i),state.word[i]);
}
static void check(RandomState state,uint16_t bound,uint16_t flags,int seed) {
    publish(state);
    Regs a={bound,0x1234,0x5678,0x9abc,0xdef0,0xaaaa,0xbbbb,0xcccc,0,0xeeee,0xffff,0x1111,0x2222,flags}, b=a;
    int sa=seed ? l1_SeedRandomFromDosSeconds(&a) : l1_NextRandomBelowAx(&a);
    uint8_t expected[12];memcpy(expected,memory,sizeof memory);
    publish(state);
    uint16_t value=0;
    if(seed) random_seed(&state,fixture); else value=random_next_below(&state,bound);
    int sb=seed ? c_SeedRandomFromDosSeconds(&b) : c_NextRandomBelowAx(&b);
    if(sa!=sb || memcmp(&a,&b,sizeof a) || memcmp(memory,expected,sizeof memory)) fail("L1/bridge shell or RAM");
    for(unsigned i=0;i<4;i++) if(state.word[i]!=rd16(0,(uint16_t)(G(RandomStateWord0)+2*i))) fail("L1/native state");
    if(!seed && (value!=a.ax || (bound ? value>=bound : value!=0))) fail("L1/native result or range");
}
int main(void) {
    unsigned long next=0,seeds=0;
    const RandomState patterns[]={{{0,0,0,0}},{{65535,65535,65535,65535}},
        {{32515,33076,18620,9031}},{{32768,32767,1,65535}}};
    for(unsigned v=0;v<65536;v++) {
        for(unsigned p=0;p<4;p++) {check(patterns[p],(uint16_t)v,(uint16_t)(v^0x602),0);next++;}
        for(unsigned word=0;word<4;word++) {
            RandomState s=patterns[1];s.word[word]=(uint16_t)v;
            check(s,(uint16_t)(word==0 ? 0 : word==1 ? 1 : word==2 ? 320 : 65535),0x8d7,0);next++;
        }
        /* Complete Cartesian domain of previous word0 and all 256 time bytes.
         * Other words are fixed here; the symbolic proof admits all 64 state bits. */
        for(unsigned seconds=0;seconds<256;seconds++) {
            RandomState s=patterns[2];s.word[0]=(uint16_t)v;
            fixture=(RandomDosTime){(uint8_t)v,(uint8_t)(v>>8),(uint8_t)seconds,(uint8_t)(v^seconds)};
            check(s,(uint16_t)v,0xed7,1);seeds++;
        }
    }
    uint32_t generator=0x12345678;
    for(unsigned n=0;n<100000;n++) {
        RandomState s;
        for(unsigned j=0;j<4;j++) {generator=generator*1664525u+1013904223u;s.word[j]=(uint16_t)(generator>>16);}
        generator=generator*1664525u+1013904223u;
        check(s,(uint16_t)(generator>>16),(uint16_t)generator,0);next++;
    }
    /* A fixed-bound transition has a period; the interactive generator does not
     * have one universal period because the bounds themselves change its state. */
    const uint16_t bounds[]={0,1,320,65535};
    unsigned collisions[4];
    for(unsigned p=0;p<4;p++) {
        RandomState slow=patterns[2],fast=slow;collisions[p]=0;
        for(unsigned n=1;n<=1000000;n++) {
            random_next_below(&slow,bounds[p]);random_next_below(&fast,bounds[p]);random_next_below(&fast,bounds[p]);
            if(!memcmp(&slow,&fast,sizeof slow)) {collisions[p]=n;break;}
        }
    }
    RandomState zero={{0,0,0,0}};random_next_below(&zero,0);
    if(memcmp(&zero,&patterns[0],sizeof zero)) fail("zero fixed point");
    printf("{\"next_cases\":%lu,\"seed_cases\":%lu,\"period_probe_bound_order\":[0,1,320,65535],\"floyd_collision_iteration\":[%u,%u,%u,%u],\"probe_limit\":1000000,\"zero_state_zero_bound_period\":1}\n",
        next,seeds,collisions[0],collisions[1],collisions[2],collisions[3]);
    return 0;
}
