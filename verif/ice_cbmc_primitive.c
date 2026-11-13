/* Real reader helpers and mechanically extracted L1 token statements. */
int main(void) {
    StreamBlob stream=nondet_stream();
    uint16_t source=nondet_word();uint8_t pending=nondet_byte();
    __CPROVER_assume(source<STREAM_SIZE || source==65535);
    l1_input=stream.bytes;
    Ice old={1,2,source,0,pending,1};
    BitReader modern={stream.bytes,STREAM_SIZE,source,pending,ICE_OK};
    unsigned a,b;
#if PRIMITIVE==0
    a=next_bit(&old);b=take_bit(&modern);
#elif PRIMITIVE==1
    unsigned count=nondet_byte();__CPROVER_assume(count<=14);
    a=read_bits(&old,(uint16_t)count);b=take_bits(&modern,count+1);
#elif PRIMITIVE==2
    uint16_t dx=l1_literal_code(&old);
    /* Proven count lemma: the original DEC/JNS loop executes dx+1 times for
     * dx<=32768, otherwise once. Full compiled-code enumeration in
     * ice_evidence.py checks all literal encodings including this boundary.
     * CBMC here checks the actual C parsers against that established lemma. */
    a=dx<=32768u ? dx+1u : 1u;b=literal_length(&modern);
#elif PRIMITIVE==3
    a=l1_length(&old);b=match_length(&modern);
#elif PRIMITIVE==4
    unsigned length=nondet_word();__CPROVER_assume(length>=2 && length<=1033);
    a=(length+l1_offset(&old,(uint16_t)(length-2))) & 65535u;
    b=match_distance(&modern,length);
#endif
    __CPROVER_assert(a==b,"primitive value");
    __CPROVER_assert(modern.error==ICE_OK,"primitive storage");
    __CPROVER_assert(old.si==modern.cursor && old.bits==modern.pending,"primitive reader invariant");
}
