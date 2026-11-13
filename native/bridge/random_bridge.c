#include "../random.h"
#include "platform.h"

static RandomState random_project(const Regs *r) {
    RandomState state={{rd16(r->cs,G(RandomStateWord0)),rd16(r->cs,G(RandomStateWord1)),
                        rd16(r->cs,G(RandomStateWord2)),rd16(r->cs,G(RandomStateWord3))}};
    return state;
}

EXPORT int c_NextRandomBelowAx(Regs *r) {
    RandomState state=random_project(r);
    uint16_t first=(uint16_t)(r->ax+state.word[0]);
    r->ax=random_next_below(&state,r->ax);
    wr16(r->cs,G(RandomStateWord1),state.word[1]);
    wr16(r->cs,G(RandomStateWord2),state.word[2]);
    wr16(r->cs,G(RandomStateWord3),state.word[3]);
    wr16(r->cs,G(RandomStateWord0),state.word[0]);
    /* MUL leaves these flags undefined on DOS. Preserve the L1 convention
     * (the final ADC flags) as well as the defined MUL carry/overflow. */
    szp(r,state.word[0],16);
    flag(r,AF,((first^state.word[3]^state.word[0])&16u)!=0);
    flag(r,CF,r->ax!=0);
    flag(r,OF,r->ax!=0);
    return UGH_OK;
}

EXPORT int c_SeedRandomFromDosSeconds(Regs *r) {
    set_ah(r,0x2c);
    int status=platform_interrupt(0x21,r);
    if(status) return status;
    RandomState state=random_project(r);
    RandomDosTime time={(uint8_t)(r->cx>>8),(uint8_t)r->cx,
                        (uint8_t)(r->dx>>8),(uint8_t)r->dx};
    random_seed(&state,time);
    wr8(r->cs,G(RandomSecondsSeedByte),(uint8_t)(state.word[0]>>8));
    return UGH_OK;
}
