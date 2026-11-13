/* Whole actual C pair. Six-digit usual domain, arbitrary output placement,
 * divisor values and divisor/output aliases inside a 256-byte RAM footprint.
 * Failed divisions are admitted and compared as partial L1 computations. */
void __CPROVER_assume(_Bool);
void __CPROVER_assert(_Bool,const char *);
void __CPROVER_array_copy(void *,const void *);
__CPROVER_bool __CPROVER_array_equal(const void *,const void *);
uint16_t arbitrary_word(void) { uint16_t value; return value; }
uint32_t arbitrary_dword(void) { uint32_t value; return value; }
static uint8_t reference[256],modern_memory[256];
uint8_t ugh_read(uint32_t address) {
    __CPROVER_assert(address<256,"decimal read in declared storage");
    return reference[address];
}
void ugh_write(uint32_t address,uint8_t value) {
    __CPROVER_assert(address<256,"decimal write in declared storage");
    reference[address]=value;
}
int main(void) {
    uint8_t seed[256];
    __CPROVER_array_copy(reference,seed);
    __CPROVER_array_copy(modern_memory,seed);
    uint32_t value=arbitrary_dword();uint16_t start=arbitrary_word(),kind=DECIMAL_KIND;
    __CPROVER_assume(value<=999999u);__CPROVER_assume(start<=249);
#if CANONICAL
    start=0;
    reference[D(DecimalTenDivisor)]=modern_memory[D(DecimalTenDivisor)]=10;
    reference[D(DecimalHundredDivisor)]=modern_memory[D(DecimalHundredDivisor)]=100;
    reference[D(DecimalThousandDivisor)]=modern_memory[D(DecimalThousandDivisor)]=232;
    reference[D(DecimalThousandDivisor)+1]=modern_memory[D(DecimalThousandDivisor)+1]=3;
    reference[D(DecimalTenThousandDivisor)]=modern_memory[D(DecimalTenThousandDivisor)]=16;
    reference[D(DecimalTenThousandDivisor)+1]=modern_memory[D(DecimalTenThousandDivisor)+1]=39;
#endif
    Regs old={0};old.ax=(uint16_t)value;old.dx=(uint16_t)(value>>16);
    old.si=start;old.cx=arbitrary_word();old.flags=arbitrary_word();
    uint16_t saved_count=old.cx,saved_flags=old.flags,initial_high=old.dx;
    int a=kind==0 ? l1_EncodeTwoDecimalDigits(&old) : kind==1 ? l1_EncodeFourDecimalDigits(&old) : l1_EncodeSixDecimalDigits(&old);
    DecimalOutput output={modern_memory,65536,start};
    DecimalDivisors divisors={modern_memory+D(DecimalTenDivisor),modern_memory+D(DecimalHundredDivisor),
        modern_memory+D(DecimalThousandDivisor),modern_memory+D(DecimalTenThousandDivisor)};
    DecimalResult result=kind==0 ? decimal_two((uint8_t)value,&output,divisors) : kind==1 ? decimal_four((uint16_t)value,&output,divisors) : decimal_six(value,&output,divisors);
    int b=result.status==DECIMAL_OK ? UGH_OK : UGH_UNSUPPORTED;
    __CPROVER_assert(a==b,"division status equality including rejected divisions");
    __CPROVER_assert(old.ax==result.last_pair && old.dx==(kind==0 ? initial_high : result.thousand_remainder) && old.si==output.cursor,"decimal results and partial cursors");
    __CPROVER_assert(old.cx==saved_count && old.flags==saved_flags,"decimal preserved environment");
    uint16_t witness=arbitrary_word();__CPROVER_assume(witness<256);
    __CPROVER_assert(reference[witness]==modern_memory[witness],"decimal complete RAM equality (arbitrary index)");
    return 0;
}
