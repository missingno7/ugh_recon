/* Actual L1 body and native body above; only memory/environment is abstracted.
 * Arrays are arbitrary and alias through base shifts; args/save area disjoint.
 * COPY_BOUND bounds count; COPY_STORAGE=64 additionally restricts footprints
 * to that nonwrapping arena. 65568 admits full cursor wrap and base aliases.
 * CANONICAL selects two disjoint spans; other profiles admit ordered overlap. */
void __CPROVER_assume(_Bool);
void __CPROVER_assert(_Bool,const char *);
void __CPROVER_array_copy(void *,const void *);
__CPROVER_bool __CPROVER_array_equal(const void *,const void *);
uint16_t arbitrary_word(void) { uint16_t value; return value; }
unsigned arbitrary_unsigned(void) { unsigned value; return value; }
static uint8_t original[COPY_STORAGE], modern[COPY_STORAGE], arguments[12];
uint8_t ugh_read(uint32_t address) {
    if (address>=0x20004u) {
        __CPROVER_assert(address<0x20010u,"argument read in declared frame");
        return arguments[address-0x20004u];
    }
    __CPROVER_assert(address<COPY_STORAGE,"L1 copy read in RAM");
    return original[address];
}
void ugh_write(uint32_t address,uint8_t value) {
    __CPROVER_assert(address<COPY_STORAGE,"L1 copy write in RAM");original[address]=value;
}
static void argument(unsigned index,uint16_t value) {
    arguments[index]=(uint8_t)value;arguments[index+1]=(uint8_t)(value>>8);
}
int main(void) {
    /* Nondeterministic array, copied relationally without an initialization loop. */
    uint8_t seed[COPY_STORAGE];
    __CPROVER_array_copy(original,seed);__CPROVER_array_copy(modern,seed);
    uint16_t source=arbitrary_word(),destination=arbitrary_word(),count=arbitrary_word();
    uint16_t source_base=arbitrary_word(),destination_base=arbitrary_word();
    uint16_t incoming_flags=arbitrary_word(),incoming_count=arbitrary_word();
    __CPROVER_assume(count<=COPY_BOUND);__CPROVER_assume(source_base<=2);__CPROVER_assume(destination_base<=2);
#if COPY_EXACT
    count=COPY_BOUND;
#endif
#if CANONICAL
    /* Disjoint, aligned borrowed spans, each wholly inside the RAM arena.
     * Direction remains arbitrary; the reverse view starts at each last byte. */
    source_base=0;destination_base=0;
    source=(incoming_flags&DF) ? (uint16_t)(COPY_BOUND-1u) : 0;
    destination=(uint16_t)(source+32u);
#endif
#if COPY_STORAGE < 65568
    __CPROVER_assume(source+source_base*16u<COPY_STORAGE);
    __CPROVER_assume(destination+destination_base*16u<COPY_STORAGE);
    if(incoming_flags&DF) {
        __CPROVER_assume(count<=source+1u && count<=destination+1u);
    } else {
        __CPROVER_assume(source+source_base*16u+count<=COPY_STORAGE);
        __CPROVER_assume(destination+destination_base*16u+count<=COPY_STORAGE);
    }
#endif
    argument(0,count);argument(2,arbitrary_word());argument(4,source);argument(6,source_base);
    argument(8,destination);argument(10,destination_base);
    Regs r={0};r.ss=0x2000;r.cx=incoming_count;r.flags=incoming_flags;
    int status=l1_CopyFarBytes(&r);
    copy_ordered_bytes(modern+destination_base*16u,modern+source_base*16u,
                       destination,source,count,(incoming_flags&DF)!=0);
    __CPROVER_assert(status==UGH_OK && r.cx==0,"copy consumes low count");
    __CPROVER_assert(r.flags==incoming_flags,"copy preserves flags");
    unsigned witness=arbitrary_unsigned();__CPROVER_assume(witness<COPY_STORAGE);
    __CPROVER_assert(original[witness]==modern[witness],"ordered copy complete RAM equality (arbitrary index)");
    return 0;
}
