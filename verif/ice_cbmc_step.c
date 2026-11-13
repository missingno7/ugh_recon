/* Included after real implementations and mechanically extracted step bodies.
 * Relational invariant at a live outer-loop boundary:
 * same source bytes and output seed, same 16-bit reader/destination indices,
 * same arbitrary sentinel byte, error==OK, a positive remaining L1 budget,
 * immutable original tables, disjoint buffers, and in-range accesses for this
 * L1 step. No already-decoded-reference assumption: seeded/corrupt matches fit.
 */
int main(void) {
    StreamBlob stream=nondet_stream();
    OutputBlob old_seed=nondet_seed(),new_seed=old_seed;
    uint8_t *input=stream.bytes,*old_output=old_seed.bytes,*new_output=new_seed.bytes;
    uint16_t source=nondet_word(),destination=nondet_word();
    uint8_t pending=nondet_byte();
    __CPROVER_assume(source<STREAM_SIZE || source==65535);
    __CPROVER_assume(destination<OUTPUT_SIZE || destination==65535);
    l1_input=input;l1_output=old_output;
    Ice old={1,2,source,destination,pending,1};
    BitReader modern={input,STREAM_SIZE,source,pending,ICE_OK};
    size_t cursor=destination;
    int old_done=l1_step(&old),new_done=0;
    IceStatus status=native_step(&modern,new_output,&cursor,&new_done);
    __CPROVER_assert(status==ICE_OK,"step status");
    __CPROVER_assert(old_done==new_done,"same terminal branch");
    __CPROVER_assert(old.si==modern.cursor && old.di==cursor,"step cursor relation");
    __CPROVER_assert(old.bits==modern.pending,"step reader relation");
    __CPROVER_assert(modern.data==input && modern.size==STREAM_SIZE && old.ds==1 && old.es==2 && old.budget==1,"preserved step environment");
    unsigned observer=nondet_word();
    __CPROVER_assume(observer<OUTPUT_SIZE);
    __CPROVER_assert(old_output[observer]==new_output[observer],"step all output bytes (arbitrary observer)");
    __CPROVER_assert(modern.cursor<STREAM_SIZE || modern.cursor==65535,"preserved reader index invariant");
    __CPROVER_assert(cursor<OUTPUT_SIZE || cursor==65535,"preserved output index invariant");
#if OUTPUT_SIZE<65536
    __CPROVER_assert(old_done || cursor==65535 || cursor+2<=destination,"continuing step progress");
#endif
}
