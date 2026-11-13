/* Actual header/initialization prefixes extracted before the two outer loops. */
int main(void) {
    StreamBlob stream=nondet_stream();
    uint8_t *input=stream.bytes;
    __CPROVER_assume((unsigned)input[6]*256u+input[7]<=STREAM_SIZE);
    __CPROVER_assume((unsigned)input[10]*256u+input[11]<=OUTPUT_SIZE);
    l1_input=input;
    Regs r={0};r.ds=1;r.es=2;r.di=nondet_word();r.flags=nondet_word();
    Ice old;BitReader modern;size_t cursor;IceResult result;
    int accepted=l1_init(&r,&old);
    IceStatus status=native_init(input,STREAM_SIZE,&result,&modern,&cursor);
    __CPROVER_assert((accepted!=0)==(status==ICE_OK),"initialization branch relation");
    __CPROVER_assert(status==ICE_OK || status==ICE_BAD_MAGIC,"initialization status");
    if(accepted) {
        __CPROVER_assert(old.si==modern.cursor && old.di==cursor && old.bits==modern.pending,"initialization establishes reader relation");
        __CPROVER_assert(modern.error==ICE_OK,"initialization establishes error invariant");
        __CPROVER_assert(modern.cursor<STREAM_SIZE || modern.cursor==65535,"initial reader index");
        __CPROVER_assert(cursor<OUTPUT_SIZE || cursor==65535,"initial output index");
    } else __CPROVER_assert(r.si==result.source_cursor,"bad-magic cursor relation");
}
