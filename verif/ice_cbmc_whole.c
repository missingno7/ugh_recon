/* The driver supplies actual L1/native sources and L0 table data before this.
 * Array-access assumptions define the bounded ordinary-buffer contract. They
 * occur only in L1: native range errors on an admitted L1 run are failures.
 */
unsigned char nondet_byte(void);
unsigned short nondet_word(void);
typedef struct { uint8_t bytes[STREAM_SIZE]; } StreamBlob;
typedef struct { uint8_t bytes[OUTPUT_SIZE]; } OutputBlob;
StreamBlob nondet_stream(void);
OutputBlob nondet_seed(void);
static uint8_t *l1_input,*l1_output;
static unsigned l1_tokens;
static unsigned seed_reads;
static _Bool written[OUTPUT_SIZE];

static uint8_t rd8(uint16_t segment,uint16_t offset) {
    if(segment==GAME_SEG) {
        __CPROVER_assert(offset>=0x4ddd && offset<0x4e19,"table address in original table");
        return ice_table[offset-0x4ddd];
    }
    if(segment==1) {
        __CPROVER_assume(offset<STREAM_SIZE);
        return l1_input[offset];
    }
    __CPROVER_assert(segment==2,"output segment");
    __CPROVER_assume(offset<OUTPUT_SIZE);
    if(!written[offset])++seed_reads;
    return l1_output[offset];
}
static uint16_t rd16(uint16_t segment,uint16_t offset) {
    return (uint16_t)(rd8(segment,offset) | (uint16_t)rd8(segment,(uint16_t)(offset+1))*256u);
}
static void wr8(uint16_t segment,uint16_t offset,uint8_t value) {
    __CPROVER_assert(segment==2,"write output segment");
    __CPROVER_assume(offset<OUTPUT_SIZE);
    l1_output[offset]=value;
    written[offset]=1;
}

int main(void) {
    StreamBlob stream=nondet_stream();
    OutputBlob old_seed=nondet_seed(),new_seed=old_seed;
    uint8_t *input=stream.bytes,*old_output=old_seed.bytes,*new_output=new_seed.bytes;
    /* No valid-magic or valid-reference requirement: header bytes, bitstream
     * and output seed are arbitrary. Only low-word sizes/storage are bounded. */
    __CPROVER_assume((unsigned)input[6]*256u+input[7]<=STREAM_SIZE);
    __CPROVER_assume((unsigned)input[10]*256u+input[11]<=OUTPUT_SIZE);
    l1_input=input;l1_output=old_output;
    Regs r={nondet_word(),nondet_word(),nondet_word(),nondet_word(),0,nondet_word(),
            nondet_word(),nondet_word(),nondet_word(),1,2,nondet_word(),nondet_word(),nondet_word()};
    Regs before=r;
    int old_status=c_UnpackIceStream(&r);
    unsigned recognized=input[0]=='I' && input[1]=='C' && input[2]=='E' && input[3]=='!';
    REACHABLE(recognized,"witness: recognized magic");
    REACHABLE(recognized && l1_tokens>=2,"witness: multiple tokens");
    REACHABLE(recognized && seed_reads>0,"witness: seed reference");
    REACHABLE(recognized && (unsigned)input[6]*256u+input[7]<12,"witness: malformed header endpoint");
    IceResult result;
    IceStatus new_status=ice_decode(input,STREAM_SIZE,new_output,OUTPUT_SIZE,&result);
    __CPROVER_assert(old_status==UGH_OK,"L1 terminates normally within admitted buffers");
    __CPROVER_assert(new_status==ICE_OK || new_status==ICE_BAD_MAGIC,"native matching completion");
    __CPROVER_assert(r.si==result.source_cursor,"observed source cursor");
    __CPROVER_assert(r.di==(new_status==ICE_OK ? result.destination_cursor : before.di),"observed destination cursor");
    __CPROVER_assert(r.flags==(uint16_t)(before.flags & ~DF),"flags projection");
    __CPROVER_assert(r.ax==before.ax && r.bx==before.bx && r.cx==before.cx && r.dx==before.dx &&
                     r.bp==before.bp && r.ds==before.ds && r.es==before.es && r.cs==before.cs &&
                     r.ss==before.ss && r.sp==before.sp && r.ip==before.ip,"preserved registers");
    __CPROVER_assert(l1_tokens<=TOKEN_BOUND,"token bound follows storage/progress");
    unsigned observer=nondet_word();
    __CPROVER_assume(observer<OUTPUT_SIZE);
    __CPROVER_assert(old_output[observer]==new_output[observer],"all output bytes (arbitrary observer)");
}
