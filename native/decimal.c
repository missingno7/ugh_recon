#include "decimal.h"

static void put_digit(DecimalOutput *output, uint8_t digit) {
    output->bytes[output->cursor]=digit;
    if (++output->cursor==output->capacity) output->cursor=0;
}
static uint16_t divisor_word(const uint8_t *bytes) {
    return (uint16_t)(bytes[0]+(uint16_t)bytes[1]*256u);
}
static DecimalResult two_tail(uint8_t value, DecimalOutput *output,
                              DecimalDivisors divisors, DecimalResult result) {
    result.last_pair=value;
    uint8_t divisor=*divisors.ten;
    if (!divisor) { result.status=DECIMAL_DIVISION_ERROR; return result; }
    uint8_t quotient=(uint8_t)(value/divisor), remainder=(uint8_t)(value%divisor);
    put_digit(output,quotient);
    put_digit(output,remainder);
    output->bytes[output->cursor]=255;
    result.last_pair=(uint16_t)(remainder*257u);
    return result;
}
static DecimalResult four_tail(uint16_t value, DecimalOutput *output,
                               DecimalDivisors divisors, DecimalResult result) {
    result.thousand_remainder=0; result.last_pair=value;
    uint16_t divisor=divisor_word(divisors.thousand);
    if (!divisor) { result.status=DECIMAL_DIVISION_ERROR; return result; }
    uint16_t remainder=(uint16_t)(value%divisor);
    put_digit(output,(uint8_t)(value/divisor));
    result.thousand_remainder=remainder; result.last_pair=remainder;
    uint8_t hundred=*divisors.hundred;
    if (!hundred || remainder/hundred>255u) {
        result.status=DECIMAL_DIVISION_ERROR; return result;
    }
    put_digit(output,(uint8_t)(remainder/hundred));
    return two_tail((uint8_t)(remainder%hundred),output,divisors,result);
}
DecimalResult decimal_two(uint8_t value, DecimalOutput *output, DecimalDivisors divisors) {
    return two_tail(value,output,divisors,(DecimalResult){DECIMAL_OK,0,0});
}
DecimalResult decimal_four(uint16_t value, DecimalOutput *output, DecimalDivisors divisors) {
    return four_tail(value,output,divisors,(DecimalResult){DECIMAL_OK,0,0});
}
DecimalResult decimal_six(uint32_t value, DecimalOutput *output, DecimalDivisors divisors) {
    uint8_t digit=255;
    /* Retained: always subtract once, stop on signed high-word sign, and wrap
     * the first byte at 256. This is not unsigned division by 100000. */
    do { ++digit; value-=100000u; } while (!(value&2147483648u));
    value+=100000u;
    put_digit(output,digit);
    DecimalResult result={DECIMAL_OK,(uint16_t)value,(uint16_t)(value>>16)};
    uint16_t divisor=divisor_word(divisors.ten_thousand);
    if (!divisor || value/divisor>65535u) {
        result.status=DECIMAL_DIVISION_ERROR; return result;
    }
    put_digit(output,(uint8_t)(value/divisor));
    return four_tail((uint16_t)(value%divisor),output,divisors,result);
}
