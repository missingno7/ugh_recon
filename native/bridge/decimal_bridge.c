#include "ugh.h"
#include "../decimal.h"

static DecimalDivisors divisors(const Regs *r) {
    return (DecimalDivisors){ugh_mem+lin(r->ds,D(DecimalTenDivisor)),
        ugh_mem+lin(r->ds,D(DecimalHundredDivisor)),
        ugh_mem+lin(r->ds,D(DecimalThousandDivisor)),
        ugh_mem+lin(r->ds,D(DecimalTenThousandDivisor))};
}
/* Only ordinary RAM, with no alias into code/live L0 save/return frames.
 * Direct borrowed RAM preserves writes that change a later divisor read. */
EXPORT int c_EncodeTwoDecimalDigits(Regs *r) {
    DecimalOutput output={ugh_mem+lin(r->ds,0),65536,r->si};
    DecimalResult result=decimal_two((uint8_t)r->ax,&output,divisors(r));
    r->si=(uint16_t)output.cursor; r->ax=result.last_pair;
    return result.status==DECIMAL_OK ? UGH_OK : UGH_UNSUPPORTED;
}
EXPORT int c_EncodeFourDecimalDigits(Regs *r) {
    DecimalOutput output={ugh_mem+lin(r->ds,0),65536,r->si};
    DecimalResult result=decimal_four(r->ax,&output,divisors(r));
    r->si=(uint16_t)output.cursor; r->ax=result.last_pair; r->dx=result.thousand_remainder;
    return result.status==DECIMAL_OK ? UGH_OK : UGH_UNSUPPORTED;
}
EXPORT int c_EncodeSixDecimalDigits(Regs *r) {
    DecimalOutput output={ugh_mem+lin(r->ds,0),65536,r->si};
    DecimalResult result=decimal_six((uint32_t)r->dx*65536u+r->ax,&output,divisors(r));
    r->si=(uint16_t)output.cursor; r->ax=result.last_pair; r->dx=result.thousand_remainder;
    return result.status==DECIMAL_OK ? UGH_OK : UGH_UNSUPPORTED;
}
